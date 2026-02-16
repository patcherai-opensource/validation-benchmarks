from flask import Flask, request, render_template, redirect, url_for, session, jsonify, Response
from lxml import etree
from functools import wraps
import os
import re
import json
import hashlib
import time

app = Flask(__name__)
app.secret_key = hashlib.sha256(b'formula-toolkit-session-key').hexdigest()

# User database (hashed passwords)
_users = {
    'admin': {
        'password_hash': hashlib.sha256(b'admin').hexdigest(),
        'role': 'admin',
        'display_name': 'Administrator'
    },
    'editor': {
        'password_hash': hashlib.sha256(b'editor').hexdigest(),
        'role': 'editor',
        'display_name': 'Content Editor'
    }
}

# Supported MathML element tags for processing
SUPPORTED_TAGS = {
    'math', 'mrow', 'mi', 'mn', 'mo', 'mfrac', 'msup', 'msub',
    'msqrt', 'mroot', 'mtext', 'mspace', 'mtable', 'mtr', 'mtd',
    'mover', 'munder', 'munderover', 'semantics', 'annotation',
    'mpadded', 'mphantom', 'mfenced', 'menclose', 'mstyle',
    'merror', 'maction'
}


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            if request.is_json or (request.content_type and 'xml' in request.content_type):
                return jsonify({'error': 'Authentication required'}), 401
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def _verify_password(username, password):
    user = _users.get(username)
    if not user:
        return False
    return user['password_hash'] == hashlib.sha256(password.encode()).hexdigest()


class FormulaElement:
    """Represents a parsed mathematical element."""
    def __init__(self, tag, value=None, children=None, attributes=None):
        self.tag = tag
        self.value = value
        self.children = children or []
        self.attributes = attributes or {}


class FormulaParser:
    """Parses MathML XML content into a formula tree structure."""

    def __init__(self):
        self.dom = None
        self.elements = []

    def parse(self, content):
        """Parse MathML content string and return structured formula data."""
        if isinstance(content, bytes):
            content = content.replace(b'&InvisibleTimes;', '\u2062'.encode('utf-8'))
            content = content.replace(b'&ApplyFunction;', '\u2061'.encode('utf-8'))
        else:
            content = content.replace('&InvisibleTimes;', '\u2062')
            content = content.replace('&ApplyFunction;', '\u2061')
            content = content.encode('utf-8')

        self.dom = etree.XMLParser(resolve_entities=True, load_dtd=True)
        root = etree.fromstring(content, self.dom)

        return self._process_node(root)

    def _process_node(self, node):
        """Recursively process a DOM node into a FormulaElement."""
        tag = etree.QName(node.tag).localname if '}' in str(node.tag) else str(node.tag)
        text = (node.text or '').strip()
        attrs = dict(node.attrib)
        children = []

        for child in node:
            children.append(self._process_node(child))

        return FormulaElement(
            tag=tag,
            value=text if text else None,
            children=children,
            attributes=attrs
        )


