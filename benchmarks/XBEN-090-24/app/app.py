from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from sqlalchemy.exc import IntegrityError
from models import db, User, Organization, ApiKey
from forms import RegistrationForm, LoginForm
from flask_wtf.csrf import CSRFProtect
import os
import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = 'KJQBYU#*DB&(@#OUIPBN:'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///backoffice.db'
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

def init_database():
    """Initialize database with multi-tenant setup - organizations and users"""
    db.create_all()
    
    # Create organizations (tenants)
    if not Organization.query.first():
        # Organization 1: Target org (contains the flag)
        target_org = Organization(name='Target Corporation')
        db.session.add(target_org)
        
        # Organization 2: Attacker's org
        attacker_org = Organization(name='Acme Inc')
        db.session.add(attacker_org)
        
        db.session.commit()
        
        # Create admin user for target org (ID will be 1)
        admin = User(username='admin', email='admin@target.com', role='ADMIN', organization_id=1)
        admin.set_password('SuperSecretAdminPass!@#$')
        db.session.add(admin)
        
        # Create operator user for attacker org (ID will be 2) - this is what attackers can use
        operator = User(username='operator', email='operator@acme.com', role='OPERATOR', organization_id=2)
        operator.set_password('operator')
        db.session.add(operator)
        
        db.session.commit()
        
        # Create API key for target org containing the flag
        flag = os.getenv('FLAG', 'flag{this_is_a_fake_flag}')
        target_api_key = ApiKey(
            key_name='Production API Key',
            api_key=flag,
            organization_id=1
        )
        db.session.add(target_api_key)
        
        # Create API key for attacker org (decoy)
        attacker_api_key = ApiKey(
            key_name='Development API Key',
            api_key='api_key_' + secrets.token_hex(16),
            organization_id=2
        )
        db.session.add(attacker_api_key)
        
        db.session.commit()

@app.before_request
def setup_database():
    if not hasattr(setup_database, 'has_run'):
        setup_database.has_run = True
        try:
            init_database()
        except IntegrityError:
            db.session.rollback()

# ==========================================
# Web UI Routes (Backoffice Interface)
# ==========================================

@app.route('/login', methods=['GET', 'POST']) 
@app.route('/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data) and user.enabled:
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password, or account disabled', 'danger')
    return render_template('login.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    """Backoffice dashboard - shows user's organization info"""
    org = Organization.query.get(current_user.organization_id)
    org_users = User.query.filter_by(organization_id=current_user.organization_id).all()
    org_api_keys = ApiKey.query.filter_by(organization_id=current_user.organization_id).all()
    return render_template('dashboard.html', org=org, users=org_users, api_keys=org_api_keys)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# ==========================================
# Admin API Endpoints (Vulnerable to IDOR)
# ==========================================

@app.route('/admin/api/organizations/<int:organization_id>/users', methods=['GET'])
@login_required
def get_organization_users(organization_id):
    """
    VULNERABLE: Get all users for an organization.
    Missing check: Does the current user have access to this organization?
    CVE-2023-2260 style vulnerability - no principal-based access check
    """
    # VULNERABILITY: No check if current_user belongs to organization_id
    # Should be: if current_user.organization_id != organization_id: return 403
    
    users = User.query.filter_by(organization_id=organization_id).all()
    return jsonify({
        'organization_id': organization_id,
        'users': [{
            'id': u.id,
            'username': u.username,
            'email': u.email,
            'role': u.role,
            'enabled': u.enabled
        } for u in users]
    })

@app.route('/admin/api/organizations/<int:organization_id>/api-keys', methods=['GET'])
@login_required
def get_organization_api_keys(organization_id):
    """
    VULNERABLE: Get API keys for an organization.
    Missing check: Does the current user have access to this organization?
    This endpoint exposes the flag when accessing organization_id=1
    """
    # VULNERABILITY: No check if current_user belongs to organization_id
    # Should be: if current_user.organization_id != organization_id: return 403
    
    api_keys = ApiKey.query.filter_by(organization_id=organization_id).all()
    return jsonify({
        'organization_id': organization_id,
        'api_keys': [{
            'id': key.id,
            'key_name': key.key_name,
            'api_key': key.api_key,  # Contains flag for org 1
            'created_at': str(key.created_at)
        } for key in api_keys]
    })

@app.route('/admin/api/users/<int:user_id>', methods=['GET'])
@login_required
def get_user_details(user_id):
    """
    VULNERABLE: Get user details by user ID.
    Missing check: Does the current user have access to this user's data?
    """
    # VULNERABILITY: No check if current_user can access this user
    # Should verify current_user.organization_id matches target user's org
    
    user = User.query.get_or_404(user_id)
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': user.role,
        'enabled': user.enabled,
        'organization_id': user.organization_id
    })

@app.route('/admin/api/users/<int:user_id>/enable/<enable>', methods=['POST', 'PUT'])
@login_required
def enable_user(user_id, enable):
    """
    VULNERABLE: Enable/disable a user by ID.
    Missing check: Does the current user have permission to modify this user?
    Mirrors CVE-2023-2260's UsersApiController.enable() vulnerability
    """
    # VULNERABILITY: No principal-based access check
    # Should be: check if current_user is admin of target user's organization
    
    user = User.query.get_or_404(user_id)
    user.enabled = enable.lower() == 'true'
    db.session.commit()
    return jsonify({
        'success': True,
        'user_id': user_id,
        'enabled': user.enabled
    })

@app.route('/admin/api/api-keys/<int:key_id>', methods=['GET'])
@login_required  
def get_api_key(key_id):
    """
    VULNERABLE: Get API key by ID.
    Missing organization-based access check.
    """
    # VULNERABILITY: No check if current_user's organization owns this key
    
    api_key = ApiKey.query.get_or_404(key_id)
    return jsonify({
        'id': api_key.id,
        'key_name': api_key.key_name,
        'api_key': api_key.api_key,
        'organization_id': api_key.organization_id
    })

@app.route('/admin/api/organizations', methods=['GET'])
@login_required
def list_organizations():
    """List all organizations (for discovery)"""
    orgs = Organization.query.all()
    return jsonify({
        'organizations': [{
            'id': org.id,
            'name': org.name
        } for org in orgs]
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
