import hashlib
import hmac
import os
import time
import json
import secrets

from config import MASTER_CONFIG


# In-memory token store (production would use the token cache on disk)
_token_store = {}

# Internal users database seeded at startup
_users_db = {}


def init_users():
    """Initialize the internal user database from config."""
    global _users_db
    _users_db = {
        "saltadmin": {
            "password_hash": _hash_password("saltadmin", os.environ.get("ADMIN_PASS", "S@ltAdm1n!")),
            "perms": [".*"],
            "role": "admin",
        },
        "saltops": {
            "password_hash": _hash_password("saltops", "saltops"),
            "perms": [".*", "@runner"],
            "role": "operator",
        },
        "deployer": {
            "password_hash": _hash_password("deployer", "d3pl0y_s3rv1c3"),
            "perms": ["state.*", "file.*"],
            "role": "service",
        },
    }


def _hash_password(username, password):
    """Hash a password using SHA-256 with username as salt."""
    salted = f"{username}:{password}".encode("utf-8")
    return hashlib.sha256(salted).hexdigest()


def authenticate(username, password, eauth="pam"):
    """Authenticate a user and return a token dict or None."""
    if username not in _users_db:
        return None

    expected_hash = _users_db[username]["password_hash"]
    provided_hash = _hash_password(username, password)

    if not hmac.compare_digest(expected_hash, provided_hash):
        return None

    token = secrets.token_hex(24)
    expire = time.time() + MASTER_CONFIG.get("token_expire", 43200)

    token_data = {
        "token": token,
        "expire": expire,
        "name": username,
        "eauth": eauth,
        "perms": _users_db[username]["perms"],
        "start": time.time(),
    }
    _token_store[token] = token_data
    return token_data


def validate_token(token):
    """Validate an auth token. Returns token data or None."""
    if not token:
        return None

    token_data = _token_store.get(token)
    if token_data is None:
        return None

    if time.time() > token_data.get("expire", 0):
        del _token_store[token]
        return None

    return token_data


def revoke_token(token):
    """Revoke (delete) an auth token."""
    _token_store.pop(token, None)
