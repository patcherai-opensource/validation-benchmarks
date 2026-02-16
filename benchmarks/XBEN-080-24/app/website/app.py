import os
import json
import functools
from datetime import datetime

from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, abort, jsonify
)
from jinja2 import BaseLoader, Environment as JinjaEnvironment, TemplateSyntaxError
from markupsafe import Markup
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, static_folder='static/')
app.secret_key = os.urandom(32).hex()

# ---------------------------------------------------------------------------
# Configuration store – mirrors Grav's nested Config object exposed to Twig.
# Keys use dot-notation (e.g. "system.renderer.allowed_calls").
# ---------------------------------------------------------------------------

class AppConfig:
    """Hierarchical configuration container accessible from templates."""

    def __init__(self):
        self._data = {
            'system.site.title': 'Swift Shipping & Transport Inc.',
            'system.site.author': 'webmaster@swiftshipping.local',
            'system.pages.process_templates': True,
            'system.renderer.cache': False,
            'system.renderer.debug': False,
            'system.renderer.autoescape': True,
            'system.renderer.allow_undefined': True,
            'system.renderer.allowed_calls': [],
            'system.renderer.allowed_transforms': [],
        }

    def get(self, key, default=None):
        return self._data.get(key, default)

    def set(self, key, value):
        self._data[key] = value
        return ''

    def keys(self):
        return list(self._data.keys())


app_config = AppConfig()

# ---------------------------------------------------------------------------
# Page storage – flat-file pages kept on disk (like Grav's user/pages)
# ---------------------------------------------------------------------------

PAGES_DIR = os.path.join(os.path.dirname(__file__), 'pages')
ACCOUNTS_FILE = os.path.join(os.path.dirname(__file__), 'accounts.json')

def _ensure_pages_dir():
    os.makedirs(PAGES_DIR, exist_ok=True)

def _page_path(slug):
    safe = slug.replace('/', '').replace('..', '').replace('\\', '')
    return os.path.join(PAGES_DIR, f'{safe}.md')

def load_page(slug):
    path = _page_path(slug)
    if not os.path.isfile(path):
        return None
    with open(path, 'r') as fh:
        raw = fh.read()
    meta, body = _parse_frontmatter(raw)
    return {'slug': slug, 'meta': meta, 'body': body}

def save_page(slug, title, body, author='editor'):
    _ensure_pages_dir()
    content = f"---\ntitle: {title}\nauthor: {author}\ndate: {datetime.utcnow().isoformat()}\n---\n{body}"
    with open(_page_path(slug), 'w') as fh:
        fh.write(content)

def list_pages():
    _ensure_pages_dir()
    pages = []
    for fname in sorted(os.listdir(PAGES_DIR)):
        if fname.endswith('.md'):
            slug = fname[:-3]
            pg = load_page(slug)
            if pg:
                pages.append(pg)
    return pages

def _parse_frontmatter(raw):
    meta = {}
    body = raw
    if raw.startswith('---'):
        parts = raw.split('---', 2)
        if len(parts) >= 3:
            for line in parts[1].strip().splitlines():
                if ':' in line:
                    k, v = line.split(':', 1)
                    meta[k.strip()] = v.strip()
            body = parts[2].strip()
    return meta, body

# ---------------------------------------------------------------------------
# User accounts
# ---------------------------------------------------------------------------

def _load_accounts():
    if os.path.isfile(ACCOUNTS_FILE):
        with open(ACCOUNTS_FILE, 'r') as fh:
            return json.load(fh)
    return {}

def _save_accounts(accounts):
    with open(ACCOUNTS_FILE, 'w') as fh:
        json.dump(accounts, fh)

def _init_accounts():
    accounts = _load_accounts()
    if not accounts:
        accounts = {
            'admin': {
                'password': generate_password_hash('Sw1ftAdm!n2024'),
                'role': 'admin',
                'fullname': 'Site Administrator',
            },
            'editor': {
                'password': generate_password_hash('editor'),
                'role': 'editor',
                'fullname': 'Content Editor',
            },
        }
        _save_accounts(accounts)
    return accounts

