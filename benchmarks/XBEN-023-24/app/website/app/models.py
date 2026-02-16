from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

from app.db import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    display_name = db.Column(db.String(100), nullable=False, default='')
    email = db.Column(db.String(100), nullable=False, default='')
    role = db.Column(db.String(20), nullable=False, default='editor')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Page(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    body = db.Column(db.Text, nullable=False, default='')
    twig_processing = db.Column(db.Boolean, default=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    author = db.relationship('User', backref='pages', lazy=True)
