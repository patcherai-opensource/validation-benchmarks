from flask_sqlalchemy import SQLAlchemy
import secrets

from app.db import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)

    orders = db.relationship('Order', backref='user')


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(50), nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='pending')
    payment_intent_id = db.Column(db.String(100), nullable=False)
    payment_confirmed = db.Column(db.Boolean, nullable=False, default=False)
    confirmation_message = db.Column(db.String(500), nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    @staticmethod
    def generate_payment_intent_id():
        return 'pi_' + secrets.token_hex(12)
