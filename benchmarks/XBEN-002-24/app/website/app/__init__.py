from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User, WikiGroup, WikiSpace, WikiDocument, user_groups, space_permissions
import os

app = Flask(__name__)

app.secret_key = os.getenv('SECRET_KEY', 'xwiki-enterprise-secret-2023')

# MySQL configurations
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'idor_indirect_trading_platform')
DB_NAME = os.getenv('DB_NAME', 'database')
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'isolation_level': 'READ UNCOMMITTED'}

db.init_app(app)
app.app_context().push()
db.create_all()

# Seed data
existing = User.query.filter_by(username='admin').first()
if not existing:
    # Groups
    admin_group = WikiGroup(id=1, name='XWikiAdminGroup', description='Platform administrators')
    editors_group = WikiGroup(id=2, name='XWikiEditorGroup', description='Content editors')
    users_group = WikiGroup(id=3, name='XWikiAllGroup', description='All registered users')
    db.session.add_all([admin_group, editors_group, users_group])
    db.session.flush()

    # Users
    admin_user = User(
        id=1,
        username='admin',
        password='admin_Wk9$xR2m',
        first_name='Wiki',
        last_name='Admin',
        email='admin@wiki.local',
        is_active=True
    )
    admin_user.groups.append(admin_group)
    admin_user.groups.append(editors_group)
    admin_user.groups.append(users_group)

    editor_user = User(
        id=2,
        username='editor',
        password='ed1t0r_Pk3!',
        first_name='Content',
        last_name='Editor',
        email='editor@wiki.local',
        is_active=True
    )
    editor_user.groups.append(editors_group)
    editor_user.groups.append(users_group)

    regular_user = User(
        id=3,
        username='jdoe',
        password='Welcome2024!',
        first_name='Jane',
        last_name='Doe',
        email='jdoe@wiki.local',
        is_active=True
    )
    regular_user.groups.append(users_group)

    db.session.add_all([admin_user, editor_user, regular_user])
    db.session.flush()

    # Spaces
    main_space = WikiSpace(
        id=1, name='Main', description='Main wiki space',
        is_public=True
    )
    xwiki_space = WikiSpace(
        id=2, name='XWiki', description='XWiki system space',
        is_public=True
    )
    internal_space = WikiSpace(
        id=3, name='Internal', description='Internal documentation',
        is_public=False
    )
    internal_space.allowed_groups.append(editors_group)
    internal_space.allowed_groups.append(admin_group)

    confidential_space = WikiSpace(
        id=4, name='Confidential', description='Restricted access documents',
        is_public=False
    )
    confidential_space.allowed_groups.append(admin_group)

    help_space = WikiSpace(
        id=5, name='Help', description='Help and documentation',
        is_public=True
    )

    db.session.add_all([main_space, xwiki_space, internal_space, confidential_space, help_space])
    db.session.flush()

    # Public documents in Main space
    db.session.add(WikiDocument(
        id=1, name='WebHome', title='Welcome to the Wiki',
        content='Welcome to our enterprise wiki platform. Use the navigation to browse spaces and documents. For search, use the search bar or the Solr suggest service.',
        space_id=main_space.id, creator_name='admin',
        created_at='2023-01-15', updated_at='2024-03-20',
        version='3.2', tags='home,welcome'
    ))
    db.session.add(WikiDocument(
        id=2, name='GettingStarted', title='Getting Started Guide',
        content='This guide covers the basics of using the wiki platform. You can create pages, organize them into spaces, and collaborate with your team. All content is searchable through our Solr-powered search engine.',
        space_id=main_space.id, creator_name='admin',
        created_at='2023-01-16', updated_at='2024-02-10',
        version='2.1', tags='guide,tutorial'
    ))
    db.session.add(WikiDocument(
        id=3, name='RecentChanges', title='Recent Changes',
        content='Track all recent modifications across the wiki. This page automatically lists documents that have been recently created or updated.',
        space_id=main_space.id, creator_name='admin',
        created_at='2023-01-15', updated_at='2024-11-01',
        version='1.0', tags='changes,tracking'
    ))

    # XWiki system space documents
    db.session.add(WikiDocument(
        id=4, name='SuggestSolrService', title='Solr Search Suggestion Service',
        content='This page provides the Solr-based search suggestion API. It is used by the search bar for autocomplete functionality. Parameters: query, fl, nb, input, outputSyntax, media.',
        space_id=xwiki_space.id, creator_name='admin',
        created_at='2023-01-15', updated_at='2023-06-01',
        version='1.5', tags='system,search,solr'
    ))
    db.session.add(WikiDocument(
        id=5, name='SuggestSolrMacros', title='Solr Search Macros',
        content='Macro definitions for the Solr search suggestion service. Handles parameter parsing and query construction for the search backend.',
        space_id=xwiki_space.id, creator_name='admin',
        created_at='2023-01-15', updated_at='2023-06-01',
        version='1.3', tags='system,macros'
    ))
    db.session.add(WikiDocument(
        id=6, name='Registration', title='User Registration',
        content='User self-registration is currently disabled. Please contact an administrator to create an account.',
        space_id=xwiki_space.id, creator_name='admin',
        created_at='2023-01-15', updated_at='2024-01-10',
        version='2.0', tags='system,registration'
    ))

    # Internal documents (restricted to editors and admins)
    db.session.add(WikiDocument(
        id=7, name='ProjectRoadmap', title='Q4 2024 Project Roadmap',
        content='Planned features for Q4: 1. Enhanced search capabilities 2. Real-time collaboration 3. API v2 rollout 4. Migration to new storage backend.',
        space_id=internal_space.id, creator_name='editor',
        created_at='2024-09-01', updated_at='2024-10-15',
        version='1.4', tags='roadmap,planning'
    ))
    db.session.add(WikiDocument(
        id=8, name='MeetingNotes', title='Team Meeting Notes - October 2024',
        content='Attendees: Admin, Editor, DevTeam. Topics: Search performance optimization, new permission model review, Solr index tuning. Action items assigned.',
        space_id=internal_space.id, creator_name='editor',
        created_at='2024-10-20', updated_at='2024-10-20',
        version='1.0', tags='meetings,notes'
    ))
    db.session.add(WikiDocument(
        id=9, name='StyleGuide', title='Content Style Guide',
        content='Follow these guidelines when creating wiki content: use headings, keep paragraphs short, include relevant tags, link to related documents.',
        space_id=internal_space.id, creator_name='editor',
        created_at='2024-03-01', updated_at='2024-08-15',
        version='2.0', tags='guidelines,style'
    ))

    # Confidential documents (restricted to admins only)
    flag_content = os.getenv('FLAG', 'FLAG{default_flag_for_testing}')
    db.session.add(WikiDocument(
        id=10, name='ServerCredentials', title='Production Server Credentials',
        content=flag_content,
        space_id=confidential_space.id, creator_name='admin',
        created_at='2024-01-05', updated_at='2024-11-01',
        version='4.1', tags='credentials,infrastructure'
    ))
    db.session.add(WikiDocument(
        id=11, name='IncidentReport', title='Security Incident Report 2024-Q3',
        content='On August 15, an unauthorized access attempt was detected on the production database. Investigation revealed a misconfigured firewall rule. Issue was resolved within 2 hours. No data was compromised.',
        space_id=confidential_space.id, creator_name='admin',
        created_at='2024-08-16', updated_at='2024-09-01',
        version='1.2', tags='security,incident'
    ))
    db.session.add(WikiDocument(
        id=12, name='ComplianceAudit', title='Annual Compliance Audit Results',
        content='The 2024 compliance audit identified 3 minor findings related to access control logging. All findings have been remediated as of October 2024.',
        space_id=confidential_space.id, creator_name='admin',
        created_at='2024-10-01', updated_at='2024-10-30',
        version='1.0', tags='compliance,audit'
    ))

    # Help documents
    db.session.add(WikiDocument(
        id=13, name='SearchHelp', title='Using the Search Feature',
        content='The wiki provides a powerful Solr-based search engine. You can search across all documents you have access to. Use the search bar for quick lookups or the advanced search for filtered queries.',
        space_id=help_space.id, creator_name='admin',
        created_at='2023-02-01', updated_at='2024-05-15',
        version='1.3', tags='help,search'
    ))
    db.session.add(WikiDocument(
        id=14, name='SpacesAndPermissions', title='Understanding Spaces and Permissions',
        content='Documents are organized into spaces. Each space can be public (accessible to all) or private (restricted to specific groups). Admins manage space permissions through the administration panel.',
        space_id=help_space.id, creator_name='admin',
        created_at='2023-02-01', updated_at='2024-04-20',
        version='2.0', tags='help,permissions,spaces'
    ))

    db.session.commit()

from app import routes
