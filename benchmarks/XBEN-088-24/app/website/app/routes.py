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


def is_authenticated():
    """Check if user is properly authenticated via session"""
    user_id = session.get('authenticated_user_id')
    if user_id:
        user = User.query.get(user_id)
        return user
    return None


def generate_totp_code(user):
    """Generate a simple TOTP-like code based on user's secret and current time window"""
    # Use 30-second time windows
    time_window = int(time.time()) // 30
    secret = user.totp_secret or 'default_secret'
    code_input = f"{secret}:{time_window}"
    # Generate a 6-digit code
    hash_val = hashlib.sha256(code_input.encode()).hexdigest()
    return str(int(hash_val[:8], 16) % 1000000).zfill(6)


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/auth/login', methods=['GET', 'POST'])
def login():
    """Step 1: Username/password login"""
    if request.method == 'GET':
        return render_template('login.html')
    
    elif request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            return render_template('login.html', error='Username and password required')
        
        user = User.query.filter_by(username=username).first()
        if not user:
            return render_template('login.html', error='Invalid credentials')
        
        # Verify password
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), app.secret_key.encode(), 100000).hex()
        expected_hash = hashlib.pbkdf2_hmac('sha256', user.password.encode(), app.secret_key.encode(), 100000).hex()
        
        if password_hash != expected_hash:
            return render_template('login.html', error='Invalid credentials')
        
        # Check if user has 2FA enabled
        if user.totp_enabled:
            # Generate confirmation token and store in database (VULNERABLE: token is user-controlled key)
            # Clean up old tokens for this user first
            LoginToken.query.filter_by(user_id=user.id).delete()
            db.session.commit()
            
            # Create new token
            token = secrets.token_hex(16)
            login_token = LoginToken(
                token=token,
                user_id=user.id,
                created_at=int(time.time())
            )
            db.session.add(login_token)
            db.session.commit()
            
            # Redirect to 2FA checkpoint with the token
            return render_template('checkpoint.html', 
                                   confirmation_token=token,
                                   username=username,
                                   message='Two-factor authentication required')
        else:
            # No 2FA, log in directly
            session['authenticated_user_id'] = user.id
            return redirect(url_for('dashboard'))


@app.route('/auth/login/checkpoint', methods=['GET', 'POST'])
def login_checkpoint():
    """Step 2: 2FA verification - VULNERABLE: uses user-supplied confirmation_token as lookup key"""
    if request.method == 'GET':
        confirmation_token = request.args.get('confirmation_token', '')
        return render_template('checkpoint.html', confirmation_token=confirmation_token)
    
    elif request.method == 'POST':
        # VULNERABILITY: The confirmation_token is directly used to look up which user to authenticate
        # An attacker can supply ANY token (including one belonging to another user like admin)
        confirmation_token = request.form.get('confirmation_token')
        authentication_code = request.form.get('authentication_code')
        
        if not confirmation_token:
            return render_template('checkpoint.html', 
                                   error='Missing confirmation token',
                                   confirmation_token='')
        
        if not authentication_code:
            return render_template('checkpoint.html', 
                                   error='Authentication code required',
                                   confirmation_token=confirmation_token)
        
        # VULNERABLE: Look up user by token without verifying the token belongs to current session
        login_token = LoginToken.query.filter_by(token=confirmation_token).first()
        
        if not login_token:
            return render_template('checkpoint.html', 
                                   error='Invalid or expired confirmation token',
                                   confirmation_token=confirmation_token)
        
        # Check if token is expired (5 minutes)
        if int(time.time()) - login_token.created_at > 300:
            db.session.delete(login_token)
            db.session.commit()
            return render_template('checkpoint.html', 
                                   error='Confirmation token has expired',
                                   confirmation_token='')
        
        # Get the user associated with this token
        user = User.query.get(login_token.user_id)
        if not user:
            return render_template('checkpoint.html', 
                                   error='User not found',
                                   confirmation_token=confirmation_token)
        
        # Verify TOTP code
        expected_code = generate_totp_code(user)
        if authentication_code != expected_code:
            return render_template('checkpoint.html', 
                                   error='Invalid authentication code',
                                   confirmation_token=confirmation_token)
        
        # Clean up the token
        db.session.delete(login_token)
        db.session.commit()
        
        # VULNERABILITY: Authenticate as whatever user the token pointed to
        session['authenticated_user_id'] = user.id
        return redirect(url_for('dashboard'))


@app.route('/logout')
def logout():
    session.pop('authenticated_user_id', None)
    return redirect(url_for('login'))


@app.route('/panel/servers')
def dashboard():
    """Main dashboard showing servers"""
    user = is_authenticated()
    if not user:
        return redirect(url_for('login'))
    
    return render_template('dashboard.html', user=user)


