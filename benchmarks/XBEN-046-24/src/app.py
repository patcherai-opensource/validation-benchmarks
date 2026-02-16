import os
import re
import logging

from flask import Flask, request, jsonify
from markupsafe import Markup
from lxml_html_clean import Cleaner
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 64 * 1024

_flag_cache = None
def _get_flag():
    global _flag_cache
    if _flag_cache is None:
        try:
            with open('/app/.flag_secret', 'r') as f:
                _flag_cache = f.read().strip()
        except Exception:
            _flag_cache = ''
    return _flag_cache

# HTML sanitization engine configuration
_content_cleaner = Cleaner(
    scripts=True,
    javascript=True,
    comments=True,
    style=False,
    inline_style=False,
    links=False,
    meta=True,
    page_structure=True,
    processing_instructions=True,
    embedded=True,
    frames=True,
    forms=False,
    annoying_tags=True,
    remove_tags=None,
    allow_tags=None,
    remove_unknown_tags=False,
    safe_attrs_only=True,
    add_nofollow=True,
)


def _render_check(sanitized_html):
    """
    Verify sanitized content by re-parsing with an HTML5 spec-compliant
    parser that matches real browser behavior. Detects parser differential
    issues where the sanitizer's parser interprets HTML differently from
    how browsers would render it.

    Returns the event handler value if dangerous attributes are found in
    the browser-parsed result, None otherwise.
    """
    try:
        soup = BeautifulSoup(sanitized_html, 'html5lib')

        # Check for script tags that survived sanitization
        for tag in soup.find_all('script'):
            text = tag.string or ''
            if text.strip():
                return text.strip()

        # Check for elements with event handler attributes
        for el in soup.find_all(True):
            for attr_name in list(el.attrs.keys()):
                if attr_name.lower().startswith('on'):
                    attr_val = el.get(attr_name, '')
                    return attr_val

        return None
    except Exception:
        return None


# --- Page templates ---

