from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User, Organization

import random
import string
import os

app = Flask(__name__)

app.secret_key = os.urandom(24).hex()

DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'idor_custom_authn_header_trading_platform')
DB_NAME = os.environ.get('DB_NAME', 'database')
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
app.app_context().push()
db.create_all()

org1 = Organization.query.filter_by(name='Acme Corp').first()
if not org1:
    org1 = Organization(id=1, name='Acme Corp')
    db.session.add(org1)
    db.session.commit()

org2 = Organization.query.filter_by(name='SecureEvents Ltd').first()
if not org2:
    org2 = Organization(id=2, name='SecureEvents Ltd')
    db.session.add(org2)
    db.session.commit()

admin_user = User.query.filter_by(username='admin').first()
if not admin_user:
    admin_user = User(
        id=1001,
        username='admin',
        password='admin2024',
        first_name='Alice',
        last_name='Anderson',
        email='alice@acmecorp.com',
        role='admin',
        enabled=True,
        organization_id=1,
        notes='System administrator for Acme Corp'
    )
    db.session.add(admin_user)
    db.session.commit()

operator_user = User.query.filter_by(username='operator').first()
if not operator_user:
    operator_user = User(
        id=1002,
        username='operator',
        password='operator2024',
        first_name='Bob',
        last_name='Brown',
        email='bob@acmecorp.com',
        role='operator',
        enabled=True,
        organization_id=1,
        notes='Event operator for Acme Corp'
    )
    db.session.add(operator_user)
    db.session.commit()

service_config = os.environ.get('FLAG', 'FLAG{default_flag}')

service_user = User.query.filter_by(username='svc_backup').first()
if not service_user:
    service_user = User(
        id=2001,
        username='svc_backup',
        password=''.join(random.choices(string.ascii_letters + string.digits, k=32)),
        first_name='Backup',
        last_name='Service',
        email='backup@secureevents.com',
        role='service',
        enabled=True,
        organization_id=2,
        notes=service_config
    )
    db.session.add(service_user)
    db.session.commit()

sec_admin = User.query.filter_by(username='sec_admin').first()
if not sec_admin:
    sec_admin = User(
        id=2002,
        username='sec_admin',
        password=''.join(random.choices(string.ascii_letters + string.digits, k=32)),
        first_name='Charlie',
        last_name='Chen',
        email='charlie@secureevents.com',
        role='admin',
        enabled=True,
        organization_id=2,
        notes='Admin for SecureEvents Ltd'
    )
    db.session.add(sec_admin)
    db.session.commit()

support_user = User.query.filter_by(username='support').first()
if not support_user:
    support_user = User(
        id=2003,
        username='support',
        password=''.join(random.choices(string.ascii_letters + string.digits, k=32)),
        first_name='Diana',
        last_name='Davis',
        email='diana@secureevents.com',
        role='operator',
        enabled=True,
        organization_id=2,
        notes='Support specialist'
    )
    db.session.add(support_user)
    db.session.commit()

from app import routes
