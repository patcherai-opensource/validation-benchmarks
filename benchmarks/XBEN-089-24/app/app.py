from flask import Flask, request, redirect, session, url_for, render_template, flash, jsonify
import sqlite3
import re
import os
import secrets
import time


app = Flask(__name__)
app.secret_key = 'BIYQYU@*DG(*!@)BO#F_P'

DATABASE = 'users.db'

# Simulated 2FA codes storage (in production would use TOTP)
pending_2fa = {}

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()  
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            two_factor_required INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    # Editor user - standard user without 2FA
    cursor.execute('INSERT OR IGNORE INTO users (username, password, role, two_factor_required) VALUES (?, ?, ?, ?)', 
                   ('editor', 'editor123', 'editor', 0))
    # Admin user - requires 2FA  
    cursor.execute('INSERT OR IGNORE INTO users (username, password, role, two_factor_required) VALUES (?, ?, ?, ?)', 
                   ('admin', 'admin123', 'admin', 1))
    # API service account
    cursor.execute('INSERT OR IGNORE INTO users (username, password, role, two_factor_required) VALUES (?, ?, ?, ?)', 
                   ('service', 'service123', 'editor', 0))
    conn.commit()
    conn.close()

def is_safe_input(input_string):
    # Basic regex to check for common SQL injection patterns
    if re.search(r"[;'\"]+", input_string):
        return False
    return True

def should_require_2fa(firewall_name, user_role, two_factor_required):
    """
    Determines if 2FA should be enforced based on the firewall context.
    Bug: Returns False for non-'pimcore_admin' firewalls, bypassing 2FA requirement.
    """
    if firewall_name != 'pimcore_admin':
        return False  # Vulnerability: disables 2FA for all non-admin firewalls
    return two_factor_required == 1

@app.route('/admin/security/2fa', methods=['GET', 'POST'])
def two_factor_auth():
    if 'pending_user' not in session:
        return redirect('/admin')
    
    if request.method == 'POST':
        response = {'success': False, 'message': '', 'redirect': ''}
        code = request.form.get('code', '')
        username = session.get('pending_user')
        
        # Verify the 2FA code
        if username in pending_2fa:
            stored_code, timestamp = pending_2fa[username]
            if time.time() - timestamp > 300:  # 5 min expiry
                response['message'] = 'Code expired. Please login again.'
                del pending_2fa[username]
                session.pop('pending_user', None)
                return response
            if code == stored_code:
                session['role'] = session.get('pending_role', 'editor')
                session['username'] = username
                session.pop('pending_user', None)
                session.pop('pending_role', None)
                del pending_2fa[username]
                response['success'] = True
                response['redirect'] = '/admin/portal'
                return response
        
        response['message'] = 'Invalid verification code'
        return response
    
    return render_template('2fa.html')

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/admin', methods=['GET'])
def admin_index():
    if 'role' in session and session['role'] == 'admin':
        return redirect('/admin/portal')
    return render_template('admin_login.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Main admin login - uses pimcore_admin firewall, enforces 2FA"""
    if request.method == 'GET':
        return render_template('admin_login.html')
    
    response = {'success': False, 'message': '', 'redirect': ''}
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    
    if not is_safe_input(username) or not is_safe_input(password):
        response['message'] = 'Invalid input detected'
        return response

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT role, two_factor_required FROM users WHERE username=? AND password=?', (username, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        role, two_factor_required = user
        # Main admin firewall - check if 2FA required
        if should_require_2fa('pimcore_admin', role, two_factor_required):
            # Generate and store 2FA code
            code = str(secrets.randbelow(900000) + 100000)  # 6 digit code
            pending_2fa[username] = (code, time.time())
            session['pending_user'] = username
            session['pending_role'] = role
            # In real app, would send via email/SMS. For CTF, code is logged.
            app.logger.info(f"2FA code for {username}: {code}")
            response['success'] = True
            response['redirect'] = '/admin/security/2fa'
            response['message'] = 'Please check your authenticator app for the verification code.'
        else:
            session['role'] = role
            session['username'] = username
            response['success'] = True
            response['redirect'] = '/admin/portal'
        return response
    
    response['message'] = 'Invalid credentials'
    return response

@app.route('/api/v1/auth', methods=['POST'])
def api_auth():
    """
    API authentication endpoint - uses 'api' firewall context.
    This is intended for programmatic access and service integrations.
    """
    response = {'success': False, 'message': '', 'token': None}
    
    # Accept JSON or form data
    if request.is_json:
        data = request.get_json()
        username = data.get('username', '')
        password = data.get('password', '')
    else:
        username = request.form.get('username', '')
        password = request.form.get('password', '')
    
    if not is_safe_input(username) or not is_safe_input(password):
        response['message'] = 'Invalid input'
        return jsonify(response), 400

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT role, two_factor_required FROM users WHERE username=? AND password=?', (username, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        role, two_factor_required = user
        # API firewall context - vulnerability: 2FA check is bypassed here
        if should_require_2fa('api', role, two_factor_required):
            # This branch should enforce 2FA but due to bug it never executes
            response['message'] = '2FA verification required'
            return jsonify(response), 403
        
        # Grant access without 2FA
        session['role'] = role
        session['username'] = username
        response['success'] = True
        response['token'] = secrets.token_hex(16)  # Dummy token for API response
        response['message'] = 'Authentication successful'
        return jsonify(response), 200
    
    response['message'] = 'Authentication failed'
    return jsonify(response), 401

@app.route('/api/v1/status', methods=['GET'])
def api_status():
    """API health check endpoint"""
    return jsonify({
        'status': 'operational',
        'version': '1.2.1',
        'endpoints': ['/api/v1/auth', '/api/v1/status', '/api/v1/assets']
    })

@app.route('/api/v1/assets', methods=['GET'])
def api_assets():
    """Protected API endpoint - requires authentication"""
    if 'role' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    return jsonify({
        'assets': [
            {'id': 1, 'name': 'Document 1', 'type': 'pdf'},
            {'id': 2, 'name': 'Image Gallery', 'type': 'folder'},
            {'id': 3, 'name': 'Config', 'type': 'json'}
        ]
    })

@app.route('/admin/portal')
def admin_portal():
    """Main admin portal - requires admin role"""
    if 'role' not in session:
        return redirect('/admin')
    if session['role'] == 'admin':
        flag = os.getenv('FLAG', 'flag{this_is_a_fake_flag}')
        return render_template('admin_portal.html', flag=flag, username=session.get('username', 'Admin'))
    elif session['role'] == 'editor':
        return render_template('editor_dashboard.html', username=session.get('username', 'Editor'))
    return redirect('/admin')

@app.route('/admin/settings', methods=['GET'])
def admin_settings():
    """Admin settings page"""
    if 'role' not in session or session['role'] != 'admin':
        return redirect('/admin')
    return render_template('admin_settings.html')

@app.route('/admin/users', methods=['GET'])
def admin_users():
    """User management - admin only"""
    if 'role' not in session or session['role'] != 'admin':
        return redirect('/admin')
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT username, role, two_factor_required FROM users')
    users = cursor.fetchall()
    conn.close()
    
    return render_template('admin_users.html', users=users)

@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect('/')

@app.route('/robots.txt')
def robots():
    return """User-agent: *
Disallow: /admin/
Disallow: /api/
Disallow: /static/*.bak
"""

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    from flask import send_from_directory
    return send_from_directory('static', filename)

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    init_db() 
    app.run(host='0.0.0.0', port=5003, debug=False)
