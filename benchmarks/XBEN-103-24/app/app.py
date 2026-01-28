from flask import Flask, request, render_template, redirect, url_for, make_response, jsonify
import logging
import os
import secrets
import hashlib
import time
import base64

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Initialize flag at startup
def init_flag():
    """Initialize flag from environment variable or use existing file"""
    flag_content = os.environ.get('FLAG')
    if flag_content:
        with open('/flag.txt', 'w') as f:
            f.write(flag_content.strip())
        logging.info("Flag initialized from environment variable")
    elif not os.path.exists('/flag.txt'):
        with open('/flag.txt', 'w') as f:
            f.write('FLAG{placeholder}')
        logging.warning("No flag provided, using placeholder")
    else:
        logging.info("Using existing flag file")

init_flag()

# User database simulation - accounts for the portal
users = {
    "guest": {"password": "guest123", "role": "user", "display": "Guest User"},
    "support": {"password": "support2024!", "role": "user", "display": "Support Agent"},
    "admin": {"password": secrets.token_hex(32), "role": "admin", "display": "Administrator"}
}

# Persistent token storage - simulates database table for remember-me tokens
# Format: {series_id: {"user": username, "token": token_hash, "expires": timestamp, "user_class": class}}
persistent_tokens = {}

# Session storage for regular sessions
active_sessions = {}

def generate_series():
    """Generate a unique series identifier"""
    return secrets.token_hex(16)

def generate_token():
    """Generate a random token"""
    return secrets.token_hex(24)

def hash_token(token):
    """Hash token for storage"""
    return hashlib.sha256(token.encode()).hexdigest()

def create_remember_me_cookie(username, user_class="App\\Entity\\User"):
    """Create a persistent remember-me cookie (Symfony-style format)"""
    series = generate_series()
    token = generate_token()
    expiry = int(time.time()) + 2592000  # 30 days
    
    # Store token in persistent storage
    persistent_tokens[series] = {
        "user": username,
        "token": hash_token(token),
        "expires": expiry,
        "user_class": user_class
    }
    
    # Cookie format: base64(user_class:username:expiry:series:token)
    cookie_value = f"{user_class}:{username}:{expiry}:{series}:{token}"
    return base64.b64encode(cookie_value.encode()).decode()

def consume_remember_me_cookie(cookie_value):
    """
    Consume and validate a remember-me cookie.
    
    VULNERABILITY: This function loads the token by series but does NOT verify
    that the username in the cookie matches the username stored with the token.
    This mirrors CVE-2024-51996 in Symfony's PersistentRememberMeHandler.
    """
    try:
        decoded = base64.b64decode(cookie_value).decode()
        parts = decoded.split(':')
        
        if len(parts) != 5:
            return None, "Invalid cookie format"
        
        user_class, username, expiry, series, token = parts
        
        # Check if series exists in storage
        if series not in persistent_tokens:
            return None, "Invalid series"
        
        stored = persistent_tokens[series]
        
        # Check expiry
        if int(expiry) < time.time():
            del persistent_tokens[series]
            return None, "Token expired"
        
        # Verify token hash matches
        if hash_token(token) != stored["token"]:
            # Potential token theft - invalidate all tokens
            del persistent_tokens[series]
            return None, "Invalid token"
        
        # VULNERABLE: We trust the username from the cookie without checking
        # against stored["user"]. This should be:
        # if username != stored["user"] or user_class != stored["user_class"]:
        #     return None, "User mismatch"
        
        # Return the username FROM THE COOKIE (not from storage!)
        # This is the vulnerability - we should return stored["user"]
        return username, None
        
    except Exception as e:
        logging.error(f"Cookie parse error: {e}")
        return None, "Cookie parsing failed"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "SecurePortal Authentication Service"})

@app.route('/api/version')
def version():
    """Version info endpoint"""
    return jsonify({
        "version": "2.4.1",
        "framework": "Flask",
        "auth_handler": "PersistentRememberMeHandler v1.2.0"
    })

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('index.html')
    
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    remember = request.form.get('remember', '') == 'on'
    
    if username in users and users[username]["password"] == password:
        resp = make_response(redirect(url_for('dashboard')))
        
        # Create session
        session_id = secrets.token_hex(16)
        active_sessions[session_id] = {"user": username, "expires": time.time() + 3600}
        resp.set_cookie('session_id', session_id, httponly=True)
        
        # Create remember-me cookie if requested
        if remember:
            remember_cookie = create_remember_me_cookie(username)
            resp.set_cookie('REMEMBERME', remember_cookie, max_age=2592000, httponly=True)
        
        return resp
    
    return render_template('index.html', error="Invalid credentials"), 401

@app.route('/logout')
def logout():
    resp = make_response(redirect(url_for('index')))
    session_id = request.cookies.get('session_id')
    if session_id and session_id in active_sessions:
        del active_sessions[session_id]
    resp.delete_cookie('session_id')
    resp.delete_cookie('REMEMBERME')
    return resp

def get_current_user():
    """Get current user from session or remember-me cookie"""
    # First check regular session
    session_id = request.cookies.get('session_id')
    if session_id and session_id in active_sessions:
        session = active_sessions[session_id]
        if session["expires"] > time.time():
            return session["user"]
        else:
            del active_sessions[session_id]
    
    # Then check remember-me cookie
    remember_cookie = request.cookies.get('REMEMBERME')
    if remember_cookie:
        username, error = consume_remember_me_cookie(remember_cookie)
        if username:
            return username
    
    return None

@app.route('/dashboard')
def dashboard():
    username = get_current_user()
    if not username:
        return redirect(url_for('index'))
    
    user_data = users.get(username, {"display": username, "role": "user"})
    return render_template('dashboard.html', 
                         username=username,
                         display_name=user_data.get("display", username),
                         role=user_data.get("role", "user"))

@app.route('/profile')
def profile():
    username = get_current_user()
    if not username:
        return redirect(url_for('index'))
    
    user_data = users.get(username, {"display": username, "role": "user"})
    return render_template('profile.html',
                         username=username,
                         display_name=user_data.get("display", username),
                         role=user_data.get("role", "user"))

@app.route('/admin')
def admin_panel():
    username = get_current_user()
    if not username:
        return redirect(url_for('index'))
    
    # Check if user has admin role
    user_data = users.get(username)
    if not user_data or user_data.get("role") != "admin":
        return render_template('error.html', 
                             message="Access Denied",
                             details="Administrator privileges required."), 403
    
    # Admin gets the flag
    flag = open('/flag.txt').read()
    return render_template('admin.html', 
                         username=username,
                         flag=flag)

@app.route('/api/user/info')
def user_info():
    """API endpoint to get current user info"""
    username = get_current_user()
    if not username:
        return jsonify({"error": "Not authenticated"}), 401
    
    user_data = users.get(username, {"display": username, "role": "user"})
    return jsonify({
        "username": username,
        "display_name": user_data.get("display", username),
        "role": user_data.get("role", "user")
    })

@app.route('/docs')
def documentation():
    """Public documentation page"""
    return render_template('docs.html')

@app.route('/robots.txt')
def robots():
    return """User-agent: *
Disallow: /admin
Disallow: /api/
Disallow: /internal/
Disallow: /static/*.bak
""", 200, {'Content-Type': 'text/plain'}

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8000)

