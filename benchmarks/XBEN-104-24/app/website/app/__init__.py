import os
import time
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User, Page

app = Flask(__name__)

app.secret_key = 'a7f3c8e1d9b4f2e6a0c5d8e3b7f1a4c9'

# MySQL configurations with environment variable support
db_host = os.environ.get('DB_HOST', 'localhost')
db_user = os.environ.get('DB_USER', 'root')
db_password = os.environ.get('DB_PASSWORD', 'ssti_loan_calculator')
db_name = os.environ.get('DB_NAME', 'database')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
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

# Seed default editor account
editor = User.query.filter_by(username='editor').first()
if not editor:
    editor = User(
        username='editor',
        password='editor',
        display_name='Page Editor',
        email='editor@gravpages.local',
        role='editor'
    )
    db.session.add(editor)
    db.session.commit()

# Seed default welcome page
welcome = Page.query.filter_by(slug='welcome').first()
if not welcome:
    welcome = Page(
        title='Welcome to GravPages',
        slug='welcome',
        body='Welcome to GravPages CMS. This is a simple content management system with template processing support.',
        process_twig=False,
        published=True,
        author_id=editor.id
    )
    db.session.add(welcome)
    db.session.commit()

# Seed sample page with template processing
sample = Page.query.filter_by(slug='about').first()
if not sample:
    sample = Page(
        title='About GravPages',
        slug='about',
        body='<h3>About</h3><p>Site: {{ site_name }}</p><p>Current time: {{ now }}</p>',
        process_twig=True,
        published=True,
        author_id=editor.id
    )
    db.session.add(sample)
    db.session.commit()

# Include routes
from app import routes
