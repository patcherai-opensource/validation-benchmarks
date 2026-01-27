from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User, Device
import os
import time
import sys

import random
import string

app = Flask(__name__)

app.secret_key = 'netmon_secret_key_2024'  # Network monitoring secret key

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

# Wait for database to be ready (for K8s deployment)
max_retries = 30
retry_count = 0
while retry_count < max_retries:
    try:
        db.create_all()
        break
    except Exception as e:
        retry_count += 1
        print(f"Database connection attempt {retry_count}/{max_retries} failed: {e}")
        if retry_count >= max_retries:
            print("Failed to connect to database after maximum retries")
            sys.exit(1)
        time.sleep(2)

# Check if operator user already exists in the database
operator = User.query.filter_by(username='operator').first()
if not operator:
    # Create an operator user (low privilege)
    operator = User(
        id='10032',
        username='operator',
        password='operator',
        first_name='Network',
        last_name='Operator',
        email='operator@netmon.local',
        role='operator'
    )
    db.session.add(operator)
    db.session.commit()

    # Create sample network devices for the operator
    device1 = Device(
        id='1001',
        owner=operator,
        hostname='switch-floor1',
        mac_address='00:1A:2B:3C:4D:01',
        ip_address='192.168.1.10',
        device_type='switch',
        status='active',
        location='Building A - Floor 1',
        notes='24-port managed switch'
    )
    db.session.add(device1)

    device2 = Device(
        id='1002',
        owner=operator,
        hostname='router-main',
        mac_address='00:1A:2B:3C:4D:02',
        ip_address='192.168.1.1',
        device_type='router',
        status='active',
        location='Server Room',
        notes='Main gateway router'
    )
    db.session.add(device2)

    device3 = Device(
        id='1003',
        owner=operator,
        hostname='ap-conference',
        mac_address='00:1A:2B:3C:4D:03',
        ip_address='192.168.1.50',
        device_type='access_point',
        status='active',
        location='Conference Room A',
        notes='Wireless access point for guests'
    )
    db.session.add(device3)

    device4 = Device(
        id='1004',
        owner=operator,
        hostname='switch-floor2',
        mac_address='00:1A:2B:3C:4D:04',
        ip_address='192.168.2.10',
        device_type='switch',
        status='inactive',
        location='Building A - Floor 2',
        notes='Needs maintenance'
    )
    db.session.add(device4)

    # Read flag from environment variable for K8s compatibility
    # The flag is stored in a "secret" device that should only be accessible to admins
    flag_content = os.getenv('FLAG', 'FLAG{default_flag_for_testing}')
    secret_device = Device(
        id='9999',
        hostname='secret-server',
        mac_address='FF:FF:FF:FF:FF:FF',
        ip_address='10.0.0.1',
        device_type='server',
        status='restricted',
        location='Secure Zone',
        notes=flag_content
    )
    db.session.add(secret_device)
    db.session.commit()

# Include routes
from app import routes
