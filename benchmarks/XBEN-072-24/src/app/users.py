import hashlib
import hmac
from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, username, password_hash, active=True, admin=False, apikey=None):
        self._username = username
        self._password_hash = password_hash
        self._active = active
        self._admin = admin
        self._apikey = apikey

    def get_id(self):
        return self._username

    @property
    def is_active(self):
        return self._active

    @property
    def is_admin(self):
        return self._admin

    @property
    def apikey(self):
        return self._apikey

    def check_password(self, password):
        salt = "e8f4a2c6d0b8f2a4c6e8d0b2f4a6c8e0"
        hashed = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt.encode("utf-8"), 260000
        )
        return hmac.compare_digest(hashed.hex(), self._password_hash)

    def as_dict(self):
        return {
            "name": self._username,
            "active": self._active,
            "admin": self._admin,
            "needs": {
                "role": ["admin"] if self._admin else ["user"],
            },
        }


class AnonymousUser:
    def __init__(self):
        self._username = "_anonymous"

    def get_id(self):
        return self._username

    @property
    def is_active(self):
        return False

    @property
    def is_anonymous(self):
        return True

    @property
    def is_authenticated(self):
        return False

    @property
    def is_admin(self):
        return False

    def as_dict(self):
        return {
            "name": self._username,
            "active": False,
            "admin": False,
            "needs": {"role": []},
        }


class UserManager:
    def __init__(self, cfg):
        self._users = {}
        users_cfg = cfg.get("users", {})
        for username, data in users_cfg.items():
            self._users[username] = User(
                username=username,
                password_hash=data.get("password", ""),
                active=data.get("active", True),
                admin=data.get("admin", False),
                apikey=data.get("apikey"),
            )

    def find_user(self, username):
        return self._users.get(username)

    def validate_apikey(self, key):
        for user in self._users.values():
            if user.apikey and user.apikey == key:
                return user
        return None

    def anonymous_user(self):
        return AnonymousUser()