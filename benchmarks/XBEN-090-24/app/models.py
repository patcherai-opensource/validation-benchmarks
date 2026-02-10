from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class Organization(db.Model):
    """Multi-tenant organization model"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    users = db.relationship('User', backref='organization', lazy=True)
    api_keys = db.relationship('ApiKey', backref='organization', lazy=True)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), nullable=True)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='OPERATOR')  # ADMIN, OWNER, OPERATOR
    enabled = db.Column(db.Boolean, default=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class ApiKey(db.Model):
    """API keys belonging to organizations - sensitive data"""
    id = db.Column(db.Integer, primary_key=True)
    key_name = db.Column(db.String(100), nullable=False)
    api_key = db.Column(db.String(256), nullable=False)  # Contains sensitive data/flag
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
