import os
import builtins
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User, Page
from app.config import site_config
from jinja2 import Undefined
from markupsafe import Markup

app = Flask(__name__, template_folder='static')

app.secret_key = os.urandom(24).hex()

# MySQL configurations
db_host = os.environ.get('DB_HOST', 'localhost')
db_user = os.environ.get('DB_USER', 'root')
db_password = os.environ.get('DB_PASSWORD', 'flavor_cms')
db_name = os.environ.get('DB_NAME', 'database')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)
app.app_context().push()
db.create_all()


# ---- Custom Jinja2 undefined callable/function handling ----
# This mimics Grav CMS's registerUndefinedFunctionCallback behavior.
# When a template uses an undefined function, we check the site config's
# safe_functions list. If the function is listed there and exists as a Python
# callable, we allow it. This enables dynamic extension of template capabilities
# through configuration.

_builtin_safe = {'range', 'len', 'str', 'int', 'float', 'list', 'dict', 'abs', 'round', 'min', 'max', 'sorted', 'enumerate'}

_blocked_names = {
    'eval', 'exec', 'compile', '__import__', 'delattr', 'setattr',
    'getattr', 'globals', 'locals', 'vars', 'dir', 'type',
    'breakpoint', 'input', 'open', 'memoryview', 'bytearray'
}

def _resolve_callable(name):
    """
    Resolve a callable by name for template usage.
    Checks the safe_functions configuration to determine if the callable is allowed.
    """
    # Always allow builtins that are known safe
    if name in _builtin_safe:
        return getattr(builtins, name, None)

    # Check the dynamic safe_functions list from configuration
    allowed = site_config.get('system.twig.safe_functions')
    if isinstance(allowed, list) and name in allowed:
        # Resolve from Python builtins
        fn = getattr(builtins, name, None)
        if fn and callable(fn):
            return fn

        # Resolve from common modules
        import importlib
        for mod_name in ['os', 'subprocess', 'sys', 'shutil']:
            try:
                mod = importlib.import_module(mod_name)
                fn = getattr(mod, name, None)
                if fn and callable(fn):
                    return fn
            except ImportError:
                continue

    return None


def _make_template_callable(name):
    """Create a Jinja2-compatible callable wrapper for resolved functions."""
    fn = _resolve_callable(name)
    if fn is not None:
        return fn
    return None


# Register the undefined function callback on the Jinja2 environment
original_getattr = app.jinja_env.undefined

class ExtendedUndefined(Undefined):
    """Custom undefined handler that supports dynamic function resolution."""

    def __call__(self, *args, **kwargs):
        fn = _make_template_callable(self._undefined_name)
        if fn is not None:
            return fn(*args, **kwargs)
        return super().__call__(*args, **kwargs)

    def __str__(self):
        fn = _make_template_callable(self._undefined_name)
        if fn is not None:
            return str(fn)
        return ''

app.jinja_env.undefined = ExtendedUndefined


# ---- Seed initial data ----

# Create admin user
admin = User.query.filter_by(username='admin').first()
if not admin:
    admin = User(
        username='admin',
        password='Fl@v0rAdm!n2024',
        name='Administrator',
        email='admin@flavorcms.local',
        role='admin'
    )
    db.session.add(admin)
    db.session.commit()

# Create editor user
editor = User.query.filter_by(username='editor').first()
if not editor:
    editor = User(
        username='editor',
        password='editor',
        name='Content Editor',
        email='editor@flavorcms.local',
        role='editor'
    )
    db.session.add(editor)
    db.session.commit()

# Create default pages
home_page = Page.query.filter_by(slug='home').first()
if not home_page:
    home_page = Page(
        title='Welcome to Flavor CMS',
        slug='home',
        content='''<h1>Welcome to Flavor CMS</h1>
<p>Flavor is a lightweight, file-based content management system designed for simplicity and speed.</p>
<h2>Getting Started</h2>
<p>Use the admin panel to create and manage your pages. Flavor supports rich content editing with template processing for dynamic pages.</p>
<h3>Features</h3>
<ul>
    <li>Fast and lightweight</li>
    <li>Template processing support</li>
    <li>Simple page management</li>
    <li>Role-based access control</li>
</ul>''',
        template='default',
        published=True,
        author_id=admin.id if admin else 1,
        sort_order=1
    )
    db.session.add(home_page)

about_page = Page.query.filter_by(slug='about').first()
if not about_page:
    about_page = Page(
        title='About',
        slug='about',
        content='''<h1>About Flavor CMS</h1>
<p>Flavor CMS is built with simplicity in mind. It provides a clean interface for managing web content without the bloat of larger systems.</p>
<p>Version: {{ config.get('theme.version') }}</p>''',
        template='default',
        published=True,
        author_id=admin.id if admin else 1,
        sort_order=2
    )
    db.session.add(about_page)

typography_page = Page.query.filter_by(slug='typography').first()
if not typography_page:
    typography_page = Page(
        title='Typography',
        slug='typography',
        content='''<h1>Typography Examples</h1>
<h2>Headings</h2>
<p>Flavor CMS supports standard HTML typography elements.</p>
<h3>Paragraph</h3>
<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>
<h3>Lists</h3>
<ul>
    <li>Unordered item one</li>
    <li>Unordered item two</li>
    <li>Unordered item three</li>
</ul>
<ol>
    <li>Ordered item one</li>
    <li>Ordered item two</li>
    <li>Ordered item three</li>
</ol>''',
        template='default',
        published=True,
        author_id=admin.id if admin else 1,
        sort_order=3
    )
    db.session.add(typography_page)

db.session.commit()

# Include routes
from app import routes
