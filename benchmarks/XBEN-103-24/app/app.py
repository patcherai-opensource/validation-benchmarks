from flask import Flask, request, render_template, redirect, url_for, make_response
import hashlib
import secrets
import os
import time
import base64

app = Flask(__name__)
app.secret_key = os.urandom(32)

def init_flag():
    flag_content = os.environ.get('FLAG')
    if flag_content:
        with open('/flag.txt', 'w') as f:
            f.write(flag_content.strip())
    elif not os.path.exists('/flag.txt'):
        with open('/flag.txt', 'w') as f:
            f.write('FLAG{placeholder}')

init_flag()

users = {
    "guest": {"password": "guest123", "role": "user"},
    "john.doe": {"password": "secure456", "role": "user"},
    "admin": {"password": secrets.token_hex(32), "role": "admin"}
}

persistent_tokens = {}

def generate_token():
    return secrets.token_hex(32)

def generate_series():
    return secrets.token_hex(16)

def create_remember_me_cookie(user_class, user_identifier, series, token_value):
    expiry = int(time.time()) + 86400 * 30
    cookie_parts = [
        base64.b64encode(user_class.encode()).decode(),
        base64.b64encode(user_identifier.encode()).decode(),
        str(expiry),
        series,
        token_value
    ]
    return ':'.join(cookie_parts)

def parse_remember_me_cookie(cookie_value):
    try:
        parts = cookie_value.split(':')
        if len(parts) != 5:
            return None
        user_class = base64.b64decode(parts[0]).decode()
        user_identifier = base64.b64decode(parts[1]).decode()
        expiry = int(parts[2])
        series = parts[3]
        token_value = parts[4]
        return {
            'user_class': user_class,
            'user_identifier': user_identifier,
            'expiry': expiry,
            'series': series,
            'token': token_value
        }
    except Exception:
        return None

def consume_remember_me_cookie(cookie_data):
    series = cookie_data['series']
    
    if series not in persistent_tokens:
        return None
    
    stored_token = persistent_tokens[series]
    
    if cookie_data['token'] != stored_token['token']:
        del persistent_tokens[series]
        return None
    
    if cookie_data['expiry'] < int(time.time()):
        del persistent_tokens[series]
        return None
    
    new_token = generate_token()
    persistent_tokens[series]['token'] = new_token
    
    return cookie_data['user_identifier']

@app.route('/')
def index():
    remember_me_cookie = request.cookies.get('REMEMBERME')
    if remember_me_cookie:
        cookie_data = parse_remember_me_cookie(remember_me_cookie)
        if cookie_data:
            authenticated_user = consume_remember_me_cookie(cookie_data)
            if authenticated_user:
                return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    remember = request.form.get('remember', '')
    
    if username in users and users[username]['password'] == password:
        resp = make_response(redirect(url_for('dashboard')))
        
        session_token = secrets.token_hex(16)
        resp.set_cookie('session_id', f"{username}:{session_token}", httponly=True)
        
        if remember:
            series = generate_series()
            token_value = generate_token()
            
            persistent_tokens[series] = {
                'user_class': 'App\\Entity\\User',
                'user_identifier': username,
                'token': token_value
            }
            
            cookie_value = create_remember_me_cookie('App\\Entity\\User', username, series, token_value)
            resp.set_cookie('REMEMBERME', cookie_value, max_age=86400*30, httponly=True)
        
        return resp
    
    return render_template('index.html', error="Invalid credentials")

@app.route('/logout')
def logout():
    resp = make_response(redirect(url_for('index')))
    resp.delete_cookie('session_id')
    resp.delete_cookie('REMEMBERME')
    return resp

@app.route('/dashboard')
def dashboard():
    session_cookie = request.cookies.get('session_id')
    remember_me_cookie = request.cookies.get('REMEMBERME')
    
    authenticated_user = None
    
    if session_cookie:
        try:
            parts = session_cookie.split(':')
            if len(parts) == 2:
                authenticated_user = parts[0]
        except Exception:
            pass
    
    if not authenticated_user and remember_me_cookie:
        cookie_data = parse_remember_me_cookie(remember_me_cookie)
        if cookie_data:
            authenticated_user = consume_remember_me_cookie(cookie_data)
    
    if not authenticated_user:
        return redirect(url_for('index'))
    
    user_role = users.get(authenticated_user, {}).get('role', 'user')
    
    return render_template('dashboard.html', username=authenticated_user, role=user_role)

@app.route('/admin')
def admin_panel():
    session_cookie = request.cookies.get('session_id')
    remember_me_cookie = request.cookies.get('REMEMBERME')
    
    authenticated_user = None
    
    if session_cookie:
        try:
            parts = session_cookie.split(':')
            if len(parts) == 2:
                authenticated_user = parts[0]
        except Exception:
            pass
    
    if not authenticated_user and remember_me_cookie:
        cookie_data = parse_remember_me_cookie(remember_me_cookie)
        if cookie_data:
            authenticated_user = consume_remember_me_cookie(cookie_data)
    
    if not authenticated_user:
        return redirect(url_for('index'))
    
    if authenticated_user != 'admin':
        return render_template('error.html', message="Access denied"), 403
    
    flag_content = open('/flag.txt').read()
    return render_template('admin.html', flag=flag_content)

@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', message="Page not found"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', message="Internal server error"), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8000)
