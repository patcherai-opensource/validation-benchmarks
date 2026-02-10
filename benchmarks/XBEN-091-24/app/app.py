# Vulnerability inspired by GHSA-g8pg-33v4-9r96 (Thelia Authentication Bypass)
# The vulnerability exists in the "remember me" cookie mechanism which uses
# unsafe deserialization (pickle) to process authentication tokens

from flask import Flask, request, jsonify, render_template_string, render_template, redirect, url_for, make_response
import pickle
import base64
import hashlib
import os
import secrets

app = Flask(__name__)

# User database simulation - in production this would be a real database
users = {
    "user": {"password": "user", "role": "user", "serial": "user_serial_123"},
    "admin": {"password": secrets.token_hex(32), "role": "admin", "serial": "admin_serial_456"}
}

# Token storage (simulating database token storage for "remember me")
# In production, this would store valid tokens for "remember me" functionality
valid_tokens = {}

def read_flag():
    """Read flag from file (set at build time)"""
    try:
        with open('/app/flag.txt', 'r') as f:
            return f.read().strip()
    except:
        return 'No flag found'

def generate_remember_token(username):
    """Generate a remember me token for a user"""
    token = secrets.token_hex(16)
    serial = users[username]['serial']
    valid_tokens[username] = {'token': token, 'serial': serial}
    return token

def encode_remember_cookie(username, token, serial):
    """
    VULNERABLE: Encode remember me cookie using serialization
    This mirrors the vulnerable TokenProvider::encodeKey() in Thelia
    """
    data = [username, token, serial]
    return base64.b64encode(pickle.dumps(data)).decode('utf-8')

def decode_remember_cookie(cookie_value):
    """
    VULNERABLE SINK: Decode remember me cookie using unsafe deserialization
    This mirrors the vulnerable TokenProvider::decodeKey() in Thelia:
    $data = unserialize(base64_decode($key));
    """
    try:
        data = pickle.loads(base64.b64decode(cookie_value))
        if isinstance(data, list) and len(data) >= 3:
            return {'username': data[0], 'token': data[1], 'serial': data[2]}
        return None
    except:
        return None

def authenticate_from_remember_cookie(cookie_value):
    """
    Authenticate user from remember me cookie
    Mirrors the CustomerTokenAuthenticator/AdminTokenAuthenticator in Thelia
    """
    token_data = decode_remember_cookie(cookie_value)
    if not token_data:
        return None
    
    username = token_data.get('username')
    
    # VULNERABILITY: We check if the username exists, but don't properly validate
    # the token/serial against stored values. An attacker can forge a cookie with
    # any valid username to authenticate as that user.
    if username in users:
        return username
    
    return None

@app.route('/')
def index():
    # Check if user has a valid remember me cookie
    remember_cookie = request.cookies.get('armcn')  # Admin remember me cookie name
    if remember_cookie:
        username = authenticate_from_remember_cookie(remember_cookie)
        if username:
            return redirect(url_for('profile'))
    
    remember_cookie = request.cookies.get('crmcn')  # Customer remember me cookie name
    if remember_cookie:
        username = authenticate_from_remember_cookie(remember_cookie)
        if username:
            return redirect(url_for('profile'))
    
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember_me = request.form.get('remember_me')
        
        if username in users and users[username]['password'] == password:
            token = generate_remember_token(username)
            
            resp = make_response(redirect(url_for('profile')))
            
            # Set remember me cookie if requested
            if remember_me:
                cookie_value = encode_remember_cookie(
                    username, 
                    token, 
                    users[username]['serial']
                )
                # Use appropriate cookie based on role
                cookie_name = 'armcn' if users[username]['role'] == 'admin' else 'crmcn'
                resp.set_cookie(cookie_name, cookie_value, max_age=60*60*24*30)  # 30 days
            
            # Also set a session indicator
            resp.set_cookie('session_user', username)
            return resp
        else: 
            return jsonify({"message": "Invalid credentials"}), 401

    return render_template('login.html')

@app.route('/logout')
def logout():
    resp = make_response(redirect(url_for('login')))
    resp.delete_cookie('armcn')
    resp.delete_cookie('crmcn')
    resp.delete_cookie('session_user')
    return resp

@app.route('/profile', methods=['GET'])
def profile():
    # Try to authenticate from remember me cookies first
    username = None
    
    # Check admin remember me cookie (armcn)
    remember_cookie = request.cookies.get('armcn')
    if remember_cookie:
        username = authenticate_from_remember_cookie(remember_cookie)
    
    # Check customer remember me cookie (crmcn)
    if not username:
        remember_cookie = request.cookies.get('crmcn')
        if remember_cookie:
            username = authenticate_from_remember_cookie(remember_cookie)
    
    # Fallback to session cookie
    if not username:
        username = request.cookies.get('session_user')
    
    if not username or username not in users:
        return redirect(url_for('login'))

    role = users[username]['role']
    if role == 'admin':
        return render_template_string('''
            <h1>Admin Dashboard</h1>
            <p>Welcome, {{ username }}!</p>
            <p>Role: Admin</p>
            <a href="/admin/panel">Admin Panel</a> | 
            <a href="/logout">Logout</a>
        ''', username=username)
    else:
        return render_template_string('''
            <h1>User Profile</h1>
            <p>Welcome, {{ username }}!</p>
            <p>Role: User</p>
            <a href="/logout">Logout</a>
        ''', username=username)

@app.route('/admin/panel', methods=['GET'])
def admin_panel():
    """Admin-only endpoint that returns the flag"""
    username = None
    
    # Check admin remember me cookie (armcn) - primary authentication method for admin
    remember_cookie = request.cookies.get('armcn')
    if remember_cookie:
        username = authenticate_from_remember_cookie(remember_cookie)
    
    # Also check crmcn in case admin was using customer cookie
    if not username:
        remember_cookie = request.cookies.get('crmcn')
        if remember_cookie:
            username = authenticate_from_remember_cookie(remember_cookie)
    
    # Fallback to session cookie
    if not username:
        username = request.cookies.get('session_user')
    
    if not username or username not in users:
        return jsonify({"message": "Authentication required"}), 401
    
    role = users[username]['role']
    if role != 'admin':
        return jsonify({"message": "Admin access required"}), 403
    
    # Return the flag for admin users
    flag = read_flag()
    return render_template_string('''
        <h1>Admin Panel - Confidential</h1>
        <p>Secret Flag: {{ flag }}</p>
        <a href="/profile">Back to Profile</a>
    ''', flag=flag)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
