from flask import Flask, request, render_template, redirect, url_for, session, jsonify, abort
from lxml import etree
from functools import wraps
import os
import uuid
import html
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(32).hex()

users = {
    'editor': {'password': 'editor', 'role': 'editor'},
    'admin': {'password': 'admin123', 'role': 'admin'}
}

content_store = {}


def init_content():
    content_store['page-1'] = {
        'id': 'page-1',
        'title': 'Welcome to RichContent CMS',
        'content': '<section><para>Welcome to our content management platform. This is the default homepage content.</para></section>',
        'author': 'admin',
        'created': datetime.now().isoformat(),
        'modified': datetime.now().isoformat(),
        'status': 'published'
    }
    content_store['page-2'] = {
        'id': 'page-2',
        'title': 'About Us',
        'content': '<section><para>Learn more about our organization and mission.</para></section>',
        'author': 'admin',
        'created': datetime.now().isoformat(),
        'modified': datetime.now().isoformat(),
        'status': 'published'
    }
    content_store['page-3'] = {
        'id': 'page-3',
        'title': 'Contact Information',
        'content': '<section><para>Get in touch with our team.</para><para>Email: contact@example.com</para></section>',
        'author': 'editor',
        'created': datetime.now().isoformat(),
        'modified': datetime.now().isoformat(),
        'status': 'draft'
    }

init_content()


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', code=404, message='Page not found'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', code=500, message='Internal server error'), 500


@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', code=403, message='Access denied'), 403


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
            return redirect(url_for('login'))
        user = users.get(session['username'])
        if not user or user['role'] not in ['editor', 'admin']:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        user = users.get(username)
        if user and user['password'] == password:
            session['username'] = username
            session['role'] = user['role']
            return redirect(url_for('dashboard'))
        else:
            error = 'Invalid username or password'
    return render_template('login.html', error=error)


@app.route('/dashboard')
@login_required
def dashboard():
    pages = list(content_store.values())
    return render_template('dashboard.html', pages=pages)


@app.route('/content')
@login_required
def content_list():
    pages = list(content_store.values())
    return render_template('content_list.html', pages=pages)


@app.route('/content/<page_id>')
@login_required
def view_content(page_id):
    page = content_store.get(page_id)
    if not page:
        abort(404)
    return render_template('view_content.html', page=page)


@app.route('/content/<page_id>/edit', methods=['GET', 'POST'])
@editor_required
def edit_content(page_id):
    page = content_store.get(page_id)
    if not page:
        abort(404)
    
    if request.method == 'POST':
        title = request.form.get('title', '')
        richtext_content = request.form.get('content', '')
        
        result = process_richtext_content(richtext_content)
        
        if result.get('error'):
            return render_template('edit_content.html', page=page, error=result['error'], 
                                 preview=None, title=title, content=richtext_content)
        
        page['title'] = html.escape(title)
        page['content'] = result['processed']
        page['modified'] = datetime.now().isoformat()
        
        return render_template('edit_content.html', page=page, success='Content saved successfully',
                             preview=result['processed'])
    
    return render_template('edit_content.html', page=page)


@app.route('/content/new', methods=['GET', 'POST'])
@editor_required
def new_content():
    if request.method == 'POST':
        title = request.form.get('title', '')
        richtext_content = request.form.get('content', '')
        
        result = process_richtext_content(richtext_content)
        
        if result.get('error'):
            return render_template('new_content.html', error=result['error'],
                                 title=title, content=richtext_content)
        
        page_id = f'page-{uuid.uuid4().hex[:8]}'
        content_store[page_id] = {
            'id': page_id,
            'title': html.escape(title),
            'content': result['processed'],
            'author': session['username'],
            'created': datetime.now().isoformat(),
            'modified': datetime.now().isoformat(),
            'status': 'draft'
        }
        
        return redirect(url_for('edit_content', page_id=page_id))
    
    return render_template('new_content.html')


def process_richtext_content(xml_content):
    if not xml_content or not xml_content.strip():
        return {'error': 'Content cannot be empty'}
    
    try:
        parser = etree.XMLParser(resolve_entities=True)
        doc = etree.fromstring(xml_content.encode('utf-8'), parser)
        
        processed_content = etree.tostring(doc, encoding='unicode', pretty_print=True)
        
        return {'processed': processed_content, 'error': None}
    except etree.XMLSyntaxError:
        return {'error': 'Invalid XML format. Please check your content structure.'}
    except Exception:
        return {'error': 'Error processing content. Please try again.'}


@app.route('/api/content/<page_id>', methods=['PUT'])
@editor_required
def api_update_content(page_id):
    page = content_store.get(page_id)
    if not page:
        return jsonify({'error': 'Content not found'}), 404
    
    content_type = request.content_type or ''
    
    if 'application/xml' in content_type or 'text/xml' in content_type:
        xml_data = request.data.decode('utf-8')
        result = process_richtext_content(xml_data)
        
        if result.get('error'):
            return jsonify({'error': result['error']}), 400
        
        page['content'] = result['processed']
        page['modified'] = datetime.now().isoformat()
        
        return jsonify({'success': True, 'content': result['processed']})
    
    return jsonify({'error': 'Unsupported content type'}), 415


@app.route('/api/content/preview', methods=['POST'])
@editor_required
def api_preview_content():
    content_type = request.content_type or ''
    
    if 'application/xml' in content_type or 'text/xml' in content_type:
        xml_data = request.data.decode('utf-8')
        result = process_richtext_content(xml_data)
        
        if result.get('error'):
            return jsonify({'error': result['error']}), 400
        
        return jsonify({'success': True, 'preview': result['processed']})
    
    return jsonify({'error': 'Unsupported content type'}), 415


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
