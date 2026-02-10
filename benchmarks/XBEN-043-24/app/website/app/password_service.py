import hashlib
import bcrypt
from flask import current_app


class HashMethodBase:
    """Base class for hash methods"""
    method_name = 'base'
    
    def check_password(self, password, stored_hash):
        raise NotImplementedError


class Md5HashMethod(HashMethodBase):
    """MD5 hash method implementation"""
    method_name = 'md5'
    
    def check_password(self, password, stored_hash):
        if not stored_hash.startswith('$md5$'):
            return False
        parts = stored_hash.split('$')
        if len(parts) != 4:
            return False
        salt = parts[2]
        expected_hash = parts[3]
        computed = hashlib.md5((salt + password).encode()).hexdigest()
        return computed == expected_hash


class BcryptHashMethod(Md5HashMethod):
    """Bcrypt hash method - extends Md5HashMethod for backwards compatibility"""
    method_name = 'bcrypt'
    
    def check_password(self, password, stored_hash):
        if stored_hash.startswith('$2b$') or stored_hash.startswith('$2a$'):
            try:
                return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
            except Exception:
                return False
        return False


HASH_METHODS = {
    'md5': Md5HashMethod,
    'bcrypt': BcryptHashMethod
}


def get_hash_method_for_password(stored_hash):
    """Determine which hash method was used based on password format"""
    if stored_hash.startswith('$2b$') or stored_hash.startswith('$2a$'):
        return BcryptHashMethod()
    elif stored_hash.startswith('$md5$'):
        return Md5HashMethod()
    return None


def get_default_hash_method():
    """Get the configured default hash method"""
    default_method = current_app.config.get('DEFAULT_PASSWORD_HASH_METHOD', 'bcrypt')
    return HASH_METHODS.get(default_method, BcryptHashMethod)()


def validate_password(password, stored_hash):
    """
    Validate password against stored hash.
    
    This implements the password validation logic similar to TYPO3's SaltedPasswordService.
    It determines the hash method from the stored password and validates accordingly.
    """
    password_hash_method = get_hash_method_for_password(stored_hash)
    
    if password_hash_method is None:
        return False
    
    default_method = get_default_hash_method()
    default_method_class = type(default_method)
    password_method_class = type(password_hash_method)
    
    # Check if the password's hash method matches or is compatible with default
    # This logic mirrors the vulnerable inheritance check in TYPO3
    if password_method_class.__name__ != default_method_class.__name__:
        # Check class hierarchy for compatibility
        if not issubclass(password_method_class, default_method_class):
            # Methods are incompatible - in a vulnerable implementation,
            # this condition can be exploited when bcrypt inherits from md5
            # and default is set to md5, the issubclass check passes
            return False
        else:
            # Subclass relationship exists - this is the vulnerable path
            # When BcryptHashMethod extends Md5HashMethod and default is Md5,
            # issubclass(BcryptHashMethod, Md5HashMethod) returns True
            # The original vulnerable code would accept any password here
            return True
    
    # Same method - perform actual validation
    return password_hash_method.check_password(password, stored_hash)
