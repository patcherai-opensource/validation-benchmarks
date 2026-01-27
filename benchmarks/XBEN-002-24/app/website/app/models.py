from flask_sqlalchemy import SQLAlchemy

from app.db import db

class Organization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(500), nullable=True)
    
    users = db.relationship('User', back_populates='organization', foreign_keys='User.organization_fk')
    events = db.relationship('Event', back_populates='organization', foreign_keys='Event.organization_fk')


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), default='operator', nullable=False)  # admin, operator
    enabled = db.Column(db.Boolean, default=True, nullable=False)
    
    organization_fk = db.Column(db.Integer, db.ForeignKey(Organization.id))
    organization = db.relationship('Organization', back_populates='users', foreign_keys=[organization_fk])

    events = db.relationship('Event', back_populates='creator', foreign_keys='Event.creator_fk')
    managed_events = db.relationship('Event', back_populates='manager', foreign_keys='Event.manager_fk')


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    ticket_type = db.Column(db.String(50), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    config_data = db.Column(db.String(500), nullable=False)  # Sensitive configuration
    enabled = db.Column(db.Boolean, default=True, nullable=False)
    
    organization_fk = db.Column(db.Integer, db.ForeignKey(Organization.id))
    organization = db.relationship('Organization', back_populates='events', foreign_keys=[organization_fk])
    
    creator_fk = db.Column(db.Integer, db.ForeignKey(User.id))
    creator = db.relationship('User', back_populates='events', foreign_keys=[creator_fk])

    manager_fk = db.Column(db.Integer, db.ForeignKey(User.id))
    manager = db.relationship('User', back_populates='managed_events', foreign_keys=[manager_fk])
