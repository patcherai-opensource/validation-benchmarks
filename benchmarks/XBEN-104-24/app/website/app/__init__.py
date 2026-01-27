import os
import time
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from app.db import db
from app.models import Provider, Service, Appointment

app = Flask(__name__)

app.secret_key = 'easyappointments_secret_2023'

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

# Check if admin provider already exists
admin = Provider.query.filter_by(username='admin').first()
if not admin:
    admin = Provider(
        username='admin',
        password='admin',
        name='Administrator',
        email='admin@clinic.local',
        specialty='Administration',
        is_admin=True
    )
    db.session.add(admin)

# Create sample provider
provider = Provider.query.filter_by(username='drsmith').first()
if not provider:
    provider = Provider(
        username='drsmith',
        password='doctor123',
        name='Dr. Sarah Smith',
        email='sarah.smith@clinic.local',
        specialty='General Medicine',
        is_admin=False
    )
    db.session.add(provider)

# Create sample services
if not Service.query.first():
    services = [
        Service(name='General Consultation', description='Standard medical consultation', duration_minutes=30, price=75.00),
        Service(name='Health Checkup', description='Complete health screening', duration_minutes=60, price=150.00),
        Service(name='Vaccination', description='Standard vaccination service', duration_minutes=15, price=35.00),
    ]
    for s in services:
        db.session.add(s)

db.session.commit()

# Include routes
from app import routes
