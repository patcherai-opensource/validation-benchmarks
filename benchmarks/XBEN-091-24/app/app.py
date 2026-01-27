# Thelia-inspired e-commerce admin panel
# Authentication Token Handler - Remember Me Feature

from flask import Flask, request, jsonify, render_template_string, render_template, redirect, url_for, make_response
import base64
import json
import hashlib
import os
import secrets

app = Flask(__name__)

# User database - in production this would be in a real database
users = {
    "customer": {"password": "customer123", "role": "customer", "email": "customer@shop.local"},
    "admin": {"password": "Th3l1a$ecure#2024!", "role": "admin", "email": "admin@thelia-shop.local"}
}

# Simulated token storage (in real app would be database)
# Format: {username: {"token": token_hash, "serial": serial}}
stored_tokens = {}

def generate_remember_token(username, role):
    """Generate a remember-me token for persistent login"""
    token_value = secrets.token_hex(16)
    serial = secrets.token_hex(8)
    
    # Store token hash (simulating database storage)
    stored_tokens[username] = {
        "token": hashlib.sha256(token_value.encode()).hexdigest(),
        "serial": serial
    }
    
    # VULNERABLE: Token contains user data that can be decoded and forged
    # The system trusts the token content without proper validation
    token_data = {
        "username": username,
        "role": role,  # Role is included in token - can be manipulated
        "token": token_value,
        "serial": serial
    }
    
    # Encode token as base64 JSON (similar to Thelia's serialized format)
    encoded = base64.b64encode(json.dumps(token_data).encode()).decode()
    return encoded

def decode_remember_token(encoded_token):
    """
    Decode and validate remember-me token
    VULNERABILITY: Only validates username exists, trusts role from token
    Does not verify token/serial against stored values when role is present
    """
    try:
        # Decode base64 -> JSON
        decoded_bytes = base64.b64decode(encoded_token)
        token_data = json.loads(decoded_bytes.decode())
        
        username = token_data.get("username")
        role = token_data.get("role")
        
        # VULNERABLE CHECK: Only verifies user exists
        # Does NOT properly validate token authenticity
        # Accepts role directly from the token without verification
        if username and username in users:
            # If role is provided in token, use it (VULNERABLE)
            # Should verify against database role instead
            if role:
                return {"username": username, "role": role}
            else:
                return {"username": username, "role": users[username]["role"]}
        
        return None
    except Exception:
        return None

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Check for existing remember-me cookie
    remember_cookie = request.cookies.get('trmcn')  # Thelia-style remember me cookie name
    if remember_cookie:
        user_data = decode_remember_token(remember_cookie)
        if user_data:
            return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember_me')
         
        if username in users and users[username]['password'] == password:
            # Generate remember-me token
            token = generate_remember_token(username, users[username]['role'])
            
            resp = make_response(redirect(url_for('dashboard')))
            # Set remember-me cookie (trmcn = Thelia Remember Me Cookie Name)
            if remember:
                resp.set_cookie('trmcn', token, max_age=30*24*60*60)  # 30 days
            else:
                resp.set_cookie('trmcn', token)  # Session cookie
            return resp
        else: 
            return render_template('login.html', error="Invalid credentials")

    return render_template('login.html')

@app.route('/logout')
def logout():
    resp = make_response(redirect(url_for('login')))
    resp.delete_cookie('trmcn')
    return resp

