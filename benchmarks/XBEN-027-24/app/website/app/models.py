from flask_sqlalchemy import SQLAlchemy
from app.db import db


class User(db.Model):
    __tablename__ = "ab_user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="Gamma")
    active = db.Column(db.Boolean, default=True)


class Dashboard(db.Model):
    __tablename__ = "dashboards"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    description = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey("ab_user.id"))
    published = db.Column(db.Boolean, default=False)

    owner = db.relationship("User", backref="dashboards")


class SavedQuery(db.Model):
    __tablename__ = "saved_query"

    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    sql_text = db.Column(db.Text, nullable=False)
    database_id = db.Column(db.Integer, db.ForeignKey("database_connection.id"))
    created_by_id = db.Column(db.Integer, db.ForeignKey("ab_user.id"))

    created_by = db.relationship("User", backref="saved_queries")
    database = db.relationship("DatabaseConnection", backref="saved_queries")


class DatabaseConnection(db.Model):
    __tablename__ = "database_connection"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    database_type = db.Column(db.String(50), nullable=False)
    connection_string = db.Column(db.String(500), nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey("ab_user.id"))

    created_by = db.relationship("User", backref="database_connections")
