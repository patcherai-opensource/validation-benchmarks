"""
Vulnerable Remember-Me Authentication System
CVE-2024-51996: Authentication Bypass via Remember-Me Cookie Tampering

This application implements a persistent remember-me token system similar to Symfony's
PersistentRememberMeHandler. The vulnerability is that when consuming a remember-me cookie,
the system validates the token series and value, but does NOT validate that the username
in the cookie matches the username stored with the token in the database.
"""

from flask import Flask, request, render_template, redirect, url_for, make_response, jsonify
import logging
import os
import secrets
import sqlite3
import base64
import hashlib
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

DATABASE = '/tmp/rememberme.db'

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

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with users and persistent token tables"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        )
    ''')
    
    # Persistent tokens table (simulating Symfony's PersistentToken storage)
    # This stores: series (unique identifier), token_value, username, user_class, last_used
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS persistent_tokens (
            series TEXT PRIMARY KEY,
            token_value TEXT NOT NULL,
            username TEXT NOT NULL,
            user_class TEXT NOT NULL,
            last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expiry TIMESTAMP NOT NULL
        )
    ''')
    
    # Create test users
    users_data = [
        ('guest', hash_password('guest123'), 'user'),
        ('admin', hash_password(secrets.token_hex(32)), 'admin'),  # Admin has unknown password
        ('alice', hash_password('alice123'), 'user'),
    ]
    
    for username, password_hash, role in users_data:
        try:
            cursor.execute(
                'INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)',
                (username, password_hash, role)
            )
        except sqlite3.IntegrityError:
            pass  # User already exists
    
    conn.commit()
    conn.close()

def hash_password(password):
    """Simple password hashing"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, password_hash):
    """Verify password against hash"""
    return hash_password(password) == password_hash

def generate_series():
    """Generate a unique series identifier for remember-me token"""
    return secrets.token_urlsafe(32)

def generate_token():
    """Generate a random token value"""
    return secrets.token_urlsafe(32)

def create_remember_me_token(username):
    """
    Create a persistent remember-me token for a user.
    Returns the cookie value in format: Class:UserIdentifier:Expiry:Series:Token
    """
    series = generate_series()
    token_value = generate_token()
    expiry = datetime.now() + timedelta(days=30)
    user_class = "App\\Entity\\User"  # Simulating Symfony's user class
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO persistent_tokens (series, token_value, username, user_class, expiry)
        VALUES (?, ?, ?, ?, ?)
    ''', (series, token_value, username, user_class, expiry))
    conn.commit()
    conn.close()
    
    # Cookie format: Class:UserIdentifier:Expiry:Series:Token (base64 encoded)
    expiry_timestamp = int(expiry.timestamp())
    cookie_parts = f"{user_class}:{username}:{expiry_timestamp}:{series}:{token_value}"
    return base64.b64encode(cookie_parts.encode()).decode()

def consume_remember_me_cookie(cookie_value):
    """
    VULNERABLE: Consume a remember-me cookie and return the authenticated user.
    
    This implementation has the same vulnerability as CVE-2024-51996:
    - It loads the persistent token from storage using the series
    - It validates that the token value matches
    - BUT it does NOT check that the username in the cookie matches the username 
      stored in the database for that token!
    
    This allows an attacker to:
    1. Login as a regular user (e.g., 'guest') with remember-me enabled
    2. Capture the remember-me cookie
    3. Modify the username in the cookie to 'admin' 
    4. Re-encode and submit the cookie
    5. Get authenticated as 'admin'
    """
    try:
        # Decode the cookie
        decoded = base64.b64decode(cookie_value).decode()
        parts = decoded.split(':')
        
        if len(parts) != 5:
            logging.debug("Invalid cookie format - wrong number of parts")
            return None
            
        user_class, user_identifier, expiry, series, token = parts
        
        logging.debug(f"Cookie parsed - user_class: {user_class}, user_identifier: {user_identifier}, series: {series[:10]}...")
        
        # Load the persistent token by series
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT series, token_value, username, user_class, expiry 
            FROM persistent_tokens 
            WHERE series = ?
        ''', (series,))
        
        stored_token = cursor.fetchone()
        
        if not stored_token:
            logging.debug("No token found for series")
            conn.close()
            return None
        
        # Check if token has expired
        stored_expiry = datetime.fromisoformat(stored_token['expiry'])
        if datetime.now() > stored_expiry:
            logging.debug("Token has expired")
            cursor.execute('DELETE FROM persistent_tokens WHERE series = ?', (series,))
            conn.commit()
            conn.close()
            return None
        
        # Validate the token value
        if token != stored_token['token_value']:
            logging.debug("Token value mismatch")
            # In a real system, this would indicate token theft and clear all tokens
            cursor.execute('DELETE FROM persistent_tokens WHERE series = ?', (series,))
            conn.commit()
            conn.close()
            return None
        
        # VULNERABILITY: We do NOT check that user_identifier matches stored_token['username']!
        # The fix would be:
        # if user_identifier != stored_token['username']:
        #     logging.debug("Username mismatch between cookie and stored token")
        #     return None
        
        # Update last used timestamp and rotate token
        new_token = generate_token()
        cursor.execute('''
            UPDATE persistent_tokens 
            SET token_value = ?, last_used = CURRENT_TIMESTAMP 
            WHERE series = ?
        ''', (new_token, series))
        conn.commit()
        conn.close()
        
        logging.info(f"Remember-me authentication successful for: {user_identifier}")
        
        # Return the user identifier from the COOKIE (not from the stored token!)
        # This is the vulnerability - we trust the username from the cookie
        return user_identifier
        
    except Exception as e:
        logging.error(f"Error consuming remember-me cookie: {e}")
        return None

def get_user_by_username(username):
    """Get user from database by username"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    return user

