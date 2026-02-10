from flask_sqlalchemy import SQLAlchemy
import time

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
    totp_secret = db.Column(db.String(32), nullable=True)


class TwoFactorToken(db.Model):
    """Stores confirmation tokens for 2FA login checkpoint"""
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(64), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    expires_at = db.Column(db.Integer, nullable=False)
    
    @classmethod
    def cleanup_expired(cls):
        """Remove expired tokens"""
        current_time = int(time.time())
        cls.query.filter(cls.expires_at < current_time).delete()
        db.session.commit()
