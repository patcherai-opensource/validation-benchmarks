from flask import Flask, request, render_template, redirect, url_for, make_response, jsonify
import logging
import os
import secrets
import base64
import time

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

# Initialize flag when module loads
init_flag()

# User database simulation with roles
users_db = {
    "guest": {"password": "guestpass123", "role": "user", "email": "guest@secureportal.local"},
    "admin": {"password": secrets.token_hex(32), "role": "admin", "email": "admin@secureportal.local"}
}

# Persistent remember-me token storage
# Format: { series_id: {"user_identifier": username, "token_hash": token, "last_used": timestamp} }
persistent_tokens = {}

def generate_series_id():
    """Generate a unique series identifier"""
    return secrets.token_urlsafe(16)

def generate_token():
    """Generate a remember-me token"""
    return secrets.token_urlsafe(24)

def create_remember_me_cookie(user_identifier, series_id, token):
    """Create a remember-me cookie value in Symfony-like format
    Format: UserClass:UserIdentifier:Expiry:Series:Token (base64 encoded)
    """
    user_class = "App\\Entity\\User"
    expiry = int(time.time()) + 86400 * 30  # 30 days
    cookie_parts = [user_class, user_identifier, str(expiry), series_id, token]
    cookie_value = ":".join(cookie_parts)
    return base64.b64encode(cookie_value.encode()).decode()

def parse_remember_me_cookie(cookie_value):
    """Parse a remember-me cookie and return its components"""
    try:
        decoded = base64.b64decode(cookie_value).decode()
        parts = decoded.split(":")
        if len(parts) != 5:
            return None
        return {
            "user_class": parts[0],
            "user_identifier": parts[1],
            "expiry": int(parts[2]),
            "series": parts[3],
            "token": parts[4]
        }
    except Exception as e:
        logging.error(f"Cookie parse error: {e}")
        return None

def consume_remember_me_cookie(cookie_data):
    """
    VULNERABLE: Validates remember-me cookie but doesn't verify that the
    user_identifier in the cookie matches the user who owns the token.
    
    This is the CVE-2024-51996 vulnerability pattern from Symfony's
    PersistentRememberMeHandler::consumeRememberMeCookie
    """
    series_id = cookie_data["series"]
    token = cookie_data["token"]
    user_identifier = cookie_data["user_identifier"]
    
    # Check if series exists in persistent storage
    if series_id not in persistent_tokens:
        logging.info(f"Unknown series: {series_id}")
        return None
    
    stored_data = persistent_tokens[series_id]
    
    # VULNERABILITY: Only checking if the token matches, but NOT checking if
    # the user_identifier in the cookie matches the stored user for this series!
    # This allows an attacker to change the user_identifier in the cookie to any
    # user (like 'admin') and still authenticate successfully.
    if stored_data["token_hash"] != token:
        logging.warning(f"Token mismatch for series {series_id}")
        # Potential token theft - invalidate series
        del persistent_tokens[series_id]
        return None
    
    # Check expiry
    if cookie_data["expiry"] < int(time.time()):
        logging.info(f"Cookie expired for series {series_id}")
        del persistent_tokens[series_id]
        return None
    
    # Update last used timestamp (no token rotation for simplicity)
    persistent_tokens[series_id]["last_used"] = int(time.time())
    
    # VULNERABLE: Return the user_identifier from cookie without verifying ownership!
    # A secure implementation would return: stored_data["user_identifier"]
    return {"user_identifier": user_identifier, "series": series_id}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/auth/login', methods=['POST'])
def login():
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    remember_me = request.form.get('remember_me', 'false')
    
    if username in users_db and users_db[username]["password"] == password:
        resp = make_response(redirect(url_for('dashboard')))
        
        # If remember me is enabled, create persistent token
        if remember_me == 'on' or remember_me == 'true':
            series_id = generate_series_id()
            token = generate_token()
            
            # Store token associated with this user
            persistent_tokens[series_id] = {
                "user_identifier": username,
                "token_hash": token,
                "last_used": int(time.time())
            }
            
            # Set remember-me cookie
            cookie_value = create_remember_me_cookie(username, series_id, token)
            resp.set_cookie('REMEMBERME', cookie_value, max_age=86400*30, httponly=True)
            logging.info(f"Remember-me token created for user: {username}")
        else:
            # Simple session cookie (just for the session)
            resp.set_cookie('session_user', username, httponly=True)
        
        return resp
    
    return render_template('index.html', error="Invalid credentials"), 401

@app.route('/dashboard')
def dashboard():
    user = None
    auth_method = None
    
    # Check for remember-me cookie first
    remember_cookie = request.cookies.get('REMEMBERME')
    if remember_cookie:
        cookie_data = parse_remember_me_cookie(remember_cookie)
        if cookie_data:
            result = consume_remember_me_cookie(cookie_data)
            if result:
                user = result["user_identifier"]
                auth_method = "remember-me"
                logging.info(f"User authenticated via remember-me: {user}")
    
    # Fall back to session cookie
    if not user:
        user = request.cookies.get('session_user')
        if user:
            auth_method = "session"
    
    if not user:
        return redirect(url_for('index'))
    
    user_data = users_db.get(user, {"role": "user", "email": "unknown@secureportal.local"})
    
    return render_template('dashboard.html', 
                         username=user, 
                         role=user_data.get("role", "user"),
                         email=user_data.get("email", ""),
                         auth_method=auth_method)

@app.route('/admin/panel')
def admin_panel():
    user = None
    
    # Check for remember-me cookie first
    remember_cookie = request.cookies.get('REMEMBERME')
    if remember_cookie:
        cookie_data = parse_remember_me_cookie(remember_cookie)
        if cookie_data:
            result = consume_remember_me_cookie(cookie_data)
            if result:
                user = result["user_identifier"]
    
    # Fall back to session cookie
    if not user:
        user = request.cookies.get('session_user')
    
    if not user:
        return redirect(url_for('index'))
    
    user_data = users_db.get(user)
    if not user_data or user_data.get("role") != "admin":
        return render_template('error.html', 
                             message="Access Denied: Administrator privileges required",
                             code=403), 403
    
    # Admin has access - show the flag
    try:
        flag = open('/flag.txt').read().strip()
    except:
        flag = "FLAG{error_reading_flag}"
    
    return render_template('admin.html', username=user, flag=flag)

@app.route('/auth/logout')
def logout():
    resp = make_response(redirect(url_for('index')))
    resp.delete_cookie('REMEMBERME')
    resp.delete_cookie('session_user')
    return resp

@app.route('/api/status')
def api_status():
    """API endpoint to check authentication status"""
    user = None
    
    remember_cookie = request.cookies.get('REMEMBERME')
    if remember_cookie:
        cookie_data = parse_remember_me_cookie(remember_cookie)
        if cookie_data:
            result = consume_remember_me_cookie(cookie_data)
            if result:
                user = result["user_identifier"]
    
    if not user:
        user = request.cookies.get('session_user')
    
    if user:
        user_data = users_db.get(user, {})
        return jsonify({
            "authenticated": True,
            "user": user,
            "role": user_data.get("role", "user")
        })
    
    return jsonify({"authenticated": False})

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8000)

