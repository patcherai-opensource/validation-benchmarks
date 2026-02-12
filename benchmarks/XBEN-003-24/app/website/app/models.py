from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

from app.db import db


class User(db.Model):
    __tablename__ = 'ab_user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='Viewer')
    active = db.Column(db.Boolean, default=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Connection(db.Model):
    __tablename__ = 'connection'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    conn_id = db.Column(db.String(250), unique=True, nullable=False)
    conn_type = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text, nullable=True)
    host = db.Column(db.String(500), nullable=True)
    schema = db.Column(db.String(500), nullable=True)
    login = db.Column(db.String(500), nullable=True)
    password = db.Column(db.String(500), nullable=True)
    port = db.Column(db.Integer, nullable=True)
    extra = db.Column(db.Text, nullable=True)
    is_encrypted = db.Column(db.Boolean, default=False)
    is_extra_encrypted = db.Column(db.Boolean, default=False)


class DagModel(db.Model):
    __tablename__ = 'dag'
    dag_id = db.Column(db.String(250), primary_key=True)
    is_paused = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    schedule_interval = db.Column(db.String(500), nullable=True)
    description = db.Column(db.Text, nullable=True)
    owners = db.Column(db.String(2000), nullable=True)
    file_loc = db.Column(db.String(2000), nullable=True)


class Variable(db.Model):
    __tablename__ = 'variable'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    key = db.Column(db.String(250), unique=True, nullable=False)
    val = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    is_encrypted = db.Column(db.Boolean, default=False)
