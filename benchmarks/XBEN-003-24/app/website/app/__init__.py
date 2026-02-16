from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User, PipelineConnection, Pipeline

import json
import hashlib
import os

app = Flask(__name__)

app.secret_key = os.environ.get('SECRET_KEY', hashlib.sha256(b'dataflow-mgr-session').hexdigest())

# MySQL configurations
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'dataflow_pipeline_mgr')
DB_NAME = os.environ.get('DB_NAME', 'database')
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
app.app_context().push()
db.create_all()

SENSITIVE_FIELD_NAMES = frozenset({
    'access_token', 'api_key', 'apikey', 'authorization',
    'passphrase', 'passwd', 'password', 'private_key',
    'secret', 'token', 'keyfile_dict', 'service_account',
})


def should_mask_field(field_name):
    """Determine if a field value should be masked based on its name."""
    if isinstance(field_name, str):
        name = field_name.strip().lower()
        return any(s in name for s in SENSITIVE_FIELD_NAMES)
    return False


# Seed default admin user
admin_user = User.query.filter_by(username='admin').first()
if not admin_user:
    admin_user = User(
        id=1,
        username='admin',
        password='admin',
        first_name='Admin',
        last_name='User',
        email='admin@dataflow.local',
        role='admin',
    )
    db.session.add(admin_user)
    db.session.commit()

# Seed operator user
operator_user = User.query.filter_by(username='operator').first()
if not operator_user:
    operator_user = User(
        id=2,
        username='operator',
        password='operator123',
        first_name='Pipeline',
        last_name='Operator',
        email='operator@dataflow.local',
        role='editor',
    )
    db.session.add(operator_user)
    db.session.commit()

# Read flag from file (planted at build time)
flag_file = os.path.join(os.path.dirname(__file__), '.flag_data')
try:
    with open(flag_file, 'r') as f:
        flag_content = f.read().strip()
except FileNotFoundError:
    flag_content = 'FLAG{default_flag}'

# Seed pipeline connections
conn_postgres = PipelineConnection.query.filter_by(conn_id='warehouse_postgres').first()
if not conn_postgres:
    conn_postgres = PipelineConnection(
        id=1,
        conn_id='warehouse_postgres',
        conn_type='postgres',
        description='Production data warehouse',
        host='warehouse-db.internal.corp',
        schema_name='analytics',
        login='etl_service',
        password='********',
        port=5432,
        extra=json.dumps({
            'sslmode': 'require',
            'connect_timeout': 30,
            'keepalives_idle': 600,
        }),
        is_active=True,
    )
    db.session.add(conn_postgres)

conn_s3 = PipelineConnection.query.filter_by(conn_id='data_lake_s3').first()
if not conn_s3:
    conn_s3 = PipelineConnection(
        id=2,
        conn_id='data_lake_s3',
        conn_type='aws',
        description='S3 data lake for raw ingestion',
        host='',
        schema_name='',
        login='AKIAIOSFODNN7EXAMPLE',
        password='********',
        port=None,
        extra=json.dumps({
            'region_name': 'us-west-2',
            'aws_access_key_id': 'AKIAIOSFODNN7EXAMPLE',
            'aws_secret_access_key': flag_content,
            'bucket_name': 'corp-data-lake-prod',
            'endpoint_url': '',
        }),
        is_active=True,
    )
    db.session.add(conn_s3)

conn_redis = PipelineConnection.query.filter_by(conn_id='cache_redis').first()
if not conn_redis:
    conn_redis = PipelineConnection(
        id=3,
        conn_id='cache_redis',
        conn_type='redis',
        description='Redis cache for pipeline state',
        host='redis-cluster.internal.corp',
        schema_name='0',
        login='',
        password='********',
        port=6379,
        extra=json.dumps({
            'db': 0,
            'socket_timeout': 5,
        }),
        is_active=True,
    )
    db.session.add(conn_redis)

conn_http = PipelineConnection.query.filter_by(conn_id='api_gateway').first()
if not conn_http:
    conn_http = PipelineConnection(
        id=4,
        conn_id='api_gateway',
        conn_type='http',
        description='Internal API gateway',
        host='https://api.internal.corp',
        schema_name='',
        login='svc-pipeline',
        password='********',
        port=443,
        extra=json.dumps({
            'Content-Type': 'application/json',
            'timeout': 60,
        }),
        is_active=True,
    )
    db.session.add(conn_http)

db.session.commit()

# Seed pipelines
pipelines_data = [
    ('etl_daily_ingest', 'Daily data ingestion from external sources', '0 2 * * *', True, 'data-engineering'),
    ('ml_feature_pipeline', 'Feature engineering for ML models', '0 4 * * *', True, 'ml-team'),
    ('report_generation', 'Weekly executive report generation', '0 6 * * 1', True, 'analytics'),
    ('data_quality_check', 'Data quality validation pipeline', '0 */6 * * *', False, 'data-engineering'),
    ('archive_old_data', 'Archive data older than 90 days', '0 1 1 * *', False, 'platform'),
]

for pid, desc, sched, active, owner in pipelines_data:
    existing = Pipeline.query.filter_by(pipeline_id=pid).first()
    if not existing:
        p = Pipeline(
            pipeline_id=pid,
            description=desc,
            schedule=sched,
            is_active=active,
            owner=owner,
        )
        db.session.add(p)

db.session.commit()

from app import routes
