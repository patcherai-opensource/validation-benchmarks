import os
import hashlib
import secrets
from functools import wraps

from flask import (
    Flask, request, jsonify, render_template, redirect,
    url_for, session, g
)

app = Flask(__name__)
app.secret_key = os.urandom(32).hex()

# ---------------------------------------------------------------------------
# Read the flag that was baked in at build time
# ---------------------------------------------------------------------------
FLAG_FILE = "/etc/sentry/internal_dsn_key"

def _read_flag():
    try:
        with open(FLAG_FILE, "r") as f:
            return f.read().strip()
    except Exception:
        return "FLAG_NOT_SET"

# ---------------------------------------------------------------------------
# In-memory data store (simulating database)
# ---------------------------------------------------------------------------

# Users
USERS = {
    "admin@sentry.io": {
        "id": 1,
        "email": "admin@sentry.io",
        "password_hash": hashlib.sha256(b"s3ntry_Adm!n_2024").hexdigest(),
        "name": "Admin User",
        "is_staff": True,
        "is_superuser": True,
        "date_joined": "2023-01-15T10:30:00Z",
    },
}

# Organization
ORGANIZATIONS = {
    1: {
        "id": 1,
        "slug": "sentry-internal",
        "name": "Sentry Internal",
        "dateCreated": "2023-01-15T10:30:00Z",
        "status": {"id": "active", "name": "active"},
    }
}

# Projects
PROJECTS = {
    1: {
        "id": 1,
        "slug": "backend-api",
        "name": "Backend API",
        "organization": {"id": 1, "slug": "sentry-internal"},
        "platform": "python",
        "dateCreated": "2023-01-16T08:00:00Z",
        "status": "active",
    },
    2: {
        "id": 2,
        "slug": "frontend-app",
        "name": "Frontend App",
        "organization": {"id": 1, "slug": "sentry-internal"},
        "platform": "javascript",
        "dateCreated": "2023-02-01T14:30:00Z",
        "status": "active",
    },
}

# Internal DSN keys (only accessible with org:admin scope)
INTERNAL_DSN_KEYS = {
    1: {
        "id": 1,
        "project": {"id": 1, "slug": "backend-api"},
        "label": "Default",
        "dsn": {
            "secret": None,  # will be set to FLAG at startup
            "public": "https://abc123@o1.ingest.sentry.io/1",
        },
        "dateCreated": "2023-01-16T08:00:00Z",
        "isActive": True,
    }
}

# API tokens for user admin@sentry.io
# Token structure mimics Sentry's ApiToken model
API_TOKENS = {}

def _init_tokens():
    """Initialize tokens. Called once at startup."""
    # Low-privilege token: only has 'event:read' scope
    # This token is "leaked" via a webhook integration config
    API_TOKENS["sntrys_lo_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"] = {
        "id": "tok_low_001",
        "token": "sntrys_lo_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
        "scopes": ["event:read"],
        "dateCreated": "2023-06-15T09:00:00Z",
        "expiresAt": None,
        "state": "active",
        "tokenLastCharacters": "o5p6",
        "user_id": 1,
    }

    # Medium-privilege token: has project-level scopes
    API_TOKENS["sntrys_md_q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2"] = {
        "id": "tok_med_002",
        "token": "sntrys_md_q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2",
        "scopes": ["event:read", "event:write", "project:read"],
        "dateCreated": "2023-07-20T14:30:00Z",
        "expiresAt": None,
        "state": "active",
        "tokenLastCharacters": "e1f2",
        "user_id": 1,
    }

    # High-privilege token: has org:admin scope - can access DSN keys
    API_TOKENS["sntrys_hi_g3h4i5j6k7l8m9n0o1p2q3r4s5t6u7v8"] = {
        "id": "tok_high_003",
        "token": "sntrys_hi_g3h4i5j6k7l8m9n0o1p2q3r4s5t6u7v8",
        "scopes": ["event:read", "event:write", "project:read", "project:write",
                    "org:read", "org:write", "org:admin", "member:read"],
        "dateCreated": "2023-08-01T11:00:00Z",
        "expiresAt": None,
        "state": "active",
        "tokenLastCharacters": "u7v8",
        "user_id": 1,
    }

_init_tokens()

