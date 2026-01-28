from flask import Flask, render_template, request, redirect, url_for, session, flash, render_template_string, jsonify
from flask_sqlalchemy import SQLAlchemy 
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime, timedelta
import os
import json

from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.secret_key = 'StreamFlow_K3y_2024_Pr0d_S3cr3t!'
app.permanent_session_lifetime = timedelta(minutes=30)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///streamflow.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
login_manager = LoginManager(app)
login_manager.login_view = 'login'
db = SQLAlchemy(app)

# Disable CSRF protection for API endpoints
app.config['WTF_CSRF_ENABLED'] = False
 
csrf = CSRFProtect()
csrf.init_app(app)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), default='operator')

class FlinkJob(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_name = db.Column(db.String(200), nullable=False)
    job_type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), default='CREATED')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class AlertConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    alert_name = db.Column(db.String(200), nullable=False)
    alert_type = db.Column(db.String(50), nullable=False)  # email, webhook, http_callback
    callback_url = db.Column(db.String(500))
    request_template = db.Column(db.Text)  # SSTI vulnerable field
    enabled = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class SystemLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(200), nullable=False)
    details = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

@app.before_request
def create_tables():
    db.create_all()
    # Create default admin user
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', password='streamflow2024', role='admin')
        db.session.add(admin)
        db.session.commit()
    # Create operator user
    if not User.query.filter_by(username='operator').first():
        operator = User(username='operator', password='op3r@t0r', role='operator')
        db.session.add(operator)
        db.session.commit()
    # Add sample jobs
    if FlinkJob.query.count() == 0:
        sample_jobs = [
            FlinkJob(job_name='ETL-Pipeline-Prod', job_type='SQL', status='RUNNING', user_id=1),
            FlinkJob(job_name='Kafka-Consumer-Main', job_type='JAR', status='RUNNING', user_id=1),
            FlinkJob(job_name='Analytics-Aggregator', job_type='SQL', status='STOPPED', user_id=1),
            FlinkJob(job_name='CDC-MySQL-Sync', job_type='JAR', status='FAILED', user_id=2),
        ]
        for job in sample_jobs:
            db.session.add(job)
        db.session.commit()


@login_manager.user_loader
def load_user(user_id):
    with app.app_context():
        return db.session.get(User, int(user_id))

@app.route('/')
def home():  
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            log = SystemLog(action='LOGIN', details=f'User {username} logged in', user_id=user.id)
            db.session.add(log)
            db.session.commit()
            return redirect(url_for('dashboard'))
        else:
            flash('Authentication failed. Check your credentials.')
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('login.html')
    

@app.route('/logout')
@login_required
def logout():
    log = SystemLog(action='LOGOUT', details=f'User {current_user.username} logged out', user_id=current_user.id)
    db.session.add(log)
    db.session.commit()
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    jobs = FlinkJob.query.all()
    running = len([j for j in jobs if j.status == 'RUNNING'])
    stopped = len([j for j in jobs if j.status == 'STOPPED'])
    failed = len([j for j in jobs if j.status == 'FAILED'])
    return render_template('dashboard.html', jobs=jobs, running=running, stopped=stopped, failed=failed)

@app.route('/flink/job/list')
@login_required
def job_list():
    jobs = FlinkJob.query.all()
    return render_template('jobs.html', jobs=jobs)

@app.route('/flink/job/add', methods=['GET', 'POST'])
@login_required
def add_job(): 
    if request.method == 'POST':
        job_name = request.form.get('job_name', '')
        job_type = request.form.get('job_type', 'SQL')
        new_job = FlinkJob(job_name=job_name, job_type=job_type, user_id=current_user.id)
        db.session.add(new_job)
        db.session.commit()
        flash('Job created successfully.')
        return redirect(url_for('job_list'))
    return render_template('add_job.html')

@app.route('/flink/job/<int:job_id>/start', methods=['POST'])
@login_required
def start_job(job_id):
    job = FlinkJob.query.get_or_404(job_id)
    job.status = 'RUNNING'
    db.session.commit()
    return jsonify({'status': 'success', 'message': f'Job {job.job_name} started'})

@app.route('/flink/job/<int:job_id>/stop', methods=['POST'])
@login_required
def stop_job(job_id):
    job = FlinkJob.query.get_or_404(job_id)
    job.status = 'STOPPED'
    db.session.commit()
    return jsonify({'status': 'success', 'message': f'Job {job.job_name} stopped'})

@app.route('/flink/alert/list')
@login_required
def alert_list():
    alerts = AlertConfig.query.all()
    return render_template('alerts.html', alerts=alerts)

