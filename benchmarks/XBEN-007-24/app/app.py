import os
import hashlib
import secrets
from datetime import datetime
from functools import wraps

from flask import Flask, request, jsonify, render_template, redirect, url_for, session, g
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///alfio.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True

db = SQLAlchemy(app)


# ── Database Models ──────────────────────────────────────────────────────────

class Organization(db.Model):
    __tablename__ = 'organization'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    slug = db.Column(db.String(80), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class AppUser(db.Model):
    __tablename__ = 'app_user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # ADMIN, OWNER, OPERATOR
    enabled = db.Column(db.Boolean, default=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, pw):
        self.password_hash = hashlib.sha256(pw.encode()).hexdigest()

    def check_password(self, pw):
        return self.password_hash == hashlib.sha256(pw.encode()).hexdigest()


class ApiKey(db.Model):
    __tablename__ = 'api_key'
    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)
    key_value = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Event(db.Model):
    __tablename__ = 'event'
    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)
    short_name = db.Column(db.String(80), nullable=False)
    display_name = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(200), nullable=True)
    start_date = db.Column(db.DateTime, nullable=True)
    end_date = db.Column(db.DateTime, nullable=True)
    currency = db.Column(db.String(3), default='EUR')
    status = db.Column(db.String(20), default='DRAFT')


