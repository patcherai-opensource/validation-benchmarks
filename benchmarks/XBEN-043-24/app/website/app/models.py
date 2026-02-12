from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from app.db import db


class User(db.Model):
    __tablename__ = 'ab_user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    username = db.Column(db.String(256), unique=True, nullable=False)
    password = db.Column(db.String(256))
    active = db.Column(db.Boolean, default=True)
    email = db.Column(db.String(256), unique=True, nullable=False)
    last_login = db.Column(db.DateTime, default=None)
    login_count = db.Column(db.Integer, default=0)
    created_on = db.Column(db.DateTime, default=datetime.utcnow)
    changed_on = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    roles = db.relationship('Role', secondary='ab_user_role', backref='users')


class Role(db.Model):
    __tablename__ = 'ab_role'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), unique=True, nullable=False)


class UserRole(db.Model):
    __tablename__ = 'ab_user_role'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('ab_user.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('ab_role.id'), nullable=False)


class Dashboard(db.Model):
    __tablename__ = 'dashboards'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dashboard_title = db.Column(db.String(500))
    slug = db.Column(db.String(255), unique=True)
    position_json = db.Column(db.Text)
    css = db.Column(db.Text)
    json_metadata = db.Column(db.Text)
    published = db.Column(db.Boolean, default=False)
    changed_on = db.Column(db.DateTime, default=datetime.utcnow)
    created_by_fk = db.Column(db.Integer, db.ForeignKey('ab_user.id'))


class SavedQuery(db.Model):
    __tablename__ = 'saved_query'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    label = db.Column(db.String(256))
    db_id = db.Column(db.Integer)
    sql = db.Column(db.Text)
    description = db.Column(db.Text)
    changed_on = db.Column(db.DateTime, default=datetime.utcnow)
    created_by_fk = db.Column(db.Integer, db.ForeignKey('ab_user.id'))


class DatabaseConnection(db.Model):
    __tablename__ = 'dbs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    database_name = db.Column(db.String(250), unique=True, nullable=False)
    sqlalchemy_uri = db.Column(db.String(1024), nullable=False)
    password = db.Column(db.String(1024))
    extra = db.Column(db.Text)
    created_by_fk = db.Column(db.Integer, db.ForeignKey('ab_user.id'))
