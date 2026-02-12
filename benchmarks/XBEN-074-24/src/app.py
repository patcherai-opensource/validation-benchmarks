# encoding=utf8

from flask import Flask, request, make_response, redirect, url_for, g, session
import subprocess
import os
import re
import sys
import json
import sqlite3
import hashlib
import time
import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

app = Flask(__name__)
app.secret_key = os.urandom(24).encode('hex')

DATABASE = '/python-docker/data/ezplatform.db'

# ─── Database helpers ───────────────────────────────────────────────────────

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
    if not os.path.exists(os.path.dirname(DATABASE)):
        os.makedirs(os.path.dirname(DATABASE))
    db = sqlite3.connect(DATABASE)
    db.execute('''CREATE TABLE IF NOT EXISTS ezuser (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        login TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        email TEXT,
        role TEXT DEFAULT 'viewer'
    )''')
    db.execute('''CREATE TABLE IF NOT EXISTS ezcontentobject (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        section_id INTEGER DEFAULT 1,
        owner_id INTEGER,
        published INTEGER,
        modified INTEGER,
        status INTEGER DEFAULT 1
    )''')
    db.execute('''CREATE TABLE IF NOT EXISTS ezcontentobject_attribute (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        contentobject_id INTEGER NOT NULL,
        data_type_string TEXT DEFAULT 'ezrichtext',
        data_text TEXT,
        sort_key_string TEXT DEFAULT '',
        FOREIGN KEY(contentobject_id) REFERENCES ezcontentobject(id)
    )''')
    db.execute('''CREATE TABLE IF NOT EXISTS ezsection (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        identifier TEXT UNIQUE
    )''')
    db.execute('''CREATE TABLE IF NOT EXISTS ezcontentobject_version (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        contentobject_id INTEGER,
        version INTEGER DEFAULT 1,
        creator_id INTEGER,
        created INTEGER,
        status INTEGER DEFAULT 1
    )''')
    # Seed sections
    db.execute("INSERT OR IGNORE INTO ezsection (id, name, identifier) VALUES (1, 'Standard', 'standard')")
    db.execute("INSERT OR IGNORE INTO ezsection (id, name, identifier) VALUES (2, 'Media', 'media')")
    db.execute("INSERT OR IGNORE INTO ezsection (id, name, identifier) VALUES (3, 'Setup', 'setup')")
    # Seed default users
    admin_hash = hashlib.sha256('admin:Publish2024!').hexdigest()
    editor_hash = hashlib.sha256('editor:Edit0rPass!').hexdigest()
    db.execute("INSERT OR IGNORE INTO ezuser (id, login, password_hash, email, role) VALUES (1, 'admin', ?, 'admin@ezplatform.local', 'admin')", (admin_hash,))
    db.execute("INSERT OR IGNORE INTO ezuser (id, login, password_hash, email, role) VALUES (2, 'editor', ?, 'editor@ezplatform.local', 'editor')", (editor_hash,))
    # Seed welcome article
    now = int(time.time())
    db.execute("INSERT OR IGNORE INTO ezcontentobject (id, name, section_id, owner_id, published, modified, status) VALUES (1, 'Welcome to eZ Platform', 1, 1, ?, ?, 1)", (now, now))
    db.execute("INSERT OR IGNORE INTO ezcontentobject_attribute (id, contentobject_id, data_type_string, data_text) VALUES (1, 1, 'ezrichtext', ?)",
        ('<section xmlns="http://docbook.org/ns/docbook"><para>Welcome to our content management platform. Use the editor to create and manage rich text content.</para></section>',))
    db.execute("INSERT OR IGNORE INTO ezcontentobject_version (contentobject_id, version, creator_id, created, status) VALUES (1, 1, 1, ?, 1)", (now,))
    db.commit()
    db.close()

init_db()

# ─── RichText Validator (Schematron-like) ───────────────────────────────────
# Validates DocBook XML content, blocking dangerous link protocols.
# Based on docbook.iso.sch validation rules.