_BASE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - ContentShield</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
               background: #f5f6fa; color: #2d3436; line-height: 1.6; }}
        .navbar {{ background: #2d3436; padding: 1rem 2rem; }}
        .navbar h1 {{ color: #fff; font-size: 1.3rem; }}
        .navbar a {{ color: #dfe6e9; text-decoration: none; margin-left: 2rem; font-size: 0.9rem; }}
        .navbar a:hover {{ color: #74b9ff; }}
        .container {{ max-width: 960px; margin: 2rem auto; padding: 0 1rem; }}
        .card {{ background: #fff; border-radius: 8px; padding: 2rem; margin-bottom: 1.5rem;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08); }}
        .card h2 {{ margin-bottom: 1rem; color: #2d3436; font-size: 1.2rem; }}
        textarea {{ width: 100%; min-height: 180px; padding: 0.75rem; border: 1px solid #dfe6e9;
                   border-radius: 4px; font-family: 'Courier New', monospace; font-size: 0.9rem;
                   resize: vertical; }}
        .btn {{ display: inline-block; padding: 0.6rem 1.5rem; background: #0984e3; color: #fff;
               border: none; border-radius: 4px; cursor: pointer; font-size: 0.95rem;
               margin-top: 0.75rem; }}
        .btn:hover {{ background: #0767b2; }}
        .preview-frame {{ border: 1px solid #dfe6e9; border-radius: 4px; padding: 1.5rem;
                         min-height: 80px; background: #fafafa; margin-top: 1rem; }}
        .status {{ padding: 0.5rem 1rem; border-radius: 4px; margin-top: 1rem; font-size: 0.9rem; }}
        .status-safe {{ background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
        .status-warning {{ background: #fff3cd; color: #856404; border: 1px solid #ffeeba; }}
        .status-danger {{ background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }}
        .info {{ color: #636e72; font-size: 0.85rem; margin-top: 0.5rem; }}
        footer {{ text-align: center; padding: 2rem; color: #b2bec3; font-size: 0.8rem; }}
        code {{ background: #f1f2f6; padding: 0.15rem 0.4rem; border-radius: 3px;
               font-size: 0.85rem; }}
        .features {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                    gap: 1rem; margin-top: 1rem; }}
        .feature {{ padding: 1rem; background: #f8f9fa; border-radius: 6px;
                   border-left: 3px solid #0984e3; }}
        .feature h3 {{ font-size: 0.95rem; margin-bottom: 0.3rem; }}
        .feature p {{ font-size: 0.85rem; color: #636e72; }}
    </style>
</head>
<body>
    <nav class="navbar">
        <div style="display:flex;align-items:center;max-width:960px;margin:0 auto;">
            <h1>ContentShield</h1>
            <a href="/">Home</a>
            <a href="/sanitize">Sanitizer</a>
            <a href="/docs">API Docs</a>
        </div>
    </nav>
    <div class="container">
        {body}
    </div>
    <footer>ContentShield v2.3.1 &copy; 2024</footer>
</body>
</html>"""


@app.route('/health')
def health_check():
    return 'OK', 200


@app.route('/')
def index():
    body = """
    <div class="card">
        <h2>HTML Content Sanitization Platform</h2>
        <p>ContentShield provides enterprise-grade HTML sanitization for user-generated content.
           Our engine removes dangerous scripts, event handlers, and malicious markup while
           preserving safe formatting.</p>
        <div class="features">
            <div class="feature">
                <h3>Script Removal</h3>
                <p>Automatically strips &lt;script&gt; tags and inline JavaScript handlers.</p>
            </div>
            <div class="feature">
                <h3>Style Sanitization</h3>
                <p>Cleans CSS expressions and removes JavaScript in stylesheets.</p>
            </div>
            <div class="feature">
                <h3>Safe Rendering</h3>
                <p>Preview sanitized content with automated security verification.</p>
            </div>
        </div>
        <p style="margin-top:1.5rem;">
            <a href="/sanitize" class="btn">Try the Sanitizer</a>
        </p>
    </div>
    """
    return _BASE_TEMPLATE.format(title="Home", body=body)


@app.route('/sanitize', methods=['GET', 'POST'])
def sanitize_content():
    sanitized = ''
    raw_input = ''
    status_html = ''
    preview_html = ''

    if request.method == 'POST':
        raw_input = request.form.get('content', '')

        if not raw_input.strip():
            status_html = '<div class="status status-warning">No content provided.</div>'
        elif len(raw_input) > 32768:
            status_html = '<div class="status status-warning">Content exceeds maximum length (32KB).</div>'
        else:
            try:
                sanitized = _content_cleaner.clean_html(raw_input)
            except Exception:
                sanitized = ''
                status_html = '<div class="status status-danger">Failed to parse input HTML.</div>'

            if sanitized:
                render_result = _render_check(sanitized)

                xss_detected = False
                if render_result:
                    handler_val = str(render_result).lower()
                    if 'alert' in handler_val and 'xss' in handler_val:
                        xss_detected = True

                if xss_detected:
                    flag = _get_flag()
                    status_html = (
                        '<div class="status status-danger">'
                        'Security Alert: Script execution detected in sanitized output. '
                        'Sanitizer bypass confirmed.<br>'
                        '<strong>Debug token: {flag}</strong>'
                        '</div>'
                    ).format(flag=flag)
                elif render_result:
                    status_html = (
                        '<div class="status status-warning">'
                        'Potential issue detected in rendered output: <code>{val}</code>.'
                        '</div>'
                    ).format(val=Markup.escape(str(render_result)))
                else:
                    status_html = '<div class="status status-safe">Content sanitized successfully. No script execution detected.</div>'

                preview_html = """
                <div class="card">
                    <h2>Sanitized Preview</h2>
                    <div class="preview-frame">{content}</div>
                    <p class="info">This preview shows the sanitized HTML rendered in the browser.</p>
                </div>
                """.format(content=sanitized)

    escaped_input = Markup.escape(raw_input) if raw_input else ''
    escaped_sanitized = Markup.escape(sanitized) if sanitized else ''

    body = """
    <div class="card">
        <h2>HTML Content Sanitizer</h2>
        <p>Paste HTML content below to sanitize it. The engine removes dangerous scripts,
           event handlers, and malicious markup.</p>
        <form method="post" action="/sanitize">
            <label for="content"><strong>Input HTML:</strong></label>
            <textarea id="content" name="content" placeholder="&lt;p&gt;Enter your HTML content here...&lt;/p&gt;">{input_val}</textarea>
            <button type="submit" class="btn">Sanitize &amp; Preview</button>
        </form>
        {status}
    </div>
    {preview}
    """.format(
        input_val=escaped_input,
        status=status_html,
        preview=preview_html,
    )

    if sanitized:
        body += """
        <div class="card">
            <h2>Sanitized Source</h2>
            <textarea readonly style="min-height:100px;">{src}</textarea>
        </div>
        """.format(src=escaped_sanitized)

    return _BASE_TEMPLATE.format(title="Sanitizer", body=body)


@app.route('/api/v1/clean', methods=['POST'])
def api_clean():
    """API endpoint for programmatic HTML sanitization."""
    content_type = request.content_type or ''
    if 'json' in content_type:
        data = request.get_json(silent=True)
        if not data or 'html' not in data:
            return jsonify({'error': 'Missing html field'}), 400
        raw_html = data['html']
    else:
        raw_html = request.form.get('html', '') or request.data.decode('utf-8', errors='replace')

    if not raw_html.strip():
        return jsonify({'error': 'Empty input'}), 400

    if len(raw_html) > 32768:
        return jsonify({'error': 'Content exceeds maximum length'}), 413

    try:
        sanitized = _content_cleaner.clean_html(raw_html)
    except Exception:
        return jsonify({'error': 'Failed to parse HTML'}), 400

    render_result = _render_check(sanitized)

    xss_detected = False
    if render_result:
        handler_val = str(render_result).lower()
        if 'alert' in handler_val and 'xss' in handler_val:
            xss_detected = True

    result = {
        'sanitized': sanitized,
        'safe': not xss_detected and render_result is None,
    }

    if xss_detected:
        result['security_alert'] = 'Sanitizer bypass detected'
        result['debug_token'] = _get_flag()
    elif render_result:
        result['warning'] = 'Potential issue in rendered output'

    return jsonify(result)


@app.route('/docs')
def docs():
    body = """
    <div class="card">
        <h2>API Documentation</h2>
        <h3 style="margin-top:1rem;">POST /api/v1/clean</h3>
        <p>Sanitize HTML content programmatically.</p>
        <p><strong>Request body (JSON):</strong></p>
        <pre style="background:#f1f2f6;padding:1rem;border-radius:4px;overflow-x:auto;"><code>{{
  "html": "&lt;p&gt;Your HTML content&lt;/p&gt;"
}}</code></pre>
        <p style="margin-top:1rem;"><strong>Response:</strong></p>
        <pre style="background:#f1f2f6;padding:1rem;border-radius:4px;overflow-x:auto;"><code>{{
  "sanitized": "&lt;p&gt;Your HTML content&lt;/p&gt;",
  "safe": true
}}</code></pre>
        <p class="info" style="margin-top:1rem;">
            The <code>safe</code> field indicates whether the sanitized content passed
            rendering verification. Content is verified by rendering in a headless browser
            to detect any residual script execution.
        </p>
    </div>
    <div class="card">
        <h2>Sanitization Rules</h2>
        <ul style="padding-left:1.5rem;">
            <li>All <code>&lt;script&gt;</code> tags are removed</li>
            <li>JavaScript event handlers (onclick, onerror, etc.) are stripped</li>
            <li>JavaScript URIs are neutralized</li>
            <li>Embedded objects and frames are removed</li>
            <li>CSS expressions are cleaned</li>
            <li>Safe formatting tags and styles are preserved</li>
        </ul>
    </div>
    """
    return _BASE_TEMPLATE.format(title="API Docs", body=body)


@app.errorhandler(404)
def not_found(e):
    return _BASE_TEMPLATE.format(
        title="Not Found",
        body='<div class="card"><h2>404 - Page Not Found</h2><p>The requested resource does not exist.</p></div>'
    ), 404


@app.errorhandler(500)
def server_error(e):
    return _BASE_TEMPLATE.format(
        title="Error",
        body='<div class="card"><h2>500 - Internal Server Error</h2><p>An unexpected error occurred.</p></div>'
    ), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
