from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User, Instance, ActivityLog

import random
import string

app = Flask(__name__)

app.secret_key = 'a3f8c2d1e7b9045f6a2c8d3e1b7094f5'

# MySQL configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:idor_broken_authz_trading_platform@localhost/database'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create the database tables
db.init_app(app)
app.app_context().push()
db.create_all()

# Seed data
existing = User.query.filter_by(username='demo').first()
if not existing:
    # Customer account
    customer = User(
        id=1001,
        username='demo',
        password='demo',
        first_name='Marcus',
        last_name='Webb',
        email='marcus.webb@example.com',
        role='customer'
    )
    db.session.add(customer)

    # Admin / internal operations account
    admin_user = User(
        id=1002,
        username='operator',
        password=''.join(random.choices(string.ascii_letters + string.digits, k=32)),
        first_name='System',
        last_name='Operations',
        email='ops@internal.cloudmatrix.io',
        role='admin'
    )
    db.session.add(admin_user)

    # Another customer
    customer2 = User(
        id=1003,
        username='jgarcia',
        password=''.join(random.choices(string.ascii_letters + string.digits, k=24)),
        first_name='Julia',
        last_name='Garcia',
        email='julia.garcia@example.net',
        role='customer'
    )
    db.session.add(customer2)
    db.session.commit()

    # Customer instances (Marcus Webb)
    inst1 = Instance(
        id=5201,
        label='web-prod-01',
        hostname='web-prod-01.customer.cloudmatrix.io',
        ip_address='198.51.100.14',
        virt_type='kvm',
        plan='VPS-2G',
        status='online',
        root_password='Xk9#mP2$vL',
        vnc_password='vnc8821',
        node='node-us-east-03',
        os_template='ubuntu-22.04-x86_64',
        bandwidth_used=342,
        bandwidth_limit=2000,
        disk_used=18,
        disk_limit=50,
        memory_mb=2048,
        created_date='2024-01-15',
        user_id=1001
    )
    db.session.add(inst1)

    inst2 = Instance(
        id=5202,
        label='db-staging',
        hostname='db-staging.customer.cloudmatrix.io',
        ip_address='198.51.100.22',
        virt_type='kvm',
        plan='VPS-4G',
        status='online',
        root_password='Rm4&nQ7!bZ',
        vnc_password='vnc4456',
        node='node-us-east-03',
        os_template='debian-12-x86_64',
        bandwidth_used=89,
        bandwidth_limit=3000,
        disk_used=31,
        disk_limit=100,
        memory_mb=4096,
        created_date='2024-02-20',
        user_id=1001
    )
    db.session.add(inst2)

    inst3 = Instance(
        id=5203,
        label='dev-sandbox',
        hostname='dev-sandbox.customer.cloudmatrix.io',
        ip_address='198.51.100.37',
        virt_type='kvm',
        plan='VPS-1G',
        status='offline',
        root_password='Yt2@kJ5!wE',
        vnc_password='vnc7713',
        node='node-us-west-01',
        os_template='centos-9-x86_64',
        bandwidth_used=12,
        bandwidth_limit=1000,
        disk_used=8,
        disk_limit=25,
        memory_mb=1024,
        created_date='2024-03-10',
        user_id=1001
    )
    db.session.add(inst3)

    # Admin infrastructure instance - flag stored as root password
    with open('/flag') as flag_file:
        flag_content = flag_file.read().strip()

    admin_inst = Instance(
        id=5204,
        label='mgmt-controller',
        hostname='mgmt-controller.ops.cloudmatrix.io',
        ip_address='10.0.0.2',
        virt_type='kvm',
        plan='VPS-8G',
        status='online',
        root_password=flag_content,
        vnc_password=''.join(random.choices(string.ascii_lowercase + string.digits, k=8)),
        node='node-mgmt-01',
        os_template='ubuntu-22.04-x86_64',
        bandwidth_used=1205,
        bandwidth_limit=10000,
        disk_used=45,
        disk_limit=200,
        memory_mb=8192,
        created_date='2023-06-01',
        user_id=1002
    )
    db.session.add(admin_inst)

    # Julia Garcia's instance
    garcia_inst = Instance(
        id=5205,
        label='app-server',
        hostname='app-server.jgarcia.cloudmatrix.io',
        ip_address='198.51.100.48',
        virt_type='kvm',
        plan='VPS-2G',
        status='online',
        root_password='Bw8#pL3$mK',
        vnc_password='vnc3309',
        node='node-eu-west-02',
        os_template='ubuntu-22.04-x86_64',
        bandwidth_used=156,
        bandwidth_limit=2000,
        disk_used=22,
        disk_limit=50,
        memory_mb=2048,
        created_date='2024-04-05',
        user_id=1003
    )
    db.session.add(garcia_inst)

    db.session.commit()

    # Activity logs
    logs = [
        ActivityLog(instance_id=5201, action='boot', details='Instance started', timestamp='2024-05-10 08:30:00'),
        ActivityLog(instance_id=5201, action='hostname_change', details='Hostname updated to web-prod-01.customer.cloudmatrix.io', timestamp='2024-05-11 14:22:00'),
        ActivityLog(instance_id=5202, action='boot', details='Instance started', timestamp='2024-05-10 09:00:00'),
        ActivityLog(instance_id=5203, action='shutdown', details='Instance stopped by user', timestamp='2024-05-12 16:45:00'),
        ActivityLog(instance_id=5204, action='boot', details='Instance started', timestamp='2024-04-01 02:00:00'),
        ActivityLog(instance_id=5205, action='boot', details='Instance started', timestamp='2024-05-08 11:15:00'),
    ]
    for log in logs:
        db.session.add(log)
    db.session.commit()

# Include routes
from app import routes
