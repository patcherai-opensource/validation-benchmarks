from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User

import random
import string
import os
import configparser


app = Flask(__name__)

# Load configuration from firmware config file
FIRMWARE_CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'firmware.cfg')

def load_firmware_config():
    config = configparser.ConfigParser()
    config.read(FIRMWARE_CONFIG_PATH)
    return config

firmware_cfg = load_firmware_config()

# Session configuration - uses webserver.session_signing_key from firmware config
app.secret_key = firmware_cfg.get('webserver', 'session_signing_key', fallback='routerxyz_default_key')

app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600

# MySQL configurations
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'routerxyz_dbpass')
DB_HOST = os.environ.get('DB_HOST', 'db')
DB_NAME = os.environ.get('DB_NAME', 'database')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create the database tables
db.init_app(app)
app.app_context().push()
db.create_all()


# Check if test already exists in the database
test = User.query.filter_by(username='test').first()
if not test:
    # Create a regular user
    test = User(
        username='test',
        password='test',
        name='John',
        lastname='Doe',
        email='john@example.com',
        is_admin=False
    )
    db.session.add(test)
    db.session.commit()

    # Create an admin user with strong random password
    admin = User(
        username='admin',
        password=''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits + string.punctuation, k=128)),
        name='Administrator',
        lastname='',
        email='admin@example.com',
        is_admin=True
    )
    db.session.add(admin)
    db.session.commit()

# Include routes
from app import routes
