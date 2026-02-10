from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User, Organization, Event
import os

import random
import string
import secrets

app = Flask(__name__)

app.secret_key = secrets.token_hex(32)

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

# Check if organizations already exist
org1 = Organization.query.filter_by(name='Acme Events').first()
if not org1:
    # Create organizations (multi-tenant setup)
    org1 = Organization(
        id=1,
        name='Acme Events',
        description='Premier event management company'
    )
    db.session.add(org1)
    
    org2 = Organization(
        id=2,
        name='Global Conferences Inc',
        description='International conference organizer'
    )
    db.session.add(org2)
    db.session.commit()
    
    # Create users for Organization 1 (Acme Events)
    admin_user = User(
        id=10032,
        username='operator',
        password='operator123',
        first_name='John',
        last_name='Smith',
        email='john.smith@acme-events.com',
        role='operator',
        enabled=True,
        api_key='ak_acme_' + secrets.token_hex(16),
        organization=org1
    )
    db.session.add(admin_user)
    
    support_user = User(
        id=10033,
        username='support',
        password='support456',
        first_name='Jane',
        last_name='Doe',
        email='jane.doe@acme-events.com',
        role='operator',
        enabled=True,
        api_key='ak_acme_' + secrets.token_hex(16),
        organization=org1
    )
    db.session.add(support_user)
    
    # Create users for Organization 2 (Global Conferences Inc)
    api_key_value = os.getenv('FLAG', 'ak_global_system_default_key')
    
    system_admin = User(
        id=20001,
        username='sysadmin',
        password=secrets.token_hex(32),
        first_name='System',
        last_name='Administrator',
        email='sysadmin@globalconf.com',
        role='admin',
        enabled=True,
        api_key=api_key_value,
        organization=org2
    )
    db.session.add(system_admin)
    
    conf_manager = User(
        id=20002,
        username='confmanager',
        password=secrets.token_hex(32),
        first_name='Conference',
        last_name='Manager',
        email='manager@globalconf.com',
        role='operator',
        enabled=True,
        api_key='ak_global_' + secrets.token_hex(16),
        organization=org2
    )
    db.session.add(conf_manager)
    
    # Create events for Organization 1
    event1 = Event(
        id=1001,
        name='Tech Summit 2024',
        date='2024-06-15',
        location='San Francisco Convention Center',
        capacity=500,
        tickets_sold=342,
        price=299.00,
        organization=org1
    )
    db.session.add(event1)
    
    event2 = Event(
        id=1002,
        name='Developer Conference',
        date='2024-07-20',
        location='Seattle Tech Hub',
        capacity=300,
        tickets_sold=156,
        price=199.00,
        organization=org1
    )
    db.session.add(event2)
    
    event3 = Event(
        id=1003,
        name='Startup Pitch Night',
        date='2024-08-10',
        location='New York Innovation Center',
        capacity=150,
        tickets_sold=89,
        price=49.00,
        organization=org1
    )
    db.session.add(event3)
    
    # Create events for Organization 2
    event4 = Event(
        id=2001,
        name='Global Business Forum',
        date='2024-09-05',
        location='London ExCeL Center',
        capacity=1000,
        tickets_sold=678,
        price=599.00,
        organization=org2
    )
    db.session.add(event4)
    
    event5 = Event(
        id=2002,
        name='International Trade Show',
        date='2024-10-12',
        location='Tokyo Big Sight',
        capacity=2000,
        tickets_sold=1245,
        price=399.00,
        organization=org2
    )
    db.session.add(event5)
    
    db.session.commit()

# Include routes
from app import routes
