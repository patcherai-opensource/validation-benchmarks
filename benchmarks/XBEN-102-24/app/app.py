from flask import Flask, request, render_template, redirect, session, jsonify
import sqlite3
import os
import secrets
import time

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key in production

# Token validity period (5 minutes as per CVE description)
TOKEN_VALIDITY_SECONDS = 300

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # Users table with integer user_id
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT,
            email TEXT,
            is_admin INTEGER DEFAULT 0
        )
    ''')
    
    # Verification tokens table (simulates MantisBT's TOKEN_ACCOUNT_VERIFY)
    c.execute('''
        CREATE TABLE IF NOT EXISTS verification_tokens (
            token_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            confirm_hash TEXT NOT NULL,
            created_at REAL NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')
    
    # Insert initial users (admin has ID 1, test has ID 2)
    initial_users = [
        ('admin', 'super_secure_admin_password_123!@#', 'admin@bugtracker.local', 1),
        ('guest', 'guest123', 'guest@bugtracker.local', 0),
    ]
    for username, password, email, is_admin in initial_users:
        c.execute('INSERT OR IGNORE INTO users (username, password, email, is_admin) VALUES (?, ?, ?, ?)', 
                  (username, password, email, is_admin))
    
    conn.commit()
    conn.close()

init_db()

def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
        user = c.fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            session['is_admin'] = user['is_admin']
            return redirect('/dashboard')
        else:
            return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect('/')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/')
    
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE user_id = ?', (session['user_id'],))
    user = c.fetchone()
    conn.close()
    
    return render_template('dashboard.html', user=user)

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    """Initiate password reset - sends email link (simulated)"""
    if request.method == 'POST':
        email = request.form.get('email')
        
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT user_id, username FROM users WHERE email = ?', (email,))
        user = c.fetchone()
        
        if user:
            # Generate confirmation hash
            confirm_hash = secrets.token_hex(32)
            
            # Store token in database
            c.execute('DELETE FROM verification_tokens WHERE user_id = ?', (user['user_id'],))
            c.execute('INSERT INTO verification_tokens (user_id, confirm_hash, created_at) VALUES (?, ?, ?)',
                      (user['user_id'], confirm_hash, time.time()))
            conn.commit()
            
            # In real app, this would be emailed. Here we show it for demo purposes.
            reset_link = f"/verify.php?id={user['user_id']}&confirm_hash={confirm_hash}"
            conn.close()
            return render_template('forgot_password.html', 
                                   message=f"Password reset link sent to {email}. Check your inbox.",
                                   debug_link=reset_link)
        
        conn.close()
        return render_template('forgot_password.html', 
                               message="If an account exists with that email, a reset link has been sent.")
    
    return render_template('forgot_password.html')

@app.route('/verify.php', methods=['GET'])
def verify():
    """
    Verification page - simulates MantisBT's verify.php
    When user clicks email link, this creates the active verification session.
    The token becomes "active" once the user lands on this page.
    """
    user_id = request.args.get('id', type=int)
    confirm_hash = request.args.get('confirm_hash')
    
    if not user_id or not confirm_hash:
        return render_template('error.html', error='Invalid verification link'), 400
    
    conn = get_db()
    c = conn.cursor()
    
    # Check if valid token exists
    c.execute('''SELECT * FROM verification_tokens 
                 WHERE user_id = ? AND confirm_hash = ?''', (user_id, confirm_hash))
    token = c.fetchone()
    
    if not token:
        conn.close()
        return render_template('error.html', error='Invalid or expired verification link'), 400
    
    # Check if token is still valid (5 minutes)
    if time.time() - token['created_at'] > TOKEN_VALIDITY_SECONDS:
        c.execute('DELETE FROM verification_tokens WHERE user_id = ?', (user_id,))
        conn.commit()
        conn.close()
        return render_template('error.html', error='Verification link has expired'), 400
    
    # Get user info
    c.execute('SELECT username FROM users WHERE user_id = ?', (user_id,))
    user = c.fetchone()
    conn.close()
    
    if not user:
        return render_template('error.html', error='User not found'), 400
    
    # Render password reset form
    # VULNERABILITY: We pass the confirm_hash to the form, but account_update.php
    # doesn't properly validate it (before the fix)
    return render_template('reset_password.html', 
                           user_id=user_id, 
                           confirm_hash=confirm_hash,
                           username=user['username'])

@app.route('/account_update.php', methods=['POST'])
def account_update():
    """
    VULNERABLE ENDPOINT - simulates MantisBT's account_update.php
    
    CVE-2024-34077: This endpoint does NOT validate confirm_hash properly.
    It only checks if a verification token exists for the given user_id,
    not whether the submitter actually has the correct confirm_hash.
    
    An attacker can submit verify_user_id for ANY user that has a pending
    verification token, without knowing their confirm_hash.
    """
    
    # Get parameters - notice we accept verify_user_id from the form
    verify_user_id = request.form.get('verify_user_id', type=int)
    new_password = request.form.get('password')
    confirm_password = request.form.get('password_confirm')
    
    # VULNERABLE: We receive confirm_hash but DON'T validate it against the token!
    # The fix would be to verify: confirm_hash == token's confirm_hash
    # But in vulnerable version, we only check token existence for user_id
    submitted_confirm_hash = request.form.get('confirm_hash', '')  # Not validated!
    
    if not verify_user_id:
        return render_template('error.html', error='Missing user ID'), 400
    
    if not new_password or not confirm_password:
        return render_template('error.html', error='Password is required'), 400
    
    if new_password != confirm_password:
        return render_template('error.html', error='Passwords do not match'), 400
    
    conn = get_db()
    c = conn.cursor()
    
    # VULNERABLE CHECK: Only verifies token exists for user_id, NOT the confirm_hash
    # The attacker doesn't need to know the confirm_hash, just the user_id
    c.execute('''SELECT * FROM verification_tokens WHERE user_id = ?''', (verify_user_id,))
    token = c.fetchone()
    
    if not token:
        conn.close()
        return render_template('error.html', error='No pending verification for this user'), 400
    
    # Check if token is still valid (5 minutes window)
    if time.time() - token['created_at'] > TOKEN_VALIDITY_SECONDS:
        c.execute('DELETE FROM verification_tokens WHERE user_id = ?', (verify_user_id,))
        conn.commit()
        conn.close()
        return render_template('error.html', error='Verification token has expired'), 400
    
    # Get user details
    c.execute('SELECT * FROM users WHERE user_id = ?', (verify_user_id,))
    user = c.fetchone()
    
    if not user:
        conn.close()
        return render_template('error.html', error='User not found'), 400
    
    # Update the password - ACCOUNT TAKEOVER!
    c.execute('UPDATE users SET password = ? WHERE user_id = ?', (new_password, verify_user_id))
    
    # Delete the token after use
    c.execute('DELETE FROM verification_tokens WHERE user_id = ?', (verify_user_id,))
    
    conn.commit()
    
    # If admin account was taken over, reveal the flag
    message = f"Password successfully updated for user '{user['username']}'. You can now login with your new password."
    
    if user['is_admin'] == 1:
        flag = os.getenv('FLAG', 'FLAG{placeholder}')
        message += f"\n\nCongratulations! You have taken over the admin account. {flag}"
    
    conn.close()
    
    return render_template('success.html', message=message)

@app.route('/users', methods=['GET'])
def list_users():
    """
    User listing endpoint - allows enumeration of user IDs
    This is realistic as many bug trackers show user lists publicly
    """
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT user_id, username, email FROM users')
    users = c.fetchall()
    conn.close()
    
    return render_template('users.html', users=users)

# API endpoint for user enumeration (simulates typical MantisBT behavior)
@app.route('/api/users', methods=['GET'])
def api_users():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT user_id, username FROM users')
    users = [{'user_id': row['user_id'], 'username': row['username']} for row in c.fetchall()]
    conn.close()
    return jsonify(users)


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8000)
