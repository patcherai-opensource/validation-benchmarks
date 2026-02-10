from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from sqlalchemy.exc import IntegrityError
from models import db, User, Organization, AuditLog
from forms import LoginForm
from flask_wtf.csrf import CSRFProtect
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'KJQBYU#*DB&(@#OUIPBN:'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///alfio.db'
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

app.config['WTF_CSRF_ENABLED'] = False
 
csrf = CSRFProtect()
csrf.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    with app.app_context():
        return db.session.get(User, int(user_id))

@app.before_request
def initialize_data():
    if not hasattr(initialize_data, 'has_run'):
        initialize_data.has_run = True
        db.create_all()
        try:
            if not Organization.query.filter_by(name='Acme Events').first():
                org1 = Organization(name='Acme Events', description='Primary event management organization')
                db.session.add(org1)
                db.session.flush()
                
                admin = User(username='admin', email='admin@acme-events.com', role='owner', organization_id=org1.id)
                admin.set_password('Acm3Ev3nts!2024')
                db.session.add(admin)
                
                operator1 = User(username='sarah.ops', email='sarah@acme-events.com', role='operator', organization_id=org1.id)
                operator1.set_password('operator123')
                db.session.add(operator1)
                
            if not Organization.query.filter_by(name='SecureTix').first():
                org2 = Organization(name='SecureTix', description='Confidential ticketing services')
                flag_value = os.getenv('FLAG', 'flag{this_is_a_fake_flag}')
                org2.api_key = flag_value
                db.session.add(org2)
                db.session.flush()
                
                secadmin = User(username='sec_admin', email='admin@securetix.io', role='owner', organization_id=org2.id)
                secadmin.set_password('S3cur3T1x!Adm1n')
                db.session.add(secadmin)
                
                secuser = User(username='ticket_agent', email='agent@securetix.io', role='operator', organization_id=org2.id)
                secuser.set_password('agent2024')
                db.session.add(secuser)
            
            if not Organization.query.filter_by(name='Demo Corp').first():
                org3 = Organization(name='Demo Corp', description='Demo organization for testing')
                db.session.add(org3)
                db.session.flush()
                
                demo_admin = User(username='demo_admin', email='admin@demo.local', role='admin', organization_id=org3.id)
                demo_admin.set_password('demo')
                db.session.add(demo_admin)
                
                demo_user = User(username='demo_user', email='user@demo.local', role='operator', organization_id=org3.id)
                demo_user.set_password('demo')
                db.session.add(demo_user)
                
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            if not user.enabled:
                flash('Account is disabled. Contact your administrator.', 'danger')
                return render_template('login.html', form=form)
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html', form=form)

@app.route('/admin/dashboard')
@login_required
def dashboard():
    org_users = User.query.filter_by(organization_id=current_user.organization_id).all()
    return render_template('dashboard.html', users=org_users, organization=current_user.organization)

@app.route('/admin/api/organizations')
@login_required
def list_organizations():
    if not (current_user.is_admin() or current_user.is_owner()):
        return jsonify({'error': 'Insufficient privileges'}), 403
    orgs = Organization.query.all()
    return jsonify([{
        'id': o.id,
        'name': o.name,
        'description': o.description
    } for o in orgs])

@app.route('/admin/api/organizations/<int:organization_id>')
@login_required
def get_organization(organization_id):
    org = Organization.query.get_or_404(organization_id)
    return jsonify({
        'id': org.id,
        'name': org.name,
        'description': org.description,
        'api_key': org.api_key,
        'user_count': len(org.users)
    })

@app.route('/admin/api/users')
@login_required
def list_users():
    organization_id = request.args.get('organizationId', type=int)
    if organization_id:
        users = User.query.filter_by(organization_id=organization_id).all()
    else:
        users = User.query.filter_by(organization_id=current_user.organization_id).all()
    return jsonify([{
        'id': u.id,
        'username': u.username,
        'email': u.email,
        'role': u.role,
        'enabled': u.enabled,
        'organization_id': u.organization_id
    } for u in users])

@app.route('/admin/api/users/<int:user_id>')
@login_required
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': user.role,
        'enabled': user.enabled,
        'organization_id': user.organization_id,
        'organization_name': user.organization.name
    })

