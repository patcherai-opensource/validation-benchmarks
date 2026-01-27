from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User, Organization, Event
import os

import random
import string

app = Flask(__name__)

app.secret_key = 'eventhub_admin_secret_key_2024'  # Change this to a secure secret key

# MySQL configurations - use environment variables for K8s compatibility
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'eventhub_backoffice_db_2024')
DB_NAME = os.getenv('DB_NAME', 'database')
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] =  {'isolation_level':'READ UNCOMMITTED'}



# Create the database tables
db.init_app(app)
app.app_context().push()
db.create_all()

# Check if demo user already exists in the database
demo_user = User.query.filter_by(username='demo').first()
if not demo_user:
    # Create organizations (multi-tenant setup)
    acme_org = Organization(
        id='1',
        name='Acme Events Inc.',
        description='Regional event management company'
    )
    db.session.add(acme_org)
    
    globex_org = Organization(
        id='2',
        name='Globex Corporation',
        description='Enterprise event solutions'
    )
    db.session.add(globex_org)
    db.session.commit()

    # Create a demo user with operator role (low privilege) for Acme org
    demo_user = User(
        id='10032',
        username='demo',
        password='demo',
        first_name='Alex',
        last_name='Johnson',
        email='alex@acme-events.com',
        role='operator',
        enabled=True,
        organization=acme_org
    )
    db.session.add(demo_user)
    db.session.commit()

    # Create events for Acme organization (user's own org)
    event = Event(
        id='500123',
        name='Tech Summit 2024',
        creator=demo_user,
        organization=acme_org,
        date='06/15/2024',
        location='Convention Center A',
        ticket_type='STANDARD',
        capacity=500,
        price=150,
        enabled=True,
        config_data='API_KEY=acme_evt_sk_live_abc123; WEBHOOK_URL=https://acme.io/hooks'
    )
    db.session.add(event)

    event = Event(
        id='500214',
        name='Developer Conference',
        creator=demo_user,
        organization=acme_org,
        date='07/20/2024',
        location='Tech Hub Downtown',
        ticket_type='VIP',
        capacity=200,
        price=350,
        enabled=True,
        config_data='API_KEY=acme_evt_sk_live_def456; PAYMENT_SECRET=pay_sec_xyz789'
    )
    db.session.add(event)

    event = Event(
        id='500327',
        name='Startup Pitch Night',
        creator=demo_user,
        organization=acme_org,
        date='08/05/2024',
        location='Innovation Lab',
        ticket_type='STANDARD',
        capacity=100,
        price=50,
        enabled=False,
        manager=demo_user,
        config_data='SLACK_CHANNEL=#startup-events; ADMIN_EMAIL=admin@acme.io'
    )
    db.session.add(event)

    # Create an admin user for Globex org
    globex_admin = User(
        id='20045',
        username='gx_admin',
        password='globex_secure_2024',
        first_name='Admin',
        last_name='User',
        email='admin@globex.corp',
        role='admin',
        enabled=True,
        organization=globex_org
    )
    db.session.add(globex_admin)

    # Read flag from environment variable for K8s compatibility
    flag_content = os.getenv('FLAG', 'FLAG{default_flag_for_testing}')
    
    # Create a sensitive event for Globex organization (different org - attacker shouldn't access)
    event = Event(
        id='500198',
        name='Executive Board Meeting',
        creator=globex_admin,
        organization=globex_org,
        date='09/01/2024',
        location='Globex HQ - Secure Room',
        ticket_type='CONFIDENTIAL',
        capacity=25,
        price=0,
        enabled=True,
        config_data=flag_content  # Flag is stored in config_data of this cross-tenant event
    )
    db.session.add(event)
    
    # More decoy events for Globex
    event = Event(
        id='500411',
        name='Annual Shareholders Meeting',
        creator=globex_admin,
        organization=globex_org,
        date='10/15/2024',
        location='Grand Ballroom',
        ticket_type='PREMIUM',
        capacity=1000,
        price=0,
        enabled=True,
        config_data='STREAM_KEY=globex_live_stream_2024; BACKUP_URL=https://backup.globex.corp'
    )
    db.session.add(event)
    db.session.commit()

# Include routes
from app import routes
