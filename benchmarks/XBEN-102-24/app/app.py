from flask import Flask, request, render_template, redirect, session
import sqlite3
import os
import json
import base64

app = Flask(__name__)
app.secret_key = os.urandom(24)

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            email TEXT,
            role TEXT DEFAULT 'user'
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_settings (
            user_id INTEGER PRIMARY KEY,
            notification_email TEXT,
            receive_updates INTEGER DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    initial_users = [
        ('admin', 'Kj8#mP2$vL9@nQ4!xR7', 'admin@acmecorp.local', 'administrator'),
        ('guest', 'guest', 'guest@acmecorp.local', 'user'),
        ('john.doe', 'SecurePass2024!', 'john.doe@acmecorp.local', 'user')
    ]
    
    for username, password, email, role in initial_users:
        c.execute('INSERT OR IGNORE INTO users (username, password, email, role) VALUES (?, ?, ?, ?)', 
                  (username, password, email, role))
        c.execute('SELECT id FROM users WHERE username = ?', (username,))
        user_id = c.fetchone()[0]
        c.execute('INSERT OR IGNORE INTO user_settings (user_id, notification_email, receive_updates) VALUES (?, ?, ?)',
                  (user_id, email, 1))

    conn.commit()
    conn.close()

init_db()

def encode_form_args(args):
    return base64.b64encode(json.dumps(args).encode()).decode()

def decode_form_args(encoded):
    try:
        return json.loads(base64.b64decode(encoded).decode())
    except:
        return None

@app.route('/')
def home():
    if 'username' in session:
        return redirect('/dashboard')
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('SELECT id, username, role FROM users WHERE username=? AND password=?', (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[2]
            return redirect('/dashboard')
        else:
            error = 'Invalid username or password'
    return render_template('login.html', error=error)

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect('/login')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect('/login')
    return render_template('dashboard.html')

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'username' not in session:
        return redirect('/login')
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT id, email FROM users WHERE username = ?', (session['username'],))
    user_data = c.fetchone()
    user_id = user_data[0]
    current_email = user_data[1]
    
    c.execute('SELECT notification_email, receive_updates FROM user_settings WHERE user_id = ?', (user_id,))
    settings_data = c.fetchone()
    conn.close()
    
    form_args = {
        'user_id': user_id,
        'form_type': 'user_settings',
        'fields': ['notification_email', 'receive_updates']
    }
    encoded_args = encode_form_args(form_args)
    
    message = None
    if request.method == 'POST':
        submitted_args = request.form.get('form_args')
        if submitted_args:
            decoded_args = decode_form_args(submitted_args)
            if decoded_args and decoded_args.get('form_type') == 'user_settings':
                target_user_id = decoded_args.get('user_id')
                
                new_notification_email = request.form.get('notification_email')
                receive_updates = 1 if request.form.get('receive_updates') else 0
                
                conn = sqlite3.connect('database.db')
                c = conn.cursor()
                c.execute('UPDATE user_settings SET notification_email = ?, receive_updates = ? WHERE user_id = ?',
                         (new_notification_email, receive_updates, target_user_id))
                c.execute('UPDATE users SET email = ? WHERE id = ?', (new_notification_email, target_user_id))
                conn.commit()
                
                c.execute('SELECT username, role FROM users WHERE id = ?', (target_user_id,))
                updated_user = c.fetchone()
                conn.close()
                
                if updated_user and updated_user[1] == 'administrator':
                    flag = os.getenv('FLAG', 'FLAG{placeholder}')
                    message = f'Administrator account updated. Security token for audit: {flag}'
                else:
                    message = 'Settings updated successfully.'
                
                current_email = new_notification_email
                settings_data = (new_notification_email, receive_updates)
    
    return render_template('settings.html', 
                          email=current_email,
                          notification_email=settings_data[0] if settings_data else current_email,
                          receive_updates=settings_data[1] if settings_data else 1,
                          form_args=encoded_args,
                          message=message)

@app.route('/admin')
def admin_panel():
    if 'username' not in session:
        return redirect('/login')
    if session.get('role') != 'administrator':
        return render_template('error.html', error='Access denied'), 403
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT id, username, email, role FROM users')
    users = c.fetchall()
    conn.close()
    
    return render_template('admin.html', users=users)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error='Page not found'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('error.html', error='Internal server error'), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8000)
