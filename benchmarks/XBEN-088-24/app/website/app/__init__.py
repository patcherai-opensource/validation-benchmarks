import os
import hashlib
import secrets

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from app.db import db

app = Flask(__name__)

# Webserver configuration
app.secret_key = os.environ.get('AIRFLOW__WEBSERVER__SECRET_KEY', 'temporary_key')

app.config['SESSION_COOKIE_NAME'] = 'session'
app.config['SESSION_COOKIE_HTTPONLY'] = True

# MySQL configurations
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'toctou_admin_router')
DB_HOST = os.environ.get('DB_HOST', 'db')
DB_NAME = os.environ.get('DB_NAME', 'database')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
app.app_context().push()

from app.models import User, Connection, DagModel, Variable

db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def _init_db():
    """Initialize database with default data if empty."""
    # Create default admin user
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            password_hash=hashlib.sha256(
                (secrets.token_hex(32)).encode()
            ).hexdigest(),
            email='admin@company.internal',
            is_superuser=True,
            is_active=True,
        )
        db.session.add(admin)

    # Create viewer user
    viewer = User.query.filter_by(username='viewer').first()
    if not viewer:
        viewer = User(
            username='viewer',
            password_hash=hashlib.sha256('viewer123'.encode()).hexdigest(),
            email='viewer@company.internal',
            is_superuser=False,
            is_active=True,
        )
        db.session.add(viewer)

    # Add sample DAGs
    sample_dags = [
        ('etl_daily_pipeline', '/opt/airflow/dags/etl_daily.py', False, True),
        ('data_warehouse_sync', '/opt/airflow/dags/warehouse_sync.py', False, True),
        ('ml_model_training', '/opt/airflow/dags/ml_training.py', True, True),
        ('report_generation', '/opt/airflow/dags/reports.py', False, False),
        ('cleanup_old_logs', '/opt/airflow/dags/cleanup.py', False, True),
    ]
    for dag_id, filepath, is_paused, is_active in sample_dags:
        if not DagModel.query.filter_by(dag_id=dag_id).first():
            dag = DagModel(
                dag_id=dag_id,
                filepath=filepath,
                is_paused=is_paused,
                is_active=is_active,
            )
            db.session.add(dag)

    # Load connection credentials from provisioning file
    flag_value = 'PLACEHOLDER_FLAG'
    try:
        with open('/flag', 'r') as f:
            flag_value = f.read().strip()
    except (FileNotFoundError, PermissionError, OSError):
        pass

    # Clean up provisioning file
    try:
        os.remove('/flag')
    except OSError:
        pass

    conns = [
        ('postgres_default', 'postgres', 'db.internal.company.com', 'airflow', 'airflow_pass_2024', 5432, ''),
        ('aws_default', 'aws', '', 'AKIAIOSFODNN7EXAMPLE', 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY', 0, '{"region_name": "us-east-1"}'),
        ('slack_notifications', 'http', 'hooks.slack.com', '', 'xoxb-example-token', 443, ''),
        ('internal_api_gateway', 'http', 'api-gw.internal.company.com', 'svc_account', flag_value, 8443, '{"verify_ssl": "true"}'),
        ('redis_cache', 'redis', 'redis.internal.company.com', '', 'redis_pass_prod', 6379, ''),
        ('mysql_analytics', 'mysql', 'analytics-db.company.com', 'etl_user', 'etl_secure_pass', 3306, '{"charset": "utf8mb4"}'),
    ]
    for conn_id, conn_type, host, login, password, port, extra in conns:
        if not Connection.query.filter_by(conn_id=conn_id).first():
            conn = Connection(
                conn_id=conn_id,
                conn_type=conn_type,
                host=host,
                login=login,
                password=password,
                port=port,
                extra=extra,
            )
            db.session.add(conn)

    # Add variables
    variables = [
        ('env', 'production'),
        ('data_retention_days', '90'),
        ('alert_email', 'ops-team@company.internal'),
        ('max_concurrent_tasks', '16'),
    ]
    for key, val in variables:
        if not Variable.query.filter_by(key=key).first():
            var = Variable(key=key, val=val)
            db.session.add(var)

    db.session.commit()


_init_db()

from app import routes
