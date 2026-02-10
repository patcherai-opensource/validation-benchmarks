from flask import Flask, request, render_template, redirect, url_for, session, jsonify
from functools import wraps
from xml.dom import minidom
import os
import uuid
import html

app = Flask(__name__)
app.secret_key = 'cms_secret_key_92847'

# CMS User data with roles (simulating ezplatform roles)
# editor: Can edit content with RichText fields
# viewer: Can only view content
users = {
    'editor': {'password': 'editor123', 'role': 'editor'},
    'viewer': {'password': 'viewer456', 'role': 'viewer'}
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

# In-memory content storage (simulating CMS content objects)
content_store = {
    '1': {
        'id': '1',
        'title': 'Welcome to Our CMS',
        'richtext': '<section xmlns="http://ez.no/namespaces/ezpublish5/xhtml5"><paragraph>Welcome to the RichText CMS platform. This is sample content.</paragraph></section>',
        'author': 'admin',
        'status': 'published'
    },
    '2': {
        'id': '2',
        'title': 'About Us',
        'richtext': '<section xmlns="http://ez.no/namespaces/ezpublish5/xhtml5"><paragraph>Learn more about our company and services.</paragraph></section>',
        'author': 'admin',
        'status': 'published'
    }
}

# Simulating DOMDocumentFactory from ezplatform-richtext
# Vulnerable: Uses entity expansion without sanitization
class DOMDocumentFactory:
    """
    Factory for creating DOMDocument instances from XML strings.
    Simulates the vulnerable behavior from ezsystems/ezplatform-richtext
    before version 2.3.26.
    """
    
    @staticmethod
    def loadXMLString(xml_string):
        """
        Load XML string into a minidom Document.
        
        VULNERABLE: This uses entity expansion (LIBXML_NOENT equivalent behavior)
        without sanitizing DOCTYPE declarations, allowing XXE attacks.
        """
        # Simulate the vulnerable parsing behavior similar to:
        # DOMDocument::loadXML with LIBXML_NOENT | LIBXML_NONET | LIBXML_PARSEHUGE
        # The Python equivalent uses defusedxml's default behavior or lxml with resolve_entities=True
        
        from lxml import etree
        
        # VULNERABLE: resolve_entities=True allows external entity expansion
        # This mimics the LIBXML_NOENT flag behavior from the PHP vulnerability
        parser = etree.XMLParser(
            resolve_entities=True,  # VULNERABLE: Expands entities
            no_network=True,        # LIBXML_NONET equivalent
            huge_tree=True          # LIBXML_PARSEHUGE equivalent  
        )
        
        try:
            doc = etree.fromstring(xml_string.encode() if isinstance(xml_string, str) else xml_string, parser)
            return doc
        except etree.XMLSyntaxError as e:
            raise ValueError(f"Invalid XML: {str(e)}")


class RichTextInputHandler:
    """
    Handles RichText field input for content objects.
    Simulates the InputHandler from ezplatform-richtext.
    """
    
    def __init__(self):
        self.factory = DOMDocumentFactory()
    
    def process(self, xml_string):
        """
        Process RichText XML input.
        
        VULNERABLE: Passes unsanitized XML to DOMDocumentFactory
        which allows XXE attacks via DOCTYPE entity definitions.
        """
        # No XMLSanitizer applied (this is the vulnerability - missing sanitization)
        # The fix would add: xml_string = XMLSanitizer.sanitize(xml_string)
        
        doc = self.factory.loadXMLString(xml_string)
        
        # Convert back to string for storage
        from lxml import etree
        return etree.tostring(doc, encoding='unicode')


@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username]['password'] == password:
            session['username'] = username
            session['role'] = users[username]['role']
            return redirect(url_for('dashboard'))
        else:
            return 'Invalid credentials', 401
    return render_template('login.html')


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def editor_required(f):
    """Decorator to require editor role (simulating ezplatform permissions)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        if session.get('role') != 'editor':
            return jsonify({'error': 'Editor permission required'}), 403
        return f(*args, **kwargs)
    return decorated_function


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', content_list=content_store.values(), role=session.get('role'))


@app.route('/content/<content_id>')
@login_required
def view_content(content_id):
    content = content_store.get(content_id)
    if not content:
        return 'Content not found', 404
    return render_template('content_view.html', content=content, role=session.get('role'))


@app.route('/content/<content_id>/edit', methods=['GET', 'POST'])
@editor_required
def edit_content(content_id):
    content = content_store.get(content_id)
    if not content:
        return 'Content not found', 404
    
    if request.method == 'POST':
        # Get the RichText XML from the form
        title = request.form.get('title', content['title'])
        richtext_xml = request.form.get('richtext', '')
        
        if richtext_xml:
            try:
                # Process the RichText XML through the vulnerable handler
                handler = RichTextInputHandler()
                processed_xml = handler.process(richtext_xml)
                
                # Update content
                content_store[content_id]['title'] = title
                content_store[content_id]['richtext'] = processed_xml
                
                return render_template('content_edit.html', content=content_store[content_id], 
                                      message='Content updated successfully', processed_xml=processed_xml)
            except Exception as e:
                return render_template('content_edit.html', content=content, 
                                      error=f'Error processing RichText: {str(e)}')
        
    return render_template('content_edit.html', content=content)


@app.route('/content/new', methods=['GET', 'POST'])
@editor_required
def new_content():
    if request.method == 'POST':
        title = request.form.get('title', 'Untitled')
        richtext_xml = request.form.get('richtext', '')
        
        if richtext_xml:
            try:
                # Process the RichText XML through the vulnerable handler
                handler = RichTextInputHandler()
                processed_xml = handler.process(richtext_xml)
                
                # Create new content
                content_id = str(uuid.uuid4())[:8]
                content_store[content_id] = {
                    'id': content_id,
                    'title': title,
                    'richtext': processed_xml,
                    'author': session['username'],
                    'status': 'draft'
                }
                
                return render_template('content_edit.html', content=content_store[content_id],
                                      message='Content created successfully', processed_xml=processed_xml)
            except Exception as e:
                return render_template('content_new.html', error=f'Error processing RichText: {str(e)}')
    
    return render_template('content_new.html')


@app.route('/api/content/<content_id>/richtext', methods=['POST'])
@editor_required
def api_update_richtext(content_id):
    """
    API endpoint for updating RichText fields.
    This simulates the ezplatform API for content editing.
    
    Accepts raw XML in the request body.
    """
    content = content_store.get(content_id)
    if not content:
        return jsonify({'error': 'Content not found'}), 404
    
    # Get XML from request body
    richtext_xml = request.data.decode('utf-8') if request.data else ''
    
    if not richtext_xml:
        return jsonify({'error': 'No RichText XML provided'}), 400
    
    try:
        # Process the RichText XML through the vulnerable handler
        handler = RichTextInputHandler()
        processed_xml = handler.process(richtext_xml)
        
        # Update content
        content_store[content_id]['richtext'] = processed_xml
        
        return jsonify({
            'status': 'success',
            'content_id': content_id,
            'processed_richtext': processed_xml
        })
    except Exception as e:
        return jsonify({'error': f'Error processing RichText: {str(e)}'}), 500


@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
