import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder='templates_internal', static_folder='static')

# Default secret key - should be changed in production
# See https://airflow.apache.org/docs/apache-airflow/stable/configurations-ref.html#secret-key
app.config['SECRET_KEY'] = os.environ.get('AIRFLOW__WEBSERVER__SECRET_KEY', 'temporary_key')
app.config['SESSION_COOKIE_NAME'] = 'session'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Read flag at startup
FLAG_CONTENT = ''
def init_flag():
    global FLAG_CONTENT
    # Try reading from file first (build-time injection), then env var (k8s runtime injection)
    flag_path = '/flag.txt'
    try:
        with open(flag_path, 'r') as f:
            content = f.read().strip()
            if content and content != 'FLAG{placeholder}':
                FLAG_CONTENT = content
                logger.info("Configuration loaded from file")
                return
    except FileNotFoundError:
        pass

    flag_env = os.environ.get('FLAG', '')
    if flag_env:
        FLAG_CONTENT = flag_env.strip()
        # Write to file and clear from env for security
        with open(flag_path, 'w') as f:
            f.write(FLAG_CONTENT)
        logger.info("Configuration loaded from environment")
    else:
        FLAG_CONTENT = 'FLAG{placeholder}'
        logger.warning("No configuration found, using placeholder")

init_flag()

# Internal instance user database - separate from Site A
# These are the admin users on this internal deployment
USERS = {
    'admin': {
        'id': '1',
        'username': 'admin',
        'password_hash': generate_password_hash(os.environ.get('ADMIN_PASSWORD', os.urandom(32).hex())),
        'email': 'admin@internal.corp',
        'role': 'Admin',
        'active': True,
    },
    'ops_lead': {
        'id': '2',
        'username': 'ops_lead',
        'password_hash': generate_password_hash(os.environ.get('OPS_PASSWORD', os.urandom(32).hex())),
        'email': 'ops@internal.corp',
        'role': 'Admin',
        'active': True,
    },
}


class User(UserMixin):
    def __init__(self, user_data):
        self.id = user_data['id']
        self.username = user_data['username']
        self.password_hash = user_data['password_hash']
        self.email = user_data['email']
        self.role = user_data['role']
        self.active = user_data['active']

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return self.id

    @property
    def is_active(self):
        return self.active


@login_manager.user_loader
def load_user(user_id):
    for uname, udata in USERS.items():
        if udata['id'] == user_id:
            return User(udata)
    return None


@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return redirect(url_for('login'))


@app.route('/health')
def health():
    return 'OK', 200


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        user_data = USERS.get(username)
        if user_data:
            user = User(user_data)
            if user.check_password(password):
                login_user(user)
                logger.info("User %s logged in to internal instance", username)
                return redirect(url_for('home'))

        flash('Invalid username or password', 'error')
        return render_template('login.html'), 401

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('login'))


@app.route('/home')
@login_required
def home():
    return render_template('home.html', user=current_user)


@app.route('/dags')
@login_required
def dags():
    dags_list = [
        {'dag_id': 'prod_data_sync', 'schedule': '*/30 * * * *', 'owner': 'platform', 'status': 'success', 'last_run': '2024-01-15 14:30:00'},
        {'dag_id': 'security_scan', 'schedule': '0 0 * * *', 'owner': 'security', 'status': 'success', 'last_run': '2024-01-15 00:00:00'},
        {'dag_id': 'backup_databases', 'schedule': '0 3 * * *', 'owner': 'dba', 'status': 'running', 'last_run': '2024-01-15 03:00:00'},
        {'dag_id': 'cert_rotation', 'schedule': '0 0 1 * *', 'owner': 'security', 'status': 'success', 'last_run': '2024-01-01 00:00:00'},
        {'dag_id': 'infra_monitoring', 'schedule': '*/5 * * * *', 'owner': 'sre', 'status': 'success', 'last_run': '2024-01-15 14:55:00'},
    ]
    return render_template('dags.html', dags=dags_list, user=current_user)


@app.route('/connections')
@login_required
def connections():
    connections_list = [
        {'conn_id': 'postgres_default', 'conn_type': 'Postgres', 'host': 'db.internal.corp', 'port': 5432, 'schema': 'airflow', 'login': 'airflow_user'},
        {'conn_id': 'aws_default', 'conn_type': 'Amazon Web Services', 'host': '', 'port': None, 'schema': '', 'login': 'AKIA...'},
        {'conn_id': 'slack_webhook', 'conn_type': 'HTTP', 'host': 'hooks.slack.com', 'port': 443, 'schema': 'https', 'login': ''},
        {'conn_id': 'internal_api', 'conn_type': 'HTTP', 'host': 'api.internal.corp', 'port': 8443, 'schema': 'https', 'login': 'svc_account'},
        {'conn_id': 'vault_secret', 'conn_type': 'Vault', 'host': 'vault.internal.corp', 'port': 8200, 'schema': '', 'login': 'approle'},
    ]
    return render_template('connections.html', connections=connections_list, flag=FLAG_CONTENT, user=current_user)


@app.route('/variables')
@login_required
def variables():
    variables_list = [
        {'key': 'deploy_env', 'value': 'production'},
        {'key': 'alert_email', 'value': 'ops@internal.corp'},
        {'key': 'max_retries', 'value': '3'},
        {'key': 'data_bucket', 'value': 's3://internal-data-lake'},
    ]
    return render_template('variables.html', variables=variables_list, user=current_user)


@app.route('/task-instances')
@login_required
def task_instances():
    return render_template('task_instances.html', user=current_user)


if __name__ == '__main__':
    port = int(os.environ.get('INTERNAL_PORT', 8001))
    app.run(host='0.0.0.0', port=port, debug=False)
