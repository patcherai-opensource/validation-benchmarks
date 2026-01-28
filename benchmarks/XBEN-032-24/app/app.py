from flask import Flask, request, render_template, redirect, url_for, session, jsonify, make_response
from lxml import etree
from functools import wraps
import os
import json
import hashlib
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'ez_platform_secret_2024_richtext'

# User database - CMS user roles
# Default editor account for content management
users = {
    'admin': {'password': 'Ezp!@tform2024', 'role': 'administrator'},
    'editor': {'password': 'R1chT3xt_Ed1t0r', 'role': 'editor'},
    'reviewer': {'password': 'read0nly_user', 'role': 'reviewer'}
}

# Load flag from file (written at build time)
with open('flag.txt', 'r') as file:
    FLAG = file.read()

# Sample content database
content_items = {
    '1': {
        'id': '1',
        'title': 'Welcome to eZ Platform',
        'content': '<section><para>Welcome to our content management system.</para></section>',
        'author': 'admin',
        'status': 'published',
        'created': '2024-01-15T10:30:00'
    },
    '2': {
        'id': '2',
        'title': 'Getting Started Guide',
        'content': '<section><para>This guide helps you get started with content editing.</para></section>',
        'author': 'editor',
        'status': 'draft',
        'created': '2024-02-20T14:45:00'
    },
    '3': {
        'id': '3',
        'title': 'API Documentation',
        'content': '<section><para>REST API endpoints for content management.</para></section>',
        'author': 'admin',
        'status': 'published',
        'created': '2024-03-01T09:00:00'
    }
}

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        if username in users and users[username]['password'] == password:
            session['username'] = username
            session['role'] = users[username]['role']
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def editor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        if session.get('role') not in ['editor', 'administrator']:
            return jsonify({'error': 'Editor privileges required'}), 403
        return f(*args, **kwargs)
    return decorated_function

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', content_items=content_items)

@app.route('/content')
@login_required
def content_list():
    """List all content items"""
    return render_template('content_list.html', content_items=content_items)

@app.route('/content/<content_id>')
@login_required
def view_content(content_id):
    """View a single content item"""
    if content_id in content_items:
        return render_template('content_view.html', item=content_items[content_id])
    return 'Content not found', 404

@app.route('/api/content', methods=['GET'])
@login_required
def api_content_list():
    """API: List all content"""
    return jsonify({'items': list(content_items.values())})

@app.route('/api/content/<content_id>', methods=['GET'])
@login_required
def api_get_content(content_id):
    """API: Get single content item"""
    if content_id in content_items:
        return jsonify(content_items[content_id])
    return jsonify({'error': 'Not found'}), 404

@app.route('/api/content/<content_id>/richtext', methods=['POST'])
@editor_required
def api_update_richtext(content_id):
    """
    API: Update RichText field for a content item
    Accepts XML body for RichText content
    """
    if content_id not in content_items:
        return jsonify({'error': 'Content not found'}), 404
    
    xml_data = request.data
    content_type = request.content_type or ''
    
    if 'xml' not in content_type.lower():
        return jsonify({'error': 'Content-Type must be application/xml'}), 400
    
    try:
        # Parse the RichText XML content using DOMDocumentFactory pattern
        # LIBXML_NOENT enables entity substitution (vulnerable configuration)
        parser = etree.XMLParser(resolve_entities=True, load_dtd=True, no_network=False)
        root = etree.fromstring(xml_data, parser)
        
        # Extract the text content from the parsed XML
        def extract_text(element):
            texts = []
            if element.text:
                texts.append(element.text)
            for child in element:
                texts.extend(extract_text(child))
                if child.tail:
                    texts.append(child.tail)
            return texts
        
        parsed_content = ' '.join(extract_text(root)).strip()
        
        # Update the content
        content_items[content_id]['content'] = etree.tostring(root, encoding='unicode')
        content_items[content_id]['modified'] = datetime.now().isoformat()
        
        return jsonify({
            'success': True,
            'message': 'RichText content updated',
            'content_id': content_id,
            'parsed_preview': parsed_content[:500]
        })
        
    except etree.XMLSyntaxError as e:
        return jsonify({
            'error': 'XML parsing failed',
            'details': str(e),
            'hint': 'Ensure your XML is well-formed'
        }), 400
    except Exception as e:
        return jsonify({
            'error': 'Processing failed',
            'details': str(e)
        }), 500

@app.route('/api/content/preview', methods=['POST'])
@editor_required
def api_preview_richtext():
    """
    API: Preview RichText content without saving
    Useful for editors to preview XML content rendering
    """
    xml_data = request.data
    
    try:
        parser = etree.XMLParser(resolve_entities=True, load_dtd=True)
        root = etree.fromstring(xml_data, parser)
        
        # Convert to string for preview
        rendered = etree.tostring(root, encoding='unicode', pretty_print=True)
        
        return app.response_class(
            response=rendered,
            status=200,
            mimetype='application/xml'
        )
    except etree.XMLSyntaxError as e:
        return jsonify({
            'error': 'XML syntax error',
            'message': str(e)
        }), 400

@app.route('/editor')
@login_required
def editor():
    """RichText editor interface"""
    if session.get('role') not in ['editor', 'administrator']:
        return render_template('access_denied.html'), 403
    return render_template('editor.html', content_items=content_items)

@app.route('/api/status')
def api_status():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'application': 'eZ Platform RichText',
        'version': '2.3.25'
    })

@app.route('/settings')
@login_required
def settings():
    """User settings page"""
    return render_template('settings.html')

@app.route('/help')
def help_page():
    """Help documentation"""
    return render_template('help.html')

@app.route('/robots.txt')
def robots():
    """Robots.txt - hints at backup location"""
    content = """User-agent: *
Disallow: /api/
Disallow: /admin/
Disallow: /backups/
Disallow: /.git/
"""
    return app.response_class(response=content, mimetype='text/plain')

@app.route('/backups/')
def backups_index():
    """Forbidden backup directory"""
    return 'Forbidden', 403

@app.route('/backups/users.json.bak')
def backups_users():
    """Backup file with user hints"""
    # Obfuscated backup showing usernames but not full passwords
    backup_data = {
        "_comment": "User backup - passwords truncated for security",
        "users": [
            {"username": "admin", "password_hint": "Ezp!@tform****", "role": "administrator"},
            {"username": "editor", "password_hint": "R1chT3xt_*****", "role": "editor"},
            {"username": "reviewer", "password_hint": "read0nly_****", "role": "reviewer"}
        ],
        "backup_date": "2024-01-10"
    }
    return jsonify(backup_data)

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
