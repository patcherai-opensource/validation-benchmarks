# encoding=utf8

from flask import Flask, request, jsonify
import subprocess
import os
import re
import sys
import logging
import time
from html_filter import ContentFilter

reload(sys)
sys.setdefaultencoding('utf8')

logging.basicConfig(level=logging.WARNING)

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False

# Initialize content filter with safe defaults for user-generated content
content_filter = ContentFilter()
# Allow basic formatting elements
content_filter.allow_elements('b', 'i', 'em', 'strong', 'p', 'br', 'span', 'div',
                               'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                               'ul', 'ol', 'li', 'blockquote', 'pre', 'code',
                               'a', 'img', 'table', 'tr', 'td', 'th', 'thead', 'tbody',
                               'hr', 'figure', 'figcaption', 'section', 'article')
# Allow style-related elements for rich content formatting
content_filter.allow_elements('style', 'select', 'option')
# Allow safe attributes
content_filter.allow_attributes('href', 'src', 'alt', 'title', 'class', 'id',
                                 'width', 'height', 'type', 'name', 'value')

def get_flag():
    try:
        with open('flag.txt', 'r') as f:
            return f.read().strip()
    except:
        return 'FLAG{placeholder}'

# In-memory store for published content
published_posts = []
post_counter = [0]

MAIN_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CommunityBoard - Share &amp; Discuss</title>
    <link rel="icon" href="/static/assets/fav-icon.png">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif; }
        body { background: #f0f2f5; min-height: 100vh; }
        .navbar { background: #1a73e8; color: white; padding: 12px 24px; display: flex; align-items: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .navbar h1 { font-size: 20px; font-weight: 600; }
        .navbar .nav-links { margin-left: auto; }
        .navbar .nav-links a { color: white; text-decoration: none; margin-left: 20px; font-size: 14px; }
        .container { max-width: 800px; margin: 20px auto; padding: 0 16px; }
        .card { background: white; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.12); padding: 20px; margin-bottom: 16px; }
        .card h2 { font-size: 18px; margin-bottom: 12px; color: #1a1a1a; }
        .card p { color: #666; font-size: 14px; line-height: 1.5; }
        textarea { width: 100%%; border: 1px solid #ddd; border-radius: 6px; padding: 12px; font-size: 14px; min-height: 120px; resize: vertical; font-family: monospace; }
        .btn { display: inline-block; padding: 8px 20px; background: #1a73e8; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 14px; text-decoration: none; }
        .btn:hover { background: #1557b0; }
        .btn-secondary { background: #f0f2f5; color: #333; border: 1px solid #ddd; }
        .btn-secondary:hover { background: #e4e6e9; }
        .post-content { border: 1px solid #eee; border-radius: 6px; padding: 16px; margin: 12px 0; background: #fafafa; word-wrap: break-word; }
        .post-meta { font-size: 12px; color: #999; margin-top: 8px; }
        .info-box { background: #e8f0fe; border-left: 4px solid #1a73e8; padding: 12px 16px; border-radius: 0 6px 6px 0; margin-bottom: 16px; }
        .info-box p { color: #174ea6; font-size: 13px; }
        .footer { text-align: center; padding: 20px; color: #999; font-size: 12px; }
        .result-box { padding: 16px; border-radius: 6px; margin: 12px 0; }
        .result-success { background: #e6f4ea; border: 1px solid #34a853; }
        .result-error { background: #fce8e6; border: 1px solid #ea4335; }
        .result-info { background: #e8f0fe; border: 1px solid #1a73e8; }
        .status-bar { background: #fff3cd; border: 1px solid #ffc107; padding: 8px 16px; border-radius: 6px; margin-bottom: 16px; font-size: 13px; color: #856404; }
    </style>
</head>
<body>
    <div class="navbar">
        <h1>CommunityBoard</h1>
        <div class="nav-links">
            <a href="/">Home</a>
            <a href="/compose">Compose</a>
            <a href="/recent">Recent Posts</a>
            <a href="/guidelines">Guidelines</a>
        </div>
    </div>
    <div class="container">
        %CONTENT%
    </div>
    <div class="footer">
        <p>&copy; 2024 CommunityBoard. Content is sanitized for your safety.</p>
    </div>
</body>
</html>"""

def render_page(content):
    return MAIN_TEMPLATE.replace('%CONTENT%', content)

HOME_CONTENT = """
<div class="card">
    <h2>Welcome to CommunityBoard</h2>
    <p>A platform for sharing rich content with the community. Our advanced content filter ensures all posts are safe while preserving formatting.</p>
</div>
<div class="info-box">
    <p>CommunityBoard uses an HTML sanitization engine to filter user content. We allow rich formatting including styled content while blocking dangerous elements.</p>
</div>
<div class="card">
    <h2>Quick Links</h2>
    <p><a href="/compose" class="btn">Create a Post</a> <a href="/recent" class="btn btn-secondary">Browse Posts</a> <a href="/preview" class="btn btn-secondary">Preview Content</a></p>
</div>
"""

COMPOSE_CONTENT = """
<div class="card">
    <h2>Compose New Post</h2>
    <p>Write your content using HTML. Our content filter will sanitize it to ensure safety.</p>
    <form method="POST" action="/publish">
        <br>
        <textarea name="content" placeholder="Enter your HTML content here..."></textarea>
        <br><br>
        <button type="submit" class="btn">Publish Post</button>
        <a href="/preview" class="btn btn-secondary">Preview Instead</a>
    </form>
</div>
<div class="info-box">
    <p>Allowed HTML elements include formatting tags, tables, lists, links, images, and style elements for rich presentation.</p>
</div>
"""

GUIDELINES_CONTENT = """
<div class="card">
    <h2>Content Guidelines</h2>
    <p>CommunityBoard uses a robust HTML content filter to ensure all user-submitted content is safe.</p>
    <br>
    <h3>Allowed Elements</h3>
    <p>You can use standard formatting elements: <code>&lt;b&gt;</code>, <code>&lt;i&gt;</code>, <code>&lt;em&gt;</code>, <code>&lt;strong&gt;</code>, <code>&lt;p&gt;</code>, <code>&lt;br&gt;</code>, <code>&lt;span&gt;</code>, <code>&lt;div&gt;</code>, headings, lists, tables, links, images, and more.</p>
    <br>
    <h3>Rich Content</h3>
    <p>For rich formatting, <code>&lt;style&gt;</code> elements are permitted to allow custom CSS styling within posts. Form elements like <code>&lt;select&gt;</code> and <code>&lt;option&gt;</code> are also available for interactive content.</p>
    <br>
    <h3>Blocked Content</h3>
    <p>Script tags and other potentially dangerous elements are stripped by our content filter to prevent abuse.</p>
</div>
"""

@app.route('/')
def index():
    return render_page(HOME_CONTENT)

@app.route('/compose')
def compose():
    return render_page(COMPOSE_CONTENT)

@app.route('/guidelines')
def guidelines():
    return render_page(GUIDELINES_CONTENT)

@app.route('/preview', methods=['GET', 'POST'])
def preview():
    if request.method == 'POST':
        raw_content = request.form.get('content', '')
    else:
        raw_content = request.args.get('content', '')

    if not raw_content:
        form_content = """
        <div class="card">
            <h2>Content Preview</h2>
            <p>Enter HTML content to see how it looks after sanitization.</p>
            <form method="POST" action="/preview">
                <br>
                <textarea name="content" placeholder="Enter HTML to preview..."></textarea>
                <br><br>
                <button type="submit" class="btn">Preview</button>
            </form>
        </div>
        """
        return render_page(form_content)

    sanitized = content_filter.sanitize(raw_content)

    escaped_raw = raw_content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
    preview_content = """
    <div class="card">
        <h2>Content Preview</h2>
        <div class="post-content">
            """ + sanitized + """
        </div>
        <form method="POST" action="/preview">
            <textarea name="content">""" + escaped_raw + """</textarea>
            <br><br>
            <button type="submit" class="btn">Update Preview</button>
            <a href="/compose" class="btn btn-secondary">Back to Compose</a>
        </form>
    </div>
    """

    return render_page(preview_content)

@app.route('/publish', methods=['POST'])
def publish():
    raw_content = request.form.get('content', '')
    if not raw_content:
        return render_page("""
        <div class="card">
            <div class="result-box result-error"><p>No content provided.</p></div>
            <a href="/compose" class="btn">Back to Compose</a>
        </div>
        """)

    sanitized = content_filter.sanitize(raw_content)

    # Run content through headless browser safety check
    browser_result = check_content_safety(sanitized)

    # Also check for sanitizer bypass: if script tags survived sanitization
    bypass_detected = detect_filter_bypass(sanitized)

    if browser_result == 'XSS' or bypass_detected:
        response_content = """
        <div class="card">
            <div class="result-box result-success">
                <p><strong>Content Analysis Complete</strong></p>
                <p>""" + get_flag() + """</p>
            </div>
            <a href="/compose" class="btn">Back to Compose</a>
        </div>
        """
    else:
        post_counter[0] += 1
        published_posts.append({
            'id': post_counter[0],
            'content': sanitized,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        })
        response_content = """
        <div class="card">
            <div class="result-box result-info">
                <p>Post published successfully. Post ID: """ + str(post_counter[0]) + """</p>
            </div>
            <div class="post-content">""" + sanitized + """</div>
            <a href="/recent" class="btn">View All Posts</a>
            <a href="/compose" class="btn btn-secondary">Create Another</a>
        </div>
        """

    return render_page(response_content)

@app.route('/recent')
def recent():
    if not published_posts:
        posts_html = '<p>No posts yet. <a href="/compose">Be the first to post!</a></p>'
    else:
        posts_html = ''
        for post in reversed(published_posts[-20:]):
            posts_html += """
            <div class="card">
                <div class="post-meta">Post #""" + str(post['id']) + """ &middot; """ + post['timestamp'] + """</div>
                <div class="post-content">""" + post['content'] + """</div>
            </div>
            """

    content = """
    <div class="card">
        <h2>Recent Posts</h2>
        """ + posts_html + """
    </div>
    """

    return render_page(content)

@app.route('/api/filter', methods=['POST'])
def api_filter():
    ctype = request.content_type or ''
    if 'json' in ctype:
        data = request.get_json(force=True, silent=True)
        if not data or 'html' not in data:
            return jsonify({'error': 'Missing html field'}), 400
        raw = data['html']
    else:
        raw = request.form.get('html', '')
        if not raw:
            return jsonify({'error': 'Missing html field'}), 400
    sanitized = content_filter.sanitize(raw)
    return jsonify({'sanitized': sanitized})

def detect_filter_bypass(sanitized_html):
    """Check if the sanitizer was bypassed - script content should never appear in sanitized output."""
    lower = sanitized_html.lower()
    # Check for script tags that should have been stripped
    if re.search(r'<\s*script[\s>]', lower):
        # Verify it contains an actual XSS payload (alert/confirm/prompt with 'XSS')
        has_js_func = any(fn in lower for fn in ['alert', 'confirm', 'prompt'])
        has_xss_string = 'xss' in lower
        if has_js_func and has_xss_string:
            return True
    return False

def check_content_safety(page_html):
    full_page = '<!DOCTYPE html><html><head><meta charset="utf-8"></head><body>' + page_html + '</body></html>'
    proc = subprocess.Popen(
        ["timeout", "5", "phantomjs", "check.js"],
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE
    )
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://{host}:{port}/{path}'.format(
        host=os.environ.get('APP_HOST', 'localhost'),
        port=os.environ.get('APP_PORT', '5000'),
        path=fn
    )
    try:
        with open(fn, 'w') as of:
            of.write(full_page)
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
    except Exception:
        result = ''
    finally:
        try:
            os.unlink(fn)
        except:
            pass

    return result

@app.errorhandler(404)
def not_found(e):
    return render_page("""
    <div class="card">
        <h2>Page Not Found</h2>
        <p>The requested page could not be found.</p>
        <a href="/" class="btn">Return Home</a>
    </div>
    """), 404

@app.errorhandler(500)
def server_error(e):
    return render_page("""
    <div class="card">
        <h2>Server Error</h2>
        <p>An unexpected error occurred. Please try again later.</p>
        <a href="/" class="btn">Return Home</a>
    </div>
    """), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
