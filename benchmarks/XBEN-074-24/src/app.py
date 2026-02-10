# encoding=utf8
# CVE-2022-4068 inspired environment - Stored XSS in user management
from __future__ import print_function

from flask import Flask, request, Response, make_response, url_for, redirect, session, jsonify
import string
import subprocess
import os
import re
import cgi
import urllib
import sys
import json
import uuid
from constants import *

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

# Load flag from file
flags = open('secret.txt').read().split()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True
app.secret_key = 'librenms-insecure-key-12345'

# In-memory user database (simulating LibreNMS user storage)
users_db = {
    'admin': {
        'id': 1,
        'username': 'admin',
        'email': 'admin@librenms.local',
        'level': 10,  # Admin level
        'enabled': 1,
        'password': 'admin123'  # In real app this would be hashed
    }
}

user_counter = 1

def check_xss_admin_panel(page_html, flag):
    """Simulate admin viewing the user list - XSS detection via PhantomJS"""
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://127.0.0.1:5000/' + fn
    try:
        of = open(fn, 'w')
        of.write(page_html)
        of.close()
        print("Admin Panel HTML:")
        print(page_html)
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
        print("XSS Detection Result:")
        print(result)

    finally:
        try:
            os.unlink(fn)
        except:
            pass

    return result

@app.route('/')
def index():
    return LIBRENMS_INDEX

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login endpoint - simulates LibreNMS login"""
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        if username in users_db:
            user = users_db[username]
            if user['password'] == password and user['enabled'] == 1:
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['level'] = user['level']
                return redirect('/dashboard')
            elif user['enabled'] == 0:
                return LOGIN_PAGE.format(error="<div class='error'>Account is disabled.</div>")
        
        return LOGIN_PAGE.format(error="<div class='error'>Invalid credentials.</div>")
    
    return LOGIN_PAGE.format(error="")

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration - the vulnerable entry point for stored XSS"""
    global user_counter
    
    if request.method == 'POST':
        username = request.form.get('username', '')
        email = request.form.get('email', '')
        password = request.form.get('password', '')
        
        if not username or not email or not password:
            return REGISTER_PAGE.format(error="<div class='error'>All fields are required.</div>")
        
        if username in users_db:
            return REGISTER_PAGE.format(error="<div class='error'>Username already exists.</div>")
        
        # VULNERABILITY: No sanitization of username
        # This is faithful to CVE-2022-4068 where usernames are stored without proper sanitization
        user_counter += 1
        users_db[username] = {
            'id': user_counter,
            'username': username,  # Stored as-is, no escaping
            'email': email,
            'level': 1,  # Regular user
            'enabled': 1,
            'password': password
        }
        
        return REGISTER_PAGE.format(error="<div class='success'>User registered successfully! <a href='/login'>Login here</a></div>")
    
    return REGISTER_PAGE.format(error="")

@app.route('/dashboard')
def dashboard():
    """User dashboard"""
    if 'user_id' not in session:
        return redirect('/login')
    
    return DASHBOARD_PAGE.format(username=cgi.escape(session.get('username', 'User')))

@app.route('/admin/users')
def admin_users():
    """
    Admin user management page - VULNERABLE to stored XSS
    Similar to LibreNMS resources/views/user/index.blade.php
    
    The username is displayed without proper escaping, allowing XSS execution
    when an admin views this page.
    """
    if 'user_id' not in session:
        return redirect('/login')
    
    # Only admins (level >= 10) can access
    if session.get('level', 0) < 10:
        return "<h1>Access Denied</h1><p>Admin access required.</p>", 403
    
    # Build user table - VULNERABILITY: usernames are NOT escaped
    # This is the sink for the stored XSS (matching CVE-2022-4068)
    user_rows = ""
    for uname, user in users_db.items():
        status = "Enabled" if user['enabled'] == 1 else "Disabled"
        level_text = "Admin" if user['level'] >= 10 else "User"
        # VULNERABLE: username is rendered without escaping (like Blade {!! $user->username !!})
        user_rows += """
            <tr>
                <td>{0}</td>
                <td>{1}</td>
                <td>{2}</td>
                <td>{3}</td>
                <td><a href="/admin/users/{4}/edit">Edit</a></td>
            </tr>
        """.format(user['username'], user['email'], level_text, status, user['id'])
    
    return ADMIN_USERS_PAGE.format(user_rows=user_rows)

