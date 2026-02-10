from flask import Flask, render_template, redirect, url_for, request, session, jsonify, send_from_directory

from app import app
from app.db import db
from app.models import User, TwoFactorToken

import hashlib
import time
import secrets
import pyotp
import os


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error_code=500, error_message='Internal Server Error'), 500


@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error_code=404, error_message='Page Not Found'), 404


def verify_session():
    """Check if user is logged in and 2FA completed"""
    if not session.get('authenticated'):
        return None
    user_id = session.get('user_id')
    if user_id:
        return User.query.get(user_id)
    return None


@app.route('/backup/<path:filename>')
def backup_files(filename):
    """Serve backup configuration files"""
    backup_dir = os.path.join(app.root_path, 'backup')
    return send_from_directory(backup_dir, filename)


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    
    user = User.query.filter_by(username=username).first()
    
    if not user:
        return render_template('login.html', error='Invalid credentials')
    
    password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), app.secret_key.encode(), 100000).hex()
    expected_hash = hashlib.pbkdf2_hmac('sha256', user.password.encode(), app.secret_key.encode(), 100000).hex()
    
    if password_hash != expected_hash:
        return render_template('login.html', error='Invalid credentials')
    
    if user.totp_enabled:
        confirmation_token = secrets.token_hex(16)
        
        TwoFactorToken.cleanup_expired()
        
        token_record = TwoFactorToken(
            token=confirmation_token,
            user_id=user.id,
            expires_at=int(time.time()) + 300
        )
        db.session.add(token_record)
        db.session.commit()
        
        return render_template('checkpoint.html', confirmation_token=confirmation_token)
    else:
        session['user_id'] = user.id
        session['authenticated'] = True
        return redirect(url_for('dashboard'))


@app.route('/auth/login/checkpoint', methods=['POST'])
def login_checkpoint():
    """Second step of 2FA login - verify TOTP code"""
    confirmation_token = request.form.get('confirmation_token', '')
    authentication_code = request.form.get('authentication_code', '')
    
    if not confirmation_token or not authentication_code:
        return render_template('checkpoint.html', 
                             confirmation_token=confirmation_token,
                             error='Missing required fields')
    
    token_record = TwoFactorToken.query.filter_by(token=confirmation_token).first()
    
    if not token_record:
        return render_template('login.html', error='Invalid or expired token. Please login again.')
    
    if token_record.expires_at < int(time.time()):
        db.session.delete(token_record)
        db.session.commit()
        return render_template('login.html', error='Token expired. Please login again.')
    
    user = User.query.get(token_record.user_id)
    
    if not user:
        return render_template('login.html', error='User not found')
    
    totp = pyotp.TOTP(user.totp_secret)
    if not totp.verify(authentication_code, valid_window=1):
        return render_template('checkpoint.html',
                             confirmation_token=confirmation_token,
                             error='Invalid authentication code')
    
    db.session.delete(token_record)
    db.session.commit()
    
    session['user_id'] = user.id
    session['authenticated'] = True
    
    return redirect(url_for('dashboard'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/admin_panel')
def admin_panel():
    user = verify_session()
    if not user:
        return redirect(url_for('login'))
    
    if not user.is_admin:
        return render_template('dashboard.html', error_message='Only administrator users can open this section.')
    
    with open('/flag') as flag_file:
        flag_content = flag_file.read()
    
    return render_template('admin_panel.html', flag=flag_content)


@app.route('/dashboard')
def dashboard():
    user = verify_session()
    if not user:
        return redirect(url_for('login'))
    
    return render_template('dashboard.html', username=user.username)


@app.route('/wifi_settings', methods=['GET', 'POST'])
def wifi_settings():
    user = verify_session()
    if not user:
        return redirect(url_for('login'))
    
    if request.method == 'GET':
        return render_template('wifi_settings.html')
    else:
        return render_template('wifi_settings.html', error_message='Settings can not be changed, the WiFi chipset is still booting.')


@app.route('/api/health/session-check', methods=['POST'])
def api_session_check():
    """
    Internal API endpoint for automated session management.
    Used by monitoring systems to verify admin session capability.
    Creates a pending 2FA token for the admin account for verification.
    """
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        return jsonify({'status': 'error', 'message': 'Admin account not found'}), 500
    
    TwoFactorToken.cleanup_expired()
    
    existing_token = TwoFactorToken.query.filter_by(user_id=admin.id).first()
    if existing_token and existing_token.expires_at > int(time.time()):
        return jsonify({
            'status': 'ok',
            'message': 'Session verification pending',
            'pending_verification': True,
            'token_id': existing_token.id
        })
    
    if existing_token:
        db.session.delete(existing_token)
        db.session.commit()
    
    confirmation_token = secrets.token_hex(16)
    token_record = TwoFactorToken(
        token=confirmation_token,
        user_id=admin.id,
        expires_at=int(time.time()) + 300
    )
    db.session.add(token_record)
    db.session.commit()
    
    return jsonify({
        'status': 'ok',
        'message': 'Session verification initiated',
        'pending_verification': True,
        'token_id': token_record.id
    })


@app.route('/api/auth/pending', methods=['GET'])
def api_auth_pending():
    """
    API endpoint to check pending authentication requests.
    Returns information about tokens awaiting 2FA verification.
    """
    TwoFactorToken.cleanup_expired()
    
    pending_tokens = TwoFactorToken.query.filter(
        TwoFactorToken.expires_at > int(time.time())
    ).all()
    
    result = []
    for token in pending_tokens:
        user = User.query.get(token.user_id)
        result.append({
            'token_id': token.id,
            'username': user.username if user else 'unknown',
            'confirmation_token': token.token,
            'expires_in': token.expires_at - int(time.time())
        })
    
    return jsonify({
        'status': 'ok',
        'pending_authentications': result
    })
