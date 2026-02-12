import os
import random
import string

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User, Role, UserRole, SystemConfig


app = Flask(__name__)

app.secret_key = os.urandom(32).hex()

db_host = os.environ.get('DB_HOST', 'localhost')
db_user = os.environ.get('DB_USER', 'root')
db_password = os.environ.get('DB_PASSWORD', 'lamp_cloud_platform')
db_name = os.environ.get('DB_NAME', 'lamp_cloud')

app.config['SQLALCHEMY_DATABASE_URI'] = (
    f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
app.app_context().push()
db.create_all()


def _seed_data():
    # Seed roles
    admin_role = Role.query.filter_by(code='SUPER_ADMIN').first()
    if not admin_role:
        admin_role = Role(id=1, name='Super Admin', code='SUPER_ADMIN',
                          describe_='Platform super administrator', status=True,
                          readonly=True)
        db.session.add(admin_role)

    user_role = Role.query.filter_by(code='PLATFORM_USER').first()
    if not user_role:
        user_role = Role(id=2, name='Platform User', code='PLATFORM_USER',
                         describe_='Standard platform user', status=True,
                         readonly=True)
        db.session.add(user_role)

    # Seed admin user with strong random password
    admin = User.query.filter_by(account='admin').first()
    if not admin:
        admin = User(
            id=1,
            account='admin',
            name='Administrator',
            email='admin@lamp-cloud.internal',
            mobile='13800000000',
            status=True,
            readonly=True,
        )
        admin.set_password(
            ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=48))
        )
        db.session.add(admin)
        db.session.flush()

        admin_ur = UserRole(id=1, user_id=admin.id, role_id=admin_role.id)
        db.session.add(admin_ur)

    # Seed regular users
    for uid, acct, nm, em in [
        (100, 'zhangsan', 'Zhang San', 'zhangsan@example.com'),
        (101, 'lisi', 'Li Si', 'lisi@example.com'),
        (102, 'wangwu', 'Wang Wu', 'wangwu@example.com'),
    ]:
        u = User.query.filter_by(account=acct).first()
        if not u:
            u = User(id=uid, account=acct, name=nm, email=em, status=True, readonly=False)
            u.set_password(
                ''.join(random.choices(string.ascii_letters + string.digits, k=32))
            )
            db.session.add(u)
            db.session.flush()
            ur = UserRole(id=uid, user_id=u.id, role_id=user_role.id)
            db.session.add(ur)

    # Store flag as a protected system configuration entry
    flag_cfg = SystemConfig.query.filter_by(key='platform.license.key').first()
    if not flag_cfg:
        with open('/flag') as f:
            flag_val = f.read().strip()
        flag_cfg = SystemConfig(
            id=1,
            key='platform.license.key',
            value=flag_val,
            description='Platform license activation key',
            readonly=True,
        )
        db.session.add(flag_cfg)

    # Add some other config entries
    for cid, k, v, d in [
        (2, 'platform.name', 'Lamp Cloud Platform', 'Platform display name'),
        (3, 'platform.version', '3.7.4', 'Current platform version'),
        (4, 'security.session.timeout', '3600', 'Session timeout in seconds'),
        (5, 'security.max_login_attempts', '5', 'Maximum login attempts before lockout'),
    ]:
        c = SystemConfig.query.filter_by(key=k).first()
        if not c:
            c = SystemConfig(id=cid, key=k, value=v, description=d, readonly=False)
            db.session.add(c)

    db.session.commit()


_seed_data()

from app import routes
from app import nacos
