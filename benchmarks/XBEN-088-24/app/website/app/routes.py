from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response, jsonify

from app import app
from app.db import db
from app.models import User

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
    def __init__(self, message='Session verifcation failed.'):
        self.message = message
        super().__init__(self.message)


# In-memory token store simulating cache (CVE-2021-41129 vulnerability pattern)
# Maps confirmation_token -> user_id
# This simulates the vulnerable cache where tokens map to user IDs
login_token_cache = {}

# Store TOTP secrets for users with 2FA enabled (in a real app, this would be per-user)
# For this CTF, admin users have 2FA enabled with a known secret
TOTP_SECRET = "ROUTERXYZ2FA"  # Simplified - in real app would be per-user

def generate_totp_code():
    """Generate a simple time-based code (simplified TOTP for CTF purposes)"""
    # Use a simple algorithm: hash of secret + time window (30 second windows)
    time_window = int(time.time()) // 30
    code_data = f"{TOTP_SECRET}:{time_window}"
    code_hash = hashlib.sha256(code_data.encode()).hexdigest()
    # Return last 6 digits as the code
    return str(int(code_hash[:8], 16) % 1000000).zfill(6)

def verify_totp_code(submitted_code):
    """Verify TOTP code - accepts current and previous window for clock drift"""
    current_code = generate_totp_code()
    # Also accept previous time window for clock drift
    time_window = int(time.time()) // 30 - 1
    code_data = f"{TOTP_SECRET}:{time_window}"
    code_hash = hashlib.sha256(code_data.encode()).hexdigest()
    prev_code = str(int(code_hash[:8], 16) % 1000000).zfill(6)
    
    return submitted_code == current_code or submitted_code == prev_code


def get_session():
    return app.session_interface.open_session(app, request)

