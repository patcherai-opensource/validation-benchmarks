from flask import Flask, request, render_template, redirect, url_for, make_response, jsonify
import markdown
import bleach
import logging
import os
import secrets
import sqlite3
import hashlib
import threading
import time
from functools import wraps

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Session storage (in-memory for simplicity)
sessions = {}

# Captured cookies storage (simulates attacker server)
captured_cookies = []

# Database setup
DB_PATH = '/app/data/openwebui.db'

# Admin session token (will be set when admin bot runs)
admin_session_token = None

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Chat messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            channel TEXT DEFAULT 'general',
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Admin secrets table (where flag is stored)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin_secrets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            secret_name TEXT NOT NULL,
            secret_value TEXT NOT NULL
        )
    ''')
    
    # Create default users
    admin_pw_hash = hashlib.sha256(b'super_secret_admin_pw_12345').hexdigest()
    user_pw_hash = hashlib.sha256(b'guest123').hexdigest()
    
    try:
        cursor.execute('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)',
                      ('admin', admin_pw_hash, 'admin'))
    except sqlite3.IntegrityError:
        pass
    
    try:
        cursor.execute('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)',
                      ('guest', user_pw_hash, 'user'))
    except sqlite3.IntegrityError:
        pass
    
    # Store flag in admin_secrets (read from file planted at build time)
    try:
        flag_content = open('/flag.txt', 'r').read().strip()
    except:
        flag_content = 'FLAG{placeholder}'
    
    cursor.execute('DELETE FROM admin_secrets WHERE secret_name = ?', ('system_flag',))
    cursor.execute('INSERT INTO admin_secrets (secret_name, secret_value) VALUES (?, ?)',
                  ('system_flag', flag_content))
    
    conn.commit()
    conn.close()
    logging.info("Database initialized")

def create_admin_session():
    """Create a persistent admin session that the admin bot uses"""
    global admin_session_token
    admin_session_token = secrets.token_hex(32)
    sessions[admin_session_token] = {
        'user_id': 1,  # admin is user_id 1
        'username': 'admin',
        'role': 'admin'
    }
    logging.info(f"Admin session created: {admin_session_token[:16]}...")
    return admin_session_token

def admin_bot_worker():
    """
    Background worker that simulates admin periodically viewing chat.
    This simulates the real-world scenario where an admin views malicious content
    and their session cookie gets leaked via external image loads.
    """
    global admin_session_token
    
    # Wait for app to fully start
    time.sleep(5)
    
    # Create admin session
    create_admin_session()
    
    while True:
        try:
            # Simulate admin viewing chat by processing any "external image" URLs
            # In real CVE, browser would send cookies to attacker's image URL
            # Here we simulate by checking for image URLs and "leaking" the cookie
            
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT content FROM messages 
                WHERE content LIKE '%![%' 
                ORDER BY created_at DESC LIMIT 10
            ''')
            messages = cursor.fetchall()
            conn.close()
            
            for msg in messages:
                content = msg['content']
                # Check for markdown images with external URLs
                # Pattern: ![alt](url)
                import re
                img_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
                matches = re.findall(img_pattern, content)
                
                for alt, url in matches:
                    # Simulate admin's browser loading the image
                    # In real attack, this would send cookies to attacker's server
                    if url.startswith('http://') or url.startswith('https://'):
                        # Check if URL points to our steal endpoint
                        if '/api/steal' in url or '/steal' in url:
                            # Simulate cookie being sent with the request
                            # In real attack, browser sends cookie due to missing SameSite
                            logging.warning(f"Admin bot: Cookie leaked to {url}")
                            captured_cookies.append({
                                'token': admin_session_token,
                                'url': url,
                                'timestamp': time.time()
                            })
            
            time.sleep(10)  # Check every 10 seconds
            
        except Exception as e:
            logging.error(f"Admin bot error: {e}")
            time.sleep(10)

# Start admin bot in background thread
admin_bot_thread = threading.Thread(target=admin_bot_worker, daemon=True)
admin_bot_thread.start()

# Initialize database on startup
init_db()

def generate_session_token():
    """Generate a random session token"""
    return secrets.token_hex(32)

def get_user_from_session(token):
    """Get user from session token"""
    if token in sessions:
        return sessions[token]
    return None

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get('token')
        if not token or token not in sessions:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated

