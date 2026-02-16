from flask_sqlalchemy import SQLAlchemy

from app.db import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='customer')

    instances = db.relationship('Instance', backref='owner')


class Instance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(100), nullable=False)
    hostname = db.Column(db.String(255), nullable=False)
    ip_address = db.Column(db.String(45), nullable=False)
    virt_type = db.Column(db.String(20), nullable=False, default='kvm')
    plan = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='online')
    root_password = db.Column(db.String(255), nullable=False)
    vnc_password = db.Column(db.String(100), nullable=False)
    node = db.Column(db.String(50), nullable=False)
    os_template = db.Column(db.String(100), nullable=False)
    bandwidth_used = db.Column(db.Integer, nullable=False, default=0)
    bandwidth_limit = db.Column(db.Integer, nullable=False, default=1000)
    disk_used = db.Column(db.Integer, nullable=False, default=0)
    disk_limit = db.Column(db.Integer, nullable=False, default=50)
    memory_mb = db.Column(db.Integer, nullable=False, default=2048)
    created_date = db.Column(db.String(50), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class ActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    instance_id = db.Column(db.Integer, db.ForeignKey('instance.id'))
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.String(50), nullable=False)
