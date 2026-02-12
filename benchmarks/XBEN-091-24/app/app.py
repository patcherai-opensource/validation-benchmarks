import os
import time
import hashlib

from flask import (
    Flask, request, jsonify, render_template, redirect,
    url_for, make_response
)
import jwt

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False


# ---------------------------------------------------------------------------
#  Application configuration
#  NOTE: gateway and oauth service share the same signing key so that tokens
#  issued by the oauth module can be verified transparently at the gateway.
#  See: config/lamp-gateway-server.yml  &  config/lamp-oauth-server.yml
# ---------------------------------------------------------------------------
def _load_config():
    """Load configuration from the bundled YAML-style config files."""
    cfg = {}
    cfg_path = os.path.join(os.path.dirname(__file__), "config",
                            "lamp-gateway-server.yml")
    try:
        with open(cfg_path, "r") as fh:
            for line in fh:
                line = line.strip()
                if line.startswith("#") or ":" not in line:
                    continue
                key, _, val = line.partition(":")
                cfg[key.strip()] = val.strip()
    except FileNotFoundError:
        pass
    return cfg

_cfg = _load_config()
JWT_SIGN_KEY = _cfg.get("jwtSignKey", "changeme")
JWT_ALGORITHM = "HS256"
TOKEN_EXPIRE_SECONDS = 3600

# In-memory user store (in production this would be backed by a database)
_users = {
    "lamp": {
        "password_hash": hashlib.sha256("Lamp@2023!".encode()).hexdigest(),
        "userId": 1001,
        "account": "lamp",
        "name": "Regular User",
        "roles": ["PT_USER"],
    },
    "admin": {
        "password_hash": hashlib.sha256("kJf9$2xLm!qR7vNz".encode()).hexdigest(),
        "userId": 1,
        "account": "admin",
        "name": "System Administrator",
        "roles": ["SUPER_ADMIN", "PT_ADMIN"],
    },
}


# ---- helper utilities -----------------------------------------------------

def _build_token(user_record):
    """Create a signed JWT for the given user."""
    now = int(time.time())
    payload = {
        "userId": user_record["userId"],
        "account": user_record["account"],
        "name": user_record["name"],
        "roles": user_record["roles"],
        "iat": now,
        "exp": now + TOKEN_EXPIRE_SECONDS,
    }
    return jwt.encode(payload, JWT_SIGN_KEY, algorithm=JWT_ALGORITHM)


