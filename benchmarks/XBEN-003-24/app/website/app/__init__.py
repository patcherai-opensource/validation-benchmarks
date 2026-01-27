from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User, Organization

import random
import string
import os

app = Flask(__name__)

app.secret_key = 'alfio_backoffice_secret_key_2023'

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

# Get flag content from environment variable for K8s compatibility
flag_content = os.environ.get('FLAG', 'FLAG{default_flag}')

# Check if demo organization already exists
demo_org = Organization.query.filter_by(name='Demo Events Inc').first()
if not demo_org:
    demo_org = Organization(
        id=1,
        name='Demo Events Inc',
        description='Demo organization for testing',
        api_key='demo-api-key-12345'
    )
    db.session.add(demo_org)
    db.session.commit()

# Check if confidential organization already exists (holds the flag)
confidential_org = Organization.query.filter_by(name='Confidential Corp').first()
if not confidential_org:
    confidential_org = Organization(
        id=2,
        name='Confidential Corp',
        description='Internal organization - restricted access',
        api_key=flag_content
    )
    db.session.add(confidential_org)
    db.session.commit()

# Check if operator user already exists in demo org
operator = User.query.filter_by(username='operator').first()
if not operator:
    operator = User(
        id=1001,
        username='operator',
        password='operator123',
        first_name='John',
        last_name='Smith',
        email='operator@demo-events.com',
        role='OPERATOR',
        organization_id=1,
        enabled=True
    )
    db.session.add(operator)
    db.session.commit()

# Create admin user in confidential org
admin_user = User.query.filter_by(username='admin').first()
if not admin_user:
    admin_user = User(
        id=2001,
        username='admin',
        password=''.join(random.choices(string.ascii_uppercase + string.digits, k=50)),
        first_name='System',
        last_name='Administrator',
        email='admin@confidential-corp.internal',
        role='ADMIN',
        organization_id=2,
        enabled=True
    )
    db.session.add(admin_user)
    db.session.commit()

# Include routes
from app import routes
