import hashlib
import secrets
import functools
from datetime import datetime

from flask import Flask, request, jsonify, session, g

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# ---------------------------------------------------------------------------
# Data layer – in-memory stores initialised at startup
# ---------------------------------------------------------------------------

USERS = {
    1: {
        "id": 1,
        "username": "ops-admin",
        "email": "ops@monitoring.internal",
        "password_hash": None,   # set in init_data()
        "is_active": True,
        "date_joined": "2022-06-14T08:22:11Z",
    },
}

# API tokens: keyed by token string
API_TOKENS = {}

# Projects
PROJECTS = {}

# Organisation
ORG = {
    "id": 1,
    "slug": "acme-corp",
    "name": "Acme Corp",
    "dateCreated": "2022-06-14T08:22:11Z",
    "status": {"id": "active", "name": "active"},
}

SYSTEM_SECRETS = {}

FLAG_VALUE = None


def _hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()


def init_data():
    """Seed realistic data."""
    global FLAG_VALUE

    # Read flag from file planted at build time
    try:
        with open("/app/.flag_secret", "r") as f:
            FLAG_VALUE = f.read().strip()
    except FileNotFoundError:
        FLAG_VALUE = "FLAG{placeholder}"

    USERS[1]["password_hash"] = _hash_pw("s3ntr!nel2024")

    # CI integration token
    API_TOKENS["sntrk_lo_" + "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"] = {
        "id": "tok_9f2e1a",
        "token": "sntrk_lo_" + "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
        "scopes": ["project:read"],
        "label": "CI read-only",
        "dateCreated": "2023-01-10T14:30:00Z",
        "expiresAt": None,
        "user_id": 1,
    }

    # Automation token
    API_TOKENS["sntrk_hi_" + "x9y8w7v6u5t4s3r2q1p0o9n8m7l6k5j4"] = {
        "id": "tok_4d7b3c",
        "token": "sntrk_hi_" + "x9y8w7v6u5t4s3r2q1p0o9n8m7l6k5j4",
        "scopes": ["org:admin", "project:admin", "member:admin", "event:admin"],
        "label": "Admin automation",
        "dateCreated": "2023-01-10T14:35:00Z",
        "expiresAt": None,
        "user_id": 1,
    }

    # Deploy pipeline token
    API_TOKENS["sntrk_md_" + "q2w3e4r5t6y7u8i9o0p1a2s3d4f5g6h7"] = {
        "id": "tok_8c1e5f",
        "token": "sntrk_md_" + "q2w3e4r5t6y7u8i9o0p1a2s3d4f5g6h7",
        "scopes": ["project:read", "project:write", "event:read"],
        "label": "Deployment pipeline",
        "dateCreated": "2023-03-22T09:15:00Z",
        "expiresAt": None,
        "user_id": 1,
    }

    # Projects
    PROJECTS["acme-backend"] = {
        "id": "proj_01",
        "slug": "acme-backend",
        "name": "Acme Backend",
        "platform": "python",
        "dateCreated": "2022-06-15T10:00:00Z",
        "status": "active",
        "dsn": {
            "public": "https://abc123@monitoring.acme-corp.io/1",
        },
        "settings": {
            "ci_token": "sntrk_lo_" + "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
            "rate_limit": 1000,
            "allowed_domains": ["*.acme-corp.io"],
        },
    }

    PROJECTS["acme-frontend"] = {
        "id": "proj_02",
        "slug": "acme-frontend",
        "name": "Acme Frontend",
        "platform": "javascript",
        "dateCreated": "2022-07-01T08:30:00Z",
        "status": "active",
        "dsn": {
            "public": "https://def456@monitoring.acme-corp.io/2",
        },
        "settings": {
            "rate_limit": 2000,
            "allowed_domains": ["*.acme-corp.io", "localhost:3000"],
        },
    }

    # System secrets
    SYSTEM_SECRETS["encryption_key"] = {
        "id": "sec_01",
        "name": "data-encryption-key",
        "value": FLAG_VALUE,
        "dateCreated": "2022-06-14T08:30:00Z",
        "status": "active",
    }
    SYSTEM_SECRETS["webhook_signing"] = {
        "id": "sec_02",
        "name": "webhook-signing-secret",
        "value": "whsk_" + secrets.token_hex(20),
        "dateCreated": "2022-08-01T12:00:00Z",
        "status": "active",
    }


# ---------------------------------------------------------------------------
# Authentication helpers
# ---------------------------------------------------------------------------

def authenticate_session(f):
    """Require a valid session cookie."""
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"detail": "Authentication credentials were not provided."}), 401
        g.auth_method = "session"
        g.user_id = session["user_id"]
        return f(*args, **kwargs)
    return wrapper


