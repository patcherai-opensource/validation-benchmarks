from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User, Order, PaymentIntent

import random
import string
import hashlib

app = Flask(__name__)

app.secret_key = 'wc_stripe_payment_gateway_secret'

# MySQL configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:idor_broken_authz_trading_platform@localhost/database'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create the database tables
db.init_app(app)
app.app_context().push()
db.create_all()

# Check if admin user already exists in the database
admin = User.query.filter_by(username='admin').first()
if not admin:
    # Create admin user (store owner)
    admin = User(
        id='1001',
        username='admin',
        password='Str0ngP@ssw0rd!2024',
        first_name='Store',
        last_name='Admin',
        email='admin@luxurystore.local',
    )
    db.session.add(admin)
    db.session.commit()

# Check if customer user already exists in the database
customer = User.query.filter_by(username='customer').first()
if not customer:
    # Create a customer user 
    customer = User(
        id='2001',
        username='customer',
        password='customer123',
        first_name='Alice',
        last_name='Johnson',
        email='alice.johnson@example.com',
    )
    db.session.add(customer)
    db.session.commit()

    # Create some orders for the customer
    order1 = Order(
        id='5001',
        user=customer,
        date='2024-01-15',
        product_name='Designer Handbag',
        quantity='1',
        price='299.99',
        status='completed',
        payment_intent_id='pi_customer_5001_abc123'
    )
    db.session.add(order1)

    order2 = Order(
        id='5002',
        user=customer,
        date='2024-01-20',
        product_name='Leather Wallet',
        quantity='2',
        price='89.99',
        status='completed',
        payment_intent_id='pi_customer_5002_def456'
    )
    db.session.add(order2)
    
    order3 = Order(
        id='5003',
        user=customer,
        date='2024-02-01',
        product_name='Premium Watch',
        quantity='1',
        price='599.00',
        status='pending',
        payment_intent_id='pi_customer_5003_ghi789'
    )
    db.session.add(order3)
    db.session.commit()

# Create special VIP order with flag - belonging to admin
# This order has the flag as a special "redemption code" that is revealed
# only when payment status is changed to 'refunded'
vip_order = Order.query.filter_by(id='9999').first()
if not vip_order:
    with open('/flag') as flag_file:
        flag_content = flag_file.read()
    
    vip_order = Order(
        id='9999',
        user_id='1001',  # belongs to admin
        date='2024-02-10',
        product_name='VIP Membership - Lifetime',
        quantity='1',
        price='9999.99',
        status='completed',
        payment_intent_id='pi_vip_9999_secret',
        redemption_code=flag_content
    )
    db.session.add(vip_order)
    db.session.commit()

# Create some payment intents
pi1 = PaymentIntent.query.filter_by(intent_id='pi_customer_5001_abc123').first()
if not pi1:
    pi1 = PaymentIntent(
        intent_id='pi_customer_5001_abc123',
        order_id='5001',
        amount=29999,
        currency='usd',
        status='succeeded'
    )
    db.session.add(pi1)

    pi2 = PaymentIntent(
        intent_id='pi_customer_5002_def456',
        order_id='5002',
        amount=17998,
        currency='usd',
        status='succeeded'
    )
    db.session.add(pi2)
    
    pi3 = PaymentIntent(
        intent_id='pi_customer_5003_ghi789',
        order_id='5003',
        amount=59900,
        currency='usd',
        status='requires_payment_method'
    )
    db.session.add(pi3)
    
    # VIP payment intent
    pi_vip = PaymentIntent(
        intent_id='pi_vip_9999_secret',
        order_id='9999',
        amount=999999,
        currency='usd',
        status='succeeded'
    )
    db.session.add(pi_vip)
    db.session.commit()

# Include routes
from app import routes