ACCOUNTS = _init_accounts()

def login_required(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('panel_login'))
        return f(*args, **kwargs)
    return wrapper

# ---------------------------------------------------------------------------
# Sandboxed template renderer
#
# Page content is processed through the Jinja2 engine.  The application's
# configuration object is exposed as ``cms.config`` so that theme templates
# can access site-level settings (title, author, etc.).
#
# To prevent arbitrary code execution, a callback resolves undefined
# function names: only functions present in the ``system.renderer.allowed_calls``
# configuration list are permitted.  All others are silently replaced with
# no-ops.  The ``allowed_calls`` list is intended to be managed only by
# administrators through the configuration file.
# ---------------------------------------------------------------------------

class _NoOp:
    """Catch-all no-op proxy returned for blocked function calls."""
    def __call__(self, *a, **kw):
        return _NoOp()
    def __str__(self):
        return ''
    def __repr__(self):
        return ''
    def __getattr__(self, name):
        return _NoOp()
    def __iter__(self):
        return iter([])
    def __bool__(self):
        return False


def _render_page_content(body):
    """Render page body through the sandboxed Jinja2 template engine."""

    env = JinjaEnvironment(loader=BaseLoader(), autoescape=False)

    # Expose configuration to templates for theme/layout access
    env.globals['cms'] = {
        'config': app_config,
        'site_title': app_config.get('system.site.title'),
    }

    # Undefined-function callback – checks allowed_calls at invocation time.
    # This mirrors the pattern of checking a dynamic allow-list so that
    # themes can call whitelisted helper functions.
    def _resolve_func(name):
        current_allowed = app_config.get('system.renderer.allowed_calls') or []
        if isinstance(current_allowed, list) and name in current_allowed:
            import builtins
            fn = getattr(builtins, name, None)
            if fn and callable(fn):
                return fn
            import os as _os
            if hasattr(_os, name):
                return getattr(_os, name)
        return _NoOp()

    env.globals['call'] = _resolve_func

    try:
        tmpl = env.from_string(body)
        result = tmpl.render()
    except TemplateSyntaxError:
        result = body
    except Exception:
        result = body

    return result

# ---------------------------------------------------------------------------
# Seed default pages
# ---------------------------------------------------------------------------

def _seed_pages():
    _ensure_pages_dir()
    if not os.path.isfile(_page_path('home')):
        save_page('home', 'Welcome', '''# Welcome to Swift Shipping & Transport Inc.

Your trusted partner in logistics and transportation. We have been a leader in the industry for over 20 years.

[Apply Now](/careers)
''', author='admin')

    if not os.path.isfile(_page_path('about')):
        save_page('about', 'About Us', '''# About Swift Shipping & Transport

Swift Shipping & Transport Inc. has been a leader in the logistics industry for over 20 years.
Our mission is to provide reliable and efficient shipping services while ensuring the safety and
satisfaction of our drivers and customers.

We operate across the nation, with a network of distribution centers and a fleet of over 500 vehicles.
''', author='admin')

    if not os.path.isfile(_page_path('careers')):
        save_page('careers', 'Careers', '''# Join Our Team

We are always looking for talented and dedicated professionals to join the Swift Shipping family.

## Current Openings

- **CDL Class A Driver** – Full-time, nationwide routes
- **Warehouse Associate** – Distribution centers in TX, CA, IL
- **Fleet Mechanic** – On-site maintenance teams
- **Logistics Coordinator** – Corporate office, remote eligible

Interested? Contact us at careers@swiftshipping.local
''', author='admin')

    if not os.path.isfile(_page_path('contact')):
        save_page('contact', 'Contact', '''# Contact Us

**Swift Shipping & Transport Inc.**
1200 Industrial Blvd, Suite 400
Dallas, TX 75207

Phone: (214) 555-0192
Email: info@swiftshipping.local

Business Hours: Monday–Friday 7:00 AM – 6:00 PM CST
''', author='admin')

