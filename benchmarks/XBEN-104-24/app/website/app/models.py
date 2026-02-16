
from flask_sqlalchemy import SQLAlchemy

from app.db import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')


class OAuthClient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.String(100), unique=True, nullable=False)
    client_secret = db.Column(db.String(100), nullable=False)
    client_name = db.Column(db.String(100), nullable=False)
    redirect_uri = db.Column(db.String(500), nullable=False)
    allowed_scopes = db.Column(db.String(500), nullable=False, default='openid profile email')
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class RealmSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    realm_name = db.Column(db.String(100), unique=True, nullable=False)
    issuer_url = db.Column(db.String(500), nullable=True)
    token_lifetime = db.Column(db.Integer, nullable=False, default=3600)
    auth_redirect_template = db.Column(db.Text, nullable=True)
    consent_prompt_enabled = db.Column(db.Boolean, nullable=False, default=True)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)


class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
