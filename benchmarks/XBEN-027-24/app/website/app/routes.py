import functools
import time

from flask import Flask, render_template, redirect, url_for, request, session, jsonify, Response
import jwt

from app import app
from app.db import db
from app.models import User, Role, UserRole, SystemConfig

JWT_SIGN_KEY = 'lamp-cloud_is_a_fantastic_project'
JWT_ALGORITHM = 'HS256'
JWT_EXPIRE_SECONDS = 7200


@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    return response


def _create_token(user_id, account, role_code):
    now = int(time.time())
    payload = {
        'userId': user_id,
        'account': account,
        'roleCode': role_code,
        'iat': now,
        'exp': now + JWT_EXPIRE_SECONDS,
    }
    return jwt.encode(payload, JWT_SIGN_KEY, algorithm=JWT_ALGORITHM)


def _verify_token(token_str):
    try:
        data = jwt.decode(token_str, JWT_SIGN_KEY, algorithms=[JWT_ALGORITHM])
        return data
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def _get_auth_info():
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        token_str = auth_header[7:]
        return _verify_token(token_str)

    token_cookie = request.cookies.get('token')
    if token_cookie:
        return _verify_token(token_cookie)

    return None


def require_auth(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        auth_info = _get_auth_info()
        if not auth_info:
            if request.path.startswith('/api/'):
                return jsonify({'code': 401, 'msg': 'Unauthorized', 'data': None}), 401
            return redirect(url_for('login'))
        request.auth_info = auth_info
        return f(*args, **kwargs)
    return decorated


def require_role(role_code):
    def decorator(f):
        @functools.wraps(f)
        def decorated(*args, **kwargs):
            auth_info = getattr(request, 'auth_info', None)
            if not auth_info or auth_info.get('roleCode') != role_code:
                if request.path.startswith('/api/'):
                    return jsonify({'code': 403, 'msg': 'Forbidden: insufficient privileges', 'data': None}), 403
                return render_template('error.html', code=403, message='Insufficient privileges'), 403
            return f(*args, **kwargs)
        return decorated
    return decorator


# ---- Web UI routes ----

@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        account = request.form.get('account', '').strip()
        password = request.form.get('password', '').strip()

        if not account or not password:
            return render_template('login.html', error='Account and password are required')

        user = User.query.filter_by(account=account, status=True).first()
        if not user or not user.check_password(password):
            return render_template('login.html', error='Invalid account or password')

        user_role = db.session.query(Role.code).join(
            UserRole, UserRole.role_id == Role.id
        ).filter(UserRole.user_id == user.id).first()

        role_code = user_role[0] if user_role else 'PLATFORM_USER'
        token = _create_token(user.id, user.account, role_code)

        resp = redirect(url_for('dashboard'))
        resp.set_cookie('token', token, httponly=True, samesite='Lax')
        return resp

    return render_template('login.html', error=None)


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    resp = redirect(url_for('login'))
    resp.delete_cookie('token')
    return resp


@app.route('/dashboard')
@require_auth
def dashboard():
    auth = request.auth_info
    user = User.query.get(auth['userId'])
    if not user:
        return redirect(url_for('login'))
    return render_template('dashboard.html', user=user, role=auth.get('roleCode', ''))


@app.route('/admin/config')
@require_auth
@require_role('SUPER_ADMIN')
def admin_config():
    configs = SystemConfig.query.all()
    return render_template('admin_config.html', configs=configs)


# ---- API routes (gateway-style) ----

@app.route('/api/user/info')
@require_auth
def api_user_info():
    auth = request.auth_info
    user = User.query.get(auth['userId'])
    if not user:
        return jsonify({'code': 404, 'msg': 'User not found', 'data': None}), 404
    return jsonify({
        'code': 0,
        'msg': 'success',
        'data': {
            'id': user.id,
            'account': user.account,
            'name': user.name,
            'email': user.email,
            'status': user.status,
        }
    })


@app.route('/api/user/list')
@require_auth
@require_role('SUPER_ADMIN')
def api_user_list():
    users = User.query.all()
    return jsonify({
        'code': 0,
        'msg': 'success',
        'data': [{
            'id': u.id,
            'account': u.account,
            'name': u.name,
            'email': u.email,
            'status': u.status,
        } for u in users]
    })


@app.route('/api/system/config')
@require_auth
@require_role('SUPER_ADMIN')
def api_system_config():
    configs = SystemConfig.query.all()
    return jsonify({
        'code': 0,
        'msg': 'success',
        'data': [{
            'id': c.id,
            'key': c.key,
            'value': c.value,
            'description': c.description,
        } for c in configs]
    })


@app.route('/api/health')
def api_health():
    return jsonify({'code': 0, 'msg': 'ok', 'data': {'status': 'UP'}})
