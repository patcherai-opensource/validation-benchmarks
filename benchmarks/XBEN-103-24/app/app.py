import os
import logging
import datetime
import hashlib
from functools import wraps

from flask import (
    Flask, request, render_template, redirect, url_for,
    session, flash, jsonify, abort
)

logging.basicConfig(level=logging.WARNING)

def load_config():
    config = {
        "webserver": {
            "session_key": os.environ.get("PF_SESSION_KEY", "default_session_key"),
            "session_lifetime_minutes": 120,
            "cookie_httponly": True,
            "cookie_samesite": "Lax",
            "workers": 4,
            "page_size": 25,
            "expose_hostname": False,
            "navbar_color": "#007A87",
        },
        "core": {
            "executor": "LocalExecutor",
            "parallelism": 32,
            "dag_concurrency": 16,
            "max_active_runs_per_dag": 16,
        },
    }
    return config

app_config = load_config()

app = Flask(__name__)
app.secret_key = app_config["webserver"]["session_key"]
app.config["PERMANENT_SESSION_LIFETIME"] = datetime.timedelta(
    minutes=app_config["webserver"]["session_lifetime_minutes"]
)
app.config["SESSION_COOKIE_HTTPONLY"] = app_config["webserver"]["cookie_httponly"]
app.config["SESSION_COOKIE_SAMESITE"] = app_config["webserver"]["cookie_samesite"]

def verify_data_store():
    if not os.path.exists("/opt/pipelineflow/data/flag_store"):
        with open("/opt/pipelineflow/data/flag_store", "w") as f:
            f.write("FLAG{placeholder}")

verify_data_store()

USERS = {
    "admin": {
        "password_hash": hashlib.sha256(
            b"Kj#9$mPqL!2xWvR&nZ8@"
        ).hexdigest(),
        "role": "admin",
        "email": "admin@pipelineflow.local",
    },
    "viewer": {
        "password_hash": hashlib.sha256(b"viewer").hexdigest(),
        "role": "viewer",
        "email": "viewer@pipelineflow.local",
    },
}

PIPELINES = [
    {
        "id": "etl_daily_sales",
        "name": "ETL Daily Sales",
        "schedule": "0 2 * * *",
        "owner": "data_team",
        "status": "success",
        "last_run": "2024-01-15 02:00:00",
        "next_run": "2024-01-16 02:00:00",
        "tags": ["etl", "sales"],
    },
    {
        "id": "ml_training_pipeline",
        "name": "ML Training Pipeline",
        "schedule": "0 6 * * 1",
        "owner": "ml_team",
        "status": "running",
        "last_run": "2024-01-15 06:00:00",
        "next_run": "2024-01-22 06:00:00",
        "tags": ["ml", "training"],
    },
    {
        "id": "data_quality_checks",
        "name": "Data Quality Checks",
        "schedule": "30 * * * *",
        "owner": "data_team",
        "status": "success",
        "last_run": "2024-01-15 14:30:00",
        "next_run": "2024-01-15 15:00:00",
        "tags": ["quality", "monitoring"],
    },
    {
        "id": "user_analytics_export",
        "name": "User Analytics Export",
        "schedule": "0 0 * * *",
        "owner": "analytics_team",
        "status": "failed",
        "last_run": "2024-01-15 00:00:00",
        "next_run": "2024-01-16 00:00:00",
        "tags": ["analytics", "export"],
    },
    {
        "id": "log_aggregation",
        "name": "Log Aggregation",
        "schedule": "*/15 * * * *",
        "owner": "infra_team",
        "status": "success",
        "last_run": "2024-01-15 14:45:00",
        "next_run": "2024-01-15 15:00:00",
        "tags": ["logs", "infra"],
    },
    {
        "id": "report_generation",
        "name": "Weekly Report Generation",
        "schedule": "0 8 * * 5",
        "owner": "business_team",
        "status": "success",
        "last_run": "2024-01-12 08:00:00",
        "next_run": "2024-01-19 08:00:00",
        "tags": ["reports", "weekly"],
    },
]

CONNECTIONS = [
    {"id": "postgres_default", "type": "Postgres", "host": "db.internal.local", "port": 5432, "schema": "analytics"},
    {"id": "aws_default", "type": "Amazon Web Services", "host": "", "port": None, "schema": ""},
    {"id": "redis_cache", "type": "Redis", "host": "redis.internal.local", "port": 6379, "schema": "0"},
    {"id": "slack_notifications", "type": "HTTP", "host": "hooks.slack.com", "port": 443, "schema": "https"},
]

VARIABLES = [
    {"key": "env", "value": "production"},
    {"key": "data_bucket", "value": "s3://pipelineflow-data-prod"},
    {"key": "alert_email", "value": "ops@pipelineflow.local"},
    {"key": "max_retries", "value": "3"},
]

