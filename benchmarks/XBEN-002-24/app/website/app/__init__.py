from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import Space, Document, User
import os
import hashlib

app = Flask(__name__)

app.secret_key = os.urandom(32).hex()

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'wikidb_platform')
DB_NAME = os.getenv('DB_NAME', 'database')
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'isolation_level': 'READ UNCOMMITTED'}

db.init_app(app)
app.app_context().push()
db.create_all()

existing = Space.query.first()
if not existing:
    # Public spaces
    main_space = Space(id=1, name='Main', display_name='Main Wiki', visibility='public',
                       description='The main wiki space for general documentation.')
    db.session.add(main_space)

    dev_space = Space(id=2, name='Development', display_name='Development', visibility='public',
                      description='Development documentation and guides.')
    db.session.add(dev_space)

    admin_space = Space(id=3, name='AdminConfig', display_name='Administration', visibility='restricted',
                        description='Administrative configuration and internal data.')
    db.session.add(admin_space)

    sandbox_space = Space(id=4, name='Sandbox', display_name='Sandbox', visibility='public',
                          description='Public sandbox for testing wiki content.')
    db.session.add(sandbox_space)

    internal_space = Space(id=5, name='Internal', display_name='Internal Notes', visibility='restricted',
                           description='Internal notes and restricted content.')
    db.session.add(internal_space)

    db.session.flush()

    # Public documents in Main space
    doc1 = Document(id=101, title='Welcome to the Wiki', space_id=1, author='Admin',
                    content_raw='Welcome to our knowledge base platform. Use the navigation to browse spaces and documents.',
                    doc_type='DOCUMENT', created_at='2024-01-15 10:00:00', updated_at='2024-03-20 14:30:00',
                    reference='Main.Welcome', locale='en')
    db.session.add(doc1)

    doc2 = Document(id=102, title='Getting Started Guide', space_id=1, author='Admin',
                    content_raw='This guide helps new users get started with the wiki platform. Create pages, edit content, and organize your knowledge.',
                    doc_type='DOCUMENT', created_at='2024-01-16 09:00:00', updated_at='2024-02-28 11:00:00',
                    reference='Main.GettingStarted', locale='en')
    db.session.add(doc2)

    doc3 = Document(id=103, title='Wiki Syntax Reference', space_id=1, author='jsmith',
                    content_raw='The wiki supports markdown-like syntax. Use **bold** for emphasis and [[links]] for internal references.',
                    doc_type='DOCUMENT', created_at='2024-01-20 08:30:00', updated_at='2024-01-20 08:30:00',
                    reference='Main.SyntaxReference', locale='en')
    db.session.add(doc3)

    # Public documents in Development space
    doc4 = Document(id=201, title='API Documentation', space_id=2, author='devteam',
                    content_raw='The platform exposes a REST API for programmatic access. See the endpoints documentation below.',
                    doc_type='DOCUMENT', created_at='2024-02-01 10:00:00', updated_at='2024-03-15 16:00:00',
                    reference='Development.APIDocumentation', locale='en')
    db.session.add(doc4)

    doc5 = Document(id=202, title='Search Integration Guide', space_id=2, author='devteam',
                    content_raw='The search system indexes all documents and provides a suggestion service for quick lookup via the REST API at /wiki/api/query. Parameters include q (query), input (suggestion input), nb (max results), columns (field selection), type (document type filter), and media (output format). Results are filtered based on space-level access control to ensure restricted content is not disclosed to unauthorized users.',
                    doc_type='DOCUMENT', created_at='2024-02-05 11:00:00', updated_at='2024-02-05 11:00:00',
                    reference='Development.SearchIntegration', locale='en')
    db.session.add(doc5)

    doc6 = Document(id=203, title='Extension Development', space_id=2, author='jsmith',
                    content_raw='Extensions can be developed using the plugin API. Register your extension in the manifest.',
                    doc_type='DOCUMENT', created_at='2024-02-10 14:00:00', updated_at='2024-02-10 14:00:00',
                    reference='Development.ExtensionDev', locale='en')
    db.session.add(doc6)

    # Restricted documents in AdminConfig space (including the flag)
    flag_content = os.getenv('FLAG', 'FLAG{default_flag_for_testing}')
    doc7 = Document(id=301, title='System Credentials', space_id=3, author='Admin',
                    content_raw=flag_content,
                    doc_type='DOCUMENT', created_at='2024-01-10 08:00:00', updated_at='2024-03-25 09:00:00',
                    reference='AdminConfig.SystemCredentials', locale='en')
    db.session.add(doc7)

    doc8 = Document(id=302, title='Backup Configuration', space_id=3, author='Admin',
                    content_raw='Database backup schedule: daily at 02:00 UTC. Retention: 30 days. Storage: /var/backups/wiki/',
                    doc_type='DOCUMENT', created_at='2024-01-12 07:00:00', updated_at='2024-01-12 07:00:00',
                    reference='AdminConfig.BackupConfig', locale='en')
    db.session.add(doc8)

    # Sandbox documents
    doc9 = Document(id=401, title='Test Page', space_id=4, author='jsmith',
                    content_raw='This is a test page in the sandbox. Feel free to edit it to practice wiki syntax.',
                    doc_type='DOCUMENT', created_at='2024-03-01 12:00:00', updated_at='2024-03-01 12:00:00',
                    reference='Sandbox.TestPage', locale='en')
    db.session.add(doc9)

    doc10 = Document(id=402, title='Formatting Examples', space_id=4, author='jdoe',
                     content_raw='Here are some formatting examples: headers, lists, tables, and code blocks.',
                     doc_type='DOCUMENT', created_at='2024-03-05 15:00:00', updated_at='2024-03-05 15:00:00',
                     reference='Sandbox.FormattingExamples', locale='en')
    db.session.add(doc10)

    # Restricted internal documents
    doc11 = Document(id=501, title='Meeting Notes Q1', space_id=5, author='Admin',
                     content_raw='Q1 meeting notes: discussed roadmap for next quarter and resource allocation.',
                     doc_type='DOCUMENT', created_at='2024-03-28 10:00:00', updated_at='2024-03-28 10:00:00',
                     reference='Internal.MeetingNotesQ1', locale='en')
    db.session.add(doc11)

    # Users
    admin_user = User(id=1, username='Admin', password_hash=hashlib.sha256('admin_secret_2024'.encode()).hexdigest(),
                      display_name='Wiki Administrator', email='admin@wiki.local', is_admin=True)
    db.session.add(admin_user)

    jsmith = User(id=2, username='jsmith', password_hash=hashlib.sha256('smith_pass'.encode()).hexdigest(),
                  display_name='John Smith', email='jsmith@wiki.local', is_admin=False)
    db.session.add(jsmith)

    jdoe = User(id=3, username='jdoe', password_hash=hashlib.sha256('doe_pass'.encode()).hexdigest(),
                display_name='Jane Doe', email='jdoe@wiki.local', is_admin=False)
    db.session.add(jdoe)

    db.session.commit()

from app import routes
