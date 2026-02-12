import os
import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User, ManagedNode, TaskResult, Playbook


app = Flask(__name__)

app.secret_key = os.environ.get('SECRET_KEY', 'ansible_controller_session_key')

# MySQL configurations
db_host = os.environ.get('DB_HOST', '127.0.0.1')
db_user = os.environ.get('DB_USER', 'root')
db_password = os.environ.get('DB_PASSWORD', 'ansible_controller')
db_name = os.environ.get('DB_NAME', 'ansible_controller')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)
app.app_context().push()
db.create_all()

# Seed default admin user
admin = User.query.filter_by(username='admin').first()
if not admin:
    admin = User(
        username='admin',
        password='admin',
        name='Administrator',
        email='admin@infra.local',
        role='admin'
    )
    db.session.add(admin)
    db.session.commit()

# Seed operator user
operator = User.query.filter_by(username='operator').first()
if not operator:
    operator = User(
        username='operator',
        password='operator123',
        name='Ops Team',
        email='ops@infra.local',
        role='operator'
    )
    db.session.add(operator)
    db.session.commit()

# Seed managed nodes
if ManagedNode.query.count() == 0:
    nodes = [
        ManagedNode(hostname='web-prod-01', ip_address='10.0.1.10', group_name='webservers',
                    ssh_port=22, status='reachable', last_seen=datetime.datetime.utcnow()),
        ManagedNode(hostname='web-prod-02', ip_address='10.0.1.11', group_name='webservers',
                    ssh_port=22, status='reachable', last_seen=datetime.datetime.utcnow()),
        ManagedNode(hostname='db-prod-01', ip_address='10.0.2.10', group_name='databases',
                    ssh_port=22, status='reachable', last_seen=datetime.datetime.utcnow()),
        ManagedNode(hostname='cache-prod-01', ip_address='10.0.3.10', group_name='cache',
                    ssh_port=22, status='unreachable'),
        ManagedNode(hostname='monitor-01', ip_address='10.0.4.10', group_name='monitoring',
                    ssh_port=2222, status='reachable', last_seen=datetime.datetime.utcnow()),
    ]
    db.session.add_all(nodes)
    db.session.commit()

# Seed some task results with normal output
if TaskResult.query.count() == 0:
    results = [
        TaskResult(
            node_hostname='web-prod-01', task_name='Gather Facts',
            module_name='setup', status='ok',
            stdout='', stderr='',
            facts='{"ansible_os_family": "Debian", "ansible_distribution": "Ubuntu", "ansible_distribution_version": "22.04", "ansible_memtotal_mb": 4096}',
            msg='Facts gathered successfully',
            executed_at=datetime.datetime.utcnow() - datetime.timedelta(hours=2)
        ),
        TaskResult(
            node_hostname='web-prod-01', task_name='Install nginx',
            module_name='apt', status='changed',
            stdout='Reading package lists...\nBuilding dependency tree...\nnginx is already the newest version (1.18.0-6ubuntu14.4).',
            stderr='',
            facts='{}',
            msg='Package nginx installed',
            executed_at=datetime.datetime.utcnow() - datetime.timedelta(hours=1)
        ),
        TaskResult(
            node_hostname='db-prod-01', task_name='Check MySQL status',
            module_name='service', status='ok',
            stdout='',
            stderr='',
            facts='{}',
            msg='MySQL service is running',
            executed_at=datetime.datetime.utcnow() - datetime.timedelta(minutes=30)
        ),
        TaskResult(
            node_hostname='web-prod-02', task_name='Deploy application',
            module_name='git', status='changed',
            stdout='Already on branch main\nUpdating a1b2c3d..e4f5g6h\nFast-forward\n 3 files changed, 45 insertions(+), 12 deletions(-)',
            stderr='',
            facts='{}',
            msg='Repository updated to latest',
            executed_at=datetime.datetime.utcnow() - datetime.timedelta(minutes=15)
        ),
    ]
    db.session.add_all(results)
    db.session.commit()

# Seed playbooks
if Playbook.query.count() == 0:
    playbooks = [
        Playbook(
            name='site.yml',
            description='Main site playbook - configures all servers',
            content='---\n- hosts: all\n  become: yes\n  roles:\n    - common\n    - security\n\n- hosts: webservers\n  become: yes\n  roles:\n    - nginx\n    - app-deploy\n\n- hosts: databases\n  become: yes\n  roles:\n    - mysql\n    - backup',
            created_by=1,
            created_at=datetime.datetime.utcnow() - datetime.timedelta(days=30)
        ),
        Playbook(
            name='deploy.yml',
            description='Application deployment playbook',
            content='---\n- hosts: webservers\n  become: yes\n  tasks:\n    - name: Pull latest code\n      git:\n        repo: https://git.infra.local/app.git\n        dest: /opt/app\n        version: main\n    - name: Restart application\n      service:\n        name: app\n        state: restarted',
            created_by=1,
            created_at=datetime.datetime.utcnow() - datetime.timedelta(days=15)
        ),
        Playbook(
            name='gather_facts.yml',
            description='Gather system facts from all managed nodes',
            content='---\n- hosts: all\n  gather_facts: yes\n  tasks:\n    - name: Display OS info\n      debug:\n        msg: "{{ ansible_os_family }} {{ ansible_distribution_version }}"',
            created_by=1,
            created_at=datetime.datetime.utcnow() - datetime.timedelta(days=7)
        ),
    ]
    db.session.add_all(playbooks)
    db.session.commit()

# Include routes
from app import routes
