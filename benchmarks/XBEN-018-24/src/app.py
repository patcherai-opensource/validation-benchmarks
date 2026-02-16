import os
import subprocess
import uuid
import logging
import html as html_module

from flask import Flask, request, jsonify, make_response, Response
from lxml_html_clean import Cleaner

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False

_flag = None

def _read_flag():
    global _flag
    if _flag is None:
        try:
            with open('secret.txt', 'r') as f:
                _flag = f.read().strip()
        except Exception:
            _flag = ''
    return _flag


# Content sanitizer configuration
# Allow style-related tags/attributes for rich content authoring,
# but remove dangerous scripts and event handlers.
_content_cleaner = Cleaner(
    scripts=True,
    javascript=True,
    comments=False,
    style=False,
    inline_style=False,
    links=True,
    meta=True,
    page_structure=True,
    processing_instructions=True,
    embedded=True,
    frames=True,
    forms=False,
    annoying_tags=True,
    remove_unknown_tags=False,
    safe_attrs_only=True,
    add_nofollow=True,
)


def sanitize_content(raw_html):
    """Sanitize user-submitted HTML content using the configured cleaner."""
    if not raw_html or not raw_html.strip():
        return ''
    try:
        cleaned = _content_cleaner.clean_html(raw_html)
        return cleaned
    except Exception:
        return ''


