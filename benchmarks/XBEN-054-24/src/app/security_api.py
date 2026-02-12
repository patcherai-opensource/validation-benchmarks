import logging
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)
from app import db
from app.models import User

logger = logging.getLogger(__name__)

security_api = Blueprint("security_api", __name__, url_prefix="/api/v1/security")

API_SECURITY_PROVIDER_DB = "db"
API_SECURITY_PROVIDER_LDAP = "ldap"
API_SECURITY_VERSION = "v1"


def auth_user_db(username, password):
    """Authenticate user against database backend"""
    user = User.query.filter_by(username=username).first()
    if user and user.is_active and user.check_password(password):
        user.login_count = (user.login_count or 0) + 1
        db.session.commit()
        return user
    return None


def auth_user_ldap(username, password):
    """Authenticate user against LDAP backend"""
    ldap_server = current_app.config.get("AUTH_LDAP_SERVER")
    if not ldap_server:
        logger.error("LDAP server not configured")
        return None
    try:
        import ldap3
        server = ldap3.Server(ldap_server, get_info=ldap3.ALL)
        bind_dn = current_app.config.get(
            "AUTH_LDAP_USERNAME_FORMAT", "uid={0},ou=users,dc=example,dc=com"
        ).format(username)
        conn = ldap3.Connection(server, user=bind_dn, password=password)
        if conn.bind():
            search_base = current_app.config.get(
                "AUTH_LDAP_SEARCH", "ou=users,dc=example,dc=com"
            )
            conn.search(search_base, "(uid={})".format(username))
            if conn.entries:
                user = User.query.filter_by(username=username).first()
                if user and user.is_active:
                    return user
            conn.unbind()
    except Exception as e:
        logger.error("LDAP authentication error: %s", str(e))
    return None


@security_api.route("/login", methods=["POST"])
def login():
    """Login endpoint for the API returns a JWT and optionally a refresh token
    ---
    post:
      description: >-
        Authenticate and get a JWT access and refresh token
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                username:
                  description: The username for authentication
                  example: admin
                  type: string
                password:
                  description: The password for authentication
                  example: complex-password
                  type: string
                provider:
                  description: Choose an authentication provider
                  example: ldap
                  type: string
                  enum:
                  - db
                  - ldap
                refresh:
                  description: If true a refresh token is provided also
                  example: true
                  type: boolean
      responses:
        200:
          description: Authentication Successful
          content:
            application/json:
              schema:
                type: object
                properties:
                  access_token:
                    type: string
                  refresh_token:
                    type: string
        400:
          description: Bad Request
        401:
          description: Unauthorized
    """
    if not request.is_json:
        return jsonify({"message": "Request payload is not JSON"}), 400

    username = request.json.get("username", None)
    password = request.json.get("password", None)
    provider = request.json.get("provider", None)
    refresh = request.json.get("refresh", False)

    if not username or not password or not provider:
        return jsonify({"message": "Missing required parameter"}), 400

    # Authenticate based on the requested provider
    if provider == API_SECURITY_PROVIDER_DB:
        user = auth_user_db(username, password)
    elif provider == API_SECURITY_PROVIDER_LDAP:
        user = auth_user_ldap(username, password)
    else:
        return jsonify(
            {"message": "Provider {} not supported".format(provider)}
        ), 400

    if not user:
        return jsonify({"message": "Not authorized"}), 401

    resp = dict()
    resp["access_token"] = create_access_token(identity=user.id, fresh=True)
    if refresh:
        resp["refresh_token"] = create_refresh_token(identity=user.id)
    return jsonify(resp), 200


@security_api.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def token_refresh():
    """Use the refresh token to get a new JWT access token"""
    identity = get_jwt_identity()
    resp = {"access_token": create_access_token(identity=identity, fresh=False)}
    return jsonify(resp), 200
