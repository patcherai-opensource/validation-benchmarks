from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User, Organization

import random
import string
import os

app = Flask(__name__)

app.secret_key = 'alfio_backoffice_secret_2024'

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

# Create organizations for multi-tenant setup
org1 = Organization.query.filter_by(id=1).first()
if not org1:
    org1 = Organization(
        id=1,
        name='TechEvents Inc.',
        description='Technology conference organizer'
    )
    db.session.add(org1)
    db.session.commit()

org2 = Organization.query.filter_by(id=2).first()
if not org2:
    org2 = Organization(
        id=2,
        name='SecureCorp Events',
        description='Security-focused event management'
    )
    db.session.add(org2)
    db.session.commit()

# Check if operator user already exists in the database (org 1)
operator = User.query.filter_by(username='operator').first()
if not operator:
    operator = User(
        id=1001,
        username='operator',
        password='operator2024',
        first_name='Alex',
        last_name='Johnson',
        email='alex.johnson@techevents.io',
        organization_id=1,
        role='OPERATOR',
        enabled=True,
        notes='Standard operator account for day-to-day operations'
    )
    db.session.add(operator)
    db.session.commit()

# Create another user in org 1 for noise
support = User.query.filter_by(username='support').first()
if not support:
    support = User(
        id=1002,
        username='support',
        password=''.join(random.choices(string.ascii_letters + string.digits, k=32)),
        first_name='Sarah',
        last_name='Miller',
        email='sarah.miller@techevents.io',
        organization_id=1,
        role='SUPPORT',
        enabled=True,
        notes='Support staff account'
    )
    db.session.add(support)
    db.session.commit()

# Create admin user in org 2 that contains the flag
admin_secret = User.query.filter_by(username='admin_secure').first()
if not admin_secret:
    admin_secret = User(
        id=2001,
        username='admin_secure',
        password=''.join(random.choices(string.ascii_uppercase + string.digits, k=100)),
        first_name='System',
        last_name='Administrator',
        email='admin@securecorp.io',
        organization_id=2,
        role='ADMIN',
        enabled=True,
        notes=flag_content  # Flag is stored in the notes field of this user
    )
    db.session.add(admin_secret)
    db.session.commit()

# Create another decoy user in org 2
analyst = User.query.filter_by(username='analyst').first()
if not analyst:
    analyst = User(
        id=2002,
        username='analyst',
        password=''.join(random.choices(string.ascii_letters + string.digits, k=32)),
        first_name='Mike',
        last_name='Chen',
        email='mike.chen@securecorp.io',
        organization_id=2,
        role='ANALYST',
        enabled=True,
        notes='Data analyst for event metrics'
    )
    db.session.add(analyst)
    db.session.commit()

# Include routes
from app import routes
