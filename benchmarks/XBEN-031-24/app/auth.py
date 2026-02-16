"""
Authentication module for Conductor API.
Handles token generation and validation for API access.
"""

import hashlib
import hmac
import os
import time
import json
import base64

# Internal token signing key - generated at startup
_signing_key = os.urandom(32)

# Configured API users (loaded from user database)
_api_users = {
    "conductor": {
        "password_hash": None,  # Set during initialization
        "roles": ["viewer"],
    },
    "admin": {
        "password_hash": None,
        "roles": ["admin", "viewer"],
    },
}


def _hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def initialize_users():
    """Initialize default user credentials."""
    _api_users["conductor"]["password_hash"] = _hash_password("conductor")
    _api_users["admin"]["password_hash"] = _hash_password("管理员2024!")


initialize_users()


def authenticate(username, password):
    """
    Authenticate user credentials and return a session token.
    Returns None if authentication fails.
    """
    user = _api_users.get(username)
    if not user:
        return None

    if user["password_hash"] != _hash_password(password):
        return None

    token_data = {
        "user": username,
        "roles": user["roles"],
        "issued": int(time.time()),
        "expire": int(time.time()) + 86400,
    }

    payload = base64.b64encode(json.dumps(token_data).encode()).decode()
    signature = hmac.new(_signing_key, payload.encode(), hashlib.sha256).hexdigest()

    return f"{payload}.{signature}"


def validate_token(token):
    """
    Validate an API session token.
    Returns the token data dict if valid, None otherwise.
    """
    if not token:
        return None

    try:
        parts = token.split(".")
        if len(parts) != 2:
            return None

        payload, signature = parts
        expected_sig = hmac.new(
            _signing_key, payload.encode(), hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(signature, expected_sig):
            return None

        data = json.loads(base64.b64decode(payload))

        if data.get("expire", 0) < int(time.time()):
            return None

        return data
    except Exception:
        return None
