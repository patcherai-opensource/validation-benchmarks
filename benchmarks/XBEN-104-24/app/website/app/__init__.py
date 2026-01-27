import os
import time
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User

app = Flask(__name__)

app.secret_key = 'automation_controller_secret_key'  # Controller secret key

# MySQL configurations with environment variable support
db_host = os.environ.get('DB_HOST', 'localhost')
db_user = os.environ.get('DB_USER', 'root')
db_password = os.environ.get('DB_PASSWORD', 'ssti_loan_calculator')
db_name = os.environ.get('DB_NAME', 'database')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create the database tables with retry logic
db.init_app(app)
app.app_context().push()

# Retry database connection and table creation
max_retries = 30
for attempt in range(max_retries):
    try:
        db.create_all()
        break
    except Exception as e:
        if attempt < max_retries - 1:
            print(f"Database connection attempt {attempt + 1} failed: {e}")
            time.sleep(2)
        else:
            print(f"Failed to connect to database after {max_retries} attempts")
            raise

# Check if admin already exists in the database
admin = User.query.filter_by(username='admin').first()
if not admin:
    # Create default admin user for automation controller
    admin = User(
        username='admin',
        password='admin',
        name='System',
        lastname='Administrator',
        email='admin@controller.local',
        role='administrator',
        last_login='2024-01-15 08:30:00',
        nodes_managed=5
    )
    db.session.add(admin)
    db.session.commit()

# Include routes
from app import routes
