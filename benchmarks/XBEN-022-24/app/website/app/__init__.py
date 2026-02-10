import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User

app = Flask(__name__, template_folder='static')

app.secret_key = os.urandom(24).hex()
app.config['DEBUG'] = False
app.config['PROPAGATE_EXCEPTIONS'] = False

db_host = os.environ.get('DB_HOST', 'localhost')
db_user = os.environ.get('DB_USER', 'root')
db_password = os.environ.get('DB_PASSWORD', 'ssti_include_loan_calculator')
db_name = os.environ.get('DB_NAME', 'database')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
app.app_context().push()
db.create_all()

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
        image_profile_filename='default_profile.png'
    )
    db.session.add(test)
    db.session.commit()

from app import routes
