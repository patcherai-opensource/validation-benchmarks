from flask_sqlalchemy import SQLAlchemy

from app.db import db


class Organization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(500), nullable=True)
    
    users = db.relationship('User', back_populates='organization')
    events = db.relationship('Event', back_populates='organization')


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='operator')
    enabled = db.Column(db.Boolean, default=True, nullable=False)
    api_key = db.Column(db.String(500), nullable=True)
    
    organization_fk = db.Column(db.Integer, db.ForeignKey(Organization.id))
    organization = db.relationship('Organization', back_populates='users')


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    tickets_sold = db.Column(db.Integer, default=0, nullable=False)
    price = db.Column(db.Float, nullable=False)
    
    organization_fk = db.Column(db.Integer, db.ForeignKey(Organization.id))
    organization = db.relationship('Organization', back_populates='events')
