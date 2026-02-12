from flask import Flask, render_template, redirect, url_for, request, session, jsonify
from functools import wraps
import hashlib
from datetime import datetime

from app import app
from app.db import db
from app.models import User, Role, Dashboard, SavedQuery, DatabaseConnection


@app.after_request
def apply_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['Cache-Control'] = 'no-store'
    response.headers['Pragma'] = 'no-cache'
    return response


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login', next=request.url))
        user = User.query.get(session['user_id'])
        if not user:
            session.clear()
            return redirect(url_for('login'))
        role_names = [r.name for r in user.roles]
        if 'Admin' not in role_names:
            return render_template('403.html'), 403
        return f(*args, **kwargs)
    return decorated_function


@app.route('/health')
def health_check():
    return 'OK', 200


@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard_list'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard_list'))

    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        user = User.query.filter_by(username=username, active=True).first()
        if user and user.password:
            pw_hash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                username.encode('utf-8'),
                100000
            ).hex()
            if pw_hash == user.password:
                session['user_id'] = user.id
                session['username'] = user.username
                user.login_count = (user.login_count or 0) + 1
                user.last_login = datetime.utcnow()
                db.session.commit()
                next_url = request.args.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect(url_for('dashboard_list'))
        error = 'Invalid username or password'

    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/superset/dashboard/')
@login_required
def dashboard_list():
    user = User.query.get(session['user_id'])
    dashboards = Dashboard.query.filter_by(published=True).all()
    return render_template('dashboard_list.html', user=user, dashboards=dashboards)


@app.route('/superset/dashboard/<slug>/')
@login_required
def dashboard_view(slug):
    user = User.query.get(session['user_id'])
    dashboard = Dashboard.query.filter_by(slug=slug).first_or_404()
    return render_template('dashboard_view.html', user=user, dashboard=dashboard)


@app.route('/superset/sqllab/')
@login_required
def sql_lab():
    user = User.query.get(session['user_id'])
    queries = SavedQuery.query.all()
    return render_template('sqllab.html', user=user, queries=queries)


@app.route('/superset/profile/')
@login_required
def profile():
    user = User.query.get(session['user_id'])
    role_names = [r.name for r in user.roles]
    return render_template('profile.html', user=user, roles=role_names)


@app.route('/api/v1/me/')
@login_required
def api_me():
    user = User.query.get(session['user_id'])
    role_names = [r.name for r in user.roles]
    return jsonify({
        'result': {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'roles': role_names,
            'is_active': user.active,
        }
    })


@app.route('/api/v1/dashboard/')
@login_required
def api_dashboards():
    dashboards = Dashboard.query.all()
    result = []
    for d in dashboards:
        result.append({
            'id': d.id,
            'dashboard_title': d.dashboard_title,
            'slug': d.slug,
            'published': d.published,
            'changed_on': d.changed_on.isoformat() if d.changed_on else None,
        })
    return jsonify({'result': result, 'count': len(result)})


@app.route('/api/v1/database/')
@login_required
def api_databases():
    connections = DatabaseConnection.query.all()
    result = []
    for c in connections:
        result.append({
            'id': c.id,
            'database_name': c.database_name,
            'backend': c.sqlalchemy_uri.split('://')[0] if '://' in c.sqlalchemy_uri else 'unknown',
        })
    return jsonify({'result': result, 'count': len(result)})


@app.route('/api/v1/query/')
@login_required
def api_queries():
    queries = SavedQuery.query.all()
    result = []
    for q in queries:
        result.append({
            'id': q.id,
            'label': q.label,
            'description': q.description,
        })
    return jsonify({'result': result, 'count': len(result)})


@app.route('/users/list/')
@admin_required
def users_list():
    users = User.query.all()
    return render_template('users_list.html', users=users)


@app.route('/admin/config/')
@admin_required
def admin_config():
    from app import ConfigEntry
    configs = ConfigEntry.query.all()
    config_dict = {c.key: c.value for c in configs}
    return render_template('admin_config.html', config=config_dict)


@app.route('/api/v1/config/')
@admin_required
def api_config():
    from app import ConfigEntry
    configs = ConfigEntry.query.all()
    result = {c.key: c.value for c in configs}
    return jsonify({'result': result})
