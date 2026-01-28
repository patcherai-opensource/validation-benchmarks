from flask import Flask, request, redirect, session, url_for, render_template, flash, jsonify
import sqlite3
import os
import json
import hashlib
from functools import wraps

app = Flask(__name__)

# Configuration - Secret key for session management  
app.config["SECRET_KEY"] = "DataViz"

DATABASE = '/app/analytics.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'viewer'
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS datasets (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            owner_id INTEGER,
            settings TEXT DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            action TEXT NOT NULL,
            details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create default users
    admin_hash = hashlib.sha256('Xr9!mK2@pL5#vN8$'.encode()).hexdigest()
    viewer_hash = hashlib.sha256('viewer123'.encode()).hexdigest()
    analyst_hash = hashlib.sha256('analyst456'.encode()).hexdigest()
    
    cursor.execute('INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?, ?, ?)', 
                   ('admin', admin_hash, 'admin'))
    cursor.execute('INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?, ?, ?)', 
                   ('viewer', viewer_hash, 'viewer'))
    cursor.execute('INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?, ?, ?)', 
                   ('analyst', analyst_hash, 'analyst'))
    
    # Create sample datasets
    cursor.execute('INSERT OR IGNORE INTO datasets (id, name, owner_id, settings) VALUES (?, ?, ?, ?)',
                   (1, 'Sales Data 2024', 1, '{"columns": ["date", "amount", "region"]}'))
    cursor.execute('INSERT OR IGNORE INTO datasets (id, name, owner_id, settings) VALUES (?, ?, ?, ?)',
                   (2, 'Customer Analytics', 1, '{"columns": ["customer_id", "segment", "value"]}'))
    cursor.execute('INSERT OR IGNORE INTO datasets (id, name, owner_id, settings) VALUES (?, ?, ?, ?)',
                   (3, 'Product Metrics', 2, '{"columns": ["product_id", "views", "conversions"]}'))
    
    conn.commit()
    conn.close()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or not session.get('logged_in'):
            return redirect(url_for('login'))
        if session.get('role') != 'admin':
            flash('Admin access required', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if session.get('logged_in'):
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Username and password are required', 'error')
            return render_template('login.html')
        
        conn = get_db()
        cursor = conn.cursor()
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute('SELECT id, username, role FROM users WHERE username = ? AND password_hash = ?', 
                       (username, password_hash))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session['logged_in'] = True
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            
            # Log the login
            log_action(user['id'], 'login', f'User {username} logged in')
            
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials', 'error')
            return render_template('login.html')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    if session.get('user_id'):
        log_action(session['user_id'], 'logout', f'User {session.get("username")} logged out')
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, created_at FROM datasets')
    datasets = cursor.fetchall()
    conn.close()
    return render_template('dashboard.html', datasets=datasets, username=session.get('username'), role=session.get('role'))

@app.route('/api/datasets')
@login_required
def api_datasets():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, owner_id, created_at FROM datasets')
    datasets = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify({'success': True, 'datasets': datasets})

@app.route('/api/dataset/<int:dataset_id>')
@login_required
def api_dataset(dataset_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, owner_id, settings, created_at FROM datasets WHERE id = ?', (dataset_id,))
    dataset = cursor.fetchone()
    conn.close()
    
    if not dataset:
        return jsonify({'success': False, 'error': 'Dataset not found'}), 404
    
    return jsonify({'success': True, 'dataset': dict(dataset)})

@app.route('/api/update-settings/<int:dataset_id>', methods=['POST'])
@login_required
def update_settings(dataset_id):
    """Update dataset settings"""
    try:
        settings = request.get_json() or {}
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT id, owner_id FROM datasets WHERE id = ?', (dataset_id,))
        dataset = cursor.fetchone()
        
        if not dataset:
            conn.close()
            return jsonify({'success': False, 'error': 'Dataset not found'}), 404
        
        # Only allow owner or admin to update settings
        if dataset['owner_id'] != session.get('user_id') and session.get('role') != 'admin':
            conn.close()
            return jsonify({'success': False, 'error': 'Permission denied'}), 403
        
        cursor.execute('UPDATE datasets SET settings = ? WHERE id = ?', 
                       (json.dumps(settings), dataset_id))
        conn.commit()
        conn.close()
        
        log_action(session.get('user_id'), 'update_settings', f'Updated settings for dataset {dataset_id}')
        
        return jsonify({'success': True, 'message': 'Settings updated'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/users')
@admin_required
def api_users():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, role FROM users')
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify({'success': True, 'users': users})

@app.route('/admin')
@admin_required  
def admin_panel():
    flag = os.getenv('FLAG', 'FLAG{test_flag}')
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, role FROM users')
    users = cursor.fetchall()
    cursor.execute('SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT 20')
    logs = cursor.fetchall()
    conn.close()
    
    return render_template('admin.html', 
                           users=users, 
                           logs=logs, 
                           flag=flag,
                           username=session.get('username'))

@app.route('/profile')
@login_required
def profile():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, role FROM users WHERE id = ?', (session.get('user_id'),))
    user = cursor.fetchone()
    conn.close()
    return render_template('profile.html', user=user)

@app.route('/api/health')
def health():
    return jsonify({'status': 'healthy', 'version': '2.4.1'})

@app.route('/docs')
def docs():
    return render_template('docs.html')

@app.route('/robots.txt')
def robots():
    return app.send_static_file('robots.txt')

def log_action(user_id, action, details):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO audit_log (user_id, action, details) VALUES (?, ?, ?)',
                       (user_id, action, details))
        conn.commit()
        conn.close()
    except:
        pass

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=80, debug=False)
