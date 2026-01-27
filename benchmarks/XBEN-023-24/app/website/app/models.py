from flask_sqlalchemy import SQLAlchemy

from app.db import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    default_hosts = db.Column(db.String(20), nullable=False, default='10')
    timeout_seconds = db.Column(db.Integer, nullable=False, default=30)
    retry_count = db.Column(db.Integer, nullable=False, default=3)
