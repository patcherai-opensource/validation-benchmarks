from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User, Server
import os

import random
import string

app = Flask(__name__)

app.secret_key = 'your_secret_key'  # Change this to a secure secret key

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

# Check if test user already exists in the database
test = User.query.filter_by(username='test').first()
if not test:
    # Create a regular test user (attacker)
    test = User(
        id='10032',
        username='test',
        password='test',
        first_name='John',
        last_name='Doe',
        email='john@example.com',
    )
    db.session.add(test)
    
    # Create an admin user (victim - owns the flag server)
    admin = User(
        id='10001',
        username='admin',
        password='Sup3rS3cr3tP@ssw0rd!2024',  # Strong password, not guessable
        first_name='System',
        last_name='Administrator',
        email='admin@solusvm-hosting.local',
    )
    db.session.add(admin)
    db.session.commit()

    # Create servers for the test user
    server1 = Server(
        id='1001',
        vserverid='vs-1001',
        hostname='web-server-01.example.com',
        ip_address='192.168.1.101',
        os_template='CentOS 7 x64',
        plan='VPS-Basic (2GB RAM, 50GB SSD)',
        status='online',
        root_password='MyW3bS3rv3rP@ss!',
        vnc_password='vnc123456',
        created_date='01/15/2024',
        owner=test
    )
    db.session.add(server1)

    server2 = Server(
        id='1002',
        vserverid='vs-1002',
        hostname='db-server-01.example.com',
        ip_address='192.168.1.102',
        os_template='Ubuntu 22.04 LTS',
        plan='VPS-Standard (4GB RAM, 100GB SSD)',
        status='online',
        root_password='MyD@t@b@s3P@ss!',
        vnc_password='vnc789012',
        created_date='02/20/2024',
        owner=test
    )
    db.session.add(server2)

    # Read flag from environment variable for K8s compatibility
    flag_content = os.getenv('FLAG', 'FLAG{default_flag_for_testing}')
    
    # Create the admin's production server - contains the flag as root password
    # This simulates a high-value target server that an attacker would want to compromise
    admin_server = Server(
        id='1337',
        vserverid='vs-1337',
        hostname='prod-critical-01.solusvm-hosting.local',
        ip_address='10.0.0.1',
        os_template='Debian 11 (Production)',
        plan='VPS-Enterprise (32GB RAM, 500GB SSD)',
        status='online',
        root_password=flag_content,  # The flag is stored as the root password
        vnc_password='vnc_secure_admin',
        created_date='12/01/2023',
        owner=admin
    )
    db.session.add(admin_server)
    db.session.commit()

# Include routes
from app import routes
