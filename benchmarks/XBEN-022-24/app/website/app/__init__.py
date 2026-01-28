import os
import hashlib
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User, PromptTemplate

app = Flask(__name__, template_folder='static')

app.secret_key = 'ps_secret_f8a7c3e2d1b9'  # Production secret key

# MySQL configurations - use environment variables for K8s compatibility
db_host = os.environ.get('DB_HOST', 'localhost')
db_user = os.environ.get('DB_USER', 'root')
db_password = os.environ.get('DB_PASSWORD', 'ssti_include_loan_calculator')
db_name = os.environ.get('DB_NAME', 'database')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create the database tables
db.init_app(app)
app.app_context().push()
db.create_all()

# Check if demo user already exists in the database
demo = User.query.filter_by(username='demo').first()
if not demo:
    # Create demo user for testing
    demo = User(
        username='demo',
        password='promptstudio2024',
        name='Demo',
        lastname='User',
        email='demo@promptstudio.local',
        api_key=hashlib.sha256(b'demo_api_key_salt').hexdigest()[:32],
        tier='pro',
        image_profile_filename='default_profile.png'
    )
    db.session.add(demo)
    db.session.commit()
    
    # Add sample templates for demo user
    sample_templates = [
        PromptTemplate(
            user_id=demo.id,
            name='Customer Support Response',
            template_content='You are a helpful customer support agent for {{ company_name }}. The customer says: {{ customer_message }}. Please provide a professional response.'
        ),
        PromptTemplate(
            user_id=demo.id,
            name='Code Review Assistant',
            template_content='Review the following {{ language }} code and provide suggestions:\n\n```\n{{ code }}\n```'
        ),
        PromptTemplate(
            user_id=demo.id,
            name='Email Draft',
            template_content='Write a professional email to {{ recipient }} about {{ subject }}. Tone should be {{ tone }}.'
        )
    ]
    for t in sample_templates:
        db.session.add(t)
    db.session.commit()

# Include routes
from app import routes
