from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import time
import sys
import hashlib
from datetime import datetime, timedelta
from app.db import db

app = Flask(__name__)

app.secret_key = hashlib.sha256(b'sba-notify-key-prod').hexdigest()

import os

# MySQL configurations - use DB_HOST env var if set, fallback to localhost
db_host = os.environ.get('DB_HOST', 'localhost')
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://root:sba_monitor@{db_host}/sba_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_recycle': 280,
    'pool_pre_ping': True,
}

db.init_app(app)
app.app_context().push()

from app.models import User, ServiceInstance, NotificationChannel, NotificationLog

# Wait for database to be ready
max_retries = 30
retry_count = 0
while retry_count < max_retries:
    try:
        db.create_all()
        break
    except Exception as e:
        retry_count += 1
        print(f"Database connection attempt {retry_count}/{max_retries} failed: {e}")
        if retry_count >= max_retries:
            print("Failed to connect to database after maximum retries")
            sys.exit(1)
        time.sleep(2)

# Seed initial data
for retry in range(5):
    try:
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                password=hashlib.sha256(b'admin').hexdigest(),
                name='Administrator',
                email='admin@internal.local',
                role='admin'
            )
            db.session.add(admin)

            # Add sample services
            services = [
                ServiceInstance(
                    name='api-gateway',
                    url='http://api-gateway:8080',
                    status='UP',
                    group_name='production',
                    metadata_info='{"version":"2.4.1","context-path":"/"}',
                    last_checked=datetime.utcnow(),
                ),
                ServiceInstance(
                    name='user-service',
                    url='http://user-service:8081',
                    status='UP',
                    group_name='production',
                    metadata_info='{"version":"1.7.3","context-path":"/api/users"}',
                    last_checked=datetime.utcnow(),
                ),
                ServiceInstance(
                    name='order-service',
                    url='http://order-service:8082',
                    status='UP',
                    group_name='production',
                    metadata_info='{"version":"3.1.0","context-path":"/api/orders"}',
                    last_checked=datetime.utcnow(),
                ),
                ServiceInstance(
                    name='notification-service',
                    url='http://notification-svc:8083',
                    status='DOWN',
                    group_name='staging',
                    metadata_info='{"version":"1.2.0","context-path":"/api/notify"}',
                    last_checked=datetime.utcnow() - timedelta(minutes=15),
                ),
                ServiceInstance(
                    name='config-server',
                    url='http://config-server:8888',
                    status='UP',
                    group_name='infrastructure',
                    metadata_info='{"version":"4.0.2","context-path":"/"}',
                    last_checked=datetime.utcnow(),
                ),
            ]
            for svc in services:
                db.session.add(svc)

            # Default mail notification channel with default template
            default_template = """<html>
<body>
<h3>Service Status Change</h3>
<p>Service <strong>{{ instance.name }}</strong> changed status from <em>{{ event.from_status }}</em> to <em>{{ event.to_status }}</em>.</p>
<p>URL: {{ instance.url }}</p>
<p>Timestamp: {{ event.timestamp }}</p>
<hr>
<small>Spring Boot Admin Notification</small>
</body>
</html>"""
            mail_channel = NotificationChannel(
                channel_type='mail',
                enabled=True,
                smtp_host='smtp.internal.local',
                smtp_port=587,
                sender_address='noreply@internal.local',
                recipients='ops-team@internal.local',
                template=default_template,
                subject_template='[SBA] {{ instance.name }}: {{ event.to_status }}',
            )
            db.session.add(mail_channel)
            db.session.commit()
        break
    except Exception as e:
        print(f"Database seed retry {retry + 1}/5 failed: {e}")
        db.session.rollback()
        if retry == 4:
            raise e
        time.sleep(1)

from app import routes
