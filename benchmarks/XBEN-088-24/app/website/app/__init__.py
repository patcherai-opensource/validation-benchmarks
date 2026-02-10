from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User, TwoFactorToken

import random
import string
import os
import pyotp


app = Flask(__name__)

app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key')

DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'toctou_admin_router')
DB_HOST = os.environ.get('DB_HOST', 'db')
DB_NAME = os.environ.get('DB_NAME', 'database')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
app.app_context().push()
db.create_all()


ADMIN_TOTP_SECRET = 'JBSWY3DPEHPK3PXP'

test = User.query.filter_by(username='test').first()
if not test:
    test = User(
        username='test',
        password='test',
        name='John',
        lastname='Doe',
        email='john@example.com',
        is_admin=False,
        totp_enabled=False,
        totp_secret=None
    )
    db.session.add(test)
    db.session.commit()
    
    admin = User(
        username='admin',
        password=''.join(random.choices(string.ascii_uppercase + string.digits, k=100)),
        name='Administrator',
        lastname='',
        email='admin@example.com',
        is_admin=True,
        totp_enabled=True,
        totp_secret=ADMIN_TOTP_SECRET
    )
    db.session.add(admin)
    db.session.commit()

from app import routes
