import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User, ConfigTemplate


app = Flask(__name__)

app.secret_key = os.environ.get('SECRET_KEY', 'configmgr_default_key')

db_host = os.environ.get('DB_HOST', 'localhost')
db_user = os.environ.get('DB_USER', 'root')
db_password = os.environ.get('DB_PASSWORD', 'configmgr_db_pass')
db_name = os.environ.get('DB_NAME', 'configmgr')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
app.app_context().push()
db.create_all()

admin = User.query.filter_by(username='admin').first()
if not admin:
    admin = User(
        username='admin',
        password='configadmin2024',
        name='Admin',
        lastname='User',
        email='admin@configmgr.local'
    )
    db.session.add(admin)
    db.session.commit()

from app import routes
