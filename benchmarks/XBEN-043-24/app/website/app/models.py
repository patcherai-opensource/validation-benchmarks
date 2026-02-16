from flask_sqlalchemy import SQLAlchemy

from app.db import db

class User(db.Model):
    __tablename__ = 'cms_users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False, default='')
    # credential_mode: 0=disabled/no-password, 1=md5, 2=bcrypt, 3=sha256
    credential_mode = db.Column(db.Integer, nullable=False, default=2)
    role = db.Column(db.String(50), nullable=False, default='user')
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    first_name = db.Column(db.String(100), nullable=False, default='')
    last_name = db.Column(db.String(100), nullable=False, default='')

class Content(db.Model):
    __tablename__ = 'cms_content'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('cms_users.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='draft')  # draft, published, archived
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)
