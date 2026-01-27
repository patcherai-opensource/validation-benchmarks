from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User, Device, ApiToken, SystemSecret

import random
import string
import hashlib

app = Flask(__name__)

app.secret_key = 'netmon_secret_key_2024'

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
    # Create admin user
    admin = User(
        id='1',
        username='admin',
        password='admin123',
        first_name='System',
        last_name='Administrator',
        email='admin@netmon.local',
        level=10
    )
    db.session.add(admin)
    db.session.commit()
    
    # Create API token for admin
    admin_token = ApiToken(
        id='1',
        token='a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6',
        user_id=admin.id,
        description='Admin API Token'
    )
    db.session.add(admin_token)

# Create demo user for testing
demo = User.query.filter_by(username='demo').first()
if not demo:
    demo = User(
        id='100',
        username='demo',
        password='demo',
        first_name='Demo',
        last_name='User',
        email='demo@netmon.local',
        level=1
    )
    db.session.add(demo)
    db.session.commit()
    
    # Create API token for demo user - this is what attackers will discover
    demo_token = ApiToken(
        id='100',
        token='d3m0t0k3n4ap1acc3ss2024x9y8z7w6',
        user_id=demo.id,
        description='Demo API Token'
    )
    db.session.add(demo_token)

# Create sample network devices
devices_exist = Device.query.first()
if not devices_exist:
    devices = [
        Device(
            id='1',
            device_id=1001,
            hostname='core-router-01',
            sysname='Cisco IOS XE',
            ip='192.168.1.1',
            status=1,
            os='IOS-XE 17.3',
            hardware='Cisco C9300',
            location='Data Center A - Rack 1',
            uptime=8640000,
            user_id=admin.id
        ),
        Device(
            id='2',
            device_id=1002,
            hostname='switch-floor1',
            sysname='Catalyst Switch',
            ip='192.168.1.10',
            status=1,
            os='IOS 15.2',
            hardware='Cisco WS-C3850',
            location='Building 1 - Floor 1',
            uptime=7200000,
            user_id=admin.id
        ),
        Device(
            id='3',
            device_id=1003,
            hostname='firewall-main',
            sysname='pfSense',
            ip='192.168.1.254',
            status=1,
            os='FreeBSD 12.2',
            hardware='Netgate SG-5100',
            location='Data Center A - Rack 2',
            uptime=6048000,
            user_id=admin.id
        ),
        Device(
            id='4',
            device_id=1004,
            hostname='ap-lobby',
            sysname='Ubiquiti AP',
            ip='192.168.2.50',
            status=0,
            os='UniFi 6.0',
            hardware='UAP-AC-PRO',
            location='Building 1 - Lobby',
            uptime=0,
            user_id=demo.id if demo else admin.id
        ),
        Device(
            id='5',
            device_id=1005,
            hostname='server-web01',
            sysname='Linux Server',
            ip='192.168.10.100',
            status=1,
            os='Ubuntu 22.04',
            hardware='Dell PowerEdge R740',
            location='Data Center A - Rack 5',
            uptime=5184000,
            user_id=admin.id
        ),
    ]
    for device in devices:
        db.session.add(device)
    
    # Store the flag as a system secret in the database
    with open('/flag') as flag_file:
        flag_content = flag_file.read()
    
    secret = SystemSecret(
        id='1',
        key_name='snmp_community',
        secret_value=flag_content
    )
    db.session.add(secret)
    
    # Add some decoy secrets too
    decoys = [
        SystemSecret(id='2', key_name='backup_password', secret_value='B@ckup2024!Secure'),
        SystemSecret(id='3', key_name='api_master_key', secret_value='mk_9f8e7d6c5b4a3210'),
        SystemSecret(id='4', key_name='ldap_bind_password', secret_value='Ldap$ecureP@ss'),
    ]
    for decoy in decoys:
        db.session.add(decoy)
    
    db.session.commit()

# Include routes
from app import routes
