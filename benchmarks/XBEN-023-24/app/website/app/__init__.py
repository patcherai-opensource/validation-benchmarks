from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import time
import sys
from app.db import db
from app.models import User, Page

app = Flask(__name__)

app.secret_key = 'x8kZ2mP9qR4wL7nY'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:ssti_blind_loan_calculator@localhost/database'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
app.app_context().push()

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

for retry in range(5):
    try:
        test = User.query.filter_by(username='test').first()
        if not test:
            test = User(
                username='test',
                password='test',
                name='John',
                lastname='Doe',
                email='john@example.com',
                loan_amount=10000.0,
                loan_term_months=60,
                monthly_payment=212.47,
                is_admin=False
            )
            db.session.add(test)
            db.session.commit()
        
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                password='admin',
                name='Admin',
                lastname='User',
                email='admin@loanportal.local',
                loan_amount=0.0,
                loan_term_months=0,
                monthly_payment=0.0,
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
        
        about_page = Page.query.filter_by(slug='about').first()
        if not about_page:
            about_page = Page(
                title='About Us',
                slug='about',
                content='<h1>About Our Loan Calculator</h1><p>Welcome to our loan calculator service. We provide tools to help you understand your loan payments.</p>',
                twig_enabled=False,
                published=True,
                author_id=admin.id
            )
            db.session.add(about_page)
            db.session.commit()
        
        break
    except Exception as e:
        print(f"Database operation retry {retry + 1}/5 failed: {e}")
        if retry == 4:
            raise e
        time.sleep(1)

from app import routes
