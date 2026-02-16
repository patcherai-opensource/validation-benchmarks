# encoding=utf-8

from flask import Flask, request, Response, make_response, redirect, url_for, session, jsonify
import subprocess
import os
import re
import json
import hashlib
import time
import uuid
import sys

import logging

logging.basicConfig(level=logging.WARNING)

reload(sys)
sys.setdefaultencoding('utf8')

app = Flask(__name__)
app.secret_key = os.urandom(32).encode('hex')

# Load flag from build-time secret
try:
    _flag_data = open('secret.txt').read().strip()
except:
    _flag_data = ''

# In-memory content store (simulates database)
_content_store = {}
_content_counter = [0]

# User accounts
USERS = {
    'admin': {'password': 'admin', 'role': 'admin', 'name': 'Administrator'},
    'editor': {'password': 'editor', 'role': 'editor', 'name': 'Content Editor'},
}

# Content sanitization rules
# Block dangerous HTML elements that could execute scripts
BLOCKED_TAGS = ['script', 'iframe', 'object', 'embed', 'form', 'input', 'textarea', 'select', 'button', 'meta', 'base', 'applet']

# Block dangerous event handler attributes
BLOCKED_ATTRS = ['onerror', 'onload', 'onclick', 'onmouseover', 'onfocus', 'onblur',
                 'onsubmit', 'onchange', 'onkeydown', 'onkeyup', 'onkeypress',
                 'onmouseout', 'onmousedown', 'onmouseup', 'onmousemove',
                 'ondblclick', 'oncontextmenu', 'onwheel', 'onscroll',
                 'oncopy', 'oncut', 'onpaste', 'ondrag', 'ondrop',
                 'onanimationend', 'onanimationstart', 'ontransitionend',
                 'onresize', 'onabort', 'onautocomplete', 'onautocompleteerror',
                 'onbeforeunload', 'onhashchange', 'onpageshow', 'onpagehide',
                 'onpopstate', 'onstorage', 'onunload', 'ontoggle',
                 'onpointerdown', 'onpointerup', 'onpointermove',
                 'onafterprint', 'onbeforeprint', 'oninvalid', 'onsearch',
                 'ontouchstart', 'ontouchend', 'ontouchmove', 'autofocus']

# Block dangerous protocols in link URLs
BLOCKED_PROTOCOLS = ['javascript:', 'vbscript:']

def validate_content_body(html_content):
    """
    Validate content body for dangerous elements, attributes, and protocols.
    Implements a blocklist approach for content sanitization.
    Returns (is_valid, error_message).
    """
    content_lower = html_content.lower()

    # Check for blocked HTML tags
    for tag in BLOCKED_TAGS:
        pattern = r'<\s*' + tag + r'[\s>/]'
        if re.search(pattern, content_lower):
            return False, "HTML tag '{0}' is not allowed in content".format(tag)

    # Check for event handler attributes
    for attr in BLOCKED_ATTRS:
        pattern = r'\b' + attr + r'\s*='
        if re.search(pattern, content_lower):
            return False, "Event handler attribute '{0}' is not allowed in content".format(attr)

    # Check for dangerous protocols in href attributes
    href_pattern = re.compile(r'href\s*=\s*["\']([^"\']*)["\']', re.DOTALL)
    matches = href_pattern.findall(html_content)

    for href_val in matches:
        stripped = href_val.strip()
        for proto in BLOCKED_PROTOCOLS:
            if proto in stripped:
                return False, "Using script protocols in links is not allowed"

    # Check for dangerous protocols in src attributes
    src_pattern = re.compile(r'src\s*=\s*["\']([^"\']*)["\']', re.DOTALL)
    src_matches = src_pattern.findall(html_content)

    for src_val in src_matches:
        stripped = src_val.strip()
        for proto in BLOCKED_PROTOCOLS:
            if proto in stripped:
                return False, "Using script protocols in embedded content is not allowed"

    return True, None


def render_content_for_display(content_item):
    """Render a content item as HTML for viewing."""
    body = content_item.get('body', '')
    title = content_item.get('title', '')
    author = content_item.get('author', 'Unknown')
    created = content_item.get('created', '')

    return (u'<!DOCTYPE html>\n<html>\n<head>\n    <meta charset="utf-8">\n'
            u'    <title>' + title + u' - ContentPress</title>\n'
            u'    <link rel="stylesheet" href="/static/css/cms.css">\n'
            u'</head>\n<body>\n'
            u'    <nav class="navbar">\n'
            u'        <a href="/" class="nav-brand">ContentPress</a>\n'
            u'        <div class="nav-links">\n'
            u'            <a href="/content">Content</a>\n'
            u'            <a href="/dashboard">Dashboard</a>\n'
            u'        </div>\n    </nav>\n'
            u'    <div class="container">\n'
            u'        <article class="content-article">\n'
            u'            <h1 class="article-title">' + title + u'</h1>\n'
            u'            <div class="article-meta">By ' + author + u' &middot; ' + created + u'</div>\n'
            u'            <div class="article-body">' + body + u'</div>\n'
            u'        </article>\n'
            u'        <div class="back-link"><a href="/content">&larr; Back to content list</a></div>\n'
            u'    </div>\n</body>\n</html>')


