import os
import json
import time
import uuid
import hashlib
import logging
import subprocess
import threading
from functools import wraps

from flask import (
    Flask, request, redirect, render_template, jsonify,
    make_response, url_for, abort, session, g
)

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("octoprint.server")

app = Flask(__name__)
app.secret_key = os.urandom(32).hex()

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

ADMIN_API_KEY = hashlib.sha256(os.urandom(32)).hexdigest()
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD_HASH = hashlib.sha256(b"octoprint-admin-2023!").hexdigest()
ADMIN_SESSION_ID = hashlib.sha256(os.urandom(32)).hexdigest()

FLAG_FILE = "/opt/octoprint/flag.txt"

_webhook_store = {}
_webhook_lock = threading.Lock()

# ---------------------------------------------------------------------------
# User database (in-memory, populated at startup)
# ---------------------------------------------------------------------------

USERS = {
    "admin": {
        "name": "admin",
        "password_hash": ADMIN_PASSWORD_HASH,
        "active": True,
        "admin": True,
        "apikey": ADMIN_API_KEY,
        "settings": {}
    }
}

# ---------------------------------------------------------------------------
# Session / auth helpers
# ---------------------------------------------------------------------------

ACTIVE_SESSIONS = {
    ADMIN_SESSION_ID: "admin"
}


def get_current_user():
    """Resolve the current user from session cookie or API key header."""
    # Check session cookie
    sess_id = request.cookies.get("octoprint_session")
    if sess_id and sess_id in ACTIVE_SESSIONS:
        uname = ACTIVE_SESSIONS[sess_id]
        return USERS.get(uname)
    # Check API key header
    api_key = request.headers.get("X-Api-Key")
    if api_key:
        for u in USERS.values():
            if u["apikey"] == api_key:
                return u
    return None


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({"error": "Unauthorized"}), 401
        g.user = user
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user()
        if not user or not user.get("admin"):
            return jsonify({"error": "Forbidden"}), 403
        g.user = user
        return f(*args, **kwargs)
    return decorated


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.route("/ping")
def ping():
    return "pong", 200


# ---------------------------------------------------------------------------
# Index – serve the OctoPrint UI shell
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    user = get_current_user()
    if user:
        return render_template("index.jinja2", user=user)
    return redirect(url_for("login"))


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    redirect_url = request.args.get("redirect", url_for("index"))

    if request.method == "POST":
        username = request.form.get("user", "")
        password = request.form.get("pass", "")
        pw_hash = hashlib.sha256(password.encode()).hexdigest()

        user = USERS.get(username)
        if user and user["password_hash"] == pw_hash and user["active"]:
            sess_id = hashlib.sha256(os.urandom(32)).hexdigest()
            ACTIVE_SESSIONS[sess_id] = username
            resp = redirect(redirect_url)
            resp.set_cookie("octoprint_session", sess_id, httponly=False, samesite="Lax")
            return resp

        return render_template(
            "login.jinja2",
            redirect_url=redirect_url,
            error="Incorrect username or password",
            version=_version_string(),
        )

    return render_template(
        "login.jinja2",
        redirect_url=redirect_url,
        error=None,
        version=_version_string(),
    )


@app.route("/api/login", methods=["POST"])
def api_login():
    """AJAX login endpoint used by the login page JavaScript."""
    data = request.get_json(silent=True) or {}
    username = data.get("user", "")
    password = data.get("pass", "")
    pw_hash = hashlib.sha256(password.encode()).hexdigest()

    user = USERS.get(username)
    if user and user["password_hash"] == pw_hash and user["active"]:
        sess_id = hashlib.sha256(os.urandom(32)).hexdigest()
        ACTIVE_SESSIONS[sess_id] = username
        resp = jsonify({"name": username, "active": True, "admin": user["admin"]})
        resp.set_cookie("octoprint_session", sess_id, httponly=False, samesite="Lax")
        return resp

    return jsonify({"error": "Incorrect username or password"}), 401


