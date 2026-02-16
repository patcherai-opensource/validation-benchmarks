import os
import re
import hashlib
import secrets
from functools import wraps
from datetime import datetime

from flask import (
    Flask, request, redirect, url_for, session,
    render_template_string, abort
)
from jinja2 import BaseLoader, TemplateSyntaxError, UndefinedError
from jinja2.sandbox import SandboxedEnvironment
import markdown


app = Flask(__name__)
app.secret_key = os.environ.get('SESSION_KEY', secrets.token_hex(32))


# ---------------------------------------------------------------------------
# Site configuration
# ---------------------------------------------------------------------------

class SiteConfig:
    """Runtime configuration store for the CMS engine.

    Provides hierarchical key access using dot-notation
    (e.g. 'engine.renderer.allowed_helpers').
    """

    def __init__(self):
        self._data = {
            'site': {
                'title': 'Flavor CMS',
                'author': {'name': 'Admin', 'email': 'admin@flavorcms.local'},
                'metadata': {
                    'description': 'A lightweight flat-file content management system',
                },
            },
            'engine': {
                'renderer': {
                    'cache': False,
                    'auto_reload': True,
                    'autoescape': True,
                    'allowed_helpers': [],
                    'allowed_transforms': [],
                    'permit_unknown_helpers': False,
                    'permit_unknown_transforms': False,
                },
                'content': {
                    'process_markdown': True,
                    'process_templates': True,
                },
                'pages': {
                    'default_layout': 'standard',
                    'date_format': '%B %d, %Y',
                },
            },
            'system': {
                'debug': False,
                'timezone': 'UTC',
                'cache_driver': 'filesystem',
            },
        }

    # Dot-notation access --------------------------------------------------

    def get(self, key, default=None):
        parts = key.split('.')
        node = self._data
        for p in parts:
            if isinstance(node, dict) and p in node:
                node = node[p]
            else:
                return default
        return node

    def set(self, key, value):
        parts = key.split('.')
        node = self._data
        for p in parts[:-1]:
            if p not in node or not isinstance(node[p], dict):
                node[p] = {}
            node = node[p]
        node[parts[-1]] = value
        return ''

    def as_dict(self):
        return self._data


site_config = SiteConfig()


# ---------------------------------------------------------------------------
# User store (flat-file accounts)
# ---------------------------------------------------------------------------

USERS = {
    'admin': {
        'password_hash': hashlib.sha256(b'Fl@vorAdm!n2024').hexdigest(),
        'role': 'admin',
        'full_name': 'Site Administrator',
    },
    'editor': {
        'password_hash': hashlib.sha256(b'editor').hexdigest(),
        'role': 'editor',
        'full_name': 'Content Editor',
    },
}


def check_auth():
    return session.get('user') is not None


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not check_auth():
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated


