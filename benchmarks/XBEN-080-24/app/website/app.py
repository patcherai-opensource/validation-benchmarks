import os
import json
import uuid
import hashlib
import sqlite3
import functools
from datetime import datetime

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, jsonify, flash, g
)
from jinja2 import Template
from markupsafe import escape

app = Flask(__name__, static_folder='static/')
app.secret_key = os.urandom(32)

DATABASE = '/app/streampark.db'


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exc):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DATABASE)
    db.executescript("""
        CREATE TABLE IF NOT EXISTS t_user (
            user_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            username   TEXT UNIQUE NOT NULL,
            password   TEXT NOT NULL,
            nick_name  TEXT,
            user_type  INTEGER DEFAULT 2,
            status     INTEGER DEFAULT 1,
            create_time TEXT
        );

        CREATE TABLE IF NOT EXISTS t_flink_app (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            app_name     TEXT NOT NULL,
            app_type     INTEGER DEFAULT 1,
            job_type     INTEGER DEFAULT 1,
            execution_mode INTEGER DEFAULT 1,
            state        INTEGER DEFAULT 0,
            owner_id     INTEGER,
            create_time  TEXT
        );

        CREATE TABLE IF NOT EXISTS t_alert_config (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         INTEGER NOT NULL,
            alert_name      TEXT NOT NULL,
            alert_type      INTEGER DEFAULT 4,
            email_params    TEXT,
            ding_talk_params TEXT,
            we_com_params   TEXT,
            http_callback_params TEXT,
            lark_params     TEXT,
            create_time     TEXT,
            modify_time     TEXT
        );

        CREATE TABLE IF NOT EXISTS t_setting (
            order_num   INTEGER PRIMARY KEY,
            setting_key TEXT NOT NULL,
            setting_value TEXT,
            setting_name TEXT,
            description TEXT,
            type        INTEGER DEFAULT 1
        );
    """)

    # Seed default admin user (password: streampark)
    pw_hash = hashlib.sha256("streampark".encode()).hexdigest()
    try:
        db.execute(
            "INSERT INTO t_user (username, password, nick_name, user_type, status, create_time) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            ("admin", pw_hash, "Administrator", 1, 1, datetime.utcnow().isoformat())
        )
    except sqlite3.IntegrityError:
        pass

    # Seed a regular user (password: user123)
    pw_hash2 = hashlib.sha256("user123".encode()).hexdigest()
    try:
        db.execute(
            "INSERT INTO t_user (username, password, nick_name, user_type, status, create_time) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            ("developer", pw_hash2, "Dev User", 2, 1, datetime.utcnow().isoformat())
        )
    except sqlite3.IntegrityError:
        pass

    # Seed some Flink applications
    for app_name in ["realtime-etl-job", "fraud-detection-stream", "log-aggregator", "metrics-pipeline"]:
        try:
            db.execute(
                "INSERT INTO t_flink_app (app_name, app_type, job_type, execution_mode, state, owner_id, create_time) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (app_name, 1, 2, 4, 1, 1, datetime.utcnow().isoformat())
            )
        except Exception:
            pass

    # Seed platform settings
    settings = [
        (1, "streampark.maven.central.repository", "https://repo1.maven.org/maven2/", "Maven Central", "Maven central repository URL", 1),
        (2, "streampark.workspace.local", "/opt/streampark/workspace", "Local Workspace", "Local workspace directory", 1),
        (3, "streampark.workspace.remote", "hdfs:///streampark/workspace", "Remote Workspace", "Remote HDFS workspace", 1),
        (4, "alert.max.retry", "3", "Alert Max Retry", "Maximum number of alert retries", 2),
        (5, "docker.register.address", "registry.example.com", "Docker Registry", "Docker registry address", 1),
    ]
    for s in settings:
        try:
            db.execute(
                "INSERT INTO t_setting (order_num, setting_key, setting_value, setting_name, description, type) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                s
            )
        except sqlite3.IntegrityError:
            pass

    db.commit()
    db.close()


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

