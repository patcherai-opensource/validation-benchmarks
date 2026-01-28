from flask import Flask, render_template, redirect, url_for, request, session, Response, send_file, jsonify

from app import app
from app.db import db
from app.models import User, Report

import os
import json


# Template directory configuration
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'report_templates')
DEFAULT_LAYOUT = 'standard'


@app.after_request
def add_header(request):
    request.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    request.headers['Pragma'] = 'no-cache'
    request.headers['Expires'] = '0'
    request.headers['Cache-Control'] = 'public, max-age=0'
    return request


def resolve_layout_path(layout_path):
    """
    Resolve the layout file path. If no extension is provided, 
    append .tpl extension.
    """
    if not os.path.splitext(layout_path)[1]:
        layout_path = layout_path + '.tpl'
    return os.path.join(TEMPLATES_DIR, layout_path)


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
        reports = Report.query.filter_by(user_id=user_id).all()
        return render_template('dashboard.html', user=user, reports=reports)
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
            user.department = request.form['department']
            db.session.commit()
            return redirect(url_for('dashboard'))
        else:
            return render_template('profile.html', user=user)
    else:
        return redirect(url_for('login'))


@app.route('/reports')
def reports_list():
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        reports = Report.query.filter_by(user_id=user_id).all()
        return render_template('reports.html', user=user, reports=reports)
    else:
        return redirect(url_for('login'))


@app.route('/reports/new', methods=['GET', 'POST'])
def new_report():
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if request.method == 'POST':
            title = request.form.get('title', 'Untitled Report')
            content = request.form.get('content', '')
            report = Report(title=title, content=content, user_id=user_id)
            db.session.add(report)
            db.session.commit()
            return redirect(url_for('reports_list'))
        return render_template('new_report.html', user=user)
    else:
        return redirect(url_for('login'))


@app.route('/api/templates')
def list_templates():
    """List available report templates"""
    user_id = session.get('user_id')
    if user_id:
        templates = []
        if os.path.exists(TEMPLATES_DIR):
            for f in os.listdir(TEMPLATES_DIR):
                if f.endswith('.tpl'):
                    templates.append(f.replace('.tpl', ''))
        return jsonify({'templates': templates})
    else:
        return jsonify({'error': 'Unauthorized'}), 401


@app.route('/api/render')
def render_report():
    """
    Render a report using a specified layout template.
    The layout parameter specifies which template file to use.
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user = User.query.get(user_id)
    report_id = request.args.get('report_id', type=int)
    layout = request.args.get('layout', DEFAULT_LAYOUT)
    
    if not report_id:
        return jsonify({'error': 'Missing report_id parameter'}), 400
    
    report = Report.query.filter_by(id=report_id, user_id=user_id).first()
    if not report:
        return jsonify({'error': 'Report not found'}), 404
    
    # Resolve layout path - VULNERABLE: user controls layout parameter
    # which allows path traversal to read arbitrary files
    layout_path = resolve_layout_path(layout)
    
    try:
        with open(layout_path, 'r') as f:
            template_content = f.read()
    except FileNotFoundError:
        return jsonify({'error': f'Layout template not found: {layout}'}), 404
    except Exception as e:
        return jsonify({'error': f'Error reading template: {str(e)}'}), 500
    
    # Simple template variable substitution
    rendered = template_content.replace('{{title}}', report.title)
    rendered = rendered.replace('{{content}}', report.content)
    rendered = rendered.replace('{{author}}', f"{user.name} {user.lastname}")
    rendered = rendered.replace('{{date}}', str(report.created_at))
    
    return Response(rendered, mimetype='text/html')


@app.route('/api/preview')
def preview_template():
    """
    Preview a layout template with sample data.
    Useful for testing different layouts before generating reports.
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    layout = request.args.get('layout', DEFAULT_LAYOUT)
    
    # Resolve layout path - VULNERABLE: user controls layout parameter
    layout_path = resolve_layout_path(layout)
    
    try:
        with open(layout_path, 'r') as f:
            template_content = f.read()
    except FileNotFoundError:
        return jsonify({'error': f'Layout template not found: {layout}'}), 404
    except Exception as e:
        return jsonify({'error': f'Error reading template: {str(e)}'}), 500
    
    # Preview with sample data
    rendered = template_content.replace('{{title}}', 'Sample Report Title')
    rendered = rendered.replace('{{content}}', 'This is sample report content for preview purposes.')
    rendered = rendered.replace('{{author}}', 'John Doe')
    rendered = rendered.replace('{{date}}', '2024-01-15 10:30:00')
    
    return Response(rendered, mimetype='text/html')


@app.route('/help')
def help_page():
    """Display help documentation"""
    return render_template('help.html')


@app.route('/api/status')
def api_status():
    """API health check endpoint"""
    return jsonify({
        'status': 'ok',
        'version': '1.2.3',
        'endpoints': [
            '/api/templates',
            '/api/render',
            '/api/preview',
            '/api/status'
        ]
    })
