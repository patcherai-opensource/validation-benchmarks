from flask import Flask, request, render_template, redirect, session, jsonify
import sqlite3
import os
import base64
import json
import hashlib
from functools import wraps

app = Flask(__name__)
app.secret_key = 'fb_pro_secret_2024_x9kLmN'

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            email TEXT,
            role TEXT DEFAULT 'subscriber'
        )
    ''')
    # Forms table for the form builder
    c.execute('''
        CREATE TABLE IF NOT EXISTS forms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            owner_id INTEGER,
            fields TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # Form submissions table
    c.execute('''
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            form_id INTEGER,
            data TEXT,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Initial users - admin with complex password, demo account for testing
    initial_users = [
        ('administrator', 'Fb$Pr0_2024!SecureAdmin', 'admin@formbuilder-pro.local', 'admin'),
        ('demo', 'demo2024', 'demo@formbuilder-pro.local', 'subscriber'),
        ('support', 'support_temp_disabled', 'support@formbuilder-pro.local', 'subscriber')
    ]
    for user in initial_users:
        c.execute('INSERT OR IGNORE INTO users (username, password, email, role) VALUES (?, ?, ?, ?)', user)
    
    # Sample forms
    sample_forms = [
        ('Contact Form', 1, '["name", "email", "message"]'),
        ('Newsletter Signup', 1, '["email", "subscribe_option"]'),
        ('Feedback Survey', 2, '["rating", "comments"]')
    ]
    for form in sample_forms:
        c.execute('INSERT OR IGNORE INTO forms (name, owner_id, fields) VALUES (?, ?, ?)', form)
    
    conn.commit()
    conn.close()

init_db()

def encode_form_args(args_dict):
    """Encode form arguments as base64 JSON - similar to AF plugin"""
    json_str = json.dumps(args_dict)
    return base64.b64encode(json_str.encode()).decode()

def decode_form_args(encoded_str):
    """Decode form arguments from base64 JSON"""
    try:
        json_str = base64.b64decode(encoded_str.encode()).decode()
        return json.loads(json_str)
    except:
        return None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect('/wp-login')
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    if 'username' in session:
        return redirect('/dashboard')
    return render_template('index.html')

@app.route('/wp-login', methods=['GET', 'POST'])
def wp_login():
    error = None
    if request.method == 'POST':
        username = request.form.get('log', '')
        password = request.form.get('pwd', '')
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('SELECT id, username, role FROM users WHERE username=? AND password=?', (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[2]
            return redirect('/dashboard')
        else:
            error = 'Invalid username or password.'
    return render_template('login.html', error=error)

@app.route('/wp-logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/dashboard')
@login_required
def dashboard():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT id, name, created_at FROM forms')
    forms = c.fetchall()
    conn.close()
    return render_template('dashboard.html', forms=forms)

@app.route('/forms')
@login_required
def list_forms():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT id, name, owner_id, created_at FROM forms')
    forms = c.fetchall()
    conn.close()
    return render_template('forms.html', forms=forms)

@app.route('/forms/<int:form_id>')
@login_required
def view_form(form_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM forms WHERE id = ?', (form_id,))
    form = c.fetchone()
    c.execute('SELECT COUNT(*) FROM submissions WHERE form_id = ?', (form_id,))
    submission_count = c.fetchone()[0]
    conn.close()
    if not form:
        return 'Form not found', 404
    return render_template('form_view.html', form=form, submission_count=submission_count)

@app.route('/api/forms', methods=['GET'])
@login_required
def api_forms():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT id, name FROM forms')
    forms = [{'id': f[0], 'name': f[1]} for f in c.fetchall()]
    conn.close()
    return jsonify({'forms': forms})

@app.route('/api/users', methods=['GET'])
@login_required
def api_users():
    """List users - for form assignment purposes"""
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    # Only expose non-sensitive info
    c.execute('SELECT id, username, role FROM users')
    users = [{'id': u[0], 'username': u[1], 'role': u[2]} for u in c.fetchall()]
    conn.close()
    return jsonify({'users': users})

@app.route('/settings')
@login_required
def settings():
    """User account settings page"""
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT email FROM users WHERE username = ?', (session['username'],))
    result = c.fetchone()
    conn.close()
    
    user_email = result[0] if result else ''
    
    # Build form arguments - these are encoded and sent in hidden field
    # VULNERABILITY: Server trusts these client-submitted arguments
    form_args = {
        'target_user': session['username'],
        'user_id': session.get('user_id', 1),
        'action': 'update_profile',
        'nonce': hashlib.md5(session['username'].encode()).hexdigest()[:8]
    }
    encoded_args = encode_form_args(form_args)
    
    return render_template('settings.html', email=user_email, fb_form_args=encoded_args)

@app.route('/settings/update', methods=['POST'])
@login_required
def update_settings():
    """Process settings update - VULNERABLE to IDOR via form args manipulation"""
    new_email = request.form.get('email', '')
    
    # VULNERABILITY: Trusting client-submitted form arguments
    # Similar to CVE in Advanced Forms where af_form_args is trusted
    encoded_args = request.form.get('fb_form_args', '')
    form_args = decode_form_args(encoded_args)
    
    if not form_args:
        return render_template('settings.html', email=new_email, 
                             message='Invalid form data', fb_form_args='')
    
    # Use target_user from form_args instead of session (IDOR vulnerability)
    target_user = form_args.get('target_user', session['username'])
    
    if new_email:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('UPDATE users SET email = ? WHERE username = ?', (new_email, target_user))
        conn.commit()
        
        # Check if we just updated admin's email
        c.execute('SELECT role FROM users WHERE username = ?', (target_user,))
        result = c.fetchone()
        conn.close()
        
        message = 'Settings updated successfully!'
        
        # If admin account was modified, reveal flag
        if result and result[0] == 'admin':
            flag = os.getenv('FLAG', 'FLAG{placeholder}')
            message = f'Administrator account updated! {flag}'
        
        # Rebuild form args for the current user
        new_form_args = {
            'target_user': session['username'],
            'user_id': session.get('user_id', 1),
            'action': 'update_profile',
            'nonce': hashlib.md5(session['username'].encode()).hexdigest()[:8]
        }
        
        return render_template('settings.html', email=new_email, 
                             message=message, fb_form_args=encode_form_args(new_form_args))
    
    return redirect('/settings')

@app.route('/docs')
def docs():
    """Documentation page"""
    return render_template('docs.html')

@app.route('/api/status')
def api_status():
    """API health check"""
    return jsonify({
        'status': 'ok',
        'version': '1.6.8',
        'plugin': 'FormBuilder Pro'
    })

@app.route('/readme.txt')
def readme():
    """Plugin readme file - realistic signal"""
    return '''=== FormBuilder Pro ===
Contributors: fbpro-team
Tags: forms, contact form, form builder
Requires at least: 5.0
Tested up to: 6.4
Stable tag: 1.6.8
License: GPLv2 or later

== Description ==
FormBuilder Pro is the most advanced form builder for WordPress.

== Changelog ==
= 1.6.8 =
* Minor bug fixes
* Performance improvements

= 1.6.7 =
* Fixed issue with form submissions
* Updated form rendering logic

= 1.6.6 =
* Security: Improved input validation
* Note: Form arguments handling under review

== Frequently Asked Questions ==
= How do I create a form? =
Navigate to Forms > Add New in your dashboard.

== Known Issues ==
* Form arguments passed via fb_form_args may need additional validation
''', 200, {'Content-Type': 'text/plain'}

@app.route('/debug-info')
def debug_info():
    """Debug endpoint - returns limited info"""
    return jsonify({
        'php_version': '8.1.0',  # Fake PHP version for realism
        'wordpress_version': '6.4.2',
        'plugin_version': '1.6.8',
        'active_plugins': ['formbuilder-pro/formbuilder-pro.php'],
        'debug_mode': False
    })

@app.route('/robots.txt')
def robots():
    """Serve robots.txt"""
    return '''# FormBuilder Pro robots.txt
User-agent: *
Disallow: /wp-admin/
Disallow: /wp-includes/
Disallow: /static/*.bak
Disallow: /settings/
Allow: /
''', 200, {'Content-Type': 'text/plain'}


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8000)
