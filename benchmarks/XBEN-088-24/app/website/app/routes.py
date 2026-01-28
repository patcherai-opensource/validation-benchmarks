from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response, jsonify

from app import app
from app.db import db
from app.models import User, LoginToken

import hashlib
import time
import random
import string
import secrets


@app.after_request
def add_header(request):
    request.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    request.headers['Pragma'] = 'no-cache'
    request.headers['Expires'] = '0'
    request.headers['Cache-Control'] = 'public, max-age=0'
    return request


class SessionError(Exception):
    def __init__(self, message='Session verification failed.'):
        self.message = message
        super().__init__(self.message)


def get_session():
    return app.session_interface.open_session(app, request)


def verify_session():
    """Verify a fully authenticated session (past 2FA)"""
    user = User.query.filter_by(username=session.get('username')).first()
    if user and session.get('authenticated') == True:
        session['user_id'] = user.id
        return True
    else:
        raise SessionError(message='Not authenticated. Please complete login.')


def verify_password(username, password):
    """Verify username and password only"""
    user = User.query.filter_by(username=username).first()
    if user:
        if user.password == password:
            return user
        else:
            return None
    return None


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "WyvernPanel"})


@app.route('/api/v1/status')
def api_status():
    """API status endpoint"""
    return jsonify({
        "version": "1.5.3",
        "api_version": "v1",
        "2fa_enabled": True,
        "maintenance": False
    })


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        user = verify_password(username, password)
        if user:
            if user.totp_enabled:
                # Generate confirmation token for 2FA checkpoint
                # VULNERABILITY: Token is predictable - based on user_id and timestamp
                # Format: auth_{user_id}_{timestamp_mod_10000}
                # This makes tokens enumerable if attacker knows an admin has 2FA enabled
                timestamp_suffix = int(time.time()) % 10000
                token = f"auth_{user.id}_{timestamp_suffix}"
                
                # Store token mapping to user_id in database
                login_token = LoginToken(
                    token=token,
                    user_id=user.id,
                    created_at=int(time.time())
                )
                db.session.add(login_token)
                db.session.commit()
                
                return jsonify({
                    "complete": False,
                    "confirmation_token": token,
                    "message": "Two-factor authentication required",
                    "redirect": "/auth/checkpoint"
                })
            else:
                # User doesn't have 2FA, log them in directly
                session['username'] = username
                session['authenticated'] = True
                return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials')


@app.route('/auth/checkpoint', methods=['GET', 'POST'])
def auth_checkpoint():
    """
    Two-factor authentication checkpoint.
    VULNERABILITY: Trusts user-supplied confirmation_token without validating
    it belongs to the current authentication flow.
    """
    if request.method == 'GET':
        return render_template('checkpoint.html')
    
    elif request.method == 'POST':
        # Accept both form data and JSON
        if request.is_json:
            data = request.get_json()
            confirmation_token = data.get('confirmation_token', '')
            auth_code = data.get('authentication_code', '')
        else:
            confirmation_token = request.form.get('confirmation_token', '')
            auth_code = request.form.get('authentication_code', '')
        
        if not confirmation_token:
            return jsonify({"error": "Missing confirmation token"}), 400
        
        # VULNERABILITY: Directly use user-supplied token to look up user
        # This allows an attacker to specify ANY token and authenticate as that user
        login_token = LoginToken.query.filter_by(token=confirmation_token).first()
        
        if not login_token:
            return jsonify({"error": "Invalid or expired token"}), 401
        
        # Check if token is expired (valid for 5 minutes)
        if int(time.time()) - login_token.created_at > 300:
            db.session.delete(login_token)
            db.session.commit()
            return jsonify({"error": "Token expired"}), 401
        
        user = User.query.get(login_token.user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Verify TOTP code (simplified: accept any 6-digit code for the admin)
        # For regular users, accept matching code
        if user.is_admin:
            # Admin's TOTP always validates (simulating the attacker having obtained the code)
            valid_code = True
        else:
            # Regular users need correct code
            valid_code = (auth_code == user.totp_secret)
        
        if valid_code or auth_code == "000000":  # Backdoor code for testing
            # Authenticate as the user from the token (NOT necessarily the original user)
            session['username'] = user.username
            session['authenticated'] = True
            session['user_id'] = user.id
            
            # Clean up token
            db.session.delete(login_token)
            db.session.commit()
            
            return jsonify({
                "complete": True,
                "message": f"Welcome, {user.username}!",
                "redirect": "/dashboard"
            })
        else:
            return jsonify({"error": "Invalid authentication code"}), 401


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/admin')
def admin_panel():
    try:
        verify_session()
    except SessionError as e:
        return render_template('login.html', error=e.message)

    user = User.query.filter_by(username=session.get('username')).first()
    if user and user.is_admin:
        with open('/flag') as flag_file:
            flag_content = flag_file.read()
        return render_template('admin_panel.html', flag=flag_content)
    else:
        return render_template('dashboard.html', error_message='Access denied. Administrator privileges required.')


@app.route('/dashboard')
def dashboard():
    try:
        verify_session()
    except SessionError as e:
        return render_template('login.html', error=e.message)

    return render_template('dashboard.html')


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    try:
        verify_session()
    except SessionError as e:
        return render_template('login.html', error=e.message)

    if request.method == 'GET':
        return render_template('settings.html')
    elif request.method == 'POST':
        return render_template('settings.html', message='Settings updated successfully.')


@app.route('/servers')
def servers():
    try:
        verify_session()
    except SessionError as e:
        return render_template('login.html', error=e.message)
    return render_template('servers.html')


@app.route('/api/v1/auth/status')
def auth_status():
    """Authentication service status"""
    # Simulate admin activity - ensure there's always an admin token
    # This represents the admin periodically logging in
    admin = User.query.filter_by(username='admin').first()
    if admin:
        existing_token = LoginToken.query.filter_by(user_id=admin.id).first()
        if not existing_token:
            # Admin "starts" a new login attempt
            admin_token = LoginToken(
                token=f"auth_{admin.id}_{int(time.time()) % 10000}",
                user_id=admin.id,
                created_at=int(time.time())
            )
            db.session.add(admin_token)
            db.session.commit()
    
    count = LoginToken.query.count()
    return jsonify({
        "service": "authentication",
        "pending_2fa_sessions": count,
        "token_ttl": 300,
        "debug": False
    })


@app.route('/api/v1/users')
def list_users():
    """List users (limited info for non-admin)"""
    users = User.query.all()
    return jsonify({
        "users": [
            {
                "id": u.id,
                "username": u.username,
                "has_2fa": u.totp_enabled,
                "role": "admin" if u.is_admin else "user"
            }
            for u in users
        ]
    })
