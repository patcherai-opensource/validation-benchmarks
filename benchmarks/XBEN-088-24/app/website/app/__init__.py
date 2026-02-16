from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User, Tenant, DeviceConfig

import random
import string
import os
import time


app = Flask(__name__)

app.secret_key = os.environ.get('SECRET_KEY', os.urandom(32).hex())

DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'toctou_admin_router')
DB_HOST = os.environ.get('DB_HOST', 'db')
DB_NAME = os.environ.get('DB_NAME', 'database')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
app.app_context().push()
db.create_all()

# Read flag from file (planted at build time)
_flag_content = ''
try:
    with open('/flag', 'r') as _f:
        _flag_content = _f.read().strip()
except Exception:
    _flag_content = 'FLAG_NOT_SET'

# Seed tenant data
def _seed_data():
    for _attempt in range(5):
        try:
            _ops = Tenant.query.filter_by(tenant_id='ops-west').first()
            if _ops:
                return
            break
        except Exception:
            time.sleep(2)
            continue
    else:
        return

    try:
        db.session.add(Tenant(tenant_id='ops-west', display_name='Operations West',
                              realm='internal', auth_endpoint='https://idp-alpha.corp.local/auth/realms/internal'))
        db.session.add(Tenant(tenant_id='eng-core', display_name='Engineering Core',
                              realm='internal', auth_endpoint='https://idp-bravo.corp.local/auth/realms/internal'))
        db.session.add(Tenant(tenant_id='fac-main', display_name='Facilities Mgmt',
                              realm='facilities', auth_endpoint='https://idp-charlie.corp.local/auth/realms/facilities'))
        db.session.commit()

        db.session.add(User(username='operator', password='operator', name='Sam', lastname='Chen',
                            email='schen@ops-west.corp.local', tenant_id='ops-west', role='viewer'))
        db.session.add(User(username='engadmin',
                            password=''.join(random.choices(string.ascii_letters + string.digits, k=64)),
                            name='DevOps', lastname='Admin', email='devops@eng-core.corp.local',
                            tenant_id='eng-core', role='admin'))
        db.session.add(User(username='dev01',
                            password=''.join(random.choices(string.ascii_letters + string.digits, k=64)),
                            name='Developer', lastname='One', email='dev01@eng-core.corp.local',
                            tenant_id='eng-core', role='viewer'))
        db.session.add(User(username='janitor',
                            password=''.join(random.choices(string.ascii_letters + string.digits, k=64)),
                            name='Maintenance', lastname='Staff', email='maint@fac-main.corp.local',
                            tenant_id='fac-main', role='viewer'))
        db.session.commit()

        db.session.add(DeviceConfig(tenant_id='ops-west', device_name='switch-core-01',
                                    config_data='{"hostname": "switch-core-01", "vlans": [10, 20, 30], "uplink": "ge-0/0/0"}'))
        db.session.add(DeviceConfig(tenant_id='ops-west', device_name='ap-floor2-west',
                                    config_data='{"hostname": "ap-floor2-west", "ssid": "CorpWiFi-West", "channel": 36}'))
        db.session.add(DeviceConfig(tenant_id='eng-core', device_name='fw-perimeter-01',
                                    config_data='{"hostname": "fw-perimeter-01", "rules": 847, "last_audit": "2024-01-15"}'))
        db.session.add(DeviceConfig(tenant_id='eng-core', device_name='vault-backup-key',
                                    config_data=f'{{"hostname": "vault-hsm-01", "backup_key": "{_flag_content}", "rotation_due": "2025-06-01"}}'))
        db.session.add(DeviceConfig(tenant_id='fac-main', device_name='hvac-controller-b2',
                                    config_data='{"hostname": "hvac-b2", "zone": "basement", "setpoint_c": 22}'))
        db.session.commit()
    except Exception:
        db.session.rollback()

_seed_data()

# Include routes
from app import routes
