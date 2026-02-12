from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User, Connection, DagModel, Variable

import json
import os

app = Flask(__name__)

app.secret_key = 'a9f3c7b2e1d04a6f8b5c9e2d7a1f3b6c8d4e9f2a5b7c1d3e6f8a0b4c7d9e2f1'

# MySQL configurations
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'airflow')
DB_NAME = os.environ.get('DB_NAME', 'database')
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True

db.init_app(app)
app.app_context().push()
db.create_all()

# Seed default admin user
admin = User.query.filter_by(username='airflow').first()
if not admin:
    admin = User(
        username='airflow',
        first_name='Airflow',
        last_name='Admin',
        email='airflow@example.com',
        role='Admin',
        active=True,
    )
    admin.set_password('airflow')
    db.session.add(admin)
    db.session.commit()

# Seed a viewer user
viewer = User.query.filter_by(username='viewer').first()
if not viewer:
    viewer = User(
        username='viewer',
        first_name='Read',
        last_name='Only',
        email='viewer@example.com',
        role='Viewer',
        active=True,
    )
    viewer.set_password('viewer123')
    db.session.add(viewer)
    db.session.commit()

# Seed connections
flag_content = os.environ.get('FLAG', 'FLAG{default_flag}')

conn_postgres = Connection.query.filter_by(conn_id='postgres_default').first()
if not conn_postgres:
    conn_postgres = Connection(
        conn_id='postgres_default',
        conn_type='postgres',
        description='Default Postgres connection',
        host='postgres.internal.corp',
        schema='airflow',
        login='airflow',
        password='p0stgr3s_s3cur3_pwd!',
        port=5432,
        extra=json.dumps({"sslmode": "require", "connect_timeout": 10}),
        is_encrypted=False,
        is_extra_encrypted=False,
    )
    db.session.add(conn_postgres)

conn_mysql = Connection.query.filter_by(conn_id='mysql_default').first()
if not conn_mysql:
    conn_mysql = Connection(
        conn_id='mysql_default',
        conn_type='mysql',
        description='Default MySQL connection for ETL pipelines',
        host='mysql-primary.internal.corp',
        schema='data_warehouse',
        login='etl_user',
        password='mYsql_3tl_pwd_2024!',
        port=3306,
        extra=json.dumps({"charset": "utf8mb4", "local_infile": True}),
        is_encrypted=False,
        is_extra_encrypted=False,
    )
    db.session.add(conn_mysql)

conn_aws = Connection.query.filter_by(conn_id='aws_default').first()
if not conn_aws:
    conn_aws = Connection(
        conn_id='aws_default',
        conn_type='aws',
        description='AWS connection for S3 and Redshift access',
        host='',
        schema='',
        login='AKIAIOSFODNN7EXAMPLE',
        password='wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
        port=None,
        extra=json.dumps({
            "region_name": "us-east-1",
            "role_arn": "arn:aws:iam::123456789012:role/airflow-role",
            "aws_session_token": ""
        }),
        is_encrypted=False,
        is_extra_encrypted=False,
    )
    db.session.add(conn_aws)

conn_http = Connection.query.filter_by(conn_id='http_default').first()
if not conn_http:
    conn_http = Connection(
        conn_id='http_default',
        conn_type='http',
        description='Default HTTP connection',
        host='https://api.internal.corp',
        schema='',
        login='',
        password='',
        port=443,
        extra=json.dumps({"Content-Type": "application/json"}),
        is_encrypted=False,
        is_extra_encrypted=False,
    )
    db.session.add(conn_http)

conn_slack = Connection.query.filter_by(conn_id='slack_alerts').first()
if not conn_slack:
    conn_slack = Connection(
        conn_id='slack_alerts',
        conn_type='slack_webhook',
        description='Slack webhook for pipeline alerts',
        host='https://hooks.slack.com',
        schema='',
        login='',
        password=flag_content,
        port=None,
        extra=json.dumps({
            "webhook_token": flag_content,
            "channel": "#data-pipeline-alerts",
            "username": "Airflow Bot"
        }),
        is_encrypted=False,
        is_extra_encrypted=False,
    )
    db.session.add(conn_slack)

conn_spark = Connection.query.filter_by(conn_id='spark_default').first()
if not conn_spark:
    conn_spark = Connection(
        conn_id='spark_default',
        conn_type='spark',
        description='Spark cluster connection',
        host='spark://spark-master.internal.corp',
        schema='',
        login='spark',
        password='spk_cluster_auth',
        port=7077,
        extra=json.dumps({"deploy-mode": "cluster", "queue": "default"}),
        is_encrypted=False,
        is_extra_encrypted=False,
    )
    db.session.add(conn_spark)

db.session.commit()

# Seed DAGs
dag_ids = [
    ('etl_daily_pipeline', '0 2 * * *', 'Daily ETL pipeline for data warehouse refresh', 'data_team', '/opt/airflow/dags/etl_daily.py'),
    ('ml_training_weekly', '0 0 * * 0', 'Weekly ML model retraining pipeline', 'ml_team', '/opt/airflow/dags/ml_training.py'),
    ('data_quality_checks', '*/30 * * * *', 'Data quality validation checks', 'data_team', '/opt/airflow/dags/dq_checks.py'),
    ('slack_notifications', '0 8 * * *', 'Send daily pipeline summary to Slack', 'platform_team', '/opt/airflow/dags/slack_notify.py'),
    ('s3_data_sync', '0 */6 * * *', 'Sync data from S3 to data warehouse', 'data_team', '/opt/airflow/dags/s3_sync.py'),
]
for dag_id, schedule, desc, owners, file_loc in dag_ids:
    existing = DagModel.query.filter_by(dag_id=dag_id).first()
    if not existing:
        dag = DagModel(
            dag_id=dag_id,
            is_paused=False,
            is_active=True,
            schedule_interval=schedule,
            description=desc,
            owners=owners,
            file_loc=file_loc,
        )
        db.session.add(dag)

# Seed Variables
variables = [
    ('env', 'production', 'Deployment environment', False),
    ('data_bucket', 's3://corp-data-lake-prod', 'Primary data lake bucket', False),
    ('slack_channel', '#data-pipeline-alerts', 'Default Slack channel for alerts', False),
    ('max_retries', '3', 'Maximum task retry count', False),
    ('email_on_failure', 'data-team@example.com', 'Alert email for failures', False),
]
for key, val, desc, encrypted in variables:
    existing = Variable.query.filter_by(key=key).first()
    if not existing:
        v = Variable(key=key, val=val, description=desc, is_encrypted=encrypted)
        db.session.add(v)

db.session.commit()

# Clear flag from environment after seeding
if 'FLAG' in os.environ:
    del os.environ['FLAG']

from app import routes
