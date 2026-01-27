import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User


app = Flask(__name__)

app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key')

# MySQL configurations - use environment variables with fallbacks
db_host = os.environ.get('DB_HOST', 'localhost')
db_user = os.environ.get('DB_USER', 'root')
db_password = os.environ.get('DB_PASSWORD', 'ansible_runner_db')
db_name = os.environ.get('DB_NAME', 'database')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create the database tables
db.init_app(app)
app.app_context().push()
db.create_all()

# Check if admin already exists in the database
admin = User.query.filter_by(username='admin').first()
if not admin:
    # Create a demo admin user for the DevOps platform
    admin = User(
        username='admin',
        password='admin',
        name='DevOps',
        lastname='Admin',
        email='admin@infractl.local',
        default_host='192.168.1.100',
        default_port=22,
        ssh_timeout=30
    )
    db.session.add(admin)
    db.session.commit()

# Include routes
from app import routes
