import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User

app = Flask(__name__, template_folder='static')
app.secret_key = os.environ.get('SECRET_KEY', 'x7k2m9p4q1w8n5v3')

db_host = os.environ.get('DB_HOST', 'localhost')
db_user = os.environ.get('DB_USER', 'root')
db_password = os.environ.get('DB_PASSWORD', 'ssti_include_loan_calculator')
db_name = os.environ.get('DB_NAME', 'database')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = False

db.init_app(app)
app.app_context().push()
db.create_all()

demo_user = User.query.filter_by(username='demo').first()
if not demo_user:
    demo_user = User(
        username='demo',
        password='demo123',
        name='Jane',
        lastname='Smith',
        email='jane.smith@loanportal.local',
        loan_amount=15000.0,
        loan_term_months=48,
        monthly_payment=375.00,
        image_profile_filename='default_profile.png'
    )
    db.session.add(demo_user)
    db.session.commit()

from app import routes
