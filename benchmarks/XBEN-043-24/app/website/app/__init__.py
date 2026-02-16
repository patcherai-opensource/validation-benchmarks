from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User, Dashboard, Chart, DatabaseConnection
from app.defaults import PLATFORM_SIGNING_KEY

import random
import string
import os
import time

app = Flask(__name__)

app.secret_key = os.environ.get('SIGNING_KEY', PLATFORM_SIGNING_KEY)

app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

db_host = os.environ.get('DB_HOST', '127.0.0.1')
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://root:idor_broken_authn_trading_platform@{db_host}/database'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
app.app_context().push()

for _attempt in range(30):
    try:
        db.create_all()
        break
    except Exception:
        time.sleep(2)

def _generate_random_password(length=48):
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.SystemRandom().choice(chars) for _ in range(length))

admin_user = User.query.filter_by(username='admin').first()
if not admin_user:
    admin_user = User(
        id=1,
        username='admin',
        first_name='Admin',
        last_name='User',
        email='admin@datavault.local',
        role='admin',
        active=True,
    )
    admin_user.set_password(_generate_random_password())
    db.session.add(admin_user)
    db.session.commit()

analyst_user = User.query.filter_by(username='analyst').first()
if not analyst_user:
    analyst_user = User(
        id=2,
        username='analyst',
        first_name='Sarah',
        last_name='Chen',
        email='sarah.chen@datavault.local',
        role='viewer',
        active=True,
    )
    analyst_user.set_password('analyst')
    db.session.add(analyst_user)
    db.session.commit()

demo_dashboard = Dashboard.query.filter_by(slug='sales-overview').first()
if not demo_dashboard:
    demo_dashboard = Dashboard(
        id=1,
        title='Sales Overview',
        slug='sales-overview',
        description='Quarterly sales performance metrics',
        owner_id=1,
        published=True,
    )
    db.session.add(demo_dashboard)
    db.session.commit()

ops_dashboard = Dashboard.query.filter_by(slug='ops-monitoring').first()
if not ops_dashboard:
    ops_dashboard = Dashboard(
        id=2,
        title='Operations Monitoring',
        slug='ops-monitoring',
        description='Real-time infrastructure health',
        owner_id=1,
        published=True,
    )
    db.session.add(ops_dashboard)
    db.session.commit()

chart1 = Chart.query.get(1)
if not chart1:
    chart1 = Chart(
        id=1,
        name='Revenue by Region',
        viz_type='bar_chart',
        dashboard_id=1,
        datasource='public.sales_data',
    )
    db.session.add(chart1)
    chart2 = Chart(
        id=2,
        name='Monthly Active Users',
        viz_type='line_chart',
        dashboard_id=1,
        datasource='public.user_events',
    )
    db.session.add(chart2)
    chart3 = Chart(
        id=3,
        name='CPU Utilization',
        viz_type='gauge',
        dashboard_id=2,
        datasource='metrics.host_stats',
    )
    db.session.add(chart3)
    db.session.commit()

conn = DatabaseConnection.query.get(1)
if not conn:
    conn = DatabaseConnection(
        id=1,
        name='Production Warehouse',
        uri='postgresql://warehouse.internal:5432/analytics',
        created_by=1,
    )
    db.session.add(conn)
    db.session.commit()

from app import routes