@app.route("/logout")
def logout():
    sess_id = request.cookies.get("octoprint_session")
    if sess_id and sess_id in ACTIVE_SESSIONS:
        del ACTIVE_SESSIONS[sess_id]
    resp = redirect(url_for("login"))
    resp.delete_cookie("octoprint_session")
    return resp


# ---------------------------------------------------------------------------
# API endpoints  (mirrors real OctoPrint REST API structure)
# ---------------------------------------------------------------------------

@app.route("/api/version")
def api_version():
    return jsonify({
        "api": "0.1",
        "server": "1.7.3",
        "text": "OctoPrint 1.7.3"
    })


@app.route("/api/settings")
@admin_required
def api_settings():
    """Return the current settings for the authenticated admin user."""
    try:
        secret_key = open(FLAG_FILE).read().strip()
    except FileNotFoundError:
        secret_key = ""

    return jsonify({
        "api": {"key": g.user["apikey"], "allowCrossOrigin": False},
        "appearance": {
            "name": "OctoPrint",
            "color": "default",
            "colorTransparent": False,
            "defaultLanguage": "_default"
        },
        "feature": {
            "temperatureGraph": True,
            "sdSupport": True,
            "keyboardControl": True,
            "modelSizeDetection": True,
        },
        "folder": {
            "uploads": "/home/octoprint/.octoprint/uploads",
            "timelapse": "/home/octoprint/.octoprint/timelapse",
        },
        "plugins": {},
        "printer": {
            "defaultExtrusionLength": 5
        },
        "scripts": {},
        "serial": {
            "port": None,
            "baudrate": None,
            "autoconnect": False,
        },
        "server": {
            "commands": {},
            "diskspace": {"warning": 500, "critical": 200},
            "onlineCheck": {"enabled": False},
            "pluginBlacklist": {"enabled": False},
            "secretKey": secret_key,
        },
        "temperature": {},
        "terminalFilters": [],
        "webcam": {
            "stream": "/webcam/?action=stream",
            "snapshot": "http://127.0.0.1:8080/?action=snapshot",
            "ffmpeg": "/usr/bin/ffmpeg"
        }
    })


@app.route("/api/printer")
@login_required
def api_printer():
    return jsonify({
        "state": {
            "text": "Operational",
            "flags": {
                "operational": True,
                "printing": False,
                "cancelling": False,
                "pausing": False,
                "error": False,
                "ready": True,
            }
        },
        "temperature": {
            "tool0": {"actual": 21.3, "target": 0.0},
            "bed": {"actual": 20.1, "target": 0.0}
        }
    })


@app.route("/api/job")
@login_required
def api_job():
    return jsonify({
        "job": {
            "file": {"name": None, "origin": None, "size": None},
            "estimatedPrintTime": None,
            "filament": None
        },
        "progress": {
            "completion": None,
            "filepos": None,
            "printTime": None,
            "printTimeLeft": None
        },
        "state": "Operational"
    })


@app.route("/api/files")
@login_required
def api_files():
    return jsonify({
        "files": [
            {
                "name": "benchy.gcode",
                "origin": "local",
                "size": 1048576,
                "date": 1672531200,
            }
        ],
        "free": "2.1GB",
        "total": "7.4GB"
    })


@app.route("/api/connection")
@login_required
def api_connection():
    return jsonify({
        "current": {
            "state": "Operational",
            "port": "/dev/ttyUSB0",
            "baudrate": 115200,
            "printerProfile": "_default"
        },
        "options": {
            "ports": ["/dev/ttyUSB0", "/dev/ttyACM0"],
            "baudrates": [115200, 250000, 230400, 57600, 38400, 19200, 9600],
            "printerProfiles": [{"id": "_default", "name": "Default"}],
        }
    })


# ---------------------------------------------------------------------------
# Webhook / request-bin  (for exfiltrating data from XSS)
#
# This simulates a simple data capture endpoint.  In a real XSS attack
# the attacker would control their own server; here we provide one inside
# the application so the challenge is self-contained.
# ---------------------------------------------------------------------------

