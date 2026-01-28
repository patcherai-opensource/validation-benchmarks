from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User, VirtualServer
import os

import random
import string

app = Flask(__name__)

app.secret_key = 'vps_control_panel_secret_2024'

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

# Check if demo user already exists in the database
demo = User.query.filter_by(username='demo').first()
if not demo:
    # Create demo user for testing
    demo = User(
        id='10032',
        username='demo',
        password='cloudvps2024',
        first_name='Alex',
        last_name='Thompson',
        email='alex.thompson@cloudvps.local',
    )
    db.session.add(demo)
    db.session.commit()

    # Demo user's VPS instances
    server = VirtualServer(
        id='1001',
        owner=demo,
        hostname='web-prod-01',
        ip_address='10.50.12.101',
        os_template='Ubuntu 22.04 LTS',
        vcpu=2,
        ram_mb=4096,
        disk_gb=80,
        status='running',
        transferred=False,
        created_at='2024-01-15',
        root_password='r00tP@ss!2024_web01'
    )
    db.session.add(server)

    server = VirtualServer(
        id='1002',
        owner=demo,
        hostname='db-staging-01',
        ip_address='10.50.12.102',
        os_template='CentOS 8 Stream',
        vcpu=4,
        ram_mb=8192,
        disk_gb=200,
        status='running',
        transferred=False,
        created_at='2024-02-20',
        root_password='db$taging_R00t#2024'
    )
    db.session.add(server)

    server = VirtualServer(
        id='1003',
        owner=demo,
        hostname='backup-srv-01',
        ip_address='10.50.12.103',
        os_template='Debian 11',
        vcpu=1,
        ram_mb=2048,
        disk_gb=500,
        status='stopped',
        transferred=False,
        created_at='2024-03-05',
        root_password='bkup_Server_P@ss123'
    )
    db.session.add(server)

    server = VirtualServer(
        id='1004',
        owner=demo,
        hostname='dev-test-01',
        ip_address='10.50.12.104',
        os_template='Ubuntu 20.04 LTS',
        vcpu=2,
        ram_mb=4096,
        disk_gb=40,
        status='running',
        transferred=True,
        manager=demo,
        created_at='2023-11-10',
        root_password='D3vT3st_r00t!Pass'
    )
    db.session.add(server)

    # Read flag from environment variable for K8s compatibility
    flag_content = os.getenv('FLAG', 'FLAG{default_flag_for_testing}')
    
    # Admin's server containing the flag as root password - NOT owned by demo user
    server = VirtualServer(
        id='1337',
        hostname='admin-secrets-01',
        ip_address='10.50.12.200',
        os_template='Alpine Linux 3.18',
        vcpu=1,
        ram_mb=512,
        disk_gb=10,
        status='running',
        transferred=False,
        created_at='2023-06-01',
        root_password=flag_content
    )
    db.session.add(server)
    db.session.commit()

# Include routes
from app import routes
