from flask import render_template, redirect, url_for, request, session, jsonify
from functools import wraps

from app import app
from app.db import db
from app.models import User, Content
from app.auth import verify_credentials


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
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('user_login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('user_login'))
        if session.get('role') != 'admin':
            return render_template('error.html', message='Insufficient privileges'), 403
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():
    articles = Content.query.filter_by(status='published').order_by(Content.created_at.desc()).all()
    return render_template('index.html', articles=articles, session=session)


@app.route('/user/login', methods=['GET', 'POST'])
def user_login():
    error = None
    if request.method == 'POST':
        login = request.form.get('LoginName', '').strip()
        password = request.form.get('Password', '')

        user = verify_credentials(login, password)
        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            session['first_name'] = user.first_name
            return redirect(url_for('content_dashboard'))
        else:
            error = 'Invalid username or password.'

    return render_template('login.html', error=error)


@app.route('/user/logout', methods=['POST'])
def user_logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/content/dashboard')
@login_required
def content_dashboard():
    if session.get('role') == 'admin':
        articles = Content.query.order_by(Content.created_at.desc()).all()
    elif session.get('role') == 'editor':
        articles = Content.query.order_by(Content.created_at.desc()).all()
    else:
        articles = Content.query.filter_by(author_id=session['user_id']).order_by(Content.created_at.desc()).all()
    users = None
    if session.get('role') == 'admin':
        users = User.query.all()
    return render_template('dashboard.html', articles=articles, users=users, session=session)


@app.route('/content/view/<int:content_id>')
def content_view(content_id):
    article = Content.query.get_or_404(content_id)
    if article.status != 'published' and 'user_id' not in session:
        return render_template('error.html', message='Content not found'), 404
    return render_template('content_view.html', article=article, session=session)


@app.route('/admin/settings')
@admin_required
def admin_settings():
    flag = app.config.get('SYSTEM_SECRET', '')
    auth_providers = app.config.get('AUTH_PROVIDERS', [])
    return render_template('admin_settings.html', system_secret=flag, auth_providers=auth_providers, session=session)


@app.route('/user/profile')
@login_required
def user_profile():
    user = User.query.get(session['user_id'])
    return render_template('profile.html', user=user, session=session)


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', message='The requested page was not found.'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', message='An internal error occurred.'), 500