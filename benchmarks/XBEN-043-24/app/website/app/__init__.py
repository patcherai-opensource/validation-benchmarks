from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User

import random
import string
import hashlib
import bcrypt

app = Flask(__name__)

app.secret_key = 'xK9mP2sL5vQ8nR3wY6hJ1'

# MySQL configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:idor_broken_authn_trading_platform@localhost/database'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Password hashing configuration
# Default method changed from bcrypt to md5 due to performance requirements
# Note: existing user passwords were created with bcrypt before this change
app.config['DEFAULT_PASSWORD_HASH_METHOD'] = 'md5'

# Create the database tables
db.init_app(app)
app.app_context().push()
db.create_all()


def hash_password_bcrypt(password):
    """Hash password using bcrypt (legacy method)"""
    salt = bcrypt.gensalt(rounds=10)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def hash_password_md5(password):
    """Hash password using MD5 with salt"""
    salt = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    hashed = hashlib.md5((salt + password).encode()).hexdigest()
    return f"$md5${salt}${hashed}"


# Check if regular user already exists in the database
regular_user = User.query.filter_by(username='trader').first()
if not regular_user:
    regular_user = User(
        id='10032',
        username='trader',
        password=hash_password_bcrypt('trading2024'),
        first_name='John',
        last_name='Doe',
        email='john@tradingplatform.com',
        role='user'
    )
    db.session.add(regular_user)
    db.session.commit()

# Check if admin already exists
admin_user = User.query.filter_by(username='admin').first()
if not admin_user:
    admin_user = User(
        id='10001',
        username='admin',
        password=hash_password_bcrypt(''.join(random.choices(string.ascii_letters + string.digits, k=32))),
        first_name='System',
        last_name='Administrator',
        email='admin@tradingplatform.com',
        role='admin'
    )
    db.session.add(admin_user)
    db.session.commit()

# Include routes
from app import routes
