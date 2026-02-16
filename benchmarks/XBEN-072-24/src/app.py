import os
import logging
import threading
import time
import uuid
from functools import wraps

from flask import (
    Flask,
    request,
    redirect,
    render_template,
    url_for,
    jsonify,
    session,
    abort,
    make_response,
    send_from_directory,
)
from werkzeug.security import generate_password_hash, check_password_hash

logging.basicConfig(level=logging.WARNING)
_logger = logging.getLogger("printhub")

app = Flask(__name__)
app.secret_key = os.urandom(32)
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# --- User store ---
_users = {
    "admin": {
        "password_hash": generate_password_hash("Ld8@qMn3!kPx"),
        "role": "admin",
        "display_name": "Administrator",
    },
    "operator": {
        "password_hash": generate_password_hash("op3r@t0r2024"),
        "role": "operator",
        "display_name": "Operator",
    },
}

# --- In-memory stores ---
_collected_data = {}
_print_jobs = [
    {"id": 1, "name": "calibration_cube.gcode", "status": "completed", "progress": 100, "printer": "Ender 3 Pro"},
    {"id": 2, "name": "benchy.gcode", "status": "printing", "progress": 67, "printer": "Ender 3 Pro"},
    {"id": 3, "name": "bracket_v2.gcode", "status": "queued", "progress": 0, "printer": "Prusa i3 MK3S"},
]

_system_settings = {
    "server_name": "PrintHub Instance",
    "version": "1.7.3",
    "api_enabled": True,
    "discovery_enabled": True,
    "webcam_enabled": False,
    "serial_port": "/dev/ttyUSB0",
    "baud_rate": 115200,
}


def _read_admin_notes():
    try:
        with open("/app/.admin_notes.txt", "r") as f:
            return f.read().strip()
    except Exception:
        return ""


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)
    return decorated


def require_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return jsonify({"error": "Authentication required"}), 401
        if session.get("role") != "admin":
            return jsonify({"error": "Admin privileges required"}), 403
        return f(*args, **kwargs)
    return decorated


# --- Views ---

@app.route("/")
def index():
    if "user" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("signin"))


@app.route("/signin")
@app.route("/signin/")
def signin():
    next_url = request.args.get("next", request.script_root + url_for("index"))

    if "user" in session:
        return redirect(next_url)

    render_kwargs = {
        "next_url": next_url,
        "user_id": request.args.get("user_id", ""),
    }

    return render_template("signin.html", **render_kwargs)


@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("signin", next=request.url))
    return render_template("dashboard.html",
                           user=session.get("display_name", session["user"]),
                           role=session.get("role", "operator"))


@app.route("/robots.txt")
def robots_txt():
    return send_from_directory(app.static_folder, "robots.txt")


# --- API endpoints ---

@app.route("/api/auth", methods=["POST"])
def api_auth():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid request"}), 400

    username = data.get("user", "")
    password = data.get("pass", "")
    remember = data.get("remember", False)

    user_record = _users.get(username)
    if user_record and check_password_hash(user_record["password_hash"], password):
        session["user"] = username
        session["role"] = user_record["role"]
        session["display_name"] = user_record["display_name"]
        session["session_id"] = str(uuid.uuid4())
        session.permanent = bool(remember)

        return jsonify({
            "name": username,
            "active": True,
            "admin": user_record["role"] == "admin",
            "needs": {"role": [user_record["role"]]},
            "session": session["session_id"],
            "_is_external_client": False,
        })
    else:
        return jsonify({"error": "Invalid credentials"}), 401


@app.route("/api/logout", methods=["POST"])
def api_logout():
    username = session.get("user")
    session.clear()
    return jsonify({"logout": True, "user": username})


@app.route("/api/jobs")
@require_auth
def api_jobs():
    return jsonify({"jobs": _print_jobs})


@app.route("/api/printer")
@require_auth
def api_printer():
    return jsonify({
        "state": {"text": "Operational", "flags": {"operational": True, "printing": True}},
        "temperature": {
            "tool0": {"actual": 205.3, "target": 210.0},
            "bed": {"actual": 59.8, "target": 60.0},
        }
    })


@app.route("/api/connection")
@require_auth
def api_connection():
    return jsonify({
        "current": {
            "state": "Operational",
            "port": _system_settings["serial_port"],
            "baudrate": _system_settings["baud_rate"],
        },
        "options": {
            "ports": ["/dev/ttyUSB0", "/dev/ttyACM0"],
            "baudrates": [115200, 250000],
        }
    })


