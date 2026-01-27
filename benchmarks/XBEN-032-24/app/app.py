from flask import Flask, request, render_template, redirect, url_for, session, jsonify
from lxml import etree
from functools import wraps
import os
import uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'ez_platform_secret_2024'

# User accounts with different roles - editor role can publish content
users = {
    'editor': {'password': 'Edit0r2024!', 'role': 'editor', 'name': 'Content Editor'},
    'admin': {'password': 'Admin2024!', 'role': 'administrator', 'name': 'Administrator'}
}

# Load flag - first try environment variable, then file
FLAG = os.environ.get('FLAG')
if FLAG:
    # If FLAG environment variable is set, write it to flag.txt for runtime injection
    with open('flag.txt', 'w') as file:
        file.write(FLAG)
else:
    # Fall back to reading from file
    with open('flag.txt', 'r') as file:
        FLAG = file.read()

# Simulated content storage
content_items = {
    '1': {
        'id': '1',
        'title': 'Welcome to eZ Platform',
        'content': '<section><paragraph>Welcome to our content management system.</paragraph></section>',
        'author': 'admin',
        'status': 'published',
        'created': '2024-01-15T10:30:00',
        'modified': '2024-01-15T10:30:00'
    },
    '2': {
        'id': '2',
        'title': 'Getting Started Guide',
        'content': '<section><paragraph>Learn how to use RichText fields effectively.</paragraph></section>',
        'author': 'editor',
        'status': 'draft',
        'created': '2024-01-16T14:22:00',
        'modified': '2024-01-16T14:22:00'
    }
}

class ContentService:
    """RichText content processing service"""
    
    @staticmethod
    def process_richtext(xml_content):
        """Process RichText XML content - WARNING: Entity expansion enabled"""
        return xml_content
    
    @staticmethod
    def get_content_item(content_id):
        return content_items.get(content_id)
    
    @staticmethod
    def list_content():
        return list(content_items.values())

# RichText XML Schema for content validation (informational)
RICHTEXT_SCHEMA_INFO = """
eZ Platform RichText XML Schema
================================
RichText fields accept DocBook-based XML format.
Example structure:
<section xmlns="http://docbook.org/ns/docbook">
    <title>Article Title</title>
    <paragraph>Content paragraph with <emphasis>formatted</emphasis> text.</paragraph>
</section>

API Endpoint: POST /api/ezp/v2/content/objects/{contentId}/versions/{versionNo}/richtext
Content-Type: application/xml
"""

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('content_dashboard'))
    return render_template('login.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin panel login - redirects to main login"""
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        if username in users and users[username]['password'] == password:
            session['username'] = username
            session['role'] = users[username]['role']
            session['display_name'] = users[username]['name']
            return redirect(url_for('content_dashboard'))
        else:
            error = 'Invalid username or password. Please check your credentials.'
    return render_template('login.html', error=error)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def editor_required(f):
    """Require editor role or higher"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        if session.get('role') not in ['editor', 'administrator']:
            return jsonify({'error': 'Insufficient permissions. Editor role required.'}), 403
        return f(*args, **kwargs)
    return decorated_function

@app.route('/dashboard')
@login_required
def content_dashboard():
    """Content management dashboard"""
    items = ContentService.list_content()
    return render_template('dashboard.html', content_items=items)

@app.route('/api/ezp/v2/content/objects')
@login_required
def api_list_content():
    """REST API: List all content objects"""
    items = ContentService.list_content()
    return jsonify({
        'ContentList': {
            '_media-type': 'application/vnd.ez.api.ContentList+json',
            'Content': items
        }
    })

@app.route('/api/ezp/v2/content/objects/<content_id>')
@login_required
def api_get_content(content_id):
    """REST API: Get single content object"""
    item = ContentService.get_content_item(content_id)
    if not item:
        return jsonify({'error': 'Content not found'}), 404
    return jsonify({
        'Content': {
            '_media-type': 'application/vnd.ez.api.Content+json',
            **item
        }
    })

@app.route('/api/ezp/v2/content/objects/<content_id>/versions/<version_no>/richtext', methods=['POST', 'PUT'])
@editor_required
def process_richtext(content_id, version_no):
    """
    Process RichText field content for a content object version.
    
    Accepts XML in DocBook-based format. The XML is parsed and processed
    to validate and transform the content before storage.
    
    Content-Type: application/xml or application/vnd.ez.api.RichText+xml
    """
    xml_data = request.data
    
    if not xml_data:
        return jsonify({'error': 'No XML content provided'}), 400
    
    try:
        # Parse the RichText XML content
        # Using DOMDocumentFactory-style parsing with entity expansion
        parser = etree.XMLParser(resolve_entities=True)
        root = etree.fromstring(xml_data, parser)
        
        # Process the content
        service = ContentService()
        
        # Extract text content from the parsed XML
        content_text = etree.tostring(root, encoding='unicode', method='text')
        xml_output = etree.tostring(root, encoding='unicode', pretty_print=True)
        
        # Generate response
        response_data = {
            'RichTextProcessingResult': {
                '_media-type': 'application/vnd.ez.api.RichTextProcessingResult+xml',
                'contentId': content_id,
                'versionNo': version_no,
                'status': 'processed',
                'processedXml': xml_output,
                'extractedText': content_text,
                'timestamp': datetime.now().isoformat()
            }
        }
        
        # Return XML response
        response_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<RichTextProcessingResult>
    <contentId>{content_id}</contentId>
    <versionNo>{version_no}</versionNo>
    <status>processed</status>
    <processedContent>{xml_output}</processedContent>
    <extractedText>{content_text}</extractedText>
    <timestamp>{datetime.now().isoformat()}</timestamp>
</RichTextProcessingResult>"""
        
        return app.response_class(response=response_xml, status=200, mimetype='application/xml')
        
    except etree.XMLSyntaxError as e:
        error_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<ErrorMessage>
    <errorCode>400</errorCode>
    <errorType>XMLSyntaxError</errorType>
    <errorMessage>Invalid XML syntax in RichText field: {str(e)}</errorMessage>
    <errorDescription>The provided XML content could not be parsed. Please ensure valid XML format.</errorDescription>
</ErrorMessage>"""
        return app.response_class(response=error_response, status=400, mimetype='application/xml')
    except Exception as e:
        error_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<ErrorMessage>
    <errorCode>500</errorCode>
    <errorType>ProcessingError</errorType>
    <errorMessage>Error processing RichText content: {str(e)}</errorMessage>
</ErrorMessage>"""
        return app.response_class(response=error_response, status=500, mimetype='application/xml')

@app.route('/api/ezp/v2/content/schema/richtext')
def richtext_schema():
    """Return RichText schema information"""
    return app.response_class(response=RICHTEXT_SCHEMA_INFO, status=200, mimetype='text/plain')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    session.pop('display_name', None)
    return redirect(url_for('login'))

@app.route('/api/ezp/v2/user/current')
@login_required
def current_user():
    """Get current user info"""
    return jsonify({
        'User': {
            '_media-type': 'application/vnd.ez.api.User+json',
            'login': session.get('username'),
            'name': session.get('display_name'),
            'role': session.get('role')
        }
    })

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Resource not found', 'code': 404}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error', 'code': 500}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
