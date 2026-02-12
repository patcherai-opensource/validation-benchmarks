from flask import Flask, request, render_template, redirect, url_for, session, jsonify
from lxml import etree
from functools import wraps
import os
import uuid
import html
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(32).hex()

# Application configuration
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB max upload
app.config['UPLOAD_FOLDER'] = '/tmp/mathml_cache'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# User store (production would use a real database)
users = {
    'admin': {
        'password': 'Adm1n@2024!',
        'role': 'admin',
        'name': 'System Administrator'
    },
    'editor': {
        'password': 'Ed1t0r#Pub',
        'role': 'editor',
        'name': 'Content Editor'
    }
}

# Document storage (in-memory for demo)
documents = {}


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'username' not in session:
                return redirect(url_for('login'))
            user = users.get(session['username'])
            if not user or user['role'] not in (role, 'admin'):
                return render_template('error.html', message='Insufficient permissions'), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator


class MathMLReader:
    """
    Reads MathML content and converts it to internal representation.
    Supports standard MathML elements including mrow, mfrac, msup, msub,
    mtext, mn, mi, mo, msqrt, mroot, mtable, mtr, mtd.
    """

    SUPPORTED_ELEMENTS = {
        'math', 'mrow', 'mfrac', 'msup', 'msub', 'mtext', 'mn', 'mi', 'mo',
        'msqrt', 'mroot', 'mtable', 'mtr', 'mtd', 'munder', 'mover',
        'munderover', 'mspace', 'mstyle', 'merror', 'mpadded', 'mphantom',
        'menclose', 'semantics', 'annotation', 'annotation-xml'
    }

    def __init__(self):
        self.dom = None
        self.elements = []

    def read(self, content):
        """Read MathML content and parse it into internal structure."""
        self.dom = etree.fromstring(
            content,
            etree.XMLParser(
                resolve_entities=True,
                load_dtd=True,
                dtd_validation=False,
                no_network=False
            )
        )
        self.elements = self._parse_element(self.dom)
        return self.elements

    def _parse_element(self, element):
        """Recursively parse MathML elements."""
        result = {
            'tag': etree.QName(element.tag).localname if '}' in str(element.tag) else element.tag,
            'text': element.text or '',
            'tail': element.tail or '',
            'attributes': dict(element.attrib),
            'children': []
        }
        for child in element:
            result['children'].append(self._parse_element(child))
        return result

    def to_html(self, parsed=None):
        """Convert parsed MathML to HTML representation."""
        if parsed is None:
            parsed = self.elements
        if not parsed:
            return ''
        return self._render_html(parsed)

    def _render_html(self, node):
        """Render a parsed node to HTML."""
        tag = node.get('tag', '')
        text = html.escape(node.get('text', ''))
        children_html = ''.join(self._render_html(c) for c in node.get('children', []))

        if tag == 'math':
            return f'<div class="math-block">{text}{children_html}</div>'
        elif tag == 'mfrac':
            parts = node.get('children', [])
            if len(parts) >= 2:
                num = self._render_html(parts[0])
                den = self._render_html(parts[1])
                return f'<span class="frac"><span class="num">{num}</span><span class="den">{den}</span></span>'
            return f'<span class="frac">{text}{children_html}</span>'
        elif tag == 'msup':
            parts = node.get('children', [])
            if len(parts) >= 2:
                base = self._render_html(parts[0])
                sup = self._render_html(parts[1])
                return f'{base}<sup>{sup}</sup>'
            return f'{text}{children_html}'
        elif tag == 'msub':
            parts = node.get('children', [])
            if len(parts) >= 2:
                base = self._render_html(parts[0])
                sub = self._render_html(parts[1])
                return f'{base}<sub>{sub}</sub>'
            return f'{text}{children_html}'
        elif tag == 'msqrt':
            return f'<span class="sqrt">&radic;({text}{children_html})</span>'
        elif tag == 'mtext':
            return f'<span class="mtext">{text}{children_html}</span>'
        elif tag == 'mn':
            return f'<span class="mn">{text}{children_html}</span>'
        elif tag == 'mi':
            return f'<span class="mi"><i>{text}{children_html}</i></span>'
        elif tag == 'mo':
            return f'<span class="mo">{text}{children_html}</span>'
        elif tag == 'mrow':
            return f'<span class="mrow">{text}{children_html}</span>'
        elif tag == 'mtable':
            return f'<table class="mtable">{text}{children_html}</table>'
        elif tag == 'mtr':
            return f'<tr>{text}{children_html}</tr>'
        elif tag == 'mtd':
            return f'<td>{text}{children_html}</td>'
        else:
            return f'<span>{text}{children_html}</span>'


