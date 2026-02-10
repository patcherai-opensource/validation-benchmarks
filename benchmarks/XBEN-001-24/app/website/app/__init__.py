from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User, Order

import random
import string
import secrets

app = Flask(__name__)

app.secret_key = secrets.token_hex(32)

# MySQL configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:idor_broken_authz_trading_platform@localhost/database'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create the database tables
db.init_app(app)
app.app_context().push()
db.create_all()

# Check if admin already exists in the database
admin = User.query.filter_by(username='admin').first()
if not admin:
    # Create admin user with random password
    admin = User(
        id='10001',
        username='admin',
        password=secrets.token_hex(32),
        first_name='Admin',
        last_name='User',
        email='admin@shopstore.local',
    )
    db.session.add(admin)
    db.session.commit()

    # Admin's special order containing the flag - payment not yet confirmed
    with open('/flag') as flag_file:
        flag_content = flag_file.read()
    admin_order = Order(
        id='500001',
        user=admin,
        date='05/16/2024',
        product_name='Premium Enterprise License',
        quantity=1,
        price=9999,
        status='awaiting_payment',
        payment_intent_id='pi_admin_premium_license_2024',
        payment_confirmed=False,
        confirmation_message=flag_content
    )
    db.session.add(admin_order)
    db.session.commit()

# Check if demo user already exists
demo = User.query.filter_by(username='demo').first()
if not demo:
    # Create demo user for customers to browse
    demo = User(
        id='10032',
        username='demo',
        password='demo123',
        first_name='Demo',
        last_name='Customer',
        email='demo@example.com',
    )
    db.session.add(demo)
    db.session.commit()

    order = Order(
        id='300123',
        user=demo,
        date='05/15/2024',
        product_name='Wireless Keyboard',
        quantity=2,
        price=45,
        status='completed',
        payment_intent_id=Order.generate_payment_intent_id(),
        payment_confirmed=True,
        confirmation_message='Thank you for your purchase! Your wireless keyboards have been shipped.'
    )
    db.session.add(order)

    order = Order(
        id='300214',
        user=demo,
        date='05/15/2024',
        product_name='USB-C Hub',
        quantity=1,
        price=35,
        status='completed',
        payment_intent_id=Order.generate_payment_intent_id(),
        payment_confirmed=True,
        confirmation_message='Thank you for your purchase! Your USB-C hub has been shipped.'
    )
    db.session.add(order)

    order = Order(
        id='300327',
        user=demo,
        date='05/16/2024',
        product_name='Monitor Stand',
        quantity=1,
        price=89,
        status='pending',
        payment_intent_id=Order.generate_payment_intent_id(),
        payment_confirmed=False,
        confirmation_message=None
    )
    db.session.add(order)

    order = Order(
        id='300481',
        user=demo,
        date='05/16/2024',
        product_name='Mechanical Keyboard',
        quantity=1,
        price=150,
        status='pending',
        payment_intent_id=Order.generate_payment_intent_id(),
        payment_confirmed=False,
        confirmation_message=None
    )
    db.session.add(order)
    db.session.commit()

# Include routes
from app import routes
