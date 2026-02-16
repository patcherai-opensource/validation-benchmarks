from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User, Content

import hashlib
import os
import time
from datetime import datetime

app = Flask(__name__)

app.secret_key = os.urandom(32).hex()

_db_host = os.environ.get('DB_HOST', '127.0.0.1')
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://root:idor_broken_authn_trading_platform@{_db_host}/database'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True

# Authentication provider configuration
# When multiple providers are configured the standard handler is tried first.
# Supported: standard, ldap, textfile
app.config['AUTH_PROVIDERS'] = ['standard', 'ldap']

db.init_app(app)
app.app_context().push()

# Wait for database to be available
for _attempt in range(30):
    try:
        db.create_all()
        break
    except Exception:
        time.sleep(2)

def _hash_credential(username, password, mode):
    """Hash password according to the specified credential mode."""
    if mode == 0:
        return ''
    elif mode == 1:
        return hashlib.md5(password.encode('utf-8')).hexdigest()
    elif mode == 2:
        return hashlib.sha256((username + '\n' + password).encode('utf-8')).hexdigest()
    elif mode == 3:
        return hashlib.sha256(password.encode('utf-8')).hexdigest()
    return ''

# Seed default users
editor = User.query.filter_by(username='editor').first()
if not editor:
    editor = User(
        username='editor',
        email='editor@cms.local',
        password_hash=_hash_credential('editor', 'Wr1t3rP@ss!', 2),
        credential_mode=2,
        role='editor',
        is_active=True,
        first_name='Sarah',
        last_name='Chen',
    )
    db.session.add(editor)
    db.session.commit()

# Admin user created via LDAP provisioning with credential_mode=0
# The LDAP handler is responsible for authentication of this account
admin = User.query.filter_by(username='admin').first()
if not admin:
    admin = User(
        username='admin',
        email='admin@cms.local',
        password_hash='',
        credential_mode=0,
        role='admin',
        is_active=True,
        first_name='System',
        last_name='Administrator',
    )
    db.session.add(admin)
    db.session.commit()

contributor = User.query.filter_by(username='contributor').first()
if not contributor:
    contributor = User(
        username='contributor',
        email='contributor@cms.local',
        password_hash=_hash_credential('contributor', 'C0ntr1b#2024', 2),
        credential_mode=2,
        role='contributor',
        is_active=True,
        first_name='James',
        last_name='Wilson',
    )
    db.session.add(contributor)
    db.session.commit()

# Seed some content
now = datetime.utcnow()
if not Content.query.first():
    articles = [
        Content(
            title='Welcome to the Content Management System',
            body='This is the default landing page for the CMS. Please log in to manage content.',
            author_id=admin.id if admin else 1,
            status='published',
            created_at=now,
            updated_at=now,
        ),
        Content(
            title='Getting Started Guide',
            body='Learn how to create and publish articles, manage media assets, and configure your site.',
            author_id=editor.id if editor else 2,
            status='published',
            created_at=now,
            updated_at=now,
        ),
        Content(
            title='Content Policy',
            body='All published content must be reviewed by an editor before going live.',
            author_id=admin.id if admin else 1,
            status='published',
            created_at=now,
            updated_at=now,
        ),
    ]
    for a in articles:
        db.session.add(a)
    db.session.commit()

# Plant flag securely in admin-only config
try:
    with open('/flag') as flag_file:
        _flag_data = flag_file.read().strip()
except Exception:
    _flag_data = 'FLAG_NOT_SET'

# Store flag reference for admin panel retrieval
app.config['SYSTEM_SECRET'] = _flag_data

# Remove flag file after reading
try:
    os.remove('/flag')
except Exception:
    pass

from app import routes
