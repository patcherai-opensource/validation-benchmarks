import os
import logging

from flask import Flask
from flask_jwt_extended import JWTManager
from werkzeug.security import generate_password_hash

from .models import db, User, Role, Permission, ViewMenu, PermissionView, SystemConfig
from .security.api import auth_api
from .views import main_bp, api_bp


def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////data/app.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.environ.get(
        "JWT_SECRET_KEY", "a7f3c8d1e9b24f5a8c6d0e2f4a7b9c1d"
    )
    app.config["PROPAGATE_EXCEPTIONS"] = False
    app.config["JWT_TOKEN_LOCATION"] = ["headers"]

    app.config["AUTH_TYPE"] = 2  # LDAP
    app.config["AUTH_LDAP_SERVER"] = "ldap://ldap.internal.corp:389"
    app.config["AUTH_LDAP_SEARCH"] = "ou=users,dc=internal,dc=corp"
    app.config["AUTH_LDAP_UID_FIELD"] = "uid"
    app.config["AUTH_LDAP_USE_TLS"] = False

    log = logging.getLogger("app")
    log.setLevel(logging.WARNING)

    db.init_app(app)
    jwt = JWTManager(app)

    app.register_blueprint(auth_api)
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)

    @app.errorhandler(404)
    def not_found(e):
        from flask import jsonify
        return jsonify({"message": "Not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        from flask import jsonify
        return jsonify({"message": "Method not allowed"}), 405

    @app.errorhandler(500)
    def internal_error(e):
        from flask import jsonify
        return jsonify({"message": "Internal server error"}), 500

    with app.app_context():
        _init_database(app)

    return app


def _init_database(app):
    db_path = "/data/app.db"
    if os.path.exists(db_path):
        return

    db.create_all()

    admin_role = Role(id=1, name="Admin")
    public_role = Role(id=2, name="Public")
    viewer_role = Role(id=3, name="Viewer")
    db.session.add_all([admin_role, public_role, viewer_role])
    db.session.flush()

    flag_value = os.environ.get("APP_INIT_TOKEN", "")

    admin_user = User(
        id=1,
        first_name="Admin",
        last_name="User",
        username="admin",
        password=generate_password_hash("admin"),
        email="admin@internal.corp",
        active=True,
    )
    admin_user.roles.append(admin_role)

    viewer_user = User(
        id=2,
        first_name="Viewer",
        last_name="User",
        username="viewer",
        password=generate_password_hash("viewer"),
        email="viewer@internal.corp",
        active=True,
    )
    viewer_user.roles.append(viewer_role)

    db.session.add_all([admin_user, viewer_user])

    configs = [
        SystemConfig(key="AUTH_TYPE", value="LDAP"),
        SystemConfig(key="AUTH_LDAP_SERVER", value="ldap://ldap.internal.corp:389"),
        SystemConfig(key="AUTH_LDAP_SEARCH", value="ou=users,dc=internal,dc=corp"),
        SystemConfig(key="APP_NAME", value="AppBuilder"),
        SystemConfig(key="APP_VERSION", value="3.3.2"),
        SystemConfig(key="SYSTEM_FLAG", value=flag_value),
    ]
    db.session.add_all(configs)

    perms = [
        Permission(id=1, name="can_list"),
        Permission(id=2, name="can_show"),
        Permission(id=3, name="can_edit"),
        Permission(id=4, name="can_delete"),
        Permission(id=5, name="can_add"),
        Permission(id=6, name="menu_access"),
    ]
    db.session.add_all(perms)

    views = [
        ViewMenu(id=1, name="UserDBModelView"),
        ViewMenu(id=2, name="RoleModelView"),
        ViewMenu(id=3, name="PermissionModelView"),
        ViewMenu(id=4, name="ViewMenuModelView"),
        ViewMenu(id=5, name="ConfigView"),
    ]
    db.session.add_all(views)
    db.session.flush()

    pvs = [
        PermissionView(permission_id=1, view_menu_id=1),
        PermissionView(permission_id=2, view_menu_id=1),
        PermissionView(permission_id=3, view_menu_id=1),
        PermissionView(permission_id=1, view_menu_id=2),
        PermissionView(permission_id=2, view_menu_id=2),
        PermissionView(permission_id=1, view_menu_id=5),
    ]
    db.session.add_all(pvs)

    db.session.commit()