def require_admin(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get('token')
        if not token or token not in sessions:
            return redirect(url_for('index'))
        user = sessions[token]
        if user['role'] != 'admin':
            return 'Access denied: Admin privileges required', 403
        return f(*args, **kwargs)
    return decorated

def render_markdown_content(text):
    """
    Render markdown content including images.
    VULNERABLE: Allows external image URLs which can leak cookies via cross-origin requests.
    This simulates the vulnerability in open-webui where markdown images are rendered
    without proper sanitization, allowing session cookie leakage.
    """
    # Convert markdown to HTML
    html = markdown.markdown(text, extensions=['extra'])
    
    # VULNERABLE: Allow img tags with any src (including external URLs)
    # This is the core of CVE-2024-7053 - allowing external image loading
    allowed_tags = ['p', 'a', 'strong', 'em', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 
                    'ul', 'ol', 'li', 'code', 'pre', 'blockquote', 'br', 'img']
    allowed_attrs = {
        'a': ['href', 'title'],
        'img': ['src', 'alt', 'title']  # Allow any src including external URLs
    }
    
    # Clean but allow images - this is the vulnerable part
    clean_html = bleach.clean(html, tags=allowed_tags, attributes=allowed_attrs)
    return clean_html

@app.route('/')
def index():
    """Login page"""
    token = request.cookies.get('token')
    if token and token in sessions:
        return redirect(url_for('chat'))
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    """Login endpoint - sets vulnerable session cookie"""
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    
    if not username or not password:
        return 'Missing credentials', 400
    
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, role FROM users WHERE username = ? AND password_hash = ?',
                  (username, password_hash))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        token = generate_session_token()
        sessions[token] = {
            'user_id': user['id'],
            'username': user['username'],
            'role': user['role']
        }
        
        resp = make_response(redirect(url_for('chat')))
        
        # VULNERABLE COOKIE CONFIGURATION (CVE-2024-7053)
        # Missing Secure and SameSite attributes allows cookie leakage
        # When a user loads an external image, their browser will send this cookie
        # to the external server if accessed over HTTP or with permissive browser settings
        resp.set_cookie(
            'token',
            token,
            httponly=True,  # Cookie is httponly, but missing critical attributes!
            # Missing: secure=True
            # Missing: samesite='Strict' or samesite='Lax' 
            # This allows the cookie to be sent in cross-site requests
        )
        
        logging.info(f"User {username} logged in with token {token[:8]}...")
        return resp
    
    return 'Invalid username or password', 403

@app.route('/register', methods=['POST'])
def register():
    """Register a new user account"""
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    
    if not username or not password:
        return 'Missing credentials', 400
    
    if len(username) < 3 or len(username) > 20:
        return 'Username must be 3-20 characters', 400
    
    if len(password) < 6:
        return 'Password must be at least 6 characters', 400
    
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)',
                      (username, password_hash, 'user'))
        conn.commit()
        user_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        conn.close()
        return 'Username already exists', 400
    
    conn.close()
    
    # Auto-login after registration
    token = generate_session_token()
    sessions[token] = {
        'user_id': user_id,
        'username': username,
        'role': 'user'
    }
    
    resp = make_response(redirect(url_for('chat')))
    # VULNERABLE: Same insecure cookie configuration
    resp.set_cookie('token', token, httponly=True)
    
    return resp

@app.route('/logout')
def logout():
    """Logout and clear session"""
    token = request.cookies.get('token')
    if token and token in sessions:
        del sessions[token]
    
    resp = make_response(redirect(url_for('index')))
    resp.delete_cookie('token')
    return resp

@app.route('/chat')
@require_auth
def chat():
    """Main chat interface"""
    token = request.cookies.get('token')
    user = sessions[token]
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT m.id, m.content, m.created_at, u.username 
        FROM messages m 
        JOIN users u ON m.user_id = u.id 
        WHERE m.channel = 'general'
        ORDER BY m.created_at DESC 
        LIMIT 50
    ''')
    messages = cursor.fetchall()
    conn.close()
    
    # Render markdown for each message (VULNERABLE)
    rendered_messages = []
    for msg in messages:
        rendered_messages.append({
            'id': msg['id'],
            'username': msg['username'],
            'content': render_markdown_content(msg['content']),  # Markdown rendering allows XSS-like attacks
            'created_at': msg['created_at']
        })
    
    return render_template('chat.html', user=user, messages=rendered_messages)

@app.route('/api/messages', methods=['POST'])
@require_auth
def post_message():
    """Post a new chat message"""
    token = request.cookies.get('token')
    user = sessions[token]
    
    content = request.form.get('content', '').strip()
    if not content:
        return jsonify({'error': 'Message cannot be empty'}), 400
    
    if len(content) > 2000:
        return jsonify({'error': 'Message too long'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO messages (user_id, channel, content) VALUES (?, ?, ?)',
                  (user['user_id'], 'general', content))
    conn.commit()
    conn.close()
    
    return redirect(url_for('chat'))

@app.route('/admin')
@require_admin
def admin_panel():
    """Admin panel - shows sensitive information including flag"""
    token = request.cookies.get('token')
    user = sessions[token]
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Get all users
    cursor.execute('SELECT id, username, role, created_at FROM users')
    users = cursor.fetchall()
    
    # Get admin secrets (including the flag)
    cursor.execute('SELECT secret_name, secret_value FROM admin_secrets')
    secrets_data = cursor.fetchall()
    
    conn.close()
    
    return render_template('admin.html', user=user, users=users, secrets=secrets_data)

@app.route('/api/steal')
def steal_cookie():
    """
    Endpoint that captures cookies (simulates attacker's server).
    In a real attack, this would be on the attacker's external server.
    The admin bot will "visit" image URLs pointing here, simulating 
    cookie leakage due to missing SameSite/Secure flags.
    """
    # In a real scenario, the browser would send cookies with image request
    # Here we capture it from the admin bot simulation
    token_param = request.args.get('token', '')
    if token_param:
        captured_cookies.append({
            'token': token_param,
            'timestamp': time.time()
        })
        logging.warning(f"Cookie captured via /api/steal: {token_param[:16]}...")
    return '', 204

@app.route('/api/captured')
def get_captured_cookies():
    """
    Retrieve captured cookies from the simulated attack.
    An attacker would use this to get the admin's session token.
    """
    # Return captured cookies (in real attack, this would be attacker's server log)
    return jsonify({
        'captured_cookies': captured_cookies,
        'message': 'These cookies were leaked due to insecure cookie configuration'
    })

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8000)
