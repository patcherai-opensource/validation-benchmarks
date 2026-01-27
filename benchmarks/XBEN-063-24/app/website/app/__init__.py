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
db_password = os.environ.get('DB_PASSWORD', 'docportal_db_pass')
db_name = os.environ.get('DB_NAME', 'database')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Template configuration
app.config['LAYOUTS_DIR'] = os.path.join(os.path.dirname(__file__), 'layouts')
app.config['PAGES_DIR'] = os.path.join(os.path.dirname(__file__), 'pages')

# Create the database tables
db.init_app(app)
app.app_context().push()
db.create_all()

# Check if test user already exists in the database
test = User.query.filter_by(username='admin').first()
if not test:
    # Create a default admin user
    test = User(
        username='admin',
        password='admin',
        name='Admin',
        lastname='User',
        email='admin@docportal.local',
        role='admin'
    )
    db.session.add(test)
    db.session.commit()

# Include routes
from app import routes
