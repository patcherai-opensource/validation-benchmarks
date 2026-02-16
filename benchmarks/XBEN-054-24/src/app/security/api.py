import logging

from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)
from werkzeug.security import check_password_hash

from ..models import db, User

log = logging.getLogger(__name__)

auth_api = Blueprint("auth_api", __name__, url_prefix="/api/v1/auth")

PROVIDER_DB = "db"
PROVIDER_LDAP = "ldap"


def _authenticate_db(username, password):
    if not username:
        return None
    user = User.query.filter_by(username=username).first()
    if user is None:
        user = User.query.filter_by(email=username).first()
    if user is None or not user.is_active:
        return None
    if check_password_hash(user.password, password):
        user.login_count = (user.login_count or 0) + 1
        db.session.commit()
        return user
    else:
        user.fail_login_count = (user.fail_login_count or 0) + 1
        db.session.commit()
        return None


def _authenticate_ldap(username, password):
    from flask import current_app
    ldap_server = current_app.config.get("AUTH_LDAP_SERVER")
    if not ldap_server:
        log.error("AUTH_LDAP_SERVER not configured")
        return None

    try:
        import ldap as ldap_module
        con = ldap_module.initialize(ldap_server)
        ldap_search = current_app.config.get("AUTH_LDAP_SEARCH", "")
        uid_field = current_app.config.get("AUTH_LDAP_UID_FIELD", "uid")
        bind_dn = "{0}={1},{2}".format(uid_field, username, ldap_search)
        con.simple_bind_s(bind_dn, password)
        user = User.query.filter_by(username=username).first()
        if user and user.is_active:
            user.login_count = (user.login_count or 0) + 1
            db.session.commit()
            return user
        return None
    except Exception as e:
        log.error("LDAP authentication error: %s", str(e))
        return None


@auth_api.route("/authenticate", methods=["POST"])
def authenticate():
    if not request.is_json:
        return jsonify({"message": "Request payload is not JSON"}), 400

    username = request.json.get("username", None)
    password = request.json.get("password", None)
    provider = request.json.get("provider", None)
    refresh = request.json.get("refresh", False)

    if not username or not password or not provider:
        return jsonify({"message": "Missing required parameter"}), 400

    if provider == PROVIDER_DB:
        user = _authenticate_db(username, password)
    elif provider == PROVIDER_LDAP:
        user = _authenticate_ldap(username, password)
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


@auth_api.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh_token():
    identity = get_jwt_identity()
    resp = {"access_token": create_access_token(identity=identity, fresh=False)}
    return jsonify(resp), 200
