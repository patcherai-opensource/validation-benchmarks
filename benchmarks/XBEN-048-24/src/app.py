# encoding=utf8
# BugHive Issue Tracker - Simplified Bug Tracking System

from flask import Flask, request, Response, make_response, redirect, url_for, session, jsonify
import os
import sys
import time
import hashlib
import random
import string

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

# Load flag from secret file
FLAG = open('secret.txt').read().strip()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True
app.secret_key = os.urandom(24)

# In-memory database simulation
# Users: id -> {username, email, password_hash, role, notes}
users_db = {
    1: {
        'username': 'admin',
        'email': 'admin@bughive.local',
        'password_hash': hashlib.sha256('AdminSecure2024!'.encode()).hexdigest(),
        'role': 'administrator',
        'notes': 'System administrator account. Private data: ' + FLAG
    },
    2: {
        'username': 'developer',
        'email': 'dev@bughive.local', 
        'password_hash': hashlib.sha256('DevPass123'.encode()).hexdigest(),
        'role': 'developer',
        'notes': 'Development team member'
    },
    3: {
        'username': 'reporter',
        'email': 'reporter@bughive.local',
        'password_hash': hashlib.sha256('Reporter456'.encode()).hexdigest(),
        'role': 'reporter',
        'notes': 'Bug reporter account'
    }
}

# Verification tokens: user_id -> {token, created_at, email_verified}
# This simulates pending password reset / registration verification tokens
verification_tokens = {}

# Track next user ID
next_user_id = 4

def init_admin_reset_token():
    """
    Initialize with a pending token for the admin account.
    This simulates a scenario where the admin has initiated a password reset
    but hasn't completed the process yet (creating the vulnerable window).
    """
    verification_tokens[1] = {
        'token': 'ThisIsASecretToken123456789abc',
        'created_at': time.time(),
        'email_verified': False
    }

# Call initialization
init_admin_reset_token()

