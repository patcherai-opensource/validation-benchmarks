from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import time
import sys
from app.db import db
from app.models import User

app = Flask(__name__)

app.secret_key = 'pynotebook_secret_key_2024'

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

# Check if demo user already exists in the database with retry logic
for retry in range(5):
    try:
        demo_user = User.query.filter_by(username='demo').first()
        if not demo_user:
            # Create a demo user
            demo_user = User(
                username='demo',
                password='demo123',
                name='Demo',
                lastname='User',
                email='demo@pynotebook.local'
            )
            db.session.add(demo_user)
            db.session.commit()
        break
    except Exception as e:
        print(f"Database operation retry {retry + 1}/5 failed: {e}")
        if retry == 4:
            raise e
        time.sleep(1)

# Include routes
from app import routes
