from flask_sqlalchemy import SQLAlchemy
from app.db import db


class Space(db.Model):
    __tablename__ = 'spaces'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    display_name = db.Column(db.String(200), nullable=False)
    visibility = db.Column(db.String(20), nullable=False, default='public')
    description = db.Column(db.String(500), nullable=True)

    documents = db.relationship('Document', back_populates='space', foreign_keys='Document.space_id')


class Document(db.Model):
    __tablename__ = 'documents'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content_raw = db.Column(db.Text, nullable=False)
    space_id = db.Column(db.Integer, db.ForeignKey('spaces.id'), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    doc_type = db.Column(db.String(50), nullable=False, default='DOCUMENT')
    created_at = db.Column(db.String(50), nullable=False)
    updated_at = db.Column(db.String(50), nullable=False)
    hidden = db.Column(db.Boolean, default=False, nullable=False)
    locale = db.Column(db.String(10), nullable=False, default='en')
    reference = db.Column(db.String(300), nullable=False)

    space = db.relationship('Space', back_populates='documents', foreign_keys=[space_id])


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    display_name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
