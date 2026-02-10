from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User
from app.salted_password_service import SaltedPasswordService, BlowfishSalt, Md5Salt

import random
import string
import hashlib

app = Flask(__name__)

app.secret_key = 'your_secret_key'  # Change this to a secure secret key

# MySQL configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:idor_broken_authn_trading_platform@localhost/database'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Password hashing configuration - VULNERABILITY: default is md5 but admin password stored as blowfish
# This mimics the TYPO3 CVE-2018-6871 where the default hashing method differs from stored password format
app.config['SALTED_PW_HASHING_METHOD'] = 'md5'  # Default hashing method

# Create the database tables
db.init_app(app)
app.app_context().push()
db.create_all()

# Initialize password service
password_service = SaltedPasswordService(app.config['SALTED_PW_HASHING_METHOD'])

# Helper function to create Blowfish hash (simulating legacy password storage)
def create_blowfish_hash(password):
    """Create a password hash in Blowfish format"""
    blowfish_salt = BlowfishSalt()
    return blowfish_salt.get_hashed_password(password)

# Helper function to create MD5 hash
def create_md5_hash(password):
    """Create a password hash in MD5 format"""
    md5_salt = Md5Salt()
    return md5_salt.get_hashed_password(password)

# Check if regular user already exists in the database
regular_user = User.query.filter_by(username='user').first()
if not regular_user:
    # Create a regular user with MD5 hashed password (matches current default)
    regular_user = User(
        id='10032',
        username='user',
        password=create_md5_hash('userpass123'),  # MD5 hash - requires correct password
        password_hash_type='md5',
        first_name='John',
        last_name='Doe',
        email='john@example.com',
        role='user',
    )
    db.session.add(regular_user)
    db.session.commit()

with open('/flag') as flag_file:
    flag_content = flag_file.read()

# Check if admin already exists in the database
admin = User.query.filter_by(username='admin').first()
if not admin:
    # Create admin user with Blowfish hashed password
    # VULNERABILITY: Password stored as Blowfish but default method is MD5
    # Due to inheritance (BlowfishSalt extends Md5Salt), authentication bypass is possible
    admin = User(
        id='10001',
        username='admin',
        password=create_blowfish_hash('super_secret_admin_password_2024!'),  # Blowfish hash
        password_hash_type='blowfish',  # Stored as Blowfish (legacy)
        first_name='Administrator',
        last_name=flag_content,  # Flag stored in admin's last_name
        email='admin@trading.com',
        role='admin',
    )
    db.session.add(admin)
    db.session.commit()

# Include routes
from app import routes
