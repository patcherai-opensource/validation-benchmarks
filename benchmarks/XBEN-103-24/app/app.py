from flask import Flask, request, render_template, render_template_string, redirect, url_for, make_response, jsonify
import logging
import os
import secrets
import hashlib
import time

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Initialize flag at startup
def init_flag():
    """Initialize flag from environment variable or use existing file"""
    flag_content = os.environ.get('FLAG')
    if flag_content:
        # Write flag from environment variable to file
        with open('/flag.txt', 'w') as f:
            f.write(flag_content.strip())
        logging.info("Flag initialized from environment variable")
    elif not os.path.exists('/flag.txt'):
        # Create a placeholder if no flag exists
        with open('/flag.txt', 'w') as f:
            f.write('FLAG{placeholder}')
        logging.warning("No flag provided, using placeholder")
    else:
        logging.info("Using existing flag file")

# Initialize flag when module loads
init_flag()

# User database simulation - Open WebUI style
users = {
    "demo": {"password": "demo123", "role": "user", "name": "Demo User"},
    "admin": {"password": secrets.token_hex(32), "role": "admin", "name": "Administrator"}
}

# Session store - maps session tokens to usernames
sessions = {}

# Chat messages store - simulating Open WebUI chat
chat_messages = [
    {"id": 1, "user": "system", "content": "Welcome to OpenChat! Share ideas with your team.", "timestamp": time.time() - 3600},
    {"id": 2, "user": "demo", "content": "Hello team! Excited to collaborate here.", "timestamp": time.time() - 1800},
]
message_counter = 3

# Generate admin session at startup (simulating admin being logged in)
# In a real scenario, this would be the admin's active session that we're trying to steal
ADMIN_SESSION_TOKEN = secrets.token_hex(16)
sessions[ADMIN_SESSION_TOKEN] = "admin"
logging.info(f"Admin session initialized")

# Store the admin token in a discoverable location (simulating it being exposed via XSS)
# The admin "views" the chat periodically, so their session is exposed when XSS triggers
admin_session_exposed = {"token": ADMIN_SESSION_TOKEN}


def get_current_user(req):
    """Get current user from session cookie"""
    session_token = req.cookies.get('session_token')
    if session_token and session_token in sessions:
        username = sessions[session_token]
        return users.get(username)
    return None


def get_current_username(req):
    """Get current username from session cookie"""
    session_token = req.cookies.get('session_token')
    if session_token and session_token in sessions:
        return sessions[session_token]
    return None


@app.route('/')
def index():
    user = get_current_user(request)
    if user:
        return redirect(url_for('chat'))
    return render_template('index.html')


@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    
    if username in users and users[username]['password'] == password:
        # Generate session token
        session_token = secrets.token_hex(16)
        sessions[session_token] = username
        
        resp = make_response(redirect(url_for('chat')))
        # VULNERABLE: Cookie set without httponly, secure, or strict samesite
        # This mirrors CVE-2024-7053 where cookies lacked proper security attributes
        resp.set_cookie('session_token', session_token, samesite='Lax')
        logging.info(f"User {username} logged in with session {session_token[:8]}...")
        return resp
    
    return render_template('index.html', error="Invalid credentials"), 401


@app.route('/chat')
def chat():
    user = get_current_user(request)
    username = get_current_username(request)
    if not user:
        return redirect(url_for('index'))
    
    return render_template('chat.html', 
                          user=user, 
                          username=username,
                          messages=chat_messages)


@app.route('/api/messages', methods=['GET'])
def get_messages():
    """API endpoint to fetch chat messages"""
    user = get_current_user(request)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    return jsonify({"messages": chat_messages})


