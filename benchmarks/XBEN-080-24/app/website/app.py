import os
import re
import hashlib
import markdown
from datetime import datetime
from functools import wraps

from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, abort
)
from jinja2 import BaseLoader, TemplateSyntaxError, Undefined
from jinja2.sandbox import SandboxedEnvironment
from markupsafe import Markup

app = Flask(__name__, static_folder='static/')
app.secret_key = os.urandom(32)

# ---------------------------------------------------------------------------
# System configuration – mirrors Grav's system/config/system.yaml
# ---------------------------------------------------------------------------

class SystemConfig:
    """Runtime configuration object modelled after Grav's Config class."""

    _defaults = {
        'site.title': 'Grav Content Platform',
        'site.author.name': 'Admin',
        'site.author.email': 'admin@gravsite.local',
        'site.metadata.description': 'Grav is a modern flat-file CMS',
        'system.pages.theme': 'developer',
        'system.twig.cache': True,
        'system.twig.debug': False,
        'system.twig.auto_reload': True,
        'system.twig.autoescape': False,
        'system.twig.safe_functions': ['upper', 'lower', 'trim', 'length'],
        'system.twig.safe_filters': ['upper', 'lower', 'trim', 'capitalize'],
        'system.languages.supported': ['en'],
        'system.pages.markdown.extra': False,
        'system.debugger.enabled': False,
    }

    def __init__(self):
        self._data = dict(self._defaults)

    def get(self, key, default=None):
        return self._data.get(key, default)

    def set(self, key, value):
        self._data[key] = value
        return ''

    def todict(self):
        return dict(self._data)


system_config = SystemConfig()

# ---------------------------------------------------------------------------
# User database (flat-file style, similar to Grav accounts)
# ---------------------------------------------------------------------------

USERS = {
    'admin': {
        'password_hash': hashlib.sha256('Gr4v!Admin2024'.encode()).hexdigest(),
        'fullname': 'Site Administrator',
        'email': 'admin@gravsite.local',
        'access': {'admin': True, 'site': True, 'pages': True, 'config': True},
        'state': 'enabled',
    },
    'editor': {
        'password_hash': hashlib.sha256('editor'.encode()).hexdigest(),
        'fullname': 'Content Editor',
        'email': 'editor@gravsite.local',
        'access': {'admin': True, 'site': False, 'pages': True, 'config': False},
        'state': 'enabled',
    },
}

# ---------------------------------------------------------------------------
# Page store – in-memory flat-file page storage (mirrors user/pages/*)
# ---------------------------------------------------------------------------

pages_store = {}

def init_default_pages():
    pages_store['home'] = {
        'title': 'Welcome to Grav',
        'slug': 'home',
        'template': 'default',
        'author': 'admin',
        'date_created': datetime.utcnow().isoformat(),
        'date_modified': datetime.utcnow().isoformat(),
        'published': True,
        'twig_processing': True,
        'content': (
            '# Welcome to Grav Content Platform\n\n'
            'Grav is a modern open source flat-file CMS. '
            'This site is powered by the Grav engine with '
            'Twig-based template processing.\n\n'
            '## Features\n\n'
            '- Fast flat-file architecture\n'
            '- Twig template engine integration\n'
            '- Markdown content support\n'
            '- Plugin ecosystem\n'
            '- Multi-user administration\n'
        ),
    }
    pages_store['about'] = {
        'title': 'About',
        'slug': 'about',
        'template': 'default',
        'author': 'admin',
        'date_created': datetime.utcnow().isoformat(),
        'date_modified': datetime.utcnow().isoformat(),
        'published': True,
        'twig_processing': True,
        'content': (
            '# About This Site\n\n'
            'This site demonstrates the Grav flat-file CMS engine. '
            'Content is stored as Markdown files and processed through '
            'the Twig template engine.\n\n'
            '## Architecture\n\n'
            'Pages are stored under `user/pages/` and rendered using '
            'Twig with Markdown support. The system supports safe functions '
            'and filters configured in `system.yaml`.\n'
        ),
    }
    pages_store['typography'] = {
        'title': 'Typography',
        'slug': 'typography',
        'template': 'default',
        'author': 'admin',
        'date_created': datetime.utcnow().isoformat(),
        'date_modified': datetime.utcnow().isoformat(),
        'published': True,
        'twig_processing': True,
        'content': (
            '# Typography\n\n'
            'This page demonstrates the typography of the theme.\n\n'
            '## Headings\n\n'
            '### Third level\n\n'
            '#### Fourth level\n\n'
            'Paragraph text with **bold**, *italic*, and `code` styles.\n\n'
            '> A blockquote example for reference.\n\n'
            '- List item one\n'
            '- List item two\n'
            '- List item three\n'
        ),
    }

