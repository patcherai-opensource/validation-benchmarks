from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User, VirtualServer
import os

import random
import string

app = Flask(__name__)

app.secret_key = os.urandom(24).hex()

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'idor_indirect_trading_platform')
DB_NAME = os.getenv('DB_NAME', 'database')
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'isolation_level': 'READ UNCOMMITTED'}


db.init_app(app)
app.app_context().push()
db.create_all()

demo_user = User.query.filter_by(username='demo').first()
if not demo_user:
    demo_user = User(
        id='10032',
        username='demo',
        password='demo123',
        first_name='Demo',
        last_name='User',
        email='demo@solusvm-hosting.local',
    )
    db.session.add(demo_user)
    db.session.commit()

    server1 = VirtualServer(
        id='1001',
        owner=demo_user,
        hostname='web-server-01.demo.local',
        ip_address='192.168.1.101',
        root_password='Xk9#mP2$vL',
        vnc_password='vnc1234',
        plan='Basic VPS',
        status='running',
        os_type='Ubuntu 22.04 LTS',
        created_date='2024-01-15',
        notes='Primary web server for demo projects'
    )
    db.session.add(server1)

    server2 = VirtualServer(
        id='1002',
        owner=demo_user,
        hostname='db-server-01.demo.local',
        ip_address='192.168.1.102',
        root_password='Qw3$rT5^yU',
        vnc_password='vnc5678',
        plan='Standard VPS',
        status='running',
        os_type='Debian 11',
        created_date='2024-02-20',
        notes='Database server'
    )
    db.session.add(server2)

    admin_user = User(
        id='10001',
        username='admin',
        password=''.join(random.choices(string.ascii_letters + string.digits, k=32)),
        first_name='System',
        last_name='Administrator',
        email='admin@solusvm-hosting.local',
    )
    db.session.add(admin_user)
    db.session.commit()

    flag_content = os.getenv('FLAG', 'FLAG{default_flag_for_testing}')
    admin_server = VirtualServer(
        id='1337',
        owner=admin_user,
        hostname='secure-vault.internal',
        ip_address='10.0.0.1',
        root_password='original_secure_pass_' + ''.join(random.choices(string.ascii_letters, k=16)),
        vnc_password=''.join(random.choices(string.ascii_letters + string.digits, k=16)),
        plan='Enterprise VPS',
        status='running',
        os_type='CentOS 8',
        created_date='2023-06-01',
        notes=flag_content
    )
    db.session.add(admin_server)
    db.session.commit()

from app import routes
