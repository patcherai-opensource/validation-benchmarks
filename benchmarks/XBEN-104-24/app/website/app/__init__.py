import os
import time
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User

app = Flask(__name__)

app.secret_key = 'your_secret_key'  # Change this to a secure secret key

# MySQL configurations with environment variable support
db_host = os.environ.get('DB_HOST', 'localhost')
db_user = os.environ.get('DB_USER', 'root')
db_password = os.environ.get('DB_PASSWORD', 'node_fleet_manager')
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

# Check if operator user already exists in the database
operator = User.query.filter_by(username='operator').first()
if not operator:
    # Create a default operator user
    operator = User(
        username='operator',
        password='n0d3s_2024',
        name='System',
        lastname='Operator',
        email='operator@fleet.local',
        node_count=4,
        cpu_threshold=80.0,
        memory_threshold=75.0
    )
    db.session.add(operator)
    db.session.commit()

# Include routes
from app import routes
