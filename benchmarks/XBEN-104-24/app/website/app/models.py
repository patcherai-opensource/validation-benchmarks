
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from app.db import db


class User(db.Model):
    __tablename__ = 'am_user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')
    status = db.Column(db.String(20), nullable=False, default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)

    def is_admin(self):
        return self.role == 'admin'


class Realm(db.Model):
    __tablename__ = 'am_realm'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(500), nullable=True)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class OAuth2Provider(db.Model):
    __tablename__ = 'am_oauth2_provider'
    id = db.Column(db.Integer, primary_key=True)
    realm_id = db.Column(db.Integer, db.ForeignKey('am_realm.id'), nullable=False)
    client_id = db.Column(db.String(200), nullable=False)
    client_secret = db.Column(db.String(200), nullable=False)
    redirect_uri = db.Column(db.String(500), nullable=False)
    scope = db.Column(db.String(200), nullable=False, default='openid profile')
    response_type = db.Column(db.String(50), nullable=False, default='code')
    token_endpoint_auth_method = db.Column(db.String(50), default='client_secret_basic')
    grant_types = db.Column(db.String(200), default='authorization_code')
    custom_login_url_template = db.Column(db.Text, nullable=True)
    issuer = db.Column(db.String(200), nullable=True)
    active = db.Column(db.Boolean, default=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    realm = db.relationship('Realm', backref=db.backref('providers', lazy=True))


class OAuth2Token(db.Model):
    __tablename__ = 'am_oauth2_token'
    id = db.Column(db.Integer, primary_key=True)
    provider_id = db.Column(db.Integer, db.ForeignKey('am_oauth2_provider.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('am_user.id'), nullable=False)
    access_token = db.Column(db.String(500), nullable=False)
    token_type = db.Column(db.String(50), default='Bearer')
    expires_at = db.Column(db.DateTime, nullable=False)
    scope = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    provider = db.relationship('OAuth2Provider', backref=db.backref('tokens', lazy=True))
    user = db.relationship('User', backref=db.backref('tokens', lazy=True))


class AuditLog(db.Model):
    __tablename__ = 'am_audit_log'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=True)
    action = db.Column(db.String(100), nullable=False)
    resource = db.Column(db.String(200), nullable=True)
    details = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(50), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
