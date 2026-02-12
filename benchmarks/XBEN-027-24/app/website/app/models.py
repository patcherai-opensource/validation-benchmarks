from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

from app.db import db


class User(db.Model):
    __tablename__ = 'sys_user'
    id = db.Column(db.BigInteger, primary_key=True)
    account = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(128), nullable=True)
    mobile = db.Column(db.String(20), nullable=True)
    status = db.Column(db.Boolean, default=True)
    readonly = db.Column(db.Boolean, default=False)

    def set_password(self, pw):
        self.password_hash = generate_password_hash(pw)

    def check_password(self, pw):
        return check_password_hash(self.password_hash, pw)


class Role(db.Model):
    __tablename__ = 'sys_role'
    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    code = db.Column(db.String(64), unique=True, nullable=False)
    describe_ = db.Column(db.String(256), nullable=True)
    status = db.Column(db.Boolean, default=True)
    readonly = db.Column(db.Boolean, default=False)


class UserRole(db.Model):
    __tablename__ = 'sys_user_role'
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('sys_user.id'), nullable=False)
    role_id = db.Column(db.BigInteger, db.ForeignKey('sys_role.id'), nullable=False)


class SystemConfig(db.Model):
    __tablename__ = 'sys_config'
    id = db.Column(db.BigInteger, primary_key=True)
    key = db.Column(db.String(128), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=True)
    description = db.Column(db.String(256), nullable=True)
    readonly = db.Column(db.Boolean, default=False)
