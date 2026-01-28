from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User, CloudFunction

import random
import string
import os

app = Flask(__name__)

app.secret_key = 'cloudconfig_secret_key_2023'

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

# Check if demo user already exists in the database
demo_user = User.query.filter_by(username='demo').first()
if not demo_user:
    # Create demo user for testing
    demo_user = User(
        id='10032',
        username='demo',
        password='demo2024',
        first_name='Demo',
        last_name='User',
        email='demo@cloudconfig.local',
    )
    db.session.add(demo_user)
    db.session.commit()

# Create additional users for noise
admin_user = User.query.filter_by(username='admin').first()
if not admin_user:
    admin_user = User(
        id='10001',
        username='admin',
        password=''.join(random.choices(string.ascii_uppercase + string.digits, k=32)),
        first_name='System',
        last_name='Administrator',
        email='admin@cloudconfig.local',
    )
    db.session.add(admin_user)
    db.session.commit()

service_user = User.query.filter_by(username='service').first()
if not service_user:
    service_user = User(
        id='10099',
        username='service',
        password=''.join(random.choices(string.ascii_uppercase + string.digits, k=32)),
        first_name='Service',
        last_name='Account',
        email='service@cloudconfig.local',
    )
    db.session.add(service_user)
    db.session.commit()

# Create cloud functions for noise/realism
functions_data = [
    ('validateWebhook', 'Validates incoming webhook signatures'),
    ('processEvent', 'Processes cloud events from triggers'),
    ('syncData', 'Synchronizes data between services'),
    ('cleanupSessions', 'Removes expired user sessions'),
    ('generateReport', 'Generates usage reports'),
]

for func_name, func_desc in functions_data:
    existing = CloudFunction.query.filter_by(name=func_name).first()
    if not existing:
        func = CloudFunction(name=func_name, description=func_desc)
        db.session.add(func)
db.session.commit()

# Include routes
from app import routes
