# encoding=utf8
# BluditLite CMS - Lightweight Content Management System
# Inspired by CVE-2019-12742 - IDOR in password change functionality

from flask import Flask, request, Response, make_response, redirect, session, render_template_string
import os
import sys
import logging
import hashlib

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

# Read the flag from secret file
flag = open('secret.txt').read().strip()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True
app.secret_key = os.urandom(24)

# In-memory user database (simulating a CMS user system)
# The admin has the flag, only accessible after login
users = {
    'admin': {
        'password': hashlib.sha256('supersecretadminpass2024!').hexdigest(),
        'role': 'administrator',
        'email': 'admin@bluditlite.local'
    },
    'editor': {
        'password': hashlib.sha256('editor123').hexdigest(),
        'role': 'editor',
        'email': 'editor@bluditlite.local'
    },
    'guest': {
        'password': hashlib.sha256('guest').hexdigest(),
        'role': 'guest',
        'email': 'guest@bluditlite.local'
    }
}

# HTML Templates
LOGIN_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>BluditLite CMS - Login</title>
    <style>
        body { font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 20px; }
        .container { max-width: 400px; margin: 100px auto; background: #16213e; padding: 30px; border-radius: 10px; box-shadow: 0 0 20px rgba(0,0,0,0.3); }
        h1 { color: #e94560; text-align: center; margin-bottom: 30px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; color: #a0a0a0; }
        input[type="text"], input[type="password"] { width: 100%; padding: 10px; border: 1px solid #0f3460; border-radius: 5px; background: #1a1a2e; color: #fff; box-sizing: border-box; }
        button { width: 100%; padding: 12px; background: #e94560; border: none; border-radius: 5px; color: white; cursor: pointer; font-size: 16px; }
        button:hover { background: #d63447; }
        .error { color: #ff6b6b; text-align: center; margin-bottom: 15px; }
        .info { color: #4ecdc4; text-align: center; margin-top: 20px; font-size: 12px; }
        .logo { text-align: center; margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🔷</div>
        <h1>BluditLite CMS</h1>
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
        <form method="POST" action="/admin/login">
            <div class="form-group">
                <label>Username</label>
                <input type="text" name="username" placeholder="Enter username" required>
            </div>
            <div class="form-group">
                <label>Password</label>
                <input type="password" name="password" placeholder="Enter password" required>
            </div>
            <button type="submit">Sign In</button>
        </form>
        <div class="info">BluditLite CMS v2.8.1</div>
    </div>
</body>
</html>
'''

DASHBOARD_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>BluditLite CMS - Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; margin: 0; }
        .header { background: #16213e; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { color: #e94560; margin: 0; font-size: 20px; }
        .nav { display: flex; gap: 20px; }
        .nav a { color: #a0a0a0; text-decoration: none; }
        .nav a:hover { color: #e94560; }
        .main { display: flex; }
        .sidebar { width: 200px; background: #0f3460; min-height: calc(100vh - 60px); padding: 20px; }
        .sidebar a { display: block; color: #a0a0a0; text-decoration: none; padding: 10px; margin-bottom: 5px; border-radius: 5px; }
        .sidebar a:hover, .sidebar a.active { background: #1a1a2e; color: #e94560; }
        .content { flex: 1; padding: 30px; }
        .card { background: #16213e; border-radius: 10px; padding: 20px; margin-bottom: 20px; }
        .card h2 { color: #e94560; margin-top: 0; }
        .user-info { display: flex; gap: 30px; }
        .user-info div { flex: 1; }
        .user-info label { color: #a0a0a0; display: block; margin-bottom: 5px; }
        .user-info span { color: #fff; }
        .flag-box { background: #0f3460; padding: 15px; border-radius: 5px; margin-top: 20px; border: 2px dashed #e94560; }
        .flag-box h3 { color: #4ecdc4; margin-top: 0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔷 BluditLite CMS</h1>
        <div class="nav">
            <span>Welcome, {{ username }}</span>
            <a href="/admin/logout">Logout</a>
        </div>
    </div>
    <div class="main">
        <div class="sidebar">
            <a href="/admin/dashboard" class="active">Dashboard</a>
            <a href="/admin/user-profile">My Profile</a>
            <a href="/admin/user-password">Change Password</a>
            {% if role == 'administrator' %}
            <a href="/admin/users">Manage Users</a>
            <a href="/admin/settings">Settings</a>
            {% endif %}
        </div>
        <div class="content">
            <div class="card">
                <h2>Dashboard</h2>
                <div class="user-info">
                    <div>
                        <label>Username</label>
                        <span>{{ username }}</span>
                    </div>
                    <div>
                        <label>Role</label>
                        <span>{{ role }}</span>
                    </div>
                    <div>
                        <label>Email</label>
                        <span>{{ email }}</span>
                    </div>
                </div>
                {% if role == 'administrator' %}
                <div class="flag-box">
                    <h3>🏴 Administrator Secret</h3>
                    <p>Congratulations! Here is your flag: <strong>{{ flag }}</strong></p>
                </div>
                {% else %}
                <div class="card" style="margin-top: 20px; background: #0f3460;">
                    <p>You are logged in as <strong>{{ role }}</strong>. Administrator features are restricted.</p>
                </div>
                {% endif %}
            </div>
        </div>
    </div>
</body>
</html>
'''

PASSWORD_CHANGE_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>BluditLite CMS - Change Password</title>
    <style>
        body { font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; margin: 0; }
        .header { background: #16213e; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { color: #e94560; margin: 0; font-size: 20px; }
        .nav { display: flex; gap: 20px; }
        .nav a { color: #a0a0a0; text-decoration: none; }
        .nav a:hover { color: #e94560; }
        .main { display: flex; }
        .sidebar { width: 200px; background: #0f3460; min-height: calc(100vh - 60px); padding: 20px; }
        .sidebar a { display: block; color: #a0a0a0; text-decoration: none; padding: 10px; margin-bottom: 5px; border-radius: 5px; }
        .sidebar a:hover, .sidebar a.active { background: #1a1a2e; color: #e94560; }
        .content { flex: 1; padding: 30px; }
        .card { background: #16213e; border-radius: 10px; padding: 20px; margin-bottom: 20px; }
        .card h2 { color: #e94560; margin-top: 0; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; color: #a0a0a0; }
        input[type="text"], input[type="password"] { width: 300px; padding: 10px; border: 1px solid #0f3460; border-radius: 5px; background: #1a1a2e; color: #fff; }
        button { padding: 12px 30px; background: #e94560; border: none; border-radius: 5px; color: white; cursor: pointer; }
        button:hover { background: #d63447; }
        .success { color: #4ecdc4; margin-bottom: 15px; padding: 10px; background: rgba(78, 205, 196, 0.1); border-radius: 5px; }
        .error { color: #ff6b6b; margin-bottom: 15px; padding: 10px; background: rgba(255, 107, 107, 0.1); border-radius: 5px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔷 BluditLite CMS</h1>
        <div class="nav">
            <span>Welcome, {{ session_user }}</span>
            <a href="/admin/logout">Logout</a>
        </div>
    </div>
    <div class="main">
        <div class="sidebar">
            <a href="/admin/dashboard">Dashboard</a>
            <a href="/admin/user-profile">My Profile</a>
            <a href="/admin/user-password" class="active">Change Password</a>
        </div>
        <div class="content">
            <div class="card">
                <h2>Change Password</h2>
                {% if success %}
                <div class="success">{{ success }}</div>
                {% endif %}
                {% if error %}
                <div class="error">{{ error }}</div>
                {% endif %}
                <form method="POST" action="/admin/user-password">
                    <div class="form-group">
                        <label>New Password</label>
                        <input type="password" name="newPassword" placeholder="Enter new password" required>
                    </div>
                    <div class="form-group">
                        <label>Confirm Password</label>
                        <input type="password" name="confirmPassword" placeholder="Confirm new password" required>
                    </div>
                    <button type="submit">Update Password</button>
                </form>
            </div>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    return redirect('/admin/login')

@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        if username in users:
            hashed = hashlib.sha256(password).hexdigest()
            if users[username]['password'] == hashed:
                session['logged_in'] = True
                session['username'] = username
                return redirect('/admin/dashboard')
        
        return render_template_string(LOGIN_PAGE, error='Invalid username or password')
    
    return render_template_string(LOGIN_PAGE, error=None)

@app.route('/admin/logout')
def logout():
    session.clear()
    return redirect('/admin/login')

@app.route('/admin/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect('/admin/login')
    
    username = session.get('username')
    user = users.get(username, {})
    
    return render_template_string(DASHBOARD_PAGE, 
                                  username=username, 
                                  role=user.get('role', 'unknown'),
                                  email=user.get('email', ''),
                                  flag=flag)

@app.route('/admin/user-profile')
def user_profile():
    if not session.get('logged_in'):
        return redirect('/admin/login')
    return redirect('/admin/dashboard')

@app.route('/admin/user-password', methods=['GET', 'POST'])
def change_password():
    """
    VULNERABLE: This endpoint accepts a 'username' parameter in POST requests
    and changes the password for that user without proper authorization checks.
    
    The vulnerability allows any authenticated user to change any other user's
    password, including the admin account.
    
    Inspired by CVE-2019-12742 in Bludit CMS.
    """
    if not session.get('logged_in'):
        return redirect('/admin/login')
    
    session_user = session.get('username')
    success_msg = None
    error_msg = None
    
    if request.method == 'POST':
        # VULNERABLE: Username is taken from POST data without authorization check
        # This should only allow changing your own password, but accepts any username
        target_username = request.form.get('username', session_user)
        new_password = request.form.get('newPassword', '')
        confirm_password = request.form.get('confirmPassword', '')
        
        if new_password != confirm_password:
            error_msg = 'Passwords do not match'
        elif len(new_password) < 1:
            error_msg = 'Password cannot be empty'
        elif target_username not in users:
            error_msg = 'User not found'
        else:
            # Change password without checking if current user is authorized
            users[target_username]['password'] = hashlib.sha256(new_password).hexdigest()
            success_msg = 'Password successfully updated for user: {}'.format(target_username)
            logging.info('Password changed for user: {} by session user: {}'.format(target_username, session_user))
    
    return render_template_string(PASSWORD_CHANGE_PAGE, 
                                  session_user=session_user,
                                  success=success_msg,
                                  error=error_msg)

@app.route('/admin/users')
def manage_users():
    """Shows list of users - only accessible to admins, provides enumeration hints"""
    if not session.get('logged_in'):
        return redirect('/admin/login')
    
    session_user = session.get('username')
    user = users.get(session_user, {})
    
    if user.get('role') != 'administrator':
        return 'Access Denied: Administrator privileges required', 403
    
    user_list = '<h2>System Users</h2><ul>'
    for uname, udata in users.items():
        user_list += '<li>{} - {} ({})</li>'.format(uname, udata.get('role'), udata.get('email'))
    user_list += '</ul>'
    
    return '''
    <!DOCTYPE html>
    <html>
    <head><title>User Management</title></head>
    <body style="background:#1a1a2e;color:#eee;font-family:Arial;">
    <div style="padding:20px;">
    {}
    <a href="/admin/dashboard" style="color:#e94560;">Back to Dashboard</a>
    </div>
    </body>
    </html>
    '''.format(user_list)

if __name__ == '__main__':
    app.run(debug=True)
