from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User, Order, SettlementIntent
import os
import hashlib

app = Flask(__name__)

app.secret_key = os.urandom(24).hex()

# MySQL configurations - use environment variables for K8s compatibility
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'idor_indirect_trading_platform')
DB_NAME = os.getenv('DB_NAME', 'database')
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'isolation_level': 'READ UNCOMMITTED'}


# Create the database tables
db.init_app(app)
app.app_context().push()
db.create_all()

# Read flag from environment variable for K8s compatibility
flag_content = os.getenv('FLAG', 'FLAG{default_flag_for_testing}')

# Check if data already exists in the database
test = User.query.filter_by(username='test').first()
if not test:
    # Create users
    admin = User(
        id='10001',
        username='admin',
        password=hashlib.sha256(os.urandom(32)).hexdigest(),
        first_name='Platform',
        last_name='Administrator',
        email='admin@tradingplatform.local',
    )
    db.session.add(admin)

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

    # User orders for 'test'
    order1 = Order(
        id='300123',
        creator=test,
        date='05/15/2024',
        ticker='SPY',
        operation_type='BUY',
        quantity='100',
        price='530.00',
        archived=False,
        receipt='Trade confirmation: BUY 100 SPY @ $530.00. Settlement T+2. Broker ref: TRD-300123-A.'
    )
    db.session.add(order1)

    order2 = Order(
        id='300214',
        creator=test,
        date='05/15/2024',
        ticker='SPY',
        operation_type='SELL',
        quantity='50',
        price='535.00',
        archived=False,
        receipt='Trade confirmation: SELL 50 SPY @ $535.00. Settlement T+2. Broker ref: TRD-300214-A.'
    )
    db.session.add(order2)

    order3 = Order(
        id='300327',
        creator=test,
        date='05/16/2024',
        ticker='SPY',
        operation_type='BUY',
        quantity='100',
        price='520.00',
        archived=False,
        receipt='Trade confirmation: BUY 100 SPY @ $520.00. Settlement T+2. Broker ref: TRD-300327-A.'
    )
    db.session.add(order3)

    order4 = Order(
        id='300481',
        creator=test,
        date='05/16/2024',
        ticker='SPY',
        operation_type='SELL',
        quantity='100',
        price='540.00',
        archived=True,
        archiver=test,
        receipt='Trade confirmation: SELL 100 SPY @ $540.00. Settlement T+2. Broker ref: TRD-300481-A.'
    )
    db.session.add(order4)

    # Admin-only order containing the flag as settlement confirmation
    flag_order = Order(
        id='300198',
        creator=admin,
        date='05/16/2024',
        ticker='PRIV',
        operation_type='SELL',
        quantity='1',
        price='1.00',
        archived=False,
        receipt=flag_content
    )
    db.session.add(flag_order)
    db.session.commit()

    # Create settlement intents for all orders
    settlements = [
        SettlementIntent(
            id=1,
            intent_token='si_9f3a7b2c1d4e',
            order_fk=300123,
            amount='53000.00',
            currency='USD',
            status='completed',
            payment_method='wire_transfer',
            description='Settlement for BUY 100 SPY',
            confirmation='Trade confirmation: BUY 100 SPY @ $530.00. Settlement T+2. Broker ref: TRD-300123-A.'
        ),
        SettlementIntent(
            id=2,
            intent_token='si_8e2b6a1c0d3f',
            order_fk=300214,
            amount='26750.00',
            currency='USD',
            status='completed',
            payment_method='wire_transfer',
            description='Settlement for SELL 50 SPY',
            confirmation='Trade confirmation: SELL 50 SPY @ $535.00. Settlement T+2. Broker ref: TRD-300214-A.'
        ),
        SettlementIntent(
            id=3,
            intent_token='si_7d1a5b0c9e2f',
            order_fk=300327,
            amount='52000.00',
            currency='USD',
            status='completed',
            payment_method='wire_transfer',
            description='Settlement for BUY 100 SPY',
            confirmation='Trade confirmation: BUY 100 SPY @ $520.00. Settlement T+2. Broker ref: TRD-300327-A.'
        ),
        SettlementIntent(
            id=4,
            intent_token='si_6c0a4b9d8e1f',
            order_fk=300481,
            amount='54000.00',
            currency='USD',
            status='completed',
            payment_method='wire_transfer',
            description='Settlement for SELL 100 SPY',
            confirmation='Trade confirmation: SELL 100 SPY @ $540.00. Settlement T+2. Broker ref: TRD-300481-A.'
        ),
        SettlementIntent(
            id=5,
            intent_token='si_5b9a3c8d7e0f',
            order_fk=300198,
            amount='1.00',
            currency='USD',
            status='pending',
            payment_method='internal_transfer',
            description='Settlement for SELL 1 PRIV',
            confirmation=flag_content
        ),
    ]
    for s in settlements:
        db.session.add(s)
    db.session.commit()

# Include routes
from app import routes