class FormulaRenderer:
    """Renders a parsed formula tree back to presentation formats."""

    @staticmethod
    def to_display(element, depth=0):
        """Convert formula tree to a plain-text display representation."""
        result = []
        indent = '  ' * depth
        tag = element.tag

        if tag in ('mi', 'mn', 'mo', 'mtext'):
            val = element.value or ''
            for child in element.children:
                val += FormulaRenderer._extract_text(child)
            result.append(f'{indent}<{tag}>{val}</{tag}>')
        elif tag == 'mfrac':
            result.append(f'{indent}<mfrac>')
            for child in element.children:
                result.append(FormulaRenderer.to_display(child, depth + 1))
            result.append(f'{indent}</mfrac>')
        elif tag == 'msup':
            result.append(f'{indent}<msup>')
            for child in element.children:
                result.append(FormulaRenderer.to_display(child, depth + 1))
            result.append(f'{indent}</msup>')
        elif tag == 'msub':
            result.append(f'{indent}<msub>')
            for child in element.children:
                result.append(FormulaRenderer.to_display(child, depth + 1))
            result.append(f'{indent}</msub>')
        elif tag == 'mrow':
            result.append(f'{indent}<mrow>')
            for child in element.children:
                result.append(FormulaRenderer.to_display(child, depth + 1))
            result.append(f'{indent}</mrow>')
        elif tag == 'msqrt':
            result.append(f'{indent}<msqrt>')
            for child in element.children:
                result.append(FormulaRenderer.to_display(child, depth + 1))
            result.append(f'{indent}</msqrt>')
        elif tag == 'semantics':
            result.append(f'{indent}<semantics>')
            for child in element.children:
                result.append(FormulaRenderer.to_display(child, depth + 1))
            result.append(f'{indent}</semantics>')
        elif tag == 'annotation':
            val = element.value or ''
            attrs_str = ' '.join(f'{k}="{v}"' for k, v in element.attributes.items())
            if attrs_str:
                result.append(f'{indent}<annotation {attrs_str}>{val}</annotation>')
            else:
                result.append(f'{indent}<annotation>{val}</annotation>')
        elif tag == 'math':
            attrs_str = ''
            for k, v in element.attributes.items():
                if not k.startswith('{'):
                    attrs_str += f' {k}="{v}"'
            result.append(f'{indent}<math{attrs_str}>')
            for child in element.children:
                result.append(FormulaRenderer.to_display(child, depth + 1))
            result.append(f'{indent}</math>')
        else:
            result.append(f'{indent}<{tag}>')
            if element.value:
                result.append(f'{indent}  {element.value}')
            for child in element.children:
                result.append(FormulaRenderer.to_display(child, depth + 1))
            result.append(f'{indent}</{tag}>')

        return '\n'.join(result)

    @staticmethod
    def _extract_text(element):
        """Recursively extract text content from element tree."""
        text = element.value or ''
        for child in element.children:
            text += FormulaRenderer._extract_text(child)
        return text

    @staticmethod
    def to_latex(element):
        """Convert formula tree to LaTeX representation."""
        tag = element.tag

        if tag == 'mn':
            return element.value or FormulaRenderer._extract_text(element) or '0'
        elif tag == 'mi':
            return element.value or FormulaRenderer._extract_text(element) or 'x'
        elif tag == 'mo':
            val = element.value or FormulaRenderer._extract_text(element) or ''
            op_map = {'+': '+', '-': '-', '=': '=', '\u00d7': '\\times',
                      '\u00f7': '\\div', '\u2062': '', '\u2061': ''}
            return op_map.get(val, val)
        elif tag == 'mtext':
            val = element.value or FormulaRenderer._extract_text(element) or ''
            return '\\text{' + val + '}'
        elif tag == 'mfrac':
            if len(element.children) >= 2:
                num = FormulaRenderer.to_latex(element.children[0])
                den = FormulaRenderer.to_latex(element.children[1])
                return f'\\frac{{{num}}}{{{den}}}'
            return '\\frac{?}{?}'
        elif tag == 'msup':
            if len(element.children) >= 2:
                base = FormulaRenderer.to_latex(element.children[0])
                exp = FormulaRenderer.to_latex(element.children[1])
                return f'{base}^{{{exp}}}'
            return '?^{?}'
        elif tag == 'msub':
            if len(element.children) >= 2:
                base = FormulaRenderer.to_latex(element.children[0])
                sub = FormulaRenderer.to_latex(element.children[1])
                return f'{base}_{{{sub}}}'
            return '?_{?}'
        elif tag == 'msqrt':
            inner = ' '.join(FormulaRenderer.to_latex(c) for c in element.children)
            return f'\\sqrt{{{inner}}}'
        elif tag in ('mrow', 'math', 'semantics'):
            return ' '.join(FormulaRenderer.to_latex(c) for c in element.children
                          if c.tag != 'annotation')
        elif tag == 'annotation':
            return ''
        else:
            parts = []
            if element.value:
                parts.append(element.value)
            for child in element.children:
                parts.append(FormulaRenderer.to_latex(child))
            return ' '.join(parts)


# Pre-built formula library
FORMULA_LIBRARY = {
    'quadratic': {
        'id': 'quadratic',
        'name': 'Quadratic Formula',
        'category': 'algebra',
        'mathml': '<math xmlns="http://www.w3.org/1998/Math/MathML"><mrow><mi>x</mi><mo>=</mo><mfrac><mrow><mo>-</mo><mi>b</mi><mo>\u00b1</mo><msqrt><mrow><msup><mi>b</mi><mn>2</mn></msup><mo>-</mo><mn>4</mn><mi>a</mi><mi>c</mi></mrow></msqrt></mrow><mrow><mn>2</mn><mi>a</mi></mrow></mfrac></mrow></math>',
        'description': 'Solutions to ax\u00b2 + bx + c = 0'
    },
    'pythagorean': {
        'id': 'pythagorean',
        'name': 'Pythagorean Theorem',
        'category': 'geometry',
        'mathml': '<math xmlns="http://www.w3.org/1998/Math/MathML"><mrow><msup><mi>a</mi><mn>2</mn></msup><mo>+</mo><msup><mi>b</mi><mn>2</mn></msup><mo>=</mo><msup><mi>c</mi><mn>2</mn></msup></mrow></math>',
        'description': 'Relationship between sides of a right triangle'
    },
    'euler': {
        'id': 'euler',
        'name': "Euler's Identity",
        'category': 'analysis',
        'mathml': '<math xmlns="http://www.w3.org/1998/Math/MathML"><mrow><msup><mi>e</mi><mrow><mi>i</mi><mi>\u03c0</mi></mrow></msup><mo>+</mo><mn>1</mn><mo>=</mo><mn>0</mn></mrow></math>',
        'description': 'Fundamental relationship between e, i, \u03c0, 1, and 0'
    },
    'integral': {
        'id': 'integral',
        'name': 'Fundamental Theorem of Calculus',
        'category': 'calculus',
        'mathml': '<math xmlns="http://www.w3.org/1998/Math/MathML"><mrow><msubsup><mo>\u222b</mo><mi>a</mi><mi>b</mi></msubsup><mi>f</mi><mo>(</mo><mi>x</mi><mo>)</mo><mi>d</mi><mi>x</mi><mo>=</mo><mi>F</mi><mo>(</mo><mi>b</mi><mo>)</mo><mo>-</mo><mi>F</mi><mo>(</mo><mi>a</mi><mo>)</mo></mrow></math>',
        'description': 'Connects differentiation and integration'
    }
}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        if _verify_password(username, password):
            session['user'] = username
            session['role'] = _users[username]['role']
            session['display_name'] = _users[username]['display_name']
            return redirect(url_for('workspace'))
        return render_template('login.html', error='Invalid credentials'), 401
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/workspace')
@login_required
def workspace():
    return render_template('workspace.html')