def verify_session():
    user = User.query.filter_by(username=session.get('username')).first()
    if user:
        user_password_hashed = hashlib.pbkdf2_hmac('sha256', user.password.encode(), app.secret_key.encode(), 100000).hex()
        if session.get('password_hash') == user_password_hashed:
            # Store user ID in session
            session['user_id'] = user.id
            session['session_id'] = session.sid
            # If login successful, redirect to home page
            return True
        else:
            raise SessionError(message='Wrong password.')
    else:
        raise SessionError(message='Invalid username.')


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Step 1 of login - username/password verification.
    For users with 2FA enabled (admin), this returns a confirmation_token
    that must be used in the checkpoint step.
    """
    debug_session = None
    debug = request.args.get('debug')
    if debug == 'session':
        debug = True

    if request.method == 'GET':
        if debug:
            debug_session = str(dict(session.items()))
        return render_template('login.html', debug_session=debug_session)
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # First verify credentials
        user = User.query.filter_by(username=username).first()
        if not user:
            return render_template('login.html', error='Invalid username.')
        
        # Verify password
        user_password_hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), app.secret_key.encode(), 100000).hex()
        stored_password_hashed = hashlib.pbkdf2_hmac('sha256', user.password.encode(), app.secret_key.encode(), 100000).hex()
        
        if user_password_hashed != stored_password_hashed:
            return render_template('login.html', error='Wrong password.')
        
        # Check if user has 2FA enabled (admin users have 2FA)
        if user.has_2fa:
            # Generate confirmation token and store in cache
            # VULNERABILITY: This token will be trusted directly from user input in checkpoint
            confirmation_token = secrets.token_hex(16)
            
            # Store the mapping: token -> user_id in cache
            login_token_cache[confirmation_token] = user.id
            
            # Return the 2FA checkpoint page with the token
            return render_template('checkpoint.html', confirmation_token=confirmation_token)
        else:
            # No 2FA - proceed with normal login
            session['username'] = username
            session['password_hash'] = hashlib.pbkdf2_hmac('sha256', password.encode(), app.secret_key.encode(), 100000).hex()
            session['authenticated'] = True
            return redirect(url_for('dashboard'))


@app.route('/auth/login/checkpoint', methods=['POST'])
def login_checkpoint():
    """
    Step 2 of login - 2FA verification (checkpoint).
    
    VULNERABLE CODE (CVE-2021-41129 pattern):
    The confirmation_token is taken directly from user input and used as a cache key
    to look up the user_id. There is NO validation that this token was issued to
    the current user's session. An attacker can supply a different user's token
    to authenticate as that user.
    """
    # Get user-supplied confirmation token
    confirmation_token = request.form.get('confirmation_token')
    authentication_code = request.form.get('authentication_code')
    
    if not confirmation_token or not authentication_code:
        return render_template('checkpoint.html', 
                             error='Missing confirmation token or authentication code.',
                             confirmation_token=confirmation_token or '')
    
    # VULNERABILITY: The confirmation_token is trusted directly from user input
    # We fetch whatever user_id is stored for this token, without validating
    # that this token was issued for the current user's login attempt.
    # An attacker can supply another user's token to authenticate as them.
    user_id = login_token_cache.get(confirmation_token, 0)
    
    if user_id == 0:
        return render_template('checkpoint.html',
                             error='Invalid or expired confirmation token.',
                             confirmation_token=confirmation_token)
    
    # Look up the user by ID from the token cache
    user = User.query.get(user_id)
    if not user:
        return render_template('checkpoint.html',
                             error='User not found.',
                             confirmation_token=confirmation_token)
    
    # Verify the TOTP code
    if not verify_totp_code(authentication_code):
        return render_template('checkpoint.html',
                             error='Invalid authentication code.',
                             confirmation_token=confirmation_token)
    
    # Authentication successful - set up session for the user from the token cache
    # Note: The user authenticated is determined by the token, not by who initiated the login!
    session['username'] = user.username
    session['password_hash'] = hashlib.pbkdf2_hmac('sha256', user.password.encode(), app.secret_key.encode(), 100000).hex()
    session['authenticated'] = True
    session['user_id'] = user.id
    
    # Clean up the token (but there's a race window before this happens)
    if confirmation_token in login_token_cache:
        del login_token_cache[confirmation_token]
    
    return redirect(url_for('dashboard'))


@app.route('/auth/tokens/active')
def list_active_tokens():
    """
    Debug endpoint that lists active tokens (simulates information leak).
    In a real scenario, an attacker might discover tokens through timing attacks,
    logs, or other side channels.
    """
    # Only show token prefixes (first 8 chars) to make it somewhat challenging
    # but provide enough info to enumerate
    tokens_info = []
    for token, user_id in login_token_cache.items():
        user = User.query.get(user_id)
        tokens_info.append({
            'token_prefix': token[:8] + '...',
            'full_token': token,  # In real exploit this wouldn't be exposed
            'user_type': 'admin' if user and user.is_admin else 'regular'
        })
    return jsonify({'active_tokens': tokens_info, 'count': len(tokens_info)})


@app.route('/simulate/admin_login')
def simulate_admin_login():
    """
    Simulates the admin user initiating a login (step 1).
    In a real scenario, this would happen when the admin user visits the login page
    and enters their credentials. This endpoint allows us to trigger the creation
    of an admin token for testing the vulnerability.
    
    This simulates the real-world scenario where:
    1. Admin user logs in with username/password
    2. System generates a confirmation_token for 2FA
    3. Token is stored in cache, waiting for TOTP verification
    4. An attacker can steal/guess this token before the admin completes 2FA
    """
    # Find the admin user
    admin = User.query.filter_by(username='admin', is_admin=True).first()
    if not admin:
        return jsonify({'error': 'Admin user not found'}), 404
    
    # Generate a confirmation token for the admin (simulating step 1 of login)
    confirmation_token = secrets.token_hex(16)
    login_token_cache[confirmation_token] = admin.id
    
    return jsonify({
        'message': 'Admin login initiated (step 1 complete, waiting for 2FA)',
        'token_created': True,
        'token_hint': confirmation_token[:8] + '...',
        'note': 'In a real scenario, this happens when admin visits /login and enters credentials'
    })


@app.route('/logout')
def logout():
    # Clear session
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('password_hash', None)
    session.pop('authenticated', None)
    return redirect(url_for('login'))


@app.route('/admin_panel')
def admin_panel():
    debug_session = None
    debug = request.args.get('debug')
    if debug == 'session':
        debug = True

    # Check if user is authenticated
    if not session.get('authenticated'):
        return render_template('login.html', error='Please log in first.')
    
    username = session.get('username')
    user = User.query.filter_by(username=username).first()
    
    if not user:
        return render_template('login.html', error='Invalid session.')
    
    if user.is_admin:
        with open('/flag') as flag_file:
            flag_content = flag_file.read()

        if debug:
            debug_session = str(dict(session.items()))
        return render_template('admin_panel.html', flag=flag_content, debug_session=debug_session)
    else:
        if debug:
            debug_session = str(dict(session.items()))
        return render_template('dashboard.html', error_message='Only administrator users can open this section.', debug_session=debug_session)


@app.route('/dashboard')
def dashboard():
    debug_session = None
    debug = request.args.get('debug')
    if debug == 'session':
        debug = True

    # Check if user is authenticated
    if not session.get('authenticated'):
        return render_template('login.html', error='Please log in first.')

    if debug:
        debug_session = str(dict(session.items()))
    return render_template('dashboard.html', debug_session=debug_session)


@app.route('/wifi_settings', methods=['GET', 'POST'])
def wifi_settings():
    if not session.get('authenticated'):
        return render_template('login.html', error='Please log in first.')

    if request.method == 'GET':
        return render_template('wifi_settings.html')
    elif request.method == 'POST':
        return render_template('wifi_settings.html', error_message='Settings can not be changed, the WiFi chipset is still booting.')


@app.route('/totp/current')
def get_current_totp():
    """
    Debug endpoint to get current TOTP code.
    In a real scenario, an attacker would need to obtain this through phishing,
    social engineering, or if the target uses a predictable TOTP app.
    For CTF purposes, this simulates having obtained the admin's TOTP somehow.
    """
    current_code = generate_totp_code()
    return jsonify({
        'code': current_code,
        'valid_for': '30 seconds',
        'note': 'This simulates obtaining the admin TOTP code through social engineering or other means.'
    })
