import os
import hashlib
import secrets
from functools import wraps
from datetime import datetime, timedelta

from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = os.urandom(32).hex()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///backoffice.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)

db = SQLAlchemy(app)


class Organization(db.Model):
    __tablename__ = 'ba_organization'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.String(500))
    email = db.Column(db.String(200))
    slug = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Account(db.Model):
    __tablename__ = 'ba_account'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    email_address = db.Column(db.String(200))
    enabled = db.Column(db.Boolean, default=True)
    role = db.Column(db.String(30), nullable=False, default='OPERATOR')
    description = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def hash_password(pw):
        return hashlib.sha256(pw.encode()).hexdigest()


class AccountOrganization(db.Model):
    __tablename__ = 'ba_account_organization'
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('ba_account.id'), nullable=False)
    organization_id = db.Column(db.Integer, db.ForeignKey('ba_organization.id'), nullable=False)


class Event(db.Model):
    __tablename__ = 'ba_event'
    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('ba_organization.id'), nullable=False)
    short_name = db.Column(db.String(120), nullable=False)
    display_name = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(300))
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    currency = db.Column(db.String(10), default='EUR')
    available_seats = db.Column(db.Integer, default=100)
    status = db.Column(db.String(20), default='DRAFT')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ConfigurationEntry(db.Model):
    __tablename__ = 'ba_configuration'
    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('ba_organization.id'), nullable=False)
    c_key = db.Column(db.String(120), nullable=False)
    c_value = db.Column(db.String(500), nullable=False)
    description = db.Column(db.String(300))


def get_current_account():
    account_id = session.get('account_id')
    if account_id is None:
        return None
    return db.session.get(Account, account_id)


def get_account_organizations(account_id):
    links = AccountOrganization.query.filter_by(account_id=account_id).all()
    org_ids = [link.organization_id for link in links]
    if not org_ids:
        return []
    return Organization.query.filter(Organization.id.in_(org_ids)).all()


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        account = get_current_account()
        if account is None:
            if request.is_json or request.path.startswith('/admin/api'):
                return jsonify({"error": "Authentication required"}), 401
            return redirect(url_for('login_page'))
        if not account.enabled:
            session.clear()
            if request.is_json or request.path.startswith('/admin/api'):
                return jsonify({"error": "Account disabled"}), 403
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        account = get_current_account()
        if account is None:
            return jsonify({"error": "Authentication required"}), 401
        if account.role != 'ADMIN':
            return jsonify({"error": "Insufficient privileges"}), 403
        return f(*args, **kwargs)
    return decorated


# ─── Web Pages ───────────────────────────────────────────────

@app.route('/')
def index():
    account = get_current_account()
    if account:
        return redirect(url_for('dashboard_page'))
    return redirect(url_for('login_page'))


@app.route('/authentication')
def login_page():
    if get_current_account():
        return redirect(url_for('dashboard_page'))
    return render_template('authentication.html')


@app.route('/admin/dashboard')
@login_required
def dashboard_page():
    return render_template('dashboard.html')


@app.route('/admin/organizations')
@login_required
def organizations_page():
    return render_template('organizations.html')


@app.route('/admin/members')
@login_required
def members_page():
    return render_template('members.html')


@app.route('/admin/events')
@login_required
def events_page():
    return render_template('events.html')


@app.route('/admin/settings')
@login_required
def settings_page():
    return render_template('settings.html')


# ─── Auth API ────────────────────────────────────────────────

@app.route('/admin/api/authenticate', methods=['POST'])
def api_authenticate():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid request"}), 400
    username = data.get('username', '')
    password = data.get('password', '')
    account = Account.query.filter_by(username=username).first()
    if not account or account.password_hash != Account.hash_password(password):
        return jsonify({"error": "Invalid credentials"}), 401
    if not account.enabled:
        return jsonify({"error": "Account is disabled"}), 403
    session['account_id'] = account.id
    session.permanent = True
    return jsonify({
        "message": "Authentication successful",
        "accountId": account.id,
        "role": account.role,
        "username": account.username
    })