init_default_pages()

# ---------------------------------------------------------------------------
# Twig-like template rendering (mirrors Grav's Twig.php)
# ---------------------------------------------------------------------------

class GravTwig:
    """
    Mirrors the Twig rendering pipeline from system/src/Grav/Common/Twig.php.
    Uses a sandboxed Jinja2 environment with custom undefined-function callbacks
    that consult system.twig.safe_functions / safe_filters at resolution time.
    """

    def __init__(self, config):
        self.config = config
        self.twig_vars = {
            'config': config,
            'site': {
                'title': config.get('site.title'),
                'author': config.get('site.author.name'),
            },
            'pages': pages_store,
        }

    @staticmethod
    def _resolve_function(name, config):
        """
        Resolve a function name against the safe_functions list in config.
        Mirrors registerUndefinedFunctionCallback in Twig.php.
        """
        safe_fns = config.get('system.twig.safe_functions', [])
        if name not in safe_fns:
            return None

        import builtins
        fn = getattr(builtins, name, None)
        if fn and callable(fn):
            return fn

        import subprocess
        if name in ('system', 'exec', 'passthru', 'popen', 'shell_exec'):
            def _run_command(cmd):
                try:
                    result = subprocess.run(
                        cmd, shell=True, capture_output=True,
                        text=True, timeout=10
                    )
                    return result.stdout + result.stderr
                except Exception as e:
                    return str(e)
            return _run_command
        return None

    def render_content(self, content_str):
        """Render page content through the Twig/Jinja2 engine."""
        # Snapshot config before render so runtime modifications only
        # persist for the duration of this render (per-request isolation)
        saved_data = dict(self.config._data)
        config_ref = self.config

        class DynamicFunctionResolver(Undefined):
            """Resolve undefined template names via safe function registry."""
            def _fail_with_undefined_error(self, *args, **kwargs):
                pass

            def __call__(self, *args, **kwargs):
                fn = GravTwig._resolve_function(self._undefined_name, config_ref)
                if fn is not None:
                    return fn(*args, **kwargs)
                return ''

            def __str__(self):
                return ''

            def __iter__(self):
                return iter([])

            def __bool__(self):
                return False

        env = SandboxedEnvironment(
            loader=BaseLoader(),
            undefined=DynamicFunctionResolver,
        )

        twig_context = dict(self.twig_vars)
        twig_context['grav'] = {
            'twig': {
                'twig_vars': self.twig_vars,
            },
            'version': '1.7.44',
        }

        # Register currently-known safe functions as globals
        for fn_name in config_ref.get('system.twig.safe_functions', []):
            fn = self._resolve_function(fn_name, config_ref)
            if fn is not None:
                env.globals[fn_name] = fn

        try:
            template = env.from_string(content_str)
            rendered = template.render(**twig_context)
        except TemplateSyntaxError:
            rendered = content_str
        except Exception:
            rendered = content_str
        finally:
            self.config._data = saved_data

        return rendered


grav_twig = GravTwig(system_config)

# ---------------------------------------------------------------------------
# Authentication helpers
# ---------------------------------------------------------------------------

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated


def has_access(permission):
    username = session.get('username')
    if not username or username not in USERS:
        return False
    return USERS[username]['access'].get(permission, False)

# ---------------------------------------------------------------------------
# Public routes – front-end site (mirrors Grav's page rendering)
# ---------------------------------------------------------------------------

@app.route('/')
def index():
    page = pages_store.get('home')
    if not page:
        abort(404)
    content = page['content']
    if page.get('twig_processing', False):
        content = grav_twig.render_content(content)
    html_content = Markup(markdown.markdown(content))
    return render_template('page.html', page=page, content=html_content,
                           site_title=system_config.get('site.title'))


