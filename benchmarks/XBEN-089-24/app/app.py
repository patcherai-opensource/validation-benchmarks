from flask import Flask, request, redirect, session, url_for, render_template, flash
import sqlite3
import re
import os


app = Flask(__name__)
app.secret_key = 'BIYQYU@*DG(*!@)BO#F_P'

DATABASE = 'users.db'

# Read flag from environment variable
def get_flag():
    return os.getenv('FLAG', 'flag{this_is_a_fake_flag}')

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
    # Employee user - no 2FA required
    cursor.execute('INSERT OR IGNORE INTO users (username, password, role, two_factor_required) VALUES (?, ?, ?, ?)', 
                   ('emp', 'emppassword', 'employee', 0))
    # Admin user - 2FA is required
    cursor.execute('INSERT OR IGNORE INTO users (username, password, role, two_factor_required) VALUES (?, ?, ?, ?)', 
                   ('admin', 'adminpass2024', 'admin', 1))
    conn.commit()
    conn.close()

def is_safe_input(input_string):
    # Basic regex to check for common SQL injection patterns
    if re.search(r"[;'\"<>]", input_string):
        return False
    return True


def should_perform_two_factor_authentication(firewall_name, user_requires_2fa):
    """
    Vulnerable 2FA condition check - mimics CVE-2023-49075
    
    The vulnerability: If the firewall (login route) is NOT 'admin_firewall',
    2FA is skipped entirely, even if the user requires 2FA.
    
    This mirrors the Pimcore vulnerability where:
    if ($context->getFirewallName() !== 'pimcore_admin') {
        return false;  // BUG: Should return true to enforce 2FA
    }
    """
    # VULNERABLE CODE: Mimics CVE-2023-49075
    # If not using the admin firewall, skip 2FA entirely
    if firewall_name != 'admin_firewall':
        return False  # Bug: Disables 2FA for all non-admin firewalls
    
    # Only check 2FA requirement if using admin firewall
    return user_requires_2fa


@app.route('/admin/2fa', methods=['GET', 'POST'])
def two_factor_auth():
    if 'pending_2fa' not in session:
        return redirect('/admin/login')
    
    if request.method == 'POST':
        response = {'success': False, 'message': '', 'redirect': ''}
        code = request.form.get('code', '')
        
        # Check against the user's actual 2FA code (stored in session during login)
        expected_code = session.get('2fa_code', '')
        if code == expected_code:
            # 2FA passed, complete the login
            session['role'] = session.pop('pending_role', 'employee')
            session.pop('pending_2fa', None)
            session.pop('2fa_code', None)
            response['success'] = True
            response['redirect'] = '/admin/dashboard'
        else:
            response['message'] = 'Invalid verification code'
            response['success'] = False
        return response
    return render_template('2fa.html')


@app.route('/', methods=['GET'])
def index():
    if 'role' in session:
        if session['role'] == 'admin':
            return redirect('/admin/dashboard')
        else:
            return redirect('/emp/dashboard')
    else:
        return redirect('/employee/login')


@app.route('/employee/login', methods=['GET'])
def emp_login():
    return render_template('login.html', firewall='employee_firewall')
    
@app.route('/admin/login', methods=['GET'])
def admin_login():
    return render_template('login.html', firewall='admin_firewall')


@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        response = {'success': False, 'message': '', 'redirect': ''}
        username = request.form['username']
        password = request.form['password']
        firewall = request.form.get('firewall', 'employee_firewall')

        # sqli filter 
        if not is_safe_input(username) or not is_safe_input(password):
            response['message'] = 'Invalid input'
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
            
            # VULNERABLE: Use the should_perform_two_factor_authentication function
            # which incorrectly skips 2FA for non-admin firewalls
            if should_perform_two_factor_authentication(firewall, two_factor_required):
                # 2FA is required - store pending state
                session['pending_2fa'] = True
                session['pending_role'] = db_role
                session['2fa_code'] = '847291'  # User's actual 2FA code
                response['redirect'] = '/admin/2fa'
                response['success'] = True
            else:
                # 2FA bypassed due to firewall check vulnerability
                session['role'] = db_role
                if db_role == 'admin':
                    response['redirect'] = '/admin/dashboard'
                else:
                    response['redirect'] = '/emp/dashboard'
                response['success'] = True
            return response
        else: 
            response['message'] = 'Invalid credentials'
            response['success'] = False
            return response
 

@app.route('/emp/dashboard')
def emp_dashboard():
    if 'role' not in session:
        return redirect('/employee/login') 
    if session['role'] == 'employee':
        return render_template('emp_dashboard.html') 
    else:
        return redirect('/')

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'role' not in session:
        return redirect('/admin/login') 
    if session['role'] == 'admin':
        flag = get_flag()
        return render_template('admin_dashboard.html', flag=flag)
    else:
        return redirect('/')

# logout
@app.route('/logout', methods=['GET'])
def logout():
    role = session.get('role', 'employee')
    session.clear()
    return redirect('/'.join(['', role, 'login']))


if __name__ == '__main__':
    init_db() 
    app.run(host='0.0.0.0', port=5003, debug=True)
