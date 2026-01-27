from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response, send_file

from app import app
from app.db import db
from app.models import User

import os
import json


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['X-Powered-By'] = 'DocPortal/2.1.0'
    return response



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
            # If login successful, redirect to dashboard
            return redirect(url_for('dashboard'))
        else:
            # If login fails, redirect back to login page with an error message
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')


@app.route('/logout')
def logout():
    # Clear user ID from session
    session.pop('user_id', None)
    return redirect(url_for('login'))


@app.route('/dashboard')
def dashboard():
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        return render_template('dashboard.html', user=user)
    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))


@app.route('/settings', methods=['GET', 'POST'])
def settings():
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
            return redirect(url_for('dashboard'))
        else:
            # Render settings template with user's information for GET request
            return render_template('settings.html', user=user)
    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))


@app.route('/docs')
def docs():
    """Documentation listing page"""
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        return render_template('docs.html', user=user)
    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))


def resolve_layout_path(layout_name):
    """
    Resolves layout path - if no extension provided, adds .html
    This mimics express-handlebars behavior
    """
    if not layout_name:
        return None
    
    # Add .html extension if not present (similar to express-handlebars adding .handlebars)
    if not os.path.splitext(layout_name)[1]:
        layout_name = layout_name + '.html'
    
    # Resolve path relative to layouts directory
    layouts_dir = app.config.get('LAYOUTS_DIR', os.path.join(os.path.dirname(__file__), 'layouts'))
    return os.path.join(layouts_dir, layout_name)


@app.route('/view')
def view_document():
    """
    View a document with optional custom layout
    Similar to express-handlebars vulnerability where layout parameter 
    can be controlled by user input leading to path traversal
    """
    # Retrieve user from session
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    user = User.query.get(user_id)
    
    # Get document and layout parameters from query string
    doc = request.args.get('doc', 'welcome')
    layout = request.args.get('layout', 'default')
    
    # Render the document content
    doc_content = ""
    pages_dir = app.config.get('PAGES_DIR', os.path.join(os.path.dirname(__file__), 'pages'))
    
    # Resolve document path
    doc_path = doc
    if not os.path.splitext(doc)[1]:
        doc_path = doc + '.html'
    doc_full_path = os.path.join(pages_dir, doc_path)
    
    try:
        with open(doc_full_path, 'r') as f:
            doc_content = f.read()
    except FileNotFoundError:
        doc_content = f"<p>Document '{doc}' not found.</p>"
    except Exception as e:
        doc_content = f"<p>Error loading document: {str(e)}</p>"
    
    # VULNERABLE: Resolve layout path without sanitizing user input
    # This allows path traversal via layout parameter
    layout_path = resolve_layout_path(layout)
    
    layout_content = ""
    if layout_path:
        try:
            with open(layout_path, 'r') as f:
                layout_content = f.read()
        except FileNotFoundError:
            # Fallback to default layout if custom layout not found
            default_layout_path = os.path.join(
                app.config.get('LAYOUTS_DIR', os.path.join(os.path.dirname(__file__), 'layouts')),
                'default.html'
            )
            try:
                with open(default_layout_path, 'r') as f:
                    layout_content = f.read()
            except:
                layout_content = "{{content}}"
        except Exception as e:
            return Response(f"Layout error: {str(e)}", status=500)
    
    # Combine layout and content
    if "{{content}}" in layout_content:
        final_html = layout_content.replace("{{content}}", doc_content)
    else:
        # If layout doesn't have content placeholder, just return layout content (file disclosure)
        final_html = layout_content
    
    return render_template_string(final_html, user=user)


@app.route('/api/docs')
def api_docs():
    """API endpoint to list available documents"""
    user_id = session.get('user_id')
    if not user_id:
        return Response(json.dumps({"error": "Unauthorized"}), status=401, mimetype='application/json')
    
    docs_list = [
        {"name": "welcome", "title": "Welcome Guide"},
        {"name": "getting-started", "title": "Getting Started"},
        {"name": "api-reference", "title": "API Reference"},
        {"name": "faq", "title": "FAQ"}
    ]
    
    return Response(json.dumps({"documents": docs_list}), mimetype='application/json')
