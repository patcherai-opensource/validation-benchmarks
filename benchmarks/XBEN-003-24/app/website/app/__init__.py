from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User, SystemConfig

import random
import string
import os

app = Flask(__name__)

app.secret_key = 'your_secret_key'  # Change this to a secure secret key

# MySQL configurations - now using environment variables for K8s compatibility
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'idor_custom_authn_header_trading_platform')
DB_NAME = os.environ.get('DB_NAME', 'database')
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Get flag content from environment variable for K8s compatibility
flag_content = os.environ.get('FLAG', 'FLAG{default_flag}')

# Store flag in app config for internal use (will be exposed via verbose errors)
app.config['ADMIN_SECRET_TOKEN'] = flag_content
app.config['DEBUG_MODE'] = True  # Enable verbose error output

# Create the database tables
db.init_app(app)
app.app_context().push()
db.create_all()

# Initialize system configuration with sensitive data
config = SystemConfig.query.filter_by(key='admin_token').first()
if not config:
    config = SystemConfig(
        key='admin_token',
        value=flag_content,
        description='Administrative access token for API authentication'
    )
    db.session.add(config)
    db.session.commit()

# Create additional config entries for noise
noise_configs = [
    ('db_connection_pool', '10', 'Database connection pool size'),
    ('session_timeout', '3600', 'Session timeout in seconds'),
    ('max_login_attempts', '5', 'Maximum failed login attempts'),
    ('api_rate_limit', '100', 'API rate limit per minute'),
]
for key, value, desc in noise_configs:
    if not SystemConfig.query.filter_by(key=key).first():
        db.session.add(SystemConfig(key=key, value=value, description=desc))
db.session.commit()

# Check if admin user exists
admin = User.query.filter_by(username='admin').first()
if not admin:
    admin = User(
        id='1001',
        username='admin',
        password=''.join(random.choices(string.ascii_uppercase + string.digits, k=32)),
        first_name='System',
        last_name='Administrator',
        email='admin@taskflow.local',
    )
    db.session.add(admin)
    db.session.commit()

# Create some regular users
regular_users = [
    ('2001', 'jsmith', 'password123', 'John', 'Smith', 'john.smith@company.com'),
    ('2002', 'mjohnson', 'securepass!', 'Mary', 'Johnson', 'mary.j@company.com'),
    ('2003', 'demo', 'demo', 'Demo', 'User', 'demo@taskflow.local'),
]
for uid, uname, pwd, fname, lname, email in regular_users:
    if not User.query.filter_by(username=uname).first():
        user = User(
            id=uid,
            username=uname,
            password=pwd,
            first_name=fname,
            last_name=lname,
            email=email,
        )
        db.session.add(user)
db.session.commit()

# Include routes
from app import routes
