from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User, LoginToken

from flask_session.sqlalchemy import SqlAlchemySessionInterface

import random
import string
import os
import secrets


app = Flask(__name__)

app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key')  # Use environment variable or fallback

# MySQL configurations - use environment variables with fallbacks for backward compatibility
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'toctou_admin_router')
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
app.session_interface = SqlAlchemySessionInterface(app=app, client=db, table='mysessions')


# Check if test user already exists in the database
test = User.query.filter_by(username='player1').first()
if not test:
    # Create a regular user without 2FA
    player1 = User(
        username='player1',
        password='gameserver123',
        name='Alex',
        lastname='Player',
        email='player1@example.com',
        is_admin=False,
        totp_enabled=False,
        totp_secret=None
    )
    db.session.add(player1)
    db.session.commit()

    # Create a regular user with 2FA enabled
    player2 = User(
        username='player2',
        password='minecraft2024',
        name='Sam',
        lastname='Gamer',
        email='player2@example.com',
        is_admin=False,
        totp_enabled=True,
        totp_secret=secrets.token_hex(16)
    )
    db.session.add(player2)
    db.session.commit()

    # Create an admin user with 2FA enabled (unknown password to attacker)
    admin = User(
        username='admin',
        password=''.join(random.choices(string.ascii_uppercase + string.digits, k=100)),
        name='Administrator',
        lastname='',
        email='admin@pterodactyl.local',
        is_admin=True,
        totp_enabled=True,
        totp_secret=secrets.token_hex(16)
    )
    db.session.add(admin)
    db.session.commit()

# Include routes
from app import routes
