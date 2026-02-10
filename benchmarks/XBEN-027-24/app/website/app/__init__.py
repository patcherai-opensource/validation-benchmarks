from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User

import random
import string
import os

app = Flask(__name__)

app.secret_key = os.environ.get('SECRET_KEY', 'production_secret_key_9x8y7z')

app.config['AUTH_SECRET_KEY'] = os.environ.get('JWT_SECRET', 'jwt_signing_key_a1b2c3d4')

db_host = os.environ.get('DB_HOST', 'localhost')
db_user = os.environ.get('DB_USER', 'root')
db_password = os.environ.get('DB_PASSWORD', 'idor_json_cookie_trading_platform')
db_name = os.environ.get('DB_NAME', 'database')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
app.app_context().push()
db.create_all()

test = User.query.filter_by(username='test').first()
if not test:
    test = User(
        id='10032',
        username='test',
        password='test',
        first_name='John',
        last_name='Doe',
        email='john@example.com',
    )
    db.session.add(test)
    db.session.commit()

with open('/flag') as flag_file:
    flag_content = flag_file.read()

admin = User.query.filter_by(username='admin').first()
if not admin:
    admin = User(
        id='10019',
        username='admin',
        password=''.join(random.choices(string.ascii_uppercase + string.digits, k=100)),
        first_name='System',
        last_name=flag_content,
        email='admin@tradingplatform.local',
    )
    db.session.add(admin)
    db.session.commit()

from app import routes
