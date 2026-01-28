
from flask_sqlalchemy import SQLAlchemy

from app.db import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    node_count = db.Column(db.Integer, nullable=False, default=4)
    cpu_threshold = db.Column(db.Float, nullable=False, default=80.0)
    memory_threshold = db.Column(db.Float, nullable=False, default=75.0)
