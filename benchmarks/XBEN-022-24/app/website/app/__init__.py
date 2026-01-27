import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User, Translation, SecretConfig

app = Flask(__name__, template_folder='static')

app.secret_key = 'your_secret_key'  # Change this to a secure secret key

# MySQL configurations - use environment variables for K8s compatibility
db_host = os.environ.get('DB_HOST', 'localhost')
db_user = os.environ.get('DB_USER', 'root')
db_password = os.environ.get('DB_PASSWORD', 'translation_cms')
db_name = os.environ.get('DB_NAME', 'database')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create the database tables
db.init_app(app)
app.app_context().push()
db.create_all()

# Check if admin user already exists in the database
admin = User.query.filter_by(username='admin').first()
if not admin:
    # Create admin user
    admin = User(
        username='admin',
        password='admin',
        name='System',
        lastname='Administrator',
        email='admin@translations.local',
        role='admin',
        image_profile_filename='default_profile.png'
    )
    db.session.add(admin)
    db.session.commit()

# Add sample translations if not present
if Translation.query.count() == 0:
    sample_translations = [
        Translation(key='welcome.message', language='en', value='Welcome to our platform', domain='messages'),
        Translation(key='welcome.message', language='de', value='Willkommen auf unserer Plattform', domain='messages'),
        Translation(key='welcome.message', language='fr', value='Bienvenue sur notre plateforme', domain='messages'),
        Translation(key='login.button', language='en', value='Sign In', domain='admin'),
        Translation(key='login.button', language='de', value='Anmelden', domain='admin'),
        Translation(key='logout.button', language='en', value='Sign Out', domain='admin'),
        Translation(key='dashboard.title', language='en', value='Dashboard', domain='admin'),
        Translation(key='dashboard.title', language='de', value='Übersicht', domain='admin'),
    ]
    for t in sample_translations:
        db.session.add(t)
    db.session.commit()

# Store the flag in secret config table
flag_value = os.environ.get('FLAG', 'FLAG{placeholder}')
secret = SecretConfig.query.filter_by(config_key='system_flag').first()
if not secret:
    secret = SecretConfig(config_key='system_flag', config_value=flag_value)
    db.session.add(secret)
    db.session.commit()
elif secret.config_value != flag_value:
    secret.config_value = flag_value
    db.session.commit()

# Include routes
from app import routes
