import base64
import json
import secrets
import hashlib
from flask import Flask, request, render_template, redirect, url_for, make_response, session

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

FLAG_FILE = '/app/flag.txt'

users = {
    "guest": {"password": "guest123", "role": "customer", "serial": "c8f2a9b3e1d4"},
    "support": {"password": "support2024!", "role": "customer", "serial": "f1e9d7c5b3a2"},
    "admin": {"password": secrets.token_hex(24), "role": "admin", "serial": "a1b2c3d4e5f6"}
}

def generate_token(username):
    user = users.get(username)
    if not user:
        return None
    token_data = [username, hashlib.sha256((username + user['serial']).encode()).hexdigest()[:16], user['serial']]
    return base64.b64encode(json.dumps(token_data).encode()).decode()

def decode_token(token_value):
    try:
        data = json.loads(base64.b64decode(token_value).decode())
        if isinstance(data, list) and len(data) >= 1:
            return data
        return None
    except:
        return None

def get_user_from_token(token_value):
    data = decode_token(token_value)
    if not data:
        return None
    username = data[0]
    if username in users:
        return {"username": username, "role": users[username]["role"]}
    return None

def check_remember_me():
    crmcn = request.cookies.get('crmcn')
    armcn = request.cookies.get('armcn')
    
    if armcn:
        user_data = get_user_from_token(armcn)
        if user_data and user_data.get('role') == 'admin':
            return user_data
    
    if crmcn:
        user_data = get_user_from_token(crmcn)
        if user_data:
            return user_data
    
    return None

@app.route('/')
def index():
    user = check_remember_me()
    if user:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember_me')
        
        if username in users and users[username]['password'] == password:
            resp = make_response(redirect(url_for('dashboard')))
            session['username'] = username
            session['role'] = users[username]['role']
            
            if remember:
                token = generate_token(username)
                if users[username]['role'] == 'admin':
                    resp.set_cookie('armcn', token, max_age=30*24*60*60, httponly=True)
                else:
                    resp.set_cookie('crmcn', token, max_age=30*24*60*60, httponly=True)
            
            return resp
        else:
            error = "Invalid username or password"
    
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    resp = make_response(redirect(url_for('login')))
    resp.delete_cookie('crmcn')
    resp.delete_cookie('armcn')
    return resp

@app.route('/dashboard')
def dashboard():
    user = None
    
    if 'username' in session:
        user = {"username": session['username'], "role": session.get('role', 'customer')}
    else:
        user = check_remember_me()
        if user:
            session['username'] = user['username']
            session['role'] = user['role']
    
    if not user:
        return redirect(url_for('login'))
    
    return render_template('dashboard.html', user=user)

@app.route('/admin')
def admin_panel():
    user = None
    
    if 'username' in session:
        user = {"username": session['username'], "role": session.get('role', 'customer')}
    else:
        user = check_remember_me()
        if user:
            session['username'] = user['username']
            session['role'] = user['role']
    
    if not user:
        return redirect(url_for('login'))
    
    if user.get('role') != 'admin':
        return render_template('error.html', message="Access denied"), 403
    
    try:
        with open(FLAG_FILE, 'r') as f:
            flag_content = f.read().strip()
    except:
        flag_content = "Configuration error"
    
    return render_template('admin.html', user=user, flag=flag_content)

@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', message="Page not found"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', message="Internal server error"), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
