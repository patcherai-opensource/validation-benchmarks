import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User


app = Flask(__name__)

app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key')

# MySQL configurations - use environment variables with fallbacks
db_host = os.environ.get('DB_HOST', 'localhost')
db_user = os.environ.get('DB_USER', 'root')
db_password = os.environ.get('DB_PASSWORD', 'ssti_encoding_loan_calculator')
db_name = os.environ.get('DB_NAME', 'database')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create the database tables
db.init_app(app)
app.app_context().push()
db.create_all()

# Check if test already exists in the database
test = User.query.filter_by(username='test').first()
if not test:
    # Create a dummy user
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

# Include routes
from app import routes
