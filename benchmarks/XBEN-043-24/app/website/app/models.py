from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

from app.db import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='viewer')
    active = db.Column(db.Boolean, default=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Dashboard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(100), unique=True)
    description = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    published = db.Column(db.Boolean, default=False)


class Chart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    viz_type = db.Column(db.String(100))
    dashboard_id = db.Column(db.Integer, db.ForeignKey('dashboard.id'))
    datasource = db.Column(db.String(200))


class DatabaseConnection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    uri = db.Column(db.String(500))
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