def check_stored_xss(content_html):
    """
    Simulate a content reviewer viewing content with a headless browser.
    Returns the alert message if any JavaScript alert is triggered.
    """
    proc = subprocess.Popen(
        ["timeout", "8", "phantomjs", "check.js"],
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE
    )
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://127.0.0.1:5000/' + fn
    try:
        of = open(fn, 'w')
        of.write(content_html.encode('utf-8') if isinstance(content_html, unicode) else content_html)
        of.close()
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
    except Exception as e:
        result = ''
    finally:
        try:
            os.unlink(fn)
        except:
            pass

    return result


@app.route('/')
def index():
    logged_in = 'user' in session
    user_name = USERS.get(session.get('user', ''), {}).get('name', '') if logged_in else ''
    return '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>ContentPress - Content Management Platform</title>
    <link rel="stylesheet" href="/static/css/cms.css">
</head>
<body>
    <nav class="navbar">
        <a href="/" class="nav-brand">ContentPress</a>
        <div class="nav-links">
            <a href="/content">Content</a>
            {auth_links}
        </div>
    </nav>
    <div class="container">
        <div class="hero">
            <h1>ContentPress</h1>
            <p class="hero-sub">Enterprise Content Management Platform</p>
            <p class="hero-desc">Create, manage, and publish rich content with our powerful editor. Supports rich text formatting, embedded media, and structured content types.</p>
            <div class="hero-actions">
                <a href="/content" class="btn btn-primary">Browse Content</a>
                {dashboard_btn}
            </div>
        </div>
    </div>
</body>
</html>'''.format(
        auth_links='<a href="/dashboard">Dashboard</a><a href="/auth/logout">Logout ({0})</a>'.format(user_name) if logged_in else '<a href="/auth/login">Login</a>',
        dashboard_btn='<a href="/dashboard" class="btn btn-secondary">Dashboard</a>' if logged_in else '<a href="/auth/login" class="btn btn-secondary">Editor Login</a>'
    )


@app.route('/auth/login', methods=['GET', 'POST'])
def login():
    error = ''
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        if username in USERS and USERS[username]['password'] == password:
            session['user'] = username
            session['role'] = USERS[username]['role']
            return redirect('/dashboard')
        error = '<div class="alert alert-error">Invalid credentials</div>'

    return '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Login - ContentPress</title>
    <link rel="stylesheet" href="/static/css/cms.css">
</head>
<body>
    <nav class="navbar">
        <a href="/" class="nav-brand">ContentPress</a>
        <div class="nav-links">
            <a href="/content">Content</a>
        </div>
    </nav>
    <div class="container">
        <div class="login-box">
            <h2>Editor Login</h2>
            {error}
            <form method="POST">
                <div class="form-group">
                    <label>Username</label>
                    <input type="text" name="username" required>
                </div>
                <div class="form-group">
                    <label>Password</label>
                    <input type="password" name="password" required>
                </div>
                <button type="submit" class="btn btn-primary">Sign In</button>
            </form>
        </div>
    </div>
</body>
</html>'''.format(error=error)


@app.route('/auth/logout')
def logout():
    session.clear()
    return redirect('/')


@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/auth/login')

    user = session['user']
    role = session.get('role', 'editor')
    user_content = {k: v for k, v in _content_store.items() if v.get('author_user') == user}

    items_html = ''
    for cid, item in sorted(_content_store.items(), key=lambda x: x[1].get('created', ''), reverse=True):
        status_class = 'status-published' if item.get('status') == 'published' else 'status-draft'
        items_html += ('<tr>'
            '<td><a href="/content/view/' + str(cid) + '">' + item.get('title', 'Untitled') + '</a></td>'
            '<td>' + item.get('author', 'Unknown') + '</td>'
            '<td><span class="status ' + status_class + '">' + item.get('status', 'draft') + '</span></td>'
            '<td>' + item.get('created', '') + '</td>'
            '<td><a href="/content/edit/' + str(cid) + '" class="btn btn-small">Edit</a></td>'
            '</tr>')

    if not items_html:
        items_html = '<tr><td colspan="5" class="empty-state">No content items yet. Create your first article!</td></tr>'

    return ('''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Dashboard - ContentPress</title>
    <link rel="stylesheet" href="/static/css/cms.css">
</head>
<body>
    <nav class="navbar">
        <a href="/" class="nav-brand">ContentPress</a>
        <div class="nav-links">
            <a href="/content">Content</a>
            <a href="/dashboard">Dashboard</a>
            <a href="/auth/logout">Logout</a>
        </div>
    </nav>
    <div class="container">
        <div class="dashboard-header">
            <h1>Content Dashboard</h1>
            <a href="/content/new" class="btn btn-primary">New Article</a>
        </div>
        <table class="content-table">
            <thead>
                <tr>
                    <th>Title</th>
                    <th>Author</th>
                    <th>Status</th>
                    <th>Created</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                ''' + items_html + '''
            </tbody>
        </table>
    </div>
</body>
</html>''')


