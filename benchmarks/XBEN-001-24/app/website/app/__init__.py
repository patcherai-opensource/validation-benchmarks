from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User, Device, ApiToken, Secret

import random
import string

app = Flask(__name__)

app.secret_key = 'nms_secret_key_2024'  # Internal secret key

# MySQL configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:idor_broken_authz_trading_platform@localhost/database'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create the database tables
db.init_app(app)
app.app_context().push()
db.create_all()

# Check if operator already exists in the database
operator = User.query.filter_by(username='operator').first()
if not operator:
    # Create network operator user
    operator = User(
        id='10001',
        username='operator',
        password='netops2024',
        first_name='Network',
        last_name='Operator',
        email='operator@netmon.local',
    )
    db.session.add(operator)
    db.session.commit()

    # Create API token for the operator
    api_token = ApiToken(
        id=1,
        token='nm_api_4f8b2c1e9a7d3f6e5b0c8a2d',
        description='Operator API access token',
        user_id=operator.id,
        active=1
    )
    db.session.add(api_token)

    # Create additional dummy API tokens for noise
    dummy_tokens = [
        ApiToken(id=2, token='nm_api_disabled_old_token_01', description='Legacy token (disabled)', user_id=operator.id, active=0),
        ApiToken(id=3, token='nm_api_readonly_monitoring_02', description='Read-only monitoring', user_id=operator.id, active=1),
    ]
    for t in dummy_tokens:
        db.session.add(t)

    # Add network devices
    devices = [
        Device(
            id=1001,
            hostname='core-sw-01.dc1.netmon.local',
            sysname='Cisco IOS Switch',
            ip_address='10.0.1.1',
            device_type='network',
            os='ios',
            version='15.2(4)M7',
            status=1,
            uptime=8640000,
            location='DC1-Rack-A01',
            last_polled='2024-05-16 14:30:00',
            user_id=operator.id
        ),
        Device(
            id=1002,
            hostname='edge-rtr-01.dc1.netmon.local',
            sysname='Juniper Router',
            ip_address='10.0.1.2',
            device_type='network',
            os='junos',
            version='21.4R1.12',
            status=1,
            uptime=2592000,
            location='DC1-Rack-A02',
            last_polled='2024-05-16 14:30:00',
            user_id=operator.id
        ),
        Device(
            id=1003,
            hostname='fw-01.dc1.netmon.local',
            sysname='Palo Alto Firewall',
            ip_address='10.0.1.3',
            device_type='firewall',
            os='panos',
            version='10.2.3',
            status=1,
            uptime=5184000,
            location='DC1-Rack-B01',
            last_polled='2024-05-16 14:30:00',
            user_id=operator.id
        ),
        Device(
            id=1004,
            hostname='access-sw-01.floor2.netmon.local',
            sysname='HP ProCurve Switch',
            ip_address='10.0.2.1',
            device_type='network',
            os='procurve',
            version='YA.16.10.0003',
            status=0,  # Down
            uptime=0,
            location='Floor2-IDF',
            last_polled='2024-05-15 08:15:00',
            user_id=operator.id
        ),
        Device(
            id=1005,
            hostname='wlc-01.netmon.local',
            sysname='Cisco Wireless Controller',
            ip_address='10.0.3.1',
            device_type='wireless',
            os='aireos',
            version='8.10.185.0',
            status=1,
            uptime=1296000,
            location='DC1-Rack-C01',
            last_polled='2024-05-16 14:30:00',
            user_id=operator.id
        ),
    ]
    
    for device in devices:
        db.session.add(device)

    # Store the flag in the secrets table - only accessible via SQL injection
    with open('/flag') as flag_file:
        flag_content = flag_file.read()
    
    secret = Secret(
        id=1,
        key_name='system_backup_key',
        key_value=flag_content
    )
    db.session.add(secret)
    
    # Add some decoy secrets
    decoy_secrets = [
        Secret(id=2, key_name='snmp_community_ro', key_value='public'),
        Secret(id=3, key_name='snmp_community_rw', key_value='private'),
        Secret(id=4, key_name='ldap_bind_password', key_value='ldap_bind_2024!'),
    ]
    for s in decoy_secrets:
        db.session.add(s)
    
    db.session.commit()

# Include routes
from app import routes