@app.route('/api/v1/formulas', methods=['GET'])
def list_formulas():
    """List available formula templates from the library."""
    category = request.args.get('category')
    formulas = list(FORMULA_LIBRARY.values())
    if category:
        formulas = [f for f in formulas if f['category'] == category]
    return jsonify({
        'formulas': [{'id': f['id'], 'name': f['name'],
                      'category': f['category'], 'description': f['description']}
                     for f in formulas],
        'total': len(formulas)
    })


@app.route('/api/v1/formulas/<formula_id>', methods=['GET'])
def get_formula(formula_id):
    """Get a specific formula by ID."""
    formula = FORMULA_LIBRARY.get(formula_id)
    if not formula:
        return jsonify({'error': 'Formula not found'}), 404
    return jsonify(formula)


@app.route('/api/v1/renderFormula', methods=['POST'])
@login_required
def render_formula():
    """Parse and render MathML content.

    Accepts MathML XML input and returns structured formula data
    with optional LaTeX conversion.
    """
    content_type = request.content_type or ''

    if 'xml' not in content_type and 'mathml' not in content_type:
        return jsonify({'error': 'Content-Type must be application/xml or application/mathml+xml'}), 415

    xml_content = request.data
    if not xml_content:
        return jsonify({'error': 'Empty request body'}), 400

    output_format = request.args.get('format', 'structured')

    try:
        parser = FormulaParser()
        formula_tree = parser.parse(xml_content)

        if output_format == 'latex':
            latex_output = FormulaRenderer.to_latex(formula_tree)
            return jsonify({
                'status': 'success',
                'format': 'latex',
                'output': latex_output
            })
        elif output_format == 'display':
            display_output = FormulaRenderer.to_display(formula_tree)
            return Response(display_output, mimetype='application/xml', status=200)
        else:
            # Structured JSON output
            def serialize(elem):
                result = {'tag': elem.tag}
                if elem.value:
                    result['value'] = elem.value
                if elem.attributes:
                    result['attributes'] = elem.attributes
                if elem.children:
                    result['children'] = [serialize(c) for c in elem.children]
                return result

            return jsonify({
                'status': 'success',
                'format': 'structured',
                'tree': serialize(formula_tree)
            })

    except etree.XMLSyntaxError as e:
        return jsonify({'error': 'Invalid XML syntax', 'detail': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Processing failed'}), 500


@app.route('/api/v1/convertFormula', methods=['POST'])
@login_required
def convert_formula():
    """Convert a library formula to LaTeX format."""
    data = request.get_json(silent=True)
    if not data or 'formula_id' not in data:
        return jsonify({'error': 'Missing formula_id parameter'}), 400

    formula = FORMULA_LIBRARY.get(data['formula_id'])
    if not formula:
        return jsonify({'error': 'Formula not found'}), 404

    try:
        parser = FormulaParser()
        tree = parser.parse(formula['mathml'])
        latex = FormulaRenderer.to_latex(tree)
        return jsonify({
            'formula_id': data['formula_id'],
            'name': formula['name'],
            'latex': latex,
            'mathml': formula['mathml']
        })
    except Exception:
        return jsonify({'error': 'Conversion failed'}), 500


@app.route('/api/v1/health')
def health():
    return jsonify({'status': 'ok', 'service': 'formula-toolkit', 'version': '1.2.0'})


@app.route('/ping')
def ping():
    return 'pong', 200


@app.errorhandler(404)
def not_found(e):
    if request.is_json or (request.content_type and 'xml' in request.content_type):
        return jsonify({'error': 'Not found'}), 404
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500


@app.after_request
def add_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers.pop('Server', None)
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
