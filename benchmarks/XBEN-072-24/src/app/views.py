import logging

from flask import (
    current_app,
    redirect,
    render_template,
    request,
    url_for,
    jsonify,
    abort,
    session,
)
from flask_login import current_user, login_user, logout_user, login_required

from app.util import resolve_client_address

logger = logging.getLogger(__name__)


def register_routes(app):

    @app.route("/ping")
    def ping():
        return "ok", 200

    @app.route("/")
    def index():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))
        return redirect(url_for("login"))

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))

        error = None
        if request.method == "POST":
            username = request.form.get("user", "").strip()
            password = request.form.get("pass", "").strip()

            if not username or not password:
                error = "Please provide both username and password."
            else:
                user_mgr = current_app.config["USER_MANAGER"]
                user = user_mgr.find_user(username)
                if user is not None and user.check_password(password):
                    login_user(user)
                    session["login_mechanism"] = "credentials"
                    return redirect(url_for("dashboard"))
                else:
                    error = "Invalid credentials."

        return render_template("login.html", error=error)

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect(url_for("login"))

    @app.route("/dashboard")
    @login_required
    def dashboard():
        cfg = current_app.config["SETTINGS"]
        fabricator_cfg = cfg.get("fabricator", {})
        return render_template(
            "dashboard.html",
            user=current_user,
            fabricator=fabricator_cfg,
        )

    @app.route("/control")
    @login_required
    def control():
        return render_template("control.html", user=current_user)

    @app.route("/temperature")
    @login_required
    def temperature():
        return render_template("temperature.html", user=current_user)

    @app.errorhandler(401)
    def unauthorized(e):
        return redirect(url_for("login"))

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("error.html", code=403, message="Forbidden"), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template("error.html", code=404, message="Not Found"), 404

    @app.after_request
    def remove_server_header(response):
        response.headers.pop("Server", None)
        return response