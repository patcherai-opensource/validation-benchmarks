import functools
from flask import (
    Flask, render_template, redirect, url_for,
    request, session, Response, flash, abort
)

from app import app
from app.db import db
from app.models import User, Connection, DagModel, Variable


SENSITIVE_FIELD_PLACEHOLDER = '********'


@app.after_request
def add_security_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    return response


def login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def get_current_user():
    user_id = session.get('user_id')
    if user_id:
        return User.query.get(user_id)
    return None


def has_permission(user, permission):
    role_permissions = {
        'Admin': ['can_read', 'can_edit', 'can_create', 'can_delete'],
        'Op': ['can_read', 'can_edit', 'can_create'],
        'User': ['can_read', 'can_edit'],
        'Viewer': ['can_read'],
    }
    return permission in role_permissions.get(user.role, [])


def mask_password(val):
    if val:
        return SENSITIVE_FIELD_PLACEHOLDER
    return ''


@app.route('/health')
def health():
    return 'OK', 200


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('home'))
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username, active=True).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            next_url = request.args.get('next')
            return redirect(next_url or url_for('home'))
        error = 'Invalid login. Please try again.'
    return render_template('login.html', error=error)


@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/')
@login_required
def home():
    user = get_current_user()
    dags = DagModel.query.all()
    return render_template('home.html', user=user, dags=dags)


@app.route('/dags')
@login_required
def dag_list():
    user = get_current_user()
    dags = DagModel.query.all()
    return render_template('dags.html', user=user, dags=dags)


@app.route('/connection')
@login_required
def connection_list():
    user = get_current_user()
    if not has_permission(user, 'can_read'):
        abort(403)
    connections = Connection.query.all()
    return render_template('connection_list.html', user=user,
                           connections=connections, mask_password=mask_password)


@app.route('/connection/edit/<int:conn_pk>', methods=['GET', 'POST'])
@login_required
def connection_edit(conn_pk):
    user = get_current_user()
    if not has_permission(user, 'can_edit'):
        abort(403)

    conn = Connection.query.get_or_404(conn_pk)

    if request.method == 'POST':
        conn.conn_id = request.form.get('conn_id', conn.conn_id)
        conn.conn_type = request.form.get('conn_type', conn.conn_type)
        conn.description = request.form.get('description', conn.description)
        conn.host = request.form.get('host', conn.host)
        conn.schema = request.form.get('schema', conn.schema)
        conn.login = request.form.get('login', conn.login)

        new_password = request.form.get('password', '')
        if new_password and new_password != SENSITIVE_FIELD_PLACEHOLDER:
            conn.password = new_password

        port_str = request.form.get('port', '')
        if port_str:
            try:
                conn.port = int(port_str)
            except ValueError:
                pass

        new_extra = request.form.get('extra', '')
        if new_extra:
            conn.extra = new_extra

        db.session.commit()
        flash('Connection updated successfully.', 'success')
        return redirect(url_for('connection_list'))

    form_data = {
        'conn_id': conn.conn_id,
        'conn_type': conn.conn_type,
        'description': conn.description or '',
        'host': conn.host or '',
        'schema': conn.schema or '',
        'login': conn.login or '',
        'password': SENSITIVE_FIELD_PLACEHOLDER if conn.password else '',
        'port': conn.port if conn.port else '',
        'extra': conn.extra or '',
    }

    return render_template('connection_edit.html', user=user, conn=conn,
                           form_data=form_data)


@app.route('/connection/add', methods=['GET', 'POST'])
@login_required
def connection_add():
    user = get_current_user()
    if not has_permission(user, 'can_create'):
        abort(403)

    if request.method == 'POST':
        new_conn = Connection(
            conn_id=request.form.get('conn_id', ''),
            conn_type=request.form.get('conn_type', ''),
            description=request.form.get('description', ''),
            host=request.form.get('host', ''),
            schema=request.form.get('schema', ''),
            login=request.form.get('login', ''),
            password=request.form.get('password', ''),
            port=int(request.form.get('port', 0)) if request.form.get('port') else None,
            extra=request.form.get('extra', ''),
            is_encrypted=False,
            is_extra_encrypted=False,
        )
        db.session.add(new_conn)
        db.session.commit()
        flash('Connection created successfully.', 'success')
        return redirect(url_for('connection_list'))

    return render_template('connection_add.html', user=user)


@app.route('/variable')
@login_required
def variable_list():
    user = get_current_user()
    if not has_permission(user, 'can_read'):
        abort(403)
    variables = Variable.query.all()
    return render_template('variable_list.html', user=user, variables=variables)


@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', code=403,
                           message='Access is Denied'), 403


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', code=404,
                           message='Page Not Found'), 404


@app.errorhandler(500)
def internal_error(e):
    return render_template('error.html', code=500,
                           message='Internal Server Error'), 500
