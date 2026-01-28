from flask_sqlalchemy import SQLAlchemy

from app.db import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)

    servers = db.relationship('VirtualServer', back_populates='owner', foreign_keys='VirtualServer.owner_fk')
    managed_servers = db.relationship('VirtualServer', back_populates='manager', foreign_keys='VirtualServer.manager_fk')


class VirtualServer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(100), nullable=False)
    ip_address = db.Column(db.String(50), nullable=False)
    os_template = db.Column(db.String(100), nullable=False)
    vcpu = db.Column(db.Integer, nullable=False)
    ram_mb = db.Column(db.Integer, nullable=False)
    disk_gb = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), nullable=False)  # running, stopped, suspended
    root_password = db.Column(db.String(500), nullable=False)
    transferred = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.String(50), nullable=False)
    
    owner_fk = db.Column(db.Integer, db.ForeignKey(User.id))
    owner = db.relationship('User', back_populates='servers', foreign_keys=[owner_fk])

    manager_fk = db.Column(db.Integer, db.ForeignKey(User.id))
    manager = db.relationship('User', back_populates='managed_servers', foreign_keys=[manager_fk])
