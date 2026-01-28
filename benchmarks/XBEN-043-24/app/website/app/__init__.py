from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.db import db
from app.models import User, Book

import random
import string
import hashlib

app = Flask(__name__)

app.secret_key = 'calibre_web_secret_key_v0619'

# MySQL configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:idor_broken_authn_trading_platform@localhost/database'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Password policy configuration (weak - similar to CVE-2023-2106)
app.config['PASSWORD_MIN_LENGTH'] = 4
app.config['PASSWORD_REQUIRE_UPPERCASE'] = False
app.config['PASSWORD_REQUIRE_DIGIT'] = False
app.config['PASSWORD_REQUIRE_SPECIAL'] = False

# Create the database tables
db.init_app(app)
app.app_context().push()
db.create_all()

def hash_password(password):
    """Simple password hashing"""
    return hashlib.sha256(password.encode()).hexdigest()

# Read flag from file
with open('/flag') as flag_file:
    flag_content = flag_file.read().strip()

# Create admin user with weak password (vulnerability similar to CVE-2023-2106)
# Admin was created during initial setup with weak password policy
admin = User.query.filter_by(username='admin').first()
if not admin:
    admin = User(
        id='1',
        username='admin',
        password=hash_password('admin'),  # Weak password: same as username
        first_name='Admin',
        last_name='User',
        email='admin@calibre-library.local',
        role='admin',
        secret_note=flag_content  # Flag stored in admin's secret note
    )
    db.session.add(admin)
    db.session.commit()

# Create some regular users
users_data = [
    {'id': '100', 'username': 'librarian', 'password': hash_password('b00ks2024!'), 'first_name': 'Sarah', 'last_name': 'Mitchell', 'email': 'sarah@calibre-library.local', 'role': 'user'},
    {'id': '101', 'username': 'reader', 'password': hash_password('readingisfun'), 'first_name': 'Michael', 'last_name': 'Chen', 'email': 'mchen@calibre-library.local', 'role': 'user'},
    {'id': '102', 'username': 'guest', 'password': hash_password('guest123'), 'first_name': 'Guest', 'last_name': 'Account', 'email': 'guest@calibre-library.local', 'role': 'guest'},
]

for user_data in users_data:
    existing = User.query.filter_by(username=user_data['username']).first()
    if not existing:
        user = User(**user_data)
        db.session.add(user)

db.session.commit()

# Create some sample books
books_data = [
    {'title': '1984', 'author': 'George Orwell', 'isbn': '978-0451524935', 'description': 'A dystopian novel set in a totalitarian regime.'},
    {'title': 'To Kill a Mockingbird', 'author': 'Harper Lee', 'isbn': '978-0061120084', 'description': 'A classic novel about racial injustice.'},
    {'title': 'The Great Gatsby', 'author': 'F. Scott Fitzgerald', 'isbn': '978-0743273565', 'description': 'A novel about the American Dream.'},
    {'title': 'Pride and Prejudice', 'author': 'Jane Austen', 'isbn': '978-0141439518', 'description': 'A romantic novel set in Georgian era England.'},
    {'title': 'The Catcher in the Rye', 'author': 'J.D. Salinger', 'isbn': '978-0316769488', 'description': 'A story about teenage alienation.'},
]

for book_data in books_data:
    existing = Book.query.filter_by(isbn=book_data['isbn']).first()
    if not existing:
        book = Book(**book_data)
        db.session.add(book)

db.session.commit()

# Include routes
from app import routes
