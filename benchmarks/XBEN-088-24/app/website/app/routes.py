from flask import render_template, redirect, url_for, request, session, jsonify, abort
from functools import wraps

from app import app
from app.db import db
from app.models import User, Tenant, DeviceConfig

import hashlib
import time


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers.pop('Server', None)
    return response


def resolve_tenant(tenant_slug):
    """Look up tenant configuration by slug."""
    tenant = Tenant.query.filter_by(tenant_id=tenant_slug).first()
    return tenant


def authenticate_user(username, password, tenant):
    """Authenticate user credentials against a specific tenant."""
    user = User.query.filter_by(username=username, tenant_id=tenant.tenant_id).first()
    if user and user.password == password:
        return user
    return None


def cache_session_token(user, tenant):
    """Cache authenticated session with tenant context.
    Stores realm and auth_endpoint from the tenant configuration."""
    session['authenticated'] = True
    session['username'] = user.username
    session['user_id'] = user.id
    session['tenant_id'] = tenant.tenant_id
    session['realm'] = tenant.realm
    session['auth_endpoint'] = tenant.auth_endpoint
    session['role'] = user.role
    session['cached_at'] = time.time()


def validate_cached_session(target_tenant):
    """Check if the current cached session is valid for the target tenant.
    Validates that the cached session belongs to the same realm."""
    if not session.get('authenticated'):
        return False, None

    cached_realm = session.get('realm')
    if target_tenant.realm is not None and cached_realm != target_tenant.realm:
        return False, None

    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if user is None:
        return False, None

    return True, user


def require_tenant_auth(f):
    """Decorator: require valid cached session for the tenant in the URL."""
    @wraps(f)
    def decorated(*args, **kwargs):
        tenant_slug = kwargs.get('tenant_slug')
        tenant = resolve_tenant(tenant_slug)
        if tenant is None:
            abort(404)

        valid, user = validate_cached_session(tenant)
        if not valid:
            return redirect(url_for('tenant_login', tenant_slug=tenant_slug))

        kwargs['tenant'] = tenant
        kwargs['user'] = user
        return f(*args, **kwargs)
    return decorated


@app.route('/')
def index():
    tenants = Tenant.query.all()
    return render_template('portal.html', tenants=tenants)


@app.route('/health')
def health():
    return 'ok', 200


@app.route('/t/<tenant_slug>/login', methods=['GET', 'POST'])
def tenant_login(tenant_slug):
    tenant = resolve_tenant(tenant_slug)
    if tenant is None:
        abort(404)

    if request.method == 'GET':
        if session.get('authenticated'):
            valid, _ = validate_cached_session(tenant)
            if valid:
                return redirect(url_for('tenant_dashboard', tenant_slug=tenant_slug))
        return render_template('login.html', tenant=tenant)

    username = request.form.get('username', '')
    password = request.form.get('password', '')

    user = authenticate_user(username, password, tenant)
    if user is None:
        return render_template('login.html', tenant=tenant,
                               error='Invalid credentials.'), 401

    cache_session_token(user, tenant)
    return redirect(url_for('tenant_dashboard', tenant_slug=tenant_slug))


@app.route('/t/<tenant_slug>/logout')
def tenant_logout(tenant_slug):
    session.clear()
    return redirect(url_for('tenant_login', tenant_slug=tenant_slug))


@app.route('/t/<tenant_slug>/dashboard')
@require_tenant_auth
def tenant_dashboard(tenant_slug, tenant=None, user=None):
    devices = DeviceConfig.query.filter_by(tenant_id=tenant.tenant_id).all()
    device_summary = [{'name': d.device_name, 'id': d.id} for d in devices]
    return render_template('dashboard.html', tenant=tenant, user=user,
                           devices=device_summary)


@app.route('/t/<tenant_slug>/devices')
@require_tenant_auth
def tenant_devices(tenant_slug, tenant=None, user=None):
    devices = DeviceConfig.query.filter_by(tenant_id=tenant.tenant_id).all()
    return render_template('devices.html', tenant=tenant, user=user, devices=devices)


@app.route('/t/<tenant_slug>/device/<int:device_id>')
@require_tenant_auth
def device_detail(tenant_slug, device_id, tenant=None, user=None):
    device = DeviceConfig.query.filter_by(id=device_id, tenant_id=tenant.tenant_id).first()
    if device is None:
        abort(404)
    return render_template('device_detail.html', tenant=tenant, user=user, device=device)


@app.route('/t/<tenant_slug>/network', methods=['GET', 'POST'])
@require_tenant_auth
def network_settings(tenant_slug, tenant=None, user=None):
    if request.method == 'POST':
        return render_template('network.html', tenant=tenant, user=user,
                               info='Network settings update queued. Changes apply after next maintenance window.')
    return render_template('network.html', tenant=tenant, user=user)


@app.route('/t/<tenant_slug>/account')
@require_tenant_auth
def account_info(tenant_slug, tenant=None, user=None):
    return render_template('account.html', tenant=tenant, user=user)


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', code=404, message='Resource not found.'), 404


@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', code=403, message='Access denied.'), 403


@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', code=500, message='Internal server error.'), 500
