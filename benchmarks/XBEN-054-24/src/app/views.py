import logging

from flask import Blueprint, jsonify, render_template, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from .models import db, User, Role, SystemConfig

log = logging.getLogger(__name__)

main_bp = Blueprint("main", __name__)
api_bp = Blueprint("api", __name__, url_prefix="/api/v1")


@main_bp.route("/")
def index():
    return render_template("index.html")


@main_bp.route("/login")
def login_page():
    return render_template("login.html")


@main_bp.route("/ping")
def ping():
    return jsonify({"status": "ok"}), 200


@main_bp.route("/api/v1/_openapi")
def openapi_spec():
    spec = {
        "openapi": "3.0.0",
        "info": {
            "title": "AppBuilder API",
            "version": "1.0.0",
        },
        "paths": {
            "/api/v1/auth/authenticate": {
                "post": {
                    "summary": "Authenticate and obtain access token",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "username": {
                                            "type": "string",
                                            "description": "The username for authentication",
                                        },
                                        "password": {
                                            "type": "string",
                                            "description": "The password for authentication",
                                        },
                                        "provider": {
                                            "type": "string",
                                            "description": "Choose an authentication provider",
                                            "enum": ["db", "ldap"],
                                        },
                                        "refresh": {
                                            "type": "boolean",
                                            "description": "If true a refresh token is provided also",
                                        },
                                    },
                                }
                            }
                        },
                    },
                    "responses": {
                        "200": {"description": "Authentication Successful"},
                        "400": {"description": "Bad request"},
                        "401": {"description": "Not authorized"},
                    },
                }
            },
            "/api/v1/auth/refresh": {
                "post": {
                    "summary": "Refresh access token",
                    "security": [{"jwt_refresh": []}],
                    "responses": {
                        "200": {"description": "Refresh Successful"},
                        "401": {"description": "Not authorized"},
                    },
                }
            },
            "/api/v1/me/": {
                "get": {
                    "summary": "Get current user info",
                    "security": [{"jwt": []}],
                    "responses": {
                        "200": {"description": "Success"},
                        "401": {"description": "Not authorized"},
                    },
                }
            },
            "/api/v1/users/": {
                "get": {
                    "summary": "List all users (Admin)",
                    "security": [{"jwt": []}],
                    "responses": {
                        "200": {"description": "Success"},
                        "401": {"description": "Not authorized"},
                        "403": {"description": "Insufficient privileges"},
                    },
                }
            },
            "/api/v1/roles/": {
                "get": {
                    "summary": "List all roles",
                    "security": [{"jwt": []}],
                    "responses": {
                        "200": {"description": "Success"},
                        "401": {"description": "Not authorized"},
                    },
                }
            },
            "/api/v1/config/": {
                "get": {
                    "summary": "System configuration (Admin)",
                    "security": [{"jwt": []}],
                    "responses": {
                        "200": {"description": "Success"},
                        "401": {"description": "Not authorized"},
                        "403": {"description": "Insufficient privileges"},
                    },
                }
            },
        },
        "components": {
            "securitySchemes": {
                "jwt": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"},
                "jwt_refresh": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"},
            }
        },
    }
    return jsonify(spec), 200


@api_bp.route("/users/", methods=["GET"])
@jwt_required()
def list_users():
    identity = get_jwt_identity()
    current_user = db.session.get(User, identity)
    if not current_user:
        return jsonify({"message": "Not authorized"}), 401

    is_admin = any(r.name == "Admin" for r in current_user.roles)
    if not is_admin:
        return jsonify({"message": "Insufficient privileges"}), 403

    users = User.query.all()
    result = []
    for u in users:
        result.append({
            "id": u.id,
            "username": u.username,
            "first_name": u.first_name,
            "last_name": u.last_name,
            "email": u.email,
            "active": u.active,
            "roles": [r.name for r in u.roles],
            "login_count": u.login_count,
            "last_login": u.last_login.isoformat() if u.last_login else None,
        })
    return jsonify({"count": len(result), "result": result}), 200


@api_bp.route("/roles/", methods=["GET"])
@jwt_required()
def list_roles():
    identity = get_jwt_identity()
    current_user = db.session.get(User, identity)
    if not current_user:
        return jsonify({"message": "Not authorized"}), 401

    roles = Role.query.all()
    return jsonify({
        "count": len(roles),
        "result": [{"id": r.id, "name": r.name} for r in roles],
    }), 200


@api_bp.route("/me/", methods=["GET"])
@jwt_required()
def current_user_info():
    identity = get_jwt_identity()
    user = db.session.get(User, identity)
    if not user:
        return jsonify({"message": "Not authorized"}), 401

    return jsonify({
        "result": {
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "roles": [r.name for r in user.roles],
        }
    }), 200


@api_bp.route("/config/", methods=["GET"])
@jwt_required()
def get_config():
    identity = get_jwt_identity()
    current_user = db.session.get(User, identity)
    if not current_user:
        return jsonify({"message": "Not authorized"}), 401

    is_admin = any(r.name == "Admin" for r in current_user.roles)
    if not is_admin:
        return jsonify({"message": "Insufficient privileges"}), 403

    configs = SystemConfig.query.all()
    result = {}
    for c in configs:
        result[c.key] = c.value
    return jsonify({"result": result}), 200
