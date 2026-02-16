import os
import time
import hashlib
import json
from functools import wraps
from flask import Flask, request, jsonify, render_template, redirect, url_for, make_response, abort

import jwt

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Application configuration
APP_CONFIG = {
    "server": {
        "port": 5003,
        "servlet": {
            "context-path": "/api"
        }
    },
    "platform": {
        "name": "NexusGate Cloud Platform",
        "version": "3.7.2",
        "swagger": {
            "title": "Authorization Service",
            "base-package": "com.nexusgate.platform"
        },
        "authentication": {
            "expire": 28800,
            "refreshExpire": 86400,
            "tokenSignKey": "nexusgate_cloud_is_an_awesome_platform"
        },
        "database": {
            "tenantDatabasePrefix": "nexus_extend",
            "multiTenantType": "SCHEMA"
        },
        "security": {
            "enabled": True,
            "type": "INTERNAL",
            "caseSensitive": False
        },
        "log": {
            "enabled": True,
            "type": "DB"
        },
        "xss": {
            "enabled": True,
            "requestBodyEnabled": False
        }
    }
}

# The signing key used for JWT operations
SIGNING_KEY = APP_CONFIG["platform"]["authentication"]["tokenSignKey"]

# User store (in production this would be a database)
_users = {
    "operator": {
        "password_hash": hashlib.sha256(("operator123" + "a1b2c3").encode()).hexdigest(),
        "salt": "a1b2c3",
        "user_id": 1001,
        "account": "operator",
        "name": "System Operator",
        "role": "operator",
        "state": True,
        "work_describe": "Platform operations management"
    },
    "admin": {
        "password_hash": hashlib.sha256(("Xe9$kL2mNp#Qw" + "d4e5f6").encode()).hexdigest(),
        "salt": "d4e5f6",
        "user_id": 1,
        "account": "admin",
        "name": "Super Administrator",
        "role": "admin",
        "state": True,
        "work_describe": "Full system administration"
    }
}

# Read flag at startup from the planted file
def _read_flag():
    try:
        with open('/app/data/system_credentials.dat', 'r') as f:
            return f.read().strip()
    except Exception:
        return "NO_FLAG_CONFIGURED"

SYSTEM_CREDENTIAL = _read_flag()


def create_auth_token(user_info):
    now = int(time.time())
    payload = {
        "userId": user_info["user_id"],
        "account": user_info["account"],
        "name": user_info["name"],
        "role": user_info["role"],
        "iat": now,
        "exp": now + APP_CONFIG["platform"]["authentication"]["expire"]
    }
    token = jwt.encode(payload, SIGNING_KEY, algorithm="HS256")
    return token


