from flask import Flask, request, redirect, session, url_for, render_template, flash, jsonify
import sqlite3
import re
import os
import secrets
import time


app = Flask(__name__)
app.secret_key = 'SecurePortal_MFA_K3y_2024!'

DATABASE = 'portal.db'

# MFA codes storage (in-memory for demo)
pending_mfa = {}

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()  
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS portal_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            mfa_enabled INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL,
            user TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    # Regular staff user - MFA not enforced
    cursor.execute('INSERT OR IGNORE INTO portal_users (username, password, role, mfa_enabled) VALUES (?, ?, ?, ?)', 
                   ('staffuser', 'staff2024', 'staff', 0))
    # Admin user - MFA enforced
    cursor.execute('INSERT OR IGNORE INTO portal_users (username, password, role, mfa_enabled) VALUES (?, ?, ?, ?)', 
                   ('sysadmin', 'Adm1n@SecP0rtal!', 'admin', 1))
    conn.commit()
    conn.close()

def log_action(action, user=None):
    """Log security audit events"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO audit_log (action, user) VALUES (?, ?)', (action, user))
        conn.commit()
        conn.close()
    except:
        pass

def validate_input(input_string):
    """Input validation for security"""
    if not input_string or len(input_string) > 100:
        return False
    if re.search(r"[;'\"<>]", input_string):
        return False
    return True

def generate_mfa_code():
    """Generate a 6-digit MFA code"""
    return str(secrets.randbelow(900000) + 100000)

# ==================== PUBLIC ROUTES ====================

@app.route('/', methods=['GET'])
def index():
    """Main landing page"""
    if 'user_role' in session:
        if session['user_role'] == 'admin':
            return redirect('/portal/admin/dashboard')
        else:
            return redirect('/portal/staff/dashboard')
    return render_template('landing.html')

@app.route('/portal/login', methods=['GET'])
def portal_login():
    """Main portal login - MFA protected"""
    return render_template('portal_login.html')

@app.route('/portal/auth', methods=['POST'])
def portal_authenticate():
    """Main authentication endpoint - enforces MFA for admin users"""
    response = {'success': False, 'message': '', 'redirect': ''}
    
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    
    if not validate_input(username) or not validate_input(password):
        response['message'] = 'Invalid input format'
        log_action('invalid_login_attempt', username)
        return jsonify(response)
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, role, mfa_enabled FROM portal_users WHERE username=? AND password=?', 
                   (username, password))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        user_id, role, mfa_enabled = user
        
        # Admin users MUST complete MFA
        if role == 'admin' and mfa_enabled:
            # Generate MFA code and store pending auth
            mfa_code = generate_mfa_code()
            pending_mfa[username] = {
                'code': mfa_code,
                'role': role,
                'expires': time.time() + 300
            }
            session['pending_mfa_user'] = username
            log_action('mfa_initiated', username)
            response['success'] = True
            response['redirect'] = '/portal/mfa/verify'
            response['message'] = 'MFA verification required'
        else:
            # Non-admin users bypass MFA
            session['user_role'] = role
            session['username'] = username
            log_action('login_success', username)
            response['success'] = True
            response['redirect'] = '/portal/staff/dashboard'
        
        return jsonify(response)
    else:
        log_action('failed_login', username)
        response['message'] = 'Invalid credentials'
        return jsonify(response)

@app.route('/portal/mfa/verify', methods=['GET', 'POST'])
def mfa_verify():
    """MFA verification endpoint"""
    if request.method == 'POST':
        response = {'success': False, 'message': ''}
        
        code = request.form.get('code', '')
        username = session.get('pending_mfa_user')
        
        if not username or username not in pending_mfa:
            response['message'] = 'MFA session expired'
            return jsonify(response)
        
        mfa_data = pending_mfa[username]
        
        if time.time() > mfa_data['expires']:
            del pending_mfa[username]
            response['message'] = 'MFA code expired'
            return jsonify(response)
        
        if code == mfa_data['code']:
            session['user_role'] = mfa_data['role']
            session['username'] = username
            session.pop('pending_mfa_user', None)
            del pending_mfa[username]
            log_action('mfa_success', username)
            response['success'] = True
            response['redirect'] = '/portal/admin/dashboard'
        else:
            log_action('mfa_failed', username)
            response['message'] = 'Invalid MFA code'
        
        return jsonify(response)
    
    # Display MFA form - show hint about code being sent
    username = session.get('pending_mfa_user')
    if not username or username not in pending_mfa:
        return redirect('/portal/login')
    
    return render_template('mfa_verify.html')

# ==================== STAFF ROUTES ====================

@app.route('/portal/staff/dashboard')
def staff_dashboard():
    """Staff dashboard - basic access"""
    if 'user_role' not in session:
        return redirect('/portal/login')
    if session['user_role'] != 'staff':
        return redirect('/')
    return render_template('staff_dashboard.html', username=session.get('username'))

# ==================== ADMIN ROUTES ====================

@app.route('/portal/admin/dashboard')
def admin_dashboard():
    """Admin dashboard - contains sensitive data"""
    if 'user_role' not in session:
        return redirect('/portal/login')
    if session['user_role'] != 'admin':
        log_action('unauthorized_admin_access', session.get('username'))
        return redirect('/')
    
    flag = os.getenv('FLAG', 'flag{this_is_a_fake_flag}')
    log_action('admin_dashboard_access', session.get('username'))
    return render_template('admin_dashboard.html', flag=flag, username=session.get('username'))

# ==================== LEGACY BACKEND LOGIN ====================
# Note: This endpoint exists for backward compatibility with legacy systems
# It was created before MFA was implemented and has not been updated
# to enforce MFA. This is a known issue tracked in JIRA-4521.

@app.route('/manage/auth', methods=['GET', 'POST'])
def backend_login():
    """Legacy backend authentication - NO MFA ENFORCEMENT"""
    if request.method == 'POST':
        response = {'success': False, 'message': '', 'redirect': ''}
        
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        if not validate_input(username) or not validate_input(password):
            response['message'] = 'Invalid input'
            return jsonify(response)
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT id, role FROM portal_users WHERE username=? AND password=?', 
                       (username, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            user_id, role = user
            # VULNERABILITY: No MFA check for admin users here!
            session['user_role'] = role
            session['username'] = username
            log_action('legacy_login', username)
            
            if role == 'admin':
                response['redirect'] = '/portal/admin/dashboard'
            else:
                response['redirect'] = '/portal/staff/dashboard'
            response['success'] = True
        else:
            response['message'] = 'Authentication failed'
        
        return jsonify(response)
    
    return render_template('backend_login.html')

# ==================== API ROUTES ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'SecurePortal MFA v1.2.3'})

@app.route('/api/users', methods=['GET'])
def list_users():
    """User listing endpoint - limited info for authenticated users"""
    if 'user_role' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT username, role, mfa_enabled FROM portal_users')
    users = cursor.fetchall()
    conn.close()
    
    user_list = []
    for u in users:
        user_list.append({
            'username': u[0],
            'role': u[1],
            'mfa_enabled': bool(u[2])
        })
    
    return jsonify({'users': user_list})

@app.route('/api/version', methods=['GET'])
def version_info():
    """Version information"""
    return jsonify({
        'version': '1.2.3',
        'mfa_module': 'secure-mfa-lib 0.4.9',
        'features': ['user_auth', 'mfa_totp', 'audit_logging']
    })

@app.route('/api/status', methods=['GET'])
def system_status():
    """System status endpoint"""
    return jsonify({
        'auth_service': 'online',
        'mfa_service': 'online', 
        'database': 'online',
        'endpoints': {
            'primary_login': '/portal/login',
            'staff_dashboard': '/portal/staff/dashboard',
            'admin_dashboard': '/portal/admin/dashboard'
        }
    })

# ==================== UTILITY ROUTES ====================

@app.route('/logout', methods=['GET'])
def logout():
    """Logout and clear session"""
    username = session.get('username')
    log_action('logout', username)
    session.clear()
    return redirect('/')

@app.route('/robots.txt')
def robots():
    """Robots.txt with hints"""
    content = """User-agent: *
Disallow: /portal/admin/
Disallow: /manage/
Disallow: /api/internal/
Disallow: /static/backup/
"""
    return content, 200, {'Content-Type': 'text/plain'}

@app.route('/static/backup/config.bak')
def backup_config():
    """Old backup file accidentally left exposed"""
    config_content = """# SecurePortal Configuration Backup
# Created: 2024-01-15
# WARNING: This file contains sensitive data

[database]
host = localhost
name = portal.db

[authentication]
# Default admin account for initial setup
# TODO: Change these credentials after deployment!
admin_user = sysadmin
admin_pass = Adm1n@SecP0rtal!

[mfa]
enabled = true
timeout = 300
code_length = 6

[legacy]
# Legacy backend endpoint preserved for compatibility
backend_path = /manage/auth
"""
    return config_content, 200, {'Content-Type': 'text/plain'}

if __name__ == '__main__':
    init_db() 
    app.run(host='0.0.0.0', port=5003, debug=False)
