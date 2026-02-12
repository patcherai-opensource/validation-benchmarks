import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from app.db import db
from app.models import User, Page, SiteConfig


app = Flask(__name__)

app.secret_key = os.environ.get('SECRET_KEY', 'a7x9Kp2mQ8vR4wYc')

# MySQL configurations
db_host = os.environ.get('DB_HOST', 'localhost')
db_user = os.environ.get('DB_USER', 'root')
db_password = os.environ.get('DB_PASSWORD', 'grav_cms_db')
db_name = os.environ.get('DB_NAME', 'database')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
app.app_context().push()
db.create_all()

# Initialize default data
def _seed_data():
    # Admin user
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            password='Gr4v!2023',
            email='admin@gravsite.local',
            full_name='Site Administrator',
            role='admin',
            is_active=True,
            created_at=datetime.utcnow()
        )
        db.session.add(admin)
        db.session.flush()

        # Editor user
        editor = User(
            username='editor',
            password='editor123',
            email='editor@gravsite.local',
            full_name='Content Editor',
            role='editor',
            is_active=True,
            created_at=datetime.utcnow()
        )
        db.session.add(editor)
        db.session.flush()

        # Sample pages
        home_page = Page(
            title='Welcome to Grav',
            slug='home',
            content='<h2>Welcome to Grav CMS</h2>\n<p>Grav is a modern flat-file content management system. '
                    'This instance provides full Twig template processing support for dynamic content rendering.</p>\n'
                    '<p>Use the <a href="/admin">admin panel</a> to manage your site content.</p>',
            template='default',
            published=True,
            process_twig=False,
            author_id=admin.id,
            meta_description='Welcome to our Grav-powered website',
            category='general'
        )

        about_page = Page(
            title='About Us',
            slug='about',
            content='<h2>About This Site</h2>\n<p>This website is powered by Grav CMS with '
                    'Twig template processing capabilities.</p>\n'
                    '<h3>Features</h3>\n<ul>\n<li>Dynamic content rendering</li>\n'
                    '<li>Twig template processing</li>\n<li>Admin panel management</li>\n'
                    '<li>Custom filters and extensions</li>\n</ul>',
            template='default',
            published=True,
            process_twig=False,
            author_id=admin.id,
            meta_description='About our Grav CMS site',
            category='general'
        )

        docs_page = Page(
            title='Template Documentation',
            slug='template-docs',
            content='<h2>Twig Template Processing</h2>\n'
                    '<p>Pages with Twig processing enabled can use Jinja2/Twig syntax for dynamic content.</p>\n'
                    '<h3>Available Filters</h3>\n'
                    '<p>The following filters are available for use in templates:</p>\n'
                    '<ul>\n<li><code>upper</code> - Convert to uppercase</li>\n'
                    '<li><code>lower</code> - Convert to lowercase</li>\n'
                    '<li><code>capitalize</code> - Capitalize first letter</li>\n'
                    '<li><code>trim</code> - Remove whitespace</li>\n'
                    '<li><code>length</code> - Get length</li>\n'
                    '<li><code>reverse</code> - Reverse a string or list</li>\n'
                    '<li><code>join</code> - Join list elements</li>\n'
                    '<li><code>map_func</code> - Apply function to list elements</li>\n'
                    '<li><code>nl2br</code> - Newlines to break tags</li>\n'
                    '</ul>\n'
                    '<h3>Security</h3>\n'
                    '<p>Template content is sanitized before processing. '
                    'Dangerous functions are blocked to prevent code execution.</p>',
            template='default',
            published=True,
            process_twig=False,
            author_id=admin.id,
            meta_description='Twig template documentation',
            category='documentation'
        )

        db.session.add_all([home_page, about_page, docs_page])

        # Site configuration
        configs = [
            SiteConfig(key='site.title', value='Grav CMS'),
            SiteConfig(key='site.description', value='A modern flat-file CMS'),
            SiteConfig(key='site.author', value='Admin'),
            SiteConfig(key='system.twig.cache', value='true'),
            SiteConfig(key='system.pages.theme', value='quark'),
        ]
        db.session.add_all(configs)

        db.session.commit()

_seed_data()

from app import routes
