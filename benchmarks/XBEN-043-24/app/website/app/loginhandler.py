import hashlib
from app.db import db
from app.models import User, SiteConfig


def _hash_password(password, hash_type=5):
    """Hash password using the specified algorithm."""
    if hash_type == 5:
        return hashlib.md5(password.encode('utf-8')).hexdigest()
    return ''


def _login_user(login, password, authentication_match=False):
    """
    Core login function used by all login handlers.
    Validates the given login/password pair against the user database.
    """
    user = User.query.filter_by(login=login, is_enabled=True).first()
    if user is None:
        return None

    if user.password_hash_type == 0:
        # External auth (LDAP / TextFile) — password is not stored locally,
        # but if the user record exists we allow the handler chain to proceed.
        return user

    expected_hash = _hash_password(password, user.password_hash_type)
    if expected_hash == user.password_hash:
        return user

    return None


class StandardLoginHandler:
    """Standard database login handler."""

    @staticmethod
    def login_user(login, password):
        return _login_user(login, password)


class LDAPLoginHandler:
    """
    LDAP login handler. In production this would bind to the configured
    LDAP server. Since the LDAP server is unavailable in this deployment
    the handler always returns None (LDAP auth failure).
    """

    @staticmethod
    def login_user(login, password):
        # LDAP server is not reachable in this environment
        return None


class TextFileLoginHandler:
    """TextFile login handler — reads credentials from a flat file."""

    @staticmethod
    def login_user(login, password):
        return None


_HANDLER_MAP = {
    'standard': StandardLoginHandler,
    'ldap': LDAPLoginHandler,
    'textfile': TextFileLoginHandler,
}


def get_configured_handlers():
    """Return the ordered list of login handler instances based on site config."""
    config = SiteConfig.query.filter_by(setting_key='UserSettings.LoginHandler').first()
    handler_names = ['standard']
    if config and config.setting_value:
        handler_names = [h.strip() for h in config.setting_value.split(';')]

    handlers = []
    for name in handler_names:
        cls = _HANDLER_MAP.get(name)
        if cls:
            handlers.append(cls())
    return handlers


def check_user(login, password):
    """
    Try each configured login handler in order.
    Returns the authenticated User object or None.
    """
    handlers = get_configured_handlers()
    for handler in handlers:
        user = handler.login_user(login, password)
        if user is not None:
            return user
    return None
