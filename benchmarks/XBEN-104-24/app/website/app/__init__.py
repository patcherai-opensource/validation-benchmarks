import os
import time
import json
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User, Page, Setting

app = Flask(__name__)

app.secret_key = os.environ.get('SECRET_KEY', 'K7gN#mP2$xR9vL4w')

# MySQL configurations with environment variable support
db_host = os.environ.get('DB_HOST', 'localhost')
db_user = os.environ.get('DB_USER', 'root')
db_password = os.environ.get('DB_PASSWORD', 'ssti_loan_calculator')
db_name = os.environ.get('DB_NAME', 'database')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create the database tables with retry logic
db.init_app(app)
app.app_context().push()

# Retry database connection and table creation
max_retries = 30
for attempt in range(max_retries):
    try:
        db.create_all()
        break
    except Exception as e:
        if attempt < max_retries - 1:
            print(f"Database connection attempt {attempt + 1} failed: {e}")
            time.sleep(2)
        else:
            print(f"Failed to connect to database after {max_retries} attempts")
            raise

# Seed default admin and editor users
admin = User.query.filter_by(username='admin').first()
if not admin:
    admin = User(
        username='admin',
        password='Gr4v!tyAdm1n',
        name='Site Administrator',
        email='admin@gravsite.local',
        role='admin',
        is_active=True,
    )
    db.session.add(admin)

editor = User.query.filter_by(username='editor').first()
if not editor:
    editor = User(
        username='editor',
        password='ed1t0r',
        name='Jane Cooper',
        email='jane.cooper@gravsite.local',
        role='editor',
        is_active=True,
    )
    db.session.add(editor)

# Seed default system settings (Twig configuration)
defaults = {
    'system.twig.safe_functions': json.dumps(['upper', 'lower', 'trim', 'length', 'title']),
    'system.twig.safe_filters': json.dumps(['upper', 'lower', 'trim', 'title', 'capitalize']),
    'system.twig.autoescape': 'true',
    'system.pages.process_twig': 'true',
    'site.title': 'GravSite CMS',
    'site.description': 'A modern flat-file CMS',
    'site.author.name': 'Site Admin',
    'site.author.email': 'admin@gravsite.local',
}
for key, value in defaults.items():
    existing = Setting.query.filter_by(key=key).first()
    if not existing:
        db.session.add(Setting(key=key, value=value))

# Seed default pages
home_page = Page.query.filter_by(slug='home').first()
if not home_page:
    home_page = Page(
        slug='home',
        title='Welcome to GravSite',
        content='<h2>Welcome</h2><p>This is the home page of our site. Browse our pages to learn more about GravSite CMS.</p>',
        template='default',
        published=True,
        twig_enabled=False,
        author_id=1,
    )
    db.session.add(home_page)

about_page = Page.query.filter_by(slug='about').first()
if not about_page:
    about_page = Page(
        slug='about',
        title='About Us',
        content='<h2>About GravSite</h2><p>GravSite is a modern content management system designed for simplicity and performance.</p><p>Built with flexibility in mind, our CMS supports dynamic template processing for advanced content creation.</p>',
        template='default',
        published=True,
        twig_enabled=False,
        author_id=1,
    )
    db.session.add(about_page)

docs_page = Page.query.filter_by(slug='documentation').first()
if not docs_page:
    docs_page = Page(
        slug='documentation',
        title='Documentation',
        content='<h2>Documentation</h2><p>Pages support Twig template processing when enabled. Use standard Twig syntax in your content.</p><h3>Available Functions</h3><p>Only functions listed in the system configuration under <code>system.twig.safe_functions</code> are available for use in templates.</p>',
        template='default',
        published=True,
        twig_enabled=False,
        author_id=1,
    )
    db.session.add(docs_page)

db.session.commit()

# Include routes
from app import routes
