from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User, Order, Adjustment

import random
import string
import uuid

app = Flask(__name__)

app.secret_key = 'your_secret_key'  # Change this to a secure secret key

# MySQL configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:idor_broken_authz_trading_platform@localhost/database'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create the database tables
db.init_app(app)
app.app_context().push()
db.create_all()

# Check if test already exists in the database
test = User.query.filter_by(username='test').first()
if not test:
    # Create a registered user with some orders
    test = User(
        id='10032',
        username='test',
        password='test',
        first_name='John',
        last_name='Doe',
        email='john@example.com',
    )
    db.session.add(test)
    db.session.commit()

    # Registered user orders (with user association)
    order1 = Order(
        id='300123',
        token_value='ord-' + str(uuid.uuid4()),
        user=test,
        date='05/15/2024',
        ticker='SPY',
        operation_type='BUY',
        quantity='100',
        price='53000',
        receipt='Order confirmation: 100 shares of SPY purchased at $530.00 per share. Total: $53,000.00',
        customer_email='john@example.com'
    )
    db.session.add(order1)

    order2 = Order(
        id='300214',
        token_value='ord-' + str(uuid.uuid4()),
        user=test,
        date='05/15/2024',
        ticker='SPY',
        operation_type='SELL',
        quantity='50',
        price='26750',
        receipt='Order confirmation: 50 shares of SPY sold at $535.00 per share. Total: $26,750.00',
        customer_email='john@example.com'
    )
    db.session.add(order2)

    # Add adjustments for registered user orders
    adj1 = Adjustment(
        id=1,
        type='order_promotion',
        label='New customer discount',
        amount=-500,  # -$5.00 discount
        order=order1
    )
    db.session.add(adj1)

    adj2 = Adjustment(
        id=2,
        type='shipping',
        label='Express processing fee',
        amount=1500,  # $15.00 fee
        order=order1
    )
    db.session.add(adj2)

    adj3 = Adjustment(
        id=3,
        type='tax',
        label='Transaction tax',
        amount=2675,  # $26.75 tax
        order=order2
    )
    db.session.add(adj3)

    # Create GUEST orders (no user association - simulating Sylius guest checkout)
    # These are the sensitive orders that should not be publicly accessible
    
    guest_order1 = Order(
        id='400001',
        token_value='guest-' + str(uuid.uuid4()),
        user=None,  # Guest order - no user
        date='05/16/2024',
        ticker='AAPL',
        operation_type='BUY',
        quantity='200',
        price='34000',
        receipt='Guest Order: 200 shares of AAPL purchased. Customer: alice.guest@email.com',
        customer_email='alice.guest@email.com'
    )
    db.session.add(guest_order1)

    adj4 = Adjustment(
        id=4,
        type='order_promotion',
        label='First time buyer discount',
        amount=-1000,  # -$10.00 discount
        order=guest_order1
    )
    db.session.add(adj4)

    guest_order2 = Order(
        id='400002',
        token_value='guest-' + str(uuid.uuid4()),
        user=None,  # Guest order - no user
        date='05/16/2024',
        ticker='GOOGL',
        operation_type='SELL',
        quantity='50',
        price='7000',
        receipt='Guest Order: 50 shares of GOOGL sold. Customer: bob.guest@email.com',
        customer_email='bob.guest@email.com'
    )
    db.session.add(guest_order2)

    adj5 = Adjustment(
        id=5,
        type='tax',
        label='Capital gains tax',
        amount=700,  # $7.00 tax
        order=guest_order2
    )
    db.session.add(adj5)

    # The FLAG order - a sensitive guest order containing the flag
    # This simulates a guest customer's confidential order data
    with open('/flag') as flag_file:
        flag_content = flag_file.read()
    
    flag_order = Order(
        id='400007',
        token_value='guest-secret-7f3a2b1c',  # Predictable token for the flag order
        user=None,  # Guest order
        date='05/16/2024',
        ticker='SECRET',
        operation_type='BUY',
        quantity='1',
        price='100',
        receipt=flag_content,  # The flag is stored here
        customer_email='confidential@internal.corp'
    )
    db.session.add(flag_order)

    # Adjustment for the flag order - this is the key vulnerability entry point
    # The adjustment's order token can be enumerated to access the flag order
    adj6 = Adjustment(
        id=7,  # ID 7 - the attacker will find this by enumeration
        type='order_promotion',
        label='Special internal discount',
        amount=-100,
        order=flag_order
    )
    db.session.add(adj6)

    db.session.commit()

# Include routes
from app import routes
