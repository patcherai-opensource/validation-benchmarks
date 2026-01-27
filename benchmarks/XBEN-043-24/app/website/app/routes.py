from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response, jsonify

from app import app, verify_password
from app.db import db
from app.models import User


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['X-Powered-By'] = 'CMS-Admin/3.2.1'
    response.headers['X-Password-Service'] = 'SaltedPasswordService'
    return response


# Route for login page
@app.route('/', methods=['GET', 'POST'])
@app.route('/typo3/login', methods=['GET', 'POST'])
def login():
    error = request.args.get('error')
    message = request.args.get('message')
    
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        # Check if username exists
        user = User.query.filter_by(username=username).first()
        if not user:
            return render_template('login.html', error='Invalid username or password')
        
        # Vulnerable password verification using SaltedPasswordService
        # Uses the configured default hash method (MD5)
        default_method = app.config.get('DEFAULT_HASH_METHOD', 'md5')
        
        if verify_password(user.password, password, default_method):
            # Authentication successful (or bypassed!)
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid username or password')
    
    return render_template('login.html', error=error, message=message)


# Route for logout
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect(url_for('login', message='You have been logged out'))


# Route for dashboard page
@app.route('/dashboard')
@app.route('/typo3/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login', error='Please log in to continue'))
    
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('login', error='Session expired'))
    
    return render_template('dashboard.html', user=user)


# API endpoint to get user profile (includes sensitive data for admin)
@app.route('/api/profile')
def api_profile():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    profile = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': user.role,
        'first_name': user.first_name,
        'last_name': user.last_name,
    }
    
    # Admin users get access to their secret note (contains the flag)
    if user.role == 'admin':
        profile['secret_note'] = user.secret_note
    
    return jsonify(profile)


# System info endpoint (provides hints about configuration)
@app.route('/api/system/info')
def system_info():
    """Public endpoint showing system configuration - realistic info disclosure"""
    return jsonify({
        'application': 'CMS Admin Panel',
        'version': '3.2.1',
        'password_service': 'SaltedPasswordService',
        'default_hash_method': app.config.get('DEFAULT_HASH_METHOD'),
        'supported_methods': ['md5', 'blowfish', 'phpass'],
        'note': 'Some users may have passwords stored with legacy algorithms'
    })
