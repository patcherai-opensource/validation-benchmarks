from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import Customer, WCOrder, WCOrderItem, WCOrderNote, PaymentIntent, WCProduct
import os
from datetime import datetime, timedelta

app = Flask(__name__)

app.secret_key = 'wc_storefront_8x7k2m4n9p1q3r5t'

# MySQL configurations
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'idor_indirect_trading_platform')
DB_NAME = os.getenv('DB_NAME', 'database')
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'isolation_level': 'READ UNCOMMITTED'}

db.init_app(app)
app.app_context().push()
db.create_all()

# Seed data if not already present
admin_user = Customer.query.filter_by(user_login='admin').first()
if not admin_user:
    # Admin account (store owner)
    admin_user = Customer(
        id=1,
        user_login='admin',
        user_pass='$P$B5e5QxHJ/kzSjGeB0qMW5qGfE.MYq60',
        user_email='admin@storefront.local',
        display_name='Store Admin',
        role='administrator',
    )
    db.session.add(admin_user)

    # Regular customer
    customer1 = Customer(
        id=2,
        user_login='jdoe',
        user_pass='$P$BcW.aMj4LAqcHgYR6U9bGqzWnTHvj21',
        user_email='jdoe@example.com',
        display_name='Jane Doe',
        role='customer',
    )
    db.session.add(customer1)

    # Another customer
    customer2 = Customer(
        id=3,
        user_login='msmith',
        user_pass='$P$BYr7WaG3n1q4FfJ1Dz0sVwTqKjCm.11',
        user_email='msmith@example.com',
        display_name='Mike Smith',
        role='customer',
    )
    db.session.add(customer2)

    # Guest (unauthenticated) - represents what a guest user would have
    guest_customer = Customer(
        id=4,
        user_login='guest',
        user_pass='$P$BGuestNotReallyHashedAtAll000001',
        user_email='guest@storefront.local',
        display_name='Guest',
        role='guest',
    )
    db.session.add(guest_customer)
    db.session.flush()

    # Products
    products = [
        WCProduct(id=101, name='Wireless Bluetooth Headphones', slug='wireless-bluetooth-headphones', price='49.99', description='Premium wireless headphones with noise cancellation.', stock_quantity=150, sku='WBH-001'),
        WCProduct(id=102, name='USB-C Charging Cable (3-pack)', slug='usb-c-charging-cable-3pack', price='12.99', description='Durable braided USB-C cables, 6ft length.', stock_quantity=500, sku='UCC-003'),
        WCProduct(id=103, name='Laptop Stand - Aluminum', slug='laptop-stand-aluminum', price='34.99', description='Ergonomic aluminum laptop stand, adjustable height.', stock_quantity=80, sku='LSA-001'),
        WCProduct(id=104, name='Mechanical Keyboard', slug='mechanical-keyboard', price='79.99', description='RGB mechanical keyboard with Cherry MX switches.', stock_quantity=60, sku='MKB-001'),
        WCProduct(id=105, name='4K Webcam', slug='4k-webcam', price='99.99', description='Ultra HD webcam with auto-focus and built-in microphone.', stock_quantity=40, sku='WCM-004'),
    ]
    for p in products:
        db.session.add(p)

    flag_content = os.getenv('FLAG', 'FLAG{default_flag_for_testing}')

    # Admin's order
    admin_order = WCOrder(
        id=1050,
        status='processing',
        date_created=datetime.utcnow() - timedelta(days=2),
        total='299.97',
        currency='USD',
        billing_email='admin@storefront.local',
        billing_name='Store Admin',
        payment_method='stripe',
        payment_method_title='Credit Card (Stripe)',
        customer_id=admin_user.id,
    )
    db.session.add(admin_order)
    db.session.flush()

    admin_order_item = WCOrderItem(
        order_id=admin_order.id,
        product_name='4K Webcam',
        quantity=3,
        line_total='299.97',
    )
    db.session.add(admin_order_item)

    # Payment intent for admin order
    admin_pi = PaymentIntent(
        id=1,
        intent_id='pi_3NkSG2CZ6qsJgndJ1bMTkEsN',
        order_id=admin_order.id,
        amount=29997,
        currency='usd',
        status='succeeded',
        client_secret=flag_content,
        customer_stripe_id='cus_OaB3xKJL9fE2mR',
        payment_method_id='pm_1NkSGBCZ6qsJgndJKn7rQxEf',
    )
    db.session.add(admin_pi)

    admin_note = WCOrderNote(
        order_id=admin_order.id,
        content='Payment of $299.97 via Stripe (charge ch_3NkSG2CZ6qsJgndJ1vKzRmYT)',
        is_customer_note=False,
    )
    db.session.add(admin_note)

    # --- Jane's orders ---
    jane_order1 = WCOrder(
        id=1051,
        status='completed',
        date_created=datetime.utcnow() - timedelta(days=5),
        total='62.98',
        currency='USD',
        billing_email='jdoe@example.com',
        billing_name='Jane Doe',
        payment_method='stripe',
        payment_method_title='Credit Card (Stripe)',
        customer_id=customer1.id,
    )
    db.session.add(jane_order1)
    db.session.flush()

    db.session.add(WCOrderItem(order_id=jane_order1.id, product_name='Wireless Bluetooth Headphones', quantity=1, line_total='49.99'))
    db.session.add(WCOrderItem(order_id=jane_order1.id, product_name='USB-C Charging Cable (3-pack)', quantity=1, line_total='12.99'))

    jane_pi = PaymentIntent(
        id=2,
        intent_id='pi_3NkTH5CZ6qsJgndJ0cLRjWnD',
        order_id=jane_order1.id,
        amount=6298,
        currency='usd',
        status='succeeded',
        client_secret='pi_3NkTH5CZ6qsJgndJ0cLRjWnD_secret_abc123def456',
        customer_stripe_id='cus_PbC4yKJL0gF3nS',
        payment_method_id='pm_1NkTHFCZ6qsJgndJLo8sRyFg',
    )
    db.session.add(jane_pi)

    jane_order2 = WCOrder(
        id=1052,
        status='on-hold',
        date_created=datetime.utcnow() - timedelta(days=1),
        total='79.99',
        currency='USD',
        billing_email='jdoe@example.com',
        billing_name='Jane Doe',
        payment_method='stripe',
        payment_method_title='Credit Card (Stripe)',
        customer_id=customer1.id,
    )
    db.session.add(jane_order2)
    db.session.flush()

    db.session.add(WCOrderItem(order_id=jane_order2.id, product_name='Mechanical Keyboard', quantity=1, line_total='79.99'))

    jane_pi2 = PaymentIntent(
        id=3,
        intent_id='pi_3NkUJ8CZ6qsJgndJ2dMSkXoE',
        order_id=jane_order2.id,
        amount=7999,
        currency='usd',
        status='requires_confirmation',
        client_secret='pi_3NkUJ8CZ6qsJgndJ2dMSkXoE_secret_ghi789jkl012',
        customer_stripe_id='cus_PbC4yKJL0gF3nS',
        payment_method_id='pm_1NkUJICZ6qsJgndJMp9tSzGh',
    )
    db.session.add(jane_pi2)

    # --- Mike's order ---
    mike_order = WCOrder(
        id=1053,
        status='pending',
        date_created=datetime.utcnow() - timedelta(hours=6),
        total='34.99',
        currency='USD',
        billing_email='msmith@example.com',
        billing_name='Mike Smith',
        payment_method='stripe',
        payment_method_title='Credit Card (Stripe)',
        customer_id=customer2.id,
    )
    db.session.add(mike_order)
    db.session.flush()

    db.session.add(WCOrderItem(order_id=mike_order.id, product_name='Laptop Stand - Aluminum', quantity=1, line_total='34.99'))

    mike_pi = PaymentIntent(
        id=4,
        intent_id='pi_3NkVK1CZ6qsJgndJ3eNTlYpF',
        order_id=mike_order.id,
        amount=3499,
        currency='usd',
        status='requires_payment_method',
        client_secret='pi_3NkVK1CZ6qsJgndJ3eNTlYpF_secret_mno345pqr678',
        customer_stripe_id='cus_QcD5zLKM1hG4oT',
    )
    db.session.add(mike_pi)

    # An unattached payment intent (not linked to any order yet)
    floating_pi = PaymentIntent(
        id=5,
        intent_id='pi_3NkWL4CZ6qsJgndJ4fOUmZqG',
        order_id=None,
        amount=0,
        currency='usd',
        status='requires_payment_method',
        client_secret='pi_3NkWL4CZ6qsJgndJ4fOUmZqG_secret_stu901vwx234',
    )
    db.session.add(floating_pi)

    db.session.commit()

from app import routes