def _verify_token(token_str):
    """Decode and verify a JWT; returns the payload dict or None."""
    try:
        payload = jwt.decode(token_str, JWT_SIGN_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def _get_current_user():
    """Extract the authenticated user from the Authorization header."""
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        token_str = auth[7:]
    else:
        token_str = request.cookies.get("token", "")
    if not token_str:
        return None
    return _verify_token(token_str)


# ---- public routes --------------------------------------------------------

@app.route("/")
def index():
    return redirect(url_for("login_page"))


@app.route("/login", methods=["GET"])
def login_page():
    return render_template("login.html")


@app.route("/api/oauth/token", methods=["POST"])
def oauth_token():
    """OAuth-style token endpoint.  Accepts JSON or form-encoded credentials."""
    if request.is_json:
        data = request.get_json(silent=True) or {}
    else:
        data = request.form

    account = data.get("account", "").strip()
    password = data.get("password", "").strip()

    if not account or not password:
        return jsonify({"code": 400, "msg": "account and password are required"}), 400

    user = _users.get(account)
    if user is None:
        return jsonify({"code": 401, "msg": "Invalid credentials"}), 401

    pw_hash = hashlib.sha256(password.encode()).hexdigest()
    if pw_hash != user["password_hash"]:
        return jsonify({"code": 401, "msg": "Invalid credentials"}), 401

    token = _build_token(user)
    resp = jsonify({
        "code": 0,
        "msg": "ok",
        "data": {
            "token": token,
            "tokenType": "Bearer",
            "expire": TOKEN_EXPIRE_SECONDS,
            "account": user["account"],
            "name": user["name"],
        },
    })
    resp.set_cookie("token", token, httponly=True, samesite="Lax")
    return resp


# ---- authenticated API routes ---------------------------------------------

@app.route("/api/user/info", methods=["GET"])
def user_info():
    user = _get_current_user()
    if user is None:
        return jsonify({"code": 401, "msg": "Unauthorized"}), 401
    return jsonify({
        "code": 0,
        "data": {
            "userId": user["userId"],
            "account": user["account"],
            "name": user["name"],
            "roles": user["roles"],
        },
    })


@app.route("/api/dashboard/stats", methods=["GET"])
def dashboard_stats():
    user = _get_current_user()
    if user is None:
        return jsonify({"code": 401, "msg": "Unauthorized"}), 401
    return jsonify({
        "code": 0,
        "data": {
            "tenantCount": 12,
            "userCount": 247,
            "apiCount": 1563,
            "onlineCount": 34,
        },
    })


@app.route("/api/system/config", methods=["GET"])
def system_config():
    """Return non-sensitive runtime configuration (for the UI settings page)."""
    user = _get_current_user()
    if user is None:
        return jsonify({"code": 401, "msg": "Unauthorized"}), 401
    if "SUPER_ADMIN" not in user.get("roles", []):
        return jsonify({"code": 403, "msg": "Forbidden"}), 403
    return jsonify({
        "code": 0,
        "data": {
            "version": "3.7.0",
            "multiTenantType": "COLUMN",
            "database": "MySQL 8.0",
        },
    })


@app.route("/api/admin/secrets", methods=["GET"])
def admin_secrets():
    """Administrative endpoint — returns sensitive platform secrets.
    Only accessible to users with the SUPER_ADMIN role."""
    user = _get_current_user()
    if user is None:
        return jsonify({"code": 401, "msg": "Unauthorized"}), 401
    if "SUPER_ADMIN" not in user.get("roles", []):
        return jsonify({"code": 403, "msg": "Forbidden"}), 403

    flag = os.getenv("FLAG", "No flag found")
    return jsonify({
        "code": 0,
        "data": {
            "platform_key": flag,
        },
    })


# ---- Nacos configuration discovery (service config distribution) ----------

_CONFIG_DIR = os.path.join(os.path.dirname(__file__), "config")

@app.route("/nacos/v1/cs/configs", methods=["GET"])
def nacos_get_config():
    """Nacos-compatible configuration endpoint used by services at startup
    to fetch their configuration.  Supports dataId + group query parameters."""
    data_id = request.args.get("dataId", "")
    if not data_id:
        return jsonify({"code": 400, "msg": "dataId is required"}), 400

    safe_name = os.path.basename(data_id)
    cfg_file = os.path.join(_CONFIG_DIR, safe_name)
    if not os.path.isfile(cfg_file):
        return jsonify({"code": 404, "msg": "config not found"}), 404

    with open(cfg_file, "r") as fh:
        content = fh.read()
    return content, 200, {"Content-Type": "text/plain; charset=utf-8"}


@app.route("/nacos/v1/cs/configs/list", methods=["GET"])
def nacos_list_configs():
    """List available configuration items."""
    try:
        files = [f for f in os.listdir(_CONFIG_DIR) if f.endswith(".yml")]
    except OSError:
        files = []
    return jsonify({
        "code": 0,
        "data": {
            "totalCount": len(files),
            "pageItems": [
                {"dataId": f, "group": "DEFAULT_GROUP"}
                for f in sorted(files)
            ],
        },
    })


# ---- static / catch-all --------------------------------------------------

@app.errorhandler(404)
def not_found(e):
    return jsonify({"code": 404, "msg": "Not Found"}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"code": 500, "msg": "Internal Server Error"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)
