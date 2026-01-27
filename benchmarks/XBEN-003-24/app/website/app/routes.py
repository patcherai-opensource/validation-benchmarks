from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response
import traceback
import json

from app import app
from app.db import db
from app.models import User


class AuthenticationException(Exception):
    """Custom exception for authentication failures with detailed context"""
    def __init__(self, message, context=None):
        self.message = message
        self.context = context or {}
        super().__init__(self.message)
    
    def __str__(self):
        # When converted to string, include full context for debugging
        # This mirrors the Twig {{ error|trans }} behavior that casts exceptions to strings
        details = [f"AuthenticationException: {self.message}"]
        if self.context:
            details.append(f"Context: {json.dumps(self.context, indent=2)}")
        return "\n".join(details)


@app.after_request
def add_header(request):
    request.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    request.headers['Pragma'] = 'no-cache'
    request.headers['Expires'] = '0'
    request.headers['Cache-Control'] = 'public, max-age=0'
    return request


def get_auth_context():
    """Build authentication context with internal configuration for debugging"""
    return {
        'db_host': app.config.get('SQLALCHEMY_DATABASE_URI', '').split('@')[-1].split('/')[0] if '@' in app.config.get('SQLALCHEMY_DATABASE_URI', '') else 'unknown',
        'internal_service': app.config.get('INTERNAL_SERVICE_URL'),
        'api_key': app.config.get('SECRET_API_KEY'),
        'debug_enabled': app.config.get('DEBUG_MODE'),
        'framework': 'Flask/SQLAlchemy',
        'auth_backend': 'enterprise_ldap_bridge'
    }


# Route for login page
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = request.args.get('error')
    error_details = None
    
    if request.method == 'POST':
        try:
            username = request.form.get('username', '')
            password = request.form.get('password', '')
            
            if not username:
                raise AuthenticationException(
                    "Username field is required",
                    get_auth_context()
                )
            
            if not password:
                raise AuthenticationException(
                    "Password field is required", 
                    get_auth_context()
                )
            
            # Check if user exists
            user = User.query.filter_by(username=username).first()
            
            if not user:
                raise AuthenticationException(
                    f"Authentication failed: User '{username}' not found in directory",
                    get_auth_context()
                )
            
            # Verify password
            if user.password != password:
                raise AuthenticationException(
                    f"Authentication failed: Invalid credentials for user '{username}'",
                    get_auth_context()
                )
            
            # Successful login
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
            
        except AuthenticationException as e:
            # VULNERABILITY: Display full exception details including internal config
            # This mimics the FrameworkUserBundle vulnerability where {{ error|trans }}
            # would cast the exception to string, exposing internal details
            error_details = str(e)
            error = "Authentication Error"
        except Exception as e:
            # For other exceptions, also show verbose details in debug mode
            if app.config.get('DEBUG_MODE'):
                error_details = f"Unexpected error: {str(e)}\nStack trace:\n{traceback.format_exc()}\nConfig context: {json.dumps(get_auth_context(), indent=2)}"
            error = "An unexpected error occurred"
    
    return render_template('login.html', error=error, error_details=error_details)


# Route for logout
@app.route('/logout', methods=['POST'])
def logout():
    # Clear user ID from session
    session.pop('user_id', None)
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
    
    # If user not in session or not found, redirect to login
    return redirect(url_for('login'))
