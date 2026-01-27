from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response, Markup

from app import app
from app.db import db
from app.models import User, WikiPage

import hashlib
import os


@app.after_request
def add_header(request):
    request.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    request.headers['Pragma'] = 'no-cache'
    request.headers['Expires'] = '0'
    request.headers['Cache-Control'] = 'public, max-age=0'
    return request


class SessionError(Exception):
    def __init__(self, message='Session verification failed.'):
        self.message = message
        super().__init__(self.message)


def verify_session():
    user = User.query.filter_by(username=session.get('username')).first()
    if user:
        user_password_hashed = hashlib.pbkdf2_hmac('sha256', user.password.encode(), app.secret_key.encode(), 100000).hex()
        if session.get('password_hash') == user_password_hashed:
            session['user_id'] = user.id
            return user
        else:
            raise SessionError(message='Wrong password.')
    else:
        raise SessionError(message='Invalid username.')


def get_current_user():
    """Get current logged in user or None"""
    try:
        return verify_session()
    except SessionError:
        return None


@app.route('/')
def index():
    return redirect(url_for('home'))


@app.route('/home')
def home():
    """Wiki homepage showing recent pages"""
    pages = WikiPage.query.order_by(WikiPage.created_at.desc()).limit(10).all()
    user = get_current_user()
    return render_template('home.html', pages=pages, user=user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        session['username'] = username
        session['password_hash'] = hashlib.pbkdf2_hmac('sha256', password.encode(), app.secret_key.encode(), 100000).hex()

        try:
            verify_session()
            return redirect(url_for('home'))
        except SessionError as e:
            return render_template('login.html', error=e.message)


@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('password_hash', None)
    session.pop('user_id', None)
    return redirect(url_for('home'))


@app.route('/page/<slug>')
def view_page(slug):
    """View a wiki page - renders attachments unsanitized (VULNERABLE)"""
    page = WikiPage.query.filter_by(slug=slug).first()
    if not page:
        return render_template('page_not_found.html', slug=slug), 404
    
    user = get_current_user()
    
    # Process the page content - this is where the vulnerability exists
    # Similar to YesWiki's {{attach}} component, we process attachment macros
    # The file parameter is NOT sanitized before being rendered
    content = process_wiki_content(page.content)
    
    return render_template('view_page.html', page=page, content=content, user=user)


def process_wiki_content(content):
    """
    Process wiki macros in content.
    VULNERABLE: The 'file' parameter in {{attach}} is processed through 
    render_template_string, allowing Server-Side Template Injection (SSTI).
    This mirrors CVE-2025-24018 in YesWiki where user input was echoed 
    unsanitized into HTML output.
    """
    import re
    
    # Find all {{attach file="..."}} macros
    attach_pattern = r'\{\{attach\s+file="([^"]*)"\s*\}\}'
    
    def replace_attach(match):
        filename = match.group(1)
        # Check if attachment exists (it won't, so we show upload prompt)
        # VULNERABILITY: filename is passed to render_template_string without sanitization
        # This allows Server-Side Template Injection (SSTI)
        # Attacker can inject Jinja2 template code like: {{config}} or {{''.__class__.__mro__[1].__subclasses__()}}
        template = f'''<div class="attachment-missing">
            <a href="/upload?file={filename}" class="btn btn-primary">
                <i class="fa fa-upload"></i> Upload File: {filename}
            </a>
        </div>'''
        try:
            return render_template_string(template)
        except Exception as e:
            return f'<div class="error">Error processing attachment: {str(e)}</div>'
    
    processed = re.sub(attach_pattern, replace_attach, content)
    return Markup(processed)


@app.route('/page/create', methods=['GET', 'POST'])
def create_page():
    """Create a new wiki page - requires authentication"""
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    
    if request.method == 'GET':
        return render_template('create_page.html', user=user)
    
    elif request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        
        if not title:
            return render_template('create_page.html', user=user, error='Title is required')
        
        # Generate slug from title
        slug = title.lower().replace(' ', '-')
        slug = ''.join(c for c in slug if c.isalnum() or c == '-')
        
        # Check if slug already exists
        existing = WikiPage.query.filter_by(slug=slug).first()
        if existing:
            return render_template('create_page.html', user=user, error='A page with this title already exists')
        
        # Create new page
        new_page = WikiPage(
            title=title,
            slug=slug,
            content=content,
            author_id=user.id
        )
        db.session.add(new_page)
        db.session.commit()
        
        return redirect(url_for('view_page', slug=slug))


@app.route('/page/<slug>/edit', methods=['GET', 'POST'])
def edit_page(slug):
    """Edit an existing wiki page - requires authentication"""
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    
    page = WikiPage.query.filter_by(slug=slug).first()
    if not page:
        return render_template('page_not_found.html', slug=slug), 404
    
    if request.method == 'GET':
        return render_template('edit_page.html', page=page, user=user)
    
    elif request.method == 'POST':
        content = request.form.get('content', '').strip()
        page.content = content
        db.session.commit()
        
        return redirect(url_for('view_page', slug=slug))


@app.route('/admin')
def admin_panel():
    """Admin panel - shows flag for admin users only"""
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    
    if not user.is_admin:
        return render_template('access_denied.html', user=user), 403
    
    # Read the flag
    try:
        with open('/flag') as f:
            flag = f.read()
    except:
        flag = 'FLAG{placeholder}'
    
    return render_template('admin_panel.html', user=user, flag=flag)


@app.route('/api/config')
def api_config():
    """API endpoint that returns wiki configuration including secret data for admins"""
    user = get_current_user()
    
    config = {
        'wiki_name': 'OpenWiki',
        'version': '4.4.5',
        'features': ['attachments', 'comments', 'revisions'],
        'public': True
    }
    
    # If admin, include sensitive config
    if user and user.is_admin:
        try:
            with open('/flag') as f:
                flag = f.read()
        except:
            flag = 'FLAG{placeholder}'
        config['admin_secret'] = flag
    
    return config


@app.route('/upload')
def upload():
    """Upload page (placeholder)"""
    user = get_current_user()
    filename = request.args.get('file', '')
    return render_template('upload.html', user=user, filename=filename)
