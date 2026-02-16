from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import time
import sys
import os
from app.db import db
from app.models import User, ServiceInstance, AlertConfig, AlertLog

app = Flask(__name__)

app.secret_key = 'f8a3b7c2d1e9f4058c6a7b3d2e1f0a94'

# MySQL configurations
db_host = os.environ.get('DB_HOST', '127.0.0.1')
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://root:svc_monitor_admin@{db_host}/monitordb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create the database tables
db.init_app(app)
app.app_context().push()

# Wait for database to be ready
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

# Seed data
for retry in range(5):
    try:
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                password='admin',
                name='System Administrator',
                email='admin@servicemonitor.local',
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()

        # Seed service instances
        if ServiceInstance.query.count() == 0:
            instances = [
                ServiceInstance(
                    name='user-service',
                    service_url='http://10.0.1.10:8080',
                    health_url='http://10.0.1.10:8080/actuator/health',
                    management_url='http://10.0.1.10:8080/actuator',
                    status='UP',
                    metadata_json='{"version":"2.4.1","group":"core"}',
                    last_checked=datetime.utcnow()
                ),
                ServiceInstance(
                    name='order-service',
                    service_url='http://10.0.1.11:8080',
                    health_url='http://10.0.1.11:8080/actuator/health',
                    management_url='http://10.0.1.11:8080/actuator',
                    status='UP',
                    metadata_json='{"version":"1.8.3","group":"core"}',
                    last_checked=datetime.utcnow()
                ),
                ServiceInstance(
                    name='payment-gateway',
                    service_url='http://10.0.1.12:8443',
                    health_url='http://10.0.1.12:8443/actuator/health',
                    management_url='http://10.0.1.12:8443/actuator',
                    status='UP',
                    metadata_json='{"version":"3.1.0","group":"payments"}',
                    last_checked=datetime.utcnow()
                ),
                ServiceInstance(
                    name='notification-service',
                    service_url='http://10.0.1.13:8080',
                    health_url='http://10.0.1.13:8080/actuator/health',
                    management_url='http://10.0.1.13:8080/actuator',
                    status='DOWN',
                    metadata_json='{"version":"1.2.0","group":"messaging"}',
                    last_checked=datetime.utcnow()
                ),
                ServiceInstance(
                    name='inventory-service',
                    service_url='http://10.0.1.14:8080',
                    health_url='http://10.0.1.14:8080/actuator/health',
                    management_url='http://10.0.1.14:8080/actuator',
                    status='UP',
                    metadata_json='{"version":"2.0.5","group":"warehouse"}',
                    last_checked=datetime.utcnow()
                ),
            ]
            for inst in instances:
                db.session.add(inst)
            db.session.commit()

        # Seed default alert configuration
        if AlertConfig.query.count() == 0:
            default_config = AlertConfig(
                recipients='ops-team@servicemonitor.local',
                sender='Service Monitor <alerts@servicemonitor.local>',
                subject_template='[{{ current_status }}] {{ instance_name }} status changed',
                body_template='''<div style="font-family: sans-serif; padding: 20px;">
    <h2>Service Status Alert</h2>
    <p>Instance <strong>{{ instance_name }}</strong> changed status.</p>
    <table style="border-collapse: collapse; width: 100%;">
        <tr>
            <td style="padding: 8px; border: 1px solid #ddd;">Instance</td>
            <td style="padding: 8px; border: 1px solid #ddd;">{{ instance_name }}</td>
        </tr>
        <tr>
            <td style="padding: 8px; border: 1px solid #ddd;">URL</td>
            <td style="padding: 8px; border: 1px solid #ddd;">{{ instance_url }}</td>
        </tr>
        <tr>
            <td style="padding: 8px; border: 1px solid #ddd;">Previous Status</td>
            <td style="padding: 8px; border: 1px solid #ddd;">{{ previous_status }}</td>
        </tr>
        <tr>
            <td style="padding: 8px; border: 1px solid #ddd;">Current Status</td>
            <td style="padding: 8px; border: 1px solid #ddd;">{{ current_status }}</td>
        </tr>
        <tr>
            <td style="padding: 8px; border: 1px solid #ddd;">Health Endpoint</td>
            <td style="padding: 8px; border: 1px solid #ddd;">{{ health_url }}</td>
        </tr>
        <tr>
            <td style="padding: 8px; border: 1px solid #ddd;">Time</td>
            <td style="padding: 8px; border: 1px solid #ddd;">{{ timestamp }}</td>
        </tr>
    </table>
</div>''',
                enabled=True
            )
            db.session.add(default_config)
            db.session.commit()

        break
    except Exception as e:
        if retry == 4:
            raise e
        time.sleep(1)

# Include routes
from app import routes
