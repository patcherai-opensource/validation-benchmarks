import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User, Page, Config

app = Flask(__name__, template_folder='templates', static_folder='static')

app.secret_key = os.environ.get('SECRET_KEY', 'k8dfj3kd9f0alsmc83hf62k')

# MySQL configurations - use environment variables for K8s compatibility
db_host = os.environ.get('DB_HOST', 'localhost')
db_user = os.environ.get('DB_USER', 'root')
db_password = os.environ.get('DB_PASSWORD', 'grav_cms_db')
db_name = os.environ.get('DB_NAME', 'database')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create the database tables
db.init_app(app)
app.app_context().push()
db.create_all()

# Seed default data if not present
admin = User.query.filter_by(username='admin').first()
if not admin:
    admin = User(
        username='admin',
        password='Gr4v!ty2024',
        full_name='Site Administrator',
        email='admin@gravsite.local',
        role='admin',
    )
    db.session.add(admin)
    db.session.commit()

editor = User.query.filter_by(username='editor').first()
if not editor:
    editor = User(
        username='editor',
        password='editor',
        full_name='Jane Mitchell',
        email='jane@gravsite.local',
        role='editor',
    )
    db.session.add(editor)
    db.session.commit()

# Create default pages
if Page.query.count() == 0:
    home_page = Page(
        slug='home',
        title='Welcome to Grav',
        content='<h2>Welcome to Grav</h2>\n<p>Grav is a modern open source flat-file CMS.</p>\n<p>This site is powered by Grav and provides a fast, flexible content management experience.</p>',
        template='default',
        process_twig=False,
        visible=True,
        routable=True,
        author_id=admin.id,
        order=1
    )
    about_page = Page(
        slug='about',
        title='About Us',
        content='<h2>About This Site</h2>\n<p>This is a demonstration site running Grav CMS.</p>\n<p>Grav is built with performance in mind, leveraging a flat-file architecture for speed and simplicity.</p>',
        template='default',
        process_twig=False,
        visible=True,
        routable=True,
        author_id=admin.id,
        order=2
    )
    docs_page = Page(
        slug='documentation',
        title='Documentation',
        content='<h2>Documentation</h2>\n<p>For full documentation, visit <strong>learn.getgrav.org</strong>.</p>\n<h3>Getting Started</h3>\n<p>Grav is easy to install and configure. Check the documentation for detailed setup instructions.</p>',
        template='default',
        process_twig=False,
        visible=True,
        routable=True,
        author_id=admin.id,
        order=3
    )
    db.session.add_all([home_page, about_page, docs_page])
    db.session.commit()

# Seed site configuration
if Config.query.count() == 0:
    defaults = [
        Config(key='site.title', value='Grav Site'),
        Config(key='site.description', value='A Grav CMS powered site'),
        Config(key='site.author.name', value='Site Admin'),
        Config(key='site.author.email', value='admin@gravsite.local'),
        Config(key='system.pages.process.twig', value='true'),
        Config(key='system.twig.cache', value='false'),
        Config(key='system.twig.debug', value='false'),
        Config(key='system.twig.autoescape', value='false'),
    ]
    db.session.add_all(defaults)
    db.session.commit()

# Include routes
from app import routes
