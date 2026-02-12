import os
import time
import hashlib
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User, Realm, OAuth2Provider, AuditLog

app = Flask(__name__)

app.secret_key = os.environ.get('AM_SESSION_KEY', 'ChangeMe-f7e2a9b1c4d8')

# MySQL configurations with environment variable support
db_host = os.environ.get('DB_HOST', 'localhost')
db_user = os.environ.get('DB_USER', 'root')
db_password = os.environ.get('DB_PASSWORD', 'openam')
db_name = os.environ.get('DB_NAME', 'database')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = False

# Create the database tables with retry logic
db.init_app(app)
app.app_context().push()

# Retry database connection and table creation
max_retries = 30
for attempt in range(max_retries):
    try:
        db.create_all()
        break
    except Exception as e:
        if attempt < max_retries - 1:
            print(f"Database connection attempt {attempt + 1} failed: {e}")
            time.sleep(2)
        else:
            print(f"Failed to connect to database after {max_retries} attempts")
            raise


def _hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# Initialize default data
admin = User.query.filter_by(username='amadmin').first()
if not admin:
    admin = User(
        username='amadmin',
        password=_hash_password('admin123'),
        display_name='AM Administrator',
        email='admin@openam.example.com',
        role='admin',
        status='active'
    )
    db.session.add(admin)

    # Regular user for testing OAuth2 flows
    demo_user = User(
        username='demo',
        password=_hash_password('demo'),
        display_name='Demo User',
        email='demo@example.com',
        role='user',
        status='active'
    )
    db.session.add(demo_user)

    # Default realm
    top_realm = Realm(
        name='/',
        description='Top Level Realm',
        active=True
    )
    db.session.add(top_realm)
    db.session.flush()

    employees_realm = Realm(
        name='/employees',
        description='Employees Realm',
        active=True
    )
    db.session.add(employees_realm)
    db.session.flush()

    # Default OAuth2 provider in top-level realm
    provider = OAuth2Provider(
        realm_id=top_realm.id,
        client_id='myOAuth2Client',
        client_secret='clientSecret123',
        redirect_uri='https://app.example.com/callback',
        scope='openid profile email',
        response_type='code',
        token_endpoint_auth_method='client_secret_basic',
        grant_types='authorization_code,refresh_token',
        custom_login_url_template=None,
        issuer='https://openam.example.com/oauth2',
        active=True
    )
    db.session.add(provider)

    # Provider in employees realm
    emp_provider = OAuth2Provider(
        realm_id=employees_realm.id,
        client_id='employeePortal',
        client_secret='empSecret456',
        redirect_uri='https://portal.example.com/auth/callback',
        scope='openid profile',
        response_type='code',
        token_endpoint_auth_method='client_secret_post',
        grant_types='authorization_code',
        custom_login_url_template=None,
        issuer='https://openam.example.com/oauth2/employees',
        active=True
    )
    db.session.add(emp_provider)

    db.session.commit()

# Include routes
from app import routes
