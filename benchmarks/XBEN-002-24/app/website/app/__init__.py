from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User, Organization
import os

import random
import string

app = Flask(__name__)

app.secret_key = 'backoffice_secret_key_2024'  # Secret key for session management

# MySQL configurations - use environment variables for K8s compatibility
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'idor_indirect_trading_platform')
DB_NAME = os.getenv('DB_NAME', 'database')
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'isolation_level': 'READ UNCOMMITTED'}


# Create the database tables
db.init_app(app)
app.app_context().push()
db.create_all()

# Check if data already exists in the database
existing_org = Organization.query.filter_by(name='Acme Events').first()
if not existing_org:
    # Create organizations (multi-tenant setup like alf.io)
    org_acme = Organization(
        id=1,
        name='Acme Events',
        description='Acme Corporation Event Management'
    )
    db.session.add(org_acme)
    
    org_globex = Organization(
        id=2,
        name='Globex Corp',
        description='Globex Corporation - Premium Events'
    )
    db.session.add(org_globex)
    
    org_internal = Organization(
        id=3,
        name='Internal Admin',
        description='Internal administration and system accounts'
    )
    db.session.add(org_internal)
    db.session.commit()
    
    # Create users for Acme Events (Organization 1)
    # This is the low-privilege attacker account
    operator_user = User(
        id=10032,
        username='operator',
        password='operator123',
        first_name='John',
        last_name='Doe',
        email='john.doe@acme-events.com',
        role='OPERATOR',
        enabled=True,
        organization=org_acme,
        secret_notes='Standard operator account for Acme Events.'
    )
    db.session.add(operator_user)
    
    admin_acme = User(
        id=10033,
        username='admin_acme',
        password='secure_admin_pass',
        first_name='Alice',
        last_name='Admin',
        email='alice@acme-events.com',
        role='ADMIN',
        enabled=True,
        organization=org_acme,
        secret_notes='Organization admin for Acme Events. Has elevated privileges within org.'
    )
    db.session.add(admin_acme)
    
    # Create users for Globex Corp (Organization 2) - different tenant
    admin_globex = User(
        id=20001,
        username='admin_globex',
        password='globex_secure_2024',
        first_name='Bob',
        last_name='Manager',
        email='bob@globex-corp.com',
        role='ADMIN',
        enabled=True,
        organization=org_globex,
        secret_notes='Globex Corp administrator. Manages all premium events. API Key: GLOBEX_KEY_7391'
    )
    db.session.add(admin_globex)
    
    api_user_globex = User(
        id=20002,
        username='api_globex',
        password='api_key_globex_2024',
        first_name='API',
        last_name='Service',
        email='api@globex-corp.com',
        role='API_KEY',
        enabled=True,
        organization=org_globex,
        secret_notes='Service account for Globex integrations.'
    )
    db.session.add(api_user_globex)
    
    # Create users for Internal Admin (Organization 3) - system/internal accounts
    # Read flag from environment variable for K8s compatibility
    flag_content = os.getenv('FLAG', 'FLAG{default_flag_for_testing}')
    
    # This is the target user whose secret_notes contains the flag
    # Only accessible via IDOR vulnerability - user belongs to different organization
    system_admin = User(
        id=99999,
        username='system_admin',
        password='system_super_secret_2024',
        first_name='System',
        last_name='Administrator',
        email='sysadmin@internal.local',
        role='ADMIN',
        enabled=True,
        organization=org_internal,
        secret_notes=f'SYSTEM ADMIN CREDENTIALS - DO NOT SHARE: {flag_content}'
    )
    db.session.add(system_admin)
    
    disabled_user = User(
        id=99998,
        username='former_admin',
        password='disabled_account',
        first_name='Former',
        last_name='Employee',
        email='former@internal.local',
        role='ADMIN',
        enabled=False,
        organization=org_internal,
        secret_notes='Account disabled due to security review.'
    )
    db.session.add(disabled_user)
    
    db.session.commit()

# Include routes
from app import routes