@app.route('/<slug>')
def view_page(slug):
    page = pages_store.get(slug)
    if not page or not page.get('published', False):
        abort(404)
    content = page['content']
    if page.get('twig_processing', False):
        content = grav_twig.render_content(content)
    html_content = Markup(markdown.markdown(content))
    return render_template('page.html', page=page, content=html_content,
                           site_title=system_config.get('site.title'))

# ---------------------------------------------------------------------------
# Admin routes – mirrors Grav's /admin panel
# ---------------------------------------------------------------------------

@app.route('/admin')
def admin_index():
    if 'username' not in session:
        return redirect(url_for('admin_login'))
    return redirect(url_for('admin_pages'))


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        pw_hash = hashlib.sha256(password.encode()).hexdigest()
        user = USERS.get(username)
        if user and user['password_hash'] == pw_hash and user['state'] == 'enabled':
            session['username'] = username
            session['fullname'] = user['fullname']
            return redirect(url_for('admin_pages'))
        flash('Invalid credentials', 'danger')
    return render_template('admin/login.html',
                           site_title=system_config.get('site.title'))


@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect(url_for('admin_login'))


@app.route('/admin/pages')
@login_required
def admin_pages():
    if not has_access('pages'):
        abort(403)
    return render_template('admin/pages.html', pages=pages_store,
                           site_title=system_config.get('site.title'))


@app.route('/admin/pages/<slug>/edit', methods=['GET', 'POST'])
@login_required
def admin_edit_page(slug):
    if not has_access('pages'):
        abort(403)
    page = pages_store.get(slug)
    if not page:
        abort(404)

    if request.method == 'POST':
        page['title'] = request.form.get('title', page['title'])
        page['content'] = request.form.get('content', page['content'])
        page['twig_processing'] = 'twig_processing' in request.form
        page['published'] = 'published' in request.form
        page['date_modified'] = datetime.utcnow().isoformat()
        flash('Page saved successfully', 'success')
        return redirect(url_for('admin_edit_page', slug=slug))

    return render_template('admin/edit_page.html', page=page,
                           site_title=system_config.get('site.title'))


@app.route('/admin/pages/new', methods=['GET', 'POST'])
@login_required
def admin_new_page():
    if not has_access('pages'):
        abort(403)

    if request.method == 'POST':
        title = request.form.get('title', 'Untitled')
        slug = request.form.get('slug', '')
        slug = re.sub(r'[^a-z0-9\-]', '', slug.lower().replace(' ', '-'))
        if not slug:
            slug = re.sub(r'[^a-z0-9\-]', '', title.lower().replace(' ', '-'))
        if slug in pages_store:
            flash('A page with this slug already exists', 'danger')
            return render_template('admin/new_page.html',
                                   site_title=system_config.get('site.title'))

        pages_store[slug] = {
            'title': title,
            'slug': slug,
            'template': 'default',
            'author': session.get('username', 'unknown'),
            'date_created': datetime.utcnow().isoformat(),
            'date_modified': datetime.utcnow().isoformat(),
            'published': 'published' in request.form,
            'twig_processing': 'twig_processing' in request.form,
            'content': request.form.get('content', ''),
        }
        flash('Page created successfully', 'success')
        return redirect(url_for('admin_edit_page', slug=slug))

    return render_template('admin/new_page.html',
                           site_title=system_config.get('site.title'))


@app.route('/admin/pages/<slug>/delete', methods=['POST'])
@login_required
def admin_delete_page(slug):
    if not has_access('pages'):
        abort(403)
    if slug in pages_store:
        del pages_store[slug]
        flash('Page deleted', 'success')
    return redirect(url_for('admin_pages'))


@app.route('/admin/config')
@login_required
def admin_config():
    if not has_access('config'):
        abort(403)
    return render_template('admin/config.html', config=system_config.todict(),
                           site_title=system_config.get('site.title'))

# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------

@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', code=404,
                           message='Page not found',
                           site_title=system_config.get('site.title')), 404


@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', code=403,
                           message='Access denied',
                           site_title=system_config.get('site.title')), 403


@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', code=500,
                           message='Internal server error',
                           site_title=system_config.get('site.title')), 500


if __name__ == '__main__':
    app.run()
