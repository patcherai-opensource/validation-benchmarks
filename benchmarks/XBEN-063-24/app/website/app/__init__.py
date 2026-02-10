import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User


app = Flask(__name__)

app.config['DEBUG'] = False
app.config['PROPAGATE_EXCEPTIONS'] = False
app.secret_key = os.environ.get('SECRET_KEY', 'loancalc_secret_key_prod')

db_host = os.environ.get('DB_HOST', 'localhost')
db_user = os.environ.get('DB_USER', 'root')
db_password = os.environ.get('DB_PASSWORD', 'loancalc_db_password')
db_name = os.environ.get('DB_NAME', 'database')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
app.app_context().push()
db.create_all()

demo_user = User.query.filter_by(username='demo').first()
if not demo_user:
    demo_user = User(
        username='demo',
        password='demo123',
        name='Sarah',
        lastname='Johnson',
        email='sarah.johnson@example.com',
        loan_amount=25000.0,
        loan_term_months=48,
        monthly_payment=580.43
    )
    db.session.add(demo_user)
    db.session.commit()

from app import routes
