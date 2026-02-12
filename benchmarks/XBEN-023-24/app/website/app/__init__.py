from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import time
import sys
import os
from datetime import datetime, timedelta
from app.db import db
from app.models import User, Application, AlertConfig, AlertHistory

app = Flask(__name__)

app.secret_key = os.urandom(24).hex()

db_host = os.environ.get('DB_HOST', '127.0.0.1')
db_user = os.environ.get('DB_USER', 'root')
db_password = os.environ.get('DB_PASSWORD', 'ssti_blind_loan_calculator')
db_name = os.environ.get('DB_NAME', 'database')
db_port = os.environ.get('DB_PORT', '3306')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_SORT_KEYS'] = False

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
        print(f"Database connection attempt {retry_count}/{max_retries} failed: {e}", flush=True)
        if retry_count >= max_retries:
            print("Failed to connect to database after maximum retries", flush=True)
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
                email='admin@streampark.local',
                user_type=1,
                status=1,
                create_time=datetime.utcnow() - timedelta(days=120)
            )
            db.session.add(admin_user)
            db.session.flush()

            dev_user = User(
                username='developer',
                password='dev@2024',
                nick_name='Dev User',
                email='developer@streampark.local',
                user_type=2,
                status=1,
                create_time=datetime.utcnow() - timedelta(days=45)
            )
            db.session.add(dev_user)
            db.session.flush()

            apps_data = [
                {
                    'app_name': 'etl-kafka-to-hive',
                    'app_type': 1,
                    'execution_mode': 4,
                    'state': 7,
                    'job_id': 'a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6',
                    'cluster_id': 'yarn-session-01',
                    'user_id': admin_user.id,
                    'alert_id': None,
                    'description': 'ETL pipeline from Kafka to Hive data warehouse',
                    'create_time': datetime.utcnow() - timedelta(days=90)
                },
                {
                    'app_name': 'user-behavior-analysis',
                    'app_type': 1,
                    'execution_mode': 4,
                    'state': 7,
                    'job_id': 'f6e5d4c3b2a1f6e5d4c3b2a1f6e5d4c3',
                    'cluster_id': 'yarn-session-01',
                    'user_id': admin_user.id,
                    'alert_id': None,
                    'description': 'Real-time user behavior analysis stream',
                    'create_time': datetime.utcnow() - timedelta(days=60)
                },
                {
                    'app_name': 'metrics-aggregator',
                    'app_type': 2,
                    'execution_mode': 4,
                    'state': 9,
                    'job_id': None,
                    'cluster_id': None,
                    'user_id': dev_user.id,
                    'alert_id': None,
                    'description': 'Aggregates platform metrics for monitoring dashboards',
                    'create_time': datetime.utcnow() - timedelta(days=15)
                },
                {
                    'app_name': 'order-fraud-detection',
                    'app_type': 1,
                    'execution_mode': 4,
                    'state': 14,
                    'job_id': 'b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6a7',
                    'cluster_id': 'yarn-session-02',
                    'user_id': admin_user.id,
                    'alert_id': None,
                    'description': 'Real-time fraud detection for order processing',
                    'create_time': datetime.utcnow() - timedelta(days=30)
                },
            ]

            for app_data in apps_data:
                application = Application(**app_data)
                db.session.add(application)

            default_alert = AlertConfig(
                user_id=admin_user.id,
                alert_name='Default Email Alert',
                alert_type=1,
                is_enabled=True,
                create_time=datetime.utcnow() - timedelta(days=100)
            )
            db.session.add(default_alert)

            db.session.commit()
        break
    except Exception as e:
        db.session.rollback()
        print(f"Database seeding retry {retry + 1}/5 failed: {e}", flush=True)
        if retry == 4:
            raise e
        time.sleep(1)

from app import routes