@app.route('/admin/api/users/<int:user_id>/enable/<enable>', methods=['POST'])
@login_required
def enable_user(user_id, enable):
    user = User.query.get_or_404(user_id)
    enabled = enable.lower() == 'true'
    user.enabled = enabled
    
    audit = AuditLog(
        action='user_enable' if enabled else 'user_disable',
        target_user_id=user_id,
        performed_by_id=current_user.id,
        details=f'User {user.username} {"enabled" if enabled else "disabled"}'
    )
    db.session.add(audit)
    db.session.commit()
    
    return jsonify({'success': True, 'user_id': user_id, 'enabled': enabled})

@app.route('/admin/api/users/<int:user_id>/reset-password', methods=['PUT'])
@login_required
def reset_password(user_id):
    user = User.query.get_or_404(user_id)
    token = user.generate_reset_token()
    
    base_url = request.args.get('baseUrl', request.host_url.rstrip('/'))
    reset_link = f"{base_url}/reset/{token}"
    
    audit = AuditLog(
        action='password_reset',
        target_user_id=user_id,
        performed_by_id=current_user.id,
        details=f'Password reset initiated for {user.username}'
    )
    db.session.add(audit)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'user_id': user_id,
        'reset_link': reset_link,
        'token': token
    })

@app.route('/admin/api/users', methods=['POST'])
@login_required
def create_user():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid request body'}), 400
    
    organization_id = data.get('organizationId', current_user.organization_id)
    org = Organization.query.get(organization_id)
    if not org:
        return jsonify({'error': 'Organization not found'}), 404
    
    username = data.get('username')
    email = data.get('email')
    role = data.get('role', 'operator')
    
    if not username:
        return jsonify({'error': 'Username is required'}), 400
    
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 409
    
    new_user = User(
        username=username,
        email=email,
        role=role,
        organization_id=organization_id,
        enabled=True
    )
    new_user.set_password('changeme123')
    
    audit = AuditLog(
        action='user_create',
        target_user_id=None,
        performed_by_id=current_user.id,
        details=f'User {username} created in organization {org.name}'
    )
    
    db.session.add(new_user)
    db.session.add(audit)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'user': {
            'id': new_user.id,
            'username': new_user.username,
            'organization_id': new_user.organization_id
        }
    }), 201

@app.route('/admin/api/users/<int:user_id>', methods=['PUT'])
@login_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Invalid request body'}), 400
    
    if 'email' in data:
        user.email = data['email']
    if 'role' in data:
        user.role = data['role']
    if 'organizationId' in data:
        new_org = Organization.query.get(data['organizationId'])
        if new_org:
            user.organization_id = data['organizationId']
    
    audit = AuditLog(
        action='user_edit',
        target_user_id=user_id,
        performed_by_id=current_user.id,
        details=f'User {user.username} updated'
    )
    db.session.add(audit)
    db.session.commit()
    
    return jsonify({'success': True, 'user_id': user_id})

@app.route('/admin/api/users/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        return jsonify({'error': 'Cannot delete your own account'}), 400
    
    username = user.username
    audit = AuditLog(
        action='user_delete',
        target_user_id=user_id,
        performed_by_id=current_user.id,
        details=f'User {username} deleted'
    )
    
    db.session.delete(user)
    db.session.add(audit)
    db.session.commit()
    
    return jsonify({'success': True, 'deleted_user': username})

@app.route('/admin/api/organizations/<int:organization_id>/api-key', methods=['POST'])
@login_required
def generate_api_key(organization_id):
    org = Organization.query.get_or_404(organization_id)
    
    import secrets
    org.api_key = secrets.token_urlsafe(32)
    
    audit = AuditLog(
        action='api_key_generated',
        target_user_id=None,
        performed_by_id=current_user.id,
        details=f'API key generated for organization {org.name}'
    )
    db.session.add(audit)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'organization_id': organization_id,
        'api_key': org.api_key
    })

@app.route('/admin/users')
@login_required
def users_page():
    org_users = User.query.filter_by(organization_id=current_user.organization_id).all()
    return render_template('users.html', users=org_users, organization=current_user.organization)

@app.route('/admin/organizations')
@login_required
def organizations_page():
    if not (current_user.is_admin() or current_user.is_owner()):
        flash('Insufficient privileges to view organizations', 'danger')
        return redirect(url_for('dashboard'))
    return render_template('organizations.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