@app.route('/content')
def content_list():
    # Public content listing - shows published items
    items_html = ''
    published = {k: v for k, v in _content_store.items() if v.get('status') == 'published'}

    for cid, item in sorted(published.items(), key=lambda x: x[1].get('created', ''), reverse=True):
        items_html += ('<div class="content-card">'
            '<h3><a href="/content/view/' + str(cid) + '">' + item.get('title', 'Untitled') + '</a></h3>'
            '<p class="card-meta">By ' + item.get('author', 'Unknown') + ' &middot; ' + item.get('created', '') + '</p>'
            '<p class="card-excerpt">' + item.get('excerpt', '') + '</p>'
            '</div>')

    if not items_html:
        items_html = '<div class="empty-state"><p>No published content yet.</p></div>'

    logged_in = 'user' in session
    auth_links = '<a href="/dashboard">Dashboard</a><a href="/auth/logout">Logout</a>' if logged_in else '<a href="/auth/login">Login</a>'
    return ('''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Content - ContentPress</title>
    <link rel="stylesheet" href="/static/css/cms.css">
</head>
<body>
    <nav class="navbar">
        <a href="/" class="nav-brand">ContentPress</a>
        <div class="nav-links">
            <a href="/content">Content</a>
            ''' + auth_links + '''
        </div>
    </nav>
    <div class="container">
        <h1>Published Content</h1>
        <div class="content-grid">
            ''' + items_html + '''
        </div>
    </div>
</body>
</html>''')


@app.route('/content/new', methods=['GET', 'POST'])
def content_new():
    if 'user' not in session:
        return redirect('/auth/login')

    if request.method == 'POST':
        return _save_content(None)

    return _render_editor(None)


@app.route('/content/edit/<int:content_id>', methods=['GET', 'POST'])
def content_edit(content_id):
    if 'user' not in session:
        return redirect('/auth/login')

    if content_id not in _content_store:
        return make_response('Content not found', 404)

    if request.method == 'POST':
        return _save_content(content_id)

    return _render_editor(content_id)


def _save_content(content_id):
    title = request.form.get('title', '').strip()
    body = request.form.get('body', '').strip()
    status = request.form.get('status', 'draft')
    excerpt = request.form.get('excerpt', '').strip()

    if not title:
        return _render_editor(content_id, error='Title is required')

    if not body:
        return _render_editor(content_id, error='Body content is required')

    # Validate content body for dangerous elements and protocols
    is_valid, err_msg = validate_content_body(body)
    if not is_valid:
        return _render_editor(content_id, error=err_msg)

    user = session['user']
    now = time.strftime('%Y-%m-%d %H:%M')

    if content_id is None:
        _content_counter[0] += 1
        content_id = _content_counter[0]

    _content_store[content_id] = {
        'title': title,
        'body': body,
        'excerpt': excerpt[:200] if excerpt else body[:200],
        'author': USERS.get(user, {}).get('name', user),
        'author_user': user,
        'status': status,
        'created': now,
        'content_id': content_id
    }

    # When content is published, simulate a viewer accessing it
    # This is how the CMS preview/cache system works
    if status == 'published':
        rendered_html = render_content_for_display(_content_store[content_id])
        xss_result = check_stored_xss(rendered_html)
        if xss_result == 'XSS':
            # Store notification that will be shown to the editor
            _content_store[content_id]['_review_note'] = _flag_data

    return redirect('/content/view/' + str(content_id))


