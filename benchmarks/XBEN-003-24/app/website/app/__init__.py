from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User

import random
import string
import os

app = Flask(__name__)

app.secret_key = 'your_secret_key'  # Change this to a secure secret key

# MySQL configurations - now using environment variables for K8s compatibility
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'enterprise_portal_db')
DB_NAME = os.environ.get('DB_NAME', 'database')
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Internal API configuration - DO NOT EXPOSE
# The SECRET_API_KEY is used for internal service authentication
flag_content = os.environ.get('FLAG', 'FLAG{default_flag}')
app.config['SECRET_API_KEY'] = flag_content
app.config['INTERNAL_SERVICE_URL'] = 'http://internal-api.corp.local:8443'
app.config['DEBUG_MODE'] = True  # TODO: Disable in production

# Create the database tables
db.init_app(app)
app.app_context().push()
db.create_all()

# Check if admin user exists
admin = User.query.filter_by(username='admin').first()
if not admin:
    # Create admin user with secure password
    admin = User(
        id='1001',
        username='admin',
        password=''.join(random.choices(string.ascii_letters + string.digits, k=32)),
        first_name='System',
        last_name='Administrator',
        email='admin@enterprise.local',
    )
    db.session.add(admin)
    db.session.commit()

# Check if demo user exists
demo = User.query.filter_by(username='demo').first()
if not demo:
    # Create demo user for testing
    demo = User(
        id='1002',
        username='demo',
        password='demo123',
        first_name='Demo',
        last_name='User',
        email='demo@enterprise.local',
    )
    db.session.add(demo)
    db.session.commit()

# Include routes
from app import routes
