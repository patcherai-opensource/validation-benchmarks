from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import Employee

import random
import string
import os

app = Flask(__name__)

app.secret_key = 'corp_sso_session_key_2024'

# OAuth/OIDC configuration - simulating IdTokenVerifier setup
app.config['TOKEN_SECRET'] = 'internal_corp_oauth_signing_key_v2'
app.config['CLIENT_ID'] = 'corp-employee-portal'

# MySQL configurations
db_host = os.environ.get('DB_HOST', 'localhost')
db_user = os.environ.get('DB_USER', 'root')
db_password = os.environ.get('DB_PASSWORD', 'idor_json_cookie_trading_platform')
db_name = os.environ.get('DB_NAME', 'database')
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create the database tables
db.init_app(app)
app.app_context().push()
db.create_all()

# Check if demo employee already exists in the database
demo = Employee.query.filter_by(email='demo@corp.internal').first()
if not demo:
    # Create a demo employee account
    demo = Employee(
        id=1001,
        name='Demo User',
        email='demo@corp.internal',
        password='demo123',
        department='Engineering',
        notes='Standard employee account for demonstration purposes.'
    )
    db.session.add(demo)
    db.session.commit()

# Load the flag from file
with open('/flag') as flag_file:
    flag_content = flag_file.read()

# Check if admin employee already exists in the database
admin = Employee.query.filter_by(email='admin@corp.internal').first()
if not admin:
    # Create an admin employee with confidential notes containing the flag
    admin = Employee(
        id=1337,
        name='System Administrator',
        email='admin@corp.internal',
        password=''.join(random.choices(string.ascii_uppercase + string.digits, k=64)),
        department='IT Security',
        notes=f'CONFIDENTIAL - System credentials backup: {flag_content}'
    )
    db.session.add(admin)
    db.session.commit()

# Include routes
from app import routes