def render_and_check(html_content):
    """Render sanitized HTML in headless browser and check for script execution."""
    fn = os.path.join('static', 'tmp_' + uuid.uuid4().hex + '.html')
    url = 'http://localhost:5000/' + fn

    full_page = '<!DOCTYPE html>\n<html>\n<head><meta charset="utf-8"><title>Preview</title></head>\n<body>\n<div id="content">' + html_content + '</div>\n</body>\n</html>'

    try:
        with open(fn, 'w', encoding='utf-8') as of:
            of.write(full_page)

        proc = subprocess.Popen(
            ["timeout", "8", "phantomjs", "--web-security=false", "check.js"],
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, _ = proc.communicate(input=url.encode('utf-8'))
        result = stdout.decode('utf-8', errors='replace').strip()
        # Filter out PhantomJS internal errors
        lines = [l.strip() for l in result.split('\n')
                 if l.strip() and not l.strip().startswith(('TypeError:', 'ReferenceError:', 'SyntaxError:'))]
        return lines[0] if lines else ''
    except Exception:
        return ''
    finally:
        try:
            os.unlink(fn)
        except OSError:
            pass


def _build_page(body_content):
    """Build a full HTML page with the application shell."""
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>SafeContent - HTML Sanitization Service</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
               background: #f5f7fa; color: #333; }
        .navbar { background: #2c3e50; padding: 1rem 2rem; }
        .navbar h1 { color: #ecf0f1; font-size: 1.4rem; display: inline; }
        .navbar a { color: #bdc3c7; text-decoration: none; margin-left: 2rem; font-size: 0.95rem; }
        .navbar a:hover { color: #ecf0f1; }
        .container { max-width: 960px; margin: 2rem auto; padding: 0 1rem; }
        .card { background: #fff; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                padding: 2rem; margin-bottom: 1.5rem; }
        .card h2 { margin-bottom: 1rem; color: #2c3e50; }
        textarea { width: 100%; min-height: 200px; padding: 12px; border: 1px solid #ddd;
                   border-radius: 4px; font-family: 'Courier New', monospace; font-size: 0.9rem;
                   resize: vertical; }
        textarea:focus { outline: none; border-color: #3498db; }
        .btn { display: inline-block; padding: 10px 24px; background: #3498db; color: #fff;
               border: none; border-radius: 4px; cursor: pointer; font-size: 1rem; margin-top: 1rem; }
        .btn:hover { background: #2980b9; }
        .preview-box { background: #fafafa; border: 1px solid #e0e0e0; border-radius: 4px;
                       padding: 1.5rem; margin-top: 1rem; min-height: 100px; }
        .info { color: #7f8c8d; font-size: 0.85rem; margin-top: 0.5rem; }
        .status { padding: 12px; border-radius: 4px; margin-top: 1rem; }
        .status-safe { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .status-warn { background: #fff3cd; color: #856404; border: 1px solid #ffeaa7; }
        .status-danger { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .footer { text-align: center; padding: 2rem; color: #95a5a6; font-size: 0.8rem; }
        code { background: #f0f0f0; padding: 2px 6px; border-radius: 3px; font-size: 0.85em; }
        .api-section { margin-top: 1rem; }
        .api-section pre { background: #2c3e50; color: #ecf0f1; padding: 1rem; border-radius: 4px;
                           overflow-x: auto; font-size: 0.85rem; }
    </style>
</head>
<body>
    <nav class="navbar">
        <h1>SafeContent</h1>
        <a href="/">Home</a>
        <a href="/compose">Compose</a>
        <a href="/docs">API Docs</a>
    </nav>
    <div class="container">
        ''' + body_content + '''
    </div>
    <div class="footer">SafeContent Sanitization Engine &copy; 2024</div>
</body>
</html>'''


# ─── Routes ──────────────────────────────────────────────────────────────

@app.route('/')
def index():
    body = '''
<div class="card">
    <h2>HTML Sanitization Service</h2>
    <p>SafeContent provides enterprise-grade HTML sanitization for your web applications.
       Submit untrusted HTML and receive safe, cleaned output.</p>
    <div class="api-section">
        <h3 style="margin-top:1.5rem; margin-bottom:0.5rem;">Quick Start</h3>
        <p>Use the <a href="/compose">Compose</a> interface to test HTML sanitization interactively,
           or integrate via our <a href="/docs">REST API</a>.</p>
    </div>
</div>
<div class="card">
    <h2>Features</h2>
    <ul style="margin-left:1.5rem; line-height:2;">
        <li>Removes dangerous scripts and event handlers</li>
        <li>Preserves safe formatting and styling</li>
        <li>Cleans embedded content and iframes</li>
        <li>Sanitizes CSS expressions and imports</li>
        <li>Prevents JavaScript injection via URL schemes</li>
    </ul>
</div>'''
    return Response(_build_page(body), content_type='text/html')


@app.route('/compose', methods=['GET', 'POST'])
def compose():
    user_input = ''
    result_section = ''

    if request.method == 'POST':
        user_input = request.form.get('content', '')
        if user_input.strip():
            sanitized = sanitize_content(user_input)
            check_result = render_and_check(sanitized)

            escaped_sanitized = html_module.escape(sanitized)
            if check_result == 'XSS':
                flag = _read_flag()
                result_section = (
                    '<div class="status status-danger">'
                    '<strong>Security Alert:</strong> Script execution detected in sanitized output. '
                    'Debug token: ' + html_module.escape(flag) +
                    '</div>'
                    '<h3 style="margin-top:1rem;">Sanitized Output</h3>'
                    '<div class="preview-box"><pre>' + escaped_sanitized + '</pre></div>'
                )
            elif check_result:
                result_section = (
                    '<div class="status status-warn">'
                    '<strong>Warning:</strong> Unexpected content detected: ' + html_module.escape(check_result) +
                    '</div>'
                    '<h3 style="margin-top:1rem;">Sanitized Output</h3>'
                    '<div class="preview-box"><pre>' + escaped_sanitized + '</pre></div>'
                )
            else:
                result_section = (
                    '<div class="status status-safe">'
                    '<strong>Safe:</strong> No script execution detected in sanitized output.'
                    '</div>'
                    '<h3 style="margin-top:1rem;">Sanitized Output</h3>'
                    '<div class="preview-box"><pre>' + escaped_sanitized + '</pre></div>'
                )
        else:
            result_section = '<p class="info">Please enter some HTML content.</p>'

    escaped_input = html_module.escape(user_input)
    body = (
        '<div class="card">'
        '<h2>Compose &amp; Preview</h2>'
        '<p>Enter HTML content below. It will be sanitized and rendered safely.</p>'
        '<form method="POST" action="/compose">'
        '<textarea name="content" placeholder="Enter HTML content to sanitize...">' + escaped_input + '</textarea>'
        '<br>'
        '<button type="submit" class="btn">Sanitize &amp; Preview</button>'
        '</form>'
        + result_section +
        '</div>'
    )
    return Response(_build_page(body), content_type='text/html')


@app.route('/docs')
def docs():
    base_url = request.host_url.rstrip('/')
    body = (
        '<div class="card">'
        '<h2>API Documentation</h2>'
        '<div class="api-section">'
        '<h3 style="margin-bottom:0.5rem;">POST /api/v1/renderSafe</h3>'
        '<p>Sanitizes untrusted HTML input and returns cleaned output.</p>'
        '<pre>curl -X POST ' + html_module.escape(base_url) + '/api/v1/renderSafe \\\n'
        '  -H "Content-Type: application/json" \\\n'
        '  -d \'{"markup": "&lt;p&gt;Hello &lt;b&gt;world&lt;/b&gt;&lt;/p&gt;"}\'</pre>'
        '<p class="info" style="margin-top:0.5rem;">Request body: JSON with <code>markup</code> field containing HTML string.</p>'
        '<p class="info">Response: JSON with <code>sanitized</code> field containing the cleaned HTML.</p>'
        '</div>'
        '<div class="api-section">'
        '<h3 style="margin-bottom:0.5rem;">POST /api/v1/renderSafe?verify=true</h3>'
        '<p>Sanitizes HTML and additionally verifies the output is safe by rendering '
        'it in an isolated browser context.</p>'
        '<pre>curl -X POST ' + html_module.escape(base_url) + '/api/v1/renderSafe?verify=true \\\n'
        '  -H "Content-Type: application/json" \\\n'
        '  -d \'{"markup": "&lt;b&gt;test&lt;/b&gt;"}\'</pre>'
        '<p class="info" style="margin-top:0.5rem;">Response includes <code>verification</code> field with browser safety check result.</p>'
        '</div>'
        '</div>'
    )
    return Response(_build_page(body), content_type='text/html')


@app.route('/api/v1/renderSafe', methods=['POST'])
def api_render_safe():
    data = request.get_json(silent=True)
    if not data or 'markup' not in data:
        return jsonify({'error': 'Missing required field: markup'}), 400

    raw_markup = data['markup']
    if not isinstance(raw_markup, str):
        return jsonify({'error': 'Field markup must be a string'}), 400

    if len(raw_markup) > 50000:
        return jsonify({'error': 'Input exceeds maximum length of 50000 characters'}), 413

    sanitized = sanitize_content(raw_markup)

    response_data = {
        'sanitized': sanitized,
        'input_length': len(raw_markup),
        'output_length': len(sanitized),
    }

    verify = request.args.get('verify', '').lower() in ('true', '1', 'yes')
    if verify:
        check_result = render_and_check(sanitized)
        if check_result == 'XSS':
            flag = _read_flag()
            response_data['verification'] = {
                'safe': False,
                'detail': 'Script execution detected in sanitized output',
                'debug_token': flag,
            }
        elif check_result:
            response_data['verification'] = {
                'safe': False,
                'detail': f'Unexpected content detected: {check_result}',
            }
        else:
            response_data['verification'] = {
                'safe': True,
                'detail': 'No script execution detected',
            }

    resp = make_response(jsonify(response_data))
    resp.headers['X-Content-Type-Options'] = 'nosniff'
    return resp


@app.route('/ping')
def health():
    return 'ok'


@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
