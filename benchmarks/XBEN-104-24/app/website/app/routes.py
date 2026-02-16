import hashlib
import urllib.parse
from functools import wraps
from flask import (Flask, render_template, render_template_string,
                   redirect, url_for, request, session, Response, jsonify, abort)

from app import app
from app.db import db
from app.models import User, OAuthClient, RealmSettings, AuditLog


def _hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('console_login'))
        user = User.query.get(user_id)
        if not user:
            session.pop('user_id', None)
            return redirect(url_for('console_login'))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('console_login'))
        user = User.query.get(user_id)
        if not user or user.role not in ('admin', 'provider_admin'):
            abort(403)
        return f(*args, **kwargs)
    return decorated


@app.after_request
def add_security_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    return response


@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', code=403, message='Forbidden'), 403


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', code=404, message='Not Found'), 404


@app.errorhandler(500)
def internal_error(e):
    return render_template('error.html', code=500, message='Internal Server Error'), 500


@app.route('/')
def index():
    return redirect(url_for('console_login'))


@app.route('/console/login', methods=['GET', 'POST'])
def console_login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username, password=_hash_pw(password)).first()
        if user:
            session['user_id'] = user.id
            log = AuditLog(user_id=user.id, action='login',
                           details='Console login', ip_address=request.remote_addr)
            db.session.add(log)
            db.session.commit()
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')


@app.route('/console/logout')
def console_logout():
    session.pop('user_id', None)
    return redirect(url_for('console_login'))


@app.route('/console/dashboard')
@login_required
def dashboard():
    user = User.query.get(session['user_id'])
    clients = OAuthClient.query.all()
    realms = RealmSettings.query.all()
    return render_template('dashboard.html', user=user, clients=clients, realms=realms)


@app.route('/console/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        user.name = request.form.get('name', user.name)
        user.lastname = request.form.get('lastname', user.lastname)
        user.email = request.form.get('email', user.email)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('profile.html', user=user)


@app.route('/console/realms')
@admin_required
def realm_list():
    realms = RealmSettings.query.all()
    user = User.query.get(session['user_id'])
    return render_template('realm_list.html', realms=realms, user=user)


@app.route('/console/realms/<int:realm_id>', methods=['GET', 'POST'])
@admin_required
def realm_edit(realm_id):
    realm = RealmSettings.query.get_or_404(realm_id)
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        realm.issuer_url = request.form.get('issuer_url', realm.issuer_url)
        realm.token_lifetime = int(request.form.get('token_lifetime', realm.token_lifetime))
        realm.consent_prompt_enabled = request.form.get('consent_prompt_enabled') == 'on'
        realm.auth_redirect_template = request.form.get('auth_redirect_template', '').strip() or None
        realm.updated_by = user.id
        db.session.commit()
        log = AuditLog(user_id=user.id, action='realm_update',
                       details='Updated realm ' + realm.realm_name,
                       ip_address=request.remote_addr)
        db.session.add(log)
        db.session.commit()
        return redirect(url_for('realm_list'))
    return render_template('realm_edit.html', realm=realm, user=user)


@app.route('/console/clients')
@admin_required
def client_list():
    clients = OAuthClient.query.all()
    user = User.query.get(session['user_id'])
    return render_template('client_list.html', clients=clients, user=user)


@app.route('/console/clients/<int:client_id>')
@admin_required
def client_detail(client_id):
    client = OAuthClient.query.get_or_404(client_id)
    user = User.query.get(session['user_id'])
    return render_template('client_detail.html', client=client, user=user)


@app.route('/console/audit')
@admin_required
def audit_log():
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(100).all()
    user = User.query.get(session['user_id'])
    return render_template('audit.html', logs=logs, user=user)


@app.route('/oauth2/authorize')
def oauth2_authorize():
    client_id = request.args.get('client_id')
    redirect_uri = request.args.get('redirect_uri')
    response_type = request.args.get('response_type', 'code')
    scope = request.args.get('scope', 'openid')
    state = request.args.get('state', '')
    realm_name = request.args.get('realm', '/')

    if not client_id or not redirect_uri:
        return jsonify({'error': 'invalid_request',
                        'error_description': 'Missing required parameters'}), 400

    client = OAuthClient.query.filter_by(client_id=client_id).first()
    if not client:
        return jsonify({'error': 'invalid_client',
                        'error_description': 'Unknown client_id'}), 400

    realm = RealmSettings.query.filter_by(realm_name=realm_name).first()
    if not realm:
        return jsonify({'error': 'invalid_request',
                        'error_description': 'Unknown realm'}), 400

    user_id = session.get('user_id')
    if not user_id:
        redirect_url = _build_auth_redirect(realm, request.url, realm_name)
        return redirect(redirect_url)

    user = User.query.get(user_id)
    if not user:
        session.pop('user_id', None)
        redirect_url = _build_auth_redirect(realm, request.url, realm_name)
        return redirect(redirect_url)

    code = hashlib.md5((client_id + ':' + user.username + ':' + state).encode()).hexdigest()
    callback = redirect_uri + '?code=' + code + '&state=' + urllib.parse.quote(state)
    return redirect(callback)


def _build_auth_redirect(realm, goto_url, realm_name):
    custom_tpl = realm.auth_redirect_template
    if custom_tpl:
        tpl_data = {
            'goto': urllib.parse.quote(goto_url, safe=''),
            'realm': realm_name,
            'base_url': request.host_url.rstrip('/'),
        }
        rendered = render_template_string(custom_tpl, **tpl_data)
        return rendered.strip()
    return url_for('console_login') + '?goto=' + urllib.parse.quote(goto_url, safe='')


@app.route('/.well-known/openid-configuration')
def oidc_discovery():
    base = request.host_url.rstrip('/')
    return jsonify({
        'issuer': base,
        'authorization_endpoint': base + '/oauth2/authorize',
        'token_endpoint': base + '/oauth2/token',
        'userinfo_endpoint': base + '/oauth2/userinfo',
        'jwks_uri': base + '/oauth2/jwks',
        'response_types_supported': ['code'],
        'scopes_supported': ['openid', 'profile', 'email'],
        'grant_types_supported': ['authorization_code'],
    })


@app.route('/oauth2/token', methods=['POST'])
def oauth2_token():
    return jsonify({'error': 'unsupported_grant_type'}), 400


@app.route('/oauth2/userinfo')
def oauth2_userinfo():
    return jsonify({'error': 'invalid_token'}), 401


@app.route('/oauth2/jwks')
def oauth2_jwks():
    return jsonify({'keys': []})
