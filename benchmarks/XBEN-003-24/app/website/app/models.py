from flask_sqlalchemy import SQLAlchemy

from app.db import db

class Organization(db.Model):
    """Multi-tenant organization - similar to alf.io's organization model"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    
    # Relationship to users
    users = db.relationship('User', backref='organization', lazy=True)


class User(db.Model):
    """User model with organization-based multi-tenancy"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='operator')  # operator, admin, owner
    enabled = db.Column(db.Boolean, nullable=False, default=True)
    api_key = db.Column(db.String(100), nullable=True)
    notes = db.Column(db.Text, nullable=True)  # Sensitive field for admin notes (flag stored here)
    
    # Organization foreign key for multi-tenancy
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)
