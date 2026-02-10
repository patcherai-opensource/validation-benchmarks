# encoding=utf8

from flask import Flask, request, Response, make_response, url_for, redirect, session, render_template_string
import string
import subprocess
import os
import re
import cgi
import urllib
import sys
import hashlib
import json
import uuid

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flag = open('secret.txt').read().strip()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False
app.secret_key = os.urandom(24)

users_db = {}
sessions_db = {}

ADMIN_TOKEN = hashlib.sha256(os.urandom(32)).hexdigest()

def init_users():
    admin_pass = hashlib.sha256(os.urandom(32)).hexdigest()
    users_db['admin'] = {
        'id': 1,
        'username': 'admin',
        'password': admin_pass,
        'email': 'admin@example.com',
        'role': 'admin',
        'enabled': True
    }
    
init_users()

def get_current_user():
    session_id = request.cookies.get('session_id')
    if session_id and session_id in sessions_db:
        user_id = sessions_db[session_id]
        for username, user in users_db.items():
            if user['id'] == user_id:
                return user
    return None

@app.route('/')
def index():
    user = get_current_user()
    if user:
        return redirect('/dashboard')
    return render_template_string(LOGIN_PAGE)

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    
    if username in users_db:
        user = users_db[username]
        if user['password'] == hashlib.sha256(password.encode()).hexdigest():
            if not user.get('enabled', True):
                return render_template_string(LOGIN_PAGE, error='Account is disabled')
            session_id = str(uuid.uuid4())
            sessions_db[session_id] = user['id']
            response = make_response(redirect('/dashboard'))
            response.set_cookie('session_id', session_id)
            return response
    
    return render_template_string(LOGIN_PAGE, error='Invalid credentials')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template_string(REGISTER_PAGE)
    
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    email = request.form.get('email', '')
    
    if not username or not password or not email:
        return render_template_string(REGISTER_PAGE, error='All fields are required')
    
    if username in users_db:
        return render_template_string(REGISTER_PAGE, error='Username already exists')
    
    if len(username) > 100:
        return render_template_string(REGISTER_PAGE, error='Username too long')
    
    user_id = len(users_db) + 1
    users_db[username] = {
        'id': user_id,
        'username': username,
        'password': hashlib.sha256(password.encode()).hexdigest(),
        'email': email,
        'role': 'user',
        'enabled': True
    }
    
    session_id = str(uuid.uuid4())
    sessions_db[session_id] = user_id
    response = make_response(redirect('/dashboard'))
    response.set_cookie('session_id', session_id)
    return response

@app.route('/dashboard')
def dashboard():
    user = get_current_user()
    if not user:
        return redirect('/')
    return render_template_string(DASHBOARD_PAGE, user=user)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    user = get_current_user()
    if not user:
        return redirect('/')
    
    if request.method == 'POST':
        new_username = request.form.get('username', user['username'])
        new_email = request.form.get('email', user['email'])
        
        if len(new_username) > 100:
            return render_template_string(PROFILE_PAGE, user=user, error='Username too long')
        
        if new_username != user['username'] and new_username in users_db:
            return render_template_string(PROFILE_PAGE, user=user, error='Username already taken')
        
        old_username = user['username']
        if new_username != old_username:
            users_db[new_username] = users_db.pop(old_username)
        
        users_db[new_username]['username'] = new_username
        users_db[new_username]['email'] = new_email
        
        return render_template_string(PROFILE_PAGE, user=users_db[new_username], message='Profile updated')
    
    return render_template_string(PROFILE_PAGE, user=user)

@app.route('/logout')
def logout():
    session_id = request.cookies.get('session_id')
    if session_id and session_id in sessions_db:
        del sessions_db[session_id]
    response = make_response(redirect('/'))
    response.delete_cookie('session_id')
    return response

@app.route('/admin/users')
def admin_users():
    admin_token = request.args.get('token', '')
    if admin_token != ADMIN_TOKEN:
        return 'Unauthorized', 403
    
    user_list = []
    for username, user in users_db.items():
        user_list.append(user)
    
    return render_template_string(ADMIN_USERS_PAGE, users=user_list, flag=flag)

