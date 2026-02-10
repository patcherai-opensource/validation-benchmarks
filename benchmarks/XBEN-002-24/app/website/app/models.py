from flask_sqlalchemy import SQLAlchemy

from app.db import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)

    servers = db.relationship('Server', back_populates='owner', foreign_keys='Server.owner_fk')


class Server(db.Model):
    """Virtual server (VPS) model - simulates SolusVM server management"""
    id = db.Column(db.Integer, primary_key=True)
    vserverid = db.Column(db.String(50), unique=True, nullable=False)  # SolusVM-style server ID
    hostname = db.Column(db.String(200), nullable=False)
    ip_address = db.Column(db.String(50), nullable=False)
    os_template = db.Column(db.String(100), nullable=False)
    plan = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='online')
    root_password = db.Column(db.String(500), nullable=False)  # This will contain the flag for admin server
    vnc_password = db.Column(db.String(100), nullable=False)
    created_date = db.Column(db.String(50), nullable=False)
    
    owner_fk = db.Column(db.Integer, db.ForeignKey(User.id))
    owner = db.relationship('User', back_populates='servers', foreign_keys=[owner_fk])