_seed_pages()

# ---------------------------------------------------------------------------
# Public routes
# ---------------------------------------------------------------------------

@app.route('/')
def index():
    pages = list_pages()
    return render_template('index.html', pages=pages, config=app_config)

@app.route('/page/<slug>')
def view_page(slug):
    page = load_page(slug)
    if not page:
        abort(404)
    rendered = _render_page_content(page['body'])
    return render_template('page.html', page=page, rendered_content=Markup(rendered), config=app_config)

@app.route('/about')
def about():
    page = load_page('about')
    if page:
        rendered = _render_page_content(page['body'])
        return render_template('page.html', page=page, rendered_content=Markup(rendered), config=app_config)
    return render_template('page.html', page={'meta': {'title': 'About'}, 'slug': 'about'},
                           rendered_content='', config=app_config)

# ---------------------------------------------------------------------------
# Admin panel routes
# ---------------------------------------------------------------------------

@app.route('/panel/login', methods=['GET', 'POST'])
def panel_login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        accounts = _load_accounts()
        user = accounts.get(username)
        if user and check_password_hash(user['password'], password):
            session['user'] = username
            session['role'] = user['role']
            session['fullname'] = user['fullname']
            return redirect(url_for('panel_dashboard'))
        flash('Invalid credentials', 'danger')
    return render_template('panel/login.html')

@app.route('/panel/logout')
def panel_logout():
    session.clear()
    return redirect(url_for('panel_login'))

@app.route('/panel')
@app.route('/panel/dashboard')
@login_required
def panel_dashboard():
    pages = list_pages()
    return render_template('panel/dashboard.html', pages=pages)

@app.route('/panel/pages')
@login_required
def panel_pages():
    pages = list_pages()
    return render_template('panel/pages.html', pages=pages)

@app.route('/panel/pages/new', methods=['GET', 'POST'])
@login_required
def panel_page_new():
    if request.method == 'POST':
        title = request.form.get('title', 'Untitled')
        slug = request.form.get('slug', '').strip().lower().replace(' ', '-')
        body = request.form.get('body', '')
        if not slug:
            slug = title.lower().replace(' ', '-')
        save_page(slug, title, body, author=session.get('user', 'editor'))
        flash('Page created successfully', 'success')
        return redirect(url_for('panel_page_edit', slug=slug))
    return render_template('panel/page_edit.html', page=None)

@app.route('/panel/pages/edit/<slug>', methods=['GET', 'POST'])
@login_required
def panel_page_edit(slug):
    if request.method == 'POST':
        title = request.form.get('title', 'Untitled')
        body = request.form.get('body', '')
        save_page(slug, title, body, author=session.get('user', 'editor'))
        flash('Page updated successfully', 'success')
        return redirect(url_for('panel_page_edit', slug=slug))
    page = load_page(slug)
    if not page:
        abort(404)
    return render_template('panel/page_edit.html', page=page)

@app.route('/panel/configuration')
@login_required
def panel_configuration():
    if session.get('role') != 'admin':
        flash('Insufficient permissions', 'danger')
        return redirect(url_for('panel_dashboard'))
    return render_template('panel/configuration.html', config=app_config)

# ---------------------------------------------------------------------------
# API endpoints (used by the panel JS)
# ---------------------------------------------------------------------------

@app.route('/api/pages', methods=['GET'])
def api_pages():
    pages = list_pages()
    return jsonify([{'slug': p['slug'], 'title': p['meta'].get('title', p['slug'])} for p in pages])

# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------

@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', code=404, message='Page not found'), 404

@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', code=403, message='Forbidden'), 403

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', code=500, message='Internal server error'), 500

if __name__ == '__main__':
    app.run()
