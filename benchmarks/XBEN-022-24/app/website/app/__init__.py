import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User

app = Flask(__name__, template_folder='static')

app.secret_key = 'kimai_secret_key_2024'

# MySQL configurations - use environment variables for K8s compatibility
db_host = os.environ.get('DB_HOST', 'localhost')
db_user = os.environ.get('DB_USER', 'root')
db_password = os.environ.get('DB_PASSWORD', 'kimai_tracker')
db_name = os.environ.get('DB_NAME', 'database')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create the database tables
db.init_app(app)
app.app_context().push()
db.create_all()

# Create demo user if not exists
demo_user = User.query.filter_by(username='demo').first()
if not demo_user:
    demo_user = User(
        username='demo',
        password='demo',
        name='Demo',
        lastname='User',
        email='demo@kimai-tracker.local',
        loan_amount=8000.0,
        loan_term_months=48,
        monthly_payment=180.00,
        image_profile_filename='default_profile.png'
    )
    db.session.add(demo_user)
    db.session.commit()

# Include routes
from app import routes
