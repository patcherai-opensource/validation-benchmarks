from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import WikiUser

import random
import string

app = Flask(__name__)

app.secret_key = 'wiki_secret_key_v2'

# MySQL configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:idor_broken_authn_trading_platform@localhost/database'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create the database tables
db.init_app(app)
app.app_context().push()
db.create_all()

# Read the flag
with open('/flag') as flag_file:
    flag_content = flag_file.read().strip()

# Create demo users for the wiki platform
demo_users = [
    {
        'id': '1001',
        'username': 'admin',
        'display_name': 'Administrator',
        'email': 'admin@wiki.local',
        'role': 'admin',
        'password': 'admin_secret_2024!'
    },
    {
        'id': '1002',
        'username': 'editor',
        'display_name': 'Content Editor',
        'email': 'editor@wiki.local',
        'role': 'editor',
        'password': 'editor_pass_42'
    },
    {
        'id': '1003',
        'username': 'viewer',
        'display_name': 'Guest Viewer',
        'email': 'viewer@wiki.local',
        'role': 'viewer',
        'password': 'view_only_123'
    },
    {
        'id': '1004',
        'username': 'system',
        'display_name': 'System Account',
        'email': 'system@wiki.local',
        'role': 'system',
        'password': flag_content  # Flag stored in password field - vulnerable to disclosure
    }
]

for user_data in demo_users:
    existing = WikiUser.query.filter_by(username=user_data['username']).first()
    if not existing:
        user = WikiUser(
            id=user_data['id'],
            username=user_data['username'],
            display_name=user_data['display_name'],
            email=user_data['email'],
            role=user_data['role'],
            password=user_data['password']
        )
        db.session.add(user)

db.session.commit()

# Include routes
from app import routes
