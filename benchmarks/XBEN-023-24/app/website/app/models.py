from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from app.db import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='admin')


class ServiceInstance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    service_url = db.Column(db.String(500), nullable=False)
    health_url = db.Column(db.String(500), nullable=True)
    management_url = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='UNKNOWN')
    metadata_json = db.Column(db.Text, nullable=True)
    last_checked = db.Column(db.DateTime, nullable=True)


class AlertConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipients = db.Column(db.Text, nullable=False, default='admin@localhost')
    sender = db.Column(db.String(200), nullable=False, default='Service Monitor <noreply@localhost>')
    subject_template = db.Column(db.Text, nullable=False, default='')
    body_template = db.Column(db.Text, nullable=False, default='')
    enabled = db.Column(db.Boolean, nullable=False, default=True)


class AlertLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    instance_id = db.Column(db.Integer, nullable=True)
    instance_name = db.Column(db.String(200), nullable=False)
    previous_status = db.Column(db.String(20), nullable=False)
    current_status = db.Column(db.String(20), nullable=False)
    rendered_subject = db.Column(db.Text, nullable=True)
    rendered_body = db.Column(db.Text, nullable=True)
    recipients = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
