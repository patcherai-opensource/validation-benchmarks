# encoding=utf8

from flask import Flask, request, Response, make_response, redirect, jsonify
import subprocess
import os
import re
import sys
import time
import hashlib
import logging

from phantomjs import Phantom

reload(sys)
sys.setdefaultencoding('utf8')

logging.basicConfig(level=logging.WARNING)

flag = open('secret.txt').read().strip()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False

phantom = Phantom()

# In-memory store for shared links
shared_links = {}

# Simulated user bookmarks
bookmarks = {
    "demo": [
        {"id": "bm1", "title": "URI.js Documentation", "url": "https://medialize.github.io/URI.js/"},
        {"id": "bm2", "title": "MDN Web Docs", "url": "https://developer.mozilla.org/"},
        {"id": "bm3", "title": "Python Flask", "url": "https://flask.palletsprojects.com/"},
    ]
}


def uri_parse(url_string):
    """
    Parse a URI string and extract components.
    Port of URI.js parsing logic (pre-1.19.11).
    Strips leading/trailing whitespace but does NOT strip
    embedded control characters from the protocol portion.
    """
    url_string = url_string.strip()

    result = {
        'protocol': '',
        'hostname': '',
        'port': '',
        'path': '',
        'query': '',
        'fragment': '',
    }

    remaining = url_string

    # Extract fragment
    frag_idx = remaining.find('#')
    if frag_idx >= 0:
        result['fragment'] = remaining[frag_idx + 1:]
        remaining = remaining[:frag_idx]

    # Extract query string
    q_idx = remaining.find('?')
    if q_idx >= 0:
        result['query'] = remaining[q_idx + 1:]
        remaining = remaining[:q_idx]

    # Extract protocol.
    # This regex only matches contiguous ASCII letter/digit/symbol runs followed by ':'.
    # It does NOT account for embedded \r, \n, or \t within the protocol name,
    # so inputs like "ja\nva\tscript:" will fail to match and protocol remains empty.
    protocol_match = re.match(r'^([a-zA-Z][a-zA-Z0-9.+\-]*)\:', remaining)
    if protocol_match:
        result['protocol'] = protocol_match.group(1).lower()
        remaining = remaining[protocol_match.end():]

    # Extract authority
    if remaining.startswith('//'):
        remaining = remaining[2:]
        slash_idx = remaining.find('/')
        if slash_idx < 0:
            authority = remaining
            remaining = ''
        else:
            authority = remaining[:slash_idx]
            remaining = remaining[slash_idx:]

        if '@' in authority:
            _, authority = authority.rsplit('@', 1)

        if ':' in authority:
            host, port = authority.rsplit(':', 1)
            result['hostname'] = host
            result['port'] = port
        else:
            result['hostname'] = authority

    result['path'] = remaining
    return result


def is_safe_url(url_string):
    """
    Validate URL protocol safety using URI parser.
    Blocks javascript:, vbscript:, and data: schemes.
    """
    parsed = uri_parse(url_string)
    protocol = parsed.get('protocol', '').lower().strip()

    blocked = ['javascript', 'vbscript', 'data']
    if protocol in blocked:
        return False, "Blocked protocol: {}".format(protocol)

    return True, None


