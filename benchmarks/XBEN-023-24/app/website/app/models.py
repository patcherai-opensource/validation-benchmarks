from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from app.db import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='viewer')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ServiceInstance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='UP')
    group_name = db.Column(db.String(50), nullable=True)
    metadata_info = db.Column(db.Text, nullable=True)
    last_checked = db.Column(db.DateTime, default=datetime.utcnow)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)


class NotificationChannel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    channel_type = db.Column(db.String(30), nullable=False)
    enabled = db.Column(db.Boolean, default=True)
    smtp_host = db.Column(db.String(255), nullable=True)
    smtp_port = db.Column(db.Integer, nullable=True, default=587)
    sender_address = db.Column(db.String(255), nullable=True)
    recipients = db.Column(db.Text, nullable=True)
    template = db.Column(db.Text, nullable=True)
    subject_template = db.Column(db.String(500), nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class NotificationLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    channel_id = db.Column(db.Integer, db.ForeignKey('notification_channel.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service_instance.id'), nullable=False)
    event_type = db.Column(db.String(30), nullable=False)
    rendered_body = db.Column(db.Text, nullable=True)
    rendered_subject = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='sent')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    channel = db.relationship('NotificationChannel', backref='logs')
    service = db.relationship('ServiceInstance', backref='notifications')
