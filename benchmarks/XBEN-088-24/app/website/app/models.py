
from flask_sqlalchemy import SQLAlchemy

from app.db import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    totp_enabled = db.Column(db.Boolean, default=False, nullable=False)
    totp_secret = db.Column(db.String(100), nullable=True)


class LoginToken(db.Model):
    """Stores confirmation tokens for 2FA login flow"""
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(100), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.Integer, nullable=False)  # Unix timestamp
