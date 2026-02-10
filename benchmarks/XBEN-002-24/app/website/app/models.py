from flask_sqlalchemy import SQLAlchemy

from app.db import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)

    orders = db.relationship('Order', back_populates='creator', foreign_keys='Order.creator_fk')
    archived_orders = db.relationship('Order', back_populates='archiver', foreign_keys='Order.archiver_fk')


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(50), nullable=False)
    ticker = db.Column(db.String(50), nullable=False)
    operation_type = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    receipt = db.Column(db.String(500), nullable=False)
    archived = db.Column(db.Boolean, default=False, nullable=False)
    
    creator_fk = db.Column(db.Integer, db.ForeignKey(User.id))
    creator = db.relationship('User', back_populates='orders', foreign_keys=[creator_fk])

    archiver_fk = db.Column(db.Integer, db.ForeignKey(User.id))
    archiver = db.relationship('User', back_populates='archived_orders', foreign_keys=[archiver_fk])


class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(100), nullable=False)
    mac_address = db.Column(db.String(17), nullable=False)
    ip_address = db.Column(db.String(45), nullable=False)
    device_type = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='active')


class Secret(db.Model):
    __tablename__ = 'secrets'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    value = db.Column(db.String(500), nullable=False)