# Webhook integrations (one exposes the low-priv token in config)
INTEGRATIONS = {
    1: {
        "id": 1,
        "name": "Slack Notifications",
        "provider": "slack",
        "status": "active",
        "config": {
            "webhook_url": "https://hooks.slack.com/services/T01ABCDEF/B02GHIJKL/xyzSecretWebhookToken",
        },
        "dateCreated": "2023-03-10T16:45:00Z",
    },
    2: {
        "id": 2,
        "name": "CI/CD Webhook",
        "provider": "custom",
        "status": "active",
        "config": {
            "url": "https://ci.internal.example.com/hooks/sentry",
            "authorization_header": "Bearer sntrys_lo_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
            "events": ["issue.created", "issue.resolved"],
        },
        "dateCreated": "2023-05-22T10:15:00Z",
    }
}

# Sessions store (cookie-based session IDs)
ACTIVE_SESSIONS = {}

# ---------------------------------------------------------------------------
# Authentication helpers
# ---------------------------------------------------------------------------

class SessionAuthentication:
    """
    Mimics DRF's SessionAuthentication.
    Accepts both session cookies AND Authorization: Bearer <token> headers.
    This is the VULNERABLE behavior - it should only accept session cookies
    for the api-tokens endpoint.
    """
    @staticmethod
    def authenticate(req):
        # Check session cookie first
        if "session_id" in session:
            sid = session["session_id"]
            if sid in ACTIVE_SESSIONS:
                user_email = ACTIVE_SESSIONS[sid]
                if user_email in USERS:
                    return USERS[user_email]

        # Also accept Bearer token auth (THIS IS THE VULNERABILITY)
        auth_header = req.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token_value = auth_header[7:].strip()
            if token_value in API_TOKENS:
                token_data = API_TOKENS[token_value]
                user_id = token_data["user_id"]
                for email, user in USERS.items():
                    if user["id"] == user_id:
                        return user
        return None


class TokenAuthentication:
    """Standard token authentication - used for most API endpoints."""
    @staticmethod
    def authenticate(req):
        auth_header = req.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token_value = auth_header[7:].strip()
            if token_value in API_TOKENS:
                token_data = API_TOKENS[token_value]
                user_id = token_data["user_id"]
                for email, user in USERS.items():
                    if user["id"] == user_id:
                        g.current_token = token_data
                        return user
        return None

    @staticmethod
    def get_token_scopes(req):
        auth_header = req.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token_value = auth_header[7:].strip()
            if token_value in API_TOKENS:
                return API_TOKENS[token_value]["scopes"]
        return []


def require_session_or_token_auth(f):
    """Decorator: requires session OR token auth (used for most endpoints)."""
    @wraps(f)
    def decorated(*args, **kwargs):
        user = SessionAuthentication.authenticate(request)
        if user is None:
            user = TokenAuthentication.authenticate(request)
        if user is None:
            return jsonify({"detail": "Authentication credentials were not provided."}), 401
        g.user = user
        return f(*args, **kwargs)
    return decorated


def require_session_auth_only(f):
    """Decorator: requires ONLY session auth (should be used for sensitive endpoints)."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "session_id" not in session:
            return jsonify({"detail": "Authentication credentials were not provided."}), 401
        sid = session["session_id"]
        if sid not in ACTIVE_SESSIONS:
            return jsonify({"detail": "Session expired."}), 401
        user_email = ACTIVE_SESSIONS[sid]
        if user_email not in USERS:
            return jsonify({"detail": "User not found."}), 401
        g.user = USERS[user_email]
        return f(*args, **kwargs)
    return decorated


def require_token_scope(scope):
    """Decorator: checks that the current token has the required scope."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            scopes = TokenAuthentication.get_token_scopes(request)
            # Session-based auth has all scopes
            if "session_id" in session and session["session_id"] in ACTIVE_SESSIONS:
                return f(*args, **kwargs)
            if scope not in scopes:
                return jsonify({
                    "detail": "You do not have permission to perform this action. "
                              f"Required scope: {scope}"
                }), 403
            return f(*args, **kwargs)
        return decorated
    return decorator


# ---------------------------------------------------------------------------
# Web UI routes (session-based)
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return redirect("/auth/login/")


