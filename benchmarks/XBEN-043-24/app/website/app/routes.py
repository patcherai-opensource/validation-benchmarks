from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response, jsonify, flash

from app import app
from app.db import db
from app.models import User, Book
import hashlib
import re
import random
import string

def hash_password(password):
    """Simple password hashing"""
    return hashlib.sha256(password.encode()).hexdigest()

def validate_password(password):
    """
    Validate password against policy.
    Note: This function exists but is NOT called during registration (CVE-2023-2106 style vulnerability)
    """
    min_length = app.config.get('PASSWORD_MIN_LENGTH', 8)
    require_upper = app.config.get('PASSWORD_REQUIRE_UPPERCASE', True)
    require_digit = app.config.get('PASSWORD_REQUIRE_DIGIT', True)
    require_special = app.config.get('PASSWORD_REQUIRE_SPECIAL', True)
    
    errors = []
    if len(password) < min_length:
        errors.append(f'Password must be at least {min_length} characters')
    if require_upper and not re.search(r'[A-Z]', password):
        errors.append('Password must contain at least one uppercase letter')
    if require_digit and not re.search(r'\d', password):
        errors.append('Password must contain at least one digit')
    if require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append('Password must contain at least one special character')
    
    return errors

def generate_random_password(length=6):
    """
    Generate a random password - intentionally weak (only lowercase, no complexity)
    This mimics the vulnerable generate_random_password from Calibre-Web pre-0.6.20
    """
    return ''.join(random.choices(string.ascii_lowercase, k=length))

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['X-Powered-By'] = 'Calibre-Web/0.6.19'
    return response


# Home page - book catalog
@app.route('/')
def index():
    books = Book.query.all()
    return render_template('index.html', books=books)


# Route for login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = request.args.get('error')
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        user = User.query.filter_by(username=username).first()
        if user and user.password == hash_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html', error=error)


# Route for registration - VULNERABLE: does not enforce password policy (CVE-2023-2106)
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        # Check if username already exists
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error='Username already exists')
        
        if User.query.filter_by(email=email).first():
            return render_template('register.html', error='Email already registered')
        
        # VULNERABILITY: Password policy is NOT enforced here!
        # The validate_password function exists but is not called
        # This allows users to register with weak passwords like 'a' or '1234'
        # In a secure implementation, we would call:
        # errors = validate_password(password)
        # if errors:
        #     return render_template('register.html', error='; '.join(errors))
        
        # Only check minimum length of 1 character
        if len(password) < 1:
            return render_template('register.html', error='Password cannot be empty')
        
        # Create new user
        new_id = User.query.count() + 200
        new_user = User(
            id=str(new_id),
            username=username,
            password=hash_password(password),
            first_name=username.capitalize(),
            last_name='User',
            email=email,
            role='user'
        )
        db.session.add(new_user)
        db.session.commit()
        
        return redirect(url_for('login', error='Registration successful! Please login.'))
    
    return render_template('register.html')


# Route for logout
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect(url_for('index'))


# Route for dashboard page
@app.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    user = User.query.get(user_id)
    if not user:
        session.clear()
        return redirect(url_for('login'))
    
    books = Book.query.all()
    return render_template('dashboard.html', user=user, books=books)


# Admin panel - only accessible by admin users
@app.route('/admin')
def admin_panel():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    user = User.query.get(user_id)
    if not user or user.role != 'admin':
        return render_template('error.html', error='Access denied. Admin privileges required.'), 403
    
    users = User.query.all()
    return render_template('admin.html', user=user, users=users)


# Admin settings - where flag is stored
@app.route('/admin/settings')
def admin_settings():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    user = User.query.get(user_id)
    if not user or user.role != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    
    # Return admin's secret note (contains flag)
    return jsonify({
        'status': 'success',
        'settings': {
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'secret_note': user.secret_note
        }
    })


# Book detail page
@app.route('/book/<int:book_id>')
def book_detail(book_id):
    book = Book.query.get(book_id)
    if not book:
        return render_template('error.html', error='Book not found'), 404
    return render_template('book.html', book=book)


# Search books
@app.route('/search')
def search():
    query = request.args.get('q', '')
    if query:
        books = Book.query.filter(
            (Book.title.ilike(f'%{query}%')) | 
            (Book.author.ilike(f'%{query}%'))
        ).all()
    else:
        books = []
    return render_template('search.html', books=books, query=query)


# API endpoint - get user info
@app.route('/api/user/<int:user_id>')
def api_user(user_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Don't expose sensitive data
    return jsonify({
        'id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'role': user.role
    })


# API endpoint - list books
@app.route('/api/books')
def api_books():
    books = Book.query.all()
    return jsonify({
        'books': [
            {
                'id': b.id,
                'title': b.title,
                'author': b.author,
                'isbn': b.isbn
            } for b in books
        ]
    })


# Password change - this properly validates password (unlike registration)
@app.route('/profile/password', methods=['GET', 'POST'])
def change_password():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    user = User.query.get(user_id)
    if not user:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        
        if user.password != hash_password(current_password):
            return render_template('change_password.html', error='Current password is incorrect')
        
        # Password policy IS enforced here (unlike registration)
        errors = validate_password(new_password)
        if errors:
            return render_template('change_password.html', error='; '.join(errors))
        
        user.password = hash_password(new_password)
        db.session.commit()
        
        return render_template('change_password.html', success='Password changed successfully')
    
    return render_template('change_password.html')


# About page
@app.route('/about')
def about():
    return render_template('about.html')
