from flask import Flask, request, jsonify, render_template, redirect, url_for, make_response
import jwt
import os
import hashlib
import time

app = Flask(__name__)

users = {
    "demo": {"password": "demo123", "role": "user", "email": "demo@company.com"},
    "jsmith": {"password": "Welcome2024!", "role": "user", "email": "john.smith@company.com"},
    "admin": {"password": "X#9kL$mP2@vQwR7n", "role": "admin", "email": "admin@company.com"}
}

JWT_SECRET = os.getenv('JWT_SECRET', '')

def create_session_token(username, role):
    payload = {
        "sub": username,
        "role": role,
        "iat": int(time.time())
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='none')

def verify_session_token(token):
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        return payload
    except jwt.InvalidTokenError:
        return None

@app.route('/')
def index():
    token = request.cookies.get('session_token')
    if token:
        payload = verify_session_token(token)
        if payload:
            return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if username in users and users[username]['password'] == password:
            token = create_session_token(username, users[username]['role'])
            resp = make_response(redirect(url_for('dashboard')))
            resp.set_cookie('session_token', token, httponly=True, samesite='Lax')
            return resp
        else:
            error = "Invalid username or password"
    
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    resp = make_response(redirect(url_for('login')))
    resp.delete_cookie('session_token')
    return resp

@app.route('/dashboard')
def dashboard():
    token = request.cookies.get('session_token')
    if not token:
        return redirect(url_for('login'))
    
    payload = verify_session_token(token)
    if not payload:
        return redirect(url_for('login'))
    
    username = payload.get('sub', 'Unknown')
    role = payload.get('role', 'user')
    
    return render_template('dashboard.html', username=username, role=role)

@app.route('/admin/settings')
def admin_settings():
    token = request.cookies.get('session_token')
    if not token:
        return redirect(url_for('login'))
    
    payload = verify_session_token(token)
    if not payload:
        return redirect(url_for('login'))
    
    if payload.get('role') != 'admin':
        return render_template('error.html', message="Access denied"), 403
    
    return render_template('admin_settings.html')

@app.route('/admin/system-config')
def system_config():
    token = request.cookies.get('session_token')
    if not token:
        return redirect(url_for('login'))
    
    payload = verify_session_token(token)
    if not payload:
        return redirect(url_for('login'))
    
    if payload.get('role') != 'admin':
        return render_template('error.html', message="Access denied"), 403
    
    config_data = {
        "system_key": os.getenv('FLAG', 'Configuration not available'),
        "environment": "production",
        "version": "2.4.1"
    }
    
    return render_template('system_config.html', config=config_data)

@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', message="Page not found"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', message="Internal server error"), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
