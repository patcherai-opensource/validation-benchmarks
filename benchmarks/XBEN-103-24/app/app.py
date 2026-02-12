import logging
import os
import hashlib
from datetime import datetime, timedelta
from functools import wraps

from flask import (
    Flask,
    request,
    render_template,
    redirect,
    url_for,
    session,
    jsonify,
    flash,
    abort,
)

from config import (
    APP_NAME,
    SECRET_KEY,
    SESSION_COOKIE_NAME,
    SESSION_COOKIE_HTTPONLY,
    ENABLE_PROXY_FIX,
    WTF_CSRF_ENABLED,
    SUPERSET_WEBSERVER_PORT,
    SUPERSET_WEBSERVER_TIMEOUT,
    TALISMAN_ENABLED,
    PREVENT_UNSAFE_DB_CONNECTIONS,
)

logger = logging.getLogger(__name__)


def create_app():
    app = Flask(__name__)

    # Apply configuration
    app.config["SECRET_KEY"] = SECRET_KEY
    app.config["APPLICATION_NAME"] = APP_NAME
    app.config["SESSION_COOKIE_NAME"] = SESSION_COOKIE_NAME
    app.config["SESSION_COOKIE_HTTPONLY"] = SESSION_COOKIE_HTTPONLY
    app.config["WTF_CSRF_ENABLED"] = WTF_CSRF_ENABLED
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=8)
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    _check_secret_key(app)

    _setup_logging(app)

    from views import register_views

    register_views(app)

    return app


def _check_secret_key(app):
    """Check the configured SECRET_KEY and warn if using the default value."""
    default_keys = {
        "CHANGE_ME_TO_A_COMPLEX_RANDOM_SECRET",
        "thisISaSECRET_1234",
        "YOUR_OWN_RANDOM_GENERATED_SECRET_KEY",
    }
    current_key = app.config.get("SECRET_KEY", "")
    if current_key in default_keys:
        logger.warning(
            "WARNING: Possible default SECRET_KEY detected. "
            "Use a strong unique SECRET_KEY for production deployments. "
            "Superset will not be able to start without a SECRET_KEY in a future version."
        )


def _setup_logging(app):
    log_format = "%(asctime)s:%(levelname)s:%(name)s:%(message)s"
    log_level = os.environ.get("LOG_LEVEL", "WARNING").upper()
    logging.basicConfig(format=log_format, level=getattr(logging, log_level, logging.WARNING))
    # Suppress noisy loggers
    logging.getLogger("werkzeug").setLevel(logging.WARNING)


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=SUPERSET_WEBSERVER_PORT, debug=False)
