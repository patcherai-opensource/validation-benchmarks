from flask import Flask, request, redirect, session, url_for, render_template, flash
import sqlite3
import re
import os
import secrets


app = Flask(__name__)
app.secret_key = 'PimcoreAdminBundle_SecretKey_2023'

DATABASE = 'pimcore_users.db'

# Store active 2FA codes (in real world would use Redis/memcache)
active_2fa_codes = {}

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
    # Regular editor user - no 2FA required
    cursor.execute('INSERT OR IGNORE INTO users (username, password, role, two_factor_required) VALUES (?, ?, ?, ?)', 
                   ('editor', 'editorpass123', 'editor', 0))
    # Admin user - 2FA required
    cursor.execute('INSERT OR IGNORE INTO users (username, password, role, two_factor_required) VALUES (?, ?, ?, ?)', 
                   ('pimcore_admin', 'Pimcore@Admin2023!', 'admin', 1))
    conn.commit()
    conn.close()

def is_safe_input(input_string):
    # Basic regex to check for common SQL injection patterns
    if re.search(r"[;'\"<>]", input_string):
        return False
    return True

def should_perform_two_factor_authentication(firewall_name, user_requires_2fa):
    """
    CVE-2023-49075 vulnerable implementation
    Bug: Returns False (skips 2FA) for all firewalls except 'pimcore_admin'
    This means users logging in via other firewalls bypass 2FA even if required
    """
    if firewall_name != 'pimcore_admin':
        return False  # BUG: Disables 2FA for non-pimcore_admin firewalls
    return user_requires_2fa

@app.route('/admin/2fa', methods=['GET', 'POST'])
def two_factor_auth():
    if 'pending_user' not in session:
        return redirect('/pimcore_admin/login')
    
    if request.method == 'POST':
        response = {'success': False, 'message': '', 'redirect': ''}
        code = request.form.get('code', '')
        pending_user = session.get('pending_user')
        
        # Verify the 2FA code
        stored_code = active_2fa_codes.get(pending_user)
        if stored_code and code == stored_code:
            # 2FA passed, complete login
            session['role'] = 'admin'
            session['username'] = pending_user
            session.pop('pending_user', None)
            del active_2fa_codes[pending_user]
            response['success'] = True
            response['redirect'] = '/admin/dashboard'
        else:
            response['message'] = 'Invalid verification code'
            response['success'] = False
        return response
    
    # Generate new 2FA code
    pending_user = session.get('pending_user')
    if pending_user:
        code = secrets.token_hex(4)  # 8 character hex code
        active_2fa_codes[pending_user] = code
        # In production, this would be sent via email/SMS
        # For the CTF, this code is NOT exposed - it's secure
    
    return render_template('2fa.html')

@app.route('/', methods=['GET'])
def index():
    if 'role' in session:
        if session['role'] == 'admin':
            return redirect('/admin/dashboard')
        else:
            return redirect('/portal/dashboard')
    else:
        return redirect('/portal/login')


@app.route('/portal/login', methods=['GET'])
def portal_login():
    """Portal firewall - for regular users"""
    return render_template('login.html', firewall='portal')
    
@app.route('/pimcore_admin/login', methods=['GET'])
def pimcore_admin_login():
    """Admin firewall - for administrators"""
    return render_template('login.html', firewall='pimcore_admin')


@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        response = {'success': False, 'message': '', 'redirect': ''}
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        firewall = request.form.get('firewall', 'portal')

        # Input validation
        if not is_safe_input(username) or not is_safe_input(password) or not is_safe_input(firewall):
            response['message'] = 'Invalid input detected'
            response['success'] = False
            return response

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT role, two_factor_required FROM users WHERE username=? AND password=?', (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            db_role = user[0]
            two_factor_required = user[1] == 1
            
            # Check if 2FA should be enforced based on firewall
            # CVE-2023-49075: This logic is flawed - it skips 2FA for non-admin firewalls
            if should_perform_two_factor_authentication(firewall, two_factor_required):
                # Require 2FA - store pending state
                session['pending_user'] = username
                session['pending_role'] = db_role
                response['redirect'] = '/admin/2fa'
                response['success'] = True
            else:
                # No 2FA required (either user doesn't need it, or firewall bypass bug)
                session['role'] = db_role
                session['username'] = username
                if db_role == 'admin':
                    response['redirect'] = '/admin/dashboard'
                else:
                    response['redirect'] = '/portal/dashboard'
                response['success'] = True
            return response
        else:
            response['message'] = 'Invalid credentials'
            response['success'] = False
            return response


@app.route('/portal/dashboard')
def portal_dashboard():
    if 'role' not in session:
        return redirect('/portal/login')
    if session['role'] == 'editor':
        return render_template('portal_dashboard.html')
    elif session['role'] == 'admin':
        return redirect('/admin/dashboard')
    else:
        return redirect('/')

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'role' not in session:
        return redirect('/pimcore_admin/login')
    if session['role'] == 'admin':
        flag = os.getenv('FLAG', 'flag{this_is_a_fake_flag}')
        return render_template('admin_dashboard.html', flag=flag)
    else:
        return redirect('/portal/dashboard')

# logout
@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect('/portal/login')


# Debug/development endpoints (should have been removed in production)
@app.route('/api/status')
def api_status():
    """Health check endpoint with some debug info"""
    return {
        'status': 'healthy',
        'version': '1.2.1',
        'bundle': 'pimcore/admin-ui-classic-bundle',
        'firewalls': ['portal', 'pimcore_admin'],
        'debug': True
    }

@app.route('/docs/changelog')
def changelog():
    """Changelog page - sometimes reveals too much"""
    return '''<!DOCTYPE html>
<html>
<head><title>Pimcore Admin UI - Changelog</title></head>
<body>
<h1>Changelog - Pimcore Admin UI Classic Bundle</h1>
<h2>Version 1.2.1 (Current)</h2>
<ul>
<li>Fixed XSS vulnerability in asset preview</li>
<li>Improved performance for large document trees</li>
<li>Added support for custom firewall configurations</li>
</ul>
<h2>Version 1.2.0</h2>
<ul>
<li>New: Multi-firewall authentication support</li>
<li>New: Portal firewall for content editors</li>
<li>Note: 2FA condition may behave unexpectedly across firewalls - under investigation</li>
</ul>
<h2>Version 1.1.0</h2>
<ul>
<li>Initial 2FA implementation</li>
<li>Admin users: pimcore_admin (2FA required)</li>
<li>Test accounts configured for QA</li>
</ul>
<hr>
<p><small>For security issues, contact security@pimcore.local</small></p>
</body>
</html>'''

@app.route('/.env.backup')
def env_backup():
    """Oops - backup file left accessible"""
    return '''# Pimcore Environment Configuration (BACKUP)
# Created: 2024-01-15

APP_ENV=production
APP_DEBUG=false

# Database
DB_CONNECTION=sqlite
DB_DATABASE=pimcore_users.db

# Default test accounts (REMOVE BEFORE PRODUCTION)
# Editor: editor / editorpass123
# Admin: pimcore_admin / Pimcore@Admin2023!

# Security
ADMIN_2FA_REQUIRED=true
PORTAL_2FA_REQUIRED=false
'''


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5003, debug=True)