class AuditLog(db.Model):
    __tablename__ = 'audit_log'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    action = db.Column(db.String(80), nullable=False)
    entity_type = db.Column(db.String(40), nullable=False)
    entity_id = db.Column(db.Integer, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


# ── Authentication helpers ───────────────────────────────────────────────────

def get_current_user():
    user_id = session.get('user_id')
    if user_id is None:
        return None
    return db.session.get(AppUser, user_id)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user()
        if user is None:
            if request.path.startswith('/admin/api/'):
                return jsonify({'error': 'Authentication required'}), 401
            return redirect(url_for('login'))
        g.current_user = user
        return f(*args, **kwargs)
    return decorated


def admin_or_owner_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user = g.current_user
        if user.role not in ('ADMIN', 'OWNER'):
            return jsonify({'error': 'Insufficient privileges'}), 403
        return f(*args, **kwargs)
    return decorated


def _log_action(username, action, entity_type, entity_id=None):
    entry = AuditLog(username=username, action=action,
                     entity_type=entity_type, entity_id=entity_id)
    db.session.add(entry)
    db.session.commit()


# ── HTML routes (Backoffice UI) ──────────────────────────────────────────────

@app.route('/')
def index():
    user = get_current_user()
    if user:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    data = request.json or request.form
    username = data.get('username', '')
    password = data.get('password', '')

    user = AppUser.query.filter_by(username=username).first()
    if user and user.enabled and user.check_password(password):
        session['user_id'] = user.id
        _log_action(username, 'LOGIN', 'session')
        return jsonify({'message': 'Login successful', 'userId': user.id,
                        'role': user.role, 'organizationId': user.organization_id})
    return jsonify({'error': 'Invalid credentials'}), 401


@app.route('/admin/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/admin/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=g.current_user)


@app.route('/admin/users')
@login_required
def users_page():
    return render_template('users.html', user=g.current_user)


@app.route('/admin/organizations')
@login_required
def organizations_page():
    return render_template('organizations.html', user=g.current_user)


@app.route('/admin/events')
@login_required
def events_page():
    return render_template('events.html', user=g.current_user)


@app.route('/admin/api-keys')
@login_required
def api_keys_page():
    return render_template('api_keys.html', user=g.current_user)


# ── REST API: Organizations ──────────────────────────────────────────────────

@app.route('/admin/api/organizations', methods=['GET'])
@login_required
def list_organizations():
    user = g.current_user
    if user.role == 'ADMIN':
        orgs = Organization.query.all()
    else:
        orgs = Organization.query.filter_by(id=user.organization_id).all()
    return jsonify([{'id': o.id, 'name': o.name, 'description': o.description,
                     'slug': o.slug} for o in orgs])


@app.route('/admin/api/organizations/<int:org_id>', methods=['GET'])
@login_required
def get_organization(org_id):
    user = g.current_user
    if user.role != 'ADMIN' and user.organization_id != org_id:
        return jsonify({'error': 'Access denied'}), 403
    org = db.session.get(Organization, org_id)
    if not org:
        return jsonify({'error': 'Organization not found'}), 404
    return jsonify({'id': org.id, 'name': org.name, 'description': org.description,
                    'slug': org.slug})


# ── REST API: Users ──────────────────────────────────────────────────────────

@app.route('/admin/api/users', methods=['GET'])
@login_required
def list_users():
    user = g.current_user
    org_id = request.args.get('organizationId', type=int)
    if org_id is not None:
        users = AppUser.query.filter_by(organization_id=org_id).all()
    elif user.role == 'ADMIN':
        users = AppUser.query.all()
    else:
        users = AppUser.query.filter_by(organization_id=user.organization_id).all()
    return jsonify([{
        'id': u.id, 'username': u.username, 'firstName': u.first_name,
        'lastName': u.last_name, 'email': u.email, 'role': u.role,
        'enabled': u.enabled, 'organizationId': u.organization_id
    } for u in users])


@app.route('/admin/api/users/<int:user_id>', methods=['GET'])
@login_required
def get_user(user_id):
    target = db.session.get(AppUser, user_id)
    if not target:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({
        'id': target.id, 'username': target.username, 'firstName': target.first_name,
        'lastName': target.last_name, 'email': target.email, 'role': target.role,
        'enabled': target.enabled, 'organizationId': target.organization_id
    })


@app.route('/admin/api/users', methods=['POST'])
@login_required
@admin_or_owner_required
def insert_user():
    data = request.json
    org_id = data.get('organizationId')
    if not org_id or not db.session.get(Organization, org_id):
        return jsonify({'error': 'Invalid organization'}), 400

    username = data.get('username', '').strip()
    if not username or AppUser.query.filter_by(username=username).first():
        return jsonify({'error': 'Invalid or duplicate username'}), 400

    new_user = AppUser(
        username=username,
        first_name=data.get('firstName', ''),
        last_name=data.get('lastName', ''),
        email=data.get('email', ''),
        role=data.get('role', 'OPERATOR'),
        organization_id=org_id,
        enabled=True
    )
    temp_pw = secrets.token_urlsafe(12)
    new_user.set_password(temp_pw)
    db.session.add(new_user)
    db.session.commit()
    _log_action(g.current_user.username, 'INSERT_USER', 'app_user', new_user.id)
    return jsonify({'id': new_user.id, 'username': new_user.username,
                    'temporaryPassword': temp_pw}), 201


@app.route('/admin/api/users/<int:user_id>', methods=['POST'])
@login_required
@admin_or_owner_required
def edit_user(user_id):
    target = db.session.get(AppUser, user_id)
    if not target:
        return jsonify({'error': 'User not found'}), 404

    data = request.json
    if 'firstName' in data:
        target.first_name = data['firstName']
    if 'lastName' in data:
        target.last_name = data['lastName']
    if 'email' in data:
        target.email = data['email']
    if 'role' in data and data['role'] in ('ADMIN', 'OWNER', 'OPERATOR'):
        target.role = data['role']
    if 'organizationId' in data:
        target.organization_id = data['organizationId']

    db.session.commit()
    _log_action(g.current_user.username, 'EDIT_USER', 'app_user', user_id)
    return jsonify({'message': 'User updated'})


@app.route('/admin/api/users/<int:user_id>/enable/<enable>', methods=['PUT'])
@login_required
@admin_or_owner_required
def enable_user(user_id, enable):
    target = db.session.get(AppUser, user_id)
    if not target:
        return jsonify({'error': 'User not found'}), 404

    target.enabled = enable.lower() == 'true'
    db.session.commit()
    _log_action(g.current_user.username, 'TOGGLE_USER', 'app_user', user_id)
    return jsonify({'message': f'User {"enabled" if target.enabled else "disabled"}'})


@app.route('/admin/api/users/<int:user_id>/reset-password', methods=['PUT'])
@login_required
@admin_or_owner_required
def reset_password(user_id):
    target = db.session.get(AppUser, user_id)
    if not target:
        return jsonify({'error': 'User not found'}), 404

    new_pw = secrets.token_urlsafe(12)
    target.set_password(new_pw)
    db.session.commit()
    _log_action(g.current_user.username, 'RESET_PASSWORD', 'app_user', user_id)
    return jsonify({'password': new_pw})


@app.route('/admin/api/users/<int:user_id>', methods=['DELETE'])
@login_required
@admin_or_owner_required
def delete_user(user_id):
    target = db.session.get(AppUser, user_id)
    if not target:
        return jsonify({'error': 'User not found'}), 404

    db.session.delete(target)
    db.session.commit()
    _log_action(g.current_user.username, 'DELETE_USER', 'app_user', user_id)
    return jsonify({'message': 'User deleted'})


# ── REST API: API Keys ───────────────────────────────────────────────────────

@app.route('/admin/api/organizations/<int:org_id>/apikey', methods=['GET'])
@login_required
def list_api_keys(org_id):
    keys = ApiKey.query.filter_by(organization_id=org_id).all()
    return jsonify([{
        'id': k.id, 'organizationId': k.organization_id,
        'keyValue': k.key_value, 'description': k.description,
        'active': k.active
    } for k in keys])


@app.route('/admin/api/organizations/<int:org_id>/apikey', methods=['POST'])
@login_required
@admin_or_owner_required
def create_api_key(org_id):
    data = request.json or {}
    key = ApiKey(
        organization_id=org_id,
        key_value=secrets.token_urlsafe(32),
        description=data.get('description', 'API Key'),
        active=True
    )
    db.session.add(key)
    db.session.commit()
    _log_action(g.current_user.username, 'CREATE_API_KEY', 'api_key', key.id)
    return jsonify({'id': key.id, 'keyValue': key.key_value}), 201


# ── REST API: Events ─────────────────────────────────────────────────────────

@app.route('/admin/api/events', methods=['GET'])
@login_required
def list_events():
    user = g.current_user
    org_id = request.args.get('organizationId', type=int)
    if org_id is not None:
        events = Event.query.filter_by(organization_id=org_id).all()
    elif user.role == 'ADMIN':
        events = Event.query.all()
    else:
        events = Event.query.filter_by(organization_id=user.organization_id).all()
    return jsonify([{
        'id': e.id, 'organizationId': e.organization_id,
        'shortName': e.short_name, 'displayName': e.display_name,
        'location': e.location, 'status': e.status
    } for e in events])


# ── REST API: Audit ──────────────────────────────────────────────────────────

@app.route('/admin/api/audit', methods=['GET'])
@login_required
@admin_or_owner_required
def list_audit():
    entries = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(50).all()
    return jsonify([{
        'id': a.id, 'username': a.username, 'action': a.action,
        'entityType': a.entity_type, 'entityId': a.entity_id,
        'timestamp': a.timestamp.isoformat() if a.timestamp else None
    } for a in entries])


# ── Database initialization ──────────────────────────────────────────────────

def init_db():
    db.drop_all()
    db.create_all()

    flag = os.getenv('FLAG', 'flag{this_is_a_fake_flag}')

    # Organization 1 - Platform admin org
    org1 = Organization(name='Alf.io Platform', description='Main platform administration',
                        slug='alfio-platform')
    db.session.add(org1)
    db.session.flush()

    # Organization 2 - Regular tenant
    org2 = Organization(name='TechConf Events', description='Technology conference organizer',
                        slug='techconf-events')
    db.session.add(org2)
    db.session.flush()

    # Organization 3 - Another tenant
    org3 = Organization(name='Music Fest Co', description='Music festival management',
                        slug='musicfest-co')
    db.session.add(org3)
    db.session.flush()

    # Admin user for org1
    admin = AppUser(username='admin', first_name='System', last_name='Administrator',
                    email='admin@alfio.local', role='ADMIN', organization_id=org1.id)
    admin.set_password('Kj8#mP2$vL9!')
    db.session.add(admin)

    # Owner for org1
    owner1 = AppUser(username='platform.owner', first_name='James', last_name='Mitchell',
                     email='james.mitchell@alfio.local', role='OWNER', organization_id=org1.id)
    owner1.set_password('xR4!nQ7@wB3k')
    db.session.add(owner1)

    # Users for org2
    owner2 = AppUser(username='sarah.chen', first_name='Sarah', last_name='Chen',
                     email='sarah.chen@techconf.io', role='OWNER', organization_id=org2.id)
    owner2.set_password('TechConf2024!')
    db.session.add(owner2)

    operator2 = AppUser(username='operator', first_name='Alex', last_name='Rivera',
                        email='alex.rivera@techconf.io', role='OPERATOR', organization_id=org2.id)
    operator2.set_password('operator')
    db.session.add(operator2)

    # Users for org3
    owner3 = AppUser(username='lisa.park', first_name='Lisa', last_name='Park',
                     email='lisa.park@musicfest.co', role='OWNER', organization_id=org3.id)
    owner3.set_password('MuS1cF3st!')
    db.session.add(owner3)

    db.session.flush()

    # Platform API keys
    prod_key = ApiKey(organization_id=org1.id, key_value=flag,
                      description='Production webhook signing secret', active=True)
    db.session.add(prod_key)

    # Some normal API keys
    for org in [org1, org2, org3]:
        for i in range(2):
            k = ApiKey(organization_id=org.id, key_value=secrets.token_urlsafe(32),
                       description=f'Integration key #{i+1}', active=True)
            db.session.add(k)

    # Events
    events_data = [
        (org1.id, 'platform-summit', 'Alf.io Platform Summit 2024', 'Virtual', 'PUBLISHED'),
        (org2.id, 'techconf-2024', 'TechConf 2024', 'San Francisco, CA', 'PUBLISHED'),
        (org2.id, 'devops-workshop', 'DevOps Workshop Series', 'Online', 'DRAFT'),
        (org3.id, 'summer-beats', 'Summer Beats Festival', 'Austin, TX', 'PUBLISHED'),
        (org3.id, 'winter-jazz', 'Winter Jazz Night', 'New Orleans, LA', 'DRAFT'),
    ]
    for oid, sn, dn, loc, st in events_data:
        ev = Event(organization_id=oid, short_name=sn, display_name=dn,
                   location=loc, status=st)
        db.session.add(ev)

    db.session.commit()


# ── Error handlers ───────────────────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    if request.path.startswith('/admin/api/'):
        return jsonify({'error': 'Not found'}), 404
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    if request.path.startswith('/admin/api/'):
        return jsonify({'error': 'Internal server error'}), 500
    return render_template('500.html'), 500


if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(host='0.0.0.0', port=5003)
