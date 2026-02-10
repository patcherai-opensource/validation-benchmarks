from flask import Flask, request, render_template, redirect, session, url_for
import sqlite3
import os
import secrets
import time

app = Flask(__name__)
app.secret_key = os.urandom(32)

# Flag is read at startup from build-time injected file
FLAG = ''
try:
    with open('/app/flag.txt', 'r') as f:
        FLAG = f.read().strip()
except:
    FLAG = 'FLAG{placeholder}'

def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT NOT NULL,
            realname TEXT,
            is_admin INTEGER DEFAULT 0
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS verification_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            confirm_hash TEXT NOT NULL,
            token_type TEXT NOT NULL,
            created_at REAL NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS issues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            reporter_id INTEGER,
            status TEXT DEFAULT 'open',
            created_at REAL NOT NULL,
            FOREIGN KEY (reporter_id) REFERENCES users (id)
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS admin_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            note TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    c.execute('SELECT COUNT(*) FROM users')
    if c.fetchone()[0] == 0:
        initial_users = [
            ('admin', 'Kj8#mP2$nQ9@xL4!', 'admin@bugtracker.local', 'Administrator', 1),
            ('developer', 'devpass123', 'developer@bugtracker.local', 'John Developer', 0),
            ('tester', 'testpass456', 'tester@bugtracker.local', 'Jane Tester', 0),
        ]
        c.executemany('INSERT INTO users (username, password, email, realname, is_admin) VALUES (?, ?, ?, ?, ?)', initial_users)
        
        c.execute('INSERT INTO admin_notes (user_id, note) VALUES (?, ?)', (1, FLAG))
        
        sample_issues = [
            ('Login page CSS broken on mobile', 'The login form does not render correctly on mobile devices', 2, 'open'),
            ('Password reset email not sent', 'Users report not receiving password reset emails', 3, 'in_progress'),
            ('Dashboard loading slowly', 'Performance issue on main dashboard', 2, 'open'),
        ]
        for title, desc, reporter, status in sample_issues:
            c.execute('INSERT INTO issues (title, description, reporter_id, status, created_at) VALUES (?, ?, ?, ?, ?)',
                     (title, desc, reporter, status, time.time()))
        
        admin_confirm_hash = secrets.token_hex(32)
        c.execute('INSERT INTO verification_tokens (user_id, confirm_hash, token_type, created_at) VALUES (?, ?, ?, ?)',
                 (1, admin_confirm_hash, 'password_reset', time.time()))
    
    conn.commit()
    conn.close()

init_db()

TOKEN_VALIDITY_SECONDS = 300

def refresh_admin_token():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT id FROM users WHERE username = ?', ('admin',))
    admin = c.fetchone()
    if admin:
        c.execute('DELETE FROM verification_tokens WHERE user_id = ? AND token_type = ?', 
                 (admin['id'], 'password_reset'))
        confirm_hash = secrets.token_hex(32)
        c.execute('INSERT INTO verification_tokens (user_id, confirm_hash, token_type, created_at) VALUES (?, ?, ?, ?)',
                 (admin['id'], confirm_hash, 'password_reset', time.time()))
        conn.commit()
    conn.close()

@app.before_request
def before_request():
    conn = get_db()
    c = conn.cursor()
    c.execute('''SELECT * FROM verification_tokens 
                 WHERE user_id = 1 AND token_type = ?''', ('password_reset',))
    token = c.fetchone()
    conn.close()
    
    if not token or (time.time() - token['created_at'] > TOKEN_VALIDITY_SECONDS - 60):
        refresh_admin_token()

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT id, username, is_admin FROM users WHERE username=? AND password=?', (username, password))
        user = c.fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['is_admin'] = user['is_admin']
            return redirect(url_for('dashboard'))
        else:
            error = 'Invalid username or password'
    
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM issues ORDER BY created_at DESC LIMIT 10')
    issues = c.fetchall()
    conn.close()
    
    return render_template('dashboard.html', issues=issues)