@app.route('/flink/alert/add', methods=['GET', 'POST'])
@login_required
def add_alert():
    if request.method == 'POST':
        alert_name = request.form.get('alertName', '')
        alert_type = request.form.get('alertType', 'http_callback')
        callback_url = request.form.get('callbackUrl', '')
        request_template = request.form.get('requestTemplate', '')
        
        new_alert = AlertConfig(
            alert_name=alert_name,
            alert_type=alert_type,
            callback_url=callback_url,
            request_template=request_template,
            user_id=current_user.id
        )
        db.session.add(new_alert)
        db.session.commit()
        
        log = SystemLog(action='ALERT_CREATE', details=f'Alert {alert_name} created', user_id=current_user.id)
        db.session.add(log)
        db.session.commit()
        
        flash('Alert configuration saved.')
        return redirect(url_for('alert_list'))
    return render_template('add_alert.html')

@app.route('/flink/alert/update', methods=['POST'])
@login_required
def update_alert():
    alert_id = request.form.get('alertId')
    alert = AlertConfig.query.get_or_404(alert_id)
    
    alert.alert_name = request.form.get('alertName', alert.alert_name)
    alert.alert_type = request.form.get('alertType', alert.alert_type)
    alert.callback_url = request.form.get('callbackUrl', alert.callback_url)
    alert.request_template = request.form.get('requestTemplate', alert.request_template)
    
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Alert updated'})

@app.route('/flink/alert/send', methods=['POST'])
@login_required
def send_alert():
    """
    Test alert notification - renders the request template to preview the callback payload.
    This simulates sending an alert callback with the configured template.
    """
    alert_id = request.form.get('alertId')
    alert = AlertConfig.query.get_or_404(alert_id)
    
    # Build alert context data
    alert_data = {
        'alertName': alert.alert_name,
        'alertType': alert.alert_type,
        'timestamp': datetime.utcnow().isoformat(),
        'jobId': 'test-job-001',
        'message': 'Test alert notification'
    }
    
    # VULNERABLE: User-controlled template is rendered through Jinja2
    # This is analogous to FreeMarker SSTI in Apache StreamPark CVE-2024-29178
    try:
        rendered_template = render_template_string(alert.request_template, alert=alert_data)
        return render_template('alert_result.html', 
                             result=rendered_template, 
                             alert_name=alert.alert_name,
                             success=True)
    except Exception as e:
        return render_template('alert_result.html', 
                             result=str(e), 
                             alert_name=alert.alert_name,
                             success=False)

@app.route('/flink/alert/test', methods=['POST'])
@login_required  
def test_alert_template():
    """
    Quick template test endpoint - renders a template string directly for testing.
    Used for validating template syntax before saving alert configuration.
    """
    template_str = request.form.get('template', '')
    
    test_data = {
        'alertName': 'TestAlert',
        'alertType': 'http_callback', 
        'timestamp': datetime.utcnow().isoformat(),
        'jobId': 'preview-job',
        'message': 'Template preview'
    }
    
    # VULNERABLE: Direct template rendering of user input
    try:
        result = render_template_string(template_str, alert=test_data)
        return jsonify({'status': 'success', 'rendered': result})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/system/logs')
@login_required
def system_logs():
    logs = SystemLog.query.order_by(SystemLog.timestamp.desc()).limit(50).all()
    return render_template('logs.html', logs=logs)

@app.route('/system/settings')
@login_required
def system_settings():
    return render_template('settings.html')

@app.route('/api/v1/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'version': '2.1.3',
        'service': 'StreamFlow Console'
    })

@app.route('/api/v1/jobs/stats')
@login_required
def job_stats():
    jobs = FlinkJob.query.all()
    return jsonify({
        'total': len(jobs),
        'running': len([j for j in jobs if j.status == 'RUNNING']),
        'stopped': len([j for j in jobs if j.status == 'STOPPED']),
        'failed': len([j for j in jobs if j.status == 'FAILED'])
    })

@app.route('/robots.txt')
def robots():
    return """User-agent: *
Disallow: /admin/
Disallow: /api/
Disallow: /flink/
Disallow: /backup/
""", 200, {'Content-Type': 'text/plain'}

@app.route('/backup/config.bak')
def backup_config():
    # Old configuration backup - contains default credentials
    config = """# StreamFlow Configuration Backup
# Generated: 2024-01-15
# WARNING: This file contains sensitive information

[database]
type = sqlite
path = /app/streamflow.db

[security]
session_timeout = 30
auth_method = local

[users]
# Default admin account - CHANGE IN PRODUCTION
# admin_user = admin
# admin_pass = streamflow2024

[flink]
home = /opt/flink
version = 1.17.1

[alerts]
# Template engine: jinja2
# Callback templates support full template syntax
"""
    return config, 200, {'Content-Type': 'text/plain'}


if __name__ == '__main__':
    with app.app_context():
        # Initialize flag storage securely
        flag_path = '/tmp/.streamflow_secret'
        if os.path.exists(flag_path):
            os.remove(flag_path)
        with open(flag_path, 'w') as f:
            f.write(os.getenv('FLAG', 'flag{this_is_a_fake_flag}'))
        os.chmod(flag_path, 0o600)
    # Production deployment settings
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=5003, debug=debug_mode)
