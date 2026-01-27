from flask import Flask, request, render_template, redirect, session, jsonify
import sqlite3
import os
import secrets
import time

app = Flask(__name__)
app.secret_key = 'mantis_secret_key_2024'

# Token validity period in seconds 
# Extended significantly for CTF environment (original CVE was 5 minutes)
# In production this would be much shorter, but for the CTF we keep it long
TOKEN_VALIDITY_SECONDS = 86400  # 24 hours

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            email TEXT,
            realname TEXT,
            access_level INTEGER DEFAULT 25
        )
    ''')
    # Password reset tokens table (simulates MantisBT's token system)
    c.execute('''
        CREATE TABLE IF NOT EXISTS password_reset_tokens (
            user_id INTEGER,
            confirm_hash TEXT,
            created_at REAL,
            token_type TEXT DEFAULT 'ACCOUNT_VERIFY',
            pending INTEGER DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    # Insert initial users (admin has higher access level)
    initial_users = [
        ('administrator', 'Adm1n$ecure#2024!', 'admin@bugtracker.local', 'System Administrator', 90),
        ('reporter', 'reporter123', 'reporter@company.com', 'Bug Reporter', 25),
        ('developer', 'dev@2024', 'dev@company.com', 'Developer', 55)
    ]
    for user in initial_users:
        c.execute('INSERT OR IGNORE INTO users (username, password, email, realname, access_level) VALUES (?, ?, ?, ?, ?)', user)
    
    # Simulate a scenario where admin requested a password reset and clicked the verification link
    # but hasn't completed setting the new password yet.
    # This creates the vulnerable window exploited in CVE-2024-34077
    # The token's confirm_hash is secret, but the user_id (1) is known/enumerable
    admin_confirm_hash = secrets.token_hex(32)  # Random hash - attacker doesn't know this
    c.execute('''INSERT OR REPLACE INTO password_reset_tokens (user_id, confirm_hash, created_at, pending) 
                VALUES (1, ?, ?, 0)''', (admin_confirm_hash, time.time()))
    
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

@app.route('/login.php', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT id, username, realname, access_level FROM users WHERE username=? AND password=?', (username, password))
        user = c.fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['realname'] = user['realname']
            session['access_level'] = user['access_level']
            return redirect('/my_view.php')
        else:
            error = 'Invalid username or password'
    
    return render_template('login.html', error=error)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect('/')

@app.route('/my_view.php')
def my_view():
    if 'user_id' not in session:
        return redirect('/')
    
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],))
    user = c.fetchone()
    conn.close()
    
    # If admin account is accessed, show the flag
    flag_message = None
    if user and user['access_level'] >= 90:
        flag = os.getenv('FLAG', 'FLAG{placeholder}')
        flag_message = f"Administrator Access Granted: {flag}"
    
    return render_template('my_view.html', user=user, flag_message=flag_message)

@app.route('/lost_pwd.php', methods=['GET', 'POST'])
@app.route('/lost_password.php', methods=['GET', 'POST'])
def lost_password():
    message = None
    reset_info = None
    if request.method == 'POST':
        email = request.form.get('email', '')
        username = request.form.get('username', '')
        
        conn = get_db()
        c = conn.cursor()
        
        # Find user by email or username
        if email:
            c.execute('SELECT id, username, email FROM users WHERE email = ?', (email,))
        else:
            c.execute('SELECT id, username, email FROM users WHERE username = ?', (username,))
        
        user = c.fetchone()
        
        if user:
            # Generate confirmation hash
            confirm_hash = secrets.token_hex(32)
            
            # Create pending verification token
            c.execute('DELETE FROM password_reset_tokens WHERE user_id = ?', (user['id'],))
            c.execute('''INSERT INTO password_reset_tokens (user_id, confirm_hash, created_at, pending) 
                        VALUES (?, ?, ?, 1)''', (user['id'], confirm_hash, time.time()))
            conn.commit()
            
            # In a real app, this would be sent via email
            # For this CTF, we simulate that the email was "sent"
            message = f"Password reset instructions sent to {user['email']}"
            
            # Simulating the real-world scenario: the reset info is returned in response
            # (This is like email being sent - the attacker can see user_id but needs confirm_hash)
            reset_info = {
                'user_id': user['id'],
                'verification_link': f"/verify.php?id={user['id']}&confirm_hash={confirm_hash}"
            }
        else:
            message = "If that account exists, a password reset email has been sent."
        
        conn.close()
    
    return render_template('lost_password.html', message=message, reset_info=reset_info)