def validate_richtext_links(content):
    """
    Validate that links in the content do not use script protocols.
    Mirrors the Schematron assertion in docbook.iso.sch:
      assert test="not(contains(@xlink:href, 'javascript:') or contains(@xlink:href, 'vbscript:'))"
    """
    blocked_protocols = ['javascript:', 'vbscript:']
    
    # Extract href values from links
    href_pattern = re.compile(r'href\s*=\s*["\']([^"\']*)["\']', re.DOTALL)
    matches = href_pattern.findall(content)
    
    for href in matches:
        for proto in blocked_protocols:
            if proto in href:
                return False, "Using scripts in links is not allowed"
    
    return True, None


def richtext_to_html(docbook_content):
    """Convert stored DocBook-like richtext to rendered HTML."""
    html = docbook_content
    # Convert section tags
    html = re.sub(r'<section[^>]*>', '<div class="ez-richtext-section">', html)
    html = html.replace('</section>', '</div>')
    # Convert para tags
    html = html.replace('<para>', '<p>').replace('</para>', '</p>')
    # Convert link tags - preserve href directly
    html = re.sub(r'<link\s+[^>]*xlink:href\s*=\s*"([^"]*)"[^>]*>', r'<a href="\1">', html)
    html = re.sub(r'<link\s+[^>]*href\s*=\s*"([^"]*)"[^>]*>', r'<a href="\1">', html)
    html = html.replace('</link>', '</a>')
    return html


# ─── Templates ──────────────────────────────────────────────────────────────

