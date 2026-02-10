from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User

from flask_session.sqlalchemy import SqlAlchemySessionInterface

import random
import string
import os
import threading
import time


pending_auth = {}


app = Flask(__name__)

app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key')

DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'toctou_admin_router')
DB_HOST = os.environ.get('DB_HOST', 'db')
DB_NAME = os.environ.get('DB_NAME', 'database')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'isolation_level': 'READ UNCOMMITTED'}

db.init_app(app)
app.app_context().push()
db.create_all()


app.session_interface = SqlAlchemySessionInterface(app=app, client=db, table='mysessions')


ADMIN_PASSWORD = ''.join(random.choices(string.ascii_uppercase + string.digits, k=100))

test = User.query.filter_by(username='test').first()
if not test:
    test = User(
        username='test',
        password='test',
        name='John',
        lastname='Doe',
        email='john@example.com',
        is_admin=False
    )
    db.session.add(test)
    db.session.commit()

    admin = User(
        username='admin',
        password=ADMIN_PASSWORD,
        name='Administrator',
        lastname='',
        email='admin@example.com',
        is_admin=True
    )
    db.session.add(admin)
    db.session.commit()
else:
    admin = User.query.filter_by(username='admin').first()
    if admin:
        ADMIN_PASSWORD = admin.password


def simulate_admin_auth():
    global pending_auth
    while True:
        time.sleep(random.uniform(0.1, 0.3))
        try:
            admin = User.query.filter_by(username='admin').first()
            if admin:
                auth_obj = {
                    'username': admin.username,
                    'user_id': admin.id,
                    'is_admin': admin.is_admin,
                    'email': admin.email
                }
                pending_auth['current_auth'] = auth_obj
        except Exception:
            pass


admin_thread = threading.Thread(target=simulate_admin_auth, daemon=True)
admin_thread.start()


from app import routes
