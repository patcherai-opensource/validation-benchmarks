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

# Initialize multi-tenant organizations (similar to alf.io's multi-org setup)
# Organization 1: Demo Events Ltd (attacker's organization)
org1 = Organization.query.filter_by(name='Demo Events Ltd').first()
if not org1:
    org1 = Organization(
        id=1,
        name='Demo Events Ltd',
        description='Demo organization for testing'
    )
    db.session.add(org1)
    db.session.commit()

# Organization 2: SecureCorp (target organization with sensitive data)
org2 = Organization.query.filter_by(name='SecureCorp').first()
if not org2:
    org2 = Organization(
        id=2,
        name='SecureCorp',
        description='Premium enterprise customer'
    )
    db.session.add(org2)
    db.session.commit()

# Create test user in Organization 1 (Demo Events Ltd) - low privilege operator
test = User.query.filter_by(username='operator').first()
if not test:
    test = User(
        id=100,
        username='operator',
        password='operator123',
        first_name='John',
        last_name='Smith',
        email='john.smith@demo-events.com',
        role='operator',
        enabled=True,
        organization_id=1,
        notes='Regular operator account'
    )
    db.session.add(test)
    db.session.commit()

# Create admin user in Organization 2 (SecureCorp) - contains flag in notes
admin_user = User.query.filter_by(username='admin').first()
if not admin_user:
    admin_user = User(
        id=200,
        username='admin',
        password=''.join(random.choices(string.ascii_uppercase + string.digits, k=50)),
        first_name='Sarah',
        last_name='Connor',
        email='admin@securecorp.com',
        role='owner',
        enabled=True,
        organization_id=2,
        notes=f'ADMIN SECRETS - API Key Recovery Code: {flag_content}'
    )
    db.session.add(admin_user)
    db.session.commit()

# Create additional users for realism
users_data = [
    (101, 'alice', 'alice2024', 'Alice', 'Johnson', 'alice@demo-events.com', 'operator', 1, 'Handles customer support'),
    (102, 'bob', 'bobsecure', 'Bob', 'Williams', 'bob@demo-events.com', 'admin', 1, 'IT administrator'),
    (201, 'mike', 'mike_pass', 'Mike', 'Thompson', 'mike@securecorp.com', 'operator', 2, 'Operations team'),
]

for uid, uname, pwd, fname, lname, email, role, org_id, notes in users_data:
    if not User.query.filter_by(username=uname).first():
        user = User(
            id=uid,
            username=uname,
            password=pwd,
            first_name=fname,
            last_name=lname,
            email=email,
            role=role,
            enabled=True,
            organization_id=org_id,
            notes=notes
        )
        db.session.add(user)

db.session.commit()

# Include routes
from app import routes
