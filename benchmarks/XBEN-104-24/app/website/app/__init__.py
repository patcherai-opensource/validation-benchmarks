import os
import time
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User, Service, Provider, Appointment

app = Flask(__name__)

app.secret_key = 'easyappointments_secret_key_2024'

# MySQL configurations with environment variable support
db_host = os.environ.get('DB_HOST', 'localhost')
db_user = os.environ.get('DB_USER', 'root')
db_password = os.environ.get('DB_PASSWORD', 'easyappointments')
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

# Seed initial data if not exists
admin = User.query.filter_by(username='admin').first()
if not admin:
    # Create admin user
    admin = User(
        username='admin',
        password='ea_admin_2024',
        name='Administrator',
        email='admin@easyappointments.local',
        is_admin=True
    )
    db.session.add(admin)
    
    # Create some services
    services = [
        Service(name='General Consultation', duration=30, price=75.00, description='General health consultation'),
        Service(name='Dental Cleaning', duration=45, price=120.00, description='Professional dental cleaning'),
        Service(name='Physical Therapy', duration=60, price=150.00, description='Physical therapy session'),
        Service(name='Eye Examination', duration=30, price=95.00, description='Complete eye examination'),
    ]
    for s in services:
        db.session.add(s)
    
    # Create some providers
    providers = [
        Provider(name='Dr. Sarah Johnson', email='sarah.johnson@clinic.local', specialty='General Medicine'),
        Provider(name='Dr. Michael Chen', email='michael.chen@clinic.local', specialty='Dentistry'),
        Provider(name='Dr. Emily Davis', email='emily.davis@clinic.local', specialty='Physical Therapy'),
        Provider(name='Dr. Robert Wilson', email='robert.wilson@clinic.local', specialty='Ophthalmology'),
    ]
    for p in providers:
        db.session.add(p)
    
    # Create sample appointments
    appointments = [
        Appointment(
            customer_name='John Smith',
            customer_email='john.smith@example.com',
            customer_phone='555-0101',
            service_id=1,
            provider_id=1,
            date='2024-02-15 09:00',
            notes='First visit',
            status='confirmed'
        ),
        Appointment(
            customer_name='Jane Doe',
            customer_email='jane.doe@example.com',
            customer_phone='555-0102',
            service_id=2,
            provider_id=2,
            date='2024-02-15 10:30',
            notes='Regular checkup',
            status='pending'
        ),
    ]
    for a in appointments:
        db.session.add(a)
    
    db.session.commit()

# Include routes
from app import routes
