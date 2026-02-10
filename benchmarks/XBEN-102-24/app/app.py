from flask import Flask, request, render_template, redirect, session, url_for
import sqlite3
import base64
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key in production

# Flag is read from flag.txt which is populated at build time
def get_flag():
    try:
        with open('flag.txt', 'r') as f:
            return f.read().strip()
    except:
        return 'FLAG{placeholder}'

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            email TEXT
        )
    ''')
    # Initial users - admin has ID 1, test user has ID 2
    initial_users = [
        ('admin', '#$%^&*()adfjhasdfbjhas', 'admin@example.com'),
        ('test', 'test', 'test@example.com')
    ]
    for username, password, email in initial_users:
        c.execute('INSERT OR IGNORE INTO users (username, password, email) VALUES (?, ?, ?)', 
                  (username, password, email))

    conn.commit()
    conn.close()

def get_user_id(username):
    """Get user ID by username"""
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT id FROM users WHERE username = ?', (username,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def encode_form_args(args_dict):
    """
    Serialize form arguments to base64-encoded JSON (mimics WordPress plugin behavior).
    This is similar to how Advanced Forms plugin encodes af_form_args.
    VULNERABLE: No integrity check/nonce validation on these args!
    """
    json_str = json.dumps(args_dict)
    return base64.b64encode(json_str.encode()).decode()

def decode_form_args(encoded_str):
    """
    Deserialize form arguments from base64-encoded JSON.
    VULNERABLE: Trusts client-submitted data without verification!
    """
    try:
        json_str = base64.b64decode(encoded_str.encode()).decode()
        return json.loads(json_str)
    except:
        return None

init_db()

@app.route('/')
def home():
    if 'username' in session:
        return redirect('/profile')
    return render_template('login.html')

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect('/')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            session['username'] = username
            session['user_id'] = user[0]  # Store user ID in session
            return redirect('/profile')
        else:
            return 'Login Failed'
    return render_template('login.html')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'username' not in session:
        return redirect('/')

    # Fetch user's email from the database
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT email FROM users WHERE username = ?', (session['username'],))
    user_email = c.fetchone()[0]
    conn.close()

    if request.method == 'POST':
        # VULNERABLE: Decode and trust client-submitted form args without verification
        # This mimics the Advanced Forms WordPress plugin vulnerability (CVE)
        # The af_form_args hidden field contains base64+JSON encoded arguments
        # that the server blindly trusts without nonce/integrity validation
        
        encoded_args = request.form.get('af_form_args')
        new_email = request.form.get('email')
        
        if encoded_args and new_email:
            # Decode the serialized form arguments - VULNERABLE!
            # No integrity check/nonce validation is performed
            form_args = decode_form_args(encoded_args)
            
            if form_args:
                # Use the user_id from the decoded (attacker-controlled) arguments
                target_user_id = form_args.get('user_id')
                
                if target_user_id:
                    # Update email based on user_id from form args (IDOR!)
                    conn = sqlite3.connect('database.db')
                    c = conn.cursor()
                    
                    # Check if we're updating admin's email (ID 1)
                    c.execute('SELECT username FROM users WHERE id = ?', (target_user_id,))
                    target_user = c.fetchone()
                    
                    c.execute('UPDATE users SET email = ? WHERE id = ?', (new_email, target_user_id))
                    conn.commit()
                    conn.close()
                    
                    message = 'Email updated successfully!'
                    
                    # If admin's account was modified, reveal the flag
                    # (simulates account takeover via password reset flow)
                    if target_user and target_user[0] == 'admin':
                        flag = get_flag()
                        message += ' ' + flag
                    
                    return render_template('profile.html', email=new_email, message=message)
    
    # Generate form args for the current user
    # These are serialized and placed in a hidden field (like af_form_args in WP plugin)
    form_args = {
        'user_id': session.get('user_id', get_user_id(session['username'])),
        'action': 'update_email'
    }
    encoded_form_args = encode_form_args(form_args)
    
    return render_template('profile.html', email=user_email, form_args=encoded_form_args)


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8000)
