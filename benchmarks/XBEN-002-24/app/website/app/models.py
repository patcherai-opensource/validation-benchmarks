from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from app.db import db


class Customer(db.Model):
    __tablename__ = 'wp_users'
    id = db.Column(db.Integer, primary_key=True)
    user_login = db.Column(db.String(100), unique=True, nullable=False)
    user_pass = db.Column(db.String(255), nullable=False)
    user_email = db.Column(db.String(100), nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    user_registered = db.Column(db.DateTime, default=datetime.utcnow)
    role = db.Column(db.String(50), default='customer')

    orders = db.relationship('WCOrder', back_populates='customer', foreign_keys='WCOrder.customer_id')


class WCOrder(db.Model):
    __tablename__ = 'wp_wc_orders'
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(50), nullable=False, default='pending')
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    total = db.Column(db.String(50), nullable=False, default='0.00')
    currency = db.Column(db.String(10), default='USD')
    billing_email = db.Column(db.String(100))
    billing_name = db.Column(db.String(200))
    payment_method = db.Column(db.String(50), default='stripe')
    payment_method_title = db.Column(db.String(100), default='Credit Card (Stripe)')

    customer_id = db.Column(db.Integer, db.ForeignKey('wp_users.id'))
    customer = db.relationship('Customer', back_populates='orders', foreign_keys=[customer_id])

    payment_intent = db.relationship('PaymentIntent', back_populates='order', uselist=False)
    items = db.relationship('WCOrderItem', back_populates='order')
    notes = db.relationship('WCOrderNote', back_populates='order', order_by='WCOrderNote.date_created.desc()')


class WCOrderItem(db.Model):
    __tablename__ = 'wp_wc_order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('wp_wc_orders.id'), nullable=False)
    product_name = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    line_total = db.Column(db.String(50), nullable=False)

    order = db.relationship('WCOrder', back_populates='items')


class WCOrderNote(db.Model):
    __tablename__ = 'wp_wc_order_notes'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('wp_wc_orders.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    is_customer_note = db.Column(db.Boolean, default=False)

    order = db.relationship('WCOrder', back_populates='notes')


class PaymentIntent(db.Model):
    __tablename__ = 'wp_wc_stripe_payment_intents'
    id = db.Column(db.Integer, primary_key=True)
    intent_id = db.Column(db.String(100), unique=True, nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('wp_wc_orders.id'), nullable=True)
    amount = db.Column(db.Integer, nullable=False)
    currency = db.Column(db.String(10), default='usd')
    status = db.Column(db.String(50), default='requires_payment_method')
    client_secret = db.Column(db.String(500), nullable=False)
    customer_stripe_id = db.Column(db.String(100))
    payment_method_id = db.Column(db.String(100))
    created = db.Column(db.DateTime, default=datetime.utcnow)
    metadata_info = db.Column(db.Text)

    order = db.relationship('WCOrder', back_populates='payment_intent', foreign_keys=[order_id])


class WCProduct(db.Model):
    __tablename__ = 'wp_wc_products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), nullable=False)
    price = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    stock_quantity = db.Column(db.Integer, default=0)
    sku = db.Column(db.String(100))
    status = db.Column(db.String(50), default='publish')
