from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

db = SQLAlchemy()


class Patient(db.Model, UserMixin):
    __tablename__ = 'patients'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(64), nullable=False, default='')
    last_name = db.Column(db.String(64), nullable=False, default='')
    date_of_birth = db.Column(db.Date, nullable=True)
    email = db.Column(db.String(128), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    role = db.Column(db.String(16), nullable=False, default='patient')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Provider(db.Model):
    __tablename__ = 'providers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    specialty = db.Column(db.String(128), nullable=True)
    facility_id = db.Column(db.Integer, db.ForeignKey('facilities.id'), nullable=True)


class Facility(db.Model):
    __tablename__ = 'facilities'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    address = db.Column(db.String(256), nullable=True)
    phone = db.Column(db.String(20), nullable=True)


class CalendarEvent(db.Model):
    __tablename__ = 'calendar_events'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    provider_id = db.Column(db.Integer, db.ForeignKey('providers.id'), nullable=True)
    facility_id = db.Column(db.Integer, db.ForeignKey('facilities.id'), nullable=True)
    event_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.String(8), nullable=False, default='09:00')
    end_time = db.Column(db.String(8), nullable=False, default='09:30')
    duration = db.Column(db.Integer, nullable=False, default=30)
    title = db.Column(db.String(128), nullable=False, default='Office Visit')
    category = db.Column(db.String(64), nullable=False, default='Office Visit')
    status = db.Column(db.String(16), nullable=False, default='confirmed')
    comments = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    patient = db.relationship('Patient', backref=db.backref('appointments', lazy=True))
    provider = db.relationship('Provider', backref=db.backref('events', lazy=True))
    facility = db.relationship('Facility', backref=db.backref('events', lazy=True))


class Medication(db.Model):
    __tablename__ = 'medications'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    drug_name = db.Column(db.String(128), nullable=False)
    dosage = db.Column(db.String(64), nullable=True)
    begin_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    patient = db.relationship('Patient', backref=db.backref('medications', lazy=True))


class LabResult(db.Model):
    __tablename__ = 'lab_results'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    test_name = db.Column(db.String(128), nullable=False)
    result_value = db.Column(db.String(64), nullable=True)
    reference_range = db.Column(db.String(64), nullable=True)
    date_collected = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(32), nullable=False, default='final')
    patient = db.relationship('Patient', backref=db.backref('lab_results', lazy=True))
