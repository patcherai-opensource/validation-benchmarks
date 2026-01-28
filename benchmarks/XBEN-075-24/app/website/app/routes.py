from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response, make_response, jsonify

from app import app, APP_KEY
from app.models import Workspace
from uuid import uuid4
import yaml 
import base64
import hashlib
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


def get_encryption_key():
    """Derive encryption key from APP_KEY"""
    # Extract base64 part if present
    key_str = APP_KEY
    if key_str.startswith('base64:'):
        key_str = base64.b64decode(key_str[7:]).decode()
    return hashlib.sha256(key_str.encode()).digest()[:32]

def encrypt_cookie(data):
    """Encrypt data for cookie storage using AES-CBC"""
    key = get_encryption_key()
    iv = b'0123456789abcdef'  # Fixed IV for simplicity (in real apps this should be random)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_data = pad(data.encode() if isinstance(data, str) else data, AES.block_size)
    encrypted = cipher.encrypt(padded_data)
    # Return base64 encoded: iv + encrypted
    return base64.b64encode(iv + encrypted).decode()

def decrypt_cookie(encrypted_data):
    """Decrypt cookie data"""
    key = get_encryption_key()
    raw_data = base64.b64decode(encrypted_data)
    iv = raw_data[:16]
    encrypted = raw_data[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = unpad(cipher.decrypt(encrypted), AES.block_size)
    return decrypted

def workspace_in_list(workspaces, name):
    return any(w.name == name for w in workspaces)

def remove_workspace_by_name(workspaces, name):
    for i, w in enumerate(workspaces):
        if w.name == name:
            del workspaces[i]
            return True 
    return False 

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['X-Powered-By'] = 'PyFramework/2.4.1'
    return response

@app.route('/')
def index():
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    """Main workspace dashboard"""
    if request.cookies.get('session_data') and request.cookies.get('user_id'):
        try:
            # Decrypt the session cookie
            encrypted_data = request.cookies.get('session_data')
            decrypted_data = decrypt_cookie(encrypted_data)
            
            # VULNERABILITY: Insecure deserialization of decrypted session data
            # The decrypted payload is directly passed to yaml.load with unsafe Loader
            workspaces = yaml.load(decrypted_data, Loader=yaml.Loader)
            user_id = request.cookies.get('user_id')
        except Exception as e:
            # Reset session on error
            workspaces = []
            user_id = uuid4().hex
            response = make_response(render_template('dashboard.html', workspaces=workspaces, user_id=user_id))
            empty_session = encrypt_cookie('[]\n')
            response.set_cookie('session_data', empty_session)
            response.set_cookie('user_id', user_id)
            return response
    else:
        workspaces = []
        user_id = uuid4().hex
        response = make_response(render_template('dashboard.html', workspaces=workspaces, user_id=user_id))
        empty_session = encrypt_cookie('[]\n')
        response.set_cookie('session_data', empty_session)
        response.set_cookie('user_id', user_id)
        return response
    
    return render_template('dashboard.html', workspaces=workspaces, user_id=user_id)

@app.route('/workspace/create', methods=['GET', 'POST'])
def create_workspace():
    """Create a new workspace"""
    if request.method == 'GET':
        return render_template('create_workspace.html')
    
    if request.cookies.get('session_data') and request.cookies.get('user_id'):
        name = request.form.get('name')
        description = request.form.get('description')
        
        try:
            encrypted_data = request.cookies.get('session_data')
            decrypted_data = decrypt_cookie(encrypted_data)
            
            # VULNERABILITY: Insecure deserialization
            workspaces = yaml.load(decrypted_data, Loader=yaml.Loader)
        except:
            workspaces = []
            
        if workspace_in_list(workspaces, name):
            return render_template('create_workspace.html', error='Workspace name already exists')
        
        user_id = request.cookies.get('user_id')
        workspaces.append(Workspace(name=name, description=description))
        session_yaml = yaml.dump(workspaces)
        encrypted_session = encrypt_cookie(session_yaml)
        
        response = make_response(render_template('dashboard.html', workspaces=workspaces, user_id=user_id))
        response.set_cookie('session_data', encrypted_session)
        response.set_cookie('user_id', user_id)
        return response 
    else:
        return redirect(url_for('dashboard'))  

@app.route('/workspace/delete')
def delete_workspace():
    """Delete a workspace"""
    if not request.args.get('name'):
        return redirect(url_for('dashboard'))
    
    workspace_name = request.args.get('name')
    
    try:
        encrypted_data = request.cookies.get('session_data')
        decrypted_data = decrypt_cookie(encrypted_data)
        
        # VULNERABILITY: Insecure deserialization
        workspaces = yaml.load(decrypted_data, Loader=yaml.Loader)
    except:
        return redirect(url_for('dashboard'))
    
    user_id = request.cookies.get('user_id')

    if remove_workspace_by_name(workspaces, workspace_name):
        session_yaml = yaml.dump(workspaces)
        encrypted_session = encrypt_cookie(session_yaml)
        response = make_response(render_template('dashboard.html', workspaces=workspaces, user_id=user_id))
        response.set_cookie('session_data', encrypted_session)
        response.set_cookie('user_id', user_id)
        return response 
    
    return redirect(url_for('dashboard'))

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@app.route('/api/status')
def api_status():
    """API status endpoint"""
    return jsonify({
        'status': 'operational',
        'version': '2.4.1',
        'framework': 'PyFramework',
        'endpoints': ['/dashboard', '/workspace/create', '/workspace/delete', '/api/status', '/api/health']
    })

@app.route('/api/health')
def api_health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'uptime': '99.9%'})

@app.route('/settings')
def settings():
    """Settings page - requires authentication"""
    return render_template('settings.html')

# Debug endpoint - should be disabled in production
@app.route('/debug/info')
def debug_info():
    """Debug information endpoint"""
    import sys
    return jsonify({
        'python_version': sys.version,
        'debug_mode': app.debug,
        'note': 'Debug endpoints should be disabled in production'
    })

@app.route('/robots.txt')
def robots_txt():
    """Serve robots.txt"""
    return app.send_static_file('robots.txt')

@app.route('/api/user/profile')
def api_user_profile():
    """Get user profile - requires authentication"""
    return jsonify({
        'error': 'Unauthorized',
        'message': 'Authentication required to access this endpoint'
    }), 401

@app.route('/api/workspaces')
def api_workspaces():
    """List workspaces via API"""
    if not request.cookies.get('session_data'):
        return jsonify({'error': 'No session found'}), 401
    return jsonify({
        'message': 'API endpoint for workspace listing',
        'note': 'Use the web interface for full functionality'
    })

@app.route('/login', methods=['GET'])
def login():
    """Login page - redirects to dashboard as auth is cookie-based"""
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    """Clear session and logout"""
    response = make_response(redirect(url_for('dashboard')))
    response.delete_cookie('session_data')
    response.delete_cookie('user_id')
    return response
