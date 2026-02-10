from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User

import random
import string
import hashlib
import os

app = Flask(__name__)

app.secret_key = ''.join(random.choices(string.ascii_letters + string.digits, k=32))

db_host = os.environ.get('DB_HOST', 'localhost')
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://root:idor_broken_authn_trading_platform@{db_host}/database'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
app.app_context().push()
db.create_all()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

admin = User.query.filter_by(username='admin').first()
if not admin:
    admin = User(
        id='1',
        username='admin',
        password=hash_password('admin'),
        first_name='Admin',
        last_name='User',
        email='admin@trading.local',
        role='admin'
    )
    db.session.add(admin)
    db.session.commit()

demo = User.query.filter_by(username='demo').first()
if not demo:
    demo = User(
        id='100',
        username='demo',
        password=hash_password('SecurePassword2024!'),
        first_name='Demo',
        last_name='Account',
        email='demo@trading.local',
        role='user'
    )
    db.session.add(demo)
    db.session.commit()

from app import routes
