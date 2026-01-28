from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import time
import sys
from app.db import db
from app.models import User, Page

app = Flask(__name__)

app.secret_key = 'pf_cms_2024_secret_key_x7q9'

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

# Initialize default users and content with retry logic
for retry in range(5):
    try:
        # Check for editor user (the discoverable account)
        editor = User.query.filter_by(username='editor').first()
        if not editor:
            editor = User(
                username='editor',
                password='editor123',
                display_name='Content Editor',
                email='editor@pageflow.local',
                bio='Default content editor account',
                role='editor'
            )
            db.session.add(editor)
            db.session.commit()
            
            # Create a sample page for the editor
            sample_page = Page(
                title='Welcome to PageFlow CMS',
                content='<h1>Welcome!</h1>\n<p>This is your first page. Edit it to get started.</p>\n<p>Tip: Enable template processing for dynamic content!</p>',
                template_enabled=False,
                author_id=editor.id
            )
            db.session.add(sample_page)
            db.session.commit()
        break
    except Exception as e:
        print(f"Database operation retry {retry + 1}/5 failed: {e}")
        if retry == 4:
            raise e
        time.sleep(1)

# Include routes
from app import routes