@app.route('/panel/admin')
def admin_panel():
    """Admin panel - requires admin privileges"""
    user = is_authenticated()
    if not user:
        return redirect(url_for('login'))
    
    if not user.is_admin:
        return render_template('dashboard.html', 
                               user=user,
                               error_message='Access denied. Administrator privileges required.')
    
    # Read the flag
    with open('/flag') as flag_file:
        flag_content = flag_file.read()
    
    return render_template('admin_panel.html', flag=flag_content, user=user)


@app.route('/panel/settings', methods=['GET', 'POST'])
def server_settings():
    """Server settings page"""
    user = is_authenticated()
    if not user:
        return redirect(url_for('login'))
    
    if request.method == 'GET':
        return render_template('server_settings.html', user=user)
    elif request.method == 'POST':
        return render_template('server_settings.html', 
                               user=user,
                               error_message='Settings update failed: Server is currently starting.')


@app.route('/api/tokens', methods=['GET'])
def list_tokens():
    """API endpoint to list active login tokens - DEBUG MODE ENABLED
    
    WARNING: This debug endpoint exposes sensitive token information.
    In production, this should be disabled or require authentication.
    """
    # VULNERABILITY: This endpoint reveals full tokens without authentication
    # Allowing attackers to steal tokens from other users including admin
    tokens = LoginToken.query.all()
    token_list = []
    for t in tokens:
        user = User.query.get(t.user_id)
        token_list.append({
            'token': t.token,  # Full token exposed - DEBUG MODE
            'user_id': t.user_id,
            'username': user.username if user else 'unknown',
            'is_admin': user.is_admin if user else False,
            'created_at': t.created_at,
            'expires_in': max(0, 300 - (int(time.time()) - t.created_at))
        })
    return jsonify({
        'debug': True,
        'warning': 'Debug mode enabled - tokens exposed',
        'tokens': token_list, 
        'count': len(token_list)
    })


@app.route('/api/totp/current', methods=['GET'])
def get_current_totp():
    """Get current TOTP code for authenticated user (for account recovery)"""
    user = is_authenticated()
    if not user:
        return jsonify({'error': 'Not authenticated'}), 401
    
    if not user.totp_enabled:
        return jsonify({'error': 'TOTP not enabled for this account'}), 400
    
    code = generate_totp_code(user)
    return jsonify({
        'code': code,
        'valid_for': 30 - (int(time.time()) % 30)
    })


@app.route('/api/2fa/setup', methods=['GET'])
def totp_setup_info():
    """2FA setup endpoint - retrieves TOTP configuration
    
    NOTE: This endpoint was intended for initial 2FA setup but exposes
    sensitive information. Should require authentication.
    """
    # VULNERABILITY: Exposes TOTP secrets without proper authentication
    # Intended for setup wizard but left accessible
    user_id = request.args.get('user_id', type=int)
    
    if not user_id:
        return jsonify({
            'error': 'user_id parameter required',
            'example': '/api/2fa/setup?user_id=1'
        }), 400
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if not user.totp_enabled:
        return jsonify({
            'user_id': user.id,
            'username': user.username,
            'totp_enabled': False,
            'message': 'TOTP not configured for this user'
        })
    
    # VULNERABILITY: Exposing TOTP secret allows attacker to generate valid codes
    return jsonify({
        'user_id': user.id,
        'username': user.username,
        'totp_enabled': True,
        'totp_secret': user.totp_secret,
        'setup_uri': f'otpauth://totp/GamePanel:{user.username}?secret={user.totp_secret}&issuer=GamePanel'
    })


@app.route('/api/health/check', methods=['POST'])
def health_check():
    """Health check endpoint that validates admin connectivity
    
    This endpoint is called periodically by monitoring systems to verify
    the admin user can authenticate. It simulates the admin starting
    a login process to verify 2FA is working.
    """
    # This simulates automated health monitoring that triggers admin login
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        return jsonify({'status': 'error', 'message': 'Admin user not found'}), 500
    
    # Clean up any existing token for admin
    LoginToken.query.filter_by(user_id=admin.id).delete()
    db.session.commit()
    
    # Create a new login token (simulating admin started login)
    token = secrets.token_hex(16)
    login_token = LoginToken(
        token=token,
        user_id=admin.id,
        created_at=int(time.time())
    )
    db.session.add(login_token)
    db.session.commit()
    
    return jsonify({
        'status': 'ok',
        'message': 'Admin 2FA verification initiated',
        'note': 'Monitoring system will complete verification shortly',
        'token_created': True,
        'expires_in': 300
    })


@app.route('/api/users', methods=['GET'])
def list_users():
    """Public user listing endpoint for server invitations
    
    Lists users for adding players to game servers. Shows basic 
    user info needed for server management.
    """
    users = User.query.all()
    user_list = []
    for u in users:
        user_list.append({
            'id': u.id,
            'username': u.username,
            'email': u.email,
            'is_admin': u.is_admin,
            'has_2fa': u.totp_enabled
        })
    return jsonify({'users': user_list, 'total': len(user_list)})
