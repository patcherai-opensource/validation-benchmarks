import ipaddress
import functools
from flask import request, g, session, redirect, url_for, jsonify


def get_remote_address(req):
    """Determine the remote address of the client.

    Takes X-Forwarded-For header into account to handle proxied requests.
    """
    forwarded_for = req.headers.get("X-Forwarded-For", None)
    if forwarded_for is not None:
        return forwarded_for.split(",")[0].strip()
    return req.remote_addr


def is_local_address(address, local_networks):
    """Check if the given address falls within any of the configured local networks."""
    try:
        addr = ipaddress.ip_address(address)
        for network_str in local_networks:
            try:
                network = ipaddress.ip_network(network_str, strict=False)
                if addr in network:
                    return True
            except ValueError:
                continue
    except ValueError:
        pass
    return False


def configure_access_control(app, config):
    """Set up before_request hook for access control and autologin."""

    ac_config = config.get("accessControl", {})
    autologin_local = ac_config.get("autologinLocal", False)
    autologin_as = ac_config.get("autologinAs", None)
    local_networks = ac_config.get("localNetworks", ["127.0.0.0/8"])

    # In-memory user store
    app.config["USERS"] = {
        "admin": {
            "name": "admin",
            "active": True,
            "permissions": ["admin"],
            "apikey": ac_config.get("apikey", ""),
            "settings": {}
        }
    }

    @app.before_request
    def perform_autologin():
        # Skip for static files and ping endpoint
        if request.path.startswith("/static") or request.path == "/ping":
            return

        remote_addr = get_remote_address(request)
        g.remote_addr = remote_addr
        g.is_local = is_local_address(remote_addr, local_networks)

        if autologin_local and g.is_local and autologin_as:
            user = app.config["USERS"].get(autologin_as)
            if user and user.get("active", False):
                g.user = user
                g.autologin = True
                return

        # Check session-based authentication
        if session.get("authenticated") and session.get("username"):
            user = app.config["USERS"].get(session["username"])
            if user and user.get("active", False):
                g.user = user
                g.autologin = False
                return

        # Check API key authentication
        apikey = request.headers.get("X-Api-Key", None)
        if apikey:
            for username, user in app.config["USERS"].items():
                if user.get("apikey") == apikey:
                    g.user = user
                    g.autologin = False
                    return

        g.user = None
        g.autologin = False


def require_login(f):
    """Decorator to require authentication for a route."""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(g, "user") or g.user is None:
            if request.is_json or request.path.startswith("/api/"):
                return jsonify({"error": "Unauthorized"}), 401
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


def require_admin(f):
    """Decorator to require admin permissions."""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(g, "user") or g.user is None:
            if request.is_json or request.path.startswith("/api/"):
                return jsonify({"error": "Unauthorized"}), 401
            return redirect(url_for("login"))
        if "admin" not in g.user.get("permissions", []):
            return jsonify({"error": "Forbidden"}), 403
        return f(*args, **kwargs)
    return decorated_function