import jwt
import os
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, g
from models import User

SECRET_KEY = os.getenv("SECRET_KEY", "f7c2a1e8b9d04567891234abcdef5678")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def create_access_token(user_id, role):
    payload = {
        "sub": str(user_id),
        "role": role,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_current_user():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ", 1)[1]
    payload = decode_token(token)
    if not payload:
        return None
    user = User.objects(id=payload["sub"]).first()
    if user and user.is_active:
        return user
    return None


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({"detail": "Not authenticated"}), 401
        g.current_user = user
        return f(*args, **kwargs)
    return decorated


def require_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({"detail": "Not authenticated"}), 401
        if user.role != "admin":
            return jsonify({"detail": "Admin privileges required"}), 403
        g.current_user = user
        return f(*args, **kwargs)
    return decorated


def require_curator_or_admin(f):
    """Require the user to have curator or admin role."""
    @wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({"detail": "Not authenticated"}), 401
        if user.role not in ("admin", "curator"):
            return jsonify({"detail": "Curator or admin privileges required"}), 403
        g.current_user = user
        return f(*args, **kwargs)
    return decorated