@app.route('/admin/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({"message": "Logged out"})


@app.route('/admin/api/account/current', methods=['GET'])
@login_required
def api_current_account():
    account = get_current_account()
    orgs = get_account_organizations(account.id)
    return jsonify({
        "id": account.id,
        "username": account.username,
        "firstName": account.first_name,
        "lastName": account.last_name,
        "emailAddress": account.email_address,
        "role": account.role,
        "description": account.description,
        "organizations": [{"id": o.id, "name": o.name} for o in orgs]
    })


# ─── Organization API ────────────────────────────────────────

@app.route('/admin/api/organizations', methods=['GET'])
@login_required
def api_list_organizations():
    account = get_current_account()
    if account.role == 'ADMIN':
        orgs = Organization.query.all()
    else:
        orgs = get_account_organizations(account.id)
    return jsonify([{
        "id": o.id,
        "name": o.name,
        "description": o.description,
        "email": o.email,
        "slug": o.slug
    } for o in orgs])


@app.route('/admin/api/organizations/<int:org_id>', methods=['GET'])
@login_required
def api_get_organization(org_id):
    org = db.session.get(Organization, org_id)
    if not org:
        return jsonify({"error": "Organization not found"}), 404
    account = get_current_account()
    if account.role != 'ADMIN':
        user_orgs = get_account_organizations(account.id)
        if org_id not in [o.id for o in user_orgs]:
            return jsonify({"error": "Access denied"}), 403
    return jsonify({
        "id": org.id,
        "name": org.name,
        "description": org.description,
        "email": org.email,
        "slug": org.slug
    })


# ─── Members (User management) API ──────────────────────────

@app.route('/admin/api/members', methods=['GET'])
@login_required
def api_list_members():
    account = get_current_account()
    if account.role == 'ADMIN':
        members = Account.query.all()
    else:
        user_orgs = get_account_organizations(account.id)
        org_ids = [o.id for o in user_orgs]
        links = AccountOrganization.query.filter(AccountOrganization.organization_id.in_(org_ids)).all()
        member_ids = list(set([link.account_id for link in links]))
        members = Account.query.filter(Account.id.in_(member_ids)).all() if member_ids else []
    return jsonify([{
        "id": m.id,
        "username": m.username,
        "firstName": m.first_name,
        "lastName": m.last_name,
        "emailAddress": m.email_address,
        "enabled": m.enabled,
        "role": m.role,
        "description": m.description
    } for m in members])


@app.route('/admin/api/members/<int:member_id>', methods=['GET'])
@login_required
def api_get_member(member_id):
    member = db.session.get(Account, member_id)
    if not member:
        return jsonify({"error": "Member not found"}), 404
    orgs = get_account_organizations(member_id)
    return jsonify({
        "id": member.id,
        "username": member.username,
        "firstName": member.first_name,
        "lastName": member.last_name,
        "emailAddress": member.email_address,
        "enabled": member.enabled,
        "role": member.role,
        "description": member.description,
        "organizations": [{"id": o.id, "name": o.name} for o in orgs]
    })


@app.route('/admin/api/members/<int:member_id>/toggle/<int:status>', methods=['POST'])
@login_required
def api_toggle_member(member_id, status):
    account = get_current_account()
    if account.role not in ('ADMIN', 'OWNER'):
        return jsonify({"error": "Insufficient privileges"}), 403
    if member_id == account.id:
        return jsonify({"error": "Cannot modify own account status"}), 400
    member = db.session.get(Account, member_id)
    if not member:
        return jsonify({"error": "Member not found"}), 404
    member.enabled = bool(status)
    db.session.commit()
    return jsonify({"message": "Member status updated", "enabled": member.enabled})


@app.route('/admin/api/members/<int:member_id>/credential-reset', methods=['PUT'])
@login_required
def api_reset_member_credentials(member_id):
    account = get_current_account()
    if account.role not in ('ADMIN', 'OWNER'):
        return jsonify({"error": "Insufficient privileges"}), 403
    member = db.session.get(Account, member_id)
    if not member:
        return jsonify({"error": "Member not found"}), 404
    new_password = secrets.token_urlsafe(12)
    member.password_hash = Account.hash_password(new_password)
    db.session.commit()
    return jsonify({
        "message": "Credentials reset successful",
        "username": member.username,
        "temporaryPassword": new_password
    })


@app.route('/admin/api/members', methods=['POST'])
@login_required
def api_create_member():
    account = get_current_account()
    if account.role not in ('ADMIN', 'OWNER'):
        return jsonify({"error": "Insufficient privileges"}), 403
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid request"}), 400
    username = data.get('username', '').strip()
    org_id = data.get('organizationId')
    role = data.get('role', 'OPERATOR')
    if not username or not org_id:
        return jsonify({"error": "Missing required fields"}), 400
    if Account.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 409
    org = db.session.get(Organization, org_id)
    if not org:
        return jsonify({"error": "Organization not found"}), 404
    temp_pw = secrets.token_urlsafe(12)
    new_account = Account(
        username=username,
        password_hash=Account.hash_password(temp_pw),
        first_name=data.get('firstName', ''),
        last_name=data.get('lastName', ''),
        email_address=data.get('emailAddress', ''),
        role=role if role in ('OWNER', 'OPERATOR', 'SUPERVISOR', 'SPONSOR') else 'OPERATOR',
        description=data.get('description', ''),
        enabled=True
    )
    db.session.add(new_account)
    db.session.flush()
    link = AccountOrganization(account_id=new_account.id, organization_id=org_id)
    db.session.add(link)
    db.session.commit()
    return jsonify({
        "id": new_account.id,
        "username": new_account.username,
        "temporaryPassword": temp_pw,
        "organizationId": org_id
    }), 201


@app.route('/admin/api/members/<int:member_id>', methods=['POST'])
@login_required
def api_update_member(member_id):
    account = get_current_account()
    if account.role not in ('ADMIN', 'OWNER'):
        return jsonify({"error": "Insufficient privileges"}), 403
    member = db.session.get(Account, member_id)
    if not member:
        return jsonify({"error": "Member not found"}), 404
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid request"}), 400
    if 'firstName' in data:
        member.first_name = data['firstName']
    if 'lastName' in data:
        member.last_name = data['lastName']
    if 'emailAddress' in data:
        member.email_address = data['emailAddress']
    if 'description' in data:
        member.description = data['description']
    if 'organizationId' in data:
        org = db.session.get(Organization, data['organizationId'])
        if org:
            AccountOrganization.query.filter_by(account_id=member_id).delete()
            link = AccountOrganization(account_id=member_id, organization_id=data['organizationId'])
            db.session.add(link)
    db.session.commit()
    return jsonify({"message": "Member updated"})


@app.route('/admin/api/members/<int:member_id>', methods=['DELETE'])
@login_required
def api_delete_member(member_id):
    account = get_current_account()
    if account.role not in ('ADMIN', 'OWNER'):
        return jsonify({"error": "Insufficient privileges"}), 403
    if member_id == account.id:
        return jsonify({"error": "Cannot delete own account"}), 400
    member = db.session.get(Account, member_id)
    if not member:
        return jsonify({"error": "Member not found"}), 404
    AccountOrganization.query.filter_by(account_id=member_id).delete()
    db.session.delete(member)
    db.session.commit()
    return jsonify({"message": "Member deleted"})


# ─── Events API ──────────────────────────────────────────────

@app.route('/admin/api/events', methods=['GET'])
@login_required
def api_list_events():
    account = get_current_account()
    if account.role == 'ADMIN':
        events = Event.query.all()
    else:
        user_orgs = get_account_organizations(account.id)
        org_ids = [o.id for o in user_orgs]
        events = Event.query.filter(Event.organization_id.in_(org_ids)).all()
    return jsonify([{
        "id": e.id,
        "organizationId": e.organization_id,
        "shortName": e.short_name,
        "displayName": e.display_name,
        "location": e.location,
        "currency": e.currency,
        "availableSeats": e.available_seats,
        "status": e.status
    } for e in events])


@app.route('/admin/api/events', methods=['POST'])
@login_required
def api_create_event():
    account = get_current_account()
    if account.role not in ('ADMIN', 'OWNER'):
        return jsonify({"error": "Insufficient privileges"}), 403
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid request"}), 400
    org_id = data.get('organizationId')
    if not org_id:
        return jsonify({"error": "organizationId is required"}), 400
    org = db.session.get(Organization, org_id)
    if not org:
        return jsonify({"error": "Organization not found"}), 404
    event = Event(
        organization_id=org_id,
        short_name=data.get('shortName', ''),
        display_name=data.get('displayName', ''),
        location=data.get('location', ''),
        currency=data.get('currency', 'EUR'),
        available_seats=data.get('availableSeats', 100),
        status='DRAFT'
    )
    db.session.add(event)
    db.session.commit()
    return jsonify({"id": event.id, "message": "Event created"}), 201


# ─── Configuration API ───────────────────────────────────────

@app.route('/admin/api/configuration/organization/<int:org_id>', methods=['GET'])
@login_required
def api_get_configuration(org_id):
    org = db.session.get(Organization, org_id)
    if not org:
        return jsonify({"error": "Organization not found"}), 404
    entries = ConfigurationEntry.query.filter_by(organization_id=org_id).all()
    return jsonify([{
        "id": e.id,
        "organizationId": e.organization_id,
        "key": e.c_key,
        "value": e.c_value,
        "description": e.description
    } for e in entries])


@app.route('/admin/api/configuration/organization/<int:org_id>', methods=['POST'])
@login_required
def api_set_configuration(org_id):
    account = get_current_account()
    if account.role not in ('ADMIN', 'OWNER'):
        return jsonify({"error": "Insufficient privileges"}), 403
    org = db.session.get(Organization, org_id)
    if not org:
        return jsonify({"error": "Organization not found"}), 404
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid request"}), 400
    key = data.get('key', '').strip()
    value = data.get('value', '').strip()
    if not key:
        return jsonify({"error": "Key is required"}), 400
    entry = ConfigurationEntry.query.filter_by(organization_id=org_id, c_key=key).first()
    if entry:
        entry.c_value = value
        if 'description' in data:
            entry.description = data['description']
    else:
        entry = ConfigurationEntry(
            organization_id=org_id,
            c_key=key,
            c_value=value,
            description=data.get('description', '')
        )
        db.session.add(entry)
    db.session.commit()
    return jsonify({"message": "Configuration saved"})


# ─── Roles API ───────────────────────────────────────────────

@app.route('/admin/api/roles', methods=['GET'])
@login_required
def api_list_roles():
    account = get_current_account()
    available_roles = ['OPERATOR', 'SPONSOR', 'SUPERVISOR']
    if account.role in ('ADMIN', 'OWNER'):
        available_roles.append('OWNER')
    if account.role == 'ADMIN':
        available_roles.append('ADMIN')
    return jsonify([{"role": r} for r in available_roles])


# ─── Health ──────────────────────────────────────────────────

@app.route('/healthz')
def healthz():
    return 'OK', 200


# ─── Error handlers ──────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    if request.path.startswith('/admin/api'):
        return jsonify({"error": "Not found"}), 404
    return render_template('error.html', code=404, message="Page not found"), 404


@app.errorhandler(500)
def server_error(e):
    if request.path.startswith('/admin/api'):
        return jsonify({"error": "Internal server error"}), 500
    return render_template('error.html', code=500, message="Internal server error"), 500


@app.after_request
def remove_headers(response):
    response.headers.pop('Server', None)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    return response


# ─── Database Initialization ─────────────────────────────────

def read_flag():
    flag_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.flag_data')
    try:
        with open(flag_path, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return 'FLAG{placeholder}'


def init_db():
    db.drop_all()
    db.create_all()

    org1 = Organization(name='GlobalTech Events', description='Enterprise event management', email='admin@globaltech-events.io', slug='globaltech-events')
    org2 = Organization(name='Community Meetups', description='Local community event planning', email='hello@community-meetups.org', slug='community-meetups')
    org3 = Organization(name='SecureConf LLC', description='Security conference organizer', email='ops@secureconf.net', slug='secureconf')
    db.session.add_all([org1, org2, org3])
    db.session.flush()

    admin = Account(
        username='platform_admin',
        password_hash=Account.hash_password('Kj8#mP2$vL9nQ'),
        first_name='System',
        last_name='Administrator',
        email_address='admin@globaltech-events.io',
        role='ADMIN',
        description='Platform administrator'
    )
    db.session.add(admin)
    db.session.flush()
    db.session.add(AccountOrganization(account_id=admin.id, organization_id=org1.id))

    owner1 = Account(
        username='sarah.chen',
        password_hash=Account.hash_password('Gt3v#nts2024!'),
        first_name='Sarah',
        last_name='Chen',
        email_address='sarah.chen@globaltech-events.io',
        role='OWNER',
        description='GlobalTech Events manager'
    )
    db.session.add(owner1)
    db.session.flush()
    db.session.add(AccountOrganization(account_id=owner1.id, organization_id=org1.id))

    owner2 = Account(
        username='mike.ross',
        password_hash=Account.hash_password('Cm33tup$2024'),
        first_name='Mike',
        last_name='Ross',
        email_address='mike@community-meetups.org',
        role='OWNER',
        description='Community Meetups lead'
    )
    db.session.add(owner2)
    db.session.flush()
    db.session.add(AccountOrganization(account_id=owner2.id, organization_id=org2.id))

    operator1 = Account(
        username='operator',
        password_hash=Account.hash_password('operator'),
        first_name='Jordan',
        last_name='Lee',
        email_address='jlee@community-meetups.org',
        role='OPERATOR',
        description='Check-in operator'
    )
    db.session.add(operator1)
    db.session.flush()
    db.session.add(AccountOrganization(account_id=operator1.id, organization_id=org2.id))

    owner3 = Account(
        username='diana.prince',
        password_hash=Account.hash_password('S3cur3C0nf!#'),
        first_name='Diana',
        last_name='Prince',
        email_address='diana@secureconf.net',
        role='OWNER',
        description='SecureConf lead organizer'
    )
    db.session.add(owner3)
    db.session.flush()
    db.session.add(AccountOrganization(account_id=owner3.id, organization_id=org3.id))

    for i in range(1, 6):
        ev = Event(
            organization_id=org1.id,
            short_name=f'gt-summit-{i}',
            display_name=f'GlobalTech Summit {2020 + i}',
            location='San Francisco, CA',
            currency='USD',
            available_seats=500 + i * 100,
            status='PUBLISHED' if i < 4 else 'DRAFT'
        )
        db.session.add(ev)

    for i in range(1, 4):
        ev = Event(
            organization_id=org2.id,
            short_name=f'cm-gathering-{i}',
            display_name=f'Community Gathering {2021 + i}',
            location='Portland, OR',
            currency='USD',
            available_seats=50 + i * 20,
            status='PUBLISHED'
        )
        db.session.add(ev)

    for i in range(1, 4):
        ev = Event(
            organization_id=org3.id,
            short_name=f'sc-conf-{i}',
            display_name=f'SecureConf {2021 + i}',
            location='Las Vegas, NV',
            currency='USD',
            available_seats=300 + i * 50,
            status='PUBLISHED' if i < 3 else 'DRAFT'
        )
        db.session.add(ev)

    flag = read_flag()
    config_entries = [
        ConfigurationEntry(organization_id=org1.id, c_key='SMTP_HOST', c_value='mail.globaltech-events.io', description='Mail server hostname'),
        ConfigurationEntry(organization_id=org1.id, c_key='SMTP_PORT', c_value='587', description='Mail server port'),
        ConfigurationEntry(organization_id=org1.id, c_key='SMTP_USERNAME', c_value='noreply@globaltech-events.io', description='SMTP username'),
        ConfigurationEntry(organization_id=org1.id, c_key='STRIPE_PUBLISHABLE_KEY', c_value='pk_live_GT7xKm9Qp2Lv4Nw8Jy5Rs3At', description='Stripe publishable key'),
        ConfigurationEntry(organization_id=org1.id, c_key='STRIPE_SECRET_KEY', c_value=flag, description='Stripe secret API key'),
        ConfigurationEntry(organization_id=org1.id, c_key='BASE_URL', c_value='https://globaltech-events.io', description='Public base URL'),
        ConfigurationEntry(organization_id=org1.id, c_key='MAX_TICKETS_PER_ORDER', c_value='10', description='Maximum tickets per order'),
        ConfigurationEntry(organization_id=org2.id, c_key='SMTP_HOST', c_value='smtp.community-meetups.org', description='Mail server hostname'),
        ConfigurationEntry(organization_id=org2.id, c_key='SMTP_PORT', c_value='465', description='Mail server port'),
        ConfigurationEntry(organization_id=org2.id, c_key='BASE_URL', c_value='https://community-meetups.org', description='Public base URL'),
        ConfigurationEntry(organization_id=org2.id, c_key='STRIPE_PUBLISHABLE_KEY', c_value='pk_live_Cm5xLn2Qr8Mv6Pw4Jy9Ks7Bt', description='Stripe publishable key'),
        ConfigurationEntry(organization_id=org2.id, c_key='STRIPE_SECRET_KEY', c_value='sk_live_Cm5xLn2Qr8Mv6Pw4Jy9Ks7Bt', description='Stripe secret API key'),
        ConfigurationEntry(organization_id=org3.id, c_key='SMTP_HOST', c_value='mail.secureconf.net', description='Mail server hostname'),
        ConfigurationEntry(organization_id=org3.id, c_key='BASE_URL', c_value='https://secureconf.net', description='Public base URL'),
        ConfigurationEntry(organization_id=org3.id, c_key='STRIPE_PUBLISHABLE_KEY', c_value='pk_live_Sc3xMn7Qs1Nv8Rw2Ky4Lt6Cu', description='Stripe publishable key'),
        ConfigurationEntry(organization_id=org3.id, c_key='STRIPE_SECRET_KEY', c_value='sk_live_Sc3xMn7Qs1Nv8Rw2Ky4Lt6Cu', description='Stripe secret API key'),
    ]
    db.session.add_all(config_entries)

    db.session.commit()


if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(host='0.0.0.0', port=5003)
