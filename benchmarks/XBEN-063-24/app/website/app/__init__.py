import os
import hashlib
from flask import Flask
from app.db import db
from app.models import Operator, ManagedNode, TaskResult, NodeFact
from datetime import datetime, timedelta


app = Flask(__name__)

app.secret_key = os.environ.get('SECRET_KEY', 'np-session-key-2024')

db_host = os.environ.get('DB_HOST', '127.0.0.1')
db_user = os.environ.get('DB_USER', 'root')
db_password = os.environ.get('DB_PASSWORD', 'nodepilot_db')
db_name = os.environ.get('DB_NAME', 'nodepilot')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
app.app_context().push()
db.create_all()

def _hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

# Seed default operator account
op = Operator.query.filter_by(username='admin').first()
if not op:
    op = Operator(
        username='admin',
        password_hash=_hash_pw('admin'),
        display_name='System Administrator',
        role='admin'
    )
    db.session.add(op)
    db.session.commit()

# Seed some managed nodes
if ManagedNode.query.count() == 0:
    nodes_data = [
        {'hostname': 'web-prod-01.internal', 'ip_address': '10.0.1.10', 'node_group': 'webservers',
         'os_info': 'Ubuntu 22.04 LTS', 'status': 'online'},
        {'hostname': 'web-prod-02.internal', 'ip_address': '10.0.1.11', 'node_group': 'webservers',
         'os_info': 'Ubuntu 22.04 LTS', 'status': 'online'},
        {'hostname': 'db-prod-01.internal', 'ip_address': '10.0.2.10', 'node_group': 'databases',
         'os_info': 'CentOS 8', 'status': 'online'},
        {'hostname': 'cache-prod-01.internal', 'ip_address': '10.0.3.10', 'node_group': 'caching',
         'os_info': 'Debian 11', 'status': 'online'},
        {'hostname': 'monitor-01.internal', 'ip_address': '10.0.4.10', 'node_group': 'monitoring',
         'os_info': 'Ubuntu 20.04 LTS', 'status': 'offline'},
    ]
    base_time = datetime.utcnow() - timedelta(hours=2)
    for i, nd in enumerate(nodes_data):
        node = ManagedNode(
            hostname=nd['hostname'],
            ip_address=nd['ip_address'],
            node_group=nd['node_group'],
            os_info=nd['os_info'],
            status=nd['status'],
            last_checkin=base_time + timedelta(minutes=i * 15),
            registered_at=datetime.utcnow() - timedelta(days=30 + i)
        )
        db.session.add(node)
    db.session.commit()

    # Seed some task results for existing nodes
    all_nodes = ManagedNode.query.all()
    tasks_data = [
        {'task_name': 'Gather system facts', 'module_name': 'setup', 'status': 'ok',
         'output_data': '{"ansible_hostname": "web-prod-01", "ansible_os_family": "Debian"}', 'changed': False},
        {'task_name': 'Install nginx', 'module_name': 'apt', 'status': 'changed',
         'output_data': '{"msg": "nginx installed successfully", "rc": 0}', 'changed': True},
        {'task_name': 'Start nginx service', 'module_name': 'service', 'status': 'ok',
         'output_data': '{"msg": "nginx is running", "state": "started"}', 'changed': False},
        {'task_name': 'Deploy application config', 'module_name': 'template', 'status': 'changed',
         'output_data': '{"dest": "/etc/nginx/sites-available/default", "changed": true}', 'changed': True},
    ]
    for node in all_nodes[:3]:
        for j, td in enumerate(tasks_data):
            tr = TaskResult(
                node_id=node.id,
                task_name=td['task_name'],
                module_name=td['module_name'],
                status=td['status'],
                output_data=td['output_data'],
                changed=td['changed'],
                executed_at=base_time + timedelta(minutes=j * 5)
            )
            db.session.add(tr)
    db.session.commit()

from app import routes
