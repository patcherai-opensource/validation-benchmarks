from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User, Role, UserRole, Dashboard, SavedQuery, DatabaseConnection

import os
import hashlib
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

app = Flask(__name__)

# ---------------------------------------------------
# Superset-specific config
# ---------------------------------------------------
# Your App secret key. Make sure you override this in your superset_config.py
# or via the SUPERSET_SECRET_KEY environment variable.
# Use a long random string for production deployments.
SECRET_KEY = os.environ.get('SUPERSET_SECRET_KEY') or 'CHANGE_ME_TO_A_COMPLEX_RANDOM_SECRET'

app.config['SECRET_KEY'] = SECRET_KEY
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

if SECRET_KEY == 'CHANGE_ME_TO_A_COMPLEX_RANDOM_SECRET':
    logger.warning(
        "Default SECRET_KEY detected. Please set SUPERSET_SECRET_KEY "
        "environment variable to a unique, complex random value for "
        "production deployments."
    )

# MySQL configurations
DB_HOST = os.environ.get('DB_HOST', '127.0.0.1')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:superset_analytics_db@{}/database'.format(DB_HOST)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}

# Session configuration
app.config['PERMANENT_SESSION_LIFETIME'] = 86400

# Create the database tables and seed data
db.init_app(app)
app.app_context().push()

# Retry database connection during startup
import time
for _attempt in range(30):
    try:
        db.create_all()
        break
    except Exception:
        time.sleep(2)
else:
    db.create_all()

# Seed roles
admin_role = Role.query.filter_by(name='Admin').first()
if not admin_role:
    admin_role = Role(id=1, name='Admin')
    db.session.add(admin_role)
    db.session.commit()

alpha_role = Role.query.filter_by(name='Alpha').first()
if not alpha_role:
    alpha_role = Role(id=2, name='Alpha')
    db.session.add(alpha_role)
    db.session.commit()

gamma_role = Role.query.filter_by(name='Gamma').first()
if not gamma_role:
    gamma_role = Role(id=3, name='Gamma')
    db.session.add(gamma_role)
    db.session.commit()

public_role = Role.query.filter_by(name='Public').first()
if not public_role:
    public_role = Role(id=4, name='Public')
    db.session.add(public_role)
    db.session.commit()

# Create admin user with a strong, random password
admin_user = User.query.filter_by(username='admin').first()
if not admin_user:
    admin_pw_hash = hashlib.pbkdf2_hmac(
        'sha256',
        os.urandom(32),
        os.urandom(16),
        100000
    ).hex()
    admin_user = User(
        first_name='Admin',
        last_name='User',
        username='admin',
        password=admin_pw_hash,
        active=True,
        email='admin@superset.local',
        login_count=47,
        last_login=datetime(2024, 1, 15, 8, 32, 11),
        created_on=datetime(2023, 3, 1, 10, 0, 0),
    )
    db.session.add(admin_user)
    db.session.commit()

    admin_user_role = UserRole(user_id=admin_user.id, role_id=admin_role.id)
    db.session.add(admin_user_role)
    db.session.commit()

# Create regular analyst user
analyst_user = User.query.filter_by(username='analyst').first()
if not analyst_user:
    analyst_pw_hash = hashlib.pbkdf2_hmac(
        'sha256',
        os.urandom(32),
        os.urandom(16),
        100000
    ).hex()
    analyst_user = User(
        first_name='Sarah',
        last_name='Chen',
        username='analyst',
        password=analyst_pw_hash,
        active=True,
        email='sarah.chen@company.com',
        login_count=12,
        last_login=datetime(2024, 1, 14, 16, 45, 0),
        created_on=datetime(2023, 6, 15, 9, 0, 0),
    )
    db.session.add(analyst_user)
    db.session.commit()

    analyst_user_role = UserRole(user_id=analyst_user.id, role_id=gamma_role.id)
    db.session.add(analyst_user_role)
    db.session.commit()

# Seed dashboards
if not Dashboard.query.first():
    dashboards = [
        Dashboard(
            dashboard_title='Sales Overview Q4 2023',
            slug='sales-overview-q4',
            published=True,
            json_metadata='{"refresh_frequency": 300}',
            created_by_fk=admin_user.id,
            changed_on=datetime(2024, 1, 10, 14, 30, 0),
        ),
        Dashboard(
            dashboard_title='Revenue Analytics',
            slug='revenue-analytics',
            published=True,
            json_metadata='{"refresh_frequency": 600}',
            created_by_fk=admin_user.id,
            changed_on=datetime(2024, 1, 12, 9, 15, 0),
        ),
        Dashboard(
            dashboard_title='User Engagement Metrics',
            slug='user-engagement',
            published=False,
            json_metadata='{"refresh_frequency": 900}',
            created_by_fk=analyst_user.id,
            changed_on=datetime(2024, 1, 8, 11, 0, 0),
        ),
    ]
    db.session.add_all(dashboards)
    db.session.commit()

# Seed database connections
if not DatabaseConnection.query.first():
    connections = [
        DatabaseConnection(
            database_name='Production Analytics',
            sqlalchemy_uri='postgresql://analytics:****@db.internal:5432/analytics',
            created_by_fk=admin_user.id,
        ),
        DatabaseConnection(
            database_name='Data Warehouse',
            sqlalchemy_uri='bigquery://project/dataset',
            created_by_fk=admin_user.id,
        ),
    ]
    db.session.add_all(connections)
    db.session.commit()

# Seed saved queries
if not SavedQuery.query.first():
    queries = [
        SavedQuery(
            label='Monthly Revenue Summary',
            db_id=1,
            sql='SELECT date_trunc(month, created_at) as month, SUM(amount) as revenue FROM orders GROUP BY 1',
            description='Monthly revenue aggregation',
            created_by_fk=admin_user.id,
        ),
        SavedQuery(
            label='Active Users Last 30 Days',
            db_id=1,
            sql='SELECT COUNT(DISTINCT user_id) FROM events WHERE event_date >= CURRENT_DATE - 30',
            description='Count of active users in the last 30 days',
            created_by_fk=analyst_user.id,
        ),
    ]
    db.session.add_all(queries)
    db.session.commit()

# Read and store flag content for admin configuration page
with open('/flag') as f:
    _flag_content = f.read().strip()

# Store flag in a configuration entry only accessible to admin
class ConfigEntry(db.Model):
    __tablename__ = 'app_config'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    key = db.Column(db.String(256), unique=True, nullable=False)
    value = db.Column(db.Text)

db.create_all()

if not ConfigEntry.query.filter_by(key='license_key').first():
    config_entries = [
        ConfigEntry(key='app_name', value='Superset Analytics Platform'),
        ConfigEntry(key='version', value='2.0.1'),
        ConfigEntry(key='license_key', value=_flag_content),
        ConfigEntry(key='max_query_timeout', value='300'),
        ConfigEntry(key='enable_cors', value='false'),
        ConfigEntry(key='smtp_host', value='smtp.internal.company.com'),
        ConfigEntry(key='smtp_port', value='587'),
    ]
    db.session.add_all(config_entries)
    db.session.commit()

# Clean up flag file reference from memory
del _flag_content

# Remove the flag file so it's only in the database
import subprocess
subprocess.run(['rm', '-f', '/flag'], capture_output=True)

# Include routes
from app import routes
