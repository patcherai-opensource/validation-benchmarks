from flask import Flask
from app.util import configure_access_control
from app.routes import register_routes


def create_app(config):
    app = Flask(__name__)
    app.config["SECRET_KEY"] = config["server"]["secretKey"]
    app.config["OCTOPRINT_CONFIG"] = config

    configure_access_control(app, config)
    register_routes(app, config)

    return app