import logging
from flask import Blueprint, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User, Role

logger = logging.getLogger(__name__)

app_api = Blueprint("app_api", __name__, url_prefix="/api/v1")


@app_api.route("/users/", methods=["GET"])
@jwt_required()
def list_users():
    """List all users - requires admin role"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    admin_role = Role.query.filter_by(name="Admin").first()
    if admin_role not in user.roles:
        return jsonify({"message": "Access denied"}), 403

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
            "login_count": u.login_count,
            "roles": [r.name for r in u.roles],
        })
    return jsonify({"count": len(result), "result": result}), 200


@app_api.route("/users/<int:user_id>", methods=["GET"])
@jwt_required()
def get_user(user_id):
    """Get a specific user"""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    if not current_user:
        return jsonify({"message": "User not found"}), 404

    target_user = User.query.get(user_id)
    if not target_user:
        return jsonify({"message": "Not found"}), 404

    return jsonify({
        "id": target_user.id,
        "username": target_user.username,
        "first_name": target_user.first_name,
        "last_name": target_user.last_name,
        "email": target_user.email,
        "active": target_user.active,
        "roles": [r.name for r in target_user.roles],
    }), 200


@app_api.route("/roles/", methods=["GET"])
@jwt_required()
def list_roles():
    """List all roles"""
    roles = Role.query.all()
    result = [{"id": r.id, "name": r.name} for r in roles]
    return jsonify({"count": len(result), "result": result}), 200


@app_api.route("/me/", methods=["GET"])
@jwt_required()
def get_current_user():
    """Get current user info"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "roles": [r.name for r in user.roles],
    }), 200


@app_api.route("/config/", methods=["GET"])
@jwt_required()
def get_config():
    """Get application configuration - admin only"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    admin_role = Role.query.filter_by(name="Admin").first()
    if admin_role not in user.roles:
        return jsonify({"message": "Access denied"}), 403

    flag = current_app.config.get("SECRET_DATA", "")

    config = {
        "auth_type": current_app.config.get("AUTH_TYPE", "LDAP"),
        "app_name": current_app.config.get("APP_NAME", ""),
        "auth_ldap_server": current_app.config.get("AUTH_LDAP_SERVER", ""),
        "secret_data": flag,
    }
    return jsonify(config), 200
