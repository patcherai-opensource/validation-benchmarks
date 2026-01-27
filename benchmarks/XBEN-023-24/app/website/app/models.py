from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from app.db import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='editor')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    pages = db.relationship('Page', backref='author', lazy=True)


class Page(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False, default='')
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    twig_enabled = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
