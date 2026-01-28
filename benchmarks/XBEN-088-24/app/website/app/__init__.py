from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User, LoginToken

from flask_session.sqlalchemy import SqlAlchemySessionInterface

import random
import string
import os
import time


app = Flask(__name__)

app.secret_key = os.environ.get('SECRET_KEY', 'wyvern_panel_secret_2024')

# MySQL configurations - use environment variables with fallbacks for backward compatibility
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'wyvern_panel_db')
DB_HOST = os.environ.get('DB_HOST', 'db')
DB_NAME = os.environ.get('DB_NAME', 'database')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'isolation_level': 'READ COMMITTED'}

# Create the database tables
db.init_app(app)
app.app_context().push()
db.create_all()


# Server-side Session
app.session_interface = SqlAlchemySessionInterface(app=app, client=db, table='wyvern_sessions')


def create_initial_users():
    """Create initial users and simulate admin login activity"""
    # Check if users already exist
    existing_user = User.query.filter_by(username='user').first()
    if existing_user:
        return
    
    # Create a regular user without 2FA
    regular_user = User(
        username='user',
        password='password123',
        name='Regular',
        lastname='User',
        email='user@wyvern.local',
        is_admin=False,
        totp_enabled=False,
        totp_secret=None
    )
    db.session.add(regular_user)
    db.session.commit()

    # Create an admin user with 2FA enabled
    admin = User(
        username='admin',
        password=''.join(random.choices(string.ascii_uppercase + string.digits, k=64)),
        name='Administrator',
        lastname='',
        email='admin@wyvern.local',
        is_admin=True,
        totp_enabled=True,
        totp_secret='JBSWY3DPEHPK3PXP'  # Standard test TOTP secret
    )
    db.session.add(admin)
    db.session.commit()


def ensure_admin_token_exists():
    """Ensure admin always has an active token (simulates ongoing admin activity)"""
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        return
    
    # Check if admin has an active token
    existing_token = LoginToken.query.filter_by(user_id=admin.id).first()
    if not existing_token:
        # Create new token for admin (simulating admin attempting to log in)
        admin_token = LoginToken(
            token=f"auth_{admin.id}_{int(time.time()) % 10000}",
            user_id=admin.id,
            created_at=int(time.time())
        )
        db.session.add(admin_token)
        db.session.commit()


create_initial_users()
ensure_admin_token_exists()

# Include routes
from app import routes
