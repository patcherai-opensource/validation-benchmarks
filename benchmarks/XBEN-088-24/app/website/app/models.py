
from flask_sqlalchemy import SQLAlchemy

from app.db import db


class Tenant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.String(64), unique=True, nullable=False)
    display_name = db.Column(db.String(128), nullable=False)
    realm = db.Column(db.String(64), nullable=False)
    auth_endpoint = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    tenant_id = db.Column(db.String(64), db.ForeignKey('tenant.tenant_id'), nullable=False)
    role = db.Column(db.String(32), default='viewer', nullable=False)

    __table_args__ = (db.UniqueConstraint('username', 'tenant_id', name='uq_user_tenant'),)


class DeviceConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.String(64), db.ForeignKey('tenant.tenant_id'), nullable=False)
    device_name = db.Column(db.String(128), nullable=False)
    config_data = db.Column(db.Text, nullable=False)
    last_updated = db.Column(db.DateTime, server_default=db.func.now())