LAYOUT_HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="generator" content="eZ Platform v3.3">
    <title>{title} - eZ Platform</title>
    <link rel="icon" href="/static/assets/fav-icon.png">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; color: #333; }}
        .ez-header {{ background: #1a1a2e; color: #fff; padding: 12px 24px; display: flex; justify-content: space-between; align-items: center; }}
        .ez-header h1 {{ font-size: 18px; font-weight: 500; }}
        .ez-header h1 span {{ color: #f47920; }}
        .ez-header nav a {{ color: #ccc; text-decoration: none; margin-left: 20px; font-size: 14px; }}
        .ez-header nav a:hover {{ color: #fff; }}
        .ez-container {{ max-width: 960px; margin: 0 auto; padding: 24px; }}
        .ez-breadcrumb {{ font-size: 13px; color: #666; margin-bottom: 16px; }}
        .ez-breadcrumb a {{ color: #f47920; text-decoration: none; }}
        .ez-card {{ background: #fff; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); padding: 24px; margin-bottom: 16px; }}
        .ez-card h2 {{ margin-bottom: 16px; font-size: 22px; }}
        .ez-card .meta {{ font-size: 12px; color: #999; margin-bottom: 12px; }}
        .ez-richtext-section {{ line-height: 1.7; }}
        .ez-richtext-section a {{ color: #f47920; }}
        .ez-btn {{ display: inline-block; padding: 8px 20px; background: #f47920; color: #fff; border: none; border-radius: 3px; cursor: pointer; text-decoration: none; font-size: 14px; }}
        .ez-btn:hover {{ background: #e0681a; }}
        .ez-btn-secondary {{ background: #6c757d; }}
        .ez-btn-secondary:hover {{ background: #5a6268; }}
        .ez-form-group {{ margin-bottom: 16px; }}
        .ez-form-group label {{ display: block; margin-bottom: 4px; font-weight: 500; font-size: 14px; }}
        .ez-form-group input, .ez-form-group textarea, .ez-form-group select {{ width: 100%; padding: 8px 12px; border: 1px solid #ddd; border-radius: 3px; font-size: 14px; }}
        .ez-form-group textarea {{ min-height: 200px; font-family: monospace; }}
        .ez-alert {{ padding: 12px 16px; border-radius: 3px; margin-bottom: 16px; font-size: 14px; }}
        .ez-alert-danger {{ background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }}
        .ez-alert-success {{ background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
        .ez-alert-info {{ background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }}
        .content-list {{ list-style: none; }}
        .content-list li {{ padding: 12px 0; border-bottom: 1px solid #eee; }}
        .content-list li:last-child {{ border-bottom: none; }}
        .content-list a {{ color: #333; text-decoration: none; font-weight: 500; }}
        .content-list a:hover {{ color: #f47920; }}
        .content-list .meta {{ font-size: 12px; color: #999; }}
        .login-wrap {{ max-width: 400px; margin: 60px auto; }}
        .footer {{ text-align: center; padding: 20px; color: #999; font-size: 12px; }}
    </style>
</head>
<body>"""

LAYOUT_HEADER_AUTHED = """
<div class="ez-header">
    <h1>e<span>Z</span> Platform</h1>
    <nav>
        <a href="/content/list">Content</a>
        <a href="/content/create">New Article</a>
        <a href="/user/logout">Logout ({user})</a>
    </nav>
</div>"""

LAYOUT_HEADER_PUBLIC = """
<div class="ez-header">
    <h1>e<span>Z</span> Platform</h1>
    <nav>
        <a href="/">Home</a>
        <a href="/user/login">Login</a>
    </nav>
</div>"""

LAYOUT_FOOTER = """
<div class="footer">
    &copy; eZ Systems. eZ Platform v3.3.
</div>
</body>
</html>"""


# ─── Auth helpers ───────────────────────────────────────────────────────────

def get_current_user():
    if 'user_id' not in session:
        return None
    db = get_db()
    user = db.execute('SELECT * FROM ezuser WHERE id = ?', (session['user_id'],)).fetchone()
    return user

def require_editor(f):
    """Decorator that requires editor or admin role."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user()
        if not user:
            return redirect('/user/login')
        if user['role'] not in ('editor', 'admin'):
            return make_response('Forbidden', 403)
        return f(*args, **kwargs)
    return decorated


# ─── Routes ─────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    db = get_db()
    articles = db.execute(
        'SELECT c.id, c.name, c.published, c.modified, u.login as author '
        'FROM ezcontentobject c LEFT JOIN ezuser u ON c.owner_id = u.id '
        'WHERE c.status = 1 ORDER BY c.modified DESC LIMIT 10'
    ).fetchall()
    
    article_html = ''
    for a in articles:
        article_html += '<li><a href="/content/view/{id}">{name}</a><div class="meta">by {author}</div></li>'.format(
            id=a['id'], name=a['name'], author=a['author'] or 'System')
    
    page = LAYOUT_HEAD.format(title='Home')
    user = get_current_user()
    if user:
        page += LAYOUT_HEADER_AUTHED.format(user=user['login'])
    else:
        page += LAYOUT_HEADER_PUBLIC
    page += """
    <div class="ez-container">
        <div class="ez-card">
            <h2>Published Content</h2>
            <ul class="content-list">{articles}</ul>
        </div>
    </div>""".format(articles=article_html if article_html else '<li>No content published yet.</li>')
    page += LAYOUT_FOOTER
    return page


@app.route('/user/login', methods=['GET', 'POST'])
def login():
    error = ''
    if request.method == 'POST':
        login_name = request.form.get('login', '')
        password = request.form.get('password', '')
        pw_hash = hashlib.sha256('{}:{}'.format(login_name, password)).hexdigest()
        db = get_db()
        user = db.execute('SELECT * FROM ezuser WHERE login = ? AND password_hash = ?', (login_name, pw_hash)).fetchone()
        if user:
            session['user_id'] = user['id']
            return redirect('/content/list')
        error = 'Invalid credentials.'
    
    page = LAYOUT_HEAD.format(title='Login')
    page += LAYOUT_HEADER_PUBLIC
    page += """
    <div class="login-wrap">
        <div class="ez-card">
            <h2>Sign in</h2>
            {error}
            <form method="post">
                <div class="ez-form-group">
                    <label>Username</label>
                    <input type="text" name="login" required>
                </div>
                <div class="ez-form-group">
                    <label>Password</label>
                    <input type="password" name="password" required>
                </div>
                <button class="ez-btn" type="submit">Login</button>
            </form>
        </div>
    </div>""".format(error='<div class="ez-alert ez-alert-danger">{}</div>'.format(error) if error else '')
    page += LAYOUT_FOOTER
    return page


@app.route('/user/logout')
def logout():
    session.clear()
    return redirect('/')


@app.route('/content/list')
@require_editor
def content_list():
    user = get_current_user()
    db = get_db()
    articles = db.execute(
        'SELECT c.id, c.name, c.published, c.modified, c.status, u.login as author '
        'FROM ezcontentobject c LEFT JOIN ezuser u ON c.owner_id = u.id '
        'ORDER BY c.modified DESC'
    ).fetchall()
    
    rows = ''
    for a in articles:
        rows += '<li><a href="/content/view/{id}">{name}</a> <span class="meta">by {author} &mdash; <a href="/content/edit/{id}">Edit</a></span></li>'.format(
            id=a['id'], name=a['name'], author=a['author'] or 'System')
    
    page = LAYOUT_HEAD.format(title='Content List')
    page += LAYOUT_HEADER_AUTHED.format(user=user['login'])
    page += """
    <div class="ez-container">
        <div class="ez-breadcrumb"><a href="/">Home</a> / Content</div>
        <div class="ez-card">
            <h2>Content Objects</h2>
            <p><a class="ez-btn" href="/content/create">Create New Article</a></p>
            <ul class="content-list">{rows}</ul>
        </div>
    </div>""".format(rows=rows if rows else '<li>No content yet.</li>')
    page += LAYOUT_FOOTER
    return page


@app.route('/content/create', methods=['GET', 'POST'])
@require_editor
def content_create():
    user = get_current_user()
    error = ''
    success = ''
    name_val = ''
    body_val = ''
    
    if request.method == 'POST':
        name_val = request.form.get('name', '').strip()
        body_val = request.form.get('body', '').strip()
        
        if not name_val:
            error = 'Title is required.'
        elif not body_val:
            error = 'Content body is required.'
        else:
            # Validate richtext content
            valid, msg = validate_richtext_links(body_val)
            if not valid:
                error = 'Validation error: ' + msg
            else:
                db = get_db()
                now = int(time.time())
                cursor = db.execute(
                    'INSERT INTO ezcontentobject (name, section_id, owner_id, published, modified, status) VALUES (?, 1, ?, ?, ?, 1)',
                    (name_val, user['id'], now, now))
                content_id = cursor.lastrowid
                db.execute(
                    'INSERT INTO ezcontentobject_attribute (contentobject_id, data_type_string, data_text) VALUES (?, ?, ?)',
                    (content_id, 'ezrichtext', body_val))
                db.execute(
                    'INSERT INTO ezcontentobject_version (contentobject_id, version, creator_id, created, status) VALUES (?, 1, ?, ?, 1)',
                    (content_id, user['id'], now))
                db.commit()
                success = 'Content published successfully.'
                return redirect('/content/view/' + str(content_id))
    
    page = LAYOUT_HEAD.format(title='Create Article')
    page += LAYOUT_HEADER_AUTHED.format(user=user['login'])
    page += """
    <div class="ez-container">
        <div class="ez-breadcrumb"><a href="/">Home</a> / <a href="/content/list">Content</a> / Create</div>
        <div class="ez-card">
            <h2>Create Content Object</h2>
            {error}{success}
            <form method="post">
                <div class="ez-form-group">
                    <label>Title</label>
                    <input type="text" name="name" value="{name_val}" required>
                </div>
                <div class="ez-form-group">
                    <label>RichText Body (DocBook XML)</label>
                    <textarea name="body" placeholder='<section xmlns="http://docbook.org/ns/docbook"><para>Your content here. Use &lt;link xlink:href="https://example.com"&gt;link text&lt;/link&gt; for links.</para></section>'>{body_val}</textarea>
                    <small style="color:#999">Supported: &lt;section&gt;, &lt;para&gt;, &lt;link xlink:href="..."&gt;</small>
                </div>
                <button class="ez-btn" type="submit">Publish</button>
                <a class="ez-btn ez-btn-secondary" href="/content/list">Cancel</a>
            </form>
        </div>
    </div>""".format(
        error='<div class="ez-alert ez-alert-danger">{}</div>'.format(error) if error else '',
        success='<div class="ez-alert ez-alert-success">{}</div>'.format(success) if success else '',
        name_val=name_val.replace('"', '&quot;'),
        body_val=body_val.replace('<', '&lt;').replace('>', '&gt;'))
    page += LAYOUT_FOOTER
    return page


@app.route('/content/edit/<int:content_id>', methods=['GET', 'POST'])
@require_editor
def content_edit(content_id):
    user = get_current_user()
    db = get_db()
    article = db.execute('SELECT * FROM ezcontentobject WHERE id = ?', (content_id,)).fetchone()
    if not article:
        return make_response('Content object not found', 404)
    
    attr = db.execute('SELECT * FROM ezcontentobject_attribute WHERE contentobject_id = ?', (content_id,)).fetchone()
    
    error = ''
    name_val = article['name']
    body_val = attr['data_text'] if attr else ''
    
    if request.method == 'POST':
        name_val = request.form.get('name', '').strip()
        body_val = request.form.get('body', '').strip()
        
        if not name_val:
            error = 'Title is required.'
        elif not body_val:
            error = 'Content body is required.'
        else:
            valid, msg = validate_richtext_links(body_val)
            if not valid:
                error = 'Validation error: ' + msg
            else:
                now = int(time.time())
                db.execute('UPDATE ezcontentobject SET name = ?, modified = ? WHERE id = ?',
                    (name_val, now, content_id))
                if attr:
                    db.execute('UPDATE ezcontentobject_attribute SET data_text = ? WHERE contentobject_id = ?',
                        (body_val, content_id))
                else:
                    db.execute('INSERT INTO ezcontentobject_attribute (contentobject_id, data_type_string, data_text) VALUES (?, ?, ?)',
                        (content_id, 'ezrichtext', body_val))
                db.commit()
                return redirect('/content/view/' + str(content_id))
    
    page = LAYOUT_HEAD.format(title='Edit: ' + name_val)
    page += LAYOUT_HEADER_AUTHED.format(user=user['login'])
    page += """
    <div class="ez-container">
        <div class="ez-breadcrumb"><a href="/">Home</a> / <a href="/content/list">Content</a> / Edit</div>
        <div class="ez-card">
            <h2>Edit Content Object #{cid}</h2>
            {error}
            <form method="post">
                <div class="ez-form-group">
                    <label>Title</label>
                    <input type="text" name="name" value="{name_val}" required>
                </div>
                <div class="ez-form-group">
                    <label>RichText Body (DocBook XML)</label>
                    <textarea name="body">{body_val}</textarea>
                </div>
                <button class="ez-btn" type="submit">Update</button>
                <a class="ez-btn ez-btn-secondary" href="/content/view/{cid}">Cancel</a>
            </form>
        </div>
    </div>""".format(
        cid=content_id,
        error='<div class="ez-alert ez-alert-danger">{}</div>'.format(error) if error else '',
        name_val=name_val.replace('"', '&quot;'),
        body_val=body_val.replace('<', '&lt;').replace('>', '&gt;'))
    page += LAYOUT_FOOTER
    return page


@app.route('/content/view/<int:content_id>')
def content_view(content_id):
    db = get_db()
    article = db.execute(
        'SELECT c.*, u.login as author FROM ezcontentobject c LEFT JOIN ezuser u ON c.owner_id = u.id WHERE c.id = ?',
        (content_id,)).fetchone()
    if not article:
        return make_response('Content object not found', 404)
    
    attr = db.execute('SELECT * FROM ezcontentobject_attribute WHERE contentobject_id = ?', (content_id,)).fetchone()
    body_html = richtext_to_html(attr['data_text']) if attr else '<p>No content.</p>'
    
    user = get_current_user()
    page = LAYOUT_HEAD.format(title=article['name'])
    if user:
        page += LAYOUT_HEADER_AUTHED.format(user=user['login'])
    else:
        page += LAYOUT_HEADER_PUBLIC
    page += """
    <div class="ez-container">
        <div class="ez-breadcrumb"><a href="/">Home</a> / <a href="/content/list">Content</a> / View</div>
        <div class="ez-card">
            <h2>{title}</h2>
            <div class="meta">Published by {author}</div>
            <hr style="margin:12px 0;border:none;border-top:1px solid #eee">
            <div class="ez-richtext-section">
                {body}
            </div>
        </div>
    </div>""".format(
        title=article['name'],
        author=article['author'] or 'System',
        body=body_html)
    page += LAYOUT_FOOTER
    return page


# ─── XSS verification endpoint (simulates another user viewing the page) ────

@app.route('/content/verify/<int:content_id>')
@require_editor
def content_verify(content_id):
    """Render the article in a headless browser to check for XSS.
    This simulates the scenario where another user views the stored content."""
    user = get_current_user()
    db = get_db()
    article = db.execute('SELECT * FROM ezcontentobject WHERE id = ?', (content_id,)).fetchone()
    if not article:
        return make_response('Content object not found', 404)
    
    attr = db.execute('SELECT * FROM ezcontentobject_attribute WHERE contentobject_id = ?', (content_id,)).fetchone()
    if not attr:
        return make_response('No content body', 404)
    
    body_html = richtext_to_html(attr['data_text'])
    
    # Build full page for headless rendering
    render_page = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>{title}</title></head>
<body><div class="content">{body}</div></body></html>""".format(
        title=article['name'], body=body_html)
    
    # Write temporary file and check with PhantomJS
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://127.0.0.1:5000/' + fn
    result_text = ''
    try:
        proc = subprocess.Popen(
            ["timeout", "5", "phantomjs", "check.js"],
            stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        of = open(fn, 'w')
        of.write(render_page)
        of.close()
        proc.stdin.write(url)
        proc.stdin.close()
        result_text = proc.stdout.readline().strip()
    except Exception as e:
        result_text = ''
    finally:
        try:
            os.unlink(fn)
        except:
            pass
    
    # Read flag from secret store
    flag_value = open('secret.txt').read().strip()
    
    if result_text == 'XSS':
        message = '<div class="ez-alert ez-alert-danger">Security Alert: XSS detected in content object #{cid}.<br>Investigation token: <strong>{flag}</strong></div>'.format(
            cid=content_id, flag=flag_value)
    elif result_text:
        message = '<div class="ez-alert ez-alert-info">Content preview rendered. Alert intercepted: "{r}"<br>Note: Only alerts with message "XSS" trigger security reporting.</div>'.format(r=result_text)
    else:
        message = '<div class="ez-alert ez-alert-success">Content preview rendered successfully. No issues detected.</div>'
    
    page = LAYOUT_HEAD.format(title='Content Preview')
    page += LAYOUT_HEADER_AUTHED.format(user=user['login'])
    page += """
    <div class="ez-container">
        <div class="ez-breadcrumb"><a href="/">Home</a> / <a href="/content/list">Content</a> / <a href="/content/view/{cid}">View</a> / Preview</div>
        <div class="ez-card">
            <h2>Content Preview: {title}</h2>
            {message}
            <hr style="margin:12px 0;border:none;border-top:1px solid #eee">
            <div class="ez-richtext-section">{body}</div>
        </div>
        <p><a class="ez-btn" href="/content/view/{cid}">Back to Article</a></p>
    </div>""".format(cid=content_id, title=article['name'], message=message, body=body_html)
    page += LAYOUT_FOOTER
    return page


@app.route('/api/v1/content/publish', methods=['POST'])
def api_publish():
    """REST API endpoint for publishing content (requires session auth)."""
    user = get_current_user()
    if not user or user['role'] not in ('editor', 'admin'):
        return make_response(json.dumps({'error': 'Authentication required. Editor role or higher needed.'}), 401)
    
    data = request.get_json(silent=True)
    if not data:
        return make_response(json.dumps({'error': 'JSON body required'}), 400)
    
    title = data.get('title', '').strip()
    body = data.get('body', '').strip()
    
    if not title or not body:
        return make_response(json.dumps({'error': 'title and body fields are required'}), 400)
    
    valid, msg = validate_richtext_links(body)
    if not valid:
        return make_response(json.dumps({'error': 'Validation failed: ' + msg}), 422)
    
    db = get_db()
    now = int(time.time())
    cursor = db.execute(
        'INSERT INTO ezcontentobject (name, section_id, owner_id, published, modified, status) VALUES (?, 1, ?, ?, ?, 1)',
        (title, user['id'], now, now))
    content_id = cursor.lastrowid
    db.execute(
        'INSERT INTO ezcontentobject_attribute (contentobject_id, data_type_string, data_text) VALUES (?, ?, ?)',
        (content_id, 'ezrichtext', body))
    db.execute(
        'INSERT INTO ezcontentobject_version (contentobject_id, version, creator_id, created, status) VALUES (?, 1, ?, ?, 1)',
        (content_id, user['id'], now))
    db.commit()
    
    return make_response(json.dumps({
        'content_id': content_id,
        'view_url': '/content/view/' + str(content_id),
        'verify_url': '/content/verify/' + str(content_id)
    }), 201)


@app.route('/ping')
def health():
    return 'OK'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
