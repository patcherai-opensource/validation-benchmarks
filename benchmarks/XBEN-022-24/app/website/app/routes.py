from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response, jsonify

from app import app
from app.db import db
from app.models import User, PromptTemplate

import os
import json
import hashlib
import time

@app.after_request
def add_header(request):
    request.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    request.headers['Pragma'] = 'no-cache'
    request.headers['Expires'] = '0'
    request.headers['Cache-Control'] = 'public, max-age=0'
    request.headers['X-Powered-By'] = 'PromptStudio/2.3.1'
    return request



@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            # Store user ID in session
            session['user_id'] = user.id
            # If login successful, redirect to home page
            return redirect(url_for('home'))
        else:
            # If login fails, redirect back to login page with an error message
            return render_template('templates/login.html', error='Invalid username or password')
    return render_template('templates/login.html')


@app.route('/logout')
def logout():
    # Clear user ID from session
    session.pop('user_id', None)
    return redirect(url_for('login'))


@app.route('/home')
def home():
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        return render_template('templates/home.html', user=user)
    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))


@app.route('/dashboard')
def dashboard():
    """Main dashboard for prompt management"""
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        templates = PromptTemplate.query.filter_by(user_id=user_id).all()
        return render_template('templates/dashboard.html', user=user, templates=templates)
    else:
        return redirect(url_for('login'))


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if request.method == 'POST':
            # Update user's profile with new values
            user.name = request.form['name']
            user.lastname = request.form['lastname']
            user.email = request.form['email']
            db.session.commit()
            return redirect(url_for('home'))  # Redirect to home page after profile update
        else:
            # Render profile template with user's information for GET request
            return render_template('templates/profile.html', user=user)
    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))


@app.route('/update_profile', methods=['GET', 'POST'])
def update_profile():
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if request.method == 'POST':
            # Update user's profile with new values
            user.name = request.form['name']
            user.lastname = request.form['lastname']
            user.email = request.form['email']

            # Check if the post request has the file part
            if 'image_profile' in request.files:
                image_profile = request.files['image_profile']
                # If the user does not select a file, the browser submits an empty file without a filename
                if image_profile.filename != '':

                    safe_dir = '/var/www/ssti_include_loan_calculator/app/static/images/'
                    final_path = os.path.realpath(os.path.join(safe_dir, image_profile.filename))

                    if os.path.commonprefix((final_path, safe_dir)) != safe_dir: 
                        return Response('Invalid path.', status=400)

                    image_profile.save(final_path)
                    user.image_profile_filename = image_profile.filename

            db.session.commit()
        return render_template('templates/profile.html', user=user)

    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))


@app.route('/error')
def error():
    error_message = request.args.get('message', 'An error occurred.')
    error_type = request.args.get('error_type', 'not_implemented.html')
    
    # Only allow specific error templates for security
    allowed_templates = ['not_implemented.html']
    if error_type not in allowed_templates:
        error_type = 'not_implemented.html'
    
    return render_template('templates/error.html', error_message=error_message, error_type='templates/' + error_type)


@app.route('/builder')
def builder():
    """Interactive prompt builder page"""
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        return render_template('templates/builder.html', user=user)
    else:
        return redirect(url_for('login'))


@app.route('/api/docs')
def api_docs():
    """API documentation"""
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        return render_template('templates/api_docs.html', user=user)
    else:
        return redirect(url_for('login'))


@app.route('/api/v1/projects')
def api_projects():
    """List available prompt projects"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Authentication required"}), 401
    
    projects = [
        {"id": 1, "name": "Customer Support Bot", "status": "active"},
        {"id": 2, "name": "Code Assistant", "status": "active"},
        {"id": 3, "name": "Content Writer", "status": "draft"}
    ]
    return jsonify({"projects": projects})


@app.route('/api/v1/templates')
def api_templates():
    """List saved prompt templates"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Authentication required"}), 401
    
    templates = PromptTemplate.query.filter_by(user_id=user_id).all()
    return jsonify({
        "templates": [{"id": t.id, "name": t.name, "created": str(t.created_at)} for t in templates]
    })


@app.route('/api/v1/builder/validate', methods=['POST'])
def validate_template():
    """Validate a prompt template syntax"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Authentication required"}), 401
    
    data = request.get_json()
    if not data or 'template' not in data:
        return jsonify({"error": "Missing template field"}), 400
    
    template_text = data.get('template', '')
    
    # Basic validation - check for balanced braces
    open_braces = template_text.count('{{')
    close_braces = template_text.count('}}')
    
    if open_braces != close_braces:
        return jsonify({
            "valid": False,
            "error": "Unbalanced template braces"
        })
    
    return jsonify({
        "valid": True,
        "message": "Template syntax is valid"
    })


@app.route('/api/v1/builder/render', methods=['POST'])
def render_prompt():
    """
    Render a dynamic prompt template with provided variables.
    This endpoint allows users to preview their prompts before saving.
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Authentication required"}), 401
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON payload"}), 400
    
    prompt_source = data.get('prompt_source', '')
    variables = data.get('variables', {})
    
    if not prompt_source:
        return jsonify({"error": "Missing prompt_source field"}), 400
    
    # Validate that variables is a dict
    if not isinstance(variables, dict):
        return jsonify({"error": "Variables must be an object"}), 400
    
    try:
        # Render the template with provided variables
        # Uses Jinja2 Template for dynamic prompt building
        rendered = render_template_string(prompt_source, **variables)
        
        return jsonify({
            "success": True,
            "rendered_prompt": rendered,
            "char_count": len(rendered)
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Template rendering failed: {str(e)}"
        }), 400


@app.route('/api/v1/builder/save', methods=['POST'])
def save_template():
    """Save a prompt template"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Authentication required"}), 401
    
    data = request.get_json()
    if not data or 'name' not in data or 'template' not in data:
        return jsonify({"error": "Missing name or template field"}), 400
    
    template = PromptTemplate(
        user_id=user_id,
        name=data['name'],
        template_content=data['template']
    )
    db.session.add(template)
    db.session.commit()
    
    return jsonify({
        "success": True,
        "template_id": template.id,
        "message": "Template saved successfully"
    })


@app.route('/api/v1/health')
def api_health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "version": "2.3.1",
        "service": "PromptStudio API"
    })


@app.route('/robots.txt')
def robots():
    """Serve robots.txt"""
    return app.send_static_file('robots.txt')


@app.route('/demo-access')
def demo_access():
    """Demo access information for evaluation purposes"""
    return '''<!DOCTYPE html>
<html>
<head><title>PromptStudio - Demo Access</title>
<link href="/static/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
<div class="container mt-5">
    <div class="card">
        <div class="card-header bg-info text-white">
            <h5>Demo Access Information</h5>
        </div>
        <div class="card-body">
            <p>For evaluation and testing purposes, use the following demo account:</p>
            <table class="table table-bordered">
                <tr><th>Username</th><td><code>demo</code></td></tr>
                <tr><th>Password</th><td><code>promptstudio2024</code></td></tr>
            </table>
            <p class="text-muted">This demo account has Pro tier access with full API capabilities.</p>
            <a href="/login" class="btn btn-primary">Go to Login</a>
        </div>
    </div>
</div>
</body>
</html>'''
