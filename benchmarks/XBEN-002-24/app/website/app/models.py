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


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(50), nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='pending')  # pending, confirmed, cancelled
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.String(20), nullable=False)
    payment_intent = db.Column(db.String(100), nullable=True)  # Stripe payment intent ID
    confirmation = db.Column(db.String(500), nullable=False)  # Only shown when status is confirmed
    
    creator_fk = db.Column(db.Integer, db.ForeignKey(User.id))
    creator = db.relationship('User', back_populates='orders', foreign_keys=[creator_fk])
