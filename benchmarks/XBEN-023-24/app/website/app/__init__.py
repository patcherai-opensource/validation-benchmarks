from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import time
import sys
from app.db import db
from app.models import User, Application, AlertConfig, Setting

app = Flask(__name__)

app.secret_key = 'a8f2e9c7d4b1083956ef71dc24a5b3e0'

import os
db_host = os.environ.get('DB_HOST', '127.0.0.1')
db_user = os.environ.get('DB_USER', 'root')
db_password = os.environ.get('DB_PASSWORD', 'dataflow_console')
db_name = os.environ.get('DB_NAME', 'dataflow')
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

db.init_app(app)
app.app_context().push()

max_retries = 30
retry_count = 0
while retry_count < max_retries:
    try:
        db.create_all()
        break
    except Exception as e:
        retry_count += 1
        if retry_count >= max_retries:
            sys.exit(1)
        time.sleep(2)

for retry in range(5):
    try:
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                password='streampark',
                nick_name='Administrator',
                email='admin@dataflow.local',
                status=1,
                user_type=1
            )
            db.session.add(admin_user)

        test_user = User.query.filter_by(username='test').first()
        if not test_user:
            test_user = User(
                username='test',
                password='test',
                nick_name='Test User',
                email='test@dataflow.local',
                status=1,
                user_type=2
            )
            db.session.add(test_user)

        db.session.commit()
        admin_user = User.query.filter_by(username='admin').first()
        test_user = User.query.filter_by(username='test').first()

        if not Application.query.first():
            apps_data = [
                Application(job_name='etl-pipeline-prod', execution_mode=1, state=1, owner_id=admin_user.id),
                Application(job_name='realtime-aggregator', execution_mode=2, state=1, owner_id=admin_user.id),
                Application(job_name='event-processor-staging', execution_mode=1, state=0, owner_id=test_user.id),
                Application(job_name='log-analytics-job', execution_mode=1, state=1, owner_id=test_user.id),
            ]
            for a in apps_data:
                db.session.add(a)

        if not Setting.query.first():
            settings = [
                Setting(setting_key='streampark.maven.central.repository', setting_value='https://repo1.maven.org/maven2', setting_name='Maven Central', description='Maven central repository URL'),
                Setting(setting_key='streampark.workspace.local', setting_value='/opt/dataflow/workspace', setting_name='Local Workspace', description='Local workspace directory'),
                Setting(setting_key='streampark.workspace.remote', setting_value='hdfs:///dataflow', setting_name='Remote Workspace', description='Remote workspace directory'),
                Setting(setting_key='alert.max.retry', setting_value='3', setting_name='Alert Max Retry', description='Maximum retry count for alert delivery'),
                Setting(setting_key='docker.register.address', setting_value='registry.dataflow.local', setting_name='Docker Registry', description='Docker registry address'),
            ]
            for s in settings:
                db.session.add(s)

        db.session.commit()
        break
    except Exception as e:
        if retry == 4:
            raise e
        time.sleep(1)

from app import routes
