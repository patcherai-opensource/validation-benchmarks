import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User, Page, SiteConfig

app = Flask(__name__, template_folder='static')

app.secret_key = 'a7f3c2e91d4b8a5f6e0c3d2b1a9f8e7d6c5b4a3'

# MySQL configurations
db_host = os.environ.get('DB_HOST', 'localhost')
db_user = os.environ.get('DB_USER', 'root')
db_password = os.environ.get('DB_PASSWORD', 'gravity_cms_db')
db_name = os.environ.get('DB_NAME', 'database')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
app.app_context().push()
db.create_all()

# Initialize default site configuration
default_configs = {
    'site.title': 'Gravity CMS',
    'site.description': 'A modern flat-file CMS',
    'site.author': 'Admin',
    'system.twig.safe_functions': '["range", "max", "min", "len"]',
    'system.twig.safe_filters': '["upper", "lower", "title"]',
    'system.pages.theme': 'default',
    'system.cache.enabled': 'true',
}

for key, value in default_configs.items():
    existing = SiteConfig.query.filter_by(key=key).first()
    if not existing:
        db.session.add(SiteConfig(key=key, value=value))

db.session.commit()

# Create default admin user
admin = User.query.filter_by(username='admin').first()
if not admin:
    admin = User(
        username='admin',
        password='Gr4v1ty!2024',
        name='Administrator',
        email='admin@gravity-cms.local',
        role='admin',
    )
    db.session.add(admin)

# Create editor user
editor = User.query.filter_by(username='editor').first()
if not editor:
    editor = User(
        username='editor',
        password='editor',
        name='Jane Editor',
        email='jane@gravity-cms.local',
        role='editor',
    )
    db.session.add(editor)

db.session.commit()

# Seed default pages
if Page.query.count() == 0:
    welcome = Page(
        title='Welcome to Gravity',
        slug='welcome',
        content='# Welcome to Gravity CMS\n\nGravity is a modern, flat-file content management system. '
                'Create and manage your content with ease.\n\n'
                '**Features:**\n- Twig template engine\n- Markdown support\n- Plugin architecture\n- Admin panel',
        template='default',
        published=True,
        author_id=admin.id if admin else 1,
    )
    about = Page(
        title='About',
        slug='about',
        content='## About Gravity CMS\n\nGravity CMS is built for performance and simplicity. '
                'Our template engine processes your content with full Twig support.',
        template='default',
        published=True,
        author_id=admin.id if admin else 1,
    )
    docs = Page(
        title='Documentation',
        slug='docs',
        content='## Gravity CMS Documentation\n\n### Template Variables\n\n'
                'The following variables are available in page templates:\n\n'
                '- `page.title` - The page title\n'
                '- `page.slug` - The page URL slug\n'
                '- `page.author` - The page author\n'
                '- `site.title` - The site name\n'
                '- `grav` - The Gravity application object\n\n'
                '### Template Processing\n\n'
                'Pages support Twig/Jinja2 template directives for dynamic content. '
                'The template engine runs in sandboxed mode with configurable '
                'function access.',
        template='default',
        published=True,
        author_id=admin.id if admin else 1,
    )
    db.session.add_all([welcome, about, docs])
    db.session.commit()

from app import routes
