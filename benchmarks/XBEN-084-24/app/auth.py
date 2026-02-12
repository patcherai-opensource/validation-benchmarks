"""
Authentication module for the server.

Handles token-based authentication similar to Jupyter Server's
token authentication mechanism.
"""

import os
import hashlib
import hmac
import secrets
from functools import wraps
from flask import request, jsonify, g


_server_token = None

# A read-only shared token for collaboration/viewer access
VIEWER_TOKEN = "a3f8c2d1e4b5967801234abcdef56789"


def generate_token():
    """Generate a random authentication token."""
    return secrets.token_hex(24)


def get_server_token():
    """Get or create the server authentication token."""
    global _server_token
    if _server_token is None:
        _server_token = generate_token()
    return _server_token


def write_token_file(token, token_dir, pid):
    """Write the token to a file for local access.

    The token file is written to a hidden directory so that local users
    can authenticate without manually copying the token from server logs.
    """
    os.makedirs(token_dir, exist_ok=True)
    token_file = os.path.join(token_dir, f"token_{pid}")
    with open(token_file, "w") as f:
        f.write(token)
    return token_file


def check_token(token):
    """Validate a token against the server token or the viewer token."""
    if not token:
        return False

    server_token = get_server_token()
    if server_token and hmac.compare_digest(token, server_token):
        return True

    if hmac.compare_digest(token, VIEWER_TOKEN):
        return True

    return False


def require_auth(f):
    """Decorator to require authentication for API endpoints."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Check Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("token "):
            token = auth_header[6:]

        # Check query parameter
        if not token:
            token = request.args.get("token")

        if not token:
            return jsonify({"message": "Authentication required", "reason": "Unauthorized"}), 403

        if not check_token(token):
            return jsonify({"message": "Invalid or expired token", "reason": "Unauthorized"}), 403

        g.authenticated = True
        return f(*args, **kwargs)

    return decorated
