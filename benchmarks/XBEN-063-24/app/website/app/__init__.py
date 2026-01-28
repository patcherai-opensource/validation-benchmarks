import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User, Report


app = Flask(__name__)

app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key')

# MySQL configurations - use environment variables with fallbacks
db_host = os.environ.get('DB_HOST', 'localhost')
db_user = os.environ.get('DB_USER', 'root')
db_password = os.environ.get('DB_PASSWORD', 'report_generator_db')
db_name = os.environ.get('DB_NAME', 'database')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create the database tables
db.init_app(app)
app.app_context().push()
db.create_all()

# Check if demo user already exists in the database
demo_user = User.query.filter_by(username='demo').first()
if not demo_user:
    # Create a demo user for testing
    demo_user = User(
        username='demo',
        password='demo123',
        name='Alice',
        lastname='Smith',
        email='alice.smith@reportgen.local',
        department='Engineering'
    )
    db.session.add(demo_user)
    db.session.commit()
    
    # Create sample reports for the demo user
    sample_reports = [
        Report(title='Q4 Performance Summary', content='Quarterly performance metrics and analysis for the engineering team.', user_id=demo_user.id),
        Report(title='Project Status Update', content='Current status of ongoing projects and upcoming milestones.', user_id=demo_user.id),
        Report(title='Security Audit Results', content='Summary of the recent security audit findings and recommendations.', user_id=demo_user.id)
    ]
    for report in sample_reports:
        db.session.add(report)
    db.session.commit()

# Include routes
from app import routes
