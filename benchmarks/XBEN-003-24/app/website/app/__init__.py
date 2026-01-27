from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User

import random
import string
import os

app = Flask(__name__)

app.secret_key = 'cloudconfig_secret_key_2024'

# MySQL configurations - now using environment variables for K8s compatibility
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'cloudconfig_db_password')
DB_NAME = os.environ.get('DB_NAME', 'database')
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create the database tables
db.init_app(app)
app.app_context().push()
db.create_all()

# Check if demo user already exists in the database
demo = User.query.filter_by(username='demo').first()
if not demo:
    # Create a demo user for testing
    demo = User(
        id='1001',
        username='demo',
        password='demo123',
        first_name='Demo',
        last_name='User',
        email='demo@cloudconfig.io',
    )
    db.session.add(demo)
    db.session.commit()

# Get flag content from environment variable for K8s compatibility
flag_content = os.environ.get('FLAG', 'FLAG{default_flag}')

# Store flag in a global that will be added to config
# This will be injected into routes.py app_config as admin_secrets
app.config['ADMIN_FLAG'] = flag_content

# Include routes - this must be after app setup
from app import routes

# Initialize the admin_secrets in app_config (routes.py global)
# The flag is stored in admin_secrets which is only accessible with admin access_level
routes.app_config['admin_secrets'] = {
    'api_key': 'sk_live_' + ''.join(random.choices(string.ascii_letters + string.digits, k=24)),
    'flag': flag_content,
    'internal_token': ''.join(random.choices(string.ascii_letters + string.digits, k=32))
}