@app.route('/admin/simulate')
def admin_simulate():
    user = get_current_user()
    if not user:
        return redirect('/')
    
    proc = subprocess.Popen(["timeout","8","phantomjs", "check_admin.js"], 
                           stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    admin_url = 'http://127.0.0.1:5000/admin/users?token=' + ADMIN_TOKEN
    try:
        proc.stdin.write(admin_url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
        proc.wait()
    except:
        result = ""
    
    if result and result.startswith('FLAG:'):
        return render_template_string(RESULT_PAGE, success=True, flag=result[5:])
    elif result:
        return render_template_string(RESULT_PAGE, success=False, message='Alert detected: ' + cgi.escape(result))
    else:
        return render_template_string(RESULT_PAGE, success=False, message='No XSS detected')

@app.errorhandler(404)
def not_found(e):
    return 'Not Found', 404

@app.errorhandler(500)
def server_error(e):
    return 'Internal Server Error', 500

LOGIN_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>NetMon - Login</title>
    <link rel="stylesheet" type="text/css" href="/static/css/style.css">
    <style>
        body { font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 20px; }
        .container { max-width: 400px; margin: 50px auto; background: #16213e; padding: 30px; border-radius: 8px; }
        h1 { text-align: center; color: #0f3460; }
        h1 { color: #e94560; }
        input { width: 100%; padding: 10px; margin: 10px 0; box-sizing: border-box; border: 1px solid #0f3460; border-radius: 4px; background: #1a1a2e; color: #eee; }
        button { width: 100%; padding: 10px; background: #e94560; color: white; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #d63050; }
        .error { color: #ff6b6b; text-align: center; }
        .links { text-align: center; margin-top: 15px; }
        .links a { color: #e94560; }
    </style>
</head>
<body>
    <div class="container">
        <h1>NetMon</h1>
        <h3 style="text-align:center;color:#888;">Network Monitoring System</h3>
        {% if error %}<p class="error">{{ error }}</p>{% endif %}
        <form method="POST" action="/login">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Login</button>
        </form>
        <div class="links">
            <a href="/register">Create an account</a>
        </div>
    </div>
</body>
</html>
'''

REGISTER_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>NetMon - Register</title>
    <style>
        body { font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 20px; }
        .container { max-width: 400px; margin: 50px auto; background: #16213e; padding: 30px; border-radius: 8px; }
        h1 { text-align: center; color: #e94560; }
        input { width: 100%; padding: 10px; margin: 10px 0; box-sizing: border-box; border: 1px solid #0f3460; border-radius: 4px; background: #1a1a2e; color: #eee; }
        button { width: 100%; padding: 10px; background: #e94560; color: white; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #d63050; }
        .error { color: #ff6b6b; text-align: center; }
        .links { text-align: center; margin-top: 15px; }
        .links a { color: #e94560; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Create Account</h1>
        {% if error %}<p class="error">{{ error }}</p>{% endif %}
        <form method="POST" action="/register">
            <input type="text" name="username" placeholder="Username" required>
            <input type="email" name="email" placeholder="Email" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Register</button>
        </form>
        <div class="links">
            <a href="/">Back to Login</a>
        </div>
    </div>
</body>
</html>
'''

DASHBOARD_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>NetMon - Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 20px; }
        .container { max-width: 800px; margin: 30px auto; background: #16213e; padding: 30px; border-radius: 8px; }
        h1 { color: #e94560; }
        .nav { margin-bottom: 20px; }
        .nav a { color: #e94560; margin-right: 15px; text-decoration: none; }
        .nav a:hover { text-decoration: underline; }
        .card { background: #0f3460; padding: 20px; border-radius: 8px; margin: 15px 0; }
        .btn { display: inline-block; padding: 10px 20px; background: #e94560; color: white; border: none; border-radius: 4px; cursor: pointer; text-decoration: none; }
        .btn:hover { background: #d63050; }
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="/dashboard">Dashboard</a>
            <a href="/profile">Profile</a>
            <a href="/logout">Logout</a>
        </div>
        <h1>Welcome, {{ user.username }}</h1>
        <div class="card">
            <h3>Network Status</h3>
            <p>All systems operational</p>
        </div>
        <div class="card">
            <h3>Recent Alerts</h3>
            <p>No alerts at this time</p>
        </div>
        <div class="card">
            <h3>Admin Review</h3>
            <p>Request an administrator to review your account settings.</p>
            <a href="/admin/simulate" class="btn">Request Admin Review</a>
        </div>
    </div>
</body>
</html>
'''

PROFILE_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>NetMon - Profile</title>
    <style>
        body { font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 20px; }
        .container { max-width: 600px; margin: 30px auto; background: #16213e; padding: 30px; border-radius: 8px; }
        h1 { color: #e94560; }
        .nav { margin-bottom: 20px; }
        .nav a { color: #e94560; margin-right: 15px; text-decoration: none; }
        input { width: 100%; padding: 10px; margin: 10px 0; box-sizing: border-box; border: 1px solid #0f3460; border-radius: 4px; background: #1a1a2e; color: #eee; }
        button { padding: 10px 20px; background: #e94560; color: white; border: none; border-radius: 4px; cursor: pointer; }
        .error { color: #ff6b6b; }
        .success { color: #51cf66; }
        label { display: block; margin-top: 15px; color: #888; }
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="/dashboard">Dashboard</a>
            <a href="/profile">Profile</a>
            <a href="/logout">Logout</a>
        </div>
        <h1>Edit Profile</h1>
        {% if error %}<p class="error">{{ error }}</p>{% endif %}
        {% if message %}<p class="success">{{ message }}</p>{% endif %}
        <form method="POST" action="/profile">
            <label>Username</label>
            <input type="text" name="username" value="{{ user.username }}" required>
            <label>Email</label>
            <input type="email" name="email" value="{{ user.email }}" required>
            <label>Role</label>
            <input type="text" value="{{ user.role }}" disabled>
            <br><br>
            <button type="submit">Update Profile</button>
        </form>
    </div>
</body>
</html>
'''

ADMIN_USERS_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>NetMon - User Management</title>
    <style>
        body { font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 20px; }
        .container { max-width: 900px; margin: 30px auto; background: #16213e; padding: 30px; border-radius: 8px; }
        h1 { color: #e94560; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #0f3460; }
        th { background: #0f3460; }
        .admin-flag { display: none; }
    </style>
</head>
<body>
    <div class="container">
        <h1>User Management</h1>
        <table>
            <tr>
                <th>ID</th>
                <th>Username</th>
                <th>Email</th>
                <th>Role</th>
                <th>Status</th>
            </tr>
            {% for user in users %}
            <tr>
                <td>{{ user.id }}</td>
                <td>{{ user.username | safe }}</td>
                <td>{{ user.email }}</td>
                <td>{{ user.role }}</td>
                <td>{% if user.enabled %}Active{% else %}Disabled{% endif %}</td>
            </tr>
            {% endfor %}
        </table>
        <div class="admin-flag" id="secret-data">{{ flag }}</div>
    </div>
</body>
</html>
'''

RESULT_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>NetMon - Admin Review Result</title>
    <style>
        body { font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 20px; }
        .container { max-width: 600px; margin: 50px auto; background: #16213e; padding: 30px; border-radius: 8px; text-align: center; }
        h1 { color: #e94560; }
        .success { color: #51cf66; font-size: 18px; }
        .error { color: #ff6b6b; }
        .flag { background: #0f3460; padding: 15px; border-radius: 4px; font-family: monospace; margin: 20px 0; word-break: break-all; }
        .btn { display: inline-block; padding: 10px 20px; background: #e94560; color: white; border: none; border-radius: 4px; cursor: pointer; text-decoration: none; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Admin Review Result</h1>
        {% if success %}
        <p class="success">Congratulations! The admin reviewed your profile and found sensitive data.</p>
        <div class="flag">{{ flag }}</div>
        {% else %}
        <p class="error">{{ message }}</p>
        {% endif %}
        <a href="/dashboard" class="btn">Back to Dashboard</a>
    </div>
</body>
</html>
'''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