def verify_auth_token(token_str):
    if not token_str:
        return None
    # Strip Bearer prefix if present
    if token_str.startswith("Bearer "):
        token_str = token_str[7:]
    try:
        payload = jwt.decode(token_str, SIGNING_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization", "")
        if not token:
            token = request.cookies.get("access_token", "")
        auth_info = verify_auth_token(token)
        if auth_info is None:
            return jsonify({"code": 40001, "msg": "Token not valid or expired", "data": None}), 401
        request.auth_info = auth_info
        return f(*args, **kwargs)
    return decorated


# --- Health / Root ---
@app.route("/")
def index():
    return redirect("/api/portal")


@app.route("/api/portal")
def portal():
    return render_template("portal.html")


@app.route("/ping")
def ping():
    return "OK", 200


# --- Authentication endpoints ---
@app.route("/api/noToken/login", methods=["GET"])
def login_page():
    return render_template("login.html")


@app.route("/api/noToken/login", methods=["POST"])
def auth_login():
    data = request.get_json(silent=True)
    if not data:
        data = {}
    account = data.get("account", "")
    password = data.get("password", "")
    grant_type = data.get("grantType", "password")

    if not account or not password:
        return jsonify({"code": -1, "msg": "Please provide account and password", "data": None}), 400

    user = _users.get(account)
    if user is None:
        return jsonify({"code": -1, "msg": "Invalid account or password", "data": None}), 401

    if not user["state"]:
        return jsonify({"code": -1, "msg": "Account has been disabled", "data": None}), 403

    password_hash = hashlib.sha256((password + user["salt"]).encode()).hexdigest()
    if password_hash != user["password_hash"]:
        return jsonify({"code": -1, "msg": "Invalid account or password", "data": None}), 401

    token = create_auth_token(user)
    auth_info = {
        "token": token,
        "tokenType": "Bearer",
        "expire": APP_CONFIG["platform"]["authentication"]["expire"],
        "refreshExpire": APP_CONFIG["platform"]["authentication"]["refreshExpire"],
        "userId": user["user_id"],
        "account": user["account"],
        "name": user["name"],
        "workDescribe": user["work_describe"]
    }
    return jsonify({"code": 0, "msg": "ok", "data": auth_info})


@app.route("/api/noToken/logout", methods=["POST"])
def auth_logout():
    return jsonify({"code": 0, "msg": "ok", "data": True})


# --- Token verification ---
@app.route("/api/anno/verify", methods=["GET"])
def verify_token():
    token = request.args.get("token", "")
    auth_info = verify_auth_token(token)
    if auth_info is None:
        return jsonify({"code": 40001, "msg": "Token not valid or expired", "data": None}), 401
    return jsonify({"code": 0, "msg": "ok", "data": auth_info})


# --- User endpoints (protected) ---
@app.route("/api/user/info", methods=["GET"])
@require_auth
def user_info():
    auth = request.auth_info
    user = _users.get(auth.get("account"))
    if user is None:
        return jsonify({"code": -1, "msg": "User not found", "data": None}), 404
    return jsonify({
        "code": 0,
        "msg": "ok",
        "data": {
            "userId": user["user_id"],
            "account": user["account"],
            "name": user["name"],
            "role": user["role"],
            "workDescribe": user["work_describe"]
        }
    })


# --- Resource / Menu endpoints (protected) ---
@app.route("/api/resource/visible", methods=["GET"])
@require_auth
def resource_visible():
    auth = request.auth_info
    role = auth.get("role", "")
    if role == "admin":
        resources = ["system:user:view", "system:role:view", "system:menu:view",
                     "system:config:view", "system:credentials:view", "system:log:view"]
    else:
        resources = ["system:user:view", "system:log:view"]
    return jsonify({
        "code": 0,
        "msg": "ok",
        "data": {
            "roleList": [role],
            "resourceList": resources,
            "caseSensitive": False,
            "enabled": True
        }
    })


@app.route("/api/menu/router", methods=["GET"])
@require_auth
def menu_router():
    auth = request.auth_info
    role = auth.get("role", "")
    menus = [
        {"name": "Dashboard", "path": "/dashboard", "component": "views/dashboard/index"},
        {"name": "User Management", "path": "/system/user", "component": "views/system/user/index"},
    ]
    if role == "admin":
        menus.extend([
            {"name": "Role Management", "path": "/system/role", "component": "views/system/role/index"},
            {"name": "Menu Management", "path": "/system/menu", "component": "views/system/menu/index"},
            {"name": "System Credentials", "path": "/system/credentials", "component": "views/system/credentials/index"},
        ])
    return jsonify({"code": 0, "msg": "ok", "data": menus})


# --- Admin-only: System credentials ---
@app.route("/api/system/credentials", methods=["GET"])
@require_auth
def system_credentials():
    auth = request.auth_info
    if auth.get("role") != "admin":
        return jsonify({"code": 40003, "msg": "Insufficient permissions. Admin role required.", "data": None}), 403
    return jsonify({
        "code": 0,
        "msg": "ok",
        "data": {
            "credentials": SYSTEM_CREDENTIAL
        }
    })


# --- Configuration endpoints (mimicking Nacos config export) ---
@app.route("/api/config/gateway", methods=["GET"])
def config_gateway():
    gateway_config = {
        "platform": {
            "log": {"enabled": False},
            "webmvc": {"enabled": False},
            "database": {"tenantDatabasePrefix": "nexus_extend"},
            "ignore": {
                "token": [
                    "/ds/**",
                    "/**/noToken/**",
                    "/**/anno/**"
                ]
            }
        },
        "spring": {
            "cloud": {
                "gateway": {
                    "discovery": {
                        "locator": {
                            "enabled": True,
                            "lowerCaseServiceId": True
                        }
                    },
                    "routes": [
                        {"id": "oauth", "uri": "lb://nexus-oauth-server", "predicates": ["Path=/oauth/**"]},
                        {"id": "authority", "uri": "lb://nexus-authority-server", "predicates": ["Path=/authority/**"]},
                        {"id": "file", "uri": "lb://nexus-file-server", "predicates": ["Path=/file/**"]},
                        {"id": "tenant", "uri": "lb://nexus-tenant-server", "predicates": ["Path=/tenant/**"]}
                    ]
                }
            }
        },
        "server": {
            "port": 8760,
            "servlet": {"context-path": "/api"}
        }
    }
    return jsonify(gateway_config)


@app.route("/api/config/auth", methods=["GET"])
def config_auth():
    auth_config = {
        "server": {"port": 5003},
        "platform": {
            "swagger": {
                "title": "Authorization Service",
                "base-package": "com.nexusgate.platform"
            },
            "authentication": {
                "expire": APP_CONFIG["platform"]["authentication"]["expire"],
                "refreshExpire": APP_CONFIG["platform"]["authentication"]["refreshExpire"],
                "tokenSignKey": SIGNING_KEY
            }
        }
    }
    return jsonify(auth_config)


@app.route("/api/config/common", methods=["GET"])
def config_common():
    common_config = {
        "platform": {
            "system": {
                "verifyPassword": True,
                "verifyCaptcha": False
            },
            "swagger": {
                "license": "Powered By NexusGate",
                "licenseUrl": "https://github.com/nexusgate",
                "global-operation-parameters": [
                    {"name": "token", "description": "User authentication token", "parameterType": "header", "required": True},
                    {"name": "Authorization", "description": "Client information", "parameterType": "header", "required": True}
                ]
            },
            "security": {
                "enabled": True,
                "type": "INTERNAL",
                "caseSensitive": False
            },
            "log": {
                "enabled": True,
                "type": "DB"
            },
            "xss": {
                "enabled": True,
                "requestBodyEnabled": False
            }
        },
        "server": {
            "shutdown": "GRACEFUL",
            "servlet": {
                "encoding": {"enabled": True, "charset": "UTF-8", "force": True}
            }
        },
        "management": {
            "endpoints": {
                "web": {
                    "base-path": "/actuator",
                    "exposure": {"include": "*"}
                }
            }
        }
    }
    return jsonify(common_config)


# --- Error handlers ---
@app.errorhandler(404)
def not_found(e):
    return jsonify({"code": 404, "msg": "Resource not found", "data": None}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"code": 500, "msg": "Internal server error", "data": None}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)
