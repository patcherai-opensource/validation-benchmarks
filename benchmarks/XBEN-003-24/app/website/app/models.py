from flask_sqlalchemy import SQLAlchemy

from app.db import db


class Organization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    users = db.relationship('User', backref='organization', lazy=True)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), default='operator')
    enabled = db.Column(db.Boolean, default=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=True)
    notes = db.Column(db.Text, nullable=True)
