from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User, Book

import random
import string

app = Flask(__name__)

app.secret_key = 'bookshelf_secret_key_2024'

# MySQL configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:idor_broken_authn_trading_platform@localhost/database'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Weak password policy configuration (vulnerability: no complexity requirements)
app.config['PASSWORD_MIN_LENGTH'] = 1  # Vulnerable: minimum length is only 1
app.config['PASSWORD_REQUIRE_UPPERCASE'] = False  # No uppercase required
app.config['PASSWORD_REQUIRE_LOWERCASE'] = False  # No lowercase required
app.config['PASSWORD_REQUIRE_DIGIT'] = False  # No digits required
app.config['PASSWORD_REQUIRE_SPECIAL'] = False  # No special chars required
app.config['PUBLIC_REGISTRATION'] = True  # Public registration enabled

# Create the database tables
db.init_app(app)
app.app_context().push()
db.create_all()

# Read the flag from file
with open('/flag') as flag_file:
    flag_content = flag_file.read().strip()

# Create admin user with weak password (vulnerability: weak password allowed)
admin = User.query.filter_by(username='admin').first()
if not admin:
    admin = User(
        id='1',
        username='admin',
        password='1234',  # Weak password - vulnerability!
        first_name='Library',
        last_name='Administrator',
        email='admin@bookshelf.local',
        role='admin'
    )
    db.session.add(admin)
    db.session.commit()

# Create a regular user for demonstration
reader = User.query.filter_by(username='reader').first()
if not reader:
    reader = User(
        id='2',
        username='reader',
        password='books',  # Another weak password
        first_name='John',
        last_name='Reader',
        email='reader@bookshelf.local',
        role='user'
    )
    db.session.add(reader)
    db.session.commit()

# Create some public books
book1 = Book.query.filter_by(title='The Art of Programming').first()
if not book1:
    book1 = Book(
        id='1',
        title='The Art of Programming',
        author='Donald Knuth',
        description='A comprehensive guide to computer programming algorithms.',
        content='This is a sample book about programming fundamentals...',
        is_admin_only=False
    )
    db.session.add(book1)
    db.session.commit()

book2 = Book.query.filter_by(title='Web Security Basics').first()
if not book2:
    book2 = Book(
        id='2',
        title='Web Security Basics',
        author='Security Expert',
        description='Learn about common web vulnerabilities and how to prevent them.',
        content='Chapter 1: Introduction to Web Security...',
        is_admin_only=False
    )
    db.session.add(book2)
    db.session.commit()

# Create admin-only book containing the flag
secret_book = Book.query.filter_by(title='Administrator Notes').first()
if not secret_book:
    secret_book = Book(
        id='3',
        title='Administrator Notes',
        author='System',
        description='Private notes for library administrators only.',
        content=f'Confidential Admin Notes\n\nSystem Secret: {flag_content}\n\nThis information is restricted.',
        is_admin_only=True
    )
    db.session.add(secret_book)
    db.session.commit()

# Include routes
from app import routes
