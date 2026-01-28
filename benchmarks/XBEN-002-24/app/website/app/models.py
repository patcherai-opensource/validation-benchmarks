from flask_sqlalchemy import SQLAlchemy

from app.db import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), default='user', nullable=False)


class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(100), nullable=False)
    ip_address = db.Column(db.String(50), nullable=False)
    mac_address = db.Column(db.String(50), nullable=False)
    device_type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='active', nullable=False)
    location = db.Column(db.String(100), nullable=True)
    last_seen = db.Column(db.String(50), nullable=True)
    
    owner_fk = db.Column(db.Integer, db.ForeignKey(User.id))
    owner = db.relationship('User', backref='devices', foreign_keys=[owner_fk])


class SystemConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    config_key = db.Column(db.String(100), unique=True, nullable=False)
    config_value = db.Column(db.String(500), nullable=False)
    description = db.Column(db.String(200), nullable=True)
