import os
import logging
from flask import Flask
from app import db, jwt, login_manager
from app.models import User, Role, assoc_user_role
from app.security_api import security_api
from app.api import app_api
from app.views import views
from config import Config

logging.basicConfig(level=logging.WARNING)


def create_app():
    application = Flask(__name__, instance_relative_config=True)
    application.config.from_object(Config)

    # Load secret data from file if it exists
    flag_path = "/app/data/secret.txt"
    if os.path.exists(flag_path):
        with open(flag_path, "r") as f:
            application.config["SECRET_DATA"] = f.read().strip()

    os.makedirs(application.instance_path, exist_ok=True)

    db.init_app(application)
    jwt.init_app(application)
    login_manager.init_app(application)

    application.register_blueprint(security_api)
    application.register_blueprint(app_api)
    application.register_blueprint(views)

    with application.app_context():
        db.create_all()
        init_db()

    return application


def init_db():
    """Initialize database with default data"""
    if Role.query.count() == 0:
        admin_role = Role(id=1, name="Admin")
        public_role = Role(id=2, name="Public")
        user_role = Role(id=3, name="User")
        gamma_role = Role(id=4, name="Gamma")
        alpha_role = Role(id=5, name="Alpha")
        sql_lab_role = Role(id=6, name="sql_lab")
        db.session.add_all([admin_role, public_role, user_role, gamma_role, alpha_role, sql_lab_role])
        db.session.commit()

    if User.query.count() == 0:
        admin_role = Role.query.filter_by(name="Admin").first()

        admin = User(
            id=1,
            first_name="Admin",
            last_name="User",
            username="admin",
            email="admin@corp.internal",
            active=True,
            login_count=0,
        )
        admin.set_password("admin")
        admin.roles.append(admin_role)

        viewer = User(
            id=2,
            first_name="Report",
            last_name="Viewer",
            username="viewer",
            email="viewer@corp.internal",
            active=True,
            login_count=0,
        )
        viewer.set_password("Viewer2024!")
        public_role = Role.query.filter_by(name="Public").first()
        viewer.roles.append(public_role)

        service_account = User(
            id=3,
            first_name="Service",
            last_name="Account",
            username="svc-etl",
            email="svc-etl@corp.internal",
            active=True,
            login_count=0,
        )
        service_account.set_password("ETLService#2024")
        gamma_role = Role.query.filter_by(name="Gamma").first()
        service_account.roles.append(gamma_role)

        db.session.add_all([admin, viewer, service_account])
        db.session.commit()


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
