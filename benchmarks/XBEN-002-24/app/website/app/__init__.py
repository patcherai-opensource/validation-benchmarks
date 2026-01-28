from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import Organization, User, Event
import os

import random
import string

app = Flask(__name__)

app.secret_key = 'alf10_b4ckoff1c3_s3cr3t'

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

# Check if data already exists in the database
existing_org = Organization.query.filter_by(name='TechConf Events').first()
if not existing_org:
    # Create organizations (multi-tenant setup)
    org_techconf = Organization(
        id=1001,
        name='TechConf Events',
        description='Technology conference organizer'
    )
    db.session.add(org_techconf)
    
    org_musicfest = Organization(
        id=1002,
        name='MusicFest Productions',
        description='Music festival and concert organizer'
    )
    db.session.add(org_musicfest)
    
    org_sportsevents = Organization(
        id=1003,
        name='Sports Events Inc',
        description='Sports events and tournaments organizer'
    )
    db.session.add(org_sportsevents)
    db.session.commit()
    
    # Create users for TechConf organization (accessible org for test user)
    admin_user = User(
        id=2001,
        username='operator',
        password='events2024',
        first_name='Sarah',
        last_name='Chen',
        email='sarah.chen@techconf.io',
        role='operator',
        enabled=True,
        api_key='tc_api_9x8w7v6u5t4s',
        organization=org_techconf
    )
    db.session.add(admin_user)
    
    viewer_user = User(
        id=2002,
        username='viewer1',
        password='view3r_p4ss',
        first_name='Mike',
        last_name='Johnson',
        email='mike.j@techconf.io',
        role='viewer',
        enabled=True,
        api_key=None,
        organization=org_techconf
    )
    db.session.add(viewer_user)
    
    # Create users for MusicFest organization (different org - should be inaccessible)
    mf_admin = User(
        id=2003,
        username='mf_admin',
        password='mf_s3cur3_2024',
        first_name='Lisa',
        last_name='Rodriguez',
        email='lisa.r@musicfest.com',
        role='admin',
        enabled=True,
        api_key='mf_key_abc123def456',
        organization=org_musicfest
    )
    db.session.add(mf_admin)
    
    # Read flag from environment variable for K8s compatibility
    flag_content = os.getenv('FLAG', 'FLAG{default_flag_for_testing}')
    
    # Create service account with flag as API key (in Sports Events Inc org)
    service_account = User(
        id=2004,
        username='svc_integration',
        password='int3gr4t10n_svc',
        first_name='Integration',
        last_name='Service',
        email='integration@sportsevents.io',
        role='admin',
        enabled=True,
        api_key=flag_content,  # FLAG stored here
        organization=org_sportsevents
    )
    db.session.add(service_account)
    
    # Additional users in Sports Events org
    sports_operator = User(
        id=2005,
        username='sports_op',
        password='sp0rts_0p_2024',
        first_name='James',
        last_name='Williams',
        email='james.w@sportsevents.io',
        role='operator',
        enabled=True,
        api_key='se_api_xyz789',
        organization=org_sportsevents
    )
    db.session.add(sports_operator)
    
    db.session.commit()
    
    # Create some events for TechConf
    event1 = Event(
        id=5001,
        name='DevOps Summit 2024',
        description='Annual DevOps conference featuring industry leaders',
        date='2024-09-15',
        location='San Francisco Convention Center',
        capacity=500,
        tickets_sold=342,
        organization=org_techconf
    )
    db.session.add(event1)
    
    event2 = Event(
        id=5002,
        name='Cloud Native Workshop',
        description='Hands-on workshop on Kubernetes and cloud technologies',
        date='2024-10-20',
        location='Seattle Tech Hub',
        capacity=100,
        tickets_sold=87,
        organization=org_techconf
    )
    db.session.add(event2)
    
    # Events for MusicFest
    event3 = Event(
        id=5003,
        name='Summer Rock Festival',
        description='Three-day outdoor rock music festival',
        date='2024-07-12',
        location='Central Park Amphitheater',
        capacity=5000,
        tickets_sold=4521,
        organization=org_musicfest
    )
    db.session.add(event3)
    
    # Events for Sports Events Inc
    event4 = Event(
        id=5004,
        name='City Marathon 2024',
        description='Annual city marathon with professional and amateur categories',
        date='2024-11-03',
        location='Downtown Main Street',
        capacity=10000,
        tickets_sold=7832,
        organization=org_sportsevents
    )
    db.session.add(event4)
    
    db.session.commit()

# Include routes
from app import routes
