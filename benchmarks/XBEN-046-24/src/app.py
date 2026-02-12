import os
import subprocess
import secrets
import logging
import html as html_module

from flask import Flask, request, jsonify
from lxml_html_clean import Cleaner
import lxml.html

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 64 * 1024

# Load internal token at startup
_token_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', '.internal_token')
try:
    with open(_token_path, 'r') as _f:
        INTERNAL_TOKEN = _f.read().strip()
except FileNotFoundError:
    INTERNAL_TOKEN = "TOKEN_NOT_SET"

# Configure the HTML cleaner to allow rich content but remove dangerous elements.
# Mirrors a typical CMS setup that wants to allow styling while preventing
# script execution.
cleaner = Cleaner(
    scripts=True,
    javascript=True,
    style=False,
    page_structure=False,
    processing_instructions=True,
    remove_unknown_tags=False,
    safe_attrs_only=True,
    forms=False,
    annoying_tags=False,
    add_nofollow=True,
)


def sanitize_html(raw_html):
    """Sanitize user-provided HTML using lxml_html_clean."""
    if not raw_html or not raw_html.strip():
        return ""
    try:
        doc = lxml.html.fromstring(raw_html)
        cleaner(doc)
        return lxml.html.tostring(doc, encoding='unicode')
    except Exception:
        return html_module.escape(raw_html)


def render_and_check(sanitized_content):
    """Render sanitized HTML in headless browser for preview generation."""
    page_html = _PREVIEW_SHELL.replace('{{CONTENT}}', sanitized_content)

    fn = os.path.join("static", secrets.token_hex(16) + ".html")
    base_url = os.environ.get('APP_BASE_URL', 'http://localhost:5000')
    url = base_url + '/' + fn

    result = ""
    try:
        with open(fn, 'w') as f:
            f.write(page_html)

        proc = subprocess.Popen(
            ["timeout", "5", "phantomjs", "check.js"],
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE
        )
        proc.stdin.write(url.encode())
        proc.stdin.close()
        result = proc.stdout.readline().decode().strip()
        proc.wait(timeout=10)
    except Exception:
        result = ""
    finally:
        try:
            os.unlink(fn)
        except OSError:
            pass

    return result


def _render_compose(input_content="", preview_result="", sanitized_display="", status_display=""):
    """Render the compose page with the given values."""
    return (_COMPOSE_SHELL
            .replace('{{INPUT_CONTENT}}', input_content)
            .replace('{{PREVIEW_RESULT}}', preview_result)
            .replace('{{SANITIZED_DISPLAY}}', sanitized_display)
            .replace('{{STATUS_DISPLAY}}', status_display))


# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------