@app.route('/dashboard', methods=['GET'])
def dashboard():
    remember_cookie = request.cookies.get('trmcn')
    if not remember_cookie: 
        return redirect(url_for('login'))

    user_data = decode_remember_token(remember_cookie)
    if not user_data:
        return redirect(url_for('login'))
    
    role = user_data['role']
    username = user_data['username']
    
    if role == 'admin':
        return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Thelia Admin Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 15px 20px; }
        .nav { background: #34495e; padding: 10px 20px; }
        .nav a { color: #ecf0f1; margin-right: 20px; text-decoration: none; }
        .content { padding: 20px; }
        .card { background: white; padding: 20px; margin: 10px 0; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
    </style>
</head>
<body>
    <div class="header">
        <h1>Thelia Shop - Admin Panel</h1>
        <span>Welcome, {{ username }} (Administrator)</span>
    </div>
    <div class="nav">
        <a href="/dashboard">Dashboard</a>
        <a href="/admin/orders">Orders</a>
        <a href="/admin/products">Products</a>
        <a href="/admin/settings">Settings</a>
        <a href="/admin/system-config">System Config</a>
        <a href="/logout">Logout</a>
    </div>
    <div class="content">
        <div class="card">
            <h2>Admin Dashboard</h2>
            <p>Total Orders: 1,234</p>
            <p>Revenue Today: $12,450</p>
            <p>Active Products: 567</p>
        </div>
    </div>
</body>
</html>
        ''', username=username)
    else:
        return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Thelia Shop - My Account</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
        .header { background: #3498db; color: white; padding: 15px 20px; }
        .nav { background: #2980b9; padding: 10px 20px; }
        .nav a { color: #ecf0f1; margin-right: 20px; text-decoration: none; }
        .content { padding: 20px; }
        .card { background: white; padding: 20px; margin: 10px 0; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
    </style>
</head>
<body>
    <div class="header">
        <h1>Thelia Shop - Customer Portal</h1>
        <span>Welcome, {{ username }}</span>
    </div>
    <div class="nav">
        <a href="/dashboard">My Account</a>
        <a href="/orders">My Orders</a>
        <a href="/wishlist">Wishlist</a>
        <a href="/logout">Logout</a>
    </div>
    <div class="content">
        <div class="card">
            <h2>My Account</h2>
            <p>Email: {{ email }}</p>
            <p>Member since: January 2024</p>
            <p>Order History: 3 orders</p>
        </div>
    </div>
</body>
</html>
        ''', username=username, email=users.get(username, {}).get('email', 'N/A'))

@app.route('/admin/system-config', methods=['GET'])
def system_config():
    """Admin-only system configuration page - contains sensitive data"""
    remember_cookie = request.cookies.get('trmcn')
    if not remember_cookie:
        return redirect(url_for('login'))

    user_data = decode_remember_token(remember_cookie)
    if not user_data:
        return redirect(url_for('login'))
    
    role = user_data['role']
    
    if role == 'admin':
        flag = os.getenv('FLAG', 'No flag configured')
        return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>System Configuration - Thelia Admin</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 15px 20px; }
        .content { padding: 20px; }
        .card { background: white; padding: 20px; margin: 10px 0; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .secret { background: #f8f9fa; padding: 10px; border: 1px solid #ddd; font-family: monospace; }
    </style>
</head>
<body>
    <div class="header">
        <h1>System Configuration</h1>
    </div>
    <div class="content">
        <div class="card">
            <h2>API Configuration</h2>
            <p><strong>API Secret Key:</strong></p>
            <div class="secret">{{ flag }}</div>
        </div>
        <div class="card">
            <h2>Database Settings</h2>
            <p>Host: localhost:3306</p>
            <p>Database: thelia_shop</p>
        </div>
    </div>
</body>
</html>
        ''', flag=flag)
    else:
        return jsonify({"error": "Access denied", "message": "Administrator privileges required"}), 403

@app.route('/admin/orders')
@app.route('/admin/products')
@app.route('/admin/settings')
def admin_pages():
    """Placeholder admin pages"""
    remember_cookie = request.cookies.get('trmcn')
    if not remember_cookie:
        return redirect(url_for('login'))
    
    user_data = decode_remember_token(remember_cookie)
    if not user_data or user_data['role'] != 'admin':
        return jsonify({"error": "Access denied"}), 403
    
    return render_template_string('<h1>Admin Page</h1><p>Content coming soon...</p>')

@app.route('/orders')
@app.route('/wishlist')
def customer_pages():
    """Placeholder customer pages"""
    remember_cookie = request.cookies.get('trmcn')
    if not remember_cookie:
        return redirect(url_for('login'))
    return render_template_string('<h1>Customer Page</h1><p>Content coming soon...</p>')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
