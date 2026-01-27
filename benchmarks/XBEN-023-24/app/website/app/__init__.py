from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import time
import sys
from app.db import db
from app.models import User, Page

app = Flask(__name__)

app.secret_key = 'pagecraft_cms_secret_2024'  # Secret key for session management

# MySQL configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:ssti_blind_loan_calculator@localhost/database'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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

# Initialize default admin user and sample pages
for retry in range(5):
    try:
        # Check if admin user exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            # Create admin user with default credentials
            admin = User(
                username='admin',
                password='admin123',
                name='Administrator',
                email='admin@pagecraft.local',
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            
            # Create sample welcome page
            welcome_page = Page(
                title='Welcome to PageCraft CMS',
                content='<h2>Getting Started</h2><p>Welcome to PageCraft CMS! This is your first page.</p><p>You can enable Twig template processing in page settings to use advanced features like loops and filters.</p>',
                author_id=admin.id,
                twig_enabled=False
            )
            db.session.add(welcome_page)
            
            # Create sample page with Twig example
            twig_example = Page(
                title='Twig Template Examples',
                content='<h2>Template Examples</h2><p>Here are some examples of Twig template features:</p><pre>{{ ["item1", "item2", "item3"] | join(", ") }}</pre><p>Enable Twig processing to see these in action!</p>',
                author_id=admin.id,
                twig_enabled=False
            )
            db.session.add(twig_example)
            db.session.commit()
        break
    except Exception as e:
        print(f"Database operation retry {retry + 1}/5 failed: {e}")
        if retry == 4:
            raise e
        time.sleep(1)

# Include routes
from app import routes
