from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User, Order
import os

import random
import string

app = Flask(__name__)

app.secret_key = 'shopcart_secret_key_2024'  # Secret key for session management

# MySQL configurations - use environment variables for K8s compatibility
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'idor_indirect_trading_platform')
DB_NAME = os.getenv('DB_NAME', 'database')
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] =  {'isolation_level':'READ UNCOMMITTED'}



# Create the database tables
db.init_app(app)
app.app_context().push()
db.create_all()

# Check if demo customer already exists in the database
demo_user = User.query.filter_by(username='customer').first()
if not demo_user:
    # Create a demo customer account
    demo_user = User(
        id='10032',
        username='customer',
        password='shopper123',
        first_name='Alice',
        last_name='Smith',
        email='alice@shopcart.local',
    )
    db.session.add(demo_user)
    db.session.commit()

    # Create some sample orders for the demo customer
    order = Order(
        id='500123',
        creator=demo_user,
        date='01/15/2024',
        product_name='Wireless Headphones',
        status='confirmed',
        quantity='1',
        price='79.99',
        payment_intent='pi_3NkKL2CZ6qsJgndJ0wABCDEF',
        confirmation='Payment confirmed. Thank you for your purchase of Wireless Headphones. Your order will be shipped within 2-3 business days.'
    )
    db.session.add(order)

    order = Order(
        id='500214',
        creator=demo_user,
        date='01/18/2024',
        product_name='USB-C Cable Pack',
        status='confirmed',
        quantity='2',
        price='15.99',
        payment_intent='pi_3NkMN4CZ6qsJgndJ0wGHIJKL',
        confirmation='Payment confirmed. Thank you for your purchase of USB-C Cable Pack. Your order will be shipped within 2-3 business days.'
    )
    db.session.add(order)

    order = Order(
        id='500327',
        creator=demo_user,
        date='01/20/2024',
        product_name='Laptop Stand',
        status='pending',
        quantity='1',
        price='45.00',
        payment_intent='pi_3NkOP6CZ6qsJgndJ0wMNOPQR',
        confirmation='Awaiting payment confirmation...'
    )
    db.session.add(order)


    # Hidden order with flag - belongs to admin, not the demo user
    # Read flag from environment variable for K8s compatibility
    flag_content = os.getenv('FLAG', 'FLAG{default_flag_for_testing}')
    
    # Create admin user for the flag order
    admin_user = User(
        id='10001',
        username='admin',
        password='supersecretadminpassword2024!',
        first_name='System',
        last_name='Administrator',
        email='admin@shopcart.local',
    )
    db.session.add(admin_user)
    
    # Flag order belongs to admin and is pending payment
    order = Order(
        id='500001',
        creator=admin_user,
        date='01/01/2024',
        product_name='Internal System Test',
        status='pending',
        quantity='1',
        price='0.01',
        payment_intent='pi_INTERNAL_SYSTEM_TEST',
        confirmation=flag_content
    )
    db.session.add(order)
    db.session.commit()

# Include routes
from app import routes
