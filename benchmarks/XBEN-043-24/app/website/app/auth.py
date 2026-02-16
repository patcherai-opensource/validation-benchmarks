import hashlib
from app.db import db
from app.models import User
from flask import current_app


def _compute_hash(username, password, mode):
    """
    Compute password hash based on the credential mode.
    
    Modes:
        0 - No hash (disabled / externally managed)
        1 - MD5 of password
        2 - SHA256 of username + password
        3 - SHA256 of password only
    """
    if mode == 1:
        return hashlib.md5(password.encode('utf-8')).hexdigest()
    elif mode == 2:
        return hashlib.sha256((username + '\n' + password).encode('utf-8')).hexdigest()
    elif mode == 3:
        return hashlib.sha256(password.encode('utf-8')).hexdigest()
    return ''


def _verify_credentials(login, password):
    """
    Core credential verification. Looks up the user by login and verifies
    the password against the stored hash according to the credential mode.
    
    Returns:
        User object if authentication succeeds.
        user_id (int) if user exists but authentication failed.
        False if user does not exist.
    """
    user = User.query.filter_by(username=login, is_active=True).first()
    
    if user is None:
        return False
    
    stored_hash = user.password_hash
    hash_type = user.credential_mode
    
    computed = _compute_hash(user.username, password, hash_type)
    
    if computed == stored_hash:
        return user
    
    return user.id


def _standard_handler(login, password):
    """Standard database authentication handler."""
    result = _verify_credentials(login, password)
    if isinstance(result, User):
        return result
    return None


def _ldap_handler(login, password):
    """
    LDAP authentication handler stub.
    
    In production this would connect to an LDAP directory server.
    If LDAP auth fails or is unreachable, falls back to the standard 
    database verification for accounts provisioned from LDAP.
    """
    # LDAP bind would happen here; if unreachable, fall through to DB lookup
    result = _verify_credentials(login, password)
    if isinstance(result, User):
        return result
    return None


def _textfile_handler(login, password):
    """
    TextFile authentication handler stub.
    
    Authenticates against a local credential file. Falls back to DB
    verification for provisioned accounts.
    """
    result = _verify_credentials(login, password)
    if isinstance(result, User):
        return result
    return None


_HANDLER_MAP = {
    'standard': _standard_handler,
    'ldap': _ldap_handler,
    'textfile': _textfile_handler,
}


def verify_credentials(login, password):
    """
    Iterate through configured authentication providers and attempt login.
    Returns a User object on success, None on failure.
    """
    providers = current_app.config.get('AUTH_PROVIDERS', ['standard'])
    
    for provider_name in providers:
        handler = _HANDLER_MAP.get(provider_name)
        if handler is None:
            continue
        user = handler(login, password)
        if user is not None:
            return user
    
    return None