# Initialize database on startup
init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    remember_me = request.form.get('remember_me', False)
    
    user = get_user_by_username(username)
    
    if user and verify_password(password, user['password_hash']):
        resp = make_response(redirect(url_for('dashboard')))
        
        # Set session cookie (simple implementation)
        session_token = secrets.token_urlsafe(32)
        resp.set_cookie('session_token', session_token, httponly=True)
        resp.set_cookie('session_user', username, httponly=True)
        
        # If remember-me is checked, create persistent token
        if remember_me:
            remember_me_cookie = create_remember_me_token(username)
            resp.set_cookie('REMEMBERME', remember_me_cookie, max_age=30*24*60*60, httponly=True)
            logging.info(f"Created remember-me token for user: {username}")
        
        return resp
    
    return render_template('index.html', error='Invalid username or password')

@app.route('/logout')
def logout():
    resp = make_response(redirect(url_for('index')))
    resp.delete_cookie('session_token')
    resp.delete_cookie('session_user')
    resp.delete_cookie('REMEMBERME')
    return resp

@app.route('/dashboard')
def dashboard():
    """Main dashboard - accessible to authenticated users"""
    username = None
    
    # First check session cookies
    session_user = request.cookies.get('session_user')
    session_token = request.cookies.get('session_token')
    
    if session_user and session_token:
        username = session_user
    else:
        # Try remember-me authentication
        remember_me_cookie = request.cookies.get('REMEMBERME')
        if remember_me_cookie:
            username = consume_remember_me_cookie(remember_me_cookie)
    
    if not username:
        return redirect(url_for('index'))
    
    user = get_user_by_username(username)
    if not user:
        return redirect(url_for('index'))
    
    return render_template('dashboard.html', username=username, role=user['role'])

@app.route('/admin')
def admin_panel():
    """Admin panel - only accessible to admin users"""
    username = None
    
    # First check session cookies
    session_user = request.cookies.get('session_user')
    session_token = request.cookies.get('session_token')
    
    if session_user and session_token:
        username = session_user
    else:
        # Try remember-me authentication
        remember_me_cookie = request.cookies.get('REMEMBERME')
        if remember_me_cookie:
            username = consume_remember_me_cookie(remember_me_cookie)
    
    if not username:
        return redirect(url_for('index'))
    
    user = get_user_by_username(username)
    if not user:
        return redirect(url_for('index'))
    
    # Check if user is admin
    if user['role'] != 'admin':
        return render_template('error.html', error='Access Denied: Admin privileges required'), 403
    
    # Admin can see the flag
    try:
        with open('/flag.txt', 'r') as f:
            flag = f.read().strip()
    except:
        flag = 'FLAG{error_reading_flag}'
    
    return render_template('admin.html', username=username, flag=flag)

@app.route('/api/user')
def api_user():
    """API endpoint to get current user info"""
    username = None
    
    session_user = request.cookies.get('session_user')
    session_token = request.cookies.get('session_token')
    
    if session_user and session_token:
        username = session_user
    else:
        remember_me_cookie = request.cookies.get('REMEMBERME')
        if remember_me_cookie:
            username = consume_remember_me_cookie(remember_me_cookie)
    
    if not username:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = get_user_by_username(username)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'username': user['username'],
        'role': user['role']
    })

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8000)
