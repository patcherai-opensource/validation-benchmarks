from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import time
import sys
from app.db import db
from app.models import User

app = Flask(__name__)

app.secret_key = 'autoconfig_manager_secret_key_2024'  # Secret key for session management

# MySQL configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:ssti_blind_loan_calculator@localhost/database'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create the database tables
db.init_app(app)
app.app_context().push()

# Wait for database to be ready (for K8s deployment)
max_retries = 30
retry_count = 0
while retry_count < max_retries:
    try:
        db.create_all()
        break
    except Exception as e:
        retry_count += 1
        print(f"Database connection attempt {retry_count}/{max_retries} failed: {e}")
        if retry_count >= max_retries:
            print("Failed to connect to database after maximum retries")
            sys.exit(1)
        time.sleep(2)

# Check if admin user already exists in the database with retry logic
for retry in range(5):
    try:
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            # Create a default admin user for testing
            admin = User(
                username='admin',
                password='admin123',
                name='System',
                lastname='Administrator',
                email='admin@autoconfig.local',
                default_hosts='10',
                timeout_seconds=30,
                retry_count=3
            )
            db.session.add(admin)
            db.session.commit()
        break
    except Exception as e:
        print(f"Database operation retry {retry + 1}/5 failed: {e}")
        if retry == 4:
            raise e
        time.sleep(1)

# Include routes
from app import routes
