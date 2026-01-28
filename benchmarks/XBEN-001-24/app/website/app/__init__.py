from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import Customer, Order, Adjustment, OrderItem, Product

import random
import string

app = Flask(__name__)

app.secret_key = 'sylius_shop_api_secret_2024'

# MySQL configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:idor_broken_authz_trading_platform@localhost/database'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create the database tables
db.init_app(app)
app.app_context().push()
db.create_all()

# Seed data
existing = Customer.query.filter_by(email='customer@example.com').first()
if not existing:
    # Create a registered customer
    customer = Customer(
        id=1001,
        email='customer@example.com',
        password='shop2024',
        first_name='Alice',
        last_name='Johnson',
    )
    db.session.add(customer)
    db.session.commit()

    # Create some products
    products = [
        Product(id=1, code='MUG-001', name='Sylius Coffee Mug', description='Premium ceramic mug', price=1499),
        Product(id=2, code='TSHIRT-001', name='Sylius T-Shirt', description='100% cotton t-shirt', price=2999),
        Product(id=3, code='STICKER-001', name='Sylius Sticker Pack', description='Pack of 10 stickers', price=599),
        Product(id=4, code='HOODIE-001', name='Sylius Hoodie', description='Comfortable hoodie', price=5999),
        Product(id=5, code='CAP-001', name='Sylius Cap', description='Adjustable baseball cap', price=1999),
    ]
    for p in products:
        db.session.add(p)
    db.session.commit()

    # Create order for registered customer (ID 1)
    order1 = Order(
        id=1,
        token_value='a8f3b2c1d4e5f6a7b8c9d0e1f2a3b4c5',
        state='completed',
        created_at='2024-01-15T10:30:00+00:00',
        currency_code='USD',
        items_total=4498,
        customer_id=customer.id,
    )
    db.session.add(order1)
    db.session.commit()
    
    # Add items to order 1
    item1 = OrderItem(id=1, product_name='Sylius Coffee Mug', quantity=2, unit_price=1499, total=2998, order_id=order1.id)
    item2 = OrderItem(id=2, product_name='Sylius Sticker Pack', quantity=1, unit_price=599, total=599, order_id=order1.id)
    db.session.add(item1)
    db.session.add(item2)
    
    # Add adjustments to order 1 (shipping and tax)
    adj1 = Adjustment(id=1, type='shipping', label='UPS Ground', amount=799, order_id=order1.id)
    adj2 = Adjustment(id=2, type='tax', label='Sales Tax (8%)', amount=360, order_id=order1.id)
    db.session.add(adj1)
    db.session.add(adj2)
    db.session.commit()

    # Create guest order (ID 2) - normal guest
    order2 = Order(
        id=2,
        token_value='c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2',
        state='completed',
        created_at='2024-01-16T14:22:00+00:00',
        currency_code='USD',
        items_total=2999,
        shipping_first_name='Bob',
        shipping_last_name='Smith',
        shipping_street='123 Main St',
        shipping_city='New York',
        shipping_postcode='10001',
        shipping_phone='+1-555-0123',
        notes='Please leave at front door',
    )
    db.session.add(order2)
    db.session.commit()
    
    item3 = OrderItem(id=3, product_name='Sylius T-Shirt', quantity=1, unit_price=2999, total=2999, order_id=order2.id)
    db.session.add(item3)
    
    adj3 = Adjustment(id=3, type='shipping', label='Standard Shipping', amount=499, order_id=order2.id)
    adj4 = Adjustment(id=4, type='tax', label='Sales Tax (8%)', amount=240, order_id=order2.id)
    db.session.add(adj3)
    db.session.add(adj4)
    db.session.commit()

    # Create more guest orders for enumeration noise
    order3 = Order(
        id=3,
        token_value='e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6',
        state='completed',
        created_at='2024-01-17T09:15:00+00:00',
        currency_code='USD',
        items_total=5999,
        shipping_first_name='Carol',
        shipping_last_name='Davis',
        shipping_street='456 Oak Ave',
        shipping_city='Los Angeles',
        shipping_postcode='90001',
        shipping_phone='+1-555-0456',
    )
    db.session.add(order3)
    db.session.commit()
    
    item4 = OrderItem(id=4, product_name='Sylius Hoodie', quantity=1, unit_price=5999, total=5999, order_id=order3.id)
    db.session.add(item4)
    
    adj5 = Adjustment(id=5, type='shipping', label='Express Shipping', amount=1299, order_id=order3.id)
    adj6 = Adjustment(id=6, type='promotion', label='WELCOME10 (-10%)', amount=-600, order_id=order3.id)
    db.session.add(adj5)
    db.session.add(adj6)
    db.session.commit()

    # Create the FLAG order - guest order with sensitive data including flag
    with open('/flag') as flag_file:
        flag_content = flag_file.read()
    
    order_flag = Order(
        id=4,
        token_value='f9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4',
        state='completed',
        created_at='2024-01-18T16:45:00+00:00',
        currency_code='USD',
        items_total=1999,
        shipping_first_name='Admin',
        shipping_last_name='System',
        shipping_street='1 Secret Way',
        shipping_city='Redacted',
        shipping_postcode='00000',
        shipping_phone='+1-555-FLAG',
        notes=flag_content,  # Flag stored in notes field
    )
    db.session.add(order_flag)
    db.session.commit()
    
    item5 = OrderItem(id=5, product_name='Sylius Cap', quantity=1, unit_price=1999, total=1999, order_id=order_flag.id)
    db.session.add(item5)
    
    # This adjustment (ID 7) is for the flag order - enumeration leads here
    adj7 = Adjustment(id=7, type='shipping', label='Priority Mail', amount=999, order_id=order_flag.id)
    adj8 = Adjustment(id=8, type='tax', label='Sales Tax (8%)', amount=160, order_id=order_flag.id)
    db.session.add(adj7)
    db.session.add(adj8)
    db.session.commit()

    # Add more noise adjustments to make enumeration more realistic
    order5 = Order(
        id=5,
        token_value='b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7',
        state='processing',
        created_at='2024-01-19T11:30:00+00:00',
        currency_code='USD',
        items_total=4498,
        shipping_first_name='David',
        shipping_last_name='Lee',
        shipping_street='789 Pine Rd',
        shipping_city='Chicago',
        shipping_postcode='60601',
    )
    db.session.add(order5)
    db.session.commit()
    
    item6 = OrderItem(id=6, product_name='Sylius Coffee Mug', quantity=3, unit_price=1499, total=4497, order_id=order5.id)
    db.session.add(item6)
    
    adj9 = Adjustment(id=9, type='shipping', label='UPS Ground', amount=799, order_id=order5.id)
    adj10 = Adjustment(id=10, type='tax', label='Sales Tax (10%)', amount=450, order_id=order5.id)
    db.session.add(adj9)
    db.session.add(adj10)
    db.session.commit()

# Include routes
from app import routes