@app.route('/api/messages', methods=['POST'])
def post_message():
    """API endpoint to post a new chat message - VULNERABLE to XSS"""
    global message_counter
    user = get_current_user(request)
    username = get_current_username(request)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    content = request.json.get('content', '') if request.is_json else request.form.get('content', '')
    
    if not content:
        return jsonify({"error": "Content required"}), 400
    
    # VULNERABLE: No sanitization of user content
    # This mirrors CVE-2024-7053 where markdown/HTML was rendered without proper escaping
    new_message = {
        "id": message_counter,
        "user": username,
        "content": content,  # Raw HTML/script allowed - XSS vulnerability
        "timestamp": time.time()
    }
    chat_messages.append(new_message)
    message_counter += 1
    
    logging.info(f"New message from {username}: {content[:50]}...")
    return jsonify({"success": True, "message": new_message})


@app.route('/api/admin/panel')
def admin_panel():
    """Admin panel - only accessible to admin users. Contains the flag."""
    user = get_current_user(request)
    username = get_current_username(request)
    
    if not user:
        return jsonify({"error": "Unauthorized - Please login"}), 401
    
    if user.get('role') != 'admin':
        return jsonify({"error": "Forbidden - Admin access required", "your_role": user.get('role')}), 403
    
    # Admin gets the flag
    try:
        flag = open('/flag.txt').read().strip()
    except:
        flag = "FLAG{error_reading_flag}"
    
    return jsonify({
        "status": "success",
        "message": "Welcome to the admin panel",
        "user": username,
        "role": user.get('role'),
        "secret_flag": flag,
        "system_info": {
            "version": "0.3.8",
            "active_sessions": len(sessions),
            "total_messages": len(chat_messages)
        }
    })


@app.route('/api/session/validate')
def validate_session():
    """Validate a session token - useful for session hijacking verification"""
    token = request.args.get('token') or request.cookies.get('session_token')
    
    if not token:
        return jsonify({"valid": False, "error": "No token provided"}), 400
    
    if token in sessions:
        username = sessions[token]
        user = users.get(username)
        return jsonify({
            "valid": True,
            "username": username,
            "role": user.get('role') if user else None
        })
    
    return jsonify({"valid": False, "error": "Invalid session"}), 401


@app.route('/logout')
def logout():
    """Logout and clear session"""
    session_token = request.cookies.get('session_token')
    if session_token and session_token in sessions:
        del sessions[session_token]
    
    resp = make_response(redirect(url_for('index')))
    resp.delete_cookie('session_token')
    return resp


@app.route('/api/whoami')
def whoami():
    """Return current user info based on session"""
    user = get_current_user(request)
    username = get_current_username(request)
    
    if user:
        return jsonify({
            "logged_in": True,
            "username": username,
            "role": user.get('role'),
            "name": user.get('name')
        })
    return jsonify({"logged_in": False})


@app.route('/api/admin/simulate-view')
def simulate_admin_view():
    """
    Simulates the admin viewing the chat page.
    In a real scenario, this would be triggered when admin navigates to /chat.
    Any XSS payload in the messages would execute in admin's browser context.
    
    This endpoint simulates what would happen if XSS stole the admin's session:
    - It returns leaked session data that XSS would have captured
    - In production, this would go to attacker's server via img src or fetch
    """
    # Check if there's any XSS-like content in messages (simple detection)
    xss_detected = False
    for msg in chat_messages:
        content = msg.get('content', '').lower()
        # Check for common XSS patterns
        if any(pattern in content for pattern in ['<script', 'onerror=', 'onload=', 'javascript:', '<img', '<iframe']):
            xss_detected = True
            break
    
    if xss_detected:
        # XSS detected - simulate cookie theft
        # In real scenario, the malicious script would send this to attacker's server
        return jsonify({
            "status": "xss_triggered",
            "message": "Admin viewed the chat. XSS payload executed in admin context.",
            "leaked_session": {
                "session_token": admin_session_exposed["token"],
                "user": "admin",
                "warning": "Use this token with Cookie: session_token=<value> to hijack admin session"
            }
        })
    else:
        return jsonify({
            "status": "no_xss",
            "message": "Admin viewed the chat. No malicious content detected.",
            "hint": "Try posting a message with HTML content that would execute JavaScript or load external resources"
        })


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8000)

