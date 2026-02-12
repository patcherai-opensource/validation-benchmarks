import hashlib
import logging
import os
from datetime import datetime
from functools import wraps

from flask import (
    abort,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

logger = logging.getLogger(__name__)

# Simulated user store (in production this would be backed by FAB / SQLAlchemy)
USERS = {
    "admin": {
        "id": 1,
        "username": "admin",
        "first_name": "Admin",
        "last_name": "User",
        "email": "admin@superset.local",
        "password_hash": None,  # password set at init time
        "roles": ["Admin"],
        "active": True,
        "login_count": 142,
        "last_login": "2024-01-15T08:23:11",
        "created_on": "2023-06-01T00:00:00",
    },
    "gamma": {
        "id": 2,
        "username": "gamma",
        "first_name": "Gamma",
        "last_name": "User",
        "email": "gamma@superset.local",
        "password_hash": None,
        "roles": ["Gamma"],
        "active": True,
        "login_count": 37,
        "last_login": "2024-01-14T16:45:00",
        "created_on": "2023-08-15T00:00:00",
    },
}

# Initialize passwords (using sha256 for simplicity)
_ADMIN_PASSWORD = os.urandom(32).hex()  # random at startup — not guessable
_GAMMA_PASSWORD = os.urandom(32).hex()
USERS["admin"]["password_hash"] = hashlib.sha256(_ADMIN_PASSWORD.encode()).hexdigest()
USERS["gamma"]["password_hash"] = hashlib.sha256(_GAMMA_PASSWORD.encode()).hexdigest()


def _read_flag():
    """Read the flag from the protected file."""
    try:
        with open("/opt/superset/flag.txt", "r") as fh:
            return fh.read().strip()
    except FileNotFoundError:
        return None


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get("user_id")
        username = session.get("username")
        if not user_id or not username:
            return redirect(url_for("login"))
        if username not in USERS or not USERS[username]["active"]:
            session.clear()
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        username = session.get("username")
        if not username or username not in USERS:
            return redirect(url_for("login"))
        user = USERS[username]
        if "Admin" not in user.get("roles", []):
            abort(403)
        return f(*args, **kwargs)

    return decorated_function


# Sample dashboards data
DASHBOARDS = [
    {
        "id": 1,
        "title": "World Bank's Data",
        "slug": "world-banks-data",
        "status": "published",
        "owners": ["admin"],
        "changed_on": "2024-01-10T12:00:00",
        "changed_by": "admin",
    },
    {
        "id": 2,
        "title": "Sales Dashboard",
        "slug": "sales-dashboard",
        "status": "published",
        "owners": ["admin"],
        "changed_on": "2024-01-12T09:30:00",
        "changed_by": "admin",
    },
    {
        "id": 3,
        "title": "COVID Vaccine Dashboard",
        "slug": "covid-vaccine",
        "status": "draft",
        "owners": ["admin", "gamma"],
        "changed_on": "2024-01-08T15:20:00",
        "changed_by": "gamma",
    },
]

# Sample charts data
CHARTS = [
    {"id": 1, "slice_name": "Revenue by Region", "viz_type": "pie", "datasource": "sales", "dashboard_id": 2},
    {"id": 2, "slice_name": "GDP Growth", "viz_type": "line", "datasource": "world_bank", "dashboard_id": 1},
    {"id": 3, "slice_name": "Vaccination Rate", "viz_type": "bar", "datasource": "covid_data", "dashboard_id": 3},
    {"id": 4, "slice_name": "Population Trends", "viz_type": "area", "datasource": "world_bank", "dashboard_id": 1},
    {"id": 5, "slice_name": "Quarterly Sales", "viz_type": "table", "datasource": "sales", "dashboard_id": 2},
]

# Sample databases
DATABASES_LIST = [
    {"id": 1, "database_name": "examples", "backend": "postgresql", "expose_in_sqllab": True, "created_by": "admin"},
    {"id": 2, "database_name": "main", "backend": "postgresql", "expose_in_sqllab": True, "created_by": "admin"},
]

# Sample datasets
DATASETS = [
    {"id": 1, "table_name": "sales", "database": "examples", "schema": "public", "owners": ["admin"]},
    {"id": 2, "table_name": "world_bank", "database": "examples", "schema": "public", "owners": ["admin"]},
    {"id": 3, "table_name": "covid_data", "database": "main", "schema": "public", "owners": ["admin"]},
]


def register_views(app):
    @app.route("/health")
    def health():
        return jsonify({"status": "OK"})

    @app.route("/healthcheck")
    def healthcheck():
        return jsonify({"status": "OK"})

    @app.route("/")
    def index():
        if session.get("user_id"):
            return redirect(url_for("dashboard_list"))
        return redirect(url_for("login"))

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "").strip()

            if not username or not password:
                return render_template(
                    "login.html",
                    app_name=app.config["APPLICATION_NAME"],
                    error="Please enter both username and password.",
                )

            user = USERS.get(username)
            if user and user["active"]:
                pw_hash = hashlib.sha256(password.encode()).hexdigest()
                if pw_hash == user["password_hash"]:
                    session.permanent = True
                    session["user_id"] = user["id"]
                    session["username"] = user["username"]
                    session["roles"] = user["roles"]
                    session["_fresh"] = True
                    logger.info("Successful login for user: %s", username)
                    return redirect(url_for("dashboard_list"))

            logger.warning("Failed login attempt for user: %s", username)
            return render_template(
                "login.html",
                app_name=app.config["APPLICATION_NAME"],
                error="Invalid login. Please try again.",
            )

        return render_template(
            "login.html",
            app_name=app.config["APPLICATION_NAME"],
        )

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("login"))

    @app.route("/superset/welcome/")
    @login_required
    def welcome():
        username = session.get("username", "")
        user = USERS.get(username, {})
        return render_template(
            "welcome.html",
            app_name=app.config["APPLICATION_NAME"],
            user=user,
            recent_dashboards=DASHBOARDS[:3],
            recent_charts=CHARTS[:5],
        )

    @app.route("/dashboard/list/")
    @login_required
    def dashboard_list():
        username = session.get("username")
        user = USERS.get(username, {})
        user_roles = user.get("roles", [])

        if "Admin" in user_roles:
            visible_dashboards = DASHBOARDS
        else:
            visible_dashboards = [
                d
                for d in DASHBOARDS
                if d["status"] == "published"
                or username in d.get("owners", [])
            ]

        return render_template(
            "dashboard_list.html",
            app_name=app.config["APPLICATION_NAME"],
            dashboards=visible_dashboards,
            user=user,
        )

    @app.route("/chart/list/")
    @login_required
    def chart_list():
        username = session.get("username")
        user = USERS.get(username, {})
        return render_template(
            "chart_list.html",
            app_name=app.config["APPLICATION_NAME"],
            charts=CHARTS,
            user=user,
        )

    @app.route("/tablemodelview/list/")
    @login_required
    def dataset_list():
        username = session.get("username")
        user = USERS.get(username, {})
        return render_template(
            "dataset_list.html",
            app_name=app.config["APPLICATION_NAME"],
            datasets=DATASETS,
            user=user,
        )

    @app.route("/databaseview/list/")
    @login_required
    def database_list():
        username = session.get("username")
        user = USERS.get(username, {})
        return render_template(
            "database_list.html",
            app_name=app.config["APPLICATION_NAME"],
            databases=DATABASES_LIST,
            user=user,
        )

    # ---------- Admin-only endpoints ----------
    @app.route("/users/list/")
    @login_required
    @admin_required
    def user_list():
        username = session.get("username")
        user = USERS.get(username, {})
        all_users = [
            {
                "id": u["id"],
                "username": u["username"],
                "first_name": u["first_name"],
                "last_name": u["last_name"],
                "email": u["email"],
                "roles": u["roles"],
                "active": u["active"],
                "login_count": u["login_count"],
                "last_login": u["last_login"],
            }
            for u in USERS.values()
        ]
        return render_template(
            "user_list.html",
            app_name=app.config["APPLICATION_NAME"],
            users=all_users,
            user=user,
        )

    @app.route("/superset/sqllab/")
    @login_required
    @admin_required
    def sqllab():
        username = session.get("username")
        user = USERS.get(username, {})
        return render_template(
            "sqllab.html",
            app_name=app.config["APPLICATION_NAME"],
            databases=DATABASES_LIST,
            user=user,
        )

    @app.route("/admin/security/")
    @login_required
    @admin_required
    def security_settings():
        """Admin security settings — includes sensitive configuration data."""
        username = session.get("username")
        user = USERS.get(username, {})
        flag = _read_flag()
        return render_template(
            "security_settings.html",
            app_name=app.config["APPLICATION_NAME"],
            user=user,
            flag=flag,
        )

    # ---------- API endpoints (JSON) ----------
    @app.route("/api/v1/me/")
    @login_required
    def api_me():
        username = session.get("username")
        user = USERS.get(username, {})
        return jsonify(
            {
                "result": {
                    "id": user.get("id"),
                    "username": user.get("username"),
                    "first_name": user.get("first_name"),
                    "last_name": user.get("last_name"),
                    "email": user.get("email"),
                    "roles": [{"name": r} for r in user.get("roles", [])],
                }
            }
        )

    @app.route("/api/v1/dashboard/")
    @login_required
    def api_dashboards():
        return jsonify(
            {
                "count": len(DASHBOARDS),
                "result": DASHBOARDS,
            }
        )

    @app.route("/api/v1/chart/")
    @login_required
    def api_charts():
        return jsonify(
            {
                "count": len(CHARTS),
                "result": CHARTS,
            }
        )

    @app.route("/api/v1/database/")
    @login_required
    def api_databases():
        return jsonify(
            {
                "count": len(DATABASES_LIST),
                "result": DATABASES_LIST,
            }
        )

    @app.route("/api/v1/dataset/")
    @login_required
    def api_datasets():
        return jsonify(
            {
                "count": len(DATASETS),
                "result": DATASETS,
            }
        )

    @app.route("/api/v1/security/csrf_token/")
    @login_required
    def api_csrf_token():
        return jsonify({"result": "not_implemented"})

    # Version info endpoint (public)
    @app.route("/api/v1/version/")
    def api_version():
        return jsonify({"result": "2.0.1"})

    # ---------- Error handlers ----------
    @app.errorhandler(403)
    def forbidden(e):
        return render_template("403.html", app_name=app.config["APPLICATION_NAME"]), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template("404.html", app_name=app.config["APPLICATION_NAME"]), 404

    @app.errorhandler(500)
    def internal_error(e):
        return render_template("500.html", app_name=app.config["APPLICATION_NAME"]), 500
