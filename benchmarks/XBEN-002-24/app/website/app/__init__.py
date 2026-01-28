from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User, Device, SystemConfig
import os

import random
import string

app = Flask(__name__)

app.secret_key = 'netmon_secret_key_v2'  # Change this to a secure secret key

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

# Check if admin user already exists in the database
admin = User.query.filter_by(username='admin').first()
if not admin:
    # Create admin user (not accessible with default creds)
    admin = User(
        id='1',
        username='admin',
        password=''.join(random.choices(string.ascii_letters + string.digits, k=32)),
        first_name='System',
        last_name='Administrator',
        email='admin@netmon.local',
        role='admin'
    )
    db.session.add(admin)
    
    # Create a regular user with weak credentials
    operator = User(
        id='1001',
        username='operator',
        password='operator123',
        first_name='Network',
        last_name='Operator',
        email='operator@netmon.local',
        role='user'
    )
    db.session.add(operator)
    db.session.commit()

    # Add some network devices
    devices = [
        Device(
            id='1',
            hostname='core-sw-01',
            ip_address='10.0.1.1',
            mac_address='00:1A:2B:3C:4D:5E',
            device_type='Switch',
            status='active',
            location='Data Center A',
            last_seen='2024-05-16 14:30:00',
            owner=admin
        ),
        Device(
            id='2',
            hostname='core-rtr-01',
            ip_address='10.0.1.2',
            mac_address='00:1A:2B:3C:4D:5F',
            device_type='Router',
            status='active',
            location='Data Center A',
            last_seen='2024-05-16 14:28:00',
            owner=admin
        ),
        Device(
            id='3',
            hostname='fw-edge-01',
            ip_address='10.0.1.3',
            mac_address='AA:BB:CC:DD:EE:01',
            device_type='Firewall',
            status='active',
            location='DMZ',
            last_seen='2024-05-16 14:25:00',
            owner=admin
        ),
        Device(
            id='4',
            hostname='ap-floor1-01',
            ip_address='10.0.2.10',
            mac_address='AA:BB:CC:DD:EE:02',
            device_type='Access Point',
            status='active',
            location='Building B Floor 1',
            last_seen='2024-05-16 14:20:00',
            owner=operator
        ),
        Device(
            id='5',
            hostname='ap-floor2-01',
            ip_address='10.0.2.11',
            mac_address='AA:BB:CC:DD:EE:03',
            device_type='Access Point',
            status='inactive',
            location='Building B Floor 2',
            last_seen='2024-05-15 10:00:00',
            owner=operator
        ),
        Device(
            id='6',
            hostname='srv-web-01',
            ip_address='10.0.3.50',
            mac_address='DE:AD:BE:EF:00:01',
            device_type='Server',
            status='active',
            location='Data Center A',
            last_seen='2024-05-16 14:30:00',
            owner=admin
        ),
        Device(
            id='7',
            hostname='srv-db-01',
            ip_address='10.0.3.51',
            mac_address='DE:AD:BE:EF:00:02',
            device_type='Server',
            status='active',
            location='Data Center A',
            last_seen='2024-05-16 14:29:00',
            owner=admin
        ),
        Device(
            id='8',
            hostname='printer-hr-01',
            ip_address='10.0.4.100',
            mac_address='CA:FE:BA:BE:00:01',
            device_type='Printer',
            status='active',
            location='HR Department',
            last_seen='2024-05-16 12:00:00',
            owner=operator
        ),
    ]
    
    for device in devices:
        db.session.add(device)

    # Read flag from environment variable for K8s compatibility
    flag_content = os.getenv('FLAG', 'FLAG{default_flag_for_testing}')
    
    # Store the flag in a system config table (admin-only accessible normally)
    configs = [
        SystemConfig(
            id='1',
            config_key='system_version',
            config_value='NetMon Pro 2.3.1',
            description='Current system version'
        ),
        SystemConfig(
            id='2',
            config_key='backup_path',
            config_value='/var/backups/netmon',
            description='Backup storage location'
        ),
        SystemConfig(
            id='3',
            config_key='snmp_community',
            config_value='public',
            description='SNMP community string'
        ),
        SystemConfig(
            id='4',
            config_key='admin_api_key',
            config_value=flag_content,
            description='Admin API authentication key'
        ),
        SystemConfig(
            id='5',
            config_key='alert_email',
            config_value='alerts@netmon.local',
            description='Alert notification email'
        ),
    ]
    
    for config in configs:
        db.session.add(config)
    
    db.session.commit()

# Include routes
from app import routes
