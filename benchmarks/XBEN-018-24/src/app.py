import os
import subprocess
import logging
import hashlib
import time
import html

from flask import Flask, request, render_template_string, jsonify, redirect, url_for, make_response
from lxml_html_clean import Cleaner

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 64 * 1024

# Read flag from build-time planted file
def _read_flag():
    try:
        with open('/app/.flag_secret', 'r') as f:
            return f.read().strip()
    except Exception:
        return 'FLAG{placeholder}'

FLAG = _read_flag()

# HTML Cleaner configuration - standard content sanitization setup
cleaner = Cleaner(
    scripts=True,
    javascript=True,
    comments=False,
    style=False,
    inline_style=False,
    links=False,
    meta=True,
    page_structure=False,
    processing_instructions=True,
    embedded=True,
    frames=True,
    forms=False,
    annoying_tags=False,
    remove_tags=None,
    remove_unknown_tags=False,
    safe_attrs_only=True,
)

# In-memory store for content previews
_content_store = {}


def _render_in_browser(html_content):
    """Render HTML content in headless browser to verify rendering."""
    fn = os.path.join('/app/static', hashlib.md5(os.urandom(16)).hexdigest() + '.html')
    url = 'http://localhost:5000/' + fn.replace('/app/', '')
    try:
        with open(fn, 'w') as f:
            f.write(html_content)
        proc = subprocess.Popen(
            ['timeout', '8', 'phantomjs', '--ignore-ssl-errors=true', 'check.js'],
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        proc.stdin.write(url.encode('utf-8'))
        proc.stdin.close()
        result = proc.stdout.readline().decode('utf-8', errors='replace').strip()
        proc.wait(timeout=10)
        return result
    except Exception as e:
        logger.error('Browser render error: %s', e)
        return ''
    finally:
        try:
            os.unlink(fn)
        except OSError:
            pass


LAYOUT = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{{ title }} - ContentGuard CMS</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f5f7fa; color: #333; }
        .navbar { background: #2c3e50; padding: 12px 24px; display: flex; align-items: center; justify-content: space-between; }
        .navbar a { color: #ecf0f1; text-decoration: none; margin: 0 12px; font-size: 14px; }
        .navbar .brand { font-weight: 700; font-size: 18px; color: #3498db; }
        .container { max-width: 960px; margin: 32px auto; padding: 0 16px; }
        .card { background: #fff; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); padding: 24px; margin-bottom: 24px; }
        h1, h2 { margin-bottom: 16px; }
        h1 { font-size: 24px; color: #2c3e50; }
        h2 { font-size: 18px; color: #34495e; }
        label { display: block; margin-bottom: 6px; font-weight: 600; font-size: 14px; color: #555; }
        textarea { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-family: "Courier New", monospace; font-size: 13px; resize: vertical; }
        .btn { display: inline-block; padding: 10px 20px; background: #3498db; color: #fff; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; text-decoration: none; }
        .btn:hover { background: #2980b9; }
        .btn-secondary { background: #95a5a6; }
        .btn-secondary:hover { background: #7f8c8d; }
        .preview-box { border: 1px solid #e0e0e0; border-radius: 4px; padding: 16px; margin-top: 12px; min-height: 80px; background: #fafafa; }
        .alert { padding: 12px 16px; border-radius: 4px; margin-bottom: 16px; font-size: 14px; }
        .alert-success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .alert-danger { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .alert-info { background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
        .footer { text-align: center; padding: 24px; color: #999; font-size: 12px; }
        .info-text { font-size: 13px; color: #777; margin-top: 8px; }
        table { width: 100%; border-collapse: collapse; margin-top: 12px; }
        th, td { padding: 10px 12px; text-align: left; border-bottom: 1px solid #eee; font-size: 14px; }
        th { background: #f8f9fa; font-weight: 600; color: #555; }
        .status-badge { display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 12px; }
        .status-safe { background: #d4edda; color: #155724; }
        .status-blocked { background: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <nav class="navbar">
        <span class="brand">ContentGuard CMS</span>
        <div>
            <a href="/">Dashboard</a>
            <a href="/compose">Compose</a>
            <a href="/content">Content</a>
            <a href="/docs">API Docs</a>
        </div>
    </nav>
    <div class="container">
        {{ content | safe }}
    </div>
    <div class="footer">ContentGuard CMS v2.4.1 &copy; 2024</div>
</body>
</html>'''


@app.route('/')
def index():
    page_content = '''
    <div class="card">
        <h1>Dashboard</h1>
        <p>Welcome to ContentGuard CMS. Manage your content securely with built-in HTML sanitization.</p>
    </div>
    <div class="card">
        <h2>Quick Actions</h2>
        <a class="btn" href="/compose">Compose New Content</a>
        <a class="btn btn-secondary" href="/content" style="margin-left: 8px;">View Content</a>
    </div>
    <div class="card">
        <h2>Security Overview</h2>
        <p style="font-size: 14px; color: #555;">All user-submitted HTML content is sanitized using our integrated HTML cleaning engine before rendering. Dangerous scripts, event handlers, and malicious markup are automatically removed.</p>
        <table>
            <tr><th>Protection</th><th>Status</th></tr>
            <tr><td>Script tag removal</td><td><span class="status-badge status-safe">Active</span></td></tr>
            <tr><td>Event handler stripping</td><td><span class="status-badge status-safe">Active</span></td></tr>
            <tr><td>JavaScript URL blocking</td><td><span class="status-badge status-safe">Active</span></td></tr>
            <tr><td>Style sanitization</td><td><span class="status-badge status-safe">Active</span></td></tr>
        </table>
    </div>'''
    return render_template_string(LAYOUT, title='Dashboard', content=page_content)


@app.route('/compose', methods=['GET'])
def compose():
    page_content = '''
    <div class="card">
        <h1>Compose Content</h1>
        <p style="font-size: 14px; color: #555; margin-bottom: 16px;">Write or paste HTML content below. It will be sanitized before preview to remove any potentially dangerous elements.</p>
        <form method="POST" action="/preview">
            <label for="content">HTML Content</label>
            <textarea id="content" name="content" rows="12" placeholder="Enter your HTML content here..."></textarea>
            <p class="info-text">Supported: Standard HTML tags, inline styles, links, images. Blocked: scripts, event handlers, iframes, forms with actions.</p>
            <br>
            <button type="submit" class="btn">Sanitize &amp; Preview</button>
        </form>
    </div>'''
    return render_template_string(LAYOUT, title='Compose', content=page_content)


@app.route('/preview', methods=['POST'])
def preview():
    raw_content = request.form.get('content', '')
    if not raw_content.strip():
        page_content = '<div class="alert alert-danger">No content provided.</div>'
        return render_template_string(LAYOUT, title='Preview', content=page_content)

    # Sanitize the HTML content using our cleaner
    try:
        sanitized = cleaner.clean_html(raw_content)
    except Exception:
        page_content = '<div class="alert alert-danger">Failed to process the provided HTML content.</div>'
        return render_template_string(LAYOUT, title='Preview', content=page_content)

    # Build the full page for browser rendering verification
    render_page = '''<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Content Preview</title></head>
<body>
<div id="content">
''' + sanitized + '''
</div>
</body>
</html>'''

    # Render in headless browser for content verification
    browser_result = _render_in_browser(render_page)

    # Generate a content ID for storage
    content_id = hashlib.md5((raw_content + str(time.time())).encode()).hexdigest()[:12]
    _content_store[content_id] = {
        'raw': raw_content,
        'sanitized': sanitized,
        'created': time.strftime('%Y-%m-%d %H:%M:%S'),
        'status': 'verified'
    }

    if browser_result == 'XSS':
        # Content triggered script execution despite sanitization
        page_content = '''
        <div class="alert alert-danger">
            <strong>Security Alert:</strong> Script execution was detected in sanitized content.
            Internal reference: ''' + html.escape(FLAG) + '''
        </div>
        <div class="card">
            <h2>Sanitized Output</h2>
            <div class="preview-box">''' + sanitized + '''</div>
        </div>'''
    else:
        page_content = '''
        <div class="alert alert-success">Content sanitized and verified successfully. Content ID: ''' + html.escape(content_id) + '''</div>
        <div class="card">
            <h2>Sanitized Preview</h2>
            <div class="preview-box">''' + sanitized + '''</div>
        </div>
        <div class="card">
            <h2>Raw Sanitized HTML</h2>
            <textarea rows="6" readonly style="width:100%; font-family: monospace; font-size: 12px;">''' + html.escape(sanitized) + '''</textarea>
        </div>'''

    page_content += '''
        <div style="margin-top: 16px;">
            <a class="btn btn-secondary" href="/compose">Compose Another</a>
        </div>'''

    response = make_response(render_template_string(LAYOUT, title='Preview', content=page_content))
    response.headers['X-XSS-Protection'] = '0'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response


@app.route('/content')
def content_list():
    rows = ''
    if _content_store:
        for cid, item in sorted(_content_store.items(), key=lambda x: x[1]['created'], reverse=True):
            rows += '<tr><td>' + html.escape(cid) + '</td><td>' + html.escape(item['created']) + '</td><td><span class="status-badge status-safe">' + html.escape(item['status']) + '</span></td><td>' + html.escape(item['sanitized'][:60]) + '...</td></tr>'
    else:
        rows = '<tr><td colspan="4" style="text-align:center; color:#999;">No content entries yet.</td></tr>'

    page_content = '''
    <div class="card">
        <h1>Content Library</h1>
        <table>
            <tr><th>ID</th><th>Created</th><th>Status</th><th>Preview</th></tr>
            ''' + rows + '''
        </table>
    </div>'''
    return render_template_string(LAYOUT, title='Content', content=page_content)


@app.route('/api/sanitize', methods=['POST'])
def api_sanitize():
    data = request.get_json(silent=True) or {}
    raw_html = data.get('html', '')
    if not raw_html:
        return jsonify({'error': 'Missing html field'}), 400

    try:
        sanitized = cleaner.clean_html(raw_html)
    except Exception:
        return jsonify({'error': 'Failed to sanitize content'}), 500

    return jsonify({
        'sanitized': sanitized,
        'original_length': len(raw_html),
        'sanitized_length': len(sanitized)
    })


@app.route('/api/preview', methods=['POST'])
def api_preview():
    data = request.get_json(silent=True) or {}
    raw_html = data.get('html', '')
    if not raw_html:
        return jsonify({'error': 'Missing html field'}), 400

    try:
        sanitized = cleaner.clean_html(raw_html)
    except Exception:
        return jsonify({'error': 'Failed to sanitize content'}), 500

    render_page = '''<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Content Preview</title></head>
<body>
<div id="content">
''' + sanitized + '''
</div>
</body>
</html>'''

    browser_result = _render_in_browser(render_page)

    result = {
        'sanitized': sanitized,
        'render_status': 'clean' if browser_result != 'XSS' else 'script_detected'
    }

    if browser_result == 'XSS':
        result['security_alert'] = FLAG

    return jsonify(result)


@app.route('/docs')
def docs():
    page_content = '''
    <div class="card">
        <h1>API Documentation</h1>
        <h2>POST /api/sanitize</h2>
        <p style="font-size: 14px; color: #555;">Sanitize HTML content. Returns cleaned HTML with dangerous elements removed.</p>
        <pre style="background: #f4f4f4; padding: 12px; border-radius: 4px; font-size: 13px;">
Request:
  POST /api/sanitize
  Content-Type: application/json
  {"html": "&lt;p&gt;Hello &lt;b&gt;world&lt;/b&gt;&lt;/p&gt;"}

Response:
  {"sanitized": "&lt;p&gt;Hello &lt;b&gt;world&lt;/b&gt;&lt;/p&gt;",
   "original_length": 28,
   "sanitized_length": 28}
        </pre>

        <h2 style="margin-top: 24px;">POST /api/preview</h2>
        <p style="font-size: 14px; color: #555;">Sanitize and render HTML content in a headless browser for verification. Returns sanitized HTML and render status.</p>
        <pre style="background: #f4f4f4; padding: 12px; border-radius: 4px; font-size: 13px;">
Request:
  POST /api/preview
  Content-Type: application/json
  {"html": "&lt;p&gt;Hello &lt;b&gt;world&lt;/b&gt;&lt;/p&gt;"}

Response:
  {"sanitized": "&lt;p&gt;Hello &lt;b&gt;world&lt;/b&gt;&lt;/p&gt;",
   "render_status": "clean"}
        </pre>

        <h2 style="margin-top: 24px;">POST /preview</h2>
        <p style="font-size: 14px; color: #555;">Form-based content preview. Submit HTML content via the compose page for sanitization and visual preview.</p>
    </div>'''
    return render_template_string(LAYOUT, title='API Docs', content=page_content)


@app.route('/ping')
def ping():
    return 'ok', 200


@app.errorhandler(404)
def not_found(e):
    return render_template_string(LAYOUT, title='Not Found',
        content='<div class="card"><h1>404 - Page Not Found</h1><p>The requested resource does not exist.</p></div>'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template_string(LAYOUT, title='Error',
        content='<div class="card"><h1>500 - Server Error</h1><p>An internal error occurred.</p></div>'), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
