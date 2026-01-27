from flask_sqlalchemy import SQLAlchemy

from app.db import db

class ApiToken(db.Model):
    """API tokens for authentication to the device management API"""
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(64), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    description = db.Column(db.String(200))


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    level = db.Column(db.Integer, default=1)  # User privilege level

    devices = db.relationship('Device', backref='owner')
    api_tokens = db.relationship('ApiToken', backref='user')


class Device(db.Model):
    """Network devices being monitored"""
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, unique=True, nullable=False)
    hostname = db.Column(db.String(100), nullable=False)
    sysname = db.Column(db.String(100))
    ip = db.Column(db.String(50), nullable=False)
    status = db.Column(db.Integer, default=1)  # 1=up, 0=down
    os = db.Column(db.String(100))
    hardware = db.Column(db.String(100))
    location = db.Column(db.String(200))
    uptime = db.Column(db.Integer, default=0)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class SystemSecret(db.Model):
    """System configuration secrets - internal use only"""
    id = db.Column(db.Integer, primary_key=True)
    key_name = db.Column(db.String(100), unique=True, nullable=False)
    secret_value = db.Column(db.String(500), nullable=False)
