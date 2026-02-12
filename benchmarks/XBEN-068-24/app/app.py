import os
import json
import time
import hashlib
import logging
from datetime import datetime

from flask import Flask, request, jsonify, render_template, session, abort

from asteval import Interpreter

app = Flask(__name__)
app.secret_key = os.urandom(32)

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("calcengine")

# Version info
APP_VERSION = "2.4.1"
BUILD_ID = "ce-" + hashlib.md5(str(time.time()).encode()).hexdigest()[:8]

# Rate limiting state (simple in-memory)
_request_counts = {}
RATE_LIMIT = 30  # requests per minute
RATE_WINDOW = 60

# Session-based interpreter pool
_interpreters = {}
MAX_SESSIONS = 100
MAX_EXPR_LENGTH = 10000
EVAL_TIMEOUT = 30


def create_interpreter():
    """Create a hardened asteval Interpreter."""
    interp = Interpreter()
    # Remove file I/O builtins for security
    for name in ("open", "file", "input"):
        interp.symtable.pop(name, None)
    return interp


def get_interpreter(session_id):
    """Get or create an asteval Interpreter for this session."""
    if session_id not in _interpreters:
        if len(_interpreters) >= MAX_SESSIONS:
            oldest = min(_interpreters, key=lambda k: _interpreters[k]["last_used"])
            del _interpreters[oldest]
        interp = create_interpreter()
        _interpreters[session_id] = {
            "interpreter": interp,
            "created": time.time(),
            "last_used": time.time(),
            "eval_count": 0,
        }
    entry = _interpreters[session_id]
    entry["last_used"] = time.time()
    return entry


def check_rate_limit(client_ip):
    """Simple rate limiting."""
    now = time.time()
    if client_ip not in _request_counts:
        _request_counts[client_ip] = []
    _request_counts[client_ip] = [
        t for t in _request_counts[client_ip] if now - t < RATE_WINDOW
    ]
    if len(_request_counts[client_ip]) >= RATE_LIMIT:
        return False
    _request_counts[client_ip].append(now)
    return True


@app.route("/")
def index():
    return render_template("index.html", version=APP_VERSION)


@app.route("/health")
def health():
    return jsonify({"status": "ok", "uptime": time.time()})


@app.route("/api/v1/info", methods=["GET"])
def api_info():
    return jsonify({
        "engine": "CalcEngine",
        "version": APP_VERSION,
        "build": BUILD_ID,
        "capabilities": [
            "arithmetic",
            "trigonometric",
            "statistical",
            "user_functions",
            "variables",
        ],
        "limits": {
            "max_expression_length": MAX_EXPR_LENGTH,
            "rate_limit": f"{RATE_LIMIT}/min",
            "eval_timeout": f"{EVAL_TIMEOUT}s",
        },
    })


@app.route("/api/v1/evaluate", methods=["POST"])
def evaluate():
    """Evaluate a mathematical expression using the sandboxed interpreter."""
    client_ip = request.remote_addr
    if not check_rate_limit(client_ip):
        return jsonify({"error": "Rate limit exceeded. Try again later."}), 429

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be valid JSON."}), 400

    expression = data.get("expression", "")
    if not expression or not isinstance(expression, str):
        return jsonify({"error": "Missing or invalid 'expression' field."}), 400

    if len(expression) > MAX_EXPR_LENGTH:
        return jsonify({
            "error": f"Expression exceeds maximum length of {MAX_EXPR_LENGTH} characters."
        }), 400

    # Get or create session
    if "sid" not in session:
        session["sid"] = hashlib.sha256(os.urandom(16)).hexdigest()[:16]
    sid = session["sid"]

    entry = get_interpreter(sid)
    interp = entry["interpreter"]
    entry["eval_count"] += 1

    try:
        result = interp(expression)
    except Exception:
        return jsonify({"error": "Evaluation failed due to an internal error."}), 500

    # Check for interpreter errors
    if interp.error:
        errors = []
        for err in interp.error:
            errors.append(str(err.get_error()[1]))
        interp.error = []
        return jsonify({
            "success": False,
            "errors": errors,
        })

    # Format result
    if result is None:
        result_str = "None"
    else:
        result_str = repr(result)

    return jsonify({
        "success": True,
        "result": result_str,
        "session": sid,
    })


@app.route("/api/v1/session/reset", methods=["POST"])
def reset_session():
    """Reset the current session's interpreter state."""
    if "sid" in session:
        sid = session["sid"]
        if sid in _interpreters:
            del _interpreters[sid]
    session.pop("sid", None)
    return jsonify({"success": True, "message": "Session reset."})


@app.route("/api/v1/session/info", methods=["GET"])
def session_info():
    """Get information about the current session."""
    if "sid" not in session or session["sid"] not in _interpreters:
        return jsonify({
            "active": False,
            "message": "No active session. Submit an expression to start.",
        })
    sid = session["sid"]
    entry = _interpreters[sid]
    return jsonify({
        "active": True,
        "session": sid,
        "eval_count": entry["eval_count"],
        "created": datetime.fromtimestamp(entry["created"]).isoformat(),
        "last_used": datetime.fromtimestamp(entry["last_used"]).isoformat(),
    })


@app.route("/docs")
def docs():
    return render_template("docs.html", version=APP_VERSION)


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"error": "Method not allowed"}), 405


@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
