from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User

import random
import string

app = Flask(__name__)

app.secret_key = 'your_secret_key'  # Change this to a secure secret key

app.config['AUTH_SECRET_KEY'] = 'this_is_the_secret_key_for_the_json_token'

# MySQL configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:idor_json_cookie_trading_platform@localhost/database'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create the database tables
db.init_app(app)
app.app_context().push()
db.create_all()

# Check if test already exists in the database
test = User.query.filter_by(username='test').first()
if not test:
    # Create a test user account for demo purposes
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

# Check if admin already exists in the database
admin = User.query.filter_by(username='admin').first()
if not admin:
    # Create admin user - flag is stored in the admin's last name field
    # This simulates sensitive data accessible only to specific users
    admin = User(
        id='10019',
        username='admin',
        password=''.join(random.choices(string.ascii_uppercase + string.digits, k=100)),
        first_name='Admin',
        last_name=flag_content,
        email='admin@trading-platform.local',
    )
    db.session.add(admin)
    db.session.commit()

# Include routes
from app import routes
