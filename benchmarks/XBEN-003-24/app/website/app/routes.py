import json
from json import JSONDecodeError
from functools import wraps

from flask import (Flask, render_template, redirect, url_for,
                   request, session, Response, flash, abort)

from app import app
from app.db import db
from app.models import User, PipelineConnection, Pipeline


MASKED_PLACEHOLDER = '********'


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    return response


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def editor_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if not user or user.role not in ('editor', 'admin'):
            abort(403)
        return f(*args, **kwargs)
    return decorated


def get_current_user():
    uid = session.get('user_id')
    if uid:
        return User.query.get(uid)
    return None


@app.route('/', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('home'))
    error = request.args.get('error')
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html', error=error)


@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))


@app.route('/home')
@login_required
def home():
    user = get_current_user()
    pipelines = Pipeline.query.all()
    return render_template('home.html', user=user, pipelines=pipelines)


@app.route('/pipeline')
@login_required
def pipeline_list():
    user = get_current_user()
    pipelines = Pipeline.query.order_by(Pipeline.pipeline_id.asc()).all()
    return render_template('pipeline_list.html', user=user, pipelines=pipelines)


@app.route('/integration')
@login_required
def integration_list():
    user = get_current_user()
    connections = PipelineConnection.query.order_by(PipelineConnection.conn_id.asc()).all()
    return render_template('integration_list.html', user=user, connections=connections)


@app.route('/integration/add', methods=['GET', 'POST'])
@editor_required
def integration_add():
    user = get_current_user()
    if request.method == 'POST':
        conn_id = request.form.get('conn_id', '').strip()
        conn_type = request.form.get('conn_type', '').strip()
        description = request.form.get('description', '').strip()
        host = request.form.get('host', '').strip()
        schema_name = request.form.get('schema_name', '').strip()
        login_val = request.form.get('login', '').strip()
        password_val = request.form.get('password', '').strip()
        port_str = request.form.get('port', '').strip()
        extra_raw = request.form.get('extra', '').strip()

        if not conn_id or not conn_type:
            flash('Connection ID and Type are required.', 'error')
            return render_template('integration_form.html', user=user, form_data=request.form,
                                   action='add', title='Add Integration')

        existing = PipelineConnection.query.filter_by(conn_id=conn_id).first()
        if existing:
            flash(f'Integration with ID "{conn_id}" already exists.', 'error')
            return render_template('integration_form.html', user=user, form_data=request.form,
                                   action='add', title='Add Integration')

        port_val = None
        if port_str:
            try:
                port_val = int(port_str)
            except ValueError:
                flash('Port must be a valid integer.', 'error')
                return render_template('integration_form.html', user=user, form_data=request.form,
                                       action='add', title='Add Integration')

        if extra_raw:
            try:
                json.loads(extra_raw)
            except (JSONDecodeError, TypeError):
                flash('Extra field must be valid JSON.', 'error')
                return render_template('integration_form.html', user=user, form_data=request.form,
                                       action='add', title='Add Integration')

        conn = PipelineConnection(
            conn_id=conn_id,
            conn_type=conn_type,
            description=description,
            host=host,
            schema_name=schema_name,
            login=login_val,
            password=password_val,
            port=port_val,
            extra=extra_raw if extra_raw else None,
            is_active=True,
        )
        db.session.add(conn)
        db.session.commit()
        flash(f'Integration "{conn_id}" created successfully.', 'success')
        return redirect(url_for('integration_list'))

    return render_template('integration_form.html', user=user, form_data={},
                           action='add', title='Add Integration')