@app.route("/auth/login/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        if email in USERS and USERS[email]["password_hash"] == password_hash:
            sid = secrets.token_hex(32)
            ACTIVE_SESSIONS[sid] = email
            session["session_id"] = sid
            return redirect("/organizations/sentry-internal/")
        return render_template("login.html", error="Invalid credentials"), 401

    return render_template("login.html", error=None)


@app.route("/auth/logout/", methods=["POST"])
def logout():
    sid = session.pop("session_id", None)
    if sid and sid in ACTIVE_SESSIONS:
        del ACTIVE_SESSIONS[sid]
    return redirect("/auth/login/")


@app.route("/organizations/<slug>/")
def organization_dashboard(slug):
    if "session_id" not in session or session["session_id"] not in ACTIVE_SESSIONS:
        return redirect("/auth/login/")
    org = None
    for o in ORGANIZATIONS.values():
        if o["slug"] == slug:
            org = o
            break
    if not org:
        return jsonify({"detail": "Organization not found."}), 404
    return render_template("dashboard.html", org=org, projects=PROJECTS.values())


# ---------------------------------------------------------------------------
# API endpoints - /api/0/
# ---------------------------------------------------------------------------

@app.route("/api/0/", methods=["GET"])
def api_root():
    return jsonify({
        "version": "0",
        "auth": {
            "session": {"url": "/auth/login/"},
            "token": {"url": "/api/0/api-tokens/"},
        },
        "urls": {
            "organizationList": "/api/0/organizations/",
            "projectList": "/api/0/projects/",
            "apiTokens": "/api/0/api-tokens/",
            "onboarding": "/api/0/organizations/{org_slug}/onboarding/",
            "integrations": "/api/0/organizations/{org_slug}/integrations/",
            "projectKeys": "/api/0/projects/{org_slug}/{project_slug}/keys/",
            "organizationStats": "/api/0/organizations/{org_slug}/stats/",
        },
    })


# VULNERABLE ENDPOINT: Uses SessionAuthentication which also accepts Bearer tokens
# This should use SessionNoAuthTokenAuthentication (session-only)
@app.route("/api/0/api-tokens/", methods=["GET"])
def api_tokens_list():
    """
    List all API tokens for the authenticated user.
    
    Authentication: SessionAuthentication
    """
    # SessionAuthentication accepts both session and bearer token
    user = SessionAuthentication.authenticate(request)
    if user is None:
        return jsonify({"detail": "Authentication credentials were not provided."}), 401

    user_id = user["id"]
    tokens = []
    for token_data in API_TOKENS.values():
        if token_data["user_id"] == user_id:
            tokens.append({
                "id": token_data["id"],
                "token": token_data["token"],
                "scopes": token_data["scopes"],
                "dateCreated": token_data["dateCreated"],
                "expiresAt": token_data["expiresAt"],
                "state": token_data["state"],
                "tokenLastCharacters": token_data["tokenLastCharacters"],
            })

    return jsonify(tokens)


@app.route("/api/0/organizations/", methods=["GET"])
def api_organizations():
    """List organizations. Public endpoint for discovery."""
    # Return minimal public info
    orgs = []
    for org in ORGANIZATIONS.values():
        orgs.append({
            "id": org["id"],
            "slug": org["slug"],
            "name": org["name"],
            "dateCreated": org["dateCreated"],
            "status": org["status"],
        })
    return jsonify(orgs)


@app.route("/api/0/organizations/<slug>/", methods=["GET"])
@require_session_or_token_auth
@require_token_scope("org:read")
def api_organization_detail(slug):
    for org in ORGANIZATIONS.values():
        if org["slug"] == slug:
            return jsonify(org)
    return jsonify({"detail": "Not found."}), 404


@app.route("/api/0/projects/", methods=["GET"])
@require_session_or_token_auth
@require_token_scope("project:read")
def api_projects():
    return jsonify(list(PROJECTS.values()))


@app.route("/api/0/projects/<org_slug>/<project_slug>/", methods=["GET"])
@require_session_or_token_auth
@require_token_scope("project:read")
def api_project_detail(org_slug, project_slug):
    for proj in PROJECTS.values():
        if proj["organization"]["slug"] == org_slug and proj["slug"] == project_slug:
            return jsonify(proj)
    return jsonify({"detail": "Not found."}), 404


@app.route("/api/0/projects/<org_slug>/<project_slug>/keys/", methods=["GET"])
@require_session_or_token_auth
@require_token_scope("org:admin")
def api_project_keys(org_slug, project_slug):
    """
    List client keys (DSN) for a project.
    Requires org:admin scope.
    """
    project = None
    for proj in PROJECTS.values():
        if proj["organization"]["slug"] == org_slug and proj["slug"] == project_slug:
            project = proj
            break
    if not project:
        return jsonify({"detail": "Not found."}), 404

    keys = []
    for key in INTERNAL_DSN_KEYS.values():
        if key["project"]["id"] == project["id"]:
            keys.append({
                "id": key["id"],
                "label": key["label"],
                "dsn": key["dsn"],
                "dateCreated": key["dateCreated"],
                "isActive": key["isActive"],
            })
    return jsonify(keys)


@app.route("/api/0/organizations/<slug>/integrations/", methods=["GET"])
@require_session_or_token_auth
@require_token_scope("org:read")
def api_integrations(slug):
    """List integrations for an organization."""
    org = None
    for o in ORGANIZATIONS.values():
        if o["slug"] == slug:
            org = o
            break
    if not org:
        return jsonify({"detail": "Not found."}), 404

    result = []
    for integration in INTEGRATIONS.values():
        result.append({
            "id": integration["id"],
            "name": integration["name"],
            "provider": integration["provider"],
            "status": integration["status"],
            "config": integration["config"],
            "dateCreated": integration["dateCreated"],
        })
    return jsonify(result)


@app.route("/api/0/organizations/<slug>/stats/", methods=["GET"])
@require_session_or_token_auth
@require_token_scope("org:read")
def api_organization_stats(slug):
    """Get event statistics for an organization."""
    return jsonify({
        "received": [
            [1690934400, 1523],
            [1691020800, 1847],
            [1691107200, 1392],
        ],
        "rejected": [
            [1690934400, 12],
            [1691020800, 8],
            [1691107200, 15],
        ],
        "blacklisted": [
            [1690934400, 0],
            [1691020800, 0],
            [1691107200, 0],
        ],
    })


@app.route("/api/0/organizations/<slug>/onboarding/", methods=["GET"])
def api_onboarding(slug):
    """
    Public onboarding endpoint that provides SDK setup instructions.
    Intentionally public so new team members can self-serve.
    """
    org = None
    for o in ORGANIZATIONS.values():
        if o["slug"] == slug:
            org = o
            break
    if not org:
        return jsonify({"detail": "Not found."}), 404

    return jsonify({
        "organization": slug,
        "platforms": {
            "python": {
                "install": "pip install sentry-sdk",
                "config": {
                    "dsn": "https://abc123@o1.ingest.sentry.io/1",
                    "traces_sample_rate": 1.0,
                    "environment": "production",
                },
                "example": (
                    "import sentry_sdk\n"
                    "sentry_sdk.init(\n"
                    '    dsn="https://abc123@o1.ingest.sentry.io/1",\n'
                    "    traces_sample_rate=1.0,\n"
                    ")\n"
                ),
            },
            "javascript": {
                "install": "npm install @sentry/browser",
                "config": {
                    "dsn": "https://def456@o1.ingest.sentry.io/2",
                    "tracesSampleRate": 1.0,
                },
            },
        },
        "api_integration": {
            "description": "Use this read-only token to verify your integration is working",
            "token": "sntrys_lo_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
            "example_curl": (
                "curl -H 'Authorization: Bearer sntrys_lo_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6' "
                "https://sentry.io/api/0/organizations/sentry-internal/"
            ),
        },
    })


@app.route("/api/0/internal/health/", methods=["GET"])
def api_health():
    return jsonify({"ok": True})


# Healthcheck endpoint for k8s probes
@app.route("/_health/", methods=["GET"])
def healthcheck():
    return "ok", 200


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------

@app.errorhandler(404)
def not_found(e):
    if request.path.startswith("/api/"):
        return jsonify({"detail": "Not found."}), 404
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(e):
    if request.path.startswith("/api/"):
        return jsonify({"detail": "Internal server error."}), 500
    return render_template("500.html"), 500


# ---------------------------------------------------------------------------
# Startup
# ---------------------------------------------------------------------------

def _setup():
    """Set the flag value into the DSN key at startup."""
    flag = _read_flag()
    INTERNAL_DSN_KEYS[1]["dsn"]["secret"] = flag

_setup()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)
