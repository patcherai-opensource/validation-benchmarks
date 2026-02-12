import hashlib
import json
import uuid
from functools import wraps
from datetime import datetime, timedelta

from flask import (Flask, render_template, render_template_string,
                   redirect, url_for, request, session, Response, jsonify, abort)
from markupsafe import escape

from app import app
from app.db import db
from app.models import User, Realm, OAuth2Provider, AuditLog, OAuth2Token


def _hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


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
        if not user or not user.is_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated


@app.after_request
def security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    return response


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', code=404, message='Page not found'), 404


@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', code=403, message='Access denied'), 403


@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', code=500, message='Internal server error'), 500


# --- Console (Admin UI) ---

@app.route('/')
def index():
    return redirect(url_for('console_login'))


@app.route('/openam/UI/Login', methods=['GET', 'POST'])
def console_login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        hashed = _hash_password(password)
        user = User.query.filter_by(username=username, password=hashed).first()
        if user and user.status == 'active':
            session['user_id'] = user.id
            user.last_login = datetime.utcnow()
            db.session.commit()
            log = AuditLog(
                user_id=user.id,
                action='LOGIN',
                resource='console',
                ip_address=request.remote_addr
            )
            db.session.add(log)
            db.session.commit()
            if user.is_admin():
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        else:
            return render_template('login.html', error='Authentication failed')
    return render_template('login.html')


@app.route('/openam/UI/Logout')
def console_logout():
    session.pop('user_id', None)
    return redirect(url_for('console_login'))


# --- Admin Console ---

@app.route('/openam/console')
@admin_required
def admin_dashboard():
    user = User.query.get(session['user_id'])
    realms = Realm.query.all()
    user_count = User.query.count()
    provider_count = OAuth2Provider.query.count()
    return render_template('admin_dashboard.html', user=user, realms=realms,
                           user_count=user_count, provider_count=provider_count)


@app.route('/openam/console/realms')
@admin_required
def list_realms():
    user = User.query.get(session['user_id'])
    realms = Realm.query.all()
    return render_template('realms.html', user=user, realms=realms)


@app.route('/openam/console/realms/<int:realm_id>/services/oauth2')
@admin_required
def realm_oauth2_providers(realm_id):
    user = User.query.get(session['user_id'])
    realm = Realm.query.get_or_404(realm_id)
    providers = OAuth2Provider.query.filter_by(realm_id=realm_id).all()
    return render_template('oauth2_providers.html', user=user, realm=realm, providers=providers)