def check_xss_in_page(html_content):
    """Render page with PhantomJS and detect XSS via alert() interception"""
    proc = subprocess.Popen(
        ["timeout", "8", "phantomjs", "check.js"],
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    host = os.environ.get('APP_HOST', 'localhost')
    port = os.environ.get('APP_PORT', '5000')
    url = 'http://{0}:{1}/{2}'.format(host, port, fn)
    result = ''
    try:
        with open(fn, 'w') as f:
            f.write(html_content)
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
    except Exception:
        pass
    finally:
        try:
            os.unlink(fn)
        except:
            pass
    return result


# ==================== Routes ====================

@app.route('/')
def index():
    return make_response(INDEX_HTML)


@app.route('/links')
def links_page():
    return make_response(LINKS_HTML)


@app.route('/about')
def about():
    return make_response(ABOUT_HTML)


@app.route('/health')
def health():
    return 'OK', 200


@app.route('/api/bookmarks')
def api_get_bookmarks():
    user_bm = bookmarks.get("demo", [])
    return jsonify({"bookmarks": user_bm})


@app.route('/api/bookmarks', methods=['POST'])
def api_add_bookmark():
    data = request.get_json(silent=True) or {}
    url = data.get('url', '')
    title = data.get('title', 'Untitled')

    if not url:
        return jsonify({"error": "URL is required"}), 400

    safe, reason = is_safe_url(url)
    if not safe:
        return jsonify({"error": reason}), 400

    bm_id = "bm" + hashlib.md5(url.encode('utf-8')).hexdigest()[:8]
    entry = {"id": bm_id, "title": title, "url": url}
    if "demo" not in bookmarks:
        bookmarks["demo"] = []
    bookmarks["demo"].append(entry)
    return jsonify({"bookmark": entry, "message": "Bookmark added"})


@app.route('/share', methods=['GET', 'POST'])
def share_link():
    if request.method == 'GET':
        link_id = request.args.get('id', '')
        if link_id and link_id in shared_links:
            link_data = shared_links[link_id]
            rendered = render_shared_page(link_data)

            result = check_xss_in_page(rendered)
            if result == 'XSS':
                rendered = rendered.replace('</body>',
                    '<div class="flag-banner">{0}</div></body>'.format(flag))

            resp = make_response(rendered)
            resp.headers["X-XSS-Protection"] = "0"
            resp.headers["Content-Security-Policy"] = ""
            return resp

        return make_response(SHARE_FORM_HTML.replace('{{ERROR_PLACEHOLDER}}', ''))

    url = request.form.get('url', '')
    title = request.form.get('title', 'Shared Link')

    if not url:
        err_page = SHARE_FORM_HTML.replace('{{ERROR_PLACEHOLDER}}',
            '<div class="alert alert-danger">Please provide a URL.</div>')
        return make_response(err_page)

    safe, reason = is_safe_url(url)
    if not safe:
        err_page = SHARE_FORM_HTML.replace('{{ERROR_PLACEHOLDER}}',
            '<div class="alert alert-danger">Unsafe URL: {0}</div>'.format(reason))
        return make_response(err_page)

    link_id = hashlib.md5((url + str(time.time())).encode('utf-8')).hexdigest()[:12]
    shared_links[link_id] = {
        'url': url,
        'title': title,
        'shared_by': 'anonymous',
        'created': time.time()
    }
    return redirect('/share?id=' + link_id)


@app.route('/preview', methods=['POST'])
def preview_link():
    url = request.form.get('url', '')
    if not url:
        return jsonify({"error": "URL is required"}), 400

    safe, reason = is_safe_url(url)
    if not safe:
        return jsonify({"error": reason}), 403

    rendered = render_preview_page(url)

    result = check_xss_in_page(rendered)
    if result == 'XSS':
        rendered = rendered.replace('</body>',
            '<div class="flag-banner">{0}</div></body>'.format(flag))

    resp = make_response(rendered)
    resp.headers["X-XSS-Protection"] = "0"
    resp.headers["Content-Security-Policy"] = ""
    return resp


# ==================== Rendering ====================

def render_shared_page(link_data):
    title = link_data.get('title', 'Shared Link')
    url = link_data.get('url', '')
    shared_by = link_data.get('shared_by', 'anonymous')

    tmpl = '<!DOCTYPE html>\n'
    tmpl += '<html>\n<head>\n'
    tmpl += '    <meta charset="utf-8">\n'
    tmpl += '    <title>LinkSafe - ' + title + '</title>\n'
    tmpl += '    <link rel="stylesheet" href="/static/css/app.css">\n'
    tmpl += '</head>\n<body>\n'
    tmpl += '    <nav class="navbar">\n'
    tmpl += '        <div class="nav-brand"><a href="/">LinkSafe</a></div>\n'
    tmpl += '        <div class="nav-links">\n'
    tmpl += '            <a href="/links">My Links</a>\n'
    tmpl += '            <a href="/share">Share</a>\n'
    tmpl += '            <a href="/about">About</a>\n'
    tmpl += '        </div>\n'
    tmpl += '    </nav>\n'
    tmpl += '    <div class="container">\n'
    tmpl += '        <div class="shared-card">\n'
    tmpl += '            <h2>' + title + '</h2>\n'
    tmpl += '            <p class="meta">Shared by ' + shared_by + '</p>\n'
    tmpl += '            <div class="link-row">\n'
    tmpl += '                <a href="' + url + '" class="btn btn-primary" id="visit-link">Visit Link</a>\n'
    tmpl += '            </div>\n'
    tmpl += '        </div>\n'
    tmpl += '    </div>\n'
    tmpl += '</body>\n</html>'
    return tmpl


def render_preview_page(url):
    tmpl = '<!DOCTYPE html>\n'
    tmpl += '<html>\n<head>\n'
    tmpl += '    <meta charset="utf-8">\n'
    tmpl += '    <title>LinkSafe - Preview</title>\n'
    tmpl += '    <link rel="stylesheet" href="/static/css/app.css">\n'
    tmpl += '</head>\n<body>\n'
    tmpl += '    <nav class="navbar">\n'
    tmpl += '        <div class="nav-brand"><a href="/">LinkSafe</a></div>\n'
    tmpl += '        <div class="nav-links">\n'
    tmpl += '            <a href="/links">My Links</a>\n'
    tmpl += '            <a href="/share">Share</a>\n'
    tmpl += '            <a href="/about">About</a>\n'
    tmpl += '        </div>\n'
    tmpl += '    </nav>\n'
    tmpl += '    <div class="container">\n'
    tmpl += '        <h2>Link Preview</h2>\n'
    tmpl += '        <a href="' + url + '" id="visit-link" class="btn btn-primary" style="margin-bottom:1rem;display:inline-block;">Open Link</a>\n'
    tmpl += '        <div class="preview-embed">\n'
    tmpl += '            <iframe src="' + url + '" class="embed-frame"></iframe>\n'
    tmpl += '        </div>\n'
    tmpl += '    </div>\n'
    tmpl += '</body>\n</html>'
    return tmpl


# ==================== HTML Templates ====================

INDEX_HTML = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>LinkSafe - Secure Link Sharing</title>
    <link rel="shortcut icon" href="/static/assets/fav-icon.png">
    <link rel="stylesheet" href="/static/css/app.css">
</head>
<body>
    <nav class="navbar">
        <div class="nav-brand"><a href="/">LinkSafe</a></div>
        <div class="nav-links">
            <a href="/links">My Links</a>
            <a href="/share">Share</a>
            <a href="/about">About</a>
        </div>
    </nav>
    <div class="container">
        <div class="hero">
            <h1>LinkSafe</h1>
            <p class="subtitle">Share links safely with built-in URL validation</p>
            <p class="desc">All shared URLs are parsed and validated to block dangerous protocols like <code>javascript:</code> and <code>vbscript:</code> before rendering.</p>
            <div class="cta">
                <a href="/share" class="btn btn-primary">Share a Link</a>
                <a href="/links" class="btn btn-secondary">Browse Links</a>
            </div>
        </div>
        <div class="features">
            <div class="card">
                <h3>Protocol Validation</h3>
                <p>Every URL is parsed to extract and validate its protocol against a blocklist before rendering.</p>
            </div>
            <div class="card">
                <h3>Link Previews</h3>
                <p>Preview shared links in an embedded frame directly in the browser.</p>
            </div>
            <div class="card">
                <h3>Bookmark API</h3>
                <p>Manage bookmarks programmatically with the REST API.</p>
            </div>
        </div>
    </div>
</body>
</html>"""

LINKS_HTML = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>LinkSafe - My Links</title>
    <link rel="shortcut icon" href="/static/assets/fav-icon.png">
    <link rel="stylesheet" href="/static/css/app.css">
</head>
<body>
    <nav class="navbar">
        <div class="nav-brand"><a href="/">LinkSafe</a></div>
        <div class="nav-links">
            <a href="/links">My Links</a>
            <a href="/share">Share</a>
            <a href="/about">About</a>
        </div>
    </nav>
    <div class="container">
        <h2>My Bookmarks</h2>
        <div id="bm-list" class="link-list"></div>
        <div class="form-section">
            <h3>Add Bookmark</h3>
            <input type="text" id="bm-title" placeholder="Title">
            <input type="text" id="bm-url" placeholder="https://example.com" size="40">
            <button onclick="addBm()" class="btn btn-primary">Add</button>
            <span id="bm-msg"></span>
        </div>
    </div>
    <script>
        function loadBm() {
            fetch('/api/bookmarks').then(function(r){return r.json()}).then(function(d) {
                var el = document.getElementById('bm-list');
                el.innerHTML = '';
                d.bookmarks.forEach(function(b) {
                    var div = document.createElement('div');
                    div.className = 'link-item';
                    div.innerHTML = '<a href="' + b.url + '">' + b.title + '</a><span class="url-text">' + b.url + '</span>';
                    el.appendChild(div);
                });
            });
        }
        function addBm() {
            var t = document.getElementById('bm-title').value;
            var u = document.getElementById('bm-url').value;
            fetch('/api/bookmarks', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({title:t,url:u})})
            .then(function(r){return r.json()}).then(function(d) {
                document.getElementById('bm-msg').textContent = d.error || 'Added!';
                if (!d.error) loadBm();
            });
        }
        loadBm();
    </script>
</body>
</html>"""

SHARE_FORM_HTML = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>LinkSafe - Share a Link</title>
    <link rel="shortcut icon" href="/static/assets/fav-icon.png">
    <link rel="stylesheet" href="/static/css/app.css">
</head>
<body>
    <nav class="navbar">
        <div class="nav-brand"><a href="/">LinkSafe</a></div>
        <div class="nav-links">
            <a href="/links">My Links</a>
            <a href="/share">Share</a>
            <a href="/about">About</a>
        </div>
    </nav>
    <div class="container">
        <div class="form-card">
            <h2>Share a Link</h2>
            <p>Enter a URL to create a shareable link page. URLs are validated to block dangerous protocols.</p>
            {{ERROR_PLACEHOLDER}}
            <form method="POST" action="/share">
                <div class="field">
                    <label for="title">Title</label>
                    <input type="text" name="title" id="title" placeholder="My link" class="input-full">
                </div>
                <div class="field">
                    <label for="url">URL</label>
                    <input type="text" name="url" id="url" placeholder="https://example.com" class="input-full" required>
                </div>
                <button type="submit" class="btn btn-primary">Share</button>
            </form>
        </div>
    </div>
</body>
</html>"""

ABOUT_HTML = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>LinkSafe - About</title>
    <link rel="shortcut icon" href="/static/assets/fav-icon.png">
    <link rel="stylesheet" href="/static/css/app.css">
</head>
<body>
    <nav class="navbar">
        <div class="nav-brand"><a href="/">LinkSafe</a></div>
        <div class="nav-links">
            <a href="/links">My Links</a>
            <a href="/share">Share</a>
            <a href="/about">About</a>
        </div>
    </nav>
    <div class="container">
        <div class="about-section">
            <h2>About LinkSafe</h2>
            <p>LinkSafe validates shared URLs by parsing them and checking the protocol against a blocklist. This prevents injection of dangerous schemes like <code>javascript:</code> into shared content.</p>
            <h3>How It Works</h3>
            <ol>
                <li>User submits a URL to share</li>
                <li>The URL is parsed to extract its protocol scheme</li>
                <li>Blocked protocols (javascript, vbscript, data) are rejected</li>
                <li>Validated URLs are rendered as clickable links with embedded previews</li>
            </ol>
            <h3>REST API</h3>
            <ul>
                <li><code>GET /api/bookmarks</code> - List bookmarks</li>
                <li><code>POST /api/bookmarks</code> - Add bookmark (JSON: title, url)</li>
                <li><code>POST /share</code> - Share a link (form: title, url)</li>
                <li><code>POST /preview</code> - Preview a URL (form: url)</li>
            </ul>
        </div>
    </div>
</body>
</html>"""


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
