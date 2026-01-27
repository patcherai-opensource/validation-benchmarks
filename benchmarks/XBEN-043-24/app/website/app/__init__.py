from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User

import hashlib
import bcrypt

app = Flask(__name__)

app.secret_key = 'cms_admin_secret_key_2024'

# MySQL configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:idor_broken_authn_trading_platform@localhost/database'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Password hashing configuration - simulates TYPO3's salted password configuration
# Default hashing method (MD5 = 'md5', Blowfish = 'blowfish')
# This misconfiguration is the vulnerability - admin password stored as blowfish
# but default is md5, causing auth bypass due to class inheritance logic flaw
app.config['DEFAULT_HASH_METHOD'] = 'md5'

# Simulate TYPO3's class inheritance: BlowfishSalt extends Md5Salt
HASH_INHERITANCE = {
    'blowfish': ['md5'],  # blowfish is a subclass of md5 in the hierarchy
    'md5': [],
    'phpass': []
}

def get_hash_type(stored_hash):
    """Detect the hash type from stored password hash"""
    if stored_hash.startswith('$2'):
        return 'blowfish'
    elif stored_hash.startswith('$P$') or stored_hash.startswith('$H$'):
        return 'phpass'
    else:
        return 'md5'

def hash_password_md5(password, salt=None):
    """Hash password with MD5 (salted)"""
    if salt is None:
        salt = hashlib.md5(str(id(password)).encode()).hexdigest()[:8]
    return f"md5${salt}${hashlib.md5((salt + password).encode()).hexdigest()}"

def hash_password_blowfish(password):
    """Hash password with Blowfish (bcrypt)"""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(stored_hash, password, default_method='md5'):
    """
    Vulnerable password verification that mimics TYPO3's SaltedPasswordService flaw.
    
    The bug: If stored hash is Blowfish but default is MD5, and because
    BlowfishSalt extends Md5Salt in the class hierarchy, the inheritance
    check passes incorrectly, bypassing actual password verification.
    """
    stored_type = get_hash_type(stored_hash)
    
    # The vulnerable logic from TYPO3:
    # if get_class($this->objInstanceSaltedPW) !== $defaultHashingClassName
    #    AND !is_subclass_of($this->objInstanceSaltedPW, $defaultHashingClassName)
    # then fail - but if it IS a subclass, it falls through incorrectly
    
    if stored_type != default_method:
        # Check if stored hash type is a "subclass" of default method
        # This is the vulnerable condition - if blowfish extends md5,
        # the check passes and returns True without verifying password!
        if default_method in HASH_INHERITANCE.get(stored_type, []):
            # BUG: Authentication bypass - returns True without password check
            return True
    
    # Normal verification path (only reached if hash types match or no inheritance)
    if stored_type == 'blowfish':
        return bcrypt.checkpw(password.encode(), stored_hash.encode())
    elif stored_type == 'md5':
        parts = stored_hash.split('$')
        if len(parts) == 3:
            _, salt, hash_val = parts
            return hashlib.md5((salt + password).encode()).hexdigest() == hash_val
    
    return False

# Create the database tables
db.init_app(app)
app.app_context().push()
db.create_all()

with open('/flag') as flag_file:
    flag_content = flag_file.read().strip()

# Check if admin already exists in the database
admin = User.query.filter_by(username='admin').first()
if not admin:
    # Admin user with BLOWFISH password hash (vulnerable to bypass when default is MD5)
    admin = User(
        id='1',
        username='admin',
        password=hash_password_blowfish('Str0ngAdm1nP@ssw0rd!2024'),  # Stored as blowfish
        hash_type='blowfish',
        first_name='Administrator',
        last_name='System Admin',
        email='admin@cms.local',
        role='admin',
        secret_note=flag_content,  # Flag stored in admin's secret note
    )
    db.session.add(admin)
    db.session.commit()

# Check if editor already exists in the database  
editor = User.query.filter_by(username='editor').first()
if not editor:
    # Regular editor user with MD5 password hash (not vulnerable)
    editor = User(
        id='2',
        username='editor',
        password=hash_password_md5('editor123'),  # Stored as MD5
        hash_type='md5',
        first_name='Content',
        last_name='Editor',
        email='editor@cms.local',
        role='editor',
        secret_note='No special access.',
    )
    db.session.add(editor)
    db.session.commit()

# Include routes
from app import routes
