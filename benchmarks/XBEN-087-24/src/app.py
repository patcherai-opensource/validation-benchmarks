# encoding=utf8

from flask import Flask, request, jsonify, redirect, session
import sqlite3
import subprocess
import os
import hashlib
import time
import json
import logging

logging.basicConfig(level=logging.WARNING)

app = Flask(__name__)
app.secret_key = os.urandom(32).hex()

DB_PATH = '/tmp/faqdata.db'
ADMIN_TOKEN = None

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS faquser (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        login TEXT UNIQUE NOT NULL,
        pass_hash TEXT NOT NULL,
        display_name TEXT DEFAULT '',
        email TEXT DEFAULT '',
        user_status TEXT DEFAULT 'active',
        is_superadmin INTEGER DEFAULT 0,
        is_visible INTEGER DEFAULT 1,
        last_modified TEXT DEFAULT '',
        auth_source TEXT DEFAULT 'local'
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS faqcategory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT DEFAULT '',
        parent_id INTEGER DEFAULT 0,
        lang TEXT DEFAULT 'en'
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS faqdata (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_id INTEGER,
        question TEXT NOT NULL,
        answer TEXT NOT NULL,
        author TEXT DEFAULT '',
        lang TEXT DEFAULT 'en',
        active TEXT DEFAULT 'yes',
        sticky INTEGER DEFAULT 0,
        date_start TEXT DEFAULT '',
        date_end TEXT DEFAULT ''
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS faqsessions (
        sid TEXT PRIMARY KEY,
        user_id INTEGER,
        ip TEXT,
        time INTEGER
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS faqconfig (
        config_name TEXT PRIMARY KEY,
        config_value TEXT
    )''')

    # Insert default config
    try:
        c.execute("INSERT INTO faqconfig VALUES ('main.titleFAQ', 'Knowledge Base')")
        c.execute("INSERT INTO faqconfig VALUES ('main.language', 'en')")
        c.execute("INSERT INTO faqconfig VALUES ('main.currentVersion', '3.1.17')")
        c.execute("INSERT INTO faqconfig VALUES ('main.metaDescription', 'FAQ Management System')")
        c.execute("INSERT INTO faqconfig VALUES ('security.permLevel', 'basic')")
        c.execute("INSERT INTO faqconfig VALUES ('records.defaultActivation', 'true')")
    except sqlite3.IntegrityError:
        pass

    # Create admin user
    admin_pass = hashlib.sha256(os.urandom(32)).hexdigest()
    try:
        c.execute("INSERT INTO faquser (login, pass_hash, display_name, email, user_status, is_superadmin) VALUES (?, ?, ?, ?, ?, ?)",
                  ('admin', hashlib.sha256(admin_pass.encode()).hexdigest(), 'Administrator', 'admin@faq.local', 'protected', 1))
    except sqlite3.IntegrityError:
        pass

    # Insert default categories
    try:
        c.execute("INSERT INTO faqcategory (name, description) VALUES ('General', 'General questions')")
        c.execute("INSERT INTO faqcategory (name, description) VALUES ('Technical', 'Technical support')")
        c.execute("INSERT INTO faqcategory (name, description) VALUES ('Account', 'Account management')")
    except:
        pass

    # Insert sample FAQ entries
    try:
        c.execute("INSERT INTO faqdata (category_id, question, answer, author) VALUES (1, 'How do I get started?', 'Please refer to the Getting Started guide in the documentation section.', 'admin')")
        c.execute("INSERT INTO faqdata (category_id, question, answer, author) VALUES (2, 'What are the system requirements?', 'A modern web browser and an active internet connection.', 'admin')")
        c.execute("INSERT INTO faqdata (category_id, question, answer, author) VALUES (1, 'How do I reset my password?', 'Use the password reset option on the login page.', 'admin')")
    except:
        pass

    conn.commit()
    conn.close()

init_db()

# Read the flag - supports both build-time file and runtime env var
FLAG_VALUE = ''
try:
    with open('flag.txt', 'r') as f:
        FLAG_VALUE = f.read().strip()
except:
    pass
if not FLAG_VALUE or FLAG_VALUE == 'FLAG{default}':
    FLAG_VALUE = os.environ.get('FLAG', 'FLAG{test}')

# Generate a unique admin review token that contains the flag
# This simulates an admin session cookie that contains sensitive data
ADMIN_TOKEN = hashlib.sha256((FLAG_VALUE + str(time.time())).encode()).hexdigest()

# Internal token for PhantomJS review to access the API
_internal_review_token = os.urandom(32).hex()

def html_entities(s):
    """Convert special characters to HTML entities - mirrors Strings::htmlentities"""
    if s is None:
        return ''
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#x27;')

def get_current_user():
    if 'user_id' not in session:
        return None
    conn = get_db()
    user = conn.execute('SELECT * FROM faquser WHERE user_id = ?', (session['user_id'],)).fetchone()
    conn.close()
    return user


# ==================== PUBLIC PAGES ====================

LAYOUT_HEAD = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Knowledge Base</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .navbar {{ background-color: #1e3a5f; }}
        .sidebar {{ min-height: calc(100vh - 56px); background-color: #f8f9fa; padding: 20px; }}
        .content {{ padding: 20px; }}
        .faq-card {{ margin-bottom: 15px; }}
    </style>
</head>
<body>
<nav class="navbar navbar-dark navbar-expand-lg">
    <div class="container-fluid">
        <a class="navbar-brand" href="/">Knowledge Base</a>
        <div class="navbar-nav ms-auto">
            {nav_items}
        </div>
    </div>
</nav>
'''

LAYOUT_FOOT = '''
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>'''

@app.route('/')
def index():
    user = get_current_user()
    if user:
        nav = '<a class="nav-link" href="/profile">Profile</a>'
        if user['is_superadmin']:
            nav += '<a class="nav-link" href="/admin/">Admin</a>'
        nav += '<a class="nav-link" href="/logout">Logout</a>'
    else:
        nav = '<a class="nav-link" href="/login">Login</a><a class="nav-link" href="/register">Register</a>'

    conn = get_db()
    categories = conn.execute('SELECT * FROM faqcategory').fetchall()
    faqs = conn.execute('SELECT f.*, c.name as category_name FROM faqdata f JOIN faqcategory c ON f.category_id = c.id WHERE f.active = "yes" ORDER BY f.id DESC').fetchall()
    conn.close()

    faq_html = ''
    for faq in faqs:
        faq_html += '''
        <div class="card faq-card">
            <div class="card-body">
                <span class="badge bg-secondary">{cat}</span>
                <h5 class="card-title mt-2">{q}</h5>
                <p class="card-text">{a}</p>
            </div>
        </div>'''.format(
            cat=html_entities(faq['category_name']),
            q=html_entities(faq['question']),
            a=html_entities(faq['answer'])
        )

    page = LAYOUT_HEAD.format(title='Home', nav_items=nav) + '''
    <div class="container mt-4">
        <h2>Frequently Asked Questions</h2>
        <hr>
        {faqs}
    </div>'''.format(faqs=faq_html) + LAYOUT_FOOT

    return page

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ''
    if request.method == 'POST':
        username = request.form.get('faqusername', '')
        password = request.form.get('faqpassword', '')
        pass_hash = hashlib.sha256(password.encode()).hexdigest()

        conn = get_db()
        user = conn.execute('SELECT * FROM faquser WHERE login = ? AND pass_hash = ?', (username, pass_hash)).fetchone()
        conn.close()

        if user and user['user_status'] != 'blocked':
            session['user_id'] = user['user_id']
            if user['is_superadmin']:
                return redirect('/admin/')
            return redirect('/')
        else:
            error = '<div class="alert alert-danger">Invalid credentials or account is blocked.</div>'

    page = LAYOUT_HEAD.format(title='Login', nav_items='<a class="nav-link" href="/register">Register</a>') + '''
    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-4">
                <div class="card">
                    <div class="card-body">
                        <h4 class="card-title text-center">Sign In</h4>
                        {error}
                        <form method="POST">
                            <div class="mb-3">
                                <label for="faqusername" class="form-label">Username</label>
                                <input type="text" class="form-control" id="faqusername" name="faqusername" required>
                            </div>
                            <div class="mb-3">
                                <label for="faqpassword" class="form-label">Password</label>
                                <input type="password" class="form-control" id="faqpassword" name="faqpassword" required>
                            </div>
                            <button type="submit" class="btn btn-primary w-100">Login</button>
                        </form>
                        <p class="mt-3 text-center"><a href="/register">Create an account</a></p>
                    </div>
                </div>
            </div>
        </div>
    </div>'''.format(error=error) + LAYOUT_FOOT

    return page

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = ''
    success = ''
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        realname = request.form.get('realname', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')

        if not username or not realname or not email:
            error = '<div class="alert alert-danger">All fields are required.</div>'
        elif len(password) < 8:
            error = '<div class="alert alert-danger">Password must be at least 8 characters.</div>'
        elif password != password_confirm:
            error = '<div class="alert alert-danger">Passwords do not match.</div>'
        else:
            conn = get_db()
            existing = conn.execute('SELECT user_id FROM faquser WHERE login = ?', (username,)).fetchone()
            if existing:
                error = '<div class="alert alert-danger">Username already exists.</div>'
                conn.close()
            else:
                pass_hash = hashlib.sha256(password.encode()).hexdigest()
                conn.execute('INSERT INTO faquser (login, pass_hash, display_name, email) VALUES (?, ?, ?, ?)',
                             (username, pass_hash, realname, email))
                conn.commit()
                conn.close()
                success = '<div class="alert alert-success">Account created successfully. <a href="/login">Login here</a>.</div>'

    page = LAYOUT_HEAD.format(title='Register', nav_items='<a class="nav-link" href="/login">Login</a>') + '''
    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-5">
                <div class="card">
                    <div class="card-body">
                        <h4 class="card-title text-center">Create Account</h4>
                        {error}{success}
                        <form method="POST">
                            <div class="mb-3">
                                <label for="username" class="form-label">Username</label>
                                <input type="text" class="form-control" id="username" name="username" required>
                            </div>
                            <div class="mb-3">
                                <label for="realname" class="form-label">Real Name</label>
                                <input type="text" class="form-control" id="realname" name="realname" required>
                            </div>
                            <div class="mb-3">
                                <label for="email" class="form-label">Email</label>
                                <input type="email" class="form-control" id="email" name="email" required>
                            </div>
                            <div class="mb-3">
                                <label for="password" class="form-label">Password</label>
                                <input type="password" class="form-control" id="password" name="password" minlength="8" required>
                            </div>
                            <div class="mb-3">
                                <label for="password_confirm" class="form-label">Confirm Password</label>
                                <input type="password" class="form-control" id="password_confirm" name="password_confirm" minlength="8" required>
                            </div>
                            <button type="submit" class="btn btn-primary w-100">Register</button>
                        </form>
                        <p class="mt-3 text-center">Already have an account? <a href="/login">Login</a></p>
                    </div>
                </div>
            </div>
        </div>
    </div>'''.format(error=error, success=success) + LAYOUT_FOOT

    return page

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    user = get_current_user()
    if not user:
        return redirect('/login')

    message = ''
    if request.method == 'POST':
        display_name = request.form.get('display_name', '')
        email = request.form.get('email', '')

        conn = get_db()
        conn.execute('UPDATE faquser SET display_name = ?, email = ?, last_modified = ? WHERE user_id = ?',
                     (display_name, email, str(int(time.time())), user['user_id']))
        conn.commit()
        conn.close()
        message = '<div class="alert alert-success">Profile updated successfully.</div>'
        # Re-fetch user
        user = get_current_user()

    nav = '<a class="nav-link" href="/">Home</a>'
    if user['is_superadmin']:
        nav += '<a class="nav-link" href="/admin/">Admin</a>'
    nav += '<a class="nav-link" href="/logout">Logout</a>'

    page = LAYOUT_HEAD.format(title='Profile', nav_items=nav) + '''
    <div class="container mt-4">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header"><h5>Edit Profile</h5></div>
                    <div class="card-body">
                        {message}
                        <form method="POST">
                            <div class="mb-3">
                                <label class="form-label">Username</label>
                                <input type="text" class="form-control" value="{login}" disabled>
                            </div>
                            <div class="mb-3">
                                <label for="display_name" class="form-label">Display Name</label>
                                <input type="text" class="form-control" id="display_name" name="display_name" value="{display_name}">
                            </div>
                            <div class="mb-3">
                                <label for="email" class="form-label">Email</label>
                                <input type="email" class="form-control" id="email" name="email" value="{email}">
                            </div>
                            <button type="submit" class="btn btn-primary">Save Changes</button>
                        </form>
                    </div>
                </div>
                <div class="card mt-3">
                    <div class="card-header"><h6>Account Verification</h6></div>
                    <div class="card-body">
                        <p class="text-muted">Request an administrator to verify your profile information.</p>
                        <div id="verify-result"></div>
                        <button class="btn btn-outline-secondary btn-sm" id="btn-verify">Request Admin Verification</button>
                        <script>
                        document.getElementById('btn-verify').addEventListener('click', function() {{
                            var fd = new FormData();
                            fd.append('member_id', '{user_id}');
                            fetch('/admin/api/review-member', {{
                                method: 'POST',
                                body: fd
                            }})
                            .then(function(r) {{ return r.json(); }})
                            .then(function(data) {{
                                document.getElementById('verify-result').innerHTML =
                                    '<div class="alert alert-info mt-2">' + data.admin_notes + '</div>';
                            }})
                            .catch(function(e) {{
                                document.getElementById('verify-result').innerHTML =
                                    '<div class="alert alert-danger mt-2">Verification request failed.</div>';
                            }});
                        }});
                        </script>
                    </div>
                </div>
            </div>
        </div>
    </div>'''.format(
        message=message,
        login=html_entities(user['login']),
        display_name=html_entities(user['display_name'] or ''),
        email=html_entities(user['email'] or ''),
        user_id=user['user_id']
    ) + LAYOUT_FOOT

    return page

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


# ==================== ADMIN PANEL ====================

ADMIN_LAYOUT_HEAD = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Admin Panel</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .sidebar {{ min-height: calc(100vh - 56px); background-color: #343a40; padding-top: 20px; }}
        .sidebar a {{ color: #adb5bd; display: block; padding: 8px 16px; text-decoration: none; }}
        .sidebar a:hover, .sidebar a.active {{ color: #fff; background-color: #495057; }}
        .content-area {{ padding: 20px; }}
        .navbar {{ background-color: #1e3a5f; }}
        .user-table td {{ vertical-align: middle; }}
    </style>
</head>
<body>
<nav class="navbar navbar-dark navbar-expand-lg">
    <div class="container-fluid">
        <a class="navbar-brand" href="/admin/">Admin Panel</a>
        <div class="navbar-nav ms-auto">
            <a class="nav-link" href="/">Public Site</a>
            <a class="nav-link" href="/logout">Logout</a>
        </div>
    </div>
</nav>
<div class="container-fluid">
    <div class="row">
        <nav class="col-md-2 sidebar">
            <a href="/admin/">Dashboard</a>
            <a href="/admin/content">Content</a>
            <a href="/admin/members">User Management</a>
            <a href="/admin/categories">Categories</a>
            <a href="/admin/settings">Configuration</a>
        </nav>
        <main class="col-md-10 content-area">
'''

ADMIN_LAYOUT_FOOT = '''
        </main>
    </div>
</div>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>'''

def require_admin(f):
    """Decorator to require admin authentication"""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user()
        if not user or not user['is_superadmin']:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated

@app.route('/admin/')
@require_admin
def admin_dashboard():
    conn = get_db()
    user_count = conn.execute('SELECT COUNT(*) as cnt FROM faquser').fetchone()['cnt']
    faq_count = conn.execute('SELECT COUNT(*) as cnt FROM faqdata').fetchone()['cnt']
    cat_count = conn.execute('SELECT COUNT(*) as cnt FROM faqcategory').fetchone()['cnt']
    conn.close()

    content = '''
        <h3>Dashboard</h3>
        <hr>
        <div class="row">
            <div class="col-md-4">
                <div class="card text-white bg-primary mb-3">
                    <div class="card-body">
                        <h5 class="card-title">{users}</h5>
                        <p class="card-text">Registered Users</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card text-white bg-success mb-3">
                    <div class="card-body">
                        <h5 class="card-title">{faqs}</h5>
                        <p class="card-text">FAQ Entries</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card text-white bg-info mb-3">
                    <div class="card-body">
                        <h5 class="card-title">{cats}</h5>
                        <p class="card-text">Categories</p>
                    </div>
                </div>
            </div>
        </div>
    '''.format(users=user_count, faqs=faq_count, cats=cat_count)

    return ADMIN_LAYOUT_HEAD.format(title='Dashboard') + content + ADMIN_LAYOUT_FOOT

@app.route('/admin/members')
@require_admin
def admin_members():
    content = '''
        <h3>User Management</h3>
        <hr>
        <div id="faq-user-message"></div>
        <div class="mb-3">
            <input type="text" class="form-control" id="memberSearch" placeholder="Search users..." style="max-width:300px">
        </div>
        <table class="table table-striped user-table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Username</th>
                    <th>Display Name</th>
                    <th>Email</th>
                    <th>Status</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody id="memberTableBody">
            </tbody>
        </table>

        <!-- Member detail modal -->
        <div class="modal fade" id="memberDetailModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">User Details</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body" id="memberDetailBody">
                    </div>
                </div>
            </div>
        </div>

        <script>
        function loadMemberList() {
            fetch('/admin/api/member-list')
                .then(r => r.json())
                .then(data => {
                    const tbody = document.getElementById('memberTableBody');
                    tbody.innerHTML = '';
                    data.forEach(u => {
                        const tr = document.createElement('tr');
                        tr.className = 'row_user_id_' + u.id;
                        tr.innerHTML = '<td>' + u.id + '</td>' +
                            '<td>' + u.userName + '</td>' +
                            '<td>' + u.displayName + '</td>' +
                            '<td>' + u.email + '</td>' +
                            '<td><span class="badge bg-' + (u.status === 'active' ? 'success' : (u.status === 'blocked' ? 'danger' : 'warning')) + '">' + u.status + '</span></td>' +
                            '<td><button class="btn btn-sm btn-outline-primary" onclick="viewMember(' + u.id + ')">View</button></td>';
                        tbody.appendChild(tr);
                    });
                });
        }

        function viewMember(userId) {
            fetch('/admin/api/member-data?member_id=' + userId)
                .then(r => r.json())
                .then(data => {
                    const body = document.getElementById('memberDetailBody');
                    body.innerHTML = '<table class="table">' +
                        '<tr><th>User ID</th><td>' + data.user_id + '</td></tr>' +
                        '<tr><th>Login</th><td>' + data.login + '</td></tr>' +
                        '<tr><th>Display Name</th><td>' + data.display_name + '</td></tr>' +
                        '<tr><th>Email</th><td>' + data.email + '</td></tr>' +
                        '<tr><th>Status</th><td>' + data.status + '</td></tr>' +
                        '<tr><th>Super Admin</th><td>' + (data.is_superadmin ? 'Yes' : 'No') + '</td></tr>' +
                        '</table>';
                    new bootstrap.Modal(document.getElementById('memberDetailModal')).show();
                });
        }

        document.getElementById('memberSearch').addEventListener('input', function() {
            const q = this.value;
            if (q.length > 0) {
                fetch('/admin/api/member-search?q=' + encodeURIComponent(q))
                    .then(r => r.json())
                    .then(data => {
                        const tbody = document.getElementById('memberTableBody');
                        tbody.innerHTML = '';
                        data.forEach(u => {
                            const tr = document.createElement('tr');
                            tr.innerHTML = '<td>' + u.user_id + '</td>' +
                                '<td>' + u.name + '</td>' +
                                '<td colspan="4"><button class="btn btn-sm btn-outline-primary" onclick="viewMember(' + u.user_id + ')">View</button></td>';
                            tbody.appendChild(tr);
                        });
                    });
            } else {
                loadMemberList();
            }
        });

        loadMemberList();
        </script>
    '''

    return ADMIN_LAYOUT_HEAD.format(title='User Management') + content + ADMIN_LAYOUT_FOOT

@app.route('/admin/content')
@require_admin
def admin_content():
    conn = get_db()
    faqs = conn.execute('SELECT f.*, c.name as category_name FROM faqdata f JOIN faqcategory c ON f.category_id = c.id ORDER BY f.id DESC').fetchall()
    conn.close()

    rows = ''
    for faq in faqs:
        rows += '<tr><td>{id}</td><td>{cat}</td><td>{q}</td><td>{status}</td></tr>'.format(
            id=faq['id'],
            cat=html_entities(faq['category_name']),
            q=html_entities(faq['question']),
            status=faq['active']
        )

    content = '''
        <h3>Content Management</h3>
        <hr>
        <table class="table table-striped">
            <thead><tr><th>ID</th><th>Category</th><th>Question</th><th>Status</th></tr></thead>
            <tbody>{rows}</tbody>
        </table>
    '''.format(rows=rows)

    return ADMIN_LAYOUT_HEAD.format(title='Content') + content + ADMIN_LAYOUT_FOOT

@app.route('/admin/categories')
@require_admin
def admin_categories():
    conn = get_db()
    cats = conn.execute('SELECT * FROM faqcategory ORDER BY id').fetchall()
    conn.close()

    rows = ''
    for cat in cats:
        rows += '<tr><td>{id}</td><td>{name}</td><td>{desc}</td></tr>'.format(
            id=cat['id'],
            name=html_entities(cat['name']),
            desc=html_entities(cat['description'])
        )

    content = '''
        <h3>Category Management</h3>
        <hr>
        <table class="table table-striped">
            <thead><tr><th>ID</th><th>Name</th><th>Description</th></tr></thead>
            <tbody>{rows}</tbody>
        </table>
    '''.format(rows=rows)

    return ADMIN_LAYOUT_HEAD.format(title='Categories') + content + ADMIN_LAYOUT_FOOT

@app.route('/admin/settings')
@require_admin
def admin_settings():
    conn = get_db()
    configs = conn.execute('SELECT * FROM faqconfig ORDER BY config_name').fetchall()
    conn.close()

    rows = ''
    for c in configs:
        rows += '<tr><td>{name}</td><td>{val}</td></tr>'.format(
            name=html_entities(c['config_name']),
            val=html_entities(c['config_value'])
        )

    content = '''
        <h3>Configuration</h3>
        <hr>
        <table class="table table-striped">
            <thead><tr><th>Setting</th><th>Value</th></tr></thead>
            <tbody>{rows}</tbody>
        </table>
    '''.format(rows=rows)

    return ADMIN_LAYOUT_HEAD.format(title='Configuration') + content + ADMIN_LAYOUT_FOOT


# ==================== ADMIN AJAX API ====================
# These endpoints mirror phpMyFAQ's admin/ajax.user.php

@app.route('/admin/api/member-search')
@require_admin
def api_member_search():
    q = request.args.get('q', '')
    conn = get_db()
    users = conn.execute('SELECT user_id, login FROM faquser WHERE login LIKE ?', ('%' + q + '%',)).fetchall()
    conn.close()

    result = []
    for u in users:
        result.append({
            'user_id': u['user_id'],
            'name': html_entities(u['login'])
        })
    return jsonify(result)

@app.route('/admin/api/member-data')
def api_member_data():
    """
    Fetch individual member data - equivalent to get_user_data action.
    Returns user details as JSON for the admin interface.
    Requires admin session or valid internal review token.
    """
    user = get_current_user()
    review_token = request.args.get('_rt', '')
    if (not user or not user['is_superadmin']) and review_token != _internal_review_token:
        return redirect('/login')

    member_id = request.args.get('member_id', type=int)
    if not member_id:
        return jsonify({'error': 'No user ID provided'}), 400

    conn = get_db()
    user_row = conn.execute('SELECT * FROM faquser WHERE user_id = ?', (member_id,)).fetchone()
    conn.close()

    if not user_row:
        return jsonify({'error': 'User not found'}), 404

    userdata = {
        'user_id': user_row['user_id'],
        'login': html_entities(user_row['login']),
        'display_name': user_row['display_name'],  # Not sanitized - mirrors the CVE
        'email': user_row['email'],
        'status': user_row['user_status'],
        'is_superadmin': bool(user_row['is_superadmin']),
        'is_visible': bool(user_row['is_visible']),
        'last_modified': user_row['last_modified'] or '',
        'auth_source': user_row['auth_source']
    }
    return jsonify(userdata)

@app.route('/admin/api/member-list')
@require_admin
def api_member_list():
    """
    Fetch all member data - equivalent to get_all_user_data action.
    Returns list of all users with their details.
    """
    conn = get_db()
    users = conn.execute('SELECT * FROM faquser ORDER BY user_id').fetchall()
    conn.close()

    result = []
    for u in users:
        result.append({
            'id': u['user_id'],
            'status': u['user_status'],
            'isSuperAdmin': bool(u['is_superadmin']),
            'isVisible': bool(u['is_visible']),
            'displayName': u['display_name'],  # Not sanitized - mirrors the CVE
            'userName': html_entities(u['login']),
            'email': u['email']
        })
    return jsonify(result)


# ==================== REPORT ENDPOINT ====================
# Simulates admin reviewing user profiles in the management panel.
# When an admin views user details, the front-end JS fetches user data
# via AJAX and renders it into the DOM - including the display_name field.

@app.route('/admin/api/review-member', methods=['POST'])
def api_review_member():
    """
    Triggers an admin review of a user profile. This simulates what happens
    when an admin opens the user management page and the browser renders
    user data including display_name from the AJAX JSON response.

    Any authenticated user can request that an admin reviews their profile.
    """
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401

    member_id = request.form.get('member_id') or request.args.get('member_id')
    if not member_id:
        return jsonify({'error': 'member_id required'}), 400

    try:
        member_id = int(member_id)
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid member_id'}), 400

    conn = get_db()
    target_user = conn.execute('SELECT * FROM faquser WHERE user_id = ?', (member_id,)).fetchone()
    conn.close()

    if not target_user:
        return jsonify({'error': 'User not found'}), 404

    # Build the page that simulates the admin panel rendering user data.
    # This mirrors exactly how phpMyFAQ's admin/user.php + user.js works:
    # 1. The admin interface loads user data as JSON from the AJAX endpoint
    # 2. The JS uses innerHTML to render user fields into the DOM
    # 3. The display_name field is NOT sanitized in the JSON response (the bug)
    # 4. So any HTML/JS in display_name gets executed in the admin's browser context
    #
    # The admin's browser has access to a sensitive session token stored in the DOM
    admin_session_token = ADMIN_TOKEN

    app_host = os.environ.get('APP_HOST', 'localhost')
    app_port = os.environ.get('APP_PORT', '5000')
    api_url = 'http://' + app_host + ':' + app_port + '/admin/api/member-data?member_id=' + str(member_id) + '&_rt=' + _internal_review_token

    review_page = '<!DOCTYPE html>\n<html>\n<head><title>User Management - Admin Panel</title></head>\n<body>\n'
    review_page += '<h3>User Details</h3>\n<div id="memberDetailBody"></div>\n'
    review_page += '<script>\n'
    review_page += 'document.cookie = "session_token=' + admin_session_token + '; path=/";\n'
    review_page += 'var xhr = new XMLHttpRequest();\n'
    review_page += 'xhr.open("GET", "' + api_url + '", true);\n'
    review_page += 'xhr.onreadystatechange = function() {\n'
    review_page += '    if (xhr.readyState === 4 && xhr.status === 200) {\n'
    review_page += '        var data = JSON.parse(xhr.responseText);\n'
    review_page += '        var body = document.getElementById("memberDetailBody");\n'
    review_page += '        body.innerHTML = \'<table>\' +\n'
    review_page += '            \'<tr><th>User ID</th><td>\' + data.user_id + \'</td></tr>\' +\n'
    review_page += '            \'<tr><th>Login</th><td>\' + data.login + \'</td></tr>\' +\n'
    review_page += '            \'<tr><th>Display Name</th><td>\' + data.display_name + \'</td></tr>\' +\n'
    review_page += '            \'<tr><th>Email</th><td>\' + data.email + \'</td></tr>\' +\n'
    review_page += '            \'<tr><th>Status</th><td>\' + data.status + \'</td></tr>\' +\n'
    review_page += '            \'</table>\';\n'
    review_page += '    }\n'
    review_page += '};\n'
    review_page += 'xhr.send();\n'
    review_page += '</script>\n</body>\n</html>'

    # Write the review page to a temp file and open with PhantomJS
    # This simulates the admin's browser rendering the user management page
    fn = "static/" + os.urandom(16).hex() + '.html'
    url = 'http://' + app_host + ':' + app_port + '/' + fn

    result_text = ''
    try:
        os.makedirs('static', exist_ok=True)
        with open(fn, 'w') as of:
            of.write(review_page)

        proc = subprocess.Popen(
            ["timeout", "10", "phantomjs", "review_check.js"],
            stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE
        )
        proc.stdin.write(url.encode())
        proc.stdin.close()
        result_text = proc.stdout.read().decode().strip()
        proc.wait()
    except Exception as e:
        logging.error("Review error: %s", str(e))
    finally:
        try:
            os.unlink(fn)
        except:
            pass

    # Check if the stored XSS was able to exfiltrate the admin session token
    if admin_session_token and admin_session_token in result_text:
        return jsonify({
            'status': 'reviewed',
            'admin_notes': FLAG_VALUE
        })
    else:
        return jsonify({
            'status': 'reviewed',
            'admin_notes': 'Profile reviewed successfully. No issues detected.'
        })

# Health check
@app.route('/ping')
def ping():
    return 'OK'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
