import os
import json
import hashlib
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User, Team, FlinkApp, AlertConfig, Variable

app = Flask(__name__, template_folder='templates', static_folder='static')

app.secret_key = hashlib.sha256(b'streampark-console-service').hexdigest()

# MySQL configurations - use environment variables for K8s compatibility
db_host = os.environ.get('DB_HOST', 'localhost')
db_user = os.environ.get('DB_USER', 'root')
db_password = os.environ.get('DB_PASSWORD', 'ssti_include_loan_calculator')
db_name = os.environ.get('DB_NAME', 'database')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create the database tables
db.init_app(app)
app.app_context().push()
db.create_all()

# Initialize default data
admin_user = User.query.filter_by(username='admin').first()
if not admin_user:
    admin_user = User(
        username='admin',
        password=hashlib.sha256(b'streampark123').hexdigest(),
        nick_name='Administrator',
        email='admin@streampark.local',
        user_type=1,
        status=1,
        description='System administrator'
    )
    db.session.add(admin_user)
    db.session.commit()

dev_user = User.query.filter_by(username='developer').first()
if not dev_user:
    dev_user = User(
        username='developer',
        password=hashlib.sha256(b'dev2024').hexdigest(),
        nick_name='Dev User',
        email='dev@streampark.local',
        user_type=2,
        status=1,
        description='Development team member'
    )
    db.session.add(dev_user)
    db.session.commit()

default_team = Team.query.filter_by(team_name='default').first()
if not default_team:
    default_team = Team(
        team_name='default',
        description='Default team'
    )
    db.session.add(default_team)
    db.session.commit()

prod_team = Team.query.filter_by(team_name='production').first()
if not prod_team:
    prod_team = Team(
        team_name='production',
        description='Production workloads'
    )
    db.session.add(prod_team)
    db.session.commit()

# Add sample Flink applications
sample_app = FlinkApp.query.filter_by(app_name='etl-pipeline-prod').first()
if not sample_app:
    sample_app = FlinkApp(
        team_id=default_team.id,
        app_name='etl-pipeline-prod',
        app_type=1,
        execution_mode=1,
        state=5,
        description='Production ETL pipeline for data warehouse'
    )
    db.session.add(sample_app)

sample_app2 = FlinkApp.query.filter_by(app_name='clickstream-analytics').first()
if not sample_app2:
    sample_app2 = FlinkApp(
        team_id=default_team.id,
        app_name='clickstream-analytics',
        app_type=2,
        execution_mode=2,
        state=5,
        description='Real-time clickstream processing'
    )
    db.session.add(sample_app2)

sample_app3 = FlinkApp.query.filter_by(app_name='fraud-detection').first()
if not sample_app3:
    sample_app3 = FlinkApp(
        team_id=prod_team.id,
        app_name='fraud-detection',
        app_type=1,
        execution_mode=4,
        state=0,
        description='Fraud detection streaming job'
    )
    db.session.add(sample_app3)

# Add sample variables
var1 = Variable.query.filter_by(variable_code='kafka.brokers').first()
if not var1:
    var1 = Variable(
        variable_code='kafka.brokers',
        variable_value='kafka-0.kafka-headless:9092,kafka-1.kafka-headless:9092',
        description='Kafka broker endpoints',
        creator_id=admin_user.id,
        desensitization=False
    )
    db.session.add(var1)

var2 = Variable.query.filter_by(variable_code='checkpoint.dir').first()
if not var2:
    var2 = Variable(
        variable_code='checkpoint.dir',
        variable_value='hdfs:///streampark/checkpoints',
        description='Flink checkpoint directory',
        creator_id=admin_user.id,
        desensitization=False
    )
    db.session.add(var2)

# Add a default alert config (email type, safe)
default_alert = AlertConfig.query.filter_by(alert_name='ops-email-alert').first()
if not default_alert:
    default_alert = AlertConfig(
        user_id=admin_user.id,
        alert_name='ops-email-alert',
        alert_type=1,
        email_params=json.dumps({
            'contacts': 'ops@streampark.local',
            'smtp_host': 'smtp.streampark.local'
        })
    )
    db.session.add(default_alert)

db.session.commit()

# Include routes
from app import routes