@app.route('/verify.php', methods=['GET'])
def verify():
    """
    Simulates the MantisBT verify.php endpoint.
    When user clicks the email link, this creates an active verification session.
    """
    user_id = request.args.get('id')
    confirm_hash = request.args.get('confirm_hash')
    
    if not user_id:
        return render_template('error.html', error='Missing user id parameter')
    
    conn = get_db()
    c = conn.cursor()
    
    # Check if valid token exists
    c.execute('''SELECT * FROM password_reset_tokens 
                WHERE user_id = ? AND confirm_hash = ? 
                AND (? - created_at) < ?''', 
             (user_id, confirm_hash, time.time(), TOKEN_VALIDITY_SECONDS))
    token = c.fetchone()
    
    if token:
        # Mark token as "being processed" - user has opened the link
        # This is the vulnerable window - token is now active but password not yet set
        c.execute('UPDATE password_reset_tokens SET pending = 0 WHERE user_id = ?', (user_id,))
        conn.commit()
        conn.close()
        
        # Show password reset form (token validated here)
        return render_template('verify.html', user_id=user_id, confirm_hash=confirm_hash)
    else:
        conn.close()
        return render_template('error.html', error='Invalid or expired verification link')

@app.route('/account_update.php', methods=['POST'])
def account_update():
    """
    VULNERABLE ENDPOINT - simulates CVE-2024-34077
    
    The vulnerability: This endpoint checks if a valid TOKEN_ACCOUNT_VERIFY exists
    for the given user_id, but it does NOT verify that the requester knows the 
    confirm_hash. An attacker can POST here with just the user_id during the
    5-minute window after the legitimate user opens their verification link.
    """
    verify_user_id = request.form.get('verify_user_id')
    new_password = request.form.get('password')
    password_confirm = request.form.get('password_confirm')
    realname = request.form.get('realname', '')
    email = request.form.get('email', '')
    
    # VULNERABLE: confirm_hash is received but NOT validated!
    confirm_hash = request.form.get('confirm_hash', '')  # Not actually checked
    
    if not verify_user_id:
        return render_template('error.html', error='Missing user id')
    
    if not new_password:
        return render_template('error.html', error='Password is required')
    
    if new_password != password_confirm:
        return render_template('error.html', error='Passwords do not match')
    
    conn = get_db()
    c = conn.cursor()
    
    # VULNERABILITY: Only checks if a token exists and is valid (within time window)
    # Does NOT verify the confirm_hash matches!
    c.execute('''SELECT * FROM password_reset_tokens 
                WHERE user_id = ? AND pending = 0
                AND (? - created_at) < ?''', 
             (verify_user_id, time.time(), TOKEN_VALIDITY_SECONDS))
    token = c.fetchone()
    
    if not token:
        conn.close()
        return render_template('error.html', error='No valid verification token found for this user')
    
    # Update user account
    if email and realname:
        c.execute('UPDATE users SET password = ?, email = ?, realname = ? WHERE id = ?', 
                 (new_password, email, realname, verify_user_id))
    elif email:
        c.execute('UPDATE users SET password = ?, email = ? WHERE id = ?', 
                 (new_password, email, verify_user_id))
    else:
        c.execute('UPDATE users SET password = ? WHERE id = ?', 
                 (new_password, verify_user_id))
    
    # Delete used token
    c.execute('DELETE FROM password_reset_tokens WHERE user_id = ?', (verify_user_id,))
    conn.commit()
    
    # Get updated user info for success message
    c.execute('SELECT username, access_level FROM users WHERE id = ?', (verify_user_id,))
    user = c.fetchone()
    conn.close()
    
    if user:
        # Log the user in automatically after password reset
        session['user_id'] = int(verify_user_id)
        session['username'] = user['username']
        session['access_level'] = user['access_level']
        
        return render_template('account_updated.html', username=user['username'])
    
    return render_template('error.html', error='Account update failed')

@app.route('/admin/users.php')
def admin_users():
    """Admin endpoint that lists users - helps with user ID enumeration"""
    # This endpoint leaks user information (simulating a real info disclosure)
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT id, username, realname, access_level FROM users ORDER BY id')
    users = c.fetchall()
    conn.close()
    
    return render_template('users.html', users=users)

@app.route('/api/users')
def api_users():
    """API endpoint that returns user list - another enumeration vector"""
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT id, username, realname FROM users ORDER BY id')
    users = c.fetchall()
    conn.close()
    
    return jsonify([dict(u) for u in users])

@app.route('/api/status')
def api_status():
    """System status endpoint - leaks information about pending resets"""
    conn = get_db()
    c = conn.cursor()
    
    # Count pending password resets (info leak)
    c.execute('''SELECT COUNT(*) as count FROM password_reset_tokens 
                WHERE pending = 0 AND (? - created_at) < ?''', 
             (time.time(), TOKEN_VALIDITY_SECONDS))
    active_resets = c.fetchone()['count']
    
    # Count users with active reset tokens (more specific info leak)
    c.execute('''SELECT user_id FROM password_reset_tokens 
                WHERE pending = 0 AND (? - created_at) < ?''', 
             (time.time(), TOKEN_VALIDITY_SECONDS))
    users_with_resets = [row['user_id'] for row in c.fetchall()]
    
    conn.close()
    
    return jsonify({
        'status': 'operational',
        'version': '2.26.1',
        'active_password_resets': active_resets,
        'users_with_pending_resets': users_with_resets,
        'token_validity_seconds': TOKEN_VALIDITY_SECONDS
    })


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8000)