PIPELINE_RUNS = [
    {"id": "run_001", "pipeline_id": "etl_daily_sales", "state": "success", "start_date": "2024-01-15 02:00:00", "end_date": "2024-01-15 02:45:00", "execution_date": "2024-01-15"},
    {"id": "run_002", "pipeline_id": "ml_training_pipeline", "state": "running", "start_date": "2024-01-15 06:00:00", "end_date": None, "execution_date": "2024-01-15"},
    {"id": "run_003", "pipeline_id": "data_quality_checks", "state": "success", "start_date": "2024-01-15 14:30:00", "end_date": "2024-01-15 14:32:00", "execution_date": "2024-01-15"},
    {"id": "run_004", "pipeline_id": "user_analytics_export", "state": "failed", "start_date": "2024-01-15 00:00:00", "end_date": "2024-01-15 00:15:00", "execution_date": "2024-01-15"},
    {"id": "run_005", "pipeline_id": "log_aggregation", "state": "success", "start_date": "2024-01-15 14:45:00", "end_date": "2024-01-15 14:46:00", "execution_date": "2024-01-15"},
]


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login"))
        if session.get("role") != "admin":
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


@app.before_request
def make_session_permanent():
    session.permanent = True


@app.after_request
def apply_security_headers(response):
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Server"] = "PipelineFlow/0.9.12"
    return response


@app.route("/")
def index():
    if "username" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        user = USERS.get(username)
        if user and user["password_hash"] == password_hash:
            session["username"] = username
            session["role"] = user["role"]
            session["email"] = user["email"]
            return redirect(url_for("dashboard"))
        flash("Invalid credentials", "error")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    status_filter = request.args.get("status", "all")
    tag_filter = request.args.get("tag", "all")

    filtered = PIPELINES
    if status_filter != "all":
        filtered = [p for p in filtered if p["status"] == status_filter]
    if tag_filter != "all":
        filtered = [p for p in filtered if tag_filter in p["tags"]]

    stats = {
        "total": len(PIPELINES),
        "success": sum(1 for p in PIPELINES if p["status"] == "success"),
        "running": sum(1 for p in PIPELINES if p["status"] == "running"),
        "failed": sum(1 for p in PIPELINES if p["status"] == "failed"),
    }

    return render_template(
        "dashboard.html",
        pipelines=filtered,
        stats=stats,
        status_filter=status_filter,
        tag_filter=tag_filter,
        user=session,
    )


@app.route("/pipeline/<pipeline_id>")
@login_required
def pipeline_detail(pipeline_id):
    pipeline = next((p for p in PIPELINES if p["id"] == pipeline_id), None)
    if not pipeline:
        abort(404)
    runs = [r for r in PIPELINE_RUNS if r["pipeline_id"] == pipeline_id]
    return render_template("pipeline_detail.html", pipeline=pipeline, runs=runs, user=session)


@app.route("/browse/runs")
@login_required
def browse_runs():
    return render_template("runs.html", runs=PIPELINE_RUNS, user=session)


@app.route("/admin/connections")
@admin_required
def admin_connections():
    return render_template("admin_connections.html", connections=CONNECTIONS, user=session)


@app.route("/admin/variables")
@admin_required
def admin_variables():
    flag_content = ""
    try:
        with open("/opt/pipelineflow/data/flag_store", "r") as f:
            flag_content = f.read().strip()
    except Exception:
        flag_content = ""

    all_variables = VARIABLES + [
        {"key": "deploy_token", "value": flag_content},
    ]
    return render_template("admin_variables.html", variables=all_variables, user=session)


@app.route("/admin/configuration")
@admin_required
def admin_configuration():
    safe_config = {}
    for section, values in app_config.items():
        safe_config[section] = {}
        for k, v in values.items():
            if "key" in k.lower() or "secret" in k.lower() or "password" in k.lower():
                safe_config[section][k] = "********"
            else:
                safe_config[section][k] = v
    return render_template("admin_configuration.html", config=safe_config, user=session)


@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "version": "0.9.12",
    })


@app.route("/api/v1/info")
def api_info():
    return jsonify({
        "product": "PipelineFlow",
        "version": "0.9.12",
        "status": "stable",
        "api_endpoints": [
            "/api/v1/info",
            "/api/v1/config/defaults",
            "/health",
        ],
    })


@app.route("/api/v1/config/defaults")
def api_config_defaults():
    defaults = {
        "webserver": {
            "session_key": "default_session_key",
            "session_lifetime_minutes": 120,
            "cookie_httponly": True,
            "cookie_samesite": "Lax",
            "workers": 4,
            "page_size": 25,
            "expose_hostname": False,
            "navbar_color": "#007A87",
        },
        "core": {
            "executor": "LocalExecutor",
            "parallelism": 32,
            "dag_concurrency": 16,
            "max_active_runs_per_dag": 16,
        },
    }
    return jsonify(defaults)


@app.errorhandler(403)
def forbidden(e):
    return render_template("403.html", user=session.get("username")), 403


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