def authenticate_bearer(f):
    """Require a valid Bearer token. Sets g.token_scopes."""
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token_str = auth_header[7:]
            token_obj = API_TOKENS.get(token_str)
            if token_obj and USERS.get(token_obj["user_id"], {}).get("is_active"):
                g.auth_method = "token"
                g.user_id = token_obj["user_id"]
                g.token_scopes = token_obj["scopes"]
                g.token_id = token_obj["id"]
                return f(*args, **kwargs)
            return jsonify({"detail": "Invalid token"}), 401
        return jsonify({"detail": "Authentication credentials were not provided."}), 401
    return wrapper


def authenticate_session_or_bearer(f):
    """
    Accept either session cookie OR Bearer token authentication.
    This mirrors DRF SessionAuthentication behaviour which accepts both.
    """
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        # Try session first
        if "user_id" in session:
            g.auth_method = "session"
            g.user_id = session["user_id"]
            return f(*args, **kwargs)
        # Fall back to Bearer token
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token_str = auth_header[7:]
            token_obj = API_TOKENS.get(token_str)
            if token_obj and USERS.get(token_obj["user_id"], {}).get("is_active"):
                g.auth_method = "token"
                g.user_id = token_obj["user_id"]
                g.token_scopes = token_obj["scopes"]
                g.token_id = token_obj["id"]
                return f(*args, **kwargs)
        return jsonify({"detail": "Authentication credentials were not provided."}), 401
    return wrapper


def require_scope(scope):
    """Decorator: require that the current token has a specific scope.
    Session-authenticated users are treated as having all scopes."""
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            if g.get("auth_method") == "session":
                return f(*args, **kwargs)
            token_scopes = g.get("token_scopes", [])
            # Check for admin wildcard or exact match
            scope_prefix = scope.split(":")[0]
            if f"{scope_prefix}:admin" in token_scopes or scope in token_scopes:
                return f(*args, **kwargs)
            return jsonify({"detail": "You do not have permission to perform this action."}), 403
        return wrapper
    return decorator


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def _serialize_token(tok, include_value=True):
    """Serialize token for API response."""
    result = {
        "id": tok["id"],
        "scopes": tok["scopes"],
        "label": tok["label"],
        "dateCreated": tok["dateCreated"],
        "expiresAt": tok["expiresAt"],
    }
    if include_value:
        result["token"] = tok["token"]
    return result


def _serialize_project(proj, include_settings=False):
    result = {
        "id": proj["id"],
        "slug": proj["slug"],
        "name": proj["name"],
        "platform": proj["platform"],
        "dateCreated": proj["dateCreated"],
        "status": proj["status"],
    }
    if include_settings:
        result["settings"] = proj["settings"]
        result["dsn"] = proj["dsn"]
    return result


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return jsonify({
        "version": "23.7.1",
        "urls": {
            "apiRoot": "/api/0/",
            "organizationUrl": "/api/0/organizations/{organization_slug}/",
        },
        "user": {
            "isAuthenticated": "user_id" in session,
        },
        "organization": {
            "slug": ORG["slug"],
        },
    })


@app.route("/api/0/")
def api_root():
    return jsonify({
        "endpoints": {
            "auth": "/api/0/auth/",
            "organizations": "/api/0/organizations/",
            "projects": "/api/0/projects/",
            "auth-tokens": "/api/0/auth-tokens/",
            "system-secrets": "/api/0/system/secrets/",
        },
        "version": "0",
    })


@app.route("/api/0/organizations/<slug>/projects/")
def list_org_projects_public(slug):
    """Public listing of project slugs for an organisation.
    Detailed project info requires authentication."""
    if slug != ORG["slug"]:
        return jsonify({"detail": "The requested resource does not exist"}), 404
    result = []
    for p in PROJECTS.values():
        result.append({
            "slug": p["slug"],
            "name": p["name"],
            "platform": p["platform"],
            "status": p["status"],
            "clientConfigUrl": f"/api/0/projects/{slug}/{p['slug']}/client-config/",
        })
    return jsonify(result)


# ---- Auth / Login ----

