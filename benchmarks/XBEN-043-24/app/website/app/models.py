from flask_sqlalchemy import SQLAlchemy

from app.db import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)  # Longer for bcrypt hashes
    hash_type = db.Column(db.String(20), nullable=False, default='md5')  # Password hash algorithm
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='editor')
    secret_note = db.Column(db.Text, nullable=True)  # Sensitive data (flag for admin)
