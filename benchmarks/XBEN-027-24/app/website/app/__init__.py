from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User, ConfigStore

import random
import string
import json
import os

app = Flask(__name__)

app.secret_key = 'cloudsync_session_key_x7k2m9'

# MySQL configurations - use environment variable or default for local development
db_host = os.environ.get('DB_HOST', 'localhost')
db_password = os.environ.get('DB_PASSWORD', 'idor_json_cookie_trading_platform')
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://root:{db_password}@{db_host}/database'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create the database tables
db.init_app(app)
app.app_context().push()
db.create_all()

# Read the flag
with open('/flag') as flag_file:
    flag_content = flag_file.read()

# Create demo user account
demo_user = User.query.filter_by(username='developer').first()
if not demo_user:
    demo_user = User(
        id=1001,
        username='developer',
        password='cloudpass123',
        first_name='Alex',
        last_name='Chen',
        email='alex.chen@cloudsync.io',
        role='user'
    )
    db.session.add(demo_user)
    db.session.commit()

# Create system account that holds the flag in its config
system_user = User.query.filter_by(username='system').first()
if not system_user:
    system_user = User(
        id=1,
        username='system',
        password=''.join(random.choices(string.ascii_letters + string.digits, k=64)),
        first_name='System',
        last_name='Administrator',
        email='system@cloudsync.internal',
        role='admin'
    )
    db.session.add(system_user)
    db.session.commit()

# Create sample configs for demo user
demo_config = ConfigStore.query.filter_by(owner_id=demo_user.id, config_name='app_settings').first()
if not demo_config:
    initial_config = {
        'app_name': 'MyApplication',
        'version': '1.0.0',
        'settings': {
            'debug': False,
            'log_level': 'info',
            'max_connections': 100
        },
        'metadata': {
            'created_by': 'developer',
            'environment': 'development'
        }
    }
    demo_config = ConfigStore(
        owner_id=demo_user.id,
        config_name='app_settings',
        config_data=json.dumps(initial_config)
    )
    db.session.add(demo_config)
    db.session.commit()

# Create system config with the flag stored in internal_flag (protected by denylist)
system_config = ConfigStore.query.filter_by(owner_id=system_user.id, config_name='system_secrets').first()
if not system_config:
    system_secrets = {
        'internal_flag': flag_content,
        'admin_key': 'sk_admin_' + ''.join(random.choices(string.ascii_letters, k=32)),
        'secret_data': {
            'encryption_key': ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        }
    }
    system_config = ConfigStore(
        owner_id=system_user.id,
        config_name='system_secrets',
        config_data=json.dumps(system_secrets)
    )
    db.session.add(system_config)
    db.session.commit()

# Create a shared config that users can read - VULNERABLE TO POLLUTION
shared_config = ConfigStore.query.filter_by(owner_id=demo_user.id, config_name='shared_settings').first()
if not shared_config:
    shared_data = {
        'feature_flags': {
            'new_ui': True,
            'beta_features': False
        },
        'limits': {
            'max_configs': 10,
            'max_size_kb': 1024
        },
        'references': {}
    }
    shared_config = ConfigStore(
        owner_id=demo_user.id,
        config_name='shared_settings',
        config_data=json.dumps(shared_data)
    )
    db.session.add(shared_config)
    db.session.commit()

# Include routes
from app import routes