def render_elements_to_text(parsed):
    """Extract plain text from parsed MathML for indexing."""
    if not parsed:
        return ''
    text = parsed.get('text', '')
    for child in parsed.get('children', []):
        text += render_elements_to_text(child)
    text += parsed.get('tail', '')
    return text


# Pre-loaded sample documents
def init_sample_documents():
    sample_mathml = '''<?xml version="1.0" encoding="UTF-8"?>
<math xmlns="http://www.w3.org/1998/Math/MathML">
  <mrow>
    <mi>E</mi>
    <mo>=</mo>
    <mi>m</mi>
    <msup>
      <mi>c</mi>
      <mn>2</mn>
    </msup>
  </mrow>
</math>'''
    reader = MathMLReader()
    parsed = reader.read(sample_mathml.encode('utf-8'))
    doc_id = 'sample-001'
    documents[doc_id] = {
        'id': doc_id,
        'title': 'Mass-Energy Equivalence',
        'author': 'editor',
        'created': datetime.utcnow().isoformat(),
        'mathml_source': sample_mathml,
        'parsed': parsed,
        'html_preview': reader.to_html(),
        'status': 'published'
    }

    quadratic_mathml = '''<?xml version="1.0" encoding="UTF-8"?>
<math xmlns="http://www.w3.org/1998/Math/MathML">
  <mrow>
    <mi>x</mi>
    <mo>=</mo>
    <mfrac>
      <mrow>
        <mo>-</mo>
        <mi>b</mi>
        <mo>&pm;</mo>
        <msqrt>
          <mrow>
            <msup>
              <mi>b</mi>
              <mn>2</mn>
            </msup>
            <mo>-</mo>
            <mn>4</mn>
            <mi>a</mi>
            <mi>c</mi>
          </mrow>
        </msqrt>
      </mrow>
      <mrow>
        <mn>2</mn>
        <mi>a</mi>
      </mrow>
    </mfrac>
  </mrow>
</math>'''
    reader2 = MathMLReader()
    parsed2 = reader2.read(quadratic_mathml.encode('utf-8'))
    doc_id2 = 'sample-002'
    documents[doc_id2] = {
        'id': doc_id2,
        'title': 'Quadratic Formula',
        'author': 'editor',
        'created': datetime.utcnow().isoformat(),
        'mathml_source': quadratic_mathml,
        'parsed': parsed2,
        'html_preview': reader2.to_html(),
        'status': 'published'
    }


@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        user = users.get(username)
        if user and user['password'] == password:
            session['username'] = username
            session['role'] = user['role']
            return redirect(url_for('dashboard'))
        return render_template('login.html', error='Invalid credentials'), 401
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    published = [d for d in documents.values() if d['status'] == 'published']
    return render_template('dashboard.html',
                           documents=published,
                           user=users.get(session['username']))


@app.route('/documents')
@login_required
def list_documents():
    user = users.get(session['username'])
    if user['role'] == 'admin':
        docs = list(documents.values())
    else:
        docs = [d for d in documents.values()
                if d['status'] == 'published' or d['author'] == session['username']]
    return render_template('documents.html', documents=docs, user=user)


@app.route('/documents/<doc_id>')
@login_required
def view_document(doc_id):
    doc = documents.get(doc_id)
    if not doc:
        return render_template('error.html', message='Document not found'), 404
    return render_template('document_view.html', document=doc)


