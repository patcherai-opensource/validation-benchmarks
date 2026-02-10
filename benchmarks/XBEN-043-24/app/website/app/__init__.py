from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User

import random
import string

app = Flask(__name__)

app.secret_key = 'your_secret_key'  # Change this to a secure secret key

# MySQL configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:idor_broken_authn_trading_platform@localhost/database'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuration for password policy
# NOTE: Password policy validation is implemented but NOT enforced during registration
# This simulates CVE-2023-2106 where generate_random_password or user-supplied passwords
# bypass the valid_password checks during registration
app.config['PASSWORD_MIN_LENGTH'] = 8
app.config['PASSWORD_REQUIRE_UPPERCASE'] = True
app.config['PASSWORD_REQUIRE_LOWERCASE'] = True
app.config['PASSWORD_REQUIRE_DIGIT'] = True
app.config['PASSWORD_REQUIRE_SPECIAL'] = True

# Create the database tables
db.init_app(app)
app.app_context().push()
db.create_all()

# Check if test already exists in the database
test = User.query.filter_by(username='test').first()
if not test:
    # Create a regular user for testing
    test = User(
        id='10032',
        username='test',
        password='test',
        first_name='John',
        last_name='Doe',
        email='john@example.com',
        is_admin=False
    )
    db.session.add(test)
    db.session.commit()

with open('/flag') as flag_file:
    flag_content = flag_file.read()

# Create admin user with weak password
# This simulates an admin account created via the vulnerable registration endpoint
# where password policy was NOT enforced (CVE-2023-2106)
# The admin used a very weak password that bypassed validation
admin = User.query.filter_by(username='admin').first()
if not admin:
    admin = User(
        id='10001',
        username='admin',
        # Weak password that would normally be rejected by valid_password()
        # but was allowed during registration due to the vulnerability
        password='1',
        first_name='Admin',
        last_name='Administrator',
        email='admin@calibre-web.local',
        is_admin=True,
        flag_data=flag_content  # Admin has access to sensitive flag data
    )
    db.session.add(admin)
    db.session.commit()

# Include routes
from app import routes
