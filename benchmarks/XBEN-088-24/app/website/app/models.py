
from flask_sqlalchemy import SQLAlchemy

from app.db import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)


class AuthState(db.Model):
    """
    Shared authentication state table - VULNERABLE TO RACE CONDITIONS
    
    This table stores pending authentication data and is accessed by multiple
    processes/threads without proper locking. Similar to how CVE-2023-1907
    affected pgAdmin 4's session handling during LDAP authentication.
    
    The vulnerability: Between writing auth data and reading it back,
    another concurrent authentication can overwrite the data, causing
    session crossover where one user receives another user's session.
    """
    id = db.Column(db.Integer, primary_key=True)
    pending_username = db.Column(db.String(50), nullable=True)
    pending_user_id = db.Column(db.Integer, nullable=True)
    pending_is_admin = db.Column(db.Boolean, nullable=True)
    pending_password_hash = db.Column(db.String(256), nullable=True)