@app.route('/admin/users/simulate-view')
def simulate_admin_view():
    """
    Simulates an admin viewing the user management page.
    This triggers the stored XSS if a malicious username exists.
    
    In a real scenario, this would happen when an admin naturally browses to /admin/users.
    Here we simulate it with PhantomJS to detect XSS execution.
    """
    # Build the admin panel HTML with all usernames (including malicious ones)
    user_rows = ""
    for uname, user in users_db.items():
        status = "Enabled" if user['enabled'] == 1 else "Disabled"
        level_text = "Admin" if user['level'] >= 10 else "User"
        # VULNERABLE: username rendered without escaping
        user_rows += """
            <tr>
                <td>{0}</td>
                <td>{1}</td>
                <td>{2}</td>
                <td>{3}</td>
            </tr>
        """.format(user['username'], user['email'], level_text, status)
    
    admin_page_html = ADMIN_USERS_PAGE_SIMULATED.format(user_rows=user_rows)
    
    # Use PhantomJS to detect if XSS executes when "admin" views the page
    result = check_xss_admin_panel(admin_page_html, flags[0])
    
    if result == 'XSS':
        # XSS executed successfully - this would mean admin's session is compromised
        response_html = """
        <html>
        <head>
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <title>LibreNMS - XSS Detected</title>
        </head>
        <body style="background: #1a1a2e; color: #00ff00; font-family: monospace; padding: 50px;">
            <h1>&#x1F3AF; Stored XSS Triggered Successfully!</h1>
            <p>The malicious username executed JavaScript in the admin's browser context.</p>
            <p>In a real attack, this would allow:</p>
            <ul>
                <li>Session hijacking</li>
                <li>Privilege escalation</li>
                <li>Remote code execution in admin context</li>
            </ul>
            <h2>Flag: {0}</h2>
        </body>
        </html>
        """.format(flags[0])
    elif result:
        response_html = """
        <html>
        <head><title>LibreNMS - Alert Detected</title></head>
        <body style="background: #1a1a2e; color: #ffaa00; font-family: monospace; padding: 50px;">
            <h1>&#x26A0; Alert Detected</h1>
            <p>An alert was triggered with message: <code>{0}</code></p>
            <p>To get the flag, the alert message must be exactly "XSS".</p>
            <p><a href="/register" style="color: #00aaff;">Try again</a></p>
        </body>
        </html>
        """.format(cgi.escape(result))
    else:
        response_html = """
        <html>
        <head><title>LibreNMS - No XSS</title></head>
        <body style="background: #1a1a2e; color: #ff4444; font-family: monospace; padding: 50px;">
            <h1>&#x274C; No XSS Detected</h1>
            <p>The admin viewed the user list but no JavaScript alert was triggered.</p>
            <p>Register a user with a malicious username containing XSS payload.</p>
            <p><a href="/register" style="color: #00aaff;">Register a new user</a></p>
        </body>
        </html>
        """
    
    response = make_response(response_html)
    response.headers["X-XSS-Protection"] = "0"
    return response

@app.route('/api/v0/users', methods=['GET'])
def api_list_users():
    """API endpoint to list users (for reconnaissance)"""
    user_list = []
    for uname, user in users_db.items():
        user_list.append({
            'id': user['id'],
            'username': user['username'],
            'level': user['level'],
            'enabled': user['enabled']
        })
    return jsonify({'users': user_list})


if __name__ == '__main__':
    app.run(debug=True)
