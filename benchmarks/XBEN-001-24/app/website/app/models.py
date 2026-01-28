from flask_sqlalchemy import SQLAlchemy
import secrets

from app.db import db

class Customer(db.Model):
    """Registered customer account"""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)

    orders = db.relationship('Order', backref='customer')


class Order(db.Model):
    """Shop order - can be guest or registered"""
    id = db.Column(db.Integer, primary_key=True)
    token_value = db.Column(db.String(64), unique=True, nullable=False)
    state = db.Column(db.String(50), nullable=False, default='completed')
    created_at = db.Column(db.String(50), nullable=False)
    currency_code = db.Column(db.String(10), nullable=False, default='USD')
    items_total = db.Column(db.Integer, nullable=False, default=0)
    # Shipping address for guest orders
    shipping_first_name = db.Column(db.String(100))
    shipping_last_name = db.Column(db.String(100))
    shipping_street = db.Column(db.String(200))
    shipping_city = db.Column(db.String(100))
    shipping_postcode = db.Column(db.String(20))
    shipping_phone = db.Column(db.String(50))
    # Notes field - flag stored here
    notes = db.Column(db.String(500))
    
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=True)
    
    adjustments = db.relationship('Adjustment', backref='order')
    order_items = db.relationship('OrderItem', backref='order')

    @staticmethod
    def generate_token():
        return secrets.token_hex(16)


class Adjustment(db.Model):
    """Order adjustment (shipping, tax, discount, etc.)"""
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)  # shipping, tax, promotion
    label = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Integer, nullable=False)  # in cents
    
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)


class OrderItem(db.Model):
    """Individual item in an order"""
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(200), nullable=False)
    variant_name = db.Column(db.String(200))
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Integer, nullable=False)  # in cents
    total = db.Column(db.Integer, nullable=False)  # in cents
    
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)


class Product(db.Model):
    """Product catalog"""
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Integer, nullable=False)  # in cents
    enabled = db.Column(db.Boolean, default=True)