@app.route("/api/util/test", methods=["POST"])
def util_test_notification():
    """Test a notification URL by having the server visit it."""
    data = request.get_json(silent=True) or {}
    target_url = data.get("url", "")

    if not target_url:
        return jsonify({"error": "Missing 'url' parameter"}), 400

    allowed_prefixes = [
        "http://localhost:5000/",
        "http://127.0.0.1:5000/",
    ]

    base_url = os.environ.get("APP_BASE_URL", "http://localhost:5000")
    if base_url and not base_url.endswith("/"):
        base_url += "/"
    allowed_prefixes.append(base_url)

    if not any(target_url.startswith(p) for p in allowed_prefixes):
        return jsonify({"error": "URL must point to this OctoPrint instance"}), 400

    def _visit():
        try:
            _run_bot(target_url)
        except Exception as e:
            logger.error("Bot error: %s", e)

    t = threading.Thread(target=_visit, daemon=True)
    t.start()

    return jsonify({"result": True, "message": "Notification test sent"})


@app.route("/api/webhook/<hook_id>", methods=["GET", "POST"])
def webhook(hook_id):
    """Webhook receiver for plugin notification callbacks."""
    if request.method == "POST":
        payload = request.get_data(as_text=True)
        with _webhook_lock:
            if hook_id not in _webhook_store:
                _webhook_store[hook_id] = []
            _webhook_store[hook_id].append({
                "timestamp": time.time(),
                "data": payload,
                "args": dict(request.args),
            })
        return jsonify({"status": "ok"})

    # GET — retrieve captured data
    if request.args.get("data"):
        payload = request.args.get("data", "")
        with _webhook_lock:
            if hook_id not in _webhook_store:
                _webhook_store[hook_id] = []
            _webhook_store[hook_id].append({
                "timestamp": time.time(),
                "data": payload,
                "args": dict(request.args),
            })
        return jsonify({"status": "ok"})

    with _webhook_lock:
        entries = _webhook_store.get(hook_id, [])
    return jsonify({"entries": entries})


# ---------------------------------------------------------------------------
# Internal browser for notification testing
# ---------------------------------------------------------------------------

def _run_bot(url):
    """Visit the given URL using a headless browser with admin credentials."""
    # Sanitize the URL for safe embedding in JS string literal
    safe_url = url.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "").replace("\r", "")

    script = f"""
var page = require('webpage').create();
page.customHeaders = {{}};
page.settings.resourceTimeout = 5000;

phantom.addCookie({{
    'name': 'octoprint_session',
    'value': '{ADMIN_SESSION_ID}',
    'domain': '127.0.0.1',
    'path': '/'
}});

phantom.addCookie({{
    'name': 'octoprint_session',
    'value': '{ADMIN_SESSION_ID}',
    'domain': 'localhost',
    'path': '/'
}});

page.onConsoleMessage = function(msg) {{}};
page.onError = function(msg, trace) {{}};
page.onNavigationRequested = function(url, type, willNavigate, main) {{
    if (main && page._loaded) {{
        phantom.exit(0);
    }}
}};

page.open('{safe_url}', function(status) {{
    page._loaded = true;
    if (status === 'success') {{
        setTimeout(function() {{
            phantom.exit(0);
        }}, 3000);
    }} else {{
        phantom.exit(1);
    }}
}});

setTimeout(function() {{
    phantom.exit(0);
}}, 6000);
"""
    tmpfile = f"/tmp/bot_{uuid.uuid4().hex}.js"
    try:
        with open(tmpfile, "w") as f:
            f.write(script)
        subprocess.run(
            ["timeout", "12", "phantomjs", "--ignore-ssl-errors=true",
             "--web-security=false", tmpfile],
            capture_output=True, timeout=15
        )
    except Exception:
        pass
    finally:
        try:
            os.unlink(tmpfile)
        except OSError:
            pass


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _version_string():
    return "OctoPrint 1.7.3"


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------

@app.errorhandler(404)
def not_found(e):
    if request.path.startswith("/api/"):
        return jsonify({"error": "Not found"}), 404
    return render_template("404.jinja2", version=_version_string()), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