def require_role(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not check_auth():
                return redirect(url_for('admin_login'))
            if session.get('role') not in roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated
    return decorator


# ---------------------------------------------------------------------------
# Page store (flat-file pages)
# ---------------------------------------------------------------------------

PAGES = {}


def init_default_pages():
    PAGES['home'] = {
        'title': 'Welcome to Flavor CMS',
        'slug': 'home',
        'body': (
            '# Welcome to Flavor CMS\n\n'
            'A lightweight flat-file content management system '
            'built for speed and simplicity.\n\n'
            '## Features\n\n'
            '- Markdown content processing\n'
            '- Template engine with sandboxed rendering\n'
            '- Flat-file page management\n'
            '- Role-based access control\n\n'
            'Navigate to the [admin panel](/panel) to manage your site content.'
        ),
        'layout': 'standard',
        'process_templates': False,
        'published': True,
        'created': datetime(2024, 1, 15),
        'modified': datetime(2024, 1, 15),
        'author': 'admin',
    }
    PAGES['about'] = {
        'title': 'About',
        'slug': 'about',
        'body': (
            '# About Flavor CMS\n\n'
            'Flavor CMS is a modern flat-file content management system.\n\n'
            '**Version:** 1.4.2\n\n'
            '**License:** MIT\n\n'
            '## Roles\n\n'
            'Flavor CMS supports multiple user roles:\n\n'
            '- **Admin** — full system access including configuration management\n'
            '- **Editor** — content creation and page management\n\n'
            'For documentation, visit our knowledge base.'
        ),
        'layout': 'standard',
        'process_templates': False,
        'published': True,
        'created': datetime(2024, 1, 15),
        'modified': datetime(2024, 1, 15),
        'author': 'admin',
    }
    PAGES['typography'] = {
        'title': 'Typography Guide',
        'slug': 'typography',
        'body': (
            '# Typography Guide\n\n'
            '## Headings\n\n'
            'Content supports full Markdown rendering with '
            'headings, lists, links, and more.\n\n'
            '### Subheading Example\n\n'
            '- Item one\n- Item two\n- Item three\n\n'
            '> Blockquote example text here.\n\n'
            '`inline code` and code blocks are supported.'
        ),
        'layout': 'standard',
        'process_templates': False,
        'published': True,
        'created': datetime(2024, 2, 1),
        'modified': datetime(2024, 2, 1),
        'author': 'admin',
    }


init_default_pages()


# ---------------------------------------------------------------------------
# Dangerous function check
# ---------------------------------------------------------------------------

DANGEROUS_BUILTINS = {
    'eval', 'exec', 'compile', '__import__', 'open',
    'getattr', 'setattr', 'delattr', 'globals', 'locals',
    'vars', 'dir', 'type', 'breakpoint', 'exit', 'quit',
    'input', 'help', 'memoryview', 'staticmethod', 'classmethod',
    'super', 'property',
}


def is_restricted_callable(name):
    return name.lower() in DANGEROUS_BUILTINS


# ---------------------------------------------------------------------------
# Template rendering engine
# ---------------------------------------------------------------------------

class HelperRegistry:
    """Proxy object that resolves callable helpers at access time.

    Checks the engine.renderer.allowed_helpers configuration list
    on every attribute access. If a requested name is present in the
    allowed list, the corresponding Python callable is returned.
    Otherwise, access is denied.
    """

    def __init__(self, config):
        self._config = config

    def __getattr__(self, name):
        if name.startswith('_'):
            raise AttributeError(name)

        allowed = self._config.get('engine.renderer.allowed_helpers')
        if isinstance(allowed, list) and name in allowed:
            # Resolve from builtins
            import builtins
            fn = getattr(builtins, name, None)
            if fn and callable(fn):
                return fn
            # Resolve from common modules
            import importlib
            for mod_name in ['os', 'subprocess', 'shutil', 'io']:
                try:
                    mod = importlib.import_module(mod_name)
                    fn = getattr(mod, name, None)
                    if fn and callable(fn):
                        return fn
                except ImportError:
                    continue
            return None

        # If permit_unknown_helpers is enabled, allow safe builtins
        if self._config.get('engine.renderer.permit_unknown_helpers', False):
            import builtins
            fn = getattr(builtins, name, None)
            if fn and callable(fn) and not is_restricted_callable(name):
                return fn

        raise AttributeError(f"Helper '{name}' is not available")


class ContentRenderer:
    """
    Renders page content through the template engine.

    When template processing is enabled for a page, the content body is
    parsed through Jinja2 with the site configuration object available
    in the template namespace. A helper registry resolves callable
    functions based on the engine.renderer.allowed_helpers config list.
    """

    def __init__(self, config):
        self.config = config
        self.helpers = HelperRegistry(config)

    def _build_env(self):
        env = SandboxedEnvironment(
            loader=BaseLoader(),
            autoescape=self.config.get('engine.renderer.autoescape', True),
        )
        return env

    def render_content(self, raw_body, page_meta=None):
        env = self._build_env()

        tpl_vars = {
            'config': self.config,
            'site': self.config.get('site'),
            'engine': self.config.get('engine'),
            'helpers': self.helpers,
            'page': page_meta or {},
            'now': datetime.utcnow(),
        }

        cleaned = self._clean_dangerous_patterns(raw_body)

        try:
            tpl = env.from_string(cleaned)
            rendered = tpl.render(**tpl_vars)
        except (TemplateSyntaxError, UndefinedError):
            rendered = raw_body
        except Exception:
            rendered = raw_body

        if self.config.get('engine.content.process_markdown', True):
            rendered = markdown.markdown(
                rendered,
                extensions=['extra', 'codehilite', 'toc']
            )

        return rendered

    def _clean_dangerous_patterns(self, content):
        """Sanitize known exploit patterns from template content."""
        blocked = [
            'array_map',
            'call_user_func',
            'register_callback',
            '__subclasses__',
        ]
        for term in blocked:
            pattern = re.compile(
                r'(\{\{.*?' + re.escape(term) + r'.*?\}\}|'
                r'\{%.*?' + re.escape(term) + r'.*?%\})',
                re.IGNORECASE | re.DOTALL
            )
            content = pattern.sub('{# blocked #}', content)
        return content


renderer = ContentRenderer(site_config)


# ---------------------------------------------------------------------------
# Helper: build full page HTML
# ---------------------------------------------------------------------------

SITE_LAYOUT = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} | Flavor CMS</title>
    <style>
        :root { --primary: #0d6efd; --dark: #212529; --light: #f8f9fa; --border: #dee2e6; }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
               line-height: 1.6; color: var(--dark); background: var(--light); }
        .navbar { background: var(--dark); padding: 1rem 2rem; display: flex;
                  justify-content: space-between; align-items: center; }
        .navbar a { color: #fff; text-decoration: none; margin-right: 1.5rem; font-size: 0.95rem; }
        .navbar a:hover { color: var(--primary); }
        .navbar .brand { font-weight: 700; font-size: 1.2rem; }
        .container { max-width: 960px; margin: 2rem auto; padding: 0 1rem; }
        .content { background: #fff; padding: 2rem; border-radius: 8px;
                   border: 1px solid var(--border); }
        .content h1 { margin-bottom: 1rem; }
        .content h2 { margin: 1.5rem 0 0.75rem; }
        .content p { margin-bottom: 1rem; }
        .content ul, .content ol { margin: 0.5rem 0 1rem 1.5rem; }
        .content a { color: var(--primary); }
        .content code { background: #e9ecef; padding: 0.15rem 0.4rem; border-radius: 3px; font-size: 0.9em; }
        .content blockquote { border-left: 4px solid var(--primary); padding: 0.5rem 1rem;
                              margin: 1rem 0; background: #f1f3f5; }
        .footer { text-align: center; padding: 2rem; color: #6c757d; font-size: 0.85rem; }
        pre { background: #e9ecef; padding: 1rem; border-radius: 4px; overflow-x: auto; }
    </style>
</head>
<body>
    <nav class="navbar">
        <div>
            <a href="/" class="brand">Flavor CMS</a>
            <a href="/page/home">Home</a>
            <a href="/page/about">About</a>
            <a href="/page/typography">Typography</a>
        </div>
        <div>
            {% if session_user %}
                <a href="/panel">Panel</a>
                <a href="/panel/signout">Sign out</a>
            {% else %}
                <a href="/panel">Sign in</a>
            {% endif %}
        </div>
    </nav>
    <div class="container">
        <div class="content">
            {{ body|safe }}
        </div>
    </div>
    <div class="footer">
        Powered by Flavor CMS v1.4.2
    </div>
</body>
</html>'''

ADMIN_LAYOUT = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} | Flavor CMS Panel</title>
    <style>
        :root { --primary: #0d6efd; --dark: #212529; --light: #f8f9fa; --border: #dee2e6; --danger: #dc3545; }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
               line-height: 1.6; color: var(--dark); background: #e9ecef; }
        .topbar { background: var(--dark); padding: 0.75rem 2rem; display: flex;
                  justify-content: space-between; align-items: center; }
        .topbar a { color: #fff; text-decoration: none; margin-right: 1.5rem; font-size: 0.9rem; }
        .topbar .brand { font-weight: 700; font-size: 1.1rem; color: var(--primary); }
        .wrap { max-width: 1100px; margin: 2rem auto; padding: 0 1rem; }
        .card { background: #fff; padding: 2rem; border-radius: 8px; border: 1px solid var(--border);
                margin-bottom: 1.5rem; }
        h1 { margin-bottom: 1.5rem; }
        h2 { margin-bottom: 1rem; }
        table { width: 100%; border-collapse: collapse; }
        th, td { text-align: left; padding: 0.6rem 1rem; border-bottom: 1px solid var(--border); }
        th { background: var(--light); font-weight: 600; }
        .btn { display: inline-block; padding: 0.4rem 1rem; border-radius: 4px;
               text-decoration: none; font-size: 0.9rem; cursor: pointer; border: none; }
        .btn-primary { background: var(--primary); color: #fff; }
        .btn-danger { background: var(--danger); color: #fff; }
        .btn-sm { padding: 0.25rem 0.6rem; font-size: 0.8rem; }
        .form-group { margin-bottom: 1rem; }
        .form-group label { display: block; margin-bottom: 0.3rem; font-weight: 500; }
        .form-group input, .form-group textarea, .form-group select {
            width: 100%; padding: 0.5rem; border: 1px solid var(--border); border-radius: 4px;
            font-family: inherit; font-size: 0.95rem; }
        .form-group textarea { min-height: 300px; font-family: "SFMono-Regular", Consolas, monospace; font-size: 0.88rem; }
        .form-check { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem; }
        .form-check input[type=checkbox] { width: auto; }
        .alert { padding: 0.75rem 1rem; border-radius: 4px; margin-bottom: 1rem; }
        .alert-success { background: #d1e7dd; color: #0f5132; }
        .alert-error { background: #f8d7da; color: #842029; }
        .meta { color: #6c757d; font-size: 0.85rem; }
    </style>
</head>
<body>
    <div class="topbar">
        <div>
            <a href="/" class="brand">Flavor CMS</a>
            <a href="/panel">Dashboard</a>
            <a href="/panel/pages">Pages</a>
        </div>
        <div>
            <a href="/">View Site</a>
            <a href="/panel/signout">Sign out ({{ session_user }})</a>
        </div>
    </div>
    <div class="wrap">
        {{ body|safe }}
    </div>
</body>
</html>'''


def render_site_page(title, body, session_user=None):
    return render_template_string(
        SITE_LAYOUT,
        title=title,
        body=body,
        session_user=session_user,
    )


def render_admin_page(title, body):
    return render_template_string(
        ADMIN_LAYOUT,
        title=title,
        body=body,
        session_user=session.get('user'),
    )


# ---------------------------------------------------------------------------
# Public routes
# ---------------------------------------------------------------------------

@app.route('/')
def index():
    page = PAGES.get('home')
    if not page:
        abort(404)
    if page.get('process_templates', False):
        body = renderer.render_content(page['body'], page)
    else:
        body = markdown.markdown(page['body'], extensions=['extra', 'codehilite', 'toc'])
    return render_site_page(page['title'], body, session.get('user'))


@app.route('/page/<slug>')
def view_page(slug):
    page = PAGES.get(slug)
    if not page or not page.get('published', True):
        abort(404)

    if page.get('process_templates', False):
        body = renderer.render_content(page['body'], page)
    else:
        body = markdown.markdown(page['body'], extensions=['extra', 'codehilite', 'toc'])

    return render_site_page(page['title'], body, session.get('user'))


# ---------------------------------------------------------------------------
# Admin panel routes
# ---------------------------------------------------------------------------

@app.route('/panel')
def admin_dashboard():
    if not check_auth():
        return redirect(url_for('admin_login'))

    page_count = len(PAGES)
    cards = f'''
    <h1>Dashboard</h1>
    <div class="card">
        <h2>Site Overview</h2>
        <p><strong>Pages:</strong> {page_count}</p>
        <p><strong>Signed in as:</strong> {session.get("full_name", "")} ({session.get("role", "")})</p>
    </div>
    <div class="card">
        <h2>Quick Actions</h2>
        <a href="/panel/pages" class="btn btn-primary">Manage Pages</a>
    </div>
    '''
    return render_admin_page('Dashboard', cards)


@app.route('/panel/signin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'GET':
        login_form = '''
        <div class="card" style="max-width:420px;margin:3rem auto;">
            <h2>Sign In</h2>
            <form method="POST">
                <div class="form-group">
                    <label>Username</label>
                    <input type="text" name="username" required autocomplete="username">
                </div>
                <div class="form-group">
                    <label>Password</label>
                    <input type="password" name="password" required autocomplete="current-password">
                </div>
                <button type="submit" class="btn btn-primary">Sign In</button>
            </form>
        </div>
        '''
        return render_admin_page('Sign In', login_form)

    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    user = USERS.get(username)

    if user and user['password_hash'] == hashlib.sha256(password.encode()).hexdigest():
        session['user'] = username
        session['role'] = user['role']
        session['full_name'] = user['full_name']
        return redirect(url_for('admin_dashboard'))

    error_form = '''
    <div class="card" style="max-width:420px;margin:3rem auto;">
        <div class="alert alert-error">Invalid credentials.</div>
        <h2>Sign In</h2>
        <form method="POST">
            <div class="form-group">
                <label>Username</label>
                <input type="text" name="username" required autocomplete="username">
            </div>
            <div class="form-group">
                <label>Password</label>
                <input type="password" name="password" required autocomplete="current-password">
            </div>
            <button type="submit" class="btn btn-primary">Sign In</button>
        </form>
    </div>
    '''
    return render_admin_page('Sign In', error_form), 401


@app.route('/panel/signout')
def admin_logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/panel/pages')
@require_auth
def admin_pages():
    rows = ''
    for slug, page in sorted(PAGES.items()):
        status = 'Published' if page.get('published') else 'Draft'
        tpl = 'Yes' if page.get('process_templates') else 'No'
        rows += f'''
        <tr>
            <td><a href="/panel/pages/edit/{slug}">{page["title"]}</a></td>
            <td><code>{slug}</code></td>
            <td>{status}</td>
            <td>{tpl}</td>
            <td>{page.get("layout", "standard")}</td>
            <td>
                <a href="/page/{slug}" class="btn btn-sm btn-primary">View</a>
                <a href="/panel/pages/edit/{slug}" class="btn btn-sm btn-primary">Edit</a>
            </td>
        </tr>
        '''
    body = f'''
    <h1>Pages</h1>
    <div class="card">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem;">
            <h2>All Pages</h2>
            <a href="/panel/pages/compose" class="btn btn-primary">New Page</a>
        </div>
        <table>
            <thead>
                <tr><th>Title</th><th>Slug</th><th>Status</th><th>Templates</th><th>Layout</th><th>Actions</th></tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
    </div>
    '''
    return render_admin_page('Pages', body)


@app.route('/panel/pages/compose', methods=['GET', 'POST'])
@require_role('admin', 'editor')
def admin_page_create():
    if request.method == 'GET':
        form = '''
        <h1>New Page</h1>
        <div class="card">
            <form method="POST">
                <div class="form-group">
                    <label>Title</label>
                    <input type="text" name="title" required>
                </div>
                <div class="form-group">
                    <label>Slug</label>
                    <input type="text" name="slug" required pattern="[a-z0-9-]+">
                </div>
                <div class="form-group">
                    <label>Layout</label>
                    <select name="layout">
                        <option value="standard">Standard</option>
                        <option value="wide">Wide</option>
                        <option value="minimal">Minimal</option>
                    </select>
                </div>
                <div class="form-check">
                    <input type="checkbox" name="process_templates" id="pt" value="1">
                    <label for="pt">Enable template processing</label>
                </div>
                <div class="form-check">
                    <input type="checkbox" name="published" id="pub" value="1" checked>
                    <label for="pub">Published</label>
                </div>
                <div class="form-group">
                    <label>Content (Markdown)</label>
                    <textarea name="body" placeholder="Write your content here..."></textarea>
                </div>
                <button type="submit" class="btn btn-primary">Create Page</button>
            </form>
        </div>
        '''
        return render_admin_page('New Page', form)

    slug = request.form.get('slug', '').strip().lower()
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    if not slug:
        abort(400)

    PAGES[slug] = {
        'title': request.form.get('title', 'Untitled'),
        'slug': slug,
        'body': request.form.get('body', ''),
        'layout': request.form.get('layout', 'standard'),
        'process_templates': request.form.get('process_templates') == '1',
        'published': request.form.get('published') == '1',
        'created': datetime.utcnow(),
        'modified': datetime.utcnow(),
        'author': session.get('user', 'unknown'),
    }
    return redirect(url_for('admin_pages'))


@app.route('/panel/pages/edit/<slug>', methods=['GET', 'POST'])
@require_role('admin', 'editor')
def admin_page_edit(slug):
    page = PAGES.get(slug)
    if not page:
        abort(404)

    if request.method == 'GET':
        checked_tpl = 'checked' if page.get('process_templates') else ''
        checked_pub = 'checked' if page.get('published', True) else ''
        sel_standard = 'selected' if page.get('layout') == 'standard' else ''
        sel_wide = 'selected' if page.get('layout') == 'wide' else ''
        sel_minimal = 'selected' if page.get('layout') == 'minimal' else ''

        form = f'''
        <h1>Edit Page: {page["title"]}</h1>
        <div class="card">
            <form method="POST">
                <div class="form-group">
                    <label>Title</label>
                    <input type="text" name="title" value="{page["title"]}" required>
                </div>
                <div class="form-group">
                    <label>Slug</label>
                    <input type="text" value="{slug}" disabled>
                    <span class="meta">Slug cannot be changed after creation.</span>
                </div>
                <div class="form-group">
                    <label>Layout</label>
                    <select name="layout">
                        <option value="standard" {sel_standard}>Standard</option>
                        <option value="wide" {sel_wide}>Wide</option>
                        <option value="minimal" {sel_minimal}>Minimal</option>
                    </select>
                </div>
                <div class="form-check">
                    <input type="checkbox" name="process_templates" id="pt" value="1" {checked_tpl}>
                    <label for="pt">Enable template processing</label>
                </div>
                <div class="form-check">
                    <input type="checkbox" name="published" id="pub" value="1" {checked_pub}>
                    <label for="pub">Published</label>
                </div>
                <div class="form-group">
                    <label>Content (Markdown)</label>
                    <textarea name="body">{page["body"]}</textarea>
                </div>
                <button type="submit" class="btn btn-primary">Save Changes</button>
            </form>
        </div>
        '''
        return render_admin_page(f'Edit: {page["title"]}', form)

    page['title'] = request.form.get('title', page['title'])
    page['body'] = request.form.get('body', page['body'])
    page['layout'] = request.form.get('layout', page.get('layout', 'standard'))
    page['process_templates'] = request.form.get('process_templates') == '1'
    page['published'] = request.form.get('published') == '1'
    page['modified'] = datetime.utcnow()
    page['author'] = session.get('user', 'unknown')

    return redirect(url_for('admin_pages'))


@app.route('/panel/pages/remove/<slug>', methods=['POST'])
@require_role('admin')
def admin_page_delete(slug):
    if slug in PAGES:
        del PAGES[slug]
    return redirect(url_for('admin_pages'))


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------

@app.errorhandler(404)
def not_found(e):
    body = '<h1>Page Not Found</h1><p>The requested page could not be found.</p>'
    return render_site_page('Not Found', body, session.get('user')), 404


@app.errorhandler(403)
def forbidden(e):
    body = '<h1>Access Denied</h1><p>You do not have permission to access this resource.</p>'
    return render_site_page('Forbidden', body, session.get('user')), 403


@app.errorhandler(500)
def server_error(e):
    body = '<h1>Internal Error</h1><p>An unexpected error occurred.</p>'
    return render_site_page('Error', body, session.get('user')), 500


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
