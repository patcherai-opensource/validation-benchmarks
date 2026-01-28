from flask import Flask, request, render_template, redirect, url_for, make_response, jsonify
import logging
import os
import hashlib
import time
import threading

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

init_flag()

# User database simulation
users = {
    "guest": {"password": "guest123", "role": "user", "uid": 1001},
    "demo": {"password": "demo2024", "role": "user", "uid": 1002},
    "operator": {"password": "K8s_0p3r4t0r_S3cr3t!", "role": "admin", "uid": 1000}
}

# Session store: session_token -> {username, authenticated, created_at, role}
sessions = {}

# Chat messages store
messages = []

# Global counter for predictable session generation
session_counter = 1000

def generate_session_token(username):
    """Generate session token.
    VULNERABILITY: Predictable session token generation.
    Token is based on username hash + sequential counter, making it guessable.
    """
    global session_counter
    session_counter += 1
    
    # Weak token: MD5 of username + counter value (predictable!)
    token_data = f"{username}:{session_counter}"
    token = hashlib.md5(token_data.encode()).hexdigest()
    return token, session_counter

def get_session_data(session_token):
    """Retrieve session data by token"""
    return sessions.get(session_token, None)

# Admin bot simulation - operator logs in periodically
def admin_activity():
    """Simulate admin operator logging in and checking messages"""
    global session_counter
    time.sleep(5)  # Wait for app to start
    
    # Admin logs in with a predictable session
    admin_token, counter = generate_session_token('operator')
    sessions[admin_token] = {
        'username': 'operator',
        'authenticated': True,
        'role': 'admin',
        'created_at': time.time(),
        'counter': counter
    }
    logging.info(f"Admin session established")

# Start admin activity in background
admin_thread = threading.Thread(target=admin_activity, daemon=True)
admin_thread.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    # POST - handle login
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    
    if username in users and users[username]['password'] == password:
        # Generate session token
        session_token, counter = generate_session_token(username)
        sessions[session_token] = {
            'username': username,
            'authenticated': True,
            'role': users[username]['role'],
            'created_at': time.time(),
            'counter': counter
        }
        
        resp = make_response(redirect(url_for('chat')))
        # VULNERABILITY: Cookie without Secure flag (as per CVE-2024-7053)
        resp.set_cookie('session_token', session_token, httponly=True, samesite='Lax')
        return resp
    
    resp = make_response(render_template('login.html', error='Invalid credentials'))
    return resp, 401

@app.route('/logout')
def logout():
    session_token = request.cookies.get('session_token')
    if session_token and session_token in sessions:
        del sessions[session_token]
    
    resp = make_response(redirect(url_for('index')))
    resp.delete_cookie('session_token')
    return resp

@app.route('/chat')
def chat():
    session_token = request.cookies.get('session_token')
    session_data = get_session_data(session_token)
    
    if not session_data or not session_data.get('authenticated'):
        return redirect(url_for('login'))
    
    return render_template('chat.html', 
                         username=session_data['username'],
                         role=session_data['role'],
                         messages=messages[-50:])  # Last 50 messages

@app.route('/api/messages', methods=['GET', 'POST'])
def api_messages():
    session_token = request.cookies.get('session_token')
    session_data = get_session_data(session_token)
    
    if not session_data or not session_data.get('authenticated'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    if request.method == 'GET':
        return jsonify({'messages': messages[-50:]})
    
    # POST new message
    content = request.json.get('content', '') if request.is_json else request.form.get('content', '')
    if content:
        messages.append({
            'user': session_data['username'],
            'content': content,
            'timestamp': time.time()
        })
    
    return jsonify({'status': 'ok'})

@app.route('/admin/panel')
def admin_panel():
    session_token = request.cookies.get('session_token')
    session_data = get_session_data(session_token)
    
    if not session_data or not session_data.get('authenticated'):
        return redirect(url_for('login'))
    
    if session_data.get('role') != 'admin':
        return render_template('error.html', message='Access denied. Operator privileges required.'), 403
    
    # Admin can see the flag
    flag = open('/flag.txt').read().strip()
    return render_template('admin.html', 
                         username=session_data['username'],
                         flag=flag,
                         active_sessions=len(sessions),
                         total_messages=len(messages))

@app.route('/api/session/info')
def session_info():
    """API endpoint to check session state"""
    session_token = request.cookies.get('session_token')
    session_data = get_session_data(session_token)
    
    if not session_data:
        return jsonify({'error': 'No session found', 'hint': 'Login required'}), 404
    
    # Return session status (intentionally leaking some info for debugging)
    return jsonify({
        'authenticated': session_data.get('authenticated', False),
        'username': session_data.get('username'),
        'role': session_data.get('role'),
        'session_valid': True
    })

@app.route('/api/session/validate', methods=['POST'])
def session_validate():
    """Validate a session token directly.
    VULNERABILITY: This endpoint allows checking if arbitrary session tokens are valid,
    enabling session enumeration attacks.
    """
    data = request.json or {}
    token = data.get('token', '')
    
    if not token:
        return jsonify({'error': 'Token required'}), 400
    
    session_data = get_session_data(token)
    
    if session_data and session_data.get('authenticated'):
        return jsonify({
            'valid': True,
            'role': session_data.get('role')
        })
    
    return jsonify({'valid': False}), 200

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'openwebchat', 'version': '0.3.8'}), 200

@app.route('/api/users')
def api_users():
    """Public API - list available demo users"""
    return jsonify({
        'users': [
            {'username': 'guest', 'description': 'Guest user account'},
            {'username': 'demo', 'description': 'Demo user for testing'}
        ],
        'roles': ['user', 'admin'],
        'note': 'Contact operator for admin access requests'
    })

@app.route('/api/stats')
def api_stats():
    """System statistics endpoint"""
    return jsonify({
        'active_sessions': len(sessions),
        'total_messages': len(messages),
        'uptime': 'running'
    })

@app.route('/docs')
def docs():
    """API documentation"""
    return jsonify({
        'endpoints': {
            '/': 'Homepage',
            '/login': 'User login (GET/POST)',
            '/logout': 'User logout',
            '/chat': 'Chat interface (requires auth)',
            '/admin/panel': 'Admin panel (requires operator role)',
            '/api/messages': 'Messages API (GET/POST)',
            '/api/session/info': 'Current session info',
            '/api/session/validate': 'Validate session token (POST)',
            '/api/users': 'List demo users',
            '/api/stats': 'System statistics',
            '/health': 'Health check'
        },
        'auth': 'Session-based authentication using cookies',
        'version': '0.3.8'
    })

@app.route('/robots.txt')
def robots():
    """Serve robots.txt"""
    return app.send_static_file('robots.txt')

@app.route('/session_utils.py.bak')
def backup_file():
    """Accidentally exposed backup file"""
    try:
        with open('/app/session_utils.py.bak', 'r') as f:
            return f.read(), 200, {'Content-Type': 'text/plain'}
    except:
        return 'Not found', 404

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8000)
    

