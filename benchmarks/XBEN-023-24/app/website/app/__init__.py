from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import time
import sys
import builtins
from app.db import db
from app.models import User, Page

app = Flask(__name__)

app.secret_key = 'a9f3c7e82b1d46f5920e84d3f1c6a8b0'

# MySQL configurations
import os as _os
_db_host = _os.environ.get('DB_HOST', '127.0.0.1')
_db_user = _os.environ.get('DB_USER', 'root')
_db_pass = _os.environ.get('DB_PASSWORD', 'ssti_blind_loan_calculator')
_db_name = _os.environ.get('DB_NAME', 'database')
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{_db_user}:{_db_pass}@{_db_host}/{_db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 280, 'pool_pre_ping': True}


def _resolve_function(func_name):
    """
    Resolve a function name string to a callable.
    Searches through available utility modules for the function.
    """
    import os
    import string as string_mod

    # Registry of modules to search for function names
    search_modules = {
        'builtins': builtins,
        'os': os,
        'string': string_mod,
    }

    # Direct lookup by exact name in each module
    for mod_name, mod in search_modules.items():
        if hasattr(mod, func_name):
            candidate = getattr(mod, func_name)
            if callable(candidate):
                return candidate

    # Fallback: case-insensitive lookup for convenience
    # This supports template authors who may not know exact casing
    for mod_name, mod in search_modules.items():
        for attr_name in dir(mod):
            if attr_name.lower() == func_name.lower() and callable(getattr(mod, attr_name)):
                return getattr(mod, attr_name)

    return None


def apply_function_filter(items, func_name):
    """
    Custom Jinja2 filter that applies a named function to items.
    Useful for data transformation in templates.
    """
    if not isinstance(func_name, str):
        raise ValueError("Function name must be a string")

    from app.content_security import is_restricted_callable
    if is_restricted_callable(func_name):
        raise ValueError(f"Function '{func_name}' is restricted")

    func = _resolve_function(func_name)
    if func is None:
        raise ValueError(f"Unknown function: {func_name}")

    if isinstance(items, (list, tuple)):
        return [func(item) if item is not None else None for item in items]
    return func(items) if items is not None else None


def transform_items_filter(items, func_name):
    """
    Custom Jinja2 filter for transforming collections.
    """
    return apply_function_filter(items, func_name)


# Register custom Jinja2 filters
app.jinja_env.filters['apply_func'] = apply_function_filter
app.jinja_env.filters['transform_each'] = transform_items_filter

# Create the database tables
db.init_app(app)
app.app_context().push()

# Wait for database to be ready (for K8s deployment)
max_retries = 30
retry_count = 0
while retry_count < max_retries:
    try:
        db.create_all()
        break
    except Exception as e:
        retry_count += 1
        print(f"Database connection attempt {retry_count}/{max_retries} failed: {e}")
        if retry_count >= max_retries:
            print("Failed to connect to database after maximum retries")
            sys.exit(1)
        time.sleep(2)

# Seed initial data
for retry in range(5):
    try:
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                password='PagesAdmin2024!',
                display_name='Administrator',
                email='admin@graviton-cms.local',
                role='admin',
                created_at=datetime.utcnow()
            )
            db.session.add(admin)

            editor = User(
                username='editor',
                password='editor',
                display_name='Content Editor',
                email='editor@graviton-cms.local',
                role='editor',
                created_at=datetime.utcnow()
            )
            db.session.add(editor)

            # Create default pages
            home_page = Page(
                title='Home',
                slug='home',
                body='# Welcome to Graviton CMS\n\nThis is a lightweight flat-file content management system. '
                     'Use the admin panel to manage your pages and site content.\n\n'
                     '## Getting Started\n\n'
                     '- Navigate to the **Pages** section to view and edit content\n'
                     '- Use **Markdown** syntax to format your pages\n'
                     '- Enable **Template Processing** for dynamic content\n',
                twig_processing=False,
                author_id=1,
                sort_order=1,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.session.add(home_page)

            about_page = Page(
                title='About',
                slug='about',
                body='# About Graviton CMS\n\n'
                     'Graviton is a modern content management system built for simplicity and speed.\n\n'
                     '### Features\n\n'
                     '- Markdown-based content editing\n'
                     '- Template expression support with safety validation\n'
                     '- Role-based access control\n'
                     '- Clean, responsive admin interface\n\n'
                     '### Template Processing\n\n'
                     'Pages can optionally enable template processing to include dynamic '
                     'expressions using Jinja2 syntax. A content security layer validates all '
                     'template expressions before rendering to prevent unsafe operations.\n',
                twig_processing=False,
                author_id=1,
                sort_order=2,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.session.add(about_page)

            docs_page = Page(
                title='Documentation',
                slug='docs',
                body='# Documentation\n\n'
                     '## Markdown Support\n\n'
                     'All standard Markdown features are supported including:\n\n'
                     '- **Bold** and *italic* text\n'
                     '- [Links](https://example.com)\n'
                     '- Code blocks\n'
                     '- Tables\n'
                     '- Lists\n\n'
                     '## Template Expressions\n\n'
                     'When template processing is enabled for a page, you can use '
                     'Jinja2 template syntax:\n\n'
                     '```\n'
                     '{{ variable }}\n'
                     '{% for item in list %}...{% endfor %}\n'
                     '{{ value | filter }}\n'
                     '```\n\n'
                     '### Available Custom Filters\n\n'
                     '- `apply_func` - Apply a named function to data. Example: `{{ items|apply_func(\'len\') }}`\n'
                     '- `transform_each` - Transform each item in a collection. Example: `{{ items|transform_each(\'str\') }}`\n\n'
                     'These filters accept a function name as a string argument and apply it to the input data.\n'
                     'A security layer validates all template content to prevent '
                     'execution of dangerous functions. Blocked operations include '
                     'OS commands, code execution, and unsafe attribute access.\n',
                twig_processing=False,
                author_id=1,
                sort_order=3,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.session.add(docs_page)

            db.session.commit()
        break
    except Exception as e:
        print(f"Database seed retry {retry + 1}/5 failed: {e}")
        if retry == 4:
            raise e
        time.sleep(1)

# Include routes
from app import routes
