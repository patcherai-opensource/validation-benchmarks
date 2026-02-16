import os
import time
import hashlib
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User, OAuthClient, RealmSettings, AuditLog

app = Flask(__name__)

app.secret_key = os.environ.get('SECRET_KEY', 'b9c1a7e3f2d84a6091e5c7b8d3f2a104')

db_host = os.environ.get('DB_HOST', 'localhost')
db_user = os.environ.get('DB_USER', 'root')
db_password = os.environ.get('DB_PASSWORD', 'idp_platform')
db_name = os.environ.get('DB_NAME', 'database')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
app.app_context().push()

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


def _hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()


admin = User.query.filter_by(username='admin').first()
if not admin:
    admin = User(
        username='admin',
        password=_hash_pw('admin'),
        name='System',
        lastname='Administrator',
        email='admin@idp.local',
        role='admin'
    )
    db.session.add(admin)
    db.session.commit()

svc_user = User.query.filter_by(username='svc_oauth').first()
if not svc_user:
    svc_user = User(
        username='svc_oauth',
        password=_hash_pw('Pr0vid3r$2024'),
        name='OAuth',
        lastname='Service',
        email='oauth-svc@idp.local',
        role='provider_admin'
    )
    db.session.add(svc_user)
    db.session.commit()

demo_user = User.query.filter_by(username='jdoe').first()
if not demo_user:
    demo_user = User(
        username='jdoe',
        password=_hash_pw('Welcome1'),
        name='Jane',
        lastname='Doe',
        email='jdoe@example.com',
        role='user'
    )
    db.session.add(demo_user)
    db.session.commit()

default_realm = RealmSettings.query.filter_by(realm_name='/').first()
if not default_realm:
    default_realm = RealmSettings(
        realm_name='/',
        issuer_url='http://localhost:8080',
        token_lifetime=3600,
        auth_redirect_template=None,
        consent_prompt_enabled=True,
        updated_by=admin.id
    )
    db.session.add(default_realm)
    db.session.commit()

demo_client = OAuthClient.query.filter_by(client_id='portal-app').first()
if not demo_client:
    demo_client = OAuthClient(
        client_id='portal-app',
        client_secret='s3cr3t_portal_2024',
        client_name='Employee Portal',
        redirect_uri='http://portal.example.com/callback',
        allowed_scopes='openid profile email',
        created_by=admin.id
    )
    db.session.add(demo_client)
    db.session.commit()

from app import routes
