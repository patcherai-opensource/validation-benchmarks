import logging
import os
import sys

from flask import Flask
from flask_login import LoginManager

from app.config import load_settings
from app.users import UserManager
from app.views import register_routes
from app.api import register_api

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)


def create_app():
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(__file__), "..", "templates"),
        static_folder=os.path.join(os.path.dirname(__file__), "..", "static"),
    )

    cfg = load_settings()
    app.secret_key = cfg["server"]["secretKey"]
    app.config["SETTINGS"] = cfg

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "login"

    user_manager = UserManager(cfg)
    app.config["USER_MANAGER"] = user_manager

    @login_manager.user_loader
    def load_user(user_id):
        return user_manager.find_user(user_id)

    @login_manager.request_loader
    def load_user_from_request(request):
        from app.util import resolve_client_address, check_autologin

        return check_autologin(request, cfg, user_manager)

    register_routes(app)
    register_api(app)

    return app


if __name__ == "__main__":
    app = create_app()
    cfg = app.config["SETTINGS"]
    host = cfg["server"]["host"]
    port = cfg["server"]["port"]
    app.run(host=host, port=port, debug=False)