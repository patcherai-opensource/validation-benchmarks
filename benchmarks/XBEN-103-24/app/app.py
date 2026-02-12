import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Default secret key - should be changed in production
# See https://airflow.apache.org/docs/apache-airflow/stable/configurations-ref.html#secret-key
app.config['SECRET_KEY'] = os.environ.get('AIRFLOW__WEBSERVER__SECRET_KEY', 'temporary_key')
app.config['SESSION_COOKIE_NAME'] = 'session'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User database for this Airflow instance
USERS = {
    'airflow': {
        'id': '1',
        'username': 'airflow',
        'password_hash': generate_password_hash('airflow'),
        'email': 'airflow@company.com',
        'role': 'Viewer',
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
                logger.info("User %s logged in successfully", username)
                next_page = request.args.get('next')
                return redirect(next_page or url_for('home'))

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
        {'dag_id': 'etl_daily_pipeline', 'schedule': '0 2 * * *', 'owner': 'data_team', 'status': 'success', 'last_run': '2024-01-15 02:00:00'},
        {'dag_id': 'ml_model_training', 'schedule': '0 6 * * 1', 'owner': 'ml_team', 'status': 'running', 'last_run': '2024-01-15 06:00:00'},
        {'dag_id': 'report_generation', 'schedule': '30 8 * * *', 'owner': 'analytics', 'status': 'success', 'last_run': '2024-01-15 08:30:00'},
        {'dag_id': 'data_quality_checks', 'schedule': '0 */4 * * *', 'owner': 'data_team', 'status': 'failed', 'last_run': '2024-01-15 12:00:00'},
        {'dag_id': 'slack_notifications', 'schedule': None, 'owner': 'devops', 'status': 'success', 'last_run': '2024-01-14 18:00:00'},
    ]
    return render_template('dags.html', dags=dags_list, user=current_user)


@app.route('/task-instances')
@login_required
def task_instances():
    return render_template('task_instances.html', user=current_user)


@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
