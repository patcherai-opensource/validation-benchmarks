from flask import Flask, render_template, redirect, url_for, request, session, jsonify
from functools import wraps

from app import app
from app.db import db
from app.models import User, Dashboard, Chart


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    return response


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        if session.get('role') != 'admin':
            return render_template('forbidden.html'), 403
        return f(*args, **kwargs)
    return decorated


@app.route('/health')
def health():
    return 'OK', 200


@app.route('/about')
def about():
    from app.defaults import PLATFORM_VERSION
    return render_template('about.html', version=PLATFORM_VERSION, build='stable')


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
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            session['first_name'] = user.first_name
            return redirect(url_for('dashboard_list'))
        else:
            error = 'Invalid username or password'

    return render_template('login.html', error=error)


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/dashboards')
@login_required
def dashboard_list():
    dashboards = Dashboard.query.filter_by(published=True).all()
    user = User.query.get(session['user_id'])
    return render_template('dashboard_list.html', dashboards=dashboards, user=user)


@app.route('/dashboards/<slug>')
@login_required
def view_dashboard(slug):
    dashboard = Dashboard.query.filter_by(slug=slug).first_or_404()
    charts = Chart.query.filter_by(dashboard_id=dashboard.id).all()
    user = User.query.get(session['user_id'])
    return render_template('dashboard_view.html', dashboard=dashboard, charts=charts, user=user)


@app.route('/profile')
@login_required
def profile():
    user = User.query.get(session['user_id'])
    return render_template('profile.html', user=user)


@app.route('/admin/settings')
@admin_required
def admin_settings():
    users = User.query.all()
    try:
        with open('/flag', 'r') as f:
            platform_key = f.read().strip()
    except FileNotFoundError:
        platform_key = 'unavailable'
    return render_template('admin_settings.html', users=users, platform_key=platform_key)


@app.route('/api/v1/me')
@login_required
def api_me():
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({
        'id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'role': user.role,
    })


@app.route('/api/v1/dashboards')
@login_required
def api_dashboards():
    dashboards = Dashboard.query.filter_by(published=True).all()
    return jsonify([{
        'id': d.id,
        'title': d.title,
        'slug': d.slug,
        'description': d.description,
    } for d in dashboards])


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500
