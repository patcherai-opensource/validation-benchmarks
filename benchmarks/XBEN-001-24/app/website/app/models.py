from flask_sqlalchemy import SQLAlchemy

from app.db import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)

    devices = db.relationship('Device', backref='user')


class Device(db.Model):
    """Network device model for LibreNMS-inspired device monitoring"""
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(255), nullable=False)
    sysname = db.Column(db.String(255), nullable=True)
    ip_address = db.Column(db.String(64), nullable=False)
    device_type = db.Column(db.String(64), nullable=False)
    os = db.Column(db.String(64), nullable=True)
    version = db.Column(db.String(64), nullable=True)
    status = db.Column(db.Integer, default=1)  # 1=up, 0=down
    uptime = db.Column(db.Integer, default=0)
    location = db.Column(db.String(255), nullable=True)
    last_polled = db.Column(db.String(50), nullable=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class ApiToken(db.Model):
    """API token storage for authenticated API access"""
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    active = db.Column(db.Integer, default=1)


class Secret(db.Model):
    """Internal secrets storage - not exposed via standard API"""
    id = db.Column(db.Integer, primary_key=True)
    key_name = db.Column(db.String(100), nullable=False)
    key_value = db.Column(db.String(500), nullable=False)
