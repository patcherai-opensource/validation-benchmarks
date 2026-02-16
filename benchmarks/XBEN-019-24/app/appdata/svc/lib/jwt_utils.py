"""
VaultKeeper - JWT Utilities
Token generation and validation for API authentication
"""
import hashlib
import hmac
import json
import base64
import time

JWT_SECRET = None

def get_bearer_token(headers):
    """Extract bearer token from Authorization header"""
    auth = headers.get('Authorization', '')
    if auth.startswith('Bearer '):
        return auth[7:]
    return None

def is_jwt_valid(token):
    """Validate JWT token"""
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return False
        payload = json.loads(base64.b64decode(parts[1] + '=='))
        if payload.get('exp', 0) < time.time():
            return False
        return True
    except Exception:
        return False

def get_bearer_data(token):
    """Extract payload data from JWT token"""
    try:
        parts = token.split('.')
        payload = json.loads(base64.b64decode(parts[1] + '=='))
        return payload
    except Exception:
        return None
