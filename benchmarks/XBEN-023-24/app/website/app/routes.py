from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response, jsonify
import os

from app import app
from app.db import db
from app.models import User, Page


@app.after_request
def add_header(request):
    request.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    request.headers['Pragma'] = 'no-cache'
    request.headers['Expires'] = '0'
    request.headers['Cache-Control'] = 'public, max-age=0'
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
        pages = Page.query.filter_by(author_id=user_id).all()
        return render_template('dashboard.html', user=user, pages=pages)
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
            # Update user's settings with new values
            user.display_name = request.form['display_name']
            user.email = request.form['email']
            user.bio = request.form.get('bio', '')
            db.session.commit()
            return redirect(url_for('dashboard'))
        else:
            return render_template('settings.html', user=user)
    else:
        return redirect(url_for('login'))


@app.route('/pages')
def pages():
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        all_pages = Page.query.filter_by(author_id=user_id).all()
        return render_template('pages.html', user=user, pages=all_pages)
    else:
        return redirect(url_for('login'))


@app.route('/pages/new', methods=['GET', 'POST'])
def new_page():
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if request.method == 'POST':
            title = request.form['title']
            content = request.form['content']
            template_enabled = request.form.get('template_enabled', 'off') == 'on'
            
            new_page = Page(
                title=title,
                content=content,
                template_enabled=template_enabled,
                author_id=user_id
            )
            db.session.add(new_page)
            db.session.commit()
            return redirect(url_for('pages'))
        return render_template('new_page.html', user=user)
    else:
        return redirect(url_for('login'))


@app.route('/pages/<int:page_id>')
def view_page(page_id):
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        page = Page.query.get_or_404(page_id)
        user = User.query.get(user_id)
        
        # If template processing is enabled, render content as template
        if page.template_enabled:
            try:
                rendered_content = render_template_string(page.content)
            except Exception as e:
                rendered_content = f"Template Error: {str(e)}"
        else:
            rendered_content = page.content
            
        return render_template('view_page.html', user=user, page=page, rendered_content=rendered_content)
    else:
        return redirect(url_for('login'))


@app.route('/pages/<int:page_id>/edit', methods=['GET', 'POST'])
def edit_page(page_id):
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        page = Page.query.get_or_404(page_id)
        user = User.query.get(user_id)
        
        if request.method == 'POST':
            page.title = request.form['title']
            page.content = request.form['content']
            page.template_enabled = request.form.get('template_enabled', 'off') == 'on'
            db.session.commit()
            return redirect(url_for('view_page', page_id=page_id))
        return render_template('edit_page.html', user=user, page=page)
    else:
        return redirect(url_for('login'))


# Preview endpoint - renders content with template processing
@app.route('/api/preview', methods=['POST'])
def preview_content():
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        content = request.form.get('content', '')
        template_enabled = request.form.get('template_enabled', 'false') == 'true'
        
        if template_enabled:
            try:
                # VULNERABLE: Direct template rendering of user content
                # Similar to Grav CVE - map/reduce filters can call arbitrary functions
                rendered = render_template_string(content)
                return jsonify({'success': True, 'rendered': rendered})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)})
        else:
            return jsonify({'success': True, 'rendered': content})
    else:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401


# Media library endpoint (noise endpoint)
@app.route('/media')
def media():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        return render_template('media.html', user=user)
    else:
        return redirect(url_for('login'))


# Themes endpoint (noise endpoint)
@app.route('/themes')
def themes():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        return render_template('themes.html', user=user)
    else:
        return redirect(url_for('login'))


# API endpoint to list pages (noise endpoint)
@app.route('/api/pages')
def api_pages():
    user_id = session.get('user_id')
    if user_id:
        pages = Page.query.filter_by(author_id=user_id).all()
        return jsonify({'pages': [{'id': p.id, 'title': p.title} for p in pages]})
    else:
        return jsonify({'error': 'Unauthorized'}), 401


# System info endpoint (noise endpoint with slight hint)
@app.route('/api/system')
def api_system():
    user_id = session.get('user_id')
    if user_id:
        return jsonify({
            'version': '2.1.4',
            'template_engine': 'Jinja2',
            'python_version': '3.9',
            'features': ['pages', 'media', 'themes', 'template_processing']
        })
    else:
        return jsonify({'error': 'Unauthorized'}), 401


# Robots.txt with hint about backup
@app.route('/robots.txt')
def robots():
    return Response("""User-agent: *
Disallow: /admin/
Disallow: /api/
Disallow: /backup/
Disallow: /.old/
""", mimetype='text/plain')


# Old backup config file (discoverable via robots.txt)
@app.route('/backup/config.old')
def backup_config():
    return Response("""# PageFlow CMS Configuration Backup
# Created: 2024-01-15
# WARNING: This file contains sensitive information

[database]
host = localhost
name = database
user = root

[auth]
# Default demo account for testing
# demo_user = editor
# demo_pass = editor123

[template]
engine = jinja2
allow_unsafe = true
""", mimetype='text/plain')
