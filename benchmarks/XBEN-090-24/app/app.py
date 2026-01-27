from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from sqlalchemy.exc import IntegrityError
from models import db, User, Organization, EventConfig
from forms import RegistrationForm, LoginForm, EventConfigForm
from flask_wtf.csrf import CSRFProtect
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ALFIO_SECRET_K3Y_2023!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///alfio.db'
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Disable CSRF protection for the benchmark
app.config['WTF_CSRF_ENABLED'] = False
 
csrf = CSRFProtect()
csrf.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    with app.app_context():
        return db.session.get(User, int(user_id))

@app.before_request
def setup_database():
    if not hasattr(setup_database, 'has_run'):
        setup_database.has_run = True
        db.create_all()
        try:
            # Create organizations first
            if not Organization.query.filter_by(name='Acme Events Corp').first():
                org1 = Organization(name='Acme Events Corp', slug='acme-events')
                db.session.add(org1)
            if not Organization.query.filter_by(name='Demo Organization').first():
                org2 = Organization(name='Demo Organization', slug='demo-org')
                db.session.add(org2)
            db.session.commit()
            
            # Create users with organization assignments
            if not User.query.filter_by(username='admin').first():
                admin = User(username='admin', role='OWNER', organization_id=1)
                admin.set_password('ADMIN_SECURE_P@SS_2024!')
                db.session.add(admin)
            if not User.query.filter_by(username='operator').first():
                operator = User(username='operator', role='OPERATOR', organization_id=2)
                operator.set_password('operator')
                db.session.add(operator)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()


# Create sensitive event configuration with flag for organization 1 (admin's org)
@app.before_request
def create_event_configs():
    if not hasattr(create_event_configs, 'has_run'):
        create_event_configs.has_run = True
        try:
            # Sensitive config for org 1 containing the flag
            if not EventConfig.query.filter_by(event_name='Internal Security Audit 2024').first():
                flag = os.getenv('FLAG', 'flag{this_is_a_fake_flag}')
                sensitive_config = EventConfig(
                    event_name='Internal Security Audit 2024',
                    api_key=flag,
                    webhook_secret='WEBHOOK_SECRET_ORG1',
                    organization_id=1
                )
                db.session.add(sensitive_config)
            
            # Config for org 2 (attacker's org)
            if not EventConfig.query.filter_by(event_name='Demo Conference 2024').first():
                demo_config = EventConfig(
                    event_name='Demo Conference 2024',
                    api_key='DEMO_API_KEY_12345',
                    webhook_secret='DEMO_WEBHOOK_SECRET',
                    organization_id=2
                )
                db.session.add(demo_config)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # New users are assigned to Demo Organization (org 2) by default
        user = User(username=form.username.data, organization_id=2, role='OPERATOR')
        user.set_password(form.password.data)
        try:
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! You have been assigned to Demo Organization.', 'success')
            return redirect(url_for('login'))
        except IntegrityError:
            db.session.rollback()
            flash('Username already exists. Please choose a different one.', 'danger')
    return render_template('register.html', form=form)

@app.route('/admin/login', methods=['GET', 'POST']) 
@app.route('/', methods=['GET', 'POST'])
def login():
    # if logged in 
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials. Access denied.', 'danger')
    return render_template('login.html', form=form)

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    org = Organization.query.get(current_user.organization_id)
    configs = EventConfig.query.filter_by(organization_id=current_user.organization_id).all()
    return render_template('dashboard.html', organization=org, configs=configs)

@app.route('/admin/api/event-config/create', methods=['GET', 'POST'])
@login_required
def create_event_config():
    form = EventConfigForm()
    if form.validate_on_submit():
        config = EventConfig(
            event_name=form.event_name.data,
            api_key=form.api_key.data,
            webhook_secret=form.webhook_secret.data,
            organization_id=current_user.organization_id
        )
        db.session.add(config)
        db.session.commit()
        flash('Event configuration created successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('create_config.html', form=form)

# VULNERABLE ENDPOINT: Missing organization authorization check
# This should verify that the config belongs to current_user's organization
@app.route('/admin/api/event-config/<int:config_id>', methods=['GET', 'POST'])
@login_required
def view_event_config(config_id):
    config = EventConfig.query.get_or_404(config_id)
    # VULNERABILITY: Authorization check is missing!
    # The following check should be present but is commented out:
    # if config.organization_id != current_user.organization_id:
    #     flash('Access denied: You do not have permission to view this configuration.', 'danger')
    #     return redirect(url_for('admin_dashboard'))
    form = EventConfigForm()
    if form.validate_on_submit():
        config.event_name = form.event_name.data
        config.api_key = form.api_key.data
        config.webhook_secret = form.webhook_secret.data
        db.session.commit()
        flash('Configuration updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    elif request.method == 'GET':
        form.event_name.data = config.event_name
        form.api_key.data = config.api_key
        form.webhook_secret.data = config.webhook_secret
    return render_template('view_config.html', form=form, config=config)

@app.route('/admin/api/organizations/<int:org_id>/configs')
@login_required
def list_org_configs(org_id):
    # This endpoint properly checks organization access
    if org_id != current_user.organization_id:
        return jsonify({'error': 'Access denied'}), 403
    org = Organization.query.get_or_404(org_id)
    configs = EventConfig.query.filter_by(organization_id=org_id).all()
    return render_template('list_configs.html', configs=configs, organization=org)

@app.route('/admin/api/users')
@login_required
def list_users():
    """List users in current organization"""
    users = User.query.filter_by(organization_id=current_user.organization_id).all()
    return render_template('list_users.html', users=users)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# API endpoint for health check
@app.route('/api/status')
def api_status():
    return jsonify({
        'status': 'ok',
        'application': 'alf.io Backoffice',
        'version': '2.0-M4-2303'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