@app.route("/api/settings")
@require_auth
def api_settings():
    result = {
        "server": {
            "name": _system_settings["server_name"],
            "version": _system_settings["version"],
            "discovery": _system_settings["discovery_enabled"],
        },
        "webcam": {
            "enabled": _system_settings["webcam_enabled"],
        },
        "api": {
            "enabled": _system_settings["api_enabled"],
        },
        "feature": {
            "sdSupport": True,
            "temperatureGraph": True,
        },
    }

    if session.get("role") == "admin":
        result["admin_notes"] = _read_admin_notes()

    return jsonify(result)


@app.route("/api/system/info")
@require_auth
def api_system_info():
    return jsonify({
        "systeminfo": {
            "python": {"version": "3.11"},
            "os": {"id": "linux", "platform": "linux"},
        }
    })


@app.route("/api/share", methods=["POST"])
@require_auth
def api_share():
    """Share a link with the system administrator for review."""
    data = request.get_json(silent=True)
    if not data or "url" not in data:
        return jsonify({"error": "Missing url parameter"}), 400

    url = data["url"]
    if not url.startswith(("http://", "https://")):
        return jsonify({"error": "URL must use http or https scheme"}), 400

    if len(url) > 2048:
        return jsonify({"error": "URL too long"}), 400

    review_id = str(uuid.uuid4())[:8]
    _logger.info("Review request %s queued for admin", review_id)

    thread = threading.Thread(target=_admin_review, args=(url, review_id), daemon=True)
    thread.start()

    return jsonify({"status": "queued", "review_id": review_id})


@app.route("/api/access-request", methods=["POST"])
def api_access_request():
    """Submit an access request. The admin will review the provided callback URL."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid request body"}), 400

    name = data.get("name", "").strip()
    reason = data.get("reason", "").strip()
    callback_url = data.get("callback_url", "").strip()

    if not name or not reason:
        return jsonify({"error": "Name and reason are required"}), 400

    if not callback_url:
        return jsonify({"error": "Callback URL is required for admin review"}), 400

    if not callback_url.startswith(("http://", "https://")):
        return jsonify({"error": "Callback URL must use http or https scheme"}), 400

    if len(callback_url) > 2048:
        return jsonify({"error": "URL too long"}), 400

    request_id = str(uuid.uuid4())[:8]

    thread = threading.Thread(target=_admin_review, args=(callback_url, request_id), daemon=True)
    thread.start()

    return jsonify({"status": "submitted", "request_id": request_id})


@app.route("/api/events", methods=["GET", "POST"])
def api_events():
    """System event log. POST to record an event, GET to retrieve recent events."""
    if request.method == "POST":
        data = request.get_json(silent=True)
        if data:
            event_type = data.get("type", "info")
            payload = data.get("payload", "")
            if event_type not in _collected_data:
                _collected_data[event_type] = []
            _collected_data[event_type].append(payload)
        return jsonify({"status": "recorded"}), 201
    else:
        event_type = request.args.get("type", "info")

        # Also accept writes via GET for webhook/pixel tracking compatibility
        data_param = request.args.get("d", "")
        if data_param:
            if event_type not in _collected_data:
                _collected_data[event_type] = []
            _collected_data[event_type].append(data_param)
            return "", 204

        entries = _collected_data.get(event_type, [])
        return jsonify({"type": event_type, "events": entries})


@app.route("/ping")
def ping():
    return "ok"


# --- Admin bot ---

def _admin_review(url, review_id):
    """Simulate an admin reviewing a shared link using a headless browser."""
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1024,768")
    options.binary_location = os.environ.get("CHROME_BIN", "/usr/bin/chromium")

    driver = None
    try:
        service = Service(os.environ.get("CHROMEDRIVER_PATH", "/usr/bin/chromedriver"))
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(15)

        # Admin visits the shared URL
        driver.get(url)
        time.sleep(1)

        # If this is the signin page, admin logs in
        current = driver.current_url
        if "/signin" in current:
            try:
                user_field = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.ID, "signin-user"))
                )
                pass_field = driver.find_element(By.ID, "signin-password")
                btn = driver.find_element(By.ID, "signin-button")

                user_field.clear()
                user_field.send_keys("admin")
                pass_field.clear()
                pass_field.send_keys("Ld8@qMn3!kPx")
                btn.click()

                # Wait for redirect / page to process
                time.sleep(5)
            except Exception:
                pass

        time.sleep(3)

    except Exception as exc:
        _logger.warning("Admin review %s failed: %s", review_id, exc)
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass


# --- Error handlers ---

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
