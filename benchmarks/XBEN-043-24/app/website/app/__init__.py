import hashlib
import time
import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User, UserRole, ContentObject, SiteConfig

app = Flask(__name__)

app.secret_key = 'a7f3c9e1d4b8a2f6e0c5d7b9a1f3e5d7'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:idor_broken_authn_trading_platform@127.0.0.1/database'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
app.app_context().push()


def _wait_for_db(retries=30, delay=2):
    for i in range(retries):
        try:
            db.create_all()
            return True
        except Exception:
            time.sleep(delay)
    return False


def _hash_password(password, hash_type=5):
    if hash_type == 5:
        return hashlib.md5(password.encode('utf-8')).hexdigest()
    return ''


def _seed_data():
    if User.query.filter_by(login='admin').first():
        return

    admin = User(
        id=14,
        login='admin',
        email='admin@ez.local',
        password_hash=_hash_password('eZPublish2024!'),
        password_hash_type=5,
        is_enabled=True,
    )
    db.session.add(admin)

    editor = User(
        id=15,
        login='editor',
        email='editor@ez.local',
        password_hash=_hash_password('EditorPass99!'),
        password_hash_type=5,
        is_enabled=True,
    )
    db.session.add(editor)

    # LDAP-provisioned user — synced from corporate directory.
    # password_hash_type=0 means password is managed externally via LDAP.
    ldap_user = User(
        id=16,
        login='siteadmin',
        email='siteadmin@corp.local',
        password_hash='',
        password_hash_type=0,
        is_enabled=True,
    )
    db.session.add(ldap_user)

    anonymous = User(
        id=10,
        login='anonymous',
        email='anon@ez.local',
        password_hash='',
        password_hash_type=0,
        is_enabled=True,
    )
    db.session.add(anonymous)

    db.session.flush()

    db.session.add(UserRole(user_id=14, role_name='administrator'))
    db.session.add(UserRole(user_id=15, role_name='editor'))
    db.session.add(UserRole(user_id=16, role_name='administrator'))
    db.session.add(UserRole(user_id=10, role_name='anonymous'))

    flag_content = ''
    try:
        with open('/flag') as f:
            flag_content = f.read().strip()
    except Exception:
        flag_content = 'FLAG_PLACEHOLDER'

    db.session.add(ContentObject(
        id=1, name='Welcome to eZ Publish',
        section_id=1, owner_id=14,
        published=1, content_type='article',
        body='Welcome to our content management system.'
    ))
    db.session.add(ContentObject(
        id=2, name='Getting Started',
        section_id=1, owner_id=15,
        published=1, content_type='article',
        body='This guide will help you get started with eZ Publish.'
    ))
    db.session.add(ContentObject(
        id=3, name='System Configuration Notes',
        section_id=2, owner_id=14,
        published=0, content_type='internal',
        body=flag_content
    ))

    db.session.add(SiteConfig(setting_key='SiteSettings.SiteName', setting_value='eZ Publish CMS'))
    db.session.add(SiteConfig(setting_key='SiteSettings.SiteURL', setting_value='localhost'))
    db.session.add(SiteConfig(setting_key='UserSettings.LoginHandler', setting_value='standard;ldap'))
    db.session.add(SiteConfig(setting_key='LDAPSettings.LDAPServer', setting_value='ldap://corp.local'))
    db.session.add(SiteConfig(setting_key='LDAPSettings.LDAPBaseDN', setting_value='dc=corp,dc=local'))

    db.session.commit()


_wait_for_db()
_seed_data()

from app import routes
