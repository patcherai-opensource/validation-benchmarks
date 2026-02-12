import hashlib
from functools import wraps

from flask import (
    render_template, redirect, url_for, request, session, flash, jsonify
)
from flask_login import login_user, logout_user, login_required, current_user

from app import app
from app.db import db
from app.models import User, Connection, DagModel, Variable


@app.after_request
def apply_headers(response):
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    return response


def superuser_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        if not current_user.is_superuser:
            flash('Access denied. Superuser privileges required.', 'danger')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return redirect(url_for('login'))


@app.route('/health')
def health():
    return 'OK', 200


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        user = User.query.filter_by(username=username).first()
        if user and user.is_active:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            if user.password_hash == password_hash:
                login_user(user, remember=True)
                session['_user_role'] = 'Admin' if user.is_superuser else 'Viewer'
                next_page = request.args.get('next')
                return redirect(next_page or url_for('home'))

        flash('Invalid credentials.', 'danger')
        return render_template('login.html'), 401

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('login'))


@app.route('/home')
@login_required
def home():
    dags = DagModel.query.all()
    return render_template('home.html', dags=dags)


@app.route('/dags')
@login_required
def dag_list():
    dags = DagModel.query.all()
    return render_template('dags.html', dags=dags)


@app.route('/connection/list')
@superuser_required
def connection_list():
    connections = Connection.query.all()
    return render_template('connections.html', connections=connections)


@app.route('/variable/list')
@login_required
def variable_list():
    variables = Variable.query.all()
    return render_template('variables.html', variables=variables)


@app.route('/admin/user/list')
@superuser_required
def user_list():
    users = User.query.all()
    return render_template('users.html', users=users)


@app.route('/api/v1/dags', methods=['GET'])
@login_required
def api_dags():
    dags = DagModel.query.all()
    return jsonify({
        'dags': [
            {
                'dag_id': d.dag_id,
                'filepath': d.filepath,
                'is_paused': d.is_paused,
                'is_active': d.is_active,
            }
            for d in dags
        ],
        'total_entries': len(dags),
    })


@app.route('/api/v1/connections', methods=['GET'])
@superuser_required
def api_connections():
    connections = Connection.query.all()
    return jsonify({
        'connections': [
            {
                'connection_id': c.conn_id,
                'conn_type': c.conn_type,
                'host': c.host,
                'login': c.login,
                'password': c.password,
                'port': c.port,
                'extra': c.extra,
            }
            for c in connections
        ],
        'total_entries': len(connections),
    })


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', code=404, message='Page not found'), 404


@app.errorhandler(500)
def internal_error(e):
    return render_template('error.html', code=500, message='Internal server error'), 500
