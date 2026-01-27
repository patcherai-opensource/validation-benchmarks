from flask_sqlalchemy import SQLAlchemy

from app.db import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='admin')
    image_profile_filename = db.Column(db.String(100), nullable=False)


class Translation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), nullable=False)
    language = db.Column(db.String(10), nullable=False)
    value = db.Column(db.Text, nullable=False)
    domain = db.Column(db.String(50), nullable=False, default='messages')


class SecretConfig(db.Model):
    """Internal configuration table - contains sensitive data"""
    id = db.Column(db.Integer, primary_key=True)
    config_key = db.Column(db.String(100), nullable=False)
    config_value = db.Column(db.Text, nullable=False)
