from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import time
import sys
from app.db import db
from app.models import User, Page

app = Flask(__name__)

app.secret_key = 'your_secret_key'  # Change this to a secure secret key

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

# Check if test already exists in the database with retry logic
for retry in range(5):
    try:
        test = User.query.filter_by(username='test').first()
        if not test:
            # Create a dummy user with page editing permissions
            test = User(
                username='test',
                password='test',
                name='John',
                lastname='Doe',
                email='john@example.com',
                loan_amount=10000.0,
                loan_term_months=60,
                monthly_payment=212.47
            )
            db.session.add(test)
            db.session.commit()
            
            # Create some sample pages
            sample_page = Page(
                title='Welcome to the Loan Calculator',
                content='<h1>Welcome!</h1>\n<p>This is a sample page. You can create your own pages with custom content.</p>\n<p>Tip: Enable Twig processing to use dynamic template features!</p>',
                twig_enabled=False,
                author_id=test.id
            )
            db.session.add(sample_page)
            
            # Create an example page showing template features
            template_example = Page(
                title='Template Features Example',
                content='<h1>Template Features</h1>\n<p>When Twig processing is enabled, you can use template syntax like:</p>\n<ul>\n<li>Variables: {{ "{{ variable }}" }}</li>\n<li>Filters: {{ "{{ value|upper }}" }}</li>\n<li>Custom filters: map, reduce, filter</li>\n</ul>\n<p>Example: {{ "{{ [1,2,3]|map(\'str\') }}" }}</p>',
                twig_enabled=False,
                author_id=test.id
            )
            db.session.add(template_example)
            db.session.commit()
        break
    except Exception as e:
        print(f"Database operation retry {retry + 1}/5 failed: {e}")
        if retry == 4:
            raise e
        time.sleep(1)

# Include routes
from app import routes
