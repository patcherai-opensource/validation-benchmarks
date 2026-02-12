from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import time
import sys
import os
from datetime import datetime
from app.db import db
from app.models import User, Page, Setting

app = Flask(__name__)

app.secret_key = 'a7f3e2d1b9c8f4a6e5d3c2b1a0f9e8d7c6b5a4f3e2d1c0b9'

# MySQL configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:ssti_blind_loan_calculator@127.0.0.1/database'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_recycle': 280,
    'pool_pre_ping': True,
}

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
                password='Gr4v!tp@ss',
                email='admin@gravpy-cms.local',
                fullname='Administrator',
                is_admin=True,
                created_at=datetime(2023, 1, 15)
            )
            db.session.add(admin)

            # Create default pages
            home_page = Page(
                title='Home',
                slug='home',
                content='<h2>Welcome to GravPy CMS</h2>\n<p>GravPy is a modern flat-file CMS powered by Python and Jinja2 templates.</p>\n<p>This is a demonstration instance.</p>',
                twig_enabled=False,
                published=True,
                author_id=1,
                created_at=datetime(2023, 1, 15)
            )

            about_page = Page(
                title='About',
                slug='about',
                content='<h2>About GravPy CMS</h2>\n<p>GravPy CMS is inspired by Grav CMS, bringing the power of flat-file content management to the Python ecosystem.</p>\n<h3>Features</h3>\n<ul>\n<li>Jinja2/Twig template processing</li>\n<li>Admin panel with page management</li>\n<li>Custom template filters</li>\n<li>Markdown support (coming soon)</li>\n</ul>',
                twig_enabled=False,
                published=True,
                author_id=1,
                created_at=datetime(2023, 2, 1)
            )

            docs_page = Page(
                title='Template Functions',
                slug='template-functions',
                content='<h2>Template Functions Reference</h2>\n<p>When Twig processing is enabled for a page, you can use Jinja2 template syntax in your content.</p>\n<h3>Available Filters</h3>\n<ul>\n<li><code>upper</code> - Convert to uppercase</li>\n<li><code>lower</code> - Convert to lowercase</li>\n<li><code>title</code> - Title case</li>\n<li><code>trim</code> - Strip whitespace</li>\n<li><code>length</code> - Get length</li>\n<li><code>reverse</code> - Reverse string or list</li>\n<li><code>join</code> - Join list elements</li>\n<li><code>split</code> - Split string</li>\n<li><code>apply_func</code> - Apply a named function</li>\n<li><code>map_func</code> - Map a function over a list</li>\n<li><code>execute</code> - Execute a function with the value</li>\n</ul>\n<h3>Example</h3>\n<pre><code>{{ "hello world" | upper }}\n{{ ["a", "b", "c"] | join(", ") }}\n{{ [1, 2, 3] | map_func("str") | join(", ") }}</code></pre>',
                twig_enabled=False,
                published=True,
                author_id=1,
                created_at=datetime(2023, 3, 10)
            )

            contact_page = Page(
                title='Contact',
                slug='contact',
                content='<h2>Contact Us</h2>\n<p>For support, please email support@gravpy-cms.local</p>',
                twig_enabled=False,
                published=True,
                author_id=1,
                created_at=datetime(2023, 4, 5)
            )

            db.session.add_all([home_page, about_page, docs_page, contact_page])

            # Default settings
            settings = [
                Setting(key='site.title', value='GravPy CMS'),
                Setting(key='site.description', value='A modern flat-file CMS'),
                Setting(key='site.author', value='GravPy Team'),
                Setting(key='system.twig.enabled', value='true'),
                Setting(key='system.pages.default_template', value='default'),
                Setting(key='system.security.denylist_enabled', value='true'),
            ]
            db.session.add_all(settings)
            db.session.commit()
        break
    except Exception as e:
        print(f"Database seeding retry {retry + 1}/5 failed: {e}")
        db.session.rollback()
        if retry == 4:
            raise e
        time.sleep(1)

# Include routes
from app import routes
