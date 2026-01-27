from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response, make_response, jsonify

from app import app
from app.models import SessionData
from uuid import uuid4
import pickle 
import base64
import hashlib
import hmac
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import json
import os


# Encryption utilities similar to Laravel's cookie encryption
def get_encryption_key():
    """Get the raw encryption key from APP_KEY"""
    app_key = app.config['APP_KEY']
    if app_key.startswith('base64:'):
        return base64.b64decode(app_key[7:])
    return app_key.encode()

def encrypt_cookie(data):
    """Encrypt data using AES-256-CBC with HMAC similar to Laravel"""
    key = get_encryption_key()
    iv = os.urandom(16)
    cipher = AES.new(key[:32].ljust(32, b'\x00'), AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(pad(data, AES.block_size))
    
    payload = {
        'iv': base64.b64encode(iv).decode('utf-8'),
        'value': base64.b64encode(encrypted).decode('utf-8'),
        'mac': hmac.new(key[:32].ljust(32, b'\x00'), iv + encrypted, hashlib.sha256).hexdigest()
    }
    return base64.b64encode(json.dumps(payload).encode()).decode('utf-8')

def decrypt_cookie(encrypted_data):
    """Decrypt data encrypted with encrypt_cookie - VULNERABLE: unserializes data!"""
    key = get_encryption_key()
    try:
        payload = json.loads(base64.b64decode(encrypted_data))
        iv = base64.b64decode(payload['iv'])
        value = base64.b64decode(payload['value'])
        
        # Verify MAC
        expected_mac = hmac.new(key[:32].ljust(32, b'\x00'), iv + value, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(payload['mac'], expected_mac):
            return None
            
        cipher = AES.new(key[:32].ljust(32, b'\x00'), AES.MODE_CBC, iv)
        decrypted = unpad(cipher.decrypt(value), AES.block_size)
        
        # VULNERABILITY: Deserializing decrypted data without validation
        # This is similar to Laravel's CVE where unserialize was called on decrypted cookie data
        return pickle.loads(decrypted)
    except Exception as e:
        return None


def session_exists(sessions, session_id):
    return any(s.session_id == session_id for s in sessions)

def remove_session(sessions, session_id):
    for i, s in enumerate(sessions):
        if s.session_id == session_id:
            del sessions[i]
            return True 
    return False 

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['X-Powered-By'] = 'PHP/7.2.10'
    response.headers['X-Framework'] = 'Laravel'
    return response

@app.route('/')
def index():
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    """Main dashboard showing active sessions"""
    if request.cookies.get('laravel_session') and request.cookies.get('user_id'):
        # Decrypt and deserialize the session cookie
        # VULNERABLE: This calls pickle.loads on decrypted data
        sessions = decrypt_cookie(request.cookies.get('laravel_session'))
        if sessions is None:
            sessions = []
        user_id = request.cookies.get('user_id')
    else:
        sessions = []
        user_id = uuid4().hex
        empty_sessions = pickle.dumps([])
        encrypted = encrypt_cookie(empty_sessions)
        response = make_response(render_template('dashboard.html', sessions=sessions, user_id=user_id))
        response.set_cookie('laravel_session', encrypted)
        response.set_cookie('user_id', user_id)
        response.set_cookie('XSRF-TOKEN', uuid4().hex)
        return response
    
    return render_template('dashboard.html', sessions=sessions, user_id=user_id)

@app.route('/sessions/create', methods=['GET', 'POST'])
def create_session():
    """Create a new session entry"""
    if request.method == 'GET':
        return render_template('create_session.html')
    
    if request.cookies.get('laravel_session') and request.cookies.get('user_id'):
        session_name = request.form.get('session_name')
        ip_address = request.form.get('ip_address')
        
        # Decrypt and deserialize - VULNERABLE
        sessions = decrypt_cookie(request.cookies.get('laravel_session'))
        if sessions is None:
            sessions = []
            
        session_id = uuid4().hex[:8]
        if session_exists(sessions, session_id):
            return render_template('create_session.html', error='Session ID collision, please try again')
        
        user_id = request.cookies.get('user_id')
        sessions.append(SessionData(session_id=session_id, session_name=session_name, ip_address=ip_address))
        
        encrypted = encrypt_cookie(pickle.dumps(sessions))
        response = make_response(render_template('dashboard.html', sessions=sessions, user_id=user_id))
        response.set_cookie('laravel_session', encrypted)
        response.set_cookie('user_id', user_id)
        return response 
    else:
        return redirect(url_for('dashboard'))  

@app.route('/sessions/revoke')
def revoke_session():
    """Revoke/delete a session"""
    if not request.args.get('id'):
        return redirect(url_for('dashboard'))
    
    session_id = request.args.get('id')
    
    # Decrypt and deserialize - VULNERABLE  
    sessions = decrypt_cookie(request.cookies.get('laravel_session'))
    if sessions is None:
        return redirect(url_for('dashboard'))
        
    user_id = request.cookies.get('user_id')
    
    if remove_session(sessions, session_id):
        encrypted = encrypt_cookie(pickle.dumps(sessions))
        response = make_response(render_template('dashboard.html', sessions=sessions, user_id=user_id))
        response.set_cookie('laravel_session', encrypted)
        response.set_cookie('user_id', user_id)
        return response 
    
    return redirect(url_for('dashboard'))


@app.route('/api/config')
def api_config():
    """API endpoint exposing application configuration - DEBUG MODE"""
    # In production this should be disabled!
    config_data = {
        'app_name': 'Laravel Session Manager',
        'app_env': 'local',
        'app_debug': True,
        'app_url': request.host_url,
        'db_connection': 'mysql',
        'cache_driver': 'file',
        'session_driver': 'cookie',
        'session_lifetime': 120,
        # DEBUG: Exposing APP_KEY for development - REMOVE IN PRODUCTION!
        'app_key': app.config['APP_KEY']
    }
    return jsonify(config_data)


@app.route('/about')
def about():
    """About page"""
    if request.method == 'GET':
        return render_template('about.html')
