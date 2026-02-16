import os
import hashlib
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import Account, ContentPage, SiteConfig

app = Flask(__name__, template_folder='static')

app.secret_key = os.urandom(24).hex()

# Database configurations
db_host = os.environ.get('DB_HOST', 'localhost')
db_user = os.environ.get('DB_USER', 'root')
db_password = os.environ.get('DB_PASSWORD', 'flatcms_db')
db_name = os.environ.get('DB_NAME', 'database')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
app.app_context().push()
db.create_all()

# Initialize default site configuration
def _seed_config():
    defaults = {
        'site.title': 'My CMS',
        'site.description': 'A lightweight flat-file content management system',
        'site.author': 'Admin',
        'pages.process_twig': 'true',
        'twig.autoescape': 'false',
        'twig.cache': 'true',
        'twig.debug': 'false',
        'system.timezone': 'UTC',
    }
    for k, v in defaults.items():
        if not SiteConfig.query.filter_by(key=k).first():
            db.session.add(SiteConfig(key=k, value=v))
    db.session.commit()

_seed_config()

# Create default editor account if not exists
editor = Account.query.filter_by(username='editor').first()
if not editor:
    editor = Account(
        username='editor',
        password_hash=hashlib.sha256('editor'.encode()).hexdigest(),
        display_name='Site Editor',
        email='editor@example.com',
        role='editor'
    )
    db.session.add(editor)
    db.session.commit()

# Create default content pages
def _seed_pages():
    pages_data = [
        {
            'slug': 'home',
            'title': 'Home',
            'body': '# Welcome to My CMS\n\nThis is a lightweight content management system built for simplicity and speed.\n\n## Features\n\n- Flat-file inspired content management\n- Template processing with Twig-style syntax\n- Simple page editor for content creators\n- Responsive design\n\nFeel free to explore the site and manage your content through the admin panel.',
            'template_name': 'default',
            'process_twig': False,
            'published': True,
            'sort_order': 1,
        },
        {
            'slug': 'about',
            'title': 'About',
            'body': '# About This Site\n\nThis CMS is inspired by flat-file content management systems like Grav. It provides a simple interface for managing web content without the overhead of a heavy framework.\n\n## Technology\n\n- Built with Python and Flask\n- Markdown-based content\n- Template processing via Jinja2\n- MySQL backend for content storage',
            'template_name': 'default',
            'process_twig': False,
            'published': True,
            'sort_order': 2,
        },
        {
            'slug': 'typography',
            'title': 'Typography',
            'body': '# Typography Samples\n\n## Headings\n\n# Heading 1\n## Heading 2\n### Heading 3\n#### Heading 4\n\n## Paragraphs\n\nLorem ipsum dolor sit amet, consectetur adipiscing elit. Praesent risus leo, dictum in vehicula sit amet, feugiat tempus tellus.\n\n## Emphasis\n\n**Bold text** and *italic text* and ~~strikethrough~~.\n\n## Lists\n\n- Item one\n- Item two\n- Item three\n\n1. First\n2. Second\n3. Third',
            'template_name': 'default',
            'process_twig': False,
            'published': True,
            'sort_order': 3,
        },
        {
            'slug': 'dynamic-content',
            'title': 'Dynamic Content',
            'body': '# Dynamic Content Example\n\nThis page demonstrates template processing capabilities.\n\n**Site Title:** {{ site.title }}\n\n**Site Description:** {{ site.description }}\n\n## Available Pages\n\n{% for p in pages %}\n- {{ p.title }} (`/page/{{ p.slug }}`)\n{% endfor %}',
            'template_name': 'default',
            'process_twig': True,
            'published': True,
            'sort_order': 4,
        },
    ]
    for pdata in pages_data:
        if not ContentPage.query.filter_by(slug=pdata['slug']).first():
            page = ContentPage(**pdata)
            db.session.add(page)
    db.session.commit()

_seed_pages()

from app import routes
