from flask_sqlalchemy import SQLAlchemy

from app.db import db


class Organization(db.Model):
    """Multi-tenant organization model - mirrors alf.io's organization concept"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(500), nullable=True)
    
    users = db.relationship('User', back_populates='organization', foreign_keys='User.organization_fk')


class User(db.Model):
    """User model with organization membership for multi-tenancy"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), default='OPERATOR', nullable=False)  # ADMIN, OPERATOR, API_KEY
    enabled = db.Column(db.Boolean, default=True, nullable=False)
    secret_notes = db.Column(db.String(1000), nullable=True)  # Internal notes - should be protected
    
    organization_fk = db.Column(db.Integer, db.ForeignKey('organization.id'))
    organization = db.relationship('Organization', back_populates='users', foreign_keys=[organization_fk])
