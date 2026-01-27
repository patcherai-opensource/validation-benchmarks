from flask import Flask, request, render_template, redirect, session
import sqlite3
import os
import json
import base64

app = Flask(__name__)
app.secret_key = 'wp_af_secure_key_2024'  # WordPress-style key

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT,
            email TEXT,
            user_id INTEGER,
            role TEXT DEFAULT 'subscriber'
        )
    ''')
    initial_users = [
        ('administrator', 'wp_s3cr3t_@dm1n_2024!', 'admin@wordpress-site.local', 1, 'administrator'),
        ('editor', 'editor123', 'editor@wordpress-site.local', 2, 'editor'),
        ('subscriber', 'subscriber', 'subscriber@wordpress-site.local', 3, 'subscriber')
    ]
    for user in initial_users:
        c.execute('INSERT OR IGNORE INTO users (username, password, email, user_id, role) VALUES (?, ?, ?, ?, ?)', user)
    
    conn.commit()
    conn.close()

init_db()

def encode_form_args(args_dict):
    """Serialize form arguments to base64-encoded JSON (like af_form_args in WordPress)"""
    json_str = json.dumps(args_dict)
    return base64.b64encode(json_str.encode()).decode()

def decode_form_args(encoded_str):
    """Decode base64-encoded JSON form arguments"""
    try:
        json_str = base64.b64decode(encoded_str.encode()).decode()
        return json.loads(json_str)
    except:
        return None

@app.route('/')
def home():
    if 'username' in session:
        return redirect('/wp-admin/profile')
    return redirect('/wp-login')

@app.route('/health')
def health():
    return 'OK', 200

@app.route('/wp-login', methods=['GET', 'POST'])
def wp_login():
    error = None
    if request.method == 'POST':
        username = request.form.get('log', '')
        password = request.form.get('pwd', '')
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            session['username'] = username
            session['user_id'] = user[3]
            session['role'] = user[4]
            return redirect('/wp-admin/profile')
        else:
            error = 'ERROR: The username or password you entered is incorrect.'
    return render_template('wp-login.html', error=error)

@app.route('/wp-admin/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect('/wp-login')

@app.route('/wp-admin/profile', methods=['GET', 'POST'])
def profile():
    if 'username' not in session:
        return redirect('/wp-login')

    # Fetch user's data from the database
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT email, user_id, role FROM users WHERE username = ?', (session['username'],))
    user_data = c.fetchone()
    conn.close()
    
    user_email = user_data[0]
    user_id = user_data[1]
    
    message = None
    error = None

    if request.method == 'POST':
        # VULNERABLE: Trusting serialized form arguments from client
        # Similar to af_form_args in Advanced Forms for WordPress
        af_form_args = request.form.get('af_form_args', '')
        
        if af_form_args:
            # Decode the serialized form arguments (IDOR vulnerability)
            form_args = decode_form_args(af_form_args)
            
            if form_args:
                target_user_id = form_args.get('user_id')
                new_email = request.form.get('email', '')
                
                if new_email and target_user_id:
                    # VULNERABLE: Using client-provided user_id without authorization check
                    # Should verify: target_user_id == session['user_id']
                    conn = sqlite3.connect('database.db')
                    c = conn.cursor()
                    
                    # Get target user info
                    c.execute('SELECT username, role FROM users WHERE user_id = ?', (target_user_id,))
                    target_user = c.fetchone()
                    
                    if target_user:
                        target_username = target_user[0]
                        target_role = target_user[1]
                        
                        # Update email for the target user
                        c.execute('UPDATE users SET email = ? WHERE user_id = ?', (new_email, target_user_id))
                        conn.commit()
                        conn.close()
                        
                        message = f'Profile updated for user ID {target_user_id}.'
                        
                        # If modifying administrator account, reveal flag
                        if target_role == 'administrator' and target_username == 'administrator':
                            flag = os.getenv('FLAG', 'FLAG{placeholder}')
                            message = f'Administrator profile updated. {flag}'
                    else:
                        conn.close()
                        error = 'Invalid user ID specified.'
            else:
                error = 'Invalid form arguments.'
        else:
            error = 'Missing form arguments.'
    
    # Generate form args for the template (base64-encoded JSON)
    form_args_data = {
        'user_id': user_id,
        'form_key': 'profile_update',
        'action': 'update_profile'
    }
    encoded_args = encode_form_args(form_args_data)
    
    return render_template('wp-profile.html', 
                         email=user_email, 
                         message=message,
                         error=error,
                         af_form_args=encoded_args,
                         user_id=user_id)


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8000)