@app.route("/api/0/auth/", methods=["GET", "POST", "DELETE"])
def auth_endpoint():
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        username = data.get("username", "")
        password = data.get("password", "")
        for uid, user in USERS.items():
            if user["username"] == username and user["password_hash"] == _hash_pw(password):
                session["user_id"] = uid
                session["_auth_method"] = "credentials"
                return jsonify({
                    "id": str(uid),
                    "username": user["username"],
                    "email": user["email"],
                    "isActive": user["is_active"],
                    "dateJoined": user["date_joined"],
                })
        return jsonify({"detail": "Invalid username or password"}), 401

    if request.method == "DELETE":
        session.clear()
        return "", 204

    # GET – check current auth
    if "user_id" in session:
        user = USERS[session["user_id"]]
        return jsonify({
            "id": str(user["id"]),
            "username": user["username"],
            "email": user["email"],
            "isActive": user["is_active"],
        })
    return jsonify({"detail": "Authentication credentials were not provided."}), 401


# ---- Organisation ----

@app.route("/api/0/organizations/")
@authenticate_session_or_bearer
def list_organizations():
    return jsonify([ORG])


@app.route("/api/0/organizations/<slug>/")
@authenticate_session_or_bearer
def get_organization(slug):
    if slug == ORG["slug"]:
        return jsonify(ORG)
    return jsonify({"detail": "The requested resource does not exist"}), 404


# ---- Projects ----

@app.route("/api/0/projects/")
@authenticate_session_or_bearer
@require_scope("project:read")
def list_projects():
    result = [_serialize_project(p) for p in PROJECTS.values()]
    return jsonify(result)


@app.route("/api/0/projects/<org_slug>/<proj_slug>/")
@authenticate_session_or_bearer
@require_scope("project:read")
def get_project(org_slug, proj_slug):
    proj = PROJECTS.get(proj_slug)
    if not proj or org_slug != ORG["slug"]:
        return jsonify({"detail": "The requested resource does not exist"}), 404
    return jsonify(_serialize_project(proj, include_settings=True))


# ---- Auth Tokens ----

@app.route("/api/0/auth-tokens/", methods=["GET", "POST", "DELETE"])
@authenticate_session_or_bearer
def manage_auth_tokens():
    user_id = g.user_id

    if request.method == "GET":
        user_tokens = [
            _serialize_token(t) for t in API_TOKENS.values()
            if t["user_id"] == user_id
        ]
        return jsonify(user_tokens)

    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        scopes = data.get("scopes", [])
        label = data.get("label", "Untitled token")
        if not scopes:
            return jsonify({"scopes": ["This field is required."]}), 400
        new_token_str = "sntrk_" + secrets.token_hex(20)
        new_token = {
            "id": "tok_" + secrets.token_hex(3),
            "token": new_token_str,
            "scopes": scopes,
            "label": label,
            "dateCreated": datetime.utcnow().isoformat() + "Z",
            "expiresAt": None,
            "user_id": user_id,
        }
        API_TOKENS[new_token_str] = new_token
        return jsonify(_serialize_token(new_token)), 201

    if request.method == "DELETE":
        data = request.get_json(silent=True) or {}
        token_val = data.get("token")
        if not token_val:
            return jsonify({"token": "This field is required."}), 400
        tok = API_TOKENS.get(token_val)
        if tok and tok["user_id"] == user_id:
            del API_TOKENS[token_val]
            return "", 204
        return jsonify({"detail": "Not found."}), 404


# ---- System Secrets (protected by admin scope) ----

@app.route("/api/0/system/secrets/")
@authenticate_bearer
@require_scope("org:admin")
def list_system_secrets():
    result = []
    for s in SYSTEM_SECRETS.values():
        result.append({
            "id": s["id"],
            "name": s["name"],
            "value": s["value"],
            "dateCreated": s["dateCreated"],
            "status": s["status"],
        })
    return jsonify(result)


# ---- Client SDK Configuration (public) ----

@app.route("/api/0/projects/<org_slug>/<proj_slug>/client-config/")
def project_client_config(org_slug, proj_slug):
    """Public endpoint that returns client SDK configuration.
    DSN and read-only tokens are considered safe to expose in client apps."""
    proj = PROJECTS.get(proj_slug)
    if not proj or org_slug != ORG["slug"]:
        return jsonify({"detail": "The requested resource does not exist"}), 404
    config = {
        "dsn": proj["dsn"]["public"],
        "project": proj["slug"],
        "organization": org_slug,
        "allowedDomains": proj["settings"].get("allowed_domains", []),
    }
    if "ci_token" in proj["settings"]:
        config["integrationToken"] = proj["settings"]["ci_token"]
    return jsonify(config)


# ---- Health check ----

@app.route("/healthz")
def healthz():
    return jsonify({"ok": True})


# ---------------------------------------------------------------------------
# Startup
# ---------------------------------------------------------------------------

@app.before_request
def suppress_server_header():
    pass

@app.after_request
def security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "deny"
    response.headers.pop("Server", None)
    return response


init_data()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)
