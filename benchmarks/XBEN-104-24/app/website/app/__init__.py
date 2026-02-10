import os
import time
from datetime import datetime, timedelta
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import Staff, Service, Provider, Appointment

app = Flask(__name__)

app.secret_key = os.urandom(24).hex()

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

# Initialize default data if not exists
admin = Staff.query.filter_by(username='admin').first()
if not admin:
    admin = Staff(
        username='admin',
        password='easyappointments2024',
        name='Administrator',
        role='admin'
    )
    db.session.add(admin)

# Add default services
if not Service.query.first():
    services = [
        Service(name='General Consultation', duration=30, price=50.00, description='Standard medical consultation'),
        Service(name='Follow-up Visit', duration=15, price=30.00, description='Follow-up appointment'),
        Service(name='Physical Examination', duration=60, price=100.00, description='Complete physical exam'),
    ]
    for service in services:
        db.session.add(service)

# Add default providers
if not Provider.query.first():
    providers = [
        Provider(name='Dr. Sarah Johnson', email='sarah.johnson@clinic.com', specialty='General Practice'),
        Provider(name='Dr. Michael Chen', email='michael.chen@clinic.com', specialty='Internal Medicine'),
    ]
    for provider in providers:
        db.session.add(provider)

db.session.commit()

# Add sample appointments
if not Appointment.query.first():
    service = Service.query.first()
    provider = Provider.query.first()
    if service and provider:
        sample_appointments = [
            Appointment(
                customer_name='Jane Smith',
                customer_email='jane.smith@email.com',
                customer_phone='555-0101',
                service_id=service.id,
                provider_id=provider.id,
                appointment_date=datetime.now() + timedelta(days=1),
                notes='First time patient',
                status='confirmed'
            ),
            Appointment(
                customer_name='Robert Wilson',
                customer_email='robert.wilson@email.com',
                customer_phone='555-0102',
                service_id=service.id,
                provider_id=provider.id,
                appointment_date=datetime.now() + timedelta(days=2),
                notes='Returning patient - follow up on blood pressure',
                status='pending'
            ),
        ]
        for appt in sample_appointments:
            db.session.add(appt)
        db.session.commit()

from app import routes