def login_required(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            if request.is_json or request.path.startswith("/flink/"):
                return jsonify({"code": 401, "message": "Not authenticated"}), 401
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


# ---------------------------------------------------------------------------
# Routes – Public
# ---------------------------------------------------------------------------

@app.route('/')
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route('/user/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()

    if not username or not password:
        flash("Username and password are required.", "danger")
        return render_template('login.html'), 400

    db = get_db()
    pw_hash = hashlib.sha256(password.encode()).hexdigest()
    user = db.execute(
        "SELECT * FROM t_user WHERE username = ? AND password = ? AND status = 1",
        (username, pw_hash)
    ).fetchone()

    if user is None:
        flash("Invalid credentials.", "danger")
        return render_template('login.html'), 401

    session["user_id"] = user["user_id"]
    session["username"] = user["username"]
    session["nick_name"] = user["nick_name"]
    session["user_type"] = user["user_type"]
    return redirect(url_for("dashboard"))


@app.route('/user/logout')
def logout():
    session.clear()
    return redirect(url_for("login"))


# ---------------------------------------------------------------------------
# Routes – Dashboard & Applications
# ---------------------------------------------------------------------------

@app.route('/dashboard')
@login_required
def dashboard():
    db = get_db()
    apps = db.execute("SELECT * FROM t_flink_app ORDER BY id").fetchall()
    alerts = db.execute(
        "SELECT * FROM t_alert_config WHERE user_id = ? ORDER BY id",
        (session["user_id"],)
    ).fetchall()
    return render_template('dashboard.html', apps=apps, alerts=alerts)


@app.route('/flink/app/list')
@login_required
def app_list():
    db = get_db()
    apps = db.execute("SELECT * FROM t_flink_app ORDER BY id").fetchall()
    result = []
    for a in apps:
        result.append({
            "id": a["id"],
            "appName": a["app_name"],
            "appType": a["app_type"],
            "jobType": a["job_type"],
            "executionMode": a["execution_mode"],
            "state": a["state"],
            "createTime": a["create_time"]
        })
    return jsonify({"code": 200, "data": result})


# ---------------------------------------------------------------------------
# Routes – Alert Configuration (CVE-2024-29178 equivalent)
# ---------------------------------------------------------------------------

@app.route('/flink/alert/list')
@login_required
def alert_list():
    db = get_db()
    alerts = db.execute(
        "SELECT * FROM t_alert_config WHERE user_id = ? ORDER BY id",
        (session["user_id"],)
    ).fetchall()
    result = []
    for a in alerts:
        result.append({
            "id": a["id"],
            "alertName": a["alert_name"],
            "alertType": a["alert_type"],
            "httpCallbackParams": json.loads(a["http_callback_params"]) if a["http_callback_params"] else None,
            "createTime": a["create_time"],
            "modifyTime": a["modify_time"]
        })
    return jsonify({"code": 200, "data": result})


@app.route('/flink/alert/add', methods=['POST'])
@login_required
def alert_add():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()

    alert_name = data.get("alertName", "").strip()
    alert_type = int(data.get("alertType", 4))

    http_callback_raw = data.get("httpCallbackParams")
    if isinstance(http_callback_raw, str):
        try:
            http_callback_raw = json.loads(http_callback_raw)
        except json.JSONDecodeError:
            return jsonify({"code": 400, "message": "Invalid httpCallbackParams JSON"}), 400
    elif http_callback_raw is None:
        http_callback_raw = {}

    if not alert_name:
        return jsonify({"code": 400, "message": "alertName is required"}), 400

    now = datetime.utcnow().isoformat()
    db = get_db()
    cursor = db.execute(
        "INSERT INTO t_alert_config (user_id, alert_name, alert_type, http_callback_params, create_time, modify_time) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (session["user_id"], alert_name, alert_type, json.dumps(http_callback_raw), now, now)
    )
    db.commit()

    return jsonify({"code": 200, "message": "Alert config created successfully", "data": {"id": cursor.lastrowid}})


@app.route('/flink/alert/update', methods=['POST', 'PUT'])
@login_required
def alert_update():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()

    alert_id = data.get("id")
    if not alert_id:
        return jsonify({"code": 400, "message": "Alert id is required"}), 400

    db = get_db()
    existing = db.execute(
        "SELECT * FROM t_alert_config WHERE id = ? AND user_id = ?",
        (alert_id, session["user_id"])
    ).fetchone()
    if not existing:
        return jsonify({"code": 404, "message": "Alert config not found"}), 404

    alert_name = data.get("alertName", existing["alert_name"])
    alert_type = int(data.get("alertType", existing["alert_type"]))

    http_callback_raw = data.get("httpCallbackParams")
    if isinstance(http_callback_raw, str):
        try:
            http_callback_raw = json.loads(http_callback_raw)
        except json.JSONDecodeError:
            return jsonify({"code": 400, "message": "Invalid httpCallbackParams JSON"}), 400
    elif http_callback_raw is None:
        http_callback_raw = json.loads(existing["http_callback_params"]) if existing["http_callback_params"] else {}

    now = datetime.utcnow().isoformat()
    db.execute(
        "UPDATE t_alert_config SET alert_name = ?, alert_type = ?, http_callback_params = ?, modify_time = ? "
        "WHERE id = ? AND user_id = ?",
        (alert_name, alert_type, json.dumps(http_callback_raw), now, alert_id, session["user_id"])
    )
    db.commit()

    return jsonify({"code": 200, "message": "Alert config updated successfully"})


@app.route('/flink/alert/delete', methods=['POST', 'DELETE'])
@login_required
def alert_delete():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()

    alert_id = data.get("id")
    if not alert_id:
        return jsonify({"code": 400, "message": "Alert id is required"}), 400

    db = get_db()
    db.execute(
        "DELETE FROM t_alert_config WHERE id = ? AND user_id = ?",
        (alert_id, session["user_id"])
    )
    db.commit()
    return jsonify({"code": 200, "message": "Alert config deleted"})


@app.route('/flink/alert/send', methods=['POST'])
@login_required
def alert_send():
    """
    Send/test an alert notification. This renders the configured request template
    with the alert context variables and returns the formatted output.
    """
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()

    alert_id = data.get("id")
    if not alert_id:
        return jsonify({"code": 400, "message": "Alert id is required"}), 400

    db = get_db()
    alert_config = db.execute(
        "SELECT * FROM t_alert_config WHERE id = ? AND user_id = ?",
        (alert_id, session["user_id"])
    ).fetchone()

    if not alert_config:
        return jsonify({"code": 404, "message": "Alert config not found"}), 404

    http_params = json.loads(alert_config["http_callback_params"]) if alert_config["http_callback_params"] else {}
    request_template = http_params.get("requestTemplate", "")

    if not request_template:
        return jsonify({"code": 400, "message": "No requestTemplate configured for this alert"}), 400

    # Alert context variables available during template rendering
    alert_template = {
        "title": "StreamPark Alert Notification",
        "alertType": alert_config["alert_type"],
        "alertName": alert_config["alert_name"],
        "alertId": alert_config["id"],
        "jobName": data.get("jobName", "realtime-etl-job"),
        "status": data.get("status", "FAILED"),
        "startTime": datetime.utcnow().isoformat(),
        "duration": "00:15:32",
        "restartCount": 3,
    }

    try:
        # Process the request template using the template engine
        template = Template(request_template)
        formatted = template.render(alert=alert_template)
        return jsonify({
            "code": 200,
            "message": "Alert sent successfully",
            "data": {"rendered": formatted}
        })
    except Exception:
        return jsonify({"code": 500, "message": "Failed to process alert template"}), 500


# ---------------------------------------------------------------------------
# Routes – Settings
# ---------------------------------------------------------------------------

@app.route('/flink/setting/list')
@login_required
def setting_list():
    db = get_db()
    settings = db.execute("SELECT * FROM t_setting ORDER BY order_num").fetchall()
    result = []
    for s in settings:
        result.append({
            "orderNum": s["order_num"],
            "settingKey": s["setting_key"],
            "settingValue": s["setting_value"],
            "settingName": s["setting_name"],
            "description": s["description"]
        })
    return jsonify({"code": 200, "data": result})


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.route('/ping')
def ping():
    return "pong", 200


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------

@app.errorhandler(404)
def not_found(e):
    if request.is_json or request.path.startswith("/flink/"):
        return jsonify({"code": 404, "message": "Not found"}), 404
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(e):
    if request.is_json or request.path.startswith("/flink/"):
        return jsonify({"code": 500, "message": "Internal server error"}), 500
    return render_template("500.html"), 500


# ---------------------------------------------------------------------------
# Startup
# ---------------------------------------------------------------------------

init_db()

if __name__ == '__main__':
    app.run()