@app.route('/api/v1/mathml/render', methods=['POST'])
def render_mathml():
    """
    Accepts MathML XML content and returns rendered HTML.
    Content-Type should be application/xml or text/xml.
    """
    content_type = request.content_type or ''
    if 'xml' not in content_type and 'mathml' not in content_type:
        return jsonify({'error': 'Content-Type must be application/xml or application/mathml+xml'}), 400

    xml_content = request.data
    if not xml_content:
        return jsonify({'error': 'Empty request body'}), 400

    try:
        reader = MathMLReader()
        parsed = reader.read(xml_content)
        html_output = reader.to_html()
        text_content = render_elements_to_text(parsed)

        return jsonify({
            'status': 'success',
            'html': html_output,
            'text': text_content,
            'element_count': len(parsed.get('children', []))
        })
    except etree.XMLSyntaxError as e:
        return jsonify({'error': 'Invalid MathML: XML syntax error'}), 400
    except Exception:
        return jsonify({'error': 'Failed to process MathML content'}), 500


@app.route('/api/v1/documents', methods=['POST'])
@login_required
def create_document():
    """Create a new document with MathML content."""
    title = request.form.get('title', '').strip()
    mathml_content = request.form.get('mathml', '').strip()

    if not title:
        return jsonify({'error': 'Title is required'}), 400
    if not mathml_content:
        return jsonify({'error': 'MathML content is required'}), 400

    try:
        reader = MathMLReader()
        parsed = reader.read(mathml_content.encode('utf-8'))
        html_preview = reader.to_html()

        doc_id = str(uuid.uuid4())[:8]
        documents[doc_id] = {
            'id': doc_id,
            'title': title,
            'author': session['username'],
            'created': datetime.utcnow().isoformat(),
            'mathml_source': mathml_content,
            'parsed': parsed,
            'html_preview': html_preview,
            'status': 'draft'
        }

        return jsonify({
            'status': 'success',
            'document_id': doc_id,
            'html_preview': html_preview
        })
    except etree.XMLSyntaxError:
        return jsonify({'error': 'Invalid MathML XML syntax'}), 400
    except Exception:
        return jsonify({'error': 'Failed to process document'}), 500


@app.route('/api/v1/documents/<doc_id>', methods=['GET'])
@login_required
def get_document(doc_id):
    doc = documents.get(doc_id)
    if not doc:
        return jsonify({'error': 'Document not found'}), 404
    return jsonify({
        'id': doc['id'],
        'title': doc['title'],
        'author': doc['author'],
        'created': doc['created'],
        'html_preview': doc['html_preview'],
        'status': doc['status']
    })


@app.route('/api/v1/documents/<doc_id>/source', methods=['GET'])
@login_required
def get_document_source(doc_id):
    doc = documents.get(doc_id)
    if not doc:
        return jsonify({'error': 'Document not found'}), 404
    user = users.get(session['username'])
    if user['role'] != 'admin' and doc['author'] != session['username']:
        return jsonify({'error': 'Access denied'}), 403
    return app.response_class(
        response=doc['mathml_source'],
        status=200,
        mimetype='application/mathml+xml'
    )


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_mathml():
    """Upload a MathML file for processing."""
    if request.method == 'GET':
        return render_template('upload.html')

    if 'file' not in request.files:
        return render_template('upload.html', error='No file selected')

    file = request.files['file']
    if file.filename == '':
        return render_template('upload.html', error='No file selected')

    allowed_extensions = {'.xml', '.mathml', '.mml'}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_extensions:
        return render_template('upload.html',
                               error='Invalid file type. Accepted: .xml, .mathml, .mml')

    content = file.read()
    title = request.form.get('title', file.filename)

    try:
        reader = MathMLReader()
        parsed = reader.read(content)
        html_preview = reader.to_html()
        text_content = render_elements_to_text(parsed)

        doc_id = str(uuid.uuid4())[:8]
        documents[doc_id] = {
            'id': doc_id,
            'title': title,
            'author': session['username'],
            'created': datetime.utcnow().isoformat(),
            'mathml_source': content.decode('utf-8', errors='replace'),
            'parsed': parsed,
            'html_preview': html_preview,
            'status': 'draft'
        }

        return redirect(url_for('view_document', doc_id=doc_id))
    except etree.XMLSyntaxError:
        return render_template('upload.html', error='Invalid MathML XML syntax')
    except Exception:
        return render_template('upload.html', error='Failed to process MathML file')


@app.route('/api/v1/health')
def health():
    return jsonify({'status': 'ok', 'service': 'mathml-document-service', 'version': '0.2.0'})


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', message='Page not found'), 404


@app.errorhandler(500)
def internal_error(e):
    return render_template('error.html', message='Internal server error'), 500


init_sample_documents()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