@app.route('/integration/detail/<int:pk>')
@login_required
def integration_detail(pk):
    user = get_current_user()
    conn = PipelineConnection.query.get_or_404(pk)

    from app import should_mask_field

    display_password = MASKED_PLACEHOLDER if conn.password else ''

    display_extra = conn.extra
    if conn.extra:
        try:
            extra_dict = json.loads(conn.extra)
            masked_dict = {}
            for k, v in extra_dict.items():
                if should_mask_field(k):
                    masked_dict[k] = MASKED_PLACEHOLDER
                else:
                    masked_dict[k] = v
            display_extra = json.dumps(masked_dict, indent=2)
        except (JSONDecodeError, TypeError):
            display_extra = conn.extra

    return render_template('integration_detail.html', user=user, conn=conn,
                           display_password=display_password, display_extra=display_extra)


@app.route('/integration/edit/<int:pk>', methods=['GET', 'POST'])
@editor_required
def integration_edit(pk):
    user = get_current_user()
    conn = PipelineConnection.query.get_or_404(pk)

    if request.method == 'POST':
        return _handle_edit_submit(conn, user)

    form_data = _populate_edit_form(conn)
    return render_template('integration_form.html', user=user, form_data=form_data,
                           action='edit', title=f'Edit Integration: {conn.conn_id}',
                           conn=conn)


def _populate_edit_form(conn):
    """Populate form fields from connection record for the edit view.

    Iterates over all stored fields including the extra JSON and populates
    them into the form data dictionary for rendering.
    """
    form_data = {
        'conn_id': conn.conn_id,
        'conn_type': conn.conn_type,
        'description': conn.description or '',
        'host': conn.host or '',
        'schema_name': conn.schema_name or '',
        'login': conn.login or '',
        'password': MASKED_PLACEHOLDER if conn.password else '',
        'port': str(conn.port) if conn.port is not None else '',
    }

    # Populate extra fields from the stored JSON into the form verbatim.
    # All fields from extra are copied into the form for display.
    if conn.extra:
        try:
            extra_dict = json.loads(conn.extra)
            form_data['extra'] = json.dumps(extra_dict, indent=2)
        except (JSONDecodeError, TypeError):
            form_data['extra'] = conn.extra
    else:
        form_data['extra'] = ''

    return form_data


def _handle_edit_submit(conn, user):
    """Process the edit form submission."""
    conn.conn_type = request.form.get('conn_type', conn.conn_type).strip()
    conn.description = request.form.get('description', '').strip()
    conn.host = request.form.get('host', '').strip()
    conn.schema_name = request.form.get('schema_name', '').strip()
    conn.login = request.form.get('login', '').strip()

    password_val = request.form.get('password', '').strip()
    if password_val and password_val != MASKED_PLACEHOLDER:
        conn.password = password_val

    port_str = request.form.get('port', '').strip()
    if port_str:
        try:
            conn.port = int(port_str)
        except ValueError:
            flash('Port must be a valid integer.', 'error')
            return render_template('integration_form.html', user=user,
                                   form_data=request.form, action='edit',
                                   title=f'Edit Integration: {conn.conn_id}', conn=conn)
    else:
        conn.port = None

    extra_raw = request.form.get('extra', '').strip()
    if extra_raw:
        try:
            json.loads(extra_raw)
            conn.extra = extra_raw
        except (JSONDecodeError, TypeError):
            flash('Extra field must be valid JSON.', 'error')
            return render_template('integration_form.html', user=user,
                                   form_data=request.form, action='edit',
                                   title=f'Edit Integration: {conn.conn_id}', conn=conn)
    else:
        conn.extra = None

    db.session.commit()
    flash(f'Integration "{conn.conn_id}" updated.', 'success')
    return redirect(url_for('integration_list'))


@app.route('/integration/delete/<int:pk>', methods=['POST'])
@editor_required
def integration_delete(pk):
    conn = PipelineConnection.query.get_or_404(pk)
    conn_id = conn.conn_id
    db.session.delete(conn)
    db.session.commit()
    flash(f'Integration "{conn_id}" deleted.', 'success')
    return redirect(url_for('integration_list'))


@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', code=403, message='Forbidden'), 403


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', code=404, message='Not Found'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', code=500, message='Internal Server Error'), 500
