from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response

from app import app, password_service
from app.db import db
from app.models import User


@app.after_request
def add_header(request):
    request.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    request.headers['Pragma'] = 'no-cache'
    request.headers['Expires'] = '0'
    request.headers['Cache-Control'] = 'public, max-age=0'
    return request



# Route for login page
@app.route('/', methods=['GET', 'POST'])
def login():
    error = request.args.get('error')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form.get('password', '')
        
        # Check if username exists
        user = User.query.filter_by(username=username).first()
        if not user:
            # Render login page with error message if username doesn't exist
            return render_template('login.html', error='User not found')
        
        # Convert user to dictionary for password service
        user_dict = {
            'id': user.id,
            'username': user.username,
            'password': user.password,
            'password_hash_type': user.password_hash_type,
        }
        
        # Use SaltedPasswordService for authentication
        # This is where the CVE-2018-6871 vulnerability is exploited:
        # When user's password is stored as Blowfish but system default is MD5,
        # authentication bypasses password verification due to class inheritance flaw
        if password_service.authenticate_user(user_dict, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html', error=error)


# Route for logout
@app.route('/logout', methods=['POST'])
def logout():
    # Clear session
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('login'))


# Route for dashboard page
@app.route('/dashboard')
def dashboard():
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if user:
            return render_template('dashboard.html', user=user)
    # If user not in session, redirect to login
    return redirect(url_for('login'))
