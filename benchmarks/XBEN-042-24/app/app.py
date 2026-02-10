import os
import json
import sqlite3
import hashlib
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, g

app = Flask(__name__)
app.secret_key = os.urandom(24)

DATABASE = '/data/connections.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    os.makedirs('/data', exist_ok=True)
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'viewer'
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS connections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conn_id TEXT UNIQUE NOT NULL,
            conn_type TEXT NOT NULL,
            host TEXT,
            port INTEGER,
            login TEXT,
            password TEXT,
            extra TEXT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    admin_hash = hashlib.sha256('4dm1n!Str0ng'.encode()).hexdigest()
    operator_hash = hashlib.sha256('operator'.encode()).hexdigest()
    viewer_hash = hashlib.sha256('analyst123'.encode()).hexdigest()
    
    try:
        cursor.execute('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)',
                      ('admin', admin_hash, 'admin'))
        cursor.execute('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)',
                      ('operator', operator_hash, 'editor'))
        cursor.execute('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)',
                      ('analyst', viewer_hash, 'viewer'))
    except sqlite3.IntegrityError:
        pass
    
    flag_value = os.environ.get('FLAG', 'FLAG{test_flag}')
    
    try:
        cursor.execute('''
            INSERT INTO connections (conn_id, conn_type, host, port, login, password, extra, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('postgres_default', 'postgres', 'db.internal.company.com', 5432, 'airflow', 
              'db_secure_pass_2024', '{}', 'Default PostgreSQL connection'))
        
        cursor.execute('''
            INSERT INTO connections (conn_id, conn_type, host, port, login, password, extra, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('aws_default', 'aws', None, None, 'AKIAIOSFODNN7EXAMPLE', 
              'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
              json.dumps({'region_name': 'us-west-2', 'aws_session_token': flag_value}),
              'AWS connection for S3 and other services'))
        
        cursor.execute('''
            INSERT INTO connections (conn_id, conn_type, host, port, login, password, extra, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('redis_cache', 'redis', 'redis.internal.company.com', 6379, None, 
              'redis_cache_pass', '{"db": 0}', 'Redis caching layer'))
        
        cursor.execute('''
            INSERT INTO connections (conn_id, conn_type, host, port, login, password, extra, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('slack_webhook', 'http', 'hooks.slack.com', 443, None, None,
              '{"webhook_url": "https://hooks.slack.com/services/T00/B00/XXXX", "channel": "#alerts"}',
              'Slack notifications'))
              
        cursor.execute('''
            INSERT INTO connections (conn_id, conn_type, host, port, login, password, extra, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('mysql_prod', 'mysql', 'mysql-prod.company.com', 3306, 'app_user', 
              'mysql_prod_2024!', '{"charset": "utf8mb4"}', 'Production MySQL database'))
    except sqlite3.IntegrityError:
        pass
    
    db.commit()
    db.close()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def editor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        if session.get('role') not in ['admin', 'editor']:
            flash('You do not have permission to perform this action.', 'error')
            return redirect(url_for('connections_list'))
        return f(*args, **kwargs)
    return decorated_function

def mask_sensitive_value(value, show_chars=4):
    if not value:
        return ''
    if len(value) <= show_chars:
        return '*' * len(value)
    return value[:show_chars] + '*' * (len(value) - show_chars)

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('connections_list'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        db = get_db()
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        user = db.execute('SELECT * FROM users WHERE username = ? AND password_hash = ?',
                         (username, password_hash)).fetchone()
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect(url_for('connections_list'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/connection')
@login_required
def connections_list():
    db = get_db()
    connections = db.execute('SELECT * FROM connections ORDER BY conn_id').fetchall()
    return render_template('connections.html', connections=connections, 
                          mask_value=mask_sensitive_value)

@app.route('/connection/edit/<int:conn_id>', methods=['GET', 'POST'])
@editor_required
def edit_connection(conn_id):
    db = get_db()
    connection = db.execute('SELECT * FROM connections WHERE id = ?', (conn_id,)).fetchone()
    
    if not connection:
        flash('Connection not found.', 'error')
        return redirect(url_for('connections_list'))
    
    if request.method == 'POST':
        host = request.form.get('host', '')
        port = request.form.get('port', '')
        login = request.form.get('login', '')
        password = request.form.get('password', '')
        extra = request.form.get('extra', '{}')
        description = request.form.get('description', '')
        
        try:
            port_val = int(port) if port else None
        except ValueError:
            port_val = None
        
        if password == '********':
            password = connection['password']
        
        db.execute('''
            UPDATE connections 
            SET host = ?, port = ?, login = ?, password = ?, extra = ?, description = ?
            WHERE id = ?
        ''', (host, port_val, login, password, extra, description, conn_id))
        db.commit()
        
        flash('Connection updated successfully.', 'success')
        return redirect(url_for('connections_list'))
    
    extra_fields = {}
    if connection['extra']:
        try:
            extra_fields = json.loads(connection['extra'])
        except json.JSONDecodeError:
            extra_fields = {}
    
    return render_template('edit_connection.html', connection=connection, 
                          extra_fields=extra_fields)

@app.route('/connection/add', methods=['GET', 'POST'])
@editor_required
def add_connection():
    if request.method == 'POST':
        conn_id = request.form.get('conn_id', '')
        conn_type = request.form.get('conn_type', '')
        host = request.form.get('host', '')
        port = request.form.get('port', '')
        login = request.form.get('login', '')
        password = request.form.get('password', '')
        extra = request.form.get('extra', '{}')
        description = request.form.get('description', '')
        
        try:
            port_val = int(port) if port else None
        except ValueError:
            port_val = None
        
        db = get_db()
        try:
            db.execute('''
                INSERT INTO connections (conn_id, conn_type, host, port, login, password, extra, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (conn_id, conn_type, host, port_val, login, password, extra, description))
            db.commit()
            flash('Connection added successfully.', 'success')
            return redirect(url_for('connections_list'))
        except sqlite3.IntegrityError:
            flash('Connection ID already exists.', 'error')
    
    return render_template('add_connection.html')

@app.route('/connection/delete/<int:conn_id>', methods=['POST'])
@editor_required
def delete_connection(conn_id):
    db = get_db()
    db.execute('DELETE FROM connections WHERE id = ?', (conn_id,))
    db.commit()
    flash('Connection deleted successfully.', 'success')
    return redirect(url_for('connections_list'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error='Page not found'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('error.html', error='Internal server error'), 500

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=80)
