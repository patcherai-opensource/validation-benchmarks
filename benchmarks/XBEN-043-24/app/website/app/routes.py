from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response, flash, jsonify

from app import app
from app.db import db
from app.models import User, Book


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['X-Powered-By'] = 'BookShelf/0.6.19'  # Hint at vulnerable version
    return response


def validate_password(password):
    """
    Weak password validation - vulnerability!
    The validation is too permissive due to misconfigured password policy.
    """
    min_length = app.config.get('PASSWORD_MIN_LENGTH', 1)
    
    # Only check minimum length (which is set to 1 - very weak!)
    if len(password) < min_length:
        return False, f'Password must be at least {min_length} character'
    
    # All other checks are disabled due to weak configuration
    return True, None


# Route for home/login page
@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user_id' in session:
        return redirect(url_for('library'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = request.args.get('error')
    message = request.args.get('message')
    
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            return redirect(url_for('library'))
        else:
            return render_template('login.html', error='Invalid username or password')
    
    return render_template('login.html', error=error, message=message)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if not app.config.get('PUBLIC_REGISTRATION', False):
        return render_template('register.html', error='Registration is currently disabled')
    
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        email = request.form.get('email', '')
        first_name = request.form.get('first_name', 'New')
        last_name = request.form.get('last_name', 'User')
        
        # Check if username already exists
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error='Username already exists')
        
        # Weak password validation (vulnerability!)
        is_valid, error_msg = validate_password(password)
        if not is_valid:
            return render_template('register.html', error=error_msg)
        
        # Create new user
        new_user = User(
            username=username,
            password=password,  # Stored in plaintext (another issue, but not the focus)
            email=email,
            first_name=first_name,
            last_name=last_name,
            role='user'
        )
        db.session.add(new_user)
        db.session.commit()
        
        return redirect(url_for('login', message='Registration successful! Please login.'))
    
    return render_template('register.html')


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/library')
def library():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    # Show all books for admin, only public books for regular users
    if session.get('role') == 'admin':
        books = Book.query.all()
    else:
        books = Book.query.filter_by(is_admin_only=False).all()
    
    return render_template('library.html', user=user, books=books)


@app.route('/book/<int:book_id>')
def view_book(book_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    book = Book.query.get(book_id)
    if not book:
        return render_template('error.html', error='Book not found'), 404
    
    # Check if book is admin-only and user is not admin
    if book.is_admin_only and session.get('role') != 'admin':
        return render_template('error.html', error='Access denied. This book is restricted to administrators.'), 403
    
    user = User.query.get(session['user_id'])
    return render_template('book.html', book=book, user=user)


@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    return render_template('profile.html', user=user)


@app.route('/admin')
def admin_panel():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if session.get('role') != 'admin':
        return render_template('error.html', error='Access denied. Administrator privileges required.'), 403
    
    users = User.query.all()
    books = Book.query.all()
    return render_template('admin.html', users=users, books=books)


# API endpoint for checking if username exists (information disclosure)
@app.route('/api/check-user', methods=['POST'])
def check_user():
    username = request.json.get('username', '') if request.is_json else request.form.get('username', '')
    user = User.query.filter_by(username=username).first()
    if user:
        return jsonify({'exists': True, 'message': 'User found'})
    return jsonify({'exists': False, 'message': 'User not found'})
