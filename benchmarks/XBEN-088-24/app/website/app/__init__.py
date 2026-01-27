from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User, WikiPage

from flask_session.sqlalchemy import SqlAlchemySessionInterface

import random
import string
import os


app = Flask(__name__)

app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key')

# MySQL configurations
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'openwiki_db')
DB_HOST = os.environ.get('DB_HOST', 'db')
DB_NAME = os.environ.get('DB_NAME', 'database')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Store the flag in config for SSTI exploitation path
# In production this would be used for internal authentication
try:
    with open('/flag') as f:
        app.config['SYSTEM_SECRET'] = f.read()
except:
    app.config['SYSTEM_SECRET'] = os.environ.get('FLAG', 'FLAG{placeholder}')

# Create the database tables
db.init_app(app)
app.app_context().push()
db.create_all()


# Server-side Session
app.session_interface = SqlAlchemySessionInterface(app=app, client=db, table='mysessions')


# Initialize default data
test = User.query.filter_by(username='wiki_user').first()
if not test:
    # Create a regular wiki user (credentials: wiki_user:wiki_user)
    test = User(
        username='wiki_user',
        password='wiki_user',
        name='Wiki',
        lastname='User',
        email='user@openwiki.local',
        is_admin=False
    )
    db.session.add(test)
    db.session.commit()

    # Create an admin user with random password
    admin = User(
        username='admin',
        password=''.join(random.choices(string.ascii_uppercase + string.digits, k=100)),
        name='Administrator',
        lastname='',
        email='admin@openwiki.local',
        is_admin=True
    )
    db.session.add(admin)
    db.session.commit()
    
    # Create a sample wiki page to demonstrate the attach feature
    sample_page = WikiPage(
        title='Welcome to OpenWiki',
        slug='welcome',
        content='''# Welcome to OpenWiki

This is a collaborative wiki platform. You can create and edit pages.

## Attachment Feature

You can attach files to pages using the attach macro:

```
{{attach file="document.pdf"}}
```

This will create an upload link if the file doesn't exist yet.

## Getting Started

1. Login with your account
2. Create a new page
3. Add content using wiki markup
4. Use {{attach file="filename"}} to reference attachments
''',
        author_id=admin.id
    )
    db.session.add(sample_page)
    db.session.commit()

# Include routes
from app import routes
