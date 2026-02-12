import os
import sys
import json
import uuid
import sqlite3
import hashlib
import threading
import time
import subprocess
import logging
from functools import wraps

from flask import (
    Flask, request, Response, make_response, redirect,
    url_for, session, g, jsonify, render_template_string
)

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.urandom(32).hex()

DATABASE = '/data/phpmyfaq.db'
ADMIN_SECRET_FLAG = open('/app/admin_secret.txt').read().strip()

# ─── Database helpers ────────────────────────────────────────────────────────

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
    db.execute('''CREATE TABLE IF NOT EXISTS faquser (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        login TEXT UNIQUE NOT NULL,
        pass TEXT NOT NULL,
        display_name TEXT NOT NULL DEFAULT '',
        email TEXT NOT NULL DEFAULT '',
        account_status TEXT NOT NULL DEFAULT 'active',
        auth_source TEXT NOT NULL DEFAULT 'local',
        member_since TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_superadmin INTEGER NOT NULL DEFAULT 0,
        is_visible INTEGER NOT NULL DEFAULT 1
    )''')
    db.execute('''CREATE TABLE IF NOT EXISTS faqdata (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lang TEXT NOT NULL DEFAULT 'en',
        thema TEXT NOT NULL,
        content TEXT NOT NULL,
        author TEXT NOT NULL,
        active TEXT NOT NULL DEFAULT 'yes',
        sticky INTEGER NOT NULL DEFAULT 0,
        updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    db.execute('''CREATE TABLE IF NOT EXISTS faqcategories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lang TEXT NOT NULL DEFAULT 'en',
        parent_id INTEGER NOT NULL DEFAULT 0,
        name TEXT NOT NULL,
        description TEXT,
        user_id INTEGER NOT NULL DEFAULT 1
    )''')
    db.execute('''CREATE TABLE IF NOT EXISTS faqconfig (
        config_name TEXT PRIMARY KEY,
        config_value TEXT
    )''')
    db.execute('''CREATE TABLE IF NOT EXISTS faqsessions (
        sid TEXT PRIMARY KEY,
        user_id INTEGER,
        ip TEXT,
        time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    db.execute('''CREATE TABLE IF NOT EXISTS faqcollector (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data TEXT NOT NULL,
        ip TEXT,
        time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    # Create admin user
    admin_pass = hashlib.sha256(b'admin_phpmyfaq_2024!').hexdigest()
    try:
        db.execute(
            'INSERT INTO faquser (login, pass, display_name, email, is_superadmin) VALUES (?, ?, ?, ?, ?)',
            ('admin', admin_pass, 'Administrator', 'admin@phpmyfaq.local', 1)
        )
    except sqlite3.IntegrityError:
        pass
    # Seed some FAQ content
    faqs = [
        ('How do I reset my password?', 'Navigate to your profile settings and click "Change Password". You will need to enter your current password and then your new password twice.', 'Administrator'),
        ('What browsers are supported?', 'phpMyFAQ supports all modern browsers including Chrome, Firefox, Safari, and Edge. Internet Explorer 11 is no longer supported.', 'Administrator'),
        ('How do I add a new FAQ entry?', 'Login to the admin panel, navigate to "Content" > "Add new FAQ" and fill in the required fields.', 'Administrator'),
        ('Can I import FAQs from other systems?', 'Yes, phpMyFAQ supports importing from CSV and XML formats. Go to "Admin" > "Import" to get started.', 'Administrator'),
    ]
    for thema, content, author in faqs:
        try:
            db.execute('INSERT INTO faqdata (thema, content, author) VALUES (?, ?, ?)', (thema, content, author))
        except:
            pass
    # Seed categories
    categories = [
        ('General', 'General questions about phpMyFAQ'),
        ('Administration', 'Questions about administering phpMyFAQ'),
        ('Installation', 'Installation and setup questions'),
    ]
    for name, desc in categories:
        try:
            db.execute('INSERT INTO faqcategories (name, description) VALUES (?, ?)', (name, desc))
        except:
            pass
    # Seed config
    configs = [
        ('main.currentVersion', '3.1.17'),
        ('main.titleFAQ', 'phpMyFAQ'),
        ('main.language', 'en'),
        ('main.referenceURL', 'http://localhost:5000'),
        ('main.administrationMail', 'admin@phpmyfaq.local'),
        ('spam.enableCaptcha', 'true'),
        ('security.loginWithEmailAddress', 'false'),
    ]
    for name, val in configs:
        try:
            db.execute('INSERT OR IGNORE INTO faqconfig (config_name, config_value) VALUES (?, ?)', (name, val))
        except:
            pass
    db.commit()
    db.close()

# ─── Auth helpers ────────────────────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('admin_login'))
        if not session.get('is_superadmin'):
            return Response('Forbidden', status=403)
        return f(*args, **kwargs)
    return decorated

# ─── Public routes ───────────────────────────────────────────────────────────

@app.route('/')
def index():
    db = get_db()
    faqs = db.execute('SELECT id, thema, content, author, updated FROM faqdata WHERE active = ? ORDER BY updated DESC', ('yes',)).fetchall()
    categories = db.execute('SELECT id, name, description FROM faqcategories ORDER BY name').fetchall()
    config = {}
    for row in db.execute('SELECT config_name, config_value FROM faqconfig').fetchall():
        config[row['config_name']] = row['config_value']
    return render_template_string(PUBLIC_INDEX, faqs=faqs, categories=categories, config=config)

@app.route('/faq/<int:faq_id>')
def view_faq(faq_id):
    db = get_db()
    faq = db.execute('SELECT * FROM faqdata WHERE id = ?', (faq_id,)).fetchone()
    if not faq:
        return Response('FAQ not found', status=404)
    return render_template_string(FAQ_DETAIL, faq=faq)

@app.route('/api/search')
def search_faqs():
    q = request.args.get('q', '')
    db = get_db()
    faqs = db.execute(
        'SELECT id, thema, author FROM faqdata WHERE active = ? AND (thema LIKE ? OR content LIKE ?)',
        ('yes', f'%{q}%', f'%{q}%')
    ).fetchall()
    return jsonify([{'id': f['id'], 'thema': f['thema'], 'author': f['author']} for f in faqs])

# ─── User registration & login ──────────────────────────────────────────────

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        login_name = request.form.get('login', '').strip()
        password = request.form.get('password', '').strip()
        display_name = request.form.get('display_name', '').strip()
        email = request.form.get('email', '').strip()
        if not login_name or not password:
            error = 'Username and password are required.'
        elif len(login_name) < 3:
            error = 'Username must be at least 3 characters.'
        else:
            db = get_db()
            existing = db.execute('SELECT user_id FROM faquser WHERE login = ?', (login_name,)).fetchone()
            if existing:
                error = 'Username already exists.'
            else:
                pass_hash = hashlib.sha256(password.encode()).hexdigest()
                db.execute(
                    'INSERT INTO faquser (login, pass, display_name, email) VALUES (?, ?, ?, ?)',
                    (login_name, pass_hash, display_name or login_name, email)
                )
                db.commit()
                return redirect(url_for('login'))
    return render_template_string(REGISTER_PAGE, error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        login_name = request.form.get('login', '').strip()
        password = request.form.get('password', '').strip()
        db = get_db()
        pass_hash = hashlib.sha256(password.encode()).hexdigest()
        user = db.execute('SELECT * FROM faquser WHERE login = ? AND pass = ?', (login_name, pass_hash)).fetchone()
        if user:
            session['user_id'] = user['user_id']
            session['login'] = user['login']
            session['display_name'] = user['display_name']
            session['is_superadmin'] = bool(user['is_superadmin'])
            if user['is_superadmin']:
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('user_profile'))
        else:
            error = 'Invalid username or password.'
    return render_template_string(LOGIN_PAGE, error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# ─── User profile ───────────────────────────────────────────────────────────

@app.route('/user/profile', methods=['GET', 'POST'])
@login_required
def user_profile():
    db = get_db()
    message = None
    if request.method == 'POST':
        display_name = request.form.get('display_name', '').strip()
        email = request.form.get('email', '').strip()
        if display_name:
            db.execute(
                'UPDATE faquser SET display_name = ?, email = ? WHERE user_id = ?',
                (display_name, email, session['user_id'])
            )
            db.commit()
            session['display_name'] = display_name
            message = 'Profile updated successfully.'
    user = db.execute('SELECT * FROM faquser WHERE user_id = ?', (session['user_id'],)).fetchone()
    return render_template_string(USER_PROFILE, user=user, message=message)

# ─── Admin routes ────────────────────────────────────────────────────────────

@app.route('/admin/', methods=['GET'])
@app.route('/admin', methods=['GET'])
def admin_login():
    if session.get('is_superadmin'):
        return redirect(url_for('admin_dashboard'))
    return render_template_string(ADMIN_LOGIN_PAGE)

@app.route('/admin/login', methods=['POST'])
def admin_login_post():
    login_name = request.form.get('faqusername', '').strip()
    password = request.form.get('faqpassword', '').strip()
    db = get_db()
    pass_hash = hashlib.sha256(password.encode()).hexdigest()
    user = db.execute(
        'SELECT * FROM faquser WHERE login = ? AND pass = ? AND is_superadmin = 1',
        (login_name, pass_hash)
    ).fetchone()
    if user:
        session['user_id'] = user['user_id']
        session['login'] = user['login']
        session['display_name'] = user['display_name']
        session['is_superadmin'] = True
        resp = make_response(redirect(url_for('admin_dashboard')))
        return resp
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    db = get_db()
    user_count = db.execute('SELECT COUNT(*) as cnt FROM faquser').fetchone()['cnt']
    faq_count = db.execute('SELECT COUNT(*) as cnt FROM faqdata').fetchone()['cnt']
    cat_count = db.execute('SELECT COUNT(*) as cnt FROM faqcategories').fetchone()['cnt']
    config = {}
    for row in db.execute('SELECT config_name, config_value FROM faqconfig').fetchall():
        config[row['config_name']] = row['config_value']
    return render_template_string(ADMIN_DASHBOARD, user_count=user_count, faq_count=faq_count, cat_count=cat_count, config=config)

@app.route('/admin/user')
@admin_required
def admin_user_list():
    return render_template_string(ADMIN_USER_PAGE)

@app.route('/admin/content')
@admin_required
def admin_content():
    db = get_db()
    faqs = db.execute('SELECT * FROM faqdata ORDER BY updated DESC').fetchall()
    return render_template_string(ADMIN_CONTENT, faqs=faqs)

@app.route('/admin/config')
@admin_required
def admin_config():
    db = get_db()
    configs = db.execute('SELECT * FROM faqconfig ORDER BY config_name').fetchall()
    return render_template_string(ADMIN_CONFIG, configs=configs)

# ─── Admin AJAX endpoints ────────────────────────────────────────────────────

@app.route('/admin/ajax/user', methods=['GET'])
@admin_required
def admin_ajax_user():
    """AJAX endpoint for user management - mirrors phpmyfaq/admin/ajax.user.php"""
    action = request.args.get('action', '')

    if action == 'get_user_list':
        db = get_db()
        users = db.execute('SELECT user_id, login, display_name, email, account_status, is_superadmin, member_since FROM faquser ORDER BY user_id').fetchall()
        user_list = []
        for u in users:
            user_list.append({
                'user_id': u['user_id'],
                'login': _htmlentities(u['login']),
                'display_name': u['display_name'],
                'email': _htmlentities(u['email']),
                'account_status': u['account_status'],
                'is_superadmin': bool(u['is_superadmin']),
                'member_since': u['member_since']
            })
        return jsonify(user_list)

    elif action == 'get_user_data':
        user_id = request.args.get('user_id', type=int)
        if not user_id:
            return jsonify({'error': 'No user ID provided'}), 400
        db = get_db()
        user = db.execute('SELECT * FROM faquser WHERE user_id = ?', (user_id,)).fetchone()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        userdata = {
            'user_id': user['user_id'],
            'login': _htmlentities(user['login']),
            'display_name': user['display_name'],
            'email': _htmlentities(user['email']),
            'account_status': user['account_status'],
            'auth_source': user['auth_source'],
            'is_superadmin': bool(user['is_superadmin']),
            'is_visible': bool(user['is_visible']),
            'member_since': user['member_since']
        }
        return jsonify(userdata)

    elif action == 'delete_user':
        user_id = request.args.get('user_id', type=int)
        if not user_id:
            return jsonify({'error': 'No user ID provided'}), 400
        db = get_db()
        db.execute('DELETE FROM faquser WHERE user_id = ? AND is_superadmin = 0', (user_id,))
        db.commit()
        return jsonify({'success': True})

    return jsonify({'error': 'Unknown action'}), 400


def _htmlentities(s):
    """Encode HTML entities - used for safe fields"""
    if s is None:
        return ''
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#x27;')

# ─── Collector endpoint (for XSS exfiltration) ──────────────────────────────

@app.route('/collect', methods=['GET', 'POST'])
def collect():
    """Endpoint to receive exfiltrated data"""
    data = request.args.get('data', '') or request.form.get('data', '') or request.get_data(as_text=True)
    if data:
        db = get_db()
        db.execute('INSERT INTO faqcollector (data, ip) VALUES (?, ?)', (data, request.remote_addr))
        db.commit()
    return Response('', status=204)

@app.route('/collected', methods=['GET'])
def collected():
    """View collected data"""
    db = get_db()
    rows = db.execute('SELECT data, ip, time FROM faqcollector ORDER BY id DESC LIMIT 50').fetchall()
    entries = [{'data': r['data'], 'ip': r['ip'], 'time': r['time']} for r in rows]
    return jsonify(entries)

# ─── Admin bot (simulates admin viewing user management) ─────────────────────

def admin_bot_loop():
    """Periodically simulate admin viewing user management page"""
    time.sleep(15)  # Wait for app startup
    while True:
        try:
            run_admin_bot()
        except Exception as e:
            logger.debug(f'Admin bot error: {e}')
        time.sleep(20)

def run_admin_bot():
    """Use PhantomJS to simulate admin visiting user management page"""
    proc = subprocess.Popen(
        ['timeout', '15', 'phantomjs', '--ignore-ssl-errors=true', '/app/admin_bot.js'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        stdin=subprocess.PIPE
    )
    bot_config = json.dumps({
        'base_url': 'http://127.0.0.1:5000',
        'admin_secret': ADMIN_SECRET_FLAG
    })
    proc.stdin.write(bot_config.encode())
    proc.stdin.close()
    stdout = proc.stdout.read().decode()
    proc.wait()

# ─── HTML Templates ─────────────────────────────────────────────────────────

COMMON_HEADER = '''
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="application-name" content="phpMyFAQ">
<meta name="generator" content="phpMyFAQ 3.1.17">
<link rel="icon" href="/static/favicon.ico" type="image/x-icon">
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; background: #f8f9fa; color: #212529; font-size: 14px; }
  .navbar { background: #343a40; padding: 0.5rem 1rem; display: flex; align-items: center; }
  .navbar a { color: #fff; text-decoration: none; padding: 0.5rem 1rem; }
  .navbar a:hover { color: #adb5bd; }
  .navbar .brand { font-size: 1.2rem; font-weight: bold; margin-right: 2rem; }
  .container { max-width: 1140px; margin: 0 auto; padding: 1rem; }
  .card { background: #fff; border: 1px solid #dee2e6; border-radius: 0.25rem; margin-bottom: 1rem; }
  .card-header { background: #f8f9fa; padding: 0.75rem 1.25rem; border-bottom: 1px solid #dee2e6; font-weight: bold; }
  .card-body { padding: 1.25rem; }
  .btn { display: inline-block; padding: 0.375rem 0.75rem; border: 1px solid transparent; border-radius: 0.25rem; cursor: pointer; text-decoration: none; font-size: 14px; }
  .btn-primary { background: #007bff; color: #fff; border-color: #007bff; }
  .btn-primary:hover { background: #0069d9; }
  .btn-danger { background: #dc3545; color: #fff; border-color: #dc3545; }
  .btn-success { background: #28a745; color: #fff; border-color: #28a745; }
  .form-group { margin-bottom: 1rem; }
  .form-group label { display: block; margin-bottom: 0.5rem; font-weight: 500; }
  .form-control { width: 100%; padding: 0.375rem 0.75rem; border: 1px solid #ced4da; border-radius: 0.25rem; font-size: 14px; }
  table { width: 100%; border-collapse: collapse; }
  th, td { padding: 0.75rem; text-align: left; border-bottom: 1px solid #dee2e6; }
  th { background: #f8f9fa; font-weight: 600; }
  .alert { padding: 0.75rem 1.25rem; border-radius: 0.25rem; margin-bottom: 1rem; }
  .alert-success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
  .alert-danger { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
  .footer { text-align: center; padding: 2rem; color: #6c757d; font-size: 12px; }
  .sidebar { float: left; width: 200px; }
  .sidebar a { display: block; padding: 8px 15px; color: #495057; text-decoration: none; border-left: 3px solid transparent; }
  .sidebar a:hover, .sidebar a.active { background: #e9ecef; border-left-color: #007bff; }
  .main-content { margin-left: 220px; }
  .badge { display: inline-block; padding: 0.25em 0.5em; font-size: 75%; border-radius: 0.25rem; color: #fff; }
  .badge-success { background: #28a745; }
  .badge-warning { background: #ffc107; color: #212529; }
  .badge-info { background: #17a2b8; }
</style>
'''

PUBLIC_NAV = '''
<nav class="navbar">
  <a class="brand" href="/">phpMyFAQ</a>
  <a href="/">Home</a>
  <a href="/login">Login</a>
  <a href="/register">Register</a>
  <a href="/admin/">Admin</a>
</nav>
'''

PUBLIC_INDEX = '''<!DOCTYPE html>
<html lang="en">
<head>
  <title>phpMyFAQ - Open Source FAQ</title>
  ''' + COMMON_HEADER + '''
</head>
<body>
  ''' + PUBLIC_NAV + '''
  <div class="container">
    <h2 style="margin: 1rem 0;">{{ config.get('main.titleFAQ', 'phpMyFAQ') }}</h2>
    <div style="display: flex; gap: 1rem;">
      <div style="flex: 1;">
        <div class="card">
          <div class="card-header">Categories</div>
          <div class="card-body">
            {% for cat in categories %}
            <div style="margin-bottom: 0.5rem;">
              <strong>{{ cat['name'] }}</strong>
              {% if cat['description'] %}<br><small style="color: #6c757d;">{{ cat['description'] }}</small>{% endif %}
            </div>
            {% endfor %}
          </div>
        </div>
      </div>
      <div style="flex: 3;">
        <div class="card">
          <div class="card-header">
            FAQ Articles
            <form action="/api/search" method="get" style="float:right; display:inline;">
              <input type="text" name="q" class="form-control" style="width:200px;display:inline;" placeholder="Search...">
            </form>
          </div>
          <div class="card-body">
            <table>
              <tr><th>Question</th><th>Author</th><th>Updated</th></tr>
              {% for faq in faqs %}
              <tr>
                <td><a href="/faq/{{ faq['id'] }}">{{ faq['thema'] }}</a></td>
                <td>{{ faq['author'] }}</td>
                <td>{{ faq['updated'] }}</td>
              </tr>
              {% endfor %}
            </table>
          </div>
        </div>
      </div>
    </div>
    <div class="footer">
      powered by phpMyFAQ 3.1.17
    </div>
  </div>
</body>
</html>'''

FAQ_DETAIL = '''<!DOCTYPE html>
<html lang="en">
<head>
  <title>{{ faq['thema'] }} - phpMyFAQ</title>
  ''' + COMMON_HEADER + '''
</head>
<body>
  ''' + PUBLIC_NAV + '''
  <div class="container">
    <div class="card" style="margin-top:1rem;">
      <div class="card-header">{{ faq['thema'] }}</div>
      <div class="card-body">
        <p>{{ faq['content'] }}</p>
        <hr>
        <small style="color:#6c757d;">Author: {{ faq['author'] }} | Last updated: {{ faq['updated'] }}</small>
      </div>
    </div>
    <a href="/">&larr; Back to FAQ list</a>
  </div>
</body>
</html>'''

REGISTER_PAGE = '''<!DOCTYPE html>
<html lang="en">
<head>
  <title>Register - phpMyFAQ</title>
  ''' + COMMON_HEADER + '''
</head>
<body>
  ''' + PUBLIC_NAV + '''
  <div class="container" style="max-width:500px; margin-top:2rem;">
    <div class="card">
      <div class="card-header">Create Account</div>
      <div class="card-body">
        {% if error %}<div class="alert alert-danger">{{ error }}</div>{% endif %}
        <form method="post">
          <div class="form-group">
            <label for="login">Username</label>
            <input type="text" name="login" class="form-control" required>
          </div>
          <div class="form-group">
            <label for="password">Password</label>
            <input type="password" name="password" class="form-control" required>
          </div>
          <div class="form-group">
            <label for="display_name">Display Name (Real Name)</label>
            <input type="text" name="display_name" class="form-control">
          </div>
          <div class="form-group">
            <label for="email">Email</label>
            <input type="email" name="email" class="form-control">
          </div>
          <button type="submit" class="btn btn-primary">Register</button>
        </form>
        <p style="margin-top:1rem;"><a href="/login">Already have an account? Login</a></p>
      </div>
    </div>
  </div>
</body>
</html>'''

LOGIN_PAGE = '''<!DOCTYPE html>
<html lang="en">
<head>
  <title>Login - phpMyFAQ</title>
  ''' + COMMON_HEADER + '''
</head>
<body>
  ''' + PUBLIC_NAV + '''
  <div class="container" style="max-width:500px; margin-top:2rem;">
    <div class="card">
      <div class="card-header">User Login</div>
      <div class="card-body">
        {% if error %}<div class="alert alert-danger">{{ error }}</div>{% endif %}
        <form method="post">
          <div class="form-group">
            <label for="login">Username</label>
            <input type="text" name="login" class="form-control" required>
          </div>
          <div class="form-group">
            <label for="password">Password</label>
            <input type="password" name="password" class="form-control" required>
          </div>
          <button type="submit" class="btn btn-primary">Login</button>
        </form>
        <p style="margin-top:1rem;"><a href="/register">Create new account</a></p>
      </div>
    </div>
  </div>
</body>
</html>'''

USER_PROFILE = '''<!DOCTYPE html>
<html lang="en">
<head>
  <title>My Profile - phpMyFAQ</title>
  ''' + COMMON_HEADER + '''
</head>
<body>
  ''' + PUBLIC_NAV + '''
  <div class="container" style="max-width:600px; margin-top:2rem;">
    <div class="card">
      <div class="card-header">My Profile</div>
      <div class="card-body">
        {% if message %}<div class="alert alert-success">{{ message }}</div>{% endif %}
        <form method="post">
          <div class="form-group">
            <label>Username</label>
            <input type="text" class="form-control" value="{{ user['login'] }}" disabled>
          </div>
          <div class="form-group">
            <label for="display_name">Display Name (Real Name)</label>
            <input type="text" name="display_name" class="form-control" value="{{ user['display_name'] }}">
          </div>
          <div class="form-group">
            <label for="email">Email</label>
            <input type="email" name="email" class="form-control" value="{{ user['email'] }}">
          </div>
          <div class="form-group">
            <label>Account Status</label>
            <input type="text" class="form-control" value="{{ user['account_status'] }}" disabled>
          </div>
          <div class="form-group">
            <label>Member Since</label>
            <input type="text" class="form-control" value="{{ user['member_since'] }}" disabled>
          </div>
          <button type="submit" class="btn btn-success">Save Changes</button>
        </form>
        <p style="margin-top:1rem;"><a href="/logout">Logout</a></p>
      </div>
    </div>
  </div>
</body>
</html>'''

ADMIN_LOGIN_PAGE = '''<!DOCTYPE html>
<html lang="en">
<head>
  <title>phpMyFAQ - Admin Login</title>
  ''' + COMMON_HEADER + '''
  <style>
    .admin-login { max-width: 400px; margin: 5rem auto; }
    .admin-header { text-align: center; margin-bottom: 2rem; }
    .admin-header h1 { font-size: 1.5rem; color: #343a40; }
  </style>
</head>
<body>
  <div class="admin-login">
    <div class="admin-header">
      <h1>phpMyFAQ Administration</h1>
      <p style="color:#6c757d;">Version 3.1.17</p>
    </div>
    <div class="card">
      <div class="card-header">Admin Login</div>
      <div class="card-body">
        <form method="post" action="/admin/login">
          <div class="form-group">
            <label for="faqusername">Username</label>
            <input type="text" name="faqusername" id="faqusername" class="form-control" required>
          </div>
          <div class="form-group">
            <label for="faqpassword">Password</label>
            <input type="password" name="faqpassword" id="faqpassword" class="form-control" required>
          </div>
          <button type="submit" class="btn btn-primary" style="width:100%;">Login</button>
        </form>
      </div>
    </div>
    <div class="footer">powered by phpMyFAQ 3.1.17</div>
  </div>
</body>
</html>'''

ADMIN_NAV = '''
<nav class="navbar">
  <a class="brand" href="/admin/dashboard">phpMyFAQ Admin</a>
  <a href="/admin/dashboard">Dashboard</a>
  <a href="/admin/user">Users</a>
  <a href="/admin/content">Content</a>
  <a href="/admin/config">Configuration</a>
  <a href="/logout">Logout</a>
</nav>
'''

ADMIN_DASHBOARD = '''<!DOCTYPE html>
<html lang="en">
<head>
  <title>Admin Dashboard - phpMyFAQ</title>
  ''' + COMMON_HEADER + '''
</head>
<body>
  ''' + ADMIN_NAV + '''
  <div class="container" style="margin-top:1rem;">
    <h2>Dashboard</h2>
    <p style="color:#6c757d;">phpMyFAQ {{ config.get('main.currentVersion', '3.1.17') }}</p>
    <div style="display:flex; gap:1rem; margin-top:1rem;">
      <div class="card" style="flex:1;">
        <div class="card-header">Users</div>
        <div class="card-body"><h3>{{ user_count }}</h3></div>
      </div>
      <div class="card" style="flex:1;">
        <div class="card-header">FAQ Entries</div>
        <div class="card-body"><h3>{{ faq_count }}</h3></div>
      </div>
      <div class="card" style="flex:1;">
        <div class="card-header">Categories</div>
        <div class="card-body"><h3>{{ cat_count }}</h3></div>
      </div>
    </div>
  </div>
</body>
</html>'''

ADMIN_USER_PAGE = '''<!DOCTYPE html>
<html lang="en">
<head>
  <title>User Management - phpMyFAQ Admin</title>
  ''' + COMMON_HEADER + '''
</head>
<body>
  ''' + ADMIN_NAV + '''
  <div class="container" style="margin-top:1rem;">
    <h2>User Management</h2>
    <div class="card" style="margin-top:1rem;">
      <div class="card-header">Registered Users</div>
      <div class="card-body">
        <table>
          <thead>
            <tr><th>ID</th><th>Login</th><th>Display Name</th><th>Email</th><th>Status</th><th>Role</th><th>Actions</th></tr>
          </thead>
          <tbody id="user-table-body">
            <tr><td colspan="7">Loading...</td></tr>
          </tbody>
        </table>
      </div>
    </div>
    <div id="user-detail-modal" style="display:none; margin-top:1rem;">
      <div class="card">
        <div class="card-header">User Details</div>
        <div class="card-body" id="user-detail-content"></div>
      </div>
    </div>
  </div>
  <script>
    // Load user list via AJAX
    function loadUsers() {
      var xhr = new XMLHttpRequest();
      xhr.open('GET', '/admin/ajax/user?action=get_user_list', true);
      xhr.onreadystatechange = function() {
        if (xhr.readyState === 4 && xhr.status === 200) {
          var users = JSON.parse(xhr.responseText);
          var tbody = document.getElementById('user-table-body');
          tbody.innerHTML = '';
          for (var i = 0; i < users.length; i++) {
            var u = users[i];
            var tr = document.createElement('tr');
            tr.innerHTML = '<td>' + u.user_id + '</td>' +
              '<td>' + u.login + '</td>' +
              '<td>' + u.display_name + '</td>' +
              '<td>' + u.email + '</td>' +
              '<td><span class="badge badge-' + (u.account_status === 'active' ? 'success' : 'warning') + '">' + u.account_status + '</span></td>' +
              '<td>' + (u.is_superadmin ? 'Admin' : 'User') + '</td>' +
              '<td><a href="#" onclick="viewUser(' + u.user_id + '); return false;" class="btn btn-primary" style="font-size:12px;">View</a></td>';
            tbody.appendChild(tr);
          }
        }
      };
      xhr.send();
    }

    // View individual user details
    function viewUser(userId) {
      var xhr = new XMLHttpRequest();
      xhr.open('GET', '/admin/ajax/user?action=get_user_data&user_id=' + userId, true);
      xhr.onreadystatechange = function() {
        if (xhr.readyState === 4 && xhr.status === 200) {
          var u = JSON.parse(xhr.responseText);
          var modal = document.getElementById('user-detail-modal');
          var content = document.getElementById('user-detail-content');
          content.innerHTML = '<table>' +
            '<tr><th>User ID</th><td>' + u.user_id + '</td></tr>' +
            '<tr><th>Login</th><td>' + u.login + '</td></tr>' +
            '<tr><th>Display Name</th><td>' + u.display_name + '</td></tr>' +
            '<tr><th>Email</th><td>' + u.email + '</td></tr>' +
            '<tr><th>Status</th><td>' + u.account_status + '</td></tr>' +
            '<tr><th>Auth Source</th><td>' + u.auth_source + '</td></tr>' +
            '<tr><th>Super Admin</th><td>' + (u.is_superadmin ? 'Yes' : 'No') + '</td></tr>' +
            '<tr><th>Member Since</th><td>' + u.member_since + '</td></tr>' +
            '</table>';
          modal.style.display = 'block';
        }
      };
      xhr.send();
    }

    // Load users on page load
    loadUsers();
  </script>
</body>
</html>'''

ADMIN_CONTENT = '''<!DOCTYPE html>
<html lang="en">
<head>
  <title>Content Management - phpMyFAQ Admin</title>
  ''' + COMMON_HEADER + '''
</head>
<body>
  ''' + ADMIN_NAV + '''
  <div class="container" style="margin-top:1rem;">
    <h2>Content Management</h2>
    <div class="card" style="margin-top:1rem;">
      <div class="card-header">FAQ Entries</div>
      <div class="card-body">
        <table>
          <tr><th>ID</th><th>Question</th><th>Author</th><th>Status</th><th>Updated</th></tr>
          {% for faq in faqs %}
          <tr>
            <td>{{ faq['id'] }}</td>
            <td>{{ faq['thema'] }}</td>
            <td>{{ faq['author'] }}</td>
            <td><span class="badge badge-{{ 'success' if faq['active'] == 'yes' else 'warning' }}">{{ faq['active'] }}</span></td>
            <td>{{ faq['updated'] }}</td>
          </tr>
          {% endfor %}
        </table>
      </div>
    </div>
  </div>
</body>
</html>'''

ADMIN_CONFIG = '''<!DOCTYPE html>
<html lang="en">
<head>
  <title>Configuration - phpMyFAQ Admin</title>
  ''' + COMMON_HEADER + '''
</head>
<body>
  ''' + ADMIN_NAV + '''
  <div class="container" style="margin-top:1rem;">
    <h2>Configuration</h2>
    <div class="card" style="margin-top:1rem;">
      <div class="card-header">System Configuration</div>
      <div class="card-body">
        <table>
          <tr><th>Setting</th><th>Value</th></tr>
          {% for c in configs %}
          <tr><td>{{ c['config_name'] }}</td><td>{{ c['config_value'] }}</td></tr>
          {% endfor %}
        </table>
      </div>
    </div>
  </div>
</body>
</html>'''

# ─── Initialize and run ─────────────────────────────────────────────────────

init_db()

# Start admin bot in background thread
bot_thread = threading.Thread(target=admin_bot_loop, daemon=True)
bot_thread.start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
