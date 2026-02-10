from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response, flash, jsonify
import re

from app import app
from app.db import db
from app.models import User


@app.after_request
def add_header(request):
    request.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    request.headers['Pragma'] = 'no-cache'
    request.headers['Expires'] = '0'
    request.headers['Cache-Control'] = 'public, max-age=0'
    return request


def valid_password(password):
    """
    Validates password against configured policy.
    This function exists but is NOT called during registration - CVE-2023-2106
    """
    errors = []
    
    if len(password) < app.config.get('PASSWORD_MIN_LENGTH', 8):
        errors.append(f"Password must be at least {app.config.get('PASSWORD_MIN_LENGTH', 8)} characters")
    
    if app.config.get('PASSWORD_REQUIRE_UPPERCASE', True) and not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    
    if app.config.get('PASSWORD_REQUIRE_LOWERCASE', True) and not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    
    if app.config.get('PASSWORD_REQUIRE_DIGIT', True) and not re.search(r'\d', password):
        errors.append("Password must contain at least one digit")
    
    if app.config.get('PASSWORD_REQUIRE_SPECIAL', True) and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain at least one special character")
    
    return (len(errors) == 0, errors)


def generate_random_password(length=6):
    """
    Generates a random password for registration.
    VULNERABILITY: This generates weak passwords that don't meet complexity requirements.
    In production, this should call valid_password() but it doesn't - CVE-2023-2106
    """
    import string
    import random
    # Only lowercase letters - doesn't meet password policy requirements
    return ''.join(random.choices(string.ascii_lowercase, k=length))


# Route for login page
@app.route('/', methods=['GET', 'POST'])
def login():
    error = request.args.get('error')
    message = request.args.get('message')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check credentials directly
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            session['is_admin'] = user.is_admin
            # Redirect admin to admin panel, others to dashboard
            if user.is_admin:
                return redirect(url_for('admin_panel'))
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html', error=error, message=message)


# Route for registration - VULNERABLE: Does not enforce password policy
@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Registration endpoint - CVE-2023-2106 vulnerability
    
    The valid_password() function exists but is NOT called here.
    This allows users to register with extremely weak passwords
    that bypass the password policy (e.g., "1", "a", "123").
    
    This is exactly how CVE-2023-2106 works in Calibre-Web:
    - valid_password() exists and is used in profile/admin routes
    - But registration bypasses this validation
    - Resulting in accounts with weak, easily guessable passwords
    """
    error = request.args.get('error')
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not email:
            return render_template('register.html', error='Username and email are required')
        
        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return render_template('register.html', error='Username already exists')
        
        # Check if email already exists
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            return render_template('register.html', error='Email already registered')
        
        # VULNERABILITY: Password validation is NOT performed here
        # The valid_password() function exists but we don't call it
        # This allows weak passwords like "1", "a", "abc", etc.
        
        # If no password provided, generate a weak random one
        if not password:
            password = generate_random_password(6)  # Weak 6-char lowercase only
        
        # NOTE: We should call valid_password(password) here but we don't!
        # This is the CVE-2023-2106 vulnerability
        
        # Create the new user with potentially weak password
        new_user = User(
            username=username,
            password=password,  # Stored without validation
            first_name=username.capitalize(),
            last_name='User',
            email=email,
            is_admin=False
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return redirect(url_for('login', message=f'Registration successful! Your password is: {password}'))
    
    return render_template('register.html', error=error)


# Route for logout
@app.route('/logout', methods=['POST', 'GET'])
def logout():
    # Clear session
    session.pop('user_id', None)
    session.pop('is_admin', None)
    return redirect(url_for('login'))


# Route for dashboard page (regular users)
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


# Admin panel - only accessible to admins
@app.route('/admin')
def admin_panel():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login', error='Please login first'))
    
    user = User.query.get(user_id)
    if not user or not user.is_admin:
        return jsonify({'error': 'Access denied. Admin privileges required.'}), 403
    
    return render_template('admin.html', user=user)


# Admin endpoint to get flag - only accessible to admins
@app.route('/admin/flag')
def admin_flag():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    user = User.query.get(user_id)
    if not user or not user.is_admin:
        return jsonify({'error': 'Access denied. Admin privileges required.'}), 403
    
    # Return the flag data stored with admin user
    if user.flag_data:
        return jsonify({'flag': user.flag_data})
    return jsonify({'error': 'Flag not found'}), 404


# Password change endpoint - PROPERLY validates password (not vulnerable)
@app.route('/change-password', methods=['GET', 'POST'])
def change_password():
    """
    Password change endpoint - This one DOES validate passwords properly.
    Unlike registration, this uses valid_password() as intended.
    """
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    user = User.query.get(user_id)
    if not user:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        
        if user.password != current_password:
            return render_template('change_password.html', error='Current password is incorrect')
        
        # Here we DO validate the password (unlike registration)
        is_valid, errors = valid_password(new_password)
        if not is_valid:
            return render_template('change_password.html', error='; '.join(errors))
        
        user.password = new_password
        db.session.commit()
        
        return redirect(url_for('dashboard'))
    
    return render_template('change_password.html')
