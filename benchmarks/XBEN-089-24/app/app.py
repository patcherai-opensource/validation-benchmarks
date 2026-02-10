from flask import Flask, request, redirect, session, url_for, render_template, flash, jsonify, send_from_directory
import sqlite3
import hashlib
import os
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

DATABASE = 'users.db'
BACKUP_DIR = 'backups'

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            two_factor_required INTEGER DEFAULT 0,
            two_factor_secret TEXT
        )
    ''')
    conn.commit()
    
    admin_pass_hash = hashlib.sha256('SecureAdm1nP@ss2024'.encode()).hexdigest()
    emp_pass_hash = hashlib.sha256('employee123'.encode()).hexdigest()
    
    cursor.execute('INSERT OR IGNORE INTO users (username, password_hash, role, two_factor_required, two_factor_secret) VALUES (?, ?, ?, ?, ?)', 
                   ('admin', admin_pass_hash, 'admin', 1, '847293'))
    cursor.execute('INSERT OR IGNORE INTO users (username, password_hash, role, two_factor_required, two_factor_secret) VALUES (?, ?, ?, ?, ?)', 
                   ('employee', emp_pass_hash, 'employee', 0, None))
    cursor.execute('INSERT OR IGNORE INTO users (username, password_hash, role, two_factor_required, two_factor_secret) VALUES (?, ?, ?, ?, ?)', 
                   ('manager', hashlib.sha256('manager456'.encode()).hexdigest(), 'manager', 1, '192837'))
    conn.commit()
    conn.close()
    
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    backup_content = """# Acme Corp User Credentials Backup
# Generated: 2024-01-15
# WARNING: Keep this file secure!

[users]
admin = SecureAdm1nP@ss2024
employee = employee123
manager = manager456

[notes]
# Admin account has 2FA enabled - use authenticator app
# Manager account also requires 2FA verification
"""
    with open(os.path.join(BACKUP_DIR, 'credentials.bak'), 'w') as f:
        f.write(backup_content)

def get_user(username, password):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute('SELECT id, username, role, two_factor_required, two_factor_secret FROM users WHERE username=? AND password_hash=?', 
                   (username, password_hash))
    user = cursor.fetchone()
    conn.close()
    return user

def should_perform_two_factor_authentication(firewall_name, user):
    """
    Check if 2FA should be performed based on the firewall/login route.
    This mimics the Pimcore PimcoreUserTwoFactorCondition vulnerability.
    """
    if firewall_name != 'admin':
        return False
    
    if user is None:
        return False
    
    return user[3] == 1

@app.route('/', methods=['GET'])
def index():
    if 'authenticated' in session and session['authenticated']:
        if session.get('role') == 'admin':
            return redirect('/admin/dashboard')
        elif session.get('role') == 'manager':
            return redirect('/manager/dashboard')
        else:
            return redirect('/emp/dashboard')
    return redirect('/employee/login')

@app.route('/employee/login', methods=['GET'])
def emp_login():
    return render_template('login.html', firewall='employee')

@app.route('/admin/login', methods=['GET'])
def admin_login():
    return render_template('admin_login.html', firewall='admin')

@app.route('/login', methods=['POST'])
def login():
    response = {'success': False, 'message': '', 'redirect': ''}
    
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    firewall = request.form.get('firewall', 'employee')
    
    if not username or not password:
        response['message'] = 'Username and password are required'
        return jsonify(response)
    
    user = get_user(username, password)
    
    if user is None:
        response['message'] = 'Invalid credentials'
        return jsonify(response)
    
    user_id, uname, role, two_factor_required, two_factor_secret = user
    
    session['pending_user_id'] = user_id
    session['pending_username'] = uname
    session['pending_role'] = role
    session['pending_2fa_secret'] = two_factor_secret
    session['login_firewall'] = firewall
    
    if should_perform_two_factor_authentication(firewall, user):
        response['success'] = True
        response['redirect'] = '/auth/2fa'
        response['requires_2fa'] = True
    else:
        session['authenticated'] = True
        session['user_id'] = user_id
        session['username'] = uname
        session['role'] = role
        
        session.pop('pending_user_id', None)
        session.pop('pending_username', None)
        session.pop('pending_role', None)
        session.pop('pending_2fa_secret', None)
        
        response['success'] = True
        if role == 'admin':
            response['redirect'] = '/admin/dashboard'
        elif role == 'manager':
            response['redirect'] = '/manager/dashboard'
        else:
            response['redirect'] = '/emp/dashboard'
    
    return jsonify(response)

@app.route('/auth/2fa', methods=['GET', 'POST'])
def two_factor_auth():
    if 'pending_user_id' not in session:
        return redirect('/employee/login')
    
    if request.method == 'POST':
        response = {'success': False, 'message': '', 'redirect': ''}
        code = request.form.get('code', '')
        
        expected_code = session.get('pending_2fa_secret')
        
        if code == expected_code:
            session['authenticated'] = True
            session['user_id'] = session['pending_user_id']
            session['username'] = session['pending_username']
            session['role'] = session['pending_role']
            
            role = session['role']
            
            session.pop('pending_user_id', None)
            session.pop('pending_username', None)
            session.pop('pending_role', None)
            session.pop('pending_2fa_secret', None)
            
            response['success'] = True
            if role == 'admin':
                response['redirect'] = '/admin/dashboard'
            elif role == 'manager':
                response['redirect'] = '/manager/dashboard'
            else:
                response['redirect'] = '/emp/dashboard'
        else:
            response['message'] = 'Invalid verification code'
            response['success'] = False
        
        return jsonify(response)
    
    return render_template('2fa.html')

@app.route('/emp/dashboard')
def emp_dashboard():
    if not session.get('authenticated'):
        return redirect('/employee/login')
    if session.get('role') == 'employee':
        return render_template('emp_dashboard.html', username=session.get('username'))
    return redirect('/')

@app.route('/manager/dashboard')
def manager_dashboard():
    if not session.get('authenticated'):
        return redirect('/employee/login')
    if session.get('role') in ['manager', 'admin']:
        return render_template('manager_dashboard.html', username=session.get('username'))
    return redirect('/')

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('authenticated'):
        return redirect('/admin/login')
    if session.get('role') == 'admin':
        flag = os.getenv('FLAG', 'flag{placeholder}')
        return render_template('admin_dashboard.html', username=session.get('username'), flag=flag)
    return redirect('/')

@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect('/employee/login')

@app.route('/backups/<path:filename>')
def serve_backup(filename):
    return send_from_directory(BACKUP_DIR, filename)

@app.route('/robots.txt')
def robots():
    return """User-agent: *
Disallow: /admin/
Disallow: /backups/
"""

@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', error_code=404, message='Page not found'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error_code=500, message='Internal server error'), 500

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5003, debug=False)
