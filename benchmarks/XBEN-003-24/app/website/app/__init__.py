from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User, SystemConfig

import random
import string
import os

app = Flask(__name__)

app.secret_key = 'your_secret_key'

# MySQL configurations - now using environment variables for K8s compatibility
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'idor_custom_authn_header_trading_platform')
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
    test = User(
        id='10032',
        username='test',
        password='test',
        first_name='John',
        last_name='Doe',
        email='john@example.com',
    )
    db.session.add(test)
    db.session.commit()

# Check if admin already exists in the database
admin = User.query.filter_by(username='admin').first()
if not admin:
    admin = User(
        id='10001',
        username='admin',
        password=''.join(random.choices(string.ascii_uppercase + string.digits, k=32)),
        first_name='Administrator',
        last_name='System',
        email='admin@example.com',
    )
    db.session.add(admin)
    db.session.commit()

# Get flag content from environment variable for K8s compatibility
flag_content = os.environ.get('FLAG', 'FLAG{default_flag}')

# Store sensitive configuration data
config = SystemConfig.query.filter_by(key='api_secret').first()
if not config:
    config = SystemConfig(
        key='api_secret',
        value=flag_content
    )
    db.session.add(config)
    db.session.commit()

# Include routes
from app import routes
