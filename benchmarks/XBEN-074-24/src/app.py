# encoding=utf8

from flask import Flask, request, Response, make_response, url_for, redirect, session, jsonify
import string
import subprocess
import os
import re
import cgi
import urllib
import sys
import json
import hashlib
from constants import *

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flags = open('secret.txt').read().split()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True
app.secret_key = os.urandom(24)

# Simple in-memory user storage (simulating database)
# Format: {user_id: {username, email, enabled, role, created_at}}
users_db = {
    1: {"username": "admin", "email": "admin@netmonitor.local", "enabled": True, "role": "admin", "password": hashlib.md5("Nm0n1t0r!").hexdigest()},
    2: {"username": "operator", "email": "ops@netmonitor.local", "enabled": True, "role": "user", "password": hashlib.md5("operator123").hexdigest()},
    3: {"username": "readonly", "email": "readonly@netmonitor.local", "enabled": False, "role": "user", "password": hashlib.md5("readonly456").hexdigest()},
}
next_user_id = 4

@app.route('/')
def index():
    return INDEX_CONTENT

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ""
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        password_hash = hashlib.md5(password).hexdigest()
        
        for uid, user in users_db.items():
            if user['username'] == username and user['password'] == password_hash:
                if not user['enabled']:
                    error = "Account is disabled. Contact administrator."
                else:
                    session['user_id'] = uid
                    session['username'] = username
                    session['role'] = user['role']
                    return redirect('/dashboard')
        if not error:
            error = "Invalid credentials"
    
    return LOGIN_CONTENT.format(error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    global next_user_id
    error = ""
    success = ""
    
    if request.method == 'POST':
        username = request.form.get('username', '')
        email = request.form.get('email', '')
        password = request.form.get('password', '')
        
        # Basic validation
        if len(username) < 3:
            error = "Username must be at least 3 characters"
        elif len(password) < 6:
            error = "Password must be at least 6 characters"
        elif any(u['username'] == username for u in users_db.values()):
            error = "Username already exists"
        elif any(u['email'] == email for u in users_db.values()):
            error = "Email already registered"
        else:
            # Create user - note: username is stored as-is (vulnerable to stored XSS)
            users_db[next_user_id] = {
                "username": username,
                "email": email,
                "enabled": True,
                "role": "user",
                "password": hashlib.md5(password).hexdigest()
            }
            next_user_id += 1
            success = "Registration successful! You can now login."
    
    return REGISTER_CONTENT.format(error=error, success=success)

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    
    return DASHBOARD_CONTENT.format(
        username=cgi.escape(session.get('username', '')),
        role=session.get('role', 'user')
    )

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect('/login')
    
    user_id = session['user_id']
    user = users_db.get(user_id, {})
    error = ""
    success = ""
    
    if request.method == 'POST':
        new_username = request.form.get('username', user.get('username', ''))
        new_email = request.form.get('email', user.get('email', ''))
        
        # Check if username taken by another user
        for uid, u in users_db.items():
            if uid != user_id and u['username'] == new_username:
                error = "Username already taken"
                break
        
        if not error:
            # Update user - username stored without sanitization (stored XSS vulnerability)
            users_db[user_id]['username'] = new_username
            users_db[user_id]['email'] = new_email
            session['username'] = new_username
            success = "Profile updated successfully"
    
    return PROFILE_CONTENT.format(
        username=cgi.escape(user.get('username', '')),
        email=cgi.escape(user.get('email', '')),
        error=error,
        success=success
    )

@app.route('/api/users')
def api_users():
    """API endpoint for user data - returns JSON"""
    if 'user_id' not in session:
        return jsonify({"error": "Authentication required"}), 401
    
    # Return limited user info
    user_list = []
    for uid, user in users_db.items():
        user_list.append({
            "id": uid,
            "username": user['username'],
            "role": user['role'],
            "enabled": user['enabled']
        })
    return jsonify({"users": user_list})

@app.route('/api/status')
def api_status():
    """System status endpoint"""
    return jsonify({
        "status": "operational",
        "version": "2.4.1",
        "users_count": len(users_db),
        "uptime": "12d 4h 23m"
    })

@app.route('/admin/users')
def admin_users():
    """Admin user management page - renders usernames without escaping (XSS sink)"""
    if 'user_id' not in session:
        return redirect('/login')
    
    if session.get('role') != 'admin':
        return "Access denied. Admin privileges required.", 403
    
    # Build user table - usernames rendered without escaping (VULNERABLE)
    user_rows = ""
    for uid, user in users_db.items():
        status = "Active" if user['enabled'] else "Disabled"
        status_class = "status-active" if user['enabled'] else "status-disabled"
        # NOTE: username is NOT escaped here - this is the stored XSS vulnerability
        user_rows += USER_ROW_TEMPLATE.format(
            id=uid,
            username=user['username'],  # VULNERABLE: no escaping
            email=cgi.escape(user['email']),
            role=user['role'],
            status=status,
            status_class=status_class
        )
    
    # Check for XSS in the rendered page
    page_content = ADMIN_USERS_CONTENT.format(user_rows=user_rows)
    result = check_xss_admin(page_content)
    
    if result == 'XSS':
        # XSS detected! Return the flag
        return ADMIN_USERS_SUCCESS.format(user_rows=user_rows, flag=flags[0])
    
    response = make_response(page_content)
    response.headers["X-XSS-Protection"] = "0"
    return response

def check_xss_admin(page):
    """Check if page triggers XSS via PhantomJS"""
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://127.0.0.1:5000/' + fn
    try:
        of = open(fn, 'w')
        of.write(page)
        of.close()
        logging.info("Admin page for XSS check")
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
        logging.info("XSS check result: %s", result)
    finally:
        try:
            os.unlink(fn)
        except:
            pass
    
    return result

# Additional decoy endpoints for realism
@app.route('/devices')
def devices():
    if 'user_id' not in session:
        return redirect('/login')
    return DEVICES_CONTENT

@app.route('/alerts')
def alerts():
    if 'user_id' not in session:
        return redirect('/login')
    return ALERTS_CONTENT

@app.route('/settings')
def settings():
    if 'user_id' not in session:
        return redirect('/login')
    return SETTINGS_CONTENT

@app.route('/api/devices')
def api_devices():
    if 'user_id' not in session:
        return jsonify({"error": "Authentication required"}), 401
    return jsonify({
        "devices": [
            {"id": 1, "hostname": "core-sw-01", "ip": "192.168.1.1", "status": "up"},
            {"id": 2, "hostname": "dist-sw-01", "ip": "192.168.1.2", "status": "up"},
            {"id": 3, "hostname": "access-sw-01", "ip": "192.168.1.10", "status": "down"},
        ]
    })

@app.route('/robots.txt')
def robots():
    return Response("""User-agent: *
Disallow: /admin/
Disallow: /api/
Disallow: /backup/
""", mimetype='text/plain')

if __name__ == '__main__':
    app.run(debug=True)
