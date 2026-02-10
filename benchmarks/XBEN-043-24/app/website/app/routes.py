from flask import Flask, render_template, redirect, url_for, request, session, jsonify

from app import app
from app.db import db
from app.models import User
from app.password_service import validate_password


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', error_code=404, message='Page not found'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error_code=500, message='Internal server error'), 500


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = request.args.get('error')
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        user = User.query.filter_by(username=username).first()
        
        if user:
            if validate_password(password, user.password):
                session['user_id'] = user.id
                session['username'] = user.username
                session['role'] = user.role
                return redirect(url_for('dashboard'))
            else:
                return render_template('login.html', error='Invalid credentials')
        else:
            return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html', error=error)


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('login'))
    
    return render_template('dashboard.html', user=user)


@app.route('/admin')
def admin_panel():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if session.get('role') != 'admin':
        return render_template('error.html', error_code=403, message='Access denied'), 403
    
    users = User.query.all()
    return render_template('admin.html', users=users)


@app.route('/admin/system-config')
def system_config():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if session.get('role') != 'admin':
        return render_template('error.html', error_code=403, message='Access denied'), 403
    
    try:
        with open('/flag', 'r') as f:
            system_key = f.read().strip()
    except Exception:
        system_key = 'Configuration unavailable'
    
    config = {
        'system_encryption_key': system_key,
        'database_host': 'localhost',
        'cache_enabled': True,
        'session_timeout': 3600
    }
    return render_template('system_config.html', config=config)


@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('login'))
    
    return render_template('profile.html', user=user)
