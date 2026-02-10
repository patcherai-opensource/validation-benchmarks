import os
import time
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User, LoanNote

app = Flask(__name__)

app.secret_key = os.urandom(24).hex()

app.config['PROPAGATE_EXCEPTIONS'] = False

db_host = os.environ.get('DB_HOST', 'localhost')
db_user = os.environ.get('DB_USER', 'root')
db_password = os.environ.get('DB_PASSWORD', 'ssti_loan_calculator')
db_name = os.environ.get('DB_NAME', 'database')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
app.app_context().push()

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
        monthly_payment=212.47
    )
    db.session.add(test)
    db.session.commit()

from app import routes