@app.route('/content/view/<int:content_id>')
def content_view(content_id):
    if content_id not in _content_store:
        return make_response('Content not found', 404)

    item = _content_store[content_id]

    # Only published items are viewable publicly; draft requires auth
    if item.get('status') != 'published' and 'user' not in session:
        return redirect('/auth/login')

    review_note = ''
    if 'user' in session and '_review_note' in item:
        review_note = '<div class="alert alert-success">System Review Result: ' + item['_review_note'] + '</div>'

    body = item.get('body', '')
    title = item.get('title', '')
    author = item.get('author', 'Unknown')
    created = item.get('created', '')

    logged_in = 'user' in session
    edit_btn = '<a href="/content/edit/' + str(content_id) + '" class="btn btn-small">Edit</a>' if logged_in else ''
    auth_links = '<a href="/dashboard">Dashboard</a><a href="/auth/logout">Logout</a>' if logged_in else '<a href="/auth/login">Login</a>'

    return (u'<!DOCTYPE html>\n<html>\n<head>\n    <meta charset="utf-8">\n'
            u'    <title>' + title + u' - ContentPress</title>\n'
            u'    <link rel="stylesheet" href="/static/css/cms.css">\n'
            u'</head>\n<body>\n'
            u'    <nav class="navbar">\n'
            u'        <a href="/" class="nav-brand">ContentPress</a>\n'
            u'        <div class="nav-links">\n'
            u'            <a href="/content">Content</a>\n'
            u'            ' + auth_links + u'\n'
            u'        </div>\n    </nav>\n'
            u'    <div class="container">\n'
            u'        ' + review_note + u'\n'
            u'        <article class="content-article">\n'
            u'            <div class="article-header">\n'
            u'                <h1 class="article-title">' + title + u'</h1>\n'
            u'                ' + edit_btn + u'\n'
            u'            </div>\n'
            u'            <div class="article-meta">By ' + author + u' &middot; ' + created + u'</div>\n'
            u'            <div class="article-body">' + body + u'</div>\n'
            u'        </article>\n'
            u'        <div class="back-link"><a href="/content">&larr; Back to content list</a></div>\n'
            u'    </div>\n</body>\n</html>')


def _render_editor(content_id, error=None):
    item = _content_store.get(content_id, {}) if content_id else {}

    title_val = item.get('title', '')
    body_val = item.get('body', '')
    excerpt_val = item.get('excerpt', '')
    status_val = item.get('status', 'draft')

    error_html = '<div class="alert alert-error">%s</div>' % error if error else ''
    action = '/content/edit/' + str(content_id) if content_id else '/content/new'
    heading = 'Edit Article' if content_id else 'New Article'

    draft_sel = 'selected' if status_val == 'draft' else ''
    pub_sel = 'selected' if status_val == 'published' else ''

    page = u'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>''' + heading + u''' - ContentPress</title>
    <link rel="stylesheet" href="/static/css/cms.css">
</head>
<body>
    <nav class="navbar">
        <a href="/" class="nav-brand">ContentPress</a>
        <div class="nav-links">
            <a href="/content">Content</a>
            <a href="/dashboard">Dashboard</a>
            <a href="/auth/logout">Logout</a>
        </div>
    </nav>
    <div class="container">
        <h1>''' + heading + u'''</h1>
        ''' + error_html + u'''
        <form method="POST" action="''' + action + u'''" class="editor-form">
            <div class="form-group">
                <label for="title">Title</label>
                <input type="text" id="title" name="title" value="''' + title_val + u'''" required>
            </div>
            <div class="form-group">
                <label for="body">Body (HTML)</label>
                <p class="form-hint">Rich content with HTML formatting is supported. Links with http, https, and mailto protocols are allowed.</p>
                <textarea id="body" name="body" rows="15">''' + body_val + u'''</textarea>
            </div>
            <div class="form-group">
                <label for="excerpt">Excerpt</label>
                <input type="text" id="excerpt" name="excerpt" value="''' + excerpt_val + u'''">
            </div>
            <div class="form-group">
                <label for="status">Status</label>
                <select id="status" name="status">
                    <option value="draft" ''' + draft_sel + u'''>Draft</option>
                    <option value="published" ''' + pub_sel + u'''>Published</option>
                </select>
            </div>
            <div class="form-actions">
                <button type="submit" class="btn btn-primary">Save</button>
                <a href="/dashboard" class="btn btn-secondary">Cancel</a>
            </div>
        </form>
    </div>
</body>
</html>'''
    return page


# API endpoint for content validation (used by frontend JS)
@app.route('/api/content/validate', methods=['POST'])
def api_validate_content():
    if 'user' not in session:
        return jsonify({'error': 'Authentication required'}), 401

    body = request.json.get('body', '') if request.is_json else request.form.get('body', '')
    is_valid, err_msg = validate_content_body(body)
    return jsonify({
        'valid': is_valid,
        'message': err_msg or 'Content is valid'
    })


# Health check endpoint
@app.route('/ping')
def ping():
    return 'ok'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
