from flask import render_template, redirect, url_for, request, session, jsonify

from app import app
from app.db import db
from app.models import User, UserRole, ContentObject, SiteConfig
from app.loginhandler import check_user


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['X-Powered-By'] = 'eZ Publish'
    return response


def _get_current_user():
    uid = session.get('user_id')
    if uid is None:
        return None
    return User.query.get(uid)


def _get_user_role(user):
    if user is None:
        return None
    role = UserRole.query.filter_by(user_id=user.id).first()
    return role.role_name if role else 'member'


@app.route('/')
def index():
    user = _get_current_user()
    articles = ContentObject.query.filter_by(published=1, content_type='article').all()
    return render_template('index.html', user=user, articles=articles)


@app.route('/user/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        login_name = request.form.get('Login', '')
        password = request.form.get('Password', '')

        user = check_user(login_name, password)
        if user is not None:
            session['user_id'] = user.id
            session['login'] = user.login
            role = _get_user_role(user)
            session['role'] = role
            if role == 'administrator':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('index'))
        else:
            error = 'Could not login. Please check your login name and password.'

    return render_template('login.html', error=error)


@app.route('/user/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/content/view/<int:object_id>')
def content_view(object_id):
    obj = ContentObject.query.get_or_404(object_id)
    user = _get_current_user()
    role = _get_user_role(user) if user else None

    if obj.published == 0:
        if role not in ('administrator', 'editor'):
            return render_template('access_denied.html'), 403

    return render_template('content_view.html', user=user, content=obj)


@app.route('/content/list')
def content_list():
    user = _get_current_user()
    role = _get_user_role(user) if user else None

    if role in ('administrator', 'editor'):
        objects = ContentObject.query.all()
    else:
        objects = ContentObject.query.filter_by(published=1).all()

    return render_template('content_list.html', user=user, objects=objects)


@app.route('/admin')
def admin_dashboard():
    user = _get_current_user()
    if user is None:
        return redirect(url_for('login'))
    role = _get_user_role(user)
    if role != 'administrator':
        return render_template('access_denied.html'), 403

    users = User.query.filter(User.login != 'anonymous').all()
    content_count = ContentObject.query.count()
    configs = SiteConfig.query.all()
    return render_template('admin_dashboard.html', user=user, users=users,
                           content_count=content_count, configs=configs)


@app.route('/admin/settings')
def admin_settings():
    user = _get_current_user()
    if user is None:
        return redirect(url_for('login'))
    role = _get_user_role(user)
    if role != 'administrator':
        return render_template('access_denied.html'), 403

    configs = SiteConfig.query.all()
    return render_template('admin_settings.html', user=user, configs=configs)
