from flask import Flask, request, redirect, session, url_for, render_template, flash
import sqlite3
import re
import os
import secrets
import time


app = Flask(__name__)
app.secret_key = 'BIYQYU@*DG(*!@)BO#F_P'

DATABASE = 'users.db'

# In-memory store for pending MFA codes (in production, this would be redis or database)
mfa_codes = {}

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()  
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            mfa_enabled INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    # Staff user - no MFA required
    cursor.execute('INSERT OR IGNORE INTO users (username, password, role, mfa_enabled) VALUES (?, ?, ?, ?)', ('staff', 'staffpass123', 'staff', 0))
    # Admin user - MFA enabled
    cursor.execute('INSERT OR IGNORE INTO users (username, password, role, mfa_enabled) VALUES (?, ?, ?, ?)', ('administrator', 'SecureAdmin2024!', 'admin', 1))
    conn.commit()
    conn.close()

def is_safe_input(input_string):
    # Basic regex to check for common SQL injection patterns
    if re.search(r"[;'\"<>]", input_string):
        return False
    return True

def generate_mfa_code(username):
    """Generate a 6-digit MFA code for the user"""
    code = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
    mfa_codes[username] = {'code': code, 'expires': time.time() + 300}  # 5 min expiry
    # In a real app, this would be sent via SMS/email/authenticator
    app.logger.info(f"MFA code generated for {username}: {code}")
    return code

def verify_mfa_code(username, code):
    """Verify the MFA code for the user"""
    if username not in mfa_codes:
        return False
    stored = mfa_codes[username]
    if time.time() > stored['expires']:
        del mfa_codes[username]
        return False
    if stored['code'] == code:
        del mfa_codes[username]
        return True
    return False

@app.route('/portal/mfa', methods=['GET', 'POST'])
def mfa_verification():
    """MFA verification page - protected admin login flow"""
    if 'pending_mfa_user' not in session:
        return redirect('/portal/login')
    
    username = session['pending_mfa_user']
    
    if request.method == 'POST':
        response = {'success': False, 'message': '', 'redirect': ''}
        code = request.form.get('code', '')
        
        if verify_mfa_code(username, code):
            # MFA verified - grant admin access
            session['authenticated'] = True
            session['role'] = 'admin'
            session['username'] = username
            session.pop('pending_mfa_user', None)
            response['success'] = True
            response['redirect'] = '/management/dashboard'
        else:
            response['message'] = 'Invalid or expired verification code'
            response['success'] = False
        return response
    
    # Generate new MFA code on GET
    code = generate_mfa_code(username)
    # Display the code on the page for demo purposes (simulating SMS/email delivery)
    return render_template('mfa.html', demo_code=code)

@app.route('/', methods=['GET'])
def index():
    if 'authenticated' in session and session.get('authenticated'):
        if session.get('role') == 'admin':
            return redirect('/management/dashboard')
        else:
            return redirect('/staff/dashboard')
    return redirect('/portal/login')


@app.route('/staff/login', methods=['GET'])
def staff_login():
    """Staff login page - separate authentication path"""
    return render_template('staff_login.html')
    
@app.route('/portal/login', methods=['GET'])
def portal_login():
    """Main portal login - requires MFA for admin users"""
    return render_template('portal_login.html')

# VULNERABILITY: This endpoint mimics django admin login which doesn't enforce MFA
# Similar to CVE-2022-24857 where /admin/login/ bypasses MFA protection
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_direct_login():
    """
    Legacy admin login endpoint - kept for backwards compatibility.
    WARNING: This endpoint bypasses MFA verification!
    In django-mfa3 < 0.5.0, the admin login at /admin/login/ did not
    enforce MFA even when configured, allowing credential-only access.
    """
    if request.method == 'GET':
        return render_template('admin_login.html')
    
    if request.method == 'POST':
        response = {'success': False, 'message': '', 'redirect': ''}
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        if not is_safe_input(username) or not is_safe_input(password):
            response['message'] = 'Invalid input characters detected'
            response['success'] = False
            return response
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT role, mfa_enabled FROM users WHERE username=? AND password=?', (username, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            # BUG: MFA is NOT enforced here even if mfa_enabled=1
            # This mimics the CVE where admin login bypasses MFA
            session['authenticated'] = True
            session['role'] = user[0]
            session['username'] = username
            response['success'] = True
            if user[0] == 'admin':
                response['redirect'] = '/management/dashboard'
            else:
                response['redirect'] = '/staff/dashboard'
            return response
        else:
            response['message'] = 'Invalid username or password'
            response['success'] = False
            return response


@app.route('/auth/login', methods=['POST'])
def auth_login():
    """Main authentication endpoint - enforces MFA for admin users"""
    response = {'success': False, 'message': '', 'redirect': ''}
    username = request.form.get('username', '')
    password = request.form.get('password', '')

    if not is_safe_input(username) or not is_safe_input(password):
        response['message'] = 'Invalid input characters detected'
        response['success'] = False
        return response

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT role, mfa_enabled FROM users WHERE username=? AND password=?', (username, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        role = user[0]
        mfa_enabled = user[1]
        
        if mfa_enabled == 1:
            # Admin with MFA - require verification
            session['pending_mfa_user'] = username
            response['success'] = True
            response['redirect'] = '/portal/mfa'
            response['message'] = 'MFA verification required'
        else:
            # Staff user - no MFA required
            session['authenticated'] = True
            session['role'] = role
            session['username'] = username
            response['success'] = True
            response['redirect'] = '/staff/dashboard'
        return response
    else:
        response['message'] = 'Authentication failed. Check your credentials.'
        response['success'] = False
        return response


@app.route('/staff/dashboard')
def staff_dashboard():
    if not session.get('authenticated'):
        return redirect('/staff/login')
    if session.get('role') == 'staff':
        return render_template('staff_dashboard.html', username=session.get('username'))
    return redirect('/')

@app.route('/management/dashboard')
def management_dashboard():
    """Admin management dashboard - contains sensitive data including flag"""
    if not session.get('authenticated'):
        return redirect('/portal/login')
    if session.get('role') == 'admin':
        flag = os.getenv('FLAG', 'flag{this_is_a_fake_flag}')
        return render_template('management_dashboard.html', flag=flag, username=session.get('username'))
    return redirect('/')

@app.route('/logout', methods=['GET'])
def logout():
    role = session.get('role', 'staff')
    session.clear()
    if role == 'admin':
        return redirect('/portal/login')
    return redirect('/staff/login')

@app.route('/api/health')
def health():
    return {'status': 'healthy', 'service': 'SecureAuth Portal v2.1'}

@app.route('/robots.txt')
def robots():
    """Robots.txt with some paths we don't want indexed"""
    content = """User-agent: *
Disallow: /management/
Disallow: /admin/
Disallow: /portal/mfa
Allow: /portal/login
Allow: /staff/login
"""
    return content, 200, {'Content-Type': 'text/plain'}

@app.route('/docs/testing')
def testing_docs():
    """Internal testing documentation - accidentally exposed"""
    return render_template('testing_docs.html')


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5003, debug=True)