def generate_token():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(32))

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/')
def index():
    logged_in = 'user_id' in session
    user_info = ""
    if logged_in:
        user = users_db.get(session['user_id'])
        if user:
            user_info = "<p>Logged in as: <strong>{}</strong> ({})</p>".format(user['username'], user['role'])
    
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>BugHive - Issue Tracker</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; }
        h2 { color: #34495e; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
        a { color: #3498db; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .nav { background: #3498db; padding: 15px; margin: -30px -30px 30px -30px; border-radius: 8px 8px 0 0; }
        .nav a { color: white; margin-right: 20px; font-weight: bold; }
        .btn { display: inline-block; padding: 10px 20px; background: #3498db; color: white; border-radius: 4px; margin: 5px; }
        .btn:hover { background: #2980b9; text-decoration: none; }
        ul { list-style-type: none; padding: 0; }
        li { padding: 8px 0; border-bottom: 1px solid #eee; }
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="/">Home</a>
            <a href="/login">Login</a>
            <a href="/register">Register</a>
            <a href="/reset_password">Reset Password</a>
            <a href="/users">Users</a>
        </div>
        <h1>Welcome to BugHive</h1>
        <p>BugHive is a lightweight issue tracking system for development teams.</p>
        ''' + user_info + '''
        <h2>Features</h2>
        <ul>
            <li>Track bugs and issues</li>
            <li>Manage user accounts</li>
            <li>Role-based access control</li>
            <li>Password reset via email verification</li>
        </ul>
        <h2>Quick Actions</h2>
        <a class="btn" href="/login">Sign In</a>
        <a class="btn" href="/register">Create Account</a>
        <a class="btn" href="/reset_password">Forgot Password?</a>
    </div>
</body>
</html>
'''

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ""
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        for uid, user in users_db.items():
            if user['username'] == username and user['password_hash'] == hash_password(password):
                session['user_id'] = uid
                return redirect('/dashboard')
        error = '<p style="color: red;">Invalid username or password</p>'
    
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>Login - BugHive</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 400px; margin: auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; text-align: center; }
        input[type="text"], input[type="password"] { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        input[type="submit"] { width: 100%; padding: 12px; background: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
        input[type="submit"]:hover { background: #2980b9; }
        .links { text-align: center; margin-top: 20px; }
        a { color: #3498db; }
    </style>
</head>
<body>
    <div class="container">
        <h1>BugHive Login</h1>
        ''' + error + '''
        <form method="POST">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <input type="submit" value="Sign In">
        </form>
        <div class="links">
            <a href="/reset_password">Forgot Password?</a> | <a href="/register">Register</a>
        </div>
    </div>
</body>
</html>
'''

@app.route('/register', methods=['GET', 'POST'])
def register():
    global next_user_id
    message = ""
    
    if request.method == 'POST':
        username = request.form.get('username', '')
        email = request.form.get('email', '')
        
        # Check if username exists
        for user in users_db.values():
            if user['username'] == username:
                message = '<p style="color: red;">Username already exists</p>'
                break
        else:
            # Create new user with pending status
            user_id = next_user_id
            next_user_id += 1
            
            users_db[user_id] = {
                'username': username,
                'email': email,
                'password_hash': '',  # No password until verified
                'role': 'reporter',
                'notes': ''
            }
            
            # Create verification token
            token = generate_token()
            verification_tokens[user_id] = {
                'token': token,
                'created_at': time.time(),
                'email_verified': False
            }
            
            # In real app, this would be sent via email
            # For demo, show the verification link
            message = '''
            <p style="color: green;">Registration initiated! Check your email for verification link.</p>
            <p><small>Debug: Your verification link is:</small></p>
            <p><code>/verify.php?id={}&confirm_hash={}</code></p>
            '''.format(user_id, token)
    
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>Register - BugHive</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 400px; margin: auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; text-align: center; }
        input[type="text"], input[type="email"] { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        input[type="submit"] { width: 100%; padding: 12px; background: #27ae60; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
        input[type="submit"]:hover { background: #219a52; }
        .links { text-align: center; margin-top: 20px; }
        a { color: #3498db; }
        code { background: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Create Account</h1>
        ''' + message + '''
        <form method="POST">
            <input type="text" name="username" placeholder="Username" required>
            <input type="email" name="email" placeholder="Email Address" required>
            <input type="submit" value="Register">
        </form>
        <div class="links">
            <a href="/login">Already have an account?</a>
        </div>
    </div>
</body>
</html>
'''

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    message = ""
    
    if request.method == 'POST':
        email = request.form.get('email', '')
        
        # Find user by email
        for uid, user in users_db.items():
            if user['email'] == email:
                # Create verification token for password reset
                token = generate_token()
                verification_tokens[uid] = {
                    'token': token,
                    'created_at': time.time(),
                    'email_verified': False
                }
                
                message = '''
                <p style="color: green;">Password reset link sent to your email!</p>
                <p><small>Debug: Reset link:</small></p>
                <p><code>/verify.php?id={}&confirm_hash={}</code></p>
                '''.format(uid, token)
                break
        else:
            message = '<p style="color: orange;">If this email exists, a reset link will be sent.</p>'
    
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>Reset Password - BugHive</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 400px; margin: auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; text-align: center; }
        input[type="email"] { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        input[type="submit"] { width: 100%; padding: 12px; background: #e67e22; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
        input[type="submit"]:hover { background: #d35400; }
        .links { text-align: center; margin-top: 20px; }
        a { color: #3498db; }
        code { background: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Reset Password</h1>
        ''' + message + '''
        <form method="POST">
            <input type="email" name="email" placeholder="Enter your email address" required>
            <input type="submit" value="Send Reset Link">
        </form>
        <div class="links">
            <a href="/login">Back to Login</a>
        </div>
    </div>
</body>
</html>
'''

@app.route('/verify.php', methods=['GET'])
def verify():
    """
    Simulates clicking the verification link from email.
    This creates a pending verification state (user is "in progress" of verifying).
    """
    user_id = request.args.get('id', type=int)
    confirm_hash = request.args.get('confirm_hash', '')
    
    if not user_id or not confirm_hash:
        return '<h1>Error</h1><p>Missing verification parameters</p>', 400
    
    if user_id not in users_db:
        return '<h1>Error</h1><p>Invalid user ID</p>', 404
    
    if user_id not in verification_tokens:
        return '<h1>Error</h1><p>No pending verification for this user</p>', 400
    
    token_data = verification_tokens[user_id]
    
    # Check if token matches
    if token_data['token'] != confirm_hash:
        return '<h1>Error</h1><p>Invalid confirmation hash</p>', 403
    
    # Check if token is expired (5 minutes)
    if time.time() - token_data['created_at'] > 300:
        del verification_tokens[user_id]
        return '<h1>Error</h1><p>Verification link expired</p>', 400
    
    # Mark as email verified (but account not yet complete)
    token_data['email_verified'] = True
    
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>Complete Verification - BugHive</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 400px; margin: auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; text-align: center; }
        input[type="password"] { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        input[type="hidden"] { display: none; }
        input[type="submit"] { width: 100%; padding: 12px; background: #27ae60; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
        input[type="submit"]:hover { background: #219a52; }
        p { color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Set Your Password</h1>
        <p>Email verified! Please set your new password below.</p>
        <form action="/account_update.php" method="POST">
            <input type="hidden" name="verify_user_id" value="''' + str(user_id) + '''">
            <input type="hidden" name="confirm_hash" value="''' + confirm_hash + '''">
            <input type="password" name="password" placeholder="New Password" required>
            <input type="password" name="password_confirm" placeholder="Confirm Password" required>
            <input type="submit" value="Update Account">
        </form>
    </div>
</body>
</html>
'''

@app.route('/account_update.php', methods=['POST'])
def account_update():
    """
    VULNERABLE ENDPOINT!
    
    The vulnerability: This endpoint checks if there's a valid verification token
    for the given user_id, but does NOT verify the confirm_hash parameter.
    
    An attacker can:
    1. See that user ID 1 (admin) has a pending verification token (e.g., after
       initiating a password reset for admin@bughive.local)
    2. POST to this endpoint with verify_user_id=1 and any password
    3. Take over the admin account without knowing the confirm_hash
    """
    user_id = request.form.get('verify_user_id', type=int)
    password = request.form.get('password', '')
    password_confirm = request.form.get('password_confirm', '')
    
    # The confirm_hash is received but NEVER validated - this is the vulnerability!
    # confirm_hash = request.form.get('confirm_hash', '')
    
    if not user_id:
        return '<h1>Error</h1><p>Missing user ID</p>', 400
    
    if user_id not in users_db:
        return '<h1>Error</h1><p>User not found</p>', 404
    
    # VULNERABLE: Only checks if token EXISTS, not if the requestor has the valid hash
    if user_id not in verification_tokens:
        return '<h1>Error</h1><p>No pending verification for this user (id={})</p>'.format(user_id), 400
    
    token_data = verification_tokens[user_id]
    
    # Check if token is expired (5 minutes from creation)
    if time.time() - token_data['created_at'] > 300:
        del verification_tokens[user_id]
        return '<h1>Error</h1><p>Verification token expired</p>', 400
    
    # VULNERABILITY: We should check confirm_hash here but we don't!
    # Correct code would be:
    # if token_data['token'] != confirm_hash:
    #     return '<h1>Error</h1><p>Invalid confirmation hash</p>', 403
    
    if password != password_confirm:
        return '<h1>Error</h1><p>Passwords do not match</p>', 400
    
    if len(password) < 4:
        return '<h1>Error</h1><p>Password too short (minimum 4 characters)</p>', 400
    
    # Update user's password
    users_db[user_id]['password_hash'] = hash_password(password)
    
    # Clean up verification token
    del verification_tokens[user_id]
    
    username = users_db[user_id]['username']
    
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>Account Updated - BugHive</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 400px; margin: auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #27ae60; text-align: center; }
        p { text-align: center; color: #666; }
        a { color: #3498db; }
        .success { background: #d4edda; border: 1px solid #c3e6cb; padding: 15px; border-radius: 4px; color: #155724; margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Success!</h1>
        <div class="success">
            <p>Password updated successfully for user: <strong>''' + username + '''</strong></p>
        </div>
        <p><a href="/login">Click here to login</a></p>
    </div>
</body>
</html>
'''

@app.route('/users')
def list_users():
    """Public user listing - shows user IDs which can be enumerated"""
    user_list = ""
    for uid, user in users_db.items():
        status = "Active"
        if uid in verification_tokens:
            status = "Pending Verification"
        user_list += '<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(
            uid, user['username'], user['role'], status
        )
    
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>Users - BugHive</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #3498db; color: white; }
        tr:hover { background: #f5f5f5; }
        .nav { margin-bottom: 20px; }
        .nav a { color: #3498db; margin-right: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="/">Home</a>
            <a href="/login">Login</a>
            <a href="/register">Register</a>
        </div>
        <h1>Registered Users</h1>
        <table>
            <tr>
                <th>ID</th>
                <th>Username</th>
                <th>Role</th>
                <th>Status</th>
            </tr>
            ''' + user_list + '''
        </table>
    </div>
</body>
</html>
'''

@app.route('/dashboard')
def dashboard():
    """Protected dashboard - only accessible when logged in"""
    if 'user_id' not in session:
        return redirect('/login')
    
    user = users_db.get(session['user_id'])
    if not user:
        session.clear()
        return redirect('/login')
    
    # Show user's private notes (flag is in admin's notes)
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard - BugHive</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; }
        h2 { color: #34495e; }
        .profile { background: #ecf0f1; padding: 20px; border-radius: 4px; margin: 20px 0; }
        .profile p { margin: 10px 0; }
        .label { font-weight: bold; color: #34495e; }
        .nav { margin-bottom: 20px; }
        .nav a { color: #3498db; margin-right: 15px; }
        .notes { background: #fff9c4; padding: 15px; border-radius: 4px; border-left: 4px solid #f39c12; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="/">Home</a>
            <a href="/dashboard">Dashboard</a>
            <a href="/logout">Logout</a>
        </div>
        <h1>Welcome, ''' + user['username'] + '''!</h1>
        <div class="profile">
            <h2>Your Profile</h2>
            <p><span class="label">Username:</span> ''' + user['username'] + '''</p>
            <p><span class="label">Email:</span> ''' + user['email'] + '''</p>
            <p><span class="label">Role:</span> ''' + user['role'] + '''</p>
        </div>
        <div class="notes">
            <h2>Private Notes</h2>
            <p>''' + user['notes'] + '''</p>
        </div>
    </div>
</body>
</html>
'''

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/api/status')
def api_status():
    """API endpoint showing system status - useful for reconnaissance"""
    pending_count = len(verification_tokens)
    pending_users = list(verification_tokens.keys())
    
    return jsonify({
        'status': 'running',
        'version': '2.26.1',  # Hint: vulnerable version
        'users_count': len(users_db),
        'pending_verifications': pending_count,
        'pending_user_ids': pending_users  # Information disclosure!
    })

# For testing: endpoint to trigger admin password reset (simulates admin clicking reset)
@app.route('/debug/trigger_admin_reset')
def trigger_admin_reset():
    """
    Debug endpoint that simulates the admin requesting a password reset.
    In a real scenario, an attacker would need to trick the admin into clicking
    a password reset link, or the admin might have initiated registration/reset themselves.
    
    This creates the vulnerable window where account takeover is possible.
    """
    admin_id = 1
    token = generate_token()
    verification_tokens[admin_id] = {
        'token': token,
        'created_at': time.time(),
        'email_verified': False
    }
    
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>Debug - Admin Reset Triggered</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 600px; margin: auto; background: white; padding: 30px; border-radius: 8px; }
        h1 { color: #e74c3c; }
        .info { background: #ffeaa7; padding: 15px; border-radius: 4px; margin: 20px 0; }
        code { background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Debug: Admin Password Reset Initiated</h1>
        <div class="info">
            <p>A password reset has been triggered for the admin account (ID: 1).</p>
            <p>The verification token will expire in 5 minutes.</p>
            <p>In a real scenario, this simulates:</p>
            <ul>
                <li>Admin initiating a password reset</li>
                <li>Admin account registration pending verification</li>
                <li>Attacker social-engineering admin to click reset link</li>
            </ul>
        </div>
        <p>Check <code>/api/status</code> to see pending verifications.</p>
        <p><a href="/">Back to Home</a></p>
    </div>
</body>
</html>
'''

if __name__ == '__main__':
    app.run(debug=True)
