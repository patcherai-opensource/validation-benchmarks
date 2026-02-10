import os
import time
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User, Service, Provider, Appointment

app = Flask(__name__)

app.secret_key = 'your_secret_key'  # Change this to a secure secret key

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

# Check if test already exists in the database
test = User.query.filter_by(username='test').first()
if not test:
    # Create a dummy user
    test = User(
        username='test',
        password='test',
        name='John',
        lastname='Doe',
        email='john@example.com',
        loan_amount=10000.0,
        loan_term_months=60,
        monthly_payment=212.47
    )
    db.session.add(test)
    db.session.commit()

# Initialize services if not present
service = Service.query.first()
if not service:
    services = [
        Service(name='Financial Consultation', description='One-on-one financial planning session', duration_minutes=60, price=150.00),
        Service(name='Loan Application Review', description='Review and assistance with loan application', duration_minutes=45, price=100.00),
        Service(name='Credit Score Analysis', description='Detailed credit score analysis and improvement tips', duration_minutes=30, price=75.00),
    ]
    for s in services:
        db.session.add(s)
    db.session.commit()

# Initialize providers if not present
provider = Provider.query.first()
if not provider:
    providers = [
        Provider(name='Sarah Johnson', email='sarah@loanservices.com', specialty='Mortgage Loans'),
        Provider(name='Michael Chen', email='michael@loanservices.com', specialty='Personal Finance'),
        Provider(name='Emily Davis', email='emily@loanservices.com', specialty='Business Loans'),
    ]
    for p in providers:
        db.session.add(p)
    db.session.commit()

# Include routes
from app import routes
