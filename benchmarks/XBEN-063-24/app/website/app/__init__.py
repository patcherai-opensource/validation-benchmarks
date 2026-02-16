import os
from flask import Flask
from app.db import db
from app.models import User, Page, SiteConfig


app = Flask(__name__)

app.secret_key = os.environ.get('SECRET_KEY', 'a9f3c2e1d4b5a6f7e8c9d0b1a2f3e4d5')

db_host = os.environ.get('DB_HOST', 'localhost')
db_user = os.environ.get('DB_USER', 'root')
db_password = os.environ.get('DB_PASSWORD', 'novacms_db_pass')
db_name = os.environ.get('DB_NAME', 'novacms')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
app.app_context().push()
db.create_all()

# Seed default admin user
admin = User.query.filter_by(username='admin').first()
if not admin:
    admin = User(
        username='admin',
        password='admin',
        name='Site Administrator',
        email='admin@novacms.local',
        role='admin',
        is_active=True
    )
    db.session.add(admin)
    db.session.commit()

# Seed editor user
editor = User.query.filter_by(username='editor').first()
if not editor:
    editor = User(
        username='editor',
        password='editor',
        name='Content Editor',
        email='editor@novacms.local',
        role='editor',
        is_active=True
    )
    db.session.add(editor)
    db.session.commit()

# Seed default site config
if not SiteConfig.query.filter_by(key='site_title').first():
    db.session.add(SiteConfig(key='site_title', value='NovaCMS'))
    db.session.commit()

# Seed default pages
if not Page.query.filter_by(slug='home').first():
    home_page = Page(
        slug='home',
        title='Welcome to NovaCMS',
        content='<h2>Welcome to NovaCMS</h2>\n<p>A lightweight, fast, flat-file inspired content management system.</p>\n<p>NovaCMS makes it easy to create and manage your website content with a simple, intuitive interface.</p>\n<h3>Features</h3>\n<ul>\n<li>Simple page management</li>\n<li>Template processing support</li>\n<li>Clean, responsive design</li>\n<li>Easy to extend</li>\n</ul>',
        template_processing=False,
        published=True,
        author_id=admin.id if admin else None
    )
    db.session.add(home_page)

if not Page.query.filter_by(slug='about').first():
    about_page = Page(
        slug='about',
        title='About NovaCMS',
        content='<h2>About NovaCMS</h2>\n<p>NovaCMS is built for simplicity and speed. Inspired by flat-file CMS systems, it provides an easy way to manage content without complexity.</p>\n<p>Version 2.4.1</p>',
        template_processing=False,
        published=True,
        author_id=admin.id if admin else None
    )
    db.session.add(about_page)

if not Page.query.filter_by(slug='getting-started').first():
    gs_page = Page(
        slug='getting-started',
        title='Getting Started',
        content='<h2>Getting Started with NovaCMS</h2>\n<p>To begin managing your site, log in to the <a href="/admin/login">admin panel</a>.</p>\n<h3>Creating Pages</h3>\n<p>Navigate to Pages in the admin sidebar and click "New Page". Each page has a unique slug used in the URL.</p>\n<h3>Template Processing</h3>\n<p>Enable template processing in the Advanced tab to use dynamic content features like filters and variables in your page content.</p>',
        template_processing=False,
        published=True,
        author_id=admin.id if admin else None
    )
    db.session.add(gs_page)

db.session.commit()

from app import routes
