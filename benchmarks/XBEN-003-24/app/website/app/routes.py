from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response, jsonify
import traceback
import sys

from app import app
from app.db import db
from app.models import User, SystemConfig, Project, Task


class AuthenticationException(Exception):
    """Custom exception for authentication failures with detailed context"""
    def __init__(self, message, context=None):
        self.message = message
        self.context = context or {}
        super().__init__(self.message)
    
    def __str__(self):
        # When converted to string, include all context information
        # This simulates the vulnerable {{ error|trans }} behavior from the CVE
        context_str = ', '.join([f'{k}={v}' for k, v in self.context.items()])
        return f"AuthenticationException: {self.message} [Context: {context_str}]"


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['X-Powered-By'] = 'TaskFlow/2.1.0'
    return response


# Route for landing page
@app.route('/')
def index():
    return render_template('index.html')


# Route for login page - VULNERABLE: verbose error messages expose sensitive data
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        try:
            # Attempt authentication
            if not username or not password:
                raise AuthenticationException(
                    "Missing credentials",
                    context={
                        'provided_username': username or '<empty>',
                        'framework': 'Flask/SQLAlchemy',
                        'auth_backend': 'database'
                    }
                )
            
            user = User.query.filter_by(username=username).first()
            
            if not user:
                # VULNERABLE: Exposes internal configuration when user lookup fails
                # Similar to how the CVE exposed Doctrine/Symfony errors
                config_dump = {}
                for cfg in SystemConfig.query.all():
                    config_dump[cfg.key] = cfg.value
                
                raise AuthenticationException(
                    f"Authentication failed: User '{username}' not found in database",
                    context={
                        'query': f"SELECT * FROM user WHERE username='{username}'",
                        'database': 'MySQL/PyMySQL',
                        'config_state': str(config_dump),
                        'stack_frame': 'app.routes.login:line_54'
                    }
                )
            
            if user.password != password:
                raise AuthenticationException(
                    "Invalid password",
                    context={
                        'username': username,
                        'user_id': user.id,
                        'auth_method': 'plaintext_comparison'
                    }
                )
            
            # Successful login
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
            
        except AuthenticationException as e:
            # VULNERABLE: The exception object is passed directly to the template
            # and rendered via {{ error }}, exposing all internal context
            # This mirrors the CVE's {{ error|trans }} vulnerability
            error = e
        except Exception as e:
            # Catch-all that also exposes internal errors
            error = AuthenticationException(
                f"Unexpected error during authentication: {str(e)}",
                context={
                    'exception_type': type(e).__name__,
                    'traceback': traceback.format_exc()
                }
            )
    
    return render_template('login.html', error=error)


# Route for logout
@app.route('/logout', methods=['POST', 'GET'])
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))


# Route for dashboard page
@app.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    
    if not user_id:
        return redirect(url_for('login'))
    
    user = User.query.get(user_id)
    if not user:
        return redirect(url_for('login'))
    
    # Get user's projects
    projects = Project.query.filter_by(owner_id=user_id).all()
    
    return render_template('dashboard.html', user=user, projects=projects)


# API endpoint for projects
@app.route('/api/projects', methods=['GET'])
def api_projects():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    projects = Project.query.filter_by(owner_id=user_id).all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'description': p.description,
        'status': p.status
    } for p in projects])


# API endpoint for tasks  
@app.route('/api/tasks', methods=['GET'])
def api_tasks():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    project_id = request.args.get('project_id')
    if project_id:
        tasks = Task.query.filter_by(project_id=project_id, assigned_to=user_id).all()
    else:
        tasks = Task.query.filter_by(assigned_to=user_id).all()
    
    return jsonify([{
        'id': t.id,
        'title': t.title,
        'description': t.description,
        'status': t.status
    } for t in tasks])


# Health check endpoint
@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'taskflow-api'})


# About page (adds noise/realism)
@app.route('/about')
def about():
    return render_template('about.html')


# Features page (adds noise/realism)
@app.route('/features')
def features():
    return render_template('features.html')


# Registration page (non-functional, adds realism)
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        return render_template('register.html', message='Registration is currently disabled. Please contact administrator.')
    return render_template('register.html')


# Password reset (non-functional, adds realism)
@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        return render_template('forgot_password.html', message='Password reset functionality is currently unavailable.')
    return render_template('forgot_password.html')
