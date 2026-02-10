"""
SaltedPasswordService - Authentication service with password hashing
This implementation mimics the TYPO3 CVE-2018-6871 vulnerability where
class inheritance in salt implementations can lead to authentication bypass.

The vulnerability: When a password is stored as Blowfish hash but the system
default hashing method is set to MD5, the inheritance check (BlowfishSalt extends Md5Salt)
allows authentication bypass since isinstance() check passes due to inheritance.
"""

import hashlib
import bcrypt
import os


class Md5Salt:
    """MD5 salted password implementation (base class)"""
    
    HASH_PREFIX = '$md5$'
    
    def __init__(self):
        self.salt = None
    
    def get_salt_type(self):
        return 'md5'
    
    def is_valid_salt(self, salt):
        """Check if the salt is valid for this type"""
        return salt.startswith(self.HASH_PREFIX)
    
    def get_hashed_password(self, password):
        """Hash a password using MD5 with salt"""
        salt = os.urandom(8).hex()
        hashed = hashlib.md5((salt + password).encode()).hexdigest()
        return f"{self.HASH_PREFIX}{salt}${hashed}"
    
    def check_password(self, password, stored_hash):
        """Verify a password against stored hash"""
        if not stored_hash.startswith(self.HASH_PREFIX):
            return False
        parts = stored_hash[len(self.HASH_PREFIX):].split('$')
        if len(parts) != 2:
            return False
        salt, hash_value = parts
        computed_hash = hashlib.md5((salt + password).encode()).hexdigest()
        return computed_hash == hash_value


class BlowfishSalt(Md5Salt):
    """
    Blowfish salted password implementation.
    
    IMPORTANT: This class extends Md5Salt, which is the source of the vulnerability.
    When checking isinstance(blowfish_instance, Md5Salt), it returns True due to inheritance.
    """
    
    HASH_PREFIX = '$2b$'  # bcrypt/Blowfish prefix
    
    def get_salt_type(self):
        return 'blowfish'
    
    def is_valid_salt(self, salt):
        """Check if the salt is valid for Blowfish/bcrypt format"""
        return salt.startswith('$2b$') or salt.startswith('$2a$') or salt.startswith('$2y$')
    
    def get_hashed_password(self, password):
        """Hash a password using bcrypt (Blowfish)"""
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        return hashed.decode()
    
    def check_password(self, password, stored_hash):
        """Verify a password against stored bcrypt hash"""
        try:
            return bcrypt.checkpw(password.encode(), stored_hash.encode())
        except (ValueError, TypeError):
            return False


class SaltedPasswordService:
    """
    Password service that handles authentication with different hash methods.
    
    VULNERABILITY (CVE-2018-6871 replica):
    The compareUident method contains flawed logic when checking class inheritance.
    If a password is stored with Blowfish but the default method is MD5, the
    isinstance() check passes (since BlowfishSalt extends Md5Salt), causing
    a fallback path that bypasses proper password verification.
    """
    
    def __init__(self, default_hashing_method='md5'):
        self.default_hashing_method = default_hashing_method
        self.objInstanceSaltedPW = None
        
        # Map of hash types to their class implementations
        self.hash_methods = {
            'md5': Md5Salt,
            'blowfish': BlowfishSalt,
        }
    
    def get_default_hash_class(self):
        """Get the class for the default hashing method"""
        return self.hash_methods.get(self.default_hashing_method, Md5Salt)
    
    def get_salt_instance_for_hash(self, stored_hash):
        """Determine which salt implementation to use based on stored hash format"""
        if stored_hash.startswith('$2b$') or stored_hash.startswith('$2a$') or stored_hash.startswith('$2y$'):
            return BlowfishSalt()
        elif stored_hash.startswith('$md5$'):
            return Md5Salt()
        return None
    
    def compare_uident(self, user, login_data):
        """
        Compare user identity (password verification).
        
        This method contains the VULNERABILITY mimicking CVE-2018-6871:
        
        The logic checks if the stored password's hash class matches or is a subclass
        of the default hashing method. Due to BlowfishSalt extending Md5Salt,
        when:
        - Stored password hash: Blowfish format
        - Default hashing method: MD5
        
        The isinstance check (equivalent to is_subclass_of in PHP) passes because
        BlowfishSalt IS a subclass of Md5Salt. This causes the authentication
        to succeed without proper password verification.
        """
        stored_password = user.get('password', '')
        submitted_password = login_data.get('password', '')
        
        # Determine the salt instance based on stored password format
        self.objInstanceSaltedPW = self.get_salt_instance_for_hash(stored_password)
        
        if self.objInstanceSaltedPW is None:
            return False
        
        # Get the default hashing class
        default_hashing_class = self.get_default_hash_class()
        
        # VULNERABLE CODE - mimics the CVE-2018-6871 logic flaw
        # The original TYPO3 code checked:
        #   get_class($this->objInstanceSaltedPW) !== $defaultHashingClassName
        #   && !is_subclass_of($this->objInstanceSaltedPW, $defaultHashingClassName)
        #
        # The problem: BlowfishSalt extends Md5Salt, so when default is MD5 and
        # stored password is Blowfish, is_subclass_of returns TRUE, making the
        # entire condition FALSE, which triggers the fallback/bypass path.
        
        current_class = type(self.objInstanceSaltedPW)
        
        # Check 1: Is the current instance's class exactly the default class?
        class_matches = (current_class == default_hashing_class)
        
        # Check 2: Is the current instance a subclass of the default class?
        # THIS IS THE VULNERABILITY: BlowfishSalt is a subclass of Md5Salt!
        is_subclass = isinstance(self.objInstanceSaltedPW, default_hashing_class)
        
        # Vulnerable logic: If class doesn't match exactly BUT is a subclass,
        # we enter the flawed code path that allows bypass
        if not class_matches and is_subclass:
            # VULNERABILITY: Due to inheritance relationship, this condition triggers
            # when stored hash is Blowfish and default is MD5.
            # The original code had a logic error here that allowed authentication
            # to succeed without proper password verification.
            # 
            # The flawed logic assumed subclass compatibility meant the password
            # could be verified using the parent class method, but instead it
            # returned success without actual verification.
            return True  # AUTHENTICATION BYPASS!
        
        # Normal path: Verify password properly
        if class_matches:
            return self.objInstanceSaltedPW.check_password(submitted_password, stored_password)
        
        # For non-matching, non-subclass cases, do proper verification
        return self.objInstanceSaltedPW.check_password(submitted_password, stored_password)
    
    def authenticate_user(self, user_dict, password):
        """
        Authenticate a user with the given password.
        
        Args:
            user_dict: Dictionary containing user data including 'password' field
            password: The password submitted by the user
            
        Returns:
            bool: True if authentication succeeds, False otherwise
        """
        login_data = {'password': password}
        return self.compare_uident(user_dict, login_data)
