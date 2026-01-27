from flask_sqlalchemy import SQLAlchemy

from app.db import db

class WikiUser(db.Model):
    """Wiki platform user model with various field types"""
    __tablename__ = 'wiki_users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    display_name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    # Password field - should be protected from query exposure
    password = db.Column(db.String(500), nullable=False)
    
    # Define which columns are safe for public queries
    PUBLIC_COLUMNS = ['id', 'username', 'display_name', 'email', 'role']
    # Password columns that should be filtered
    PASSWORD_COLUMNS = ['password']
    ALL_COLUMNS = ['id', 'username', 'display_name', 'email', 'role', 'password']