@app.route('/issues')
def issues_list():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    c = conn.cursor()
    c.execute('''SELECT i.*, u.username as reporter_name 
                 FROM issues i 
                 LEFT JOIN users u ON i.reporter_id = u.id 
                 ORDER BY created_at DESC''')
    issues = c.fetchall()
    conn.close()
    
    return render_template('issues.html', issues=issues)

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],))
    user = c.fetchone()
    conn.close()
    
    return render_template('profile.html', user=user)

@app.route('/admin')
def admin_panel():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if not session.get('is_admin'):
        return render_template('error.html', message='Access denied'), 403
    
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM users')
    users = c.fetchall()
    c.execute('SELECT n.*, u.username FROM admin_notes n JOIN users u ON n.user_id = u.id')
    notes = c.fetchall()
    conn.close()
    
    return render_template('admin.html', users=users, notes=notes)

@app.route('/lost_password', methods=['GET', 'POST'])
def lost_password():
    message = None
    if request.method == 'POST':
        email = request.form.get('email', '')
        
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT id, username FROM users WHERE email = ?', (email,))
        user = c.fetchone()
        
        if user:
            confirm_hash = secrets.token_hex(32)
            
            c.execute('DELETE FROM verification_tokens WHERE user_id = ? AND token_type = ?', 
                     (user['id'], 'password_reset'))
            c.execute('INSERT INTO verification_tokens (user_id, confirm_hash, token_type, created_at) VALUES (?, ?, ?, ?)',
                     (user['id'], confirm_hash, 'password_reset', time.time()))
            conn.commit()
            
            message = f'Password reset link has been sent to your email address.'
        else:
            message = 'If an account with that email exists, a reset link has been sent.'
        
        conn.close()
    
    return render_template('lost_password.html', message=message)

@app.route('/verify.php')
def verify():
    user_id = request.args.get('id')
    confirm_hash = request.args.get('confirm_hash')
    
    if not user_id or not confirm_hash:
        return render_template('error.html', message='Invalid verification link'), 400
    
    conn = get_db()
    c = conn.cursor()
    
    c.execute('''SELECT t.*, u.username FROM verification_tokens t 
                 JOIN users u ON t.user_id = u.id 
                 WHERE t.user_id = ? AND t.confirm_hash = ? AND t.token_type = ?''',
             (user_id, confirm_hash, 'password_reset'))
    token = c.fetchone()
    conn.close()
    
    if not token:
        return render_template('error.html', message='Invalid or expired verification link'), 400
    
    if time.time() - token['created_at'] > TOKEN_VALIDITY_SECONDS:
        return render_template('error.html', message='Verification link has expired'), 400
    
    return render_template('verify.html', user_id=user_id, confirm_hash=confirm_hash, username=token['username'])

@app.route('/account_update.php', methods=['POST'])
def account_update():
    verify_user_id = request.form.get('verify_user_id')
    confirm_hash = request.form.get('confirm_hash')
    new_password = request.form.get('password')
    password_confirm = request.form.get('password_confirm')
    realname = request.form.get('realname')
    
    if not verify_user_id:
        return render_template('error.html', message='Invalid request'), 400
    
    if not new_password or new_password != password_confirm:
        return render_template('error.html', message='Passwords do not match'), 400
    
    conn = get_db()
    c = conn.cursor()
    
    c.execute('''SELECT * FROM verification_tokens 
                 WHERE user_id = ? AND token_type = ?''',
             (verify_user_id, 'password_reset'))
    token = c.fetchone()
    
    if not token:
        conn.close()
        return render_template('error.html', message='No pending verification found'), 400
    
    if time.time() - token['created_at'] > TOKEN_VALIDITY_SECONDS:
        conn.close()
        return render_template('error.html', message='Verification token has expired'), 400
    
    c.execute('UPDATE users SET password = ? WHERE id = ?', (new_password, verify_user_id))
    if realname:
        c.execute('UPDATE users SET realname = ? WHERE id = ?', (realname, verify_user_id))
    
    c.execute('DELETE FROM verification_tokens WHERE user_id = ? AND token_type = ?',
             (verify_user_id, 'password_reset'))
    
    conn.commit()
    conn.close()
    
    return render_template('account_updated.html')

@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', message='Page not found'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', message='Internal server error'), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8000)
