from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

from app.db import db


class User(UserMixin, db.Model):
    __tablename__ = 'ab_user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    is_superuser = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)


class Connection(db.Model):
    __tablename__ = 'connection'
    id = db.Column(db.Integer, primary_key=True)
    conn_id = db.Column(db.String(250), unique=True, nullable=False)
    conn_type = db.Column(db.String(500), nullable=False)
    host = db.Column(db.String(500))
    login = db.Column(db.String(500))
    password = db.Column(db.String(500))
    port = db.Column(db.Integer)
    extra = db.Column(db.Text)


class DagModel(db.Model):
    __tablename__ = 'dag'
    dag_id = db.Column(db.String(250), primary_key=True)
    filepath = db.Column(db.String(2000))
    is_paused = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)


class Variable(db.Model):
    __tablename__ = 'variable'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(250), unique=True, nullable=False)
    val = db.Column(db.Text)
