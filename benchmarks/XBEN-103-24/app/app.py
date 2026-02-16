import logging
import os
from datetime import datetime

from flask import (
    Flask,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from werkzeug.security import check_password_hash, generate_password_hash

from config import AppConfig

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("datalens")


def verify_signing_key(app_config):
    from config import DEFAULT_SIGNING_KEY

    if app_config.SECRET_KEY == DEFAULT_SIGNING_KEY:
        banner = "-" * 72
        logger.warning(banner)
        logger.warning(
            "  WARNING: Default SIGNING_KEY detected. "
            "Override it in datalens_config.py"
        )
        logger.warning(
            "  Generate a secure key with: openssl rand -base64 42"
        )
        logger.warning(banner)


def create_app():
    app = Flask(__name__)
    app.config.from_object(AppConfig)

    verify_signing_key(AppConfig)

    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth_login"

    users_db = {}

    class User(UserMixin):
        def __init__(self, user_id, username, password_hash, role="Viewer", active=True):
            self.id = user_id
            self.username = username
            self.password_hash = password_hash
            self.role = role
            self.active = active
            self.login_count = 0
            self.last_login = None
            self.created_on = datetime.utcnow()

        def is_active(self):
            return self.active

        def check_password(self, password):
            return check_password_hash(self.password_hash, password)

    def init_users():
        admin_pw = os.environ.get("ADMIN_PASSWORD", "xK9#mP2$vL5nR8@qW3jF6hT1")
        users_db["1"] = User(
            "1", "admin",
            generate_password_hash(admin_pw),
            role="Admin"
        )
        users_db["2"] = User(
            "2", "viewer",
            generate_password_hash("bQ7$nL4@xR9mK2#pW6"),
            role="Viewer"
        )
        users_db["3"] = User(
            "3", "analyst",
            generate_password_hash("yH3&tV8!cJ5fN1@sD4"),
            role="Analyst"
        )

    init_users()

    @login_manager.user_loader
    def load_user(user_id):
        return users_db.get(user_id)

    def find_user_by_username(username):
        for u in users_db.values():
            if u.username == username:
                return u
        return None

    @app.after_request
    def apply_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        return response

    @app.route("/")
    def index():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard_list"))
        return redirect(url_for("auth_login"))

    @app.route("/health")
    @app.route("/healthcheck")
    @app.route("/ping")
    def health():
        return "OK"

    @app.route("/login", methods=["GET", "POST"])
    def auth_login():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard_list"))

        error = None
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")

            user = find_user_by_username(username)
            if user and user.check_password(password):
                user.login_count += 1
                user.last_login = datetime.utcnow()
                login_user(user)
                next_page = request.args.get("next")
                return redirect(next_page or url_for("dashboard_list"))
            error = "Invalid credentials"

        return render_template("login.html", error=error)

    @app.route("/logout")
    @login_required
    def auth_logout():
        logout_user()
        return redirect(url_for("auth_login"))

    @app.route("/dashboard/list")
    @login_required
    def dashboard_list():
        dashboards = [
            {
                "id": 1,
                "title": "Sales Overview",
                "owner": "admin",
                "status": "published",
                "changed_on": "2024-01-15 09:30:00",
            },
            {
                "id": 2,
                "title": "User Analytics",
                "owner": "analyst",
                "status": "published",
                "changed_on": "2024-01-14 14:22:00",
            },
            {
                "id": 3,
                "title": "Infrastructure Metrics",
                "owner": "admin",
                "status": "draft",
                "changed_on": "2024-01-13 11:05:00",
            },
        ]
        return render_template(
            "dashboard_list.html",
            dashboards=dashboards,
            user=current_user,
        )

    @app.route("/dashboard/<int:dashboard_id>")
    @login_required
    def dashboard_view(dashboard_id):
        dashboard_data = {
            1: {"title": "Sales Overview", "owner": "admin", "charts": 4},
            2: {"title": "User Analytics", "owner": "analyst", "charts": 3},
            3: {"title": "Infrastructure Metrics", "owner": "admin", "charts": 5},
        }
        dash = dashboard_data.get(dashboard_id)
        if not dash:
            return render_template("error.html", message="Dashboard not found"), 404
        return render_template(
            "dashboard_view.html", dashboard=dash, dashboard_id=dashboard_id, user=current_user
        )

    @app.route("/api/v1/me")
    @login_required
    def api_me():
        return jsonify({
            "result": {
                "id": current_user.id,
                "username": current_user.username,
                "role": current_user.role,
                "login_count": current_user.login_count,
                "last_login": str(current_user.last_login) if current_user.last_login else None,
            }
        })

    @app.route("/api/v1/dashboard/")
    @login_required
    def api_dashboards():
        result = [
            {"id": 1, "dashboard_title": "Sales Overview", "status": "published"},
            {"id": 2, "dashboard_title": "User Analytics", "status": "published"},
            {"id": 3, "dashboard_title": "Infrastructure Metrics", "status": "draft"},
        ]
        return jsonify({"result": result, "count": len(result)})

    @app.route("/api/v1/chart/")
    @login_required
    def api_charts():
        result = [
            {"id": 1, "slice_name": "Revenue by Region", "viz_type": "bar"},
            {"id": 2, "slice_name": "Monthly Active Users", "viz_type": "line"},
            {"id": 3, "slice_name": "Response Time P95", "viz_type": "area"},
        ]
        return jsonify({"result": result, "count": len(result)})

    @app.route("/api/v1/database/")
    @login_required
    def api_databases():
        result = [
            {"id": 1, "database_name": "production_analytics", "backend": "postgresql"},
            {"id": 2, "database_name": "warehouse", "backend": "postgresql"},
        ]
        return jsonify({"result": result, "count": len(result)})

    @app.route("/admin/settings")
    @login_required
    def admin_settings():
        if current_user.role != "Admin":
            return render_template("error.html", message="Forbidden"), 403

        flag_content = ""
        try:
            with open("/data/system_config.dat", "r") as f:
                flag_content = f.read().strip()
        except FileNotFoundError:
            flag_content = "Configuration file not found"
        except Exception:
            flag_content = "Error reading configuration"

        return render_template(
            "admin_settings.html",
            user=current_user,
            system_token=flag_content,
        )

    @app.route("/api/v1/security/csrf_token/")
    @login_required
    def api_csrf_token():
        return jsonify({"result": "csrf_disabled_in_api_mode"})

    @app.errorhandler(404)
    def not_found(e):
        return render_template("error.html", message="Page not found"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("error.html", message="Internal server error"), 500

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
