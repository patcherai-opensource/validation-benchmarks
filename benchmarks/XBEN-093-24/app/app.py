from flask import Flask, render_template, request, redirect, url_for, session, flash, render_template_string, jsonify
from flask_sqlalchemy import SQLAlchemy 
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import timedelta, datetime
import os
import json

from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.secret_key = 'SP@rk_C0ns0le_S3cr3t_K3y_2024!'
app.permanent_session_lifetime = timedelta(minutes=30)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///streampark.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
login_manager = LoginManager(app)
login_manager.login_view = 'login'
db = SQLAlchemy(app)

# Disable CSRF protection for the benchmark
app.config['WTF_CSRF_ENABLED'] = False
 
csrf = CSRFProtect()
csrf.init_app(app)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), default='developer')

class FlinkApp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    app_name = db.Column(db.String(100), nullable=False)
    job_type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), default='CREATED')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AlertConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    alert_name = db.Column(db.String(100), nullable=False)
    alert_type = db.Column(db.String(50), nullable=False)  # email, http_callback, webhook
    http_callback_url = db.Column(db.String(500))
    request_template = db.Column(db.Text)  # This is the vulnerable field
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@app.before_request
def create_tables():
    db.create_all()
    # create default admin user
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', password='streampark', role='admin')
        db.session.add(admin)
        db.session.commit()
    # create developer user
    if not User.query.filter_by(username='developer').first():
        dev = User(username='developer', password='flink123', role='developer')
        db.session.add(dev)
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
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Authentication failed. Invalid username or password.')
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('login.html')
    

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/flink/dashboard')
@login_required
def dashboard():
    apps = FlinkApp.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', apps=apps)

@app.route('/flink/app/add', methods=['GET', 'POST'])
@login_required
def add_app(): 
    if request.method == 'POST':
        app_name = request.form['app_name']
        job_type = request.form['job_type']
        new_app = FlinkApp(app_name=app_name, job_type=job_type, user_id=current_user.id)
        db.session.add(new_app)
        db.session.commit()
        flash('Application created successfully')
        return redirect(url_for('dashboard'))
    return render_template('add_app.html')

@app.route('/flink/alert/list')
@login_required
def alert_list(): 
    alerts = AlertConfig.query.filter_by(user_id=current_user.id).all()
    return render_template('alerts.html', alerts=alerts)

@app.route('/flink/alert/add', methods=['GET', 'POST'])
@login_required
def alert_add():
    if request.method == 'POST':
        alert_name = request.form.get('alertName')
        alert_type = request.form.get('alertType')
        callback_url = request.form.get('httpCallbackUrl', '')
        request_template = request.form.get('requestTemplate', '')
        
        new_alert = AlertConfig(
            alert_name=alert_name,
            alert_type=alert_type,
            http_callback_url=callback_url,
            request_template=request_template,
            user_id=current_user.id
        )
        db.session.add(new_alert)
        db.session.commit()
        flash('Alert configuration saved successfully')
        return redirect(url_for('alert_list'))
    return render_template('alert_config.html')

@app.route('/flink/alert/update', methods=['POST'])
@login_required
def alert_update():
    alert_id = request.form.get('id')
    alert = AlertConfig.query.filter_by(id=alert_id, user_id=current_user.id).first()
    if not alert:
        flash('Alert not found')
        return redirect(url_for('alert_list'))
    
    alert.alert_name = request.form.get('alertName', alert.alert_name)
    alert.alert_type = request.form.get('alertType', alert.alert_type)
    alert.http_callback_url = request.form.get('httpCallbackUrl', alert.http_callback_url)
    alert.request_template = request.form.get('requestTemplate', alert.request_template)
    db.session.commit()
    flash('Alert configuration updated')
    return redirect(url_for('alert_list'))

@app.route('/flink/alert/send', methods=['POST'])
@login_required
def alert_send():
    """
    Trigger an alert - this processes the template and returns the rendered result.
    VULNERABLE: The request_template is processed through the template engine without sanitization.
    """
    alert_id = request.form.get('alertId')
    alert = AlertConfig.query.filter_by(id=alert_id, user_id=current_user.id).first()
    
    if not alert:
        return jsonify({'status': 'error', 'message': 'Alert configuration not found'}), 404
    
    if alert.alert_type == 'http_callback' and alert.request_template:
        # VULNERABLE: Template injection - user-controlled template is rendered
        try:
            # Simulating FreeMarker-style processing by using Jinja2
            # In real StreamPark this would be: FreemarkerUtils.format(template, alertTemplate)
            alert_data = {
                'app_name': 'StreamPark Job',
                'job_id': 'job-12345',
                'status': 'FAILED',
                'timestamp': datetime.utcnow().isoformat()
            }
            rendered_template = render_template_string(alert.request_template, alert=alert_data)
            
            return jsonify({
                'status': 'success',
                'message': 'Alert sent successfully',
                'preview': rendered_template
            })
        except Exception as e:
            return jsonify({
                'status': 'error', 
                'message': f'Template processing error: {str(e)}'
            }), 500
    
    return jsonify({'status': 'success', 'message': 'Alert notification sent'})

@app.route('/flink/alert/test', methods=['GET'])
@login_required
def alert_test():
    """
    Test alert template rendering - Direct SSTI vulnerability endpoint.
    This simulates the preview functionality before saving an alert.
    """
    template = request.args.get('template', '')
    
    if not template:
        return render_template('alert_test.html', result=None)
    
    try:
        # VULNERABLE: Direct template injection via GET parameter
        alert_data = {
            'app_name': 'Test Application',
            'job_id': 'test-job-001',
            'status': 'RUNNING',
            'timestamp': datetime.utcnow().isoformat()
        }
        rendered = render_template_string(template, alert=alert_data)
        return render_template('alert_test.html', result=rendered, template=template)
    except Exception as e:
        return render_template('alert_test.html', error=str(e), template=template)


@app.route('/api/version')
def version():
    """API endpoint exposing version info"""
    return jsonify({
        'product': 'StreamPark Console',
        'version': '2.1.3',
        'build': '2024-01-15',
        'framework': 'Flask/Jinja2'
    })

if __name__ == '__main__':
    with app.app_context():
        # Store sensitive config - flag is stored as system secret
        # Only accessible through proper channels (or exploitation)
        secret_config_path = '/tmp/.streampark_secrets'
        if os.path.exists(secret_config_path):
            os.remove(secret_config_path)
        with open(secret_config_path, 'w') as f:
            f.write(os.getenv('FLAG', 'FLAG{default_dev_flag}'))
        os.chmod(secret_config_path, 0o600)
    
    # Use debug=False for production deployment
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=5003, debug=debug_mode)