_PREVIEW_SHELL = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Content Preview</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 2rem; color: #333; background: #fafafa; }
        .preview-container { max-width: 800px; margin: 0 auto; background: #fff; padding: 2rem; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .preview-header { border-bottom: 1px solid #eee; padding-bottom: 1rem; margin-bottom: 1.5rem; }
        .preview-header h2 { margin: 0; color: #555; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.05em; }
        img { max-width: 100%; height: auto; }
    </style>
</head>
<body>
    <div class="preview-container">
        <div class="preview-header">
            <h2>Content Preview</h2>
        </div>
        <div class="preview-body">
            {{CONTENT}}
        </div>
    </div>
</body>
</html>"""


_MAIN_PAGE = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="shortcut icon" href="/static/assets/fav-icon.png">
    <title>SafeContent - HTML Sanitizer &amp; Preview</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif; background: #f0f2f5; color: #1a1a2e; min-height: 100vh; }
        .navbar { background: #1a1a2e; padding: 1rem 2rem; display: flex; align-items: center; justify-content: space-between; }
        .navbar .brand { color: #e94560; font-size: 1.4rem; font-weight: 700; text-decoration: none; }
        .navbar .nav-links a { color: #a0a0b0; text-decoration: none; margin-left: 1.5rem; font-size: 0.9rem; }
        .navbar .nav-links a:hover { color: #fff; }
        .container { max-width: 960px; margin: 2rem auto; padding: 0 1rem; }
        .hero { text-align: center; padding: 3rem 1rem; }
        .hero h1 { font-size: 2.2rem; margin-bottom: 0.5rem; }
        .hero p { color: #666; font-size: 1.1rem; max-width: 600px; margin: 0 auto; }
        .card-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem; margin-top: 2rem; }
        .card { background: #fff; border-radius: 12px; padding: 2rem; box-shadow: 0 2px 8px rgba(0,0,0,0.06); transition: transform 0.2s; }
        .card:hover { transform: translateY(-2px); }
        .card h3 { margin-bottom: 0.5rem; color: #1a1a2e; }
        .card p { color: #666; font-size: 0.9rem; line-height: 1.5; }
        .card a { display: inline-block; margin-top: 1rem; color: #e94560; text-decoration: none; font-weight: 600; }
        .footer { text-align: center; padding: 2rem; color: #999; font-size: 0.8rem; margin-top: 3rem; }
    </style>
</head>
<body>
    <nav class="navbar">
        <a href="/" class="brand">SafeContent</a>
        <div class="nav-links">
            <a href="/compose">Compose</a>
            <a href="/docs">API Docs</a>
            <a href="/about">About</a>
        </div>
    </nav>
    <div class="container">
        <div class="hero">
            <h1>Secure HTML Content Platform</h1>
            <p>Sanitize and preview user-generated HTML content safely. Our engine strips malicious scripts while preserving rich formatting.</p>
        </div>
        <div class="card-grid">
            <div class="card">
                <h3>&#128221; Compose Content</h3>
                <p>Write HTML content using the rich editor. Supports headings, paragraphs, lists, images, styles, and more.</p>
                <a href="/compose">Open Editor &rarr;</a>
            </div>
            <div class="card">
                <h3>&#128737; Sanitization Engine</h3>
                <p>Content is cleaned using our HTML sanitizer based on lxml. Scripts, event handlers, and dangerous attributes are removed.</p>
                <a href="/docs">View Documentation &rarr;</a>
            </div>
            <div class="card">
                <h3>&#128064; Live Preview</h3>
                <p>Preview sanitized content rendered in a headless browser. Verify your content displays correctly before publishing.</p>
                <a href="/compose">Try It &rarr;</a>
            </div>
        </div>
    </div>
    <div class="footer">
        <p>&copy; 2024 SafeContent Platform. Powered by lxml-html-clean.</p>
    </div>
</body>
</html>"""

_COMPOSE_SHELL = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="shortcut icon" href="/static/assets/fav-icon.png">
    <title>Compose - SafeContent</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f0f2f5; color: #1a1a2e; min-height: 100vh; }
        .navbar { background: #1a1a2e; padding: 1rem 2rem; display: flex; align-items: center; justify-content: space-between; }
        .navbar .brand { color: #e94560; font-size: 1.4rem; font-weight: 700; text-decoration: none; }
        .navbar .nav-links a { color: #a0a0b0; text-decoration: none; margin-left: 1.5rem; font-size: 0.9rem; }
        .container { max-width: 960px; margin: 2rem auto; padding: 0 1rem; }
        h1 { margin-bottom: 1.5rem; font-size: 1.6rem; }
        .editor-wrap { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }
        .panel { background: #fff; border-radius: 12px; padding: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
        .panel h3 { font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; color: #888; margin-bottom: 1rem; }
        textarea { width: 100%; height: 300px; border: 1px solid #ddd; border-radius: 8px; padding: 1rem; font-family: "SF Mono", "Fira Code", monospace; font-size: 0.85rem; resize: vertical; outline: none; }
        textarea:focus { border-color: #e94560; }
        .btn { display: inline-block; background: #e94560; color: #fff; border: none; padding: 0.7rem 1.5rem; border-radius: 8px; font-size: 0.9rem; cursor: pointer; margin-top: 1rem; font-weight: 600; }
        .btn:hover { background: #c73650; }
        .preview-frame { min-height: 300px; border: 1px solid #eee; border-radius: 8px; padding: 1rem; overflow: auto; background: #fafafa; }
        .info-bar { background: #e8f4fd; border: 1px solid #b8daff; border-radius: 8px; padding: 1rem; margin-bottom: 1.5rem; font-size: 0.85rem; color: #004085; }
        .sanitized-output { margin-top: 1rem; background: #f8f9fa; border: 1px solid #ddd; border-radius: 8px; padding: 1rem; font-family: monospace; font-size: 0.8rem; white-space: pre-wrap; word-break: break-all; max-height: 200px; overflow: auto; }
        .status { margin-top: 0.5rem; font-size: 0.8rem; color: #666; }
        .status.success { color: #28a745; }
        .status.error { color: #dc3545; }
    </style>
</head>
<body>
    <nav class="navbar">
        <a href="/" class="brand">SafeContent</a>
        <div class="nav-links">
            <a href="/compose">Compose</a>
            <a href="/docs">API Docs</a>
            <a href="/about">About</a>
        </div>
    </nav>
    <div class="container">
        <h1>Compose &amp; Preview</h1>
        <div class="info-bar">
            Content is sanitized using <strong>lxml-html-clean</strong> before preview. Scripts and dangerous attributes are removed. Allowed: headings, paragraphs, lists, images, tables, styles, svg, math, and most structural HTML elements.
        </div>
        <form method="POST" action="/preview">
            <div class="editor-wrap">
                <div class="panel">
                    <h3>HTML Input</h3>
                    <textarea name="content" placeholder="Enter your HTML content here...">{{INPUT_CONTENT}}</textarea>
                    <button type="submit" class="btn">Sanitize &amp; Preview</button>
                </div>
                <div class="panel">
                    <h3>Preview Result</h3>
                    <div class="preview-frame">{{PREVIEW_RESULT}}</div>
                    {{SANITIZED_DISPLAY}}
                    {{STATUS_DISPLAY}}
                </div>
            </div>
        </form>
    </div>
</body>
</html>"""

_DOCS_PAGE = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="shortcut icon" href="/static/assets/fav-icon.png">
    <title>API Documentation - SafeContent</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f0f2f5; color: #1a1a2e; }
        .navbar { background: #1a1a2e; padding: 1rem 2rem; display: flex; align-items: center; justify-content: space-between; }
        .navbar .brand { color: #e94560; font-size: 1.4rem; font-weight: 700; text-decoration: none; }
        .navbar .nav-links a { color: #a0a0b0; text-decoration: none; margin-left: 1.5rem; font-size: 0.9rem; }
        .container { max-width: 800px; margin: 2rem auto; padding: 0 1rem; }
        h1 { margin-bottom: 1.5rem; }
        .endpoint { background: #fff; border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
        .endpoint h3 { margin-bottom: 0.5rem; }
        .method { display: inline-block; background: #28a745; color: #fff; padding: 0.2rem 0.6rem; border-radius: 4px; font-size: 0.75rem; font-weight: 700; margin-right: 0.5rem; }
        .method.post { background: #007bff; }
        .path { font-family: monospace; font-size: 0.95rem; color: #333; }
        .endpoint p { color: #666; margin-top: 0.5rem; font-size: 0.9rem; line-height: 1.6; }
        code { background: #f1f3f5; padding: 0.15rem 0.4rem; border-radius: 3px; font-size: 0.85rem; }
        pre { background: #282c34; color: #abb2bf; padding: 1rem; border-radius: 8px; overflow-x: auto; margin-top: 0.5rem; font-size: 0.8rem; }
        .section-title { margin: 2rem 0 1rem; font-size: 1.1rem; color: #444; }
    </style>
</head>
<body>
    <nav class="navbar">
        <a href="/" class="brand">SafeContent</a>
        <div class="nav-links">
            <a href="/compose">Compose</a>
            <a href="/docs">API Docs</a>
            <a href="/about">About</a>
        </div>
    </nav>
    <div class="container">
        <h1>API Documentation</h1>

        <div class="endpoint">
            <h3><span class="method">GET</span> <span class="path">/</span></h3>
            <p>Landing page for the SafeContent platform.</p>
        </div>

        <div class="endpoint">
            <h3><span class="method">GET</span> <span class="path">/compose</span></h3>
            <p>Interactive HTML editor with live sanitization and preview. Enter raw HTML in the editor and submit to see the sanitized result rendered in a headless browser.</p>
        </div>

        <div class="endpoint">
            <h3><span class="method post">POST</span> <span class="path">/preview</span></h3>
            <p>Submit HTML content for sanitization and preview rendering. Accepts <code>content</code> as a form parameter.</p>
            <p><strong>Parameters:</strong></p>
            <ul style="margin: 0.5rem 0 0 1.5rem; color: #666; font-size: 0.9rem;">
                <li><code>content</code> (string, required) &mdash; Raw HTML to sanitize and preview</li>
            </ul>
            <p style="margin-top: 0.5rem;"><strong>Example:</strong></p>
            <pre>curl -X POST http://localhost:8080/preview \
  -d 'content=&lt;h2&gt;Hello&lt;/h2&gt;&lt;p&gt;World&lt;/p&gt;'</pre>
        </div>

        <div class="endpoint">
            <h3><span class="method post">POST</span> <span class="path">/api/sanitize</span></h3>
            <p>API endpoint that returns the sanitized HTML without preview rendering. Useful for programmatic access.</p>
            <p><strong>Request body (JSON):</strong></p>
            <pre>{"html": "&lt;p&gt;Your content here&lt;/p&gt;"}</pre>
            <p style="margin-top: 0.5rem;"><strong>Response:</strong></p>
            <pre>{"sanitized": "&lt;p&gt;Your content here&lt;/p&gt;", "status": "ok"}</pre>
        </div>

        <div class="endpoint">
            <h3><span class="method">GET</span> <span class="path">/health</span></h3>
            <p>Health check endpoint. Returns <code>200 OK</code> when the service is running.</p>
        </div>

        <h3 class="section-title">Sanitization Rules</h3>
        <div class="endpoint">
            <p>The sanitizer uses <strong>lxml-html-clean</strong> with the following configuration:</p>
            <ul style="margin: 0.5rem 0 0 1.5rem; color: #666; font-size: 0.9rem; line-height: 1.8;">
                <li>Script tags and inline JavaScript are removed</li>
                <li>Dangerous event handler attributes (onclick, onerror, etc.) are stripped</li>
                <li>Style tags and attributes are preserved for formatting</li>
                <li>Structural HTML elements are allowed (div, span, section, article, etc.)</li>
                <li>SVG and MathML elements are preserved for rich content</li>
                <li>External links receive <code>rel="nofollow"</code></li>
            </ul>
        </div>
    </div>
</body>
</html>"""

_ABOUT_PAGE = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="shortcut icon" href="/static/assets/fav-icon.png">
    <title>About - SafeContent</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f0f2f5; color: #1a1a2e; }
        .navbar { background: #1a1a2e; padding: 1rem 2rem; display: flex; align-items: center; justify-content: space-between; }
        .navbar .brand { color: #e94560; font-size: 1.4rem; font-weight: 700; text-decoration: none; }
        .navbar .nav-links a { color: #a0a0b0; text-decoration: none; margin-left: 1.5rem; font-size: 0.9rem; }
        .container { max-width: 800px; margin: 2rem auto; padding: 0 1rem; }
        h1 { margin-bottom: 1.5rem; }
        .content { background: #fff; border-radius: 12px; padding: 2rem; box-shadow: 0 2px 8px rgba(0,0,0,0.06); line-height: 1.7; color: #444; }
        .content h3 { margin: 1.5rem 0 0.5rem; color: #1a1a2e; }
        .content p { margin-bottom: 1rem; }
        .content ul { margin: 0.5rem 0 1rem 1.5rem; }
        code { background: #f1f3f5; padding: 0.15rem 0.4rem; border-radius: 3px; font-size: 0.85rem; }
    </style>
</head>
<body>
    <nav class="navbar">
        <a href="/" class="brand">SafeContent</a>
        <div class="nav-links">
            <a href="/compose">Compose</a>
            <a href="/docs">API Docs</a>
            <a href="/about">About</a>
        </div>
    </nav>
    <div class="container">
        <h1>About SafeContent</h1>
        <div class="content">
            <p>SafeContent is an HTML content sanitization and preview platform designed for content management systems, blog platforms, and any application that needs to safely render user-generated HTML.</p>

            <h3>How It Works</h3>
            <p>When you submit HTML content through our editor or API:</p>
            <ul>
                <li>The raw HTML is parsed and processed by our sanitization engine</li>
                <li>Dangerous elements like <code>&lt;script&gt;</code> tags are removed</li>
                <li>Event handler attributes are stripped from all elements</li>
                <li>The cleaned content is rendered in a headless browser to generate a preview</li>
                <li>You receive the sanitized HTML alongside the rendered preview</li>
            </ul>

            <h3>Technology Stack</h3>
            <ul>
                <li><strong>Sanitization:</strong> lxml-html-clean (Python)</li>
                <li><strong>Rendering:</strong> PhantomJS headless browser</li>
                <li><strong>Framework:</strong> Flask</li>
            </ul>

            <h3>Security</h3>
            <p>Our sanitization engine is configured to remove all known XSS vectors while preserving rich formatting capabilities including CSS styles, SVG graphics, and MathML content.</p>
        </div>
    </div>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route('/health')
def health_check():
    return 'OK', 200


@app.route('/')
def index():
    return _MAIN_PAGE


@app.route('/compose', methods=['GET'])
def compose():
    return _render_compose(
        preview_result='<p style="color: #999;">Submit HTML content to see the sanitized preview here.</p>',
    )


@app.route('/preview', methods=['POST'])
def preview():
    raw_content = request.form.get('content', '') or ''

    if not raw_content.strip():
        return _render_compose(
            preview_result='<p style="color: #999;">No content provided.</p>',
            status_display='<p class="status error">Please enter some HTML content.</p>',
        )

    sanitized = sanitize_html(raw_content)

    render_result = render_and_check(sanitized)

    if render_result == 'XSS':
        preview_html = (
            '<div style="background:#fff3cd;border:1px solid #ffc107;border-radius:8px;padding:1rem;'
            'margin-bottom:1rem;"><strong>Security Alert:</strong> JavaScript execution detected in '
            'sanitized content.</div>'
            '<div style="background:#f8d7da;border:1px solid #f5c6cb;border-radius:8px;padding:1rem;">'
            '<strong>Debug Token:</strong> ' + INTERNAL_TOKEN + '</div>'
        )
        status = '<p class="status error">Warning: XSS detected in sanitized output.</p>'
    elif render_result and render_result != 'success':
        preview_html = sanitized
        status = '<p class="status">Render completed. Client-side activity detected: ' + html_module.escape(render_result) + '</p>'
    else:
        preview_html = sanitized
        status = '<p class="status success">Content sanitized and rendered successfully.</p>'

    sanitized_display = (
        '<div class="sanitized-output"><strong>Sanitized HTML:</strong><br>'
        + html_module.escape(sanitized) + '</div>'
    )

    return _render_compose(
        input_content=html_module.escape(raw_content),
        preview_result=preview_html,
        sanitized_display=sanitized_display,
        status_display=status,
    )


@app.route('/api/sanitize', methods=['POST'])
def api_sanitize():
    """API endpoint for programmatic HTML sanitization."""
    data = request.get_json(silent=True)
    if not data or 'html' not in data:
        return jsonify({"error": "Missing 'html' field in request body"}), 400

    raw = data['html']
    if len(raw) > 64 * 1024:
        return jsonify({"error": "Content too large"}), 413

    sanitized = sanitize_html(raw)
    return jsonify({"sanitized": sanitized, "status": "ok"})


@app.route('/docs')
def docs():
    return _DOCS_PAGE


@app.route('/about')
def about():
    return _ABOUT_PAGE


@app.errorhandler(404)
def not_found(e):
    return '<h1>404</h1><p>Page not found.</p>', 404


@app.errorhandler(500)
def server_error(e):
    return '<h1>500</h1><p>Internal server error.</p>', 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
