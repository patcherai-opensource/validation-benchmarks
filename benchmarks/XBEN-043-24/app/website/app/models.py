from flask_sqlalchemy import SQLAlchemy
from app.db import db


class User(db.Model):
    __tablename__ = 'ezuser'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), nullable=False, default='')
    password_hash = db.Column(db.String(255), nullable=False, default='')
    password_hash_type = db.Column(db.Integer, nullable=False, default=5)
    is_enabled = db.Column(db.Boolean, default=True)


class UserRole(db.Model):
    __tablename__ = 'ezuser_role'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('ezuser.id'), nullable=False)
    role_name = db.Column(db.String(100), nullable=False, default='member')


class ContentObject(db.Model):
    __tablename__ = 'ezcontentobject'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    section_id = db.Column(db.Integer, nullable=False, default=1)
    owner_id = db.Column(db.Integer, db.ForeignKey('ezuser.id'), nullable=False)
    published = db.Column(db.Integer, default=0)
    content_type = db.Column(db.String(50), nullable=False, default='article')
    body = db.Column(db.Text, default='')


class SiteConfig(db.Model):
    __tablename__ = 'ezsiteconfig'
    id = db.Column(db.Integer, primary_key=True)
    setting_key = db.Column(db.String(150), unique=True, nullable=False)
    setting_value = db.Column(db.Text, nullable=False, default='')