@app.route('/openam/console/realms/<int:realm_id>/services/oauth2/<int:provider_id>', methods=['GET', 'POST'])
@admin_required
def edit_oauth2_provider(realm_id, provider_id):
    user = User.query.get(session['user_id'])
    realm = Realm.query.get_or_404(realm_id)
    provider = OAuth2Provider.query.get_or_404(provider_id)

    if provider.realm_id != realm_id:
        abort(404)

    if request.method == 'POST':
        provider.client_id = request.form.get('client_id', provider.client_id)
        provider.client_secret = request.form.get('client_secret', provider.client_secret)
        provider.redirect_uri = request.form.get('redirect_uri', provider.redirect_uri)
        provider.scope = request.form.get('scope', provider.scope)
        provider.response_type = request.form.get('response_type', provider.response_type)
        provider.token_endpoint_auth_method = request.form.get('token_endpoint_auth_method', provider.token_endpoint_auth_method)
        provider.grant_types = request.form.get('grant_types', provider.grant_types)
        provider.custom_login_url_template = request.form.get('custom_login_url_template', '').strip() or None
        provider.issuer = request.form.get('issuer', provider.issuer)
        provider.active = 'active' in request.form
        provider.updated_at = datetime.utcnow()
        db.session.commit()

        log = AuditLog(
            user_id=user.id,
            action='UPDATE_OAUTH2_PROVIDER',
            resource=f'realm={realm.name}, provider={provider.client_id}',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()

        return redirect(url_for('realm_oauth2_providers', realm_id=realm_id))

    return render_template('edit_provider.html', user=user, realm=realm, provider=provider)


@app.route('/openam/console/users')
@admin_required
def list_users():
    user = User.query.get(session['user_id'])
    users = User.query.all()
    return render_template('users.html', user=user, users=users)


@app.route('/openam/console/audit')
@admin_required
def audit_log():
    user = User.query.get(session['user_id'])
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(100).all()
    return render_template('audit.html', user=user, logs=logs)


# --- User Dashboard ---

@app.route('/openam/dashboard')
@login_required
def user_dashboard():
    user = User.query.get(session['user_id'])
    return render_template('user_dashboard.html', user=user)


@app.route('/openam/dashboard/profile', methods=['GET', 'POST'])
@login_required
def user_profile():
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        user.display_name = request.form.get('display_name', user.display_name)
        user.email = request.form.get('email', user.email)
        db.session.commit()
        return redirect(url_for('user_dashboard'))
    return render_template('user_profile.html', user=user)


# --- OAuth2 Authorization Endpoint ---

@app.route('/oauth2/authorize')
def oauth2_authorize():
    """OAuth2 authorization endpoint. When a custom login URL template is configured,
    it is rendered to build the redirect URL for resource owner authentication."""
    client_id = request.args.get('client_id', '')
    redirect_uri = request.args.get('redirect_uri', '')
    response_type = request.args.get('response_type', 'code')
    scope = request.args.get('scope', 'openid')
    state = request.args.get('state', '')
    realm = request.args.get('realm', '/')

    # Look up the provider by client_id
    provider = OAuth2Provider.query.filter_by(client_id=client_id, active=True).first()

    if not provider:
        return render_template('oauth2_error.html',
                               error='invalid_client',
                               description='Unknown client_id'), 400

    # Check if user is already authenticated
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if user:
            # Generate authorization code
            auth_code = str(uuid.uuid4())
            return redirect(f"{provider.redirect_uri}?code={auth_code}&state={escape(state)}")

    # Build login URL -- if a custom template is configured, render it
    template_data = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'response_type': response_type,
        'scope': scope,
        'state': state,
        'realm': realm,
        'goto': request.url,
        'base_url': request.host_url.rstrip('/')
    }

    if provider.custom_login_url_template:
        # Process the custom login URL template
        login_url = render_template_string(provider.custom_login_url_template, **template_data)
        return redirect(login_url.strip())
    else:
        # Default login redirect
        return redirect(url_for('oauth2_login', client_id=client_id,
                                redirect_uri=redirect_uri, state=state))


@app.route('/oauth2/login', methods=['GET', 'POST'])
def oauth2_login():
    """Resource owner login for OAuth2 flows."""
    client_id = request.args.get('client_id', request.form.get('client_id', ''))
    redirect_uri = request.args.get('redirect_uri', request.form.get('redirect_uri', ''))
    state = request.args.get('state', request.form.get('state', ''))

    provider = OAuth2Provider.query.filter_by(client_id=client_id, active=True).first()
    if not provider:
        return render_template('oauth2_error.html',
                               error='invalid_client',
                               description='Unknown client_id'), 400

    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        hashed = _hash_password(password)
        user = User.query.filter_by(username=username, password=hashed, status='active').first()

        if user:
            session['user_id'] = user.id
            auth_code = str(uuid.uuid4())
            return redirect(f"{provider.redirect_uri}?code={auth_code}&state={escape(state)}")
        else:
            return render_template('oauth2_login.html', client_id=client_id,
                                   redirect_uri=redirect_uri, state=state,
                                   error='Invalid credentials')

    return render_template('oauth2_login.html', client_id=client_id,
                           redirect_uri=redirect_uri, state=state)


# --- Well-Known / Discovery ---

@app.route('/.well-known/openid-configuration')
def openid_config():
    base = request.host_url.rstrip('/')
    return jsonify({
        'issuer': base + '/oauth2',
        'authorization_endpoint': base + '/oauth2/authorize',
        'token_endpoint': base + '/oauth2/token',
        'userinfo_endpoint': base + '/oauth2/userinfo',
        'jwks_uri': base + '/oauth2/jwks',
        'response_types_supported': ['code', 'token', 'id_token'],
        'subject_types_supported': ['public'],
        'id_token_signing_alg_values_supported': ['RS256'],
        'scopes_supported': ['openid', 'profile', 'email']
    })


@app.route('/oauth2/token', methods=['POST'])
def oauth2_token():
    return jsonify({'error': 'invalid_grant', 'error_description': 'Authorization code expired'}), 400


@app.route('/oauth2/userinfo')
def oauth2_userinfo():
    return jsonify({'error': 'invalid_token'}), 401


@app.route('/openam/isAlive.jsp')
def health():
    return Response('Server is ALIVE', content_type='text/plain')
