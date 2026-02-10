
from flask_sqlalchemy import SQLAlchemy

from app.db import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    loan_amount = db.Column(db.Float, nullable=False)
    loan_term_months = db.Column(db.Integer, nullable=False)
    monthly_payment = db.Column(db.Float, nullable=False)


class Service(db.Model):
    """Available services for booking"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    duration_minutes = db.Column(db.Integer, default=60)
    price = db.Column(db.Float, nullable=False)


class Provider(db.Model):
    """Service providers/staff"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    specialty = db.Column(db.String(100), nullable=True)


class Appointment(db.Model):
    """Customer appointments - stores user-provided data"""
    id = db.Column(db.Integer, primary_key=True)
    # Customer information (user-provided)
    customer_name = db.Column(db.String(200), nullable=False)
    customer_email = db.Column(db.String(200), nullable=False)
    customer_phone = db.Column(db.String(50), nullable=True)
    customer_address = db.Column(db.String(500), nullable=True)
    # Appointment details
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    provider_id = db.Column(db.Integer, db.ForeignKey('provider.id'), nullable=False)
    appointment_date = db.Column(db.String(20), nullable=False)
    appointment_time = db.Column(db.String(10), nullable=False)
    # Notes field - vulnerable to injection (user-provided, rendered unescaped)
    notes = db.Column(db.Text, nullable=True)
    # Confirmation code
    confirmation_code = db.Column(db.String(20), nullable=False)
    # Status
    status = db.Column(db.String(20), default='confirmed')
    
    service = db.relationship('Service', backref='appointments')
    provider = db.relationship('Provider', backref='appointments')
