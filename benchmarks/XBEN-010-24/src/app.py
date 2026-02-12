# encoding=utf8

from flask import Flask, request, Response, make_response, redirect, url_for, jsonify
import subprocess
import os
import re
import hashlib
import time
import json
import sys
import cgi
import urllib

from phantomjs import Phantom

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flag = open('secret.txt').read().strip()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False

phantom = Phantom()

# In-memory page cache (simulates TYPO3's page cache)
page_cache = {}
CACHE_TTL = 300  # 5 minutes

# Site configuration (simulates TYPO3 TypoScript config)
site_config = {
    'config.absRefPrefix': 'auto',
    'config.doctype': 'html5',
    'config.language': 'en',
    'config.locale_all': 'en_US.UTF-8',
    'config.htmlTag_setParams': 'none',
    'config.cache_period': '86400',
    'config.sendCacheHeaders': '1',
    'config.compressJs': '0',
    'config.compressCss': '0',
    'config.concatenateJs': '0',
    'config.concatenateCss': '0',
}


def get_indp_env(key):
    """
    Simulates TYPO3 GeneralUtility::getIndpEnv().
    Retrieves independent environment variables from the server context.
    In PHP-CGI/FPM, PATH_INFO is appended to SCRIPT_NAME and is
    attacker-controllable via the URL path.
    """
    if key == 'SCRIPT_NAME':
        # Reconstruct SCRIPT_NAME as PHP-CGI/FPM would see it
        # PATH_INFO in WSGI is the full path; we simulate PHP behavior
        # where SCRIPT_NAME = /index.php and PATH_INFO = everything after
        raw_path = request.environ.get('PATH_INFO', '/')
        # URL-decode to simulate PHP-CGI behavior (PHP auto-decodes PATH_INFO)
        decoded_path = urllib.unquote(raw_path)
        return decoded_path

    elif key == 'REQUEST_URI':
        return request.environ.get('REQUEST_URI', request.url)

    elif key == 'TYPO3_SITE_URL':
        return request.host_url

    elif key == 'TYPO3_REQUEST_HOST':
        return request.host

    elif key == 'TYPO3_SITE_PATH':
        # In TYPO3, this computes the site base path from SCRIPT_NAME
        # by stripping the script filename portion
        script_name = get_indp_env('SCRIPT_NAME')
        # Extract directory path: /index.php/foo/bar -> /index.php/foo/
        idx = script_name.rfind('/')
        if idx >= 0:
            site_path = script_name[:idx + 1]
        else:
            site_path = '/'
        return site_path

    return ''


def determine_abs_ref_prefix():
    """
    Simulates TypoScriptFrontendController::setAbsRefPrefix()
    When config.absRefPrefix=auto, the prefix is computed from the
    server environment. The vulnerable behavior uses unfiltered PATH_INFO
    in the site path computation without HTML encoding the output.
    """
    abs_ref_prefix = site_config.get('config.absRefPrefix', '')

    if abs_ref_prefix == 'auto':
        abs_ref_prefix = get_indp_env('TYPO3_SITE_PATH')

    return abs_ref_prefix


def get_cache_key(page_id):
    """Generate cache key for a page."""
    key_parts = 'page_{0}'.format(page_id)
    return hashlib.md5(key_parts.encode('utf-8')).hexdigest()


def render_page(page_id, abs_ref_prefix):
    """Render a CMS page with the computed absRefPrefix for resource URLs."""

    pages = {
        'home': {
            'title': 'Welcome - TYPO3 Corporate Site',
            'nav_active': 'home',
            'content': '''
                <div class="ce-bodytext">
                    <h2>Welcome to Our Corporate Website</h2>
                    <p>This website is powered by TYPO3 CMS, the enterprise open source content management system.</p>
                    <p>We provide innovative solutions for digital transformation and web presence management.</p>
                </div>
                <div class="ce-image">
                    <img src="{prefix}fileadmin/templates/images/hero-banner.jpg" alt="Corporate Banner" width="960" height="400" />
                </div>
            ''',
        },
        'about': {
            'title': 'About Us - TYPO3 Corporate Site',
            'nav_active': 'about',
            'content': '''
                <div class="ce-bodytext">
                    <h2>About Our Company</h2>
                    <p>Founded in 2003, we have been delivering enterprise web solutions using TYPO3 CMS.</p>
                    <p>Our team of certified TYPO3 developers ensures robust and scalable implementations.</p>
                </div>
            ''',
        },
        'news': {
            'title': 'News - TYPO3 Corporate Site',
            'nav_active': 'news',
            'content': '''
                <div class="ce-bodytext">
                    <h2>Latest News</h2>
                    <div class="news-list-view">
                        <div class="article">
                            <h3>TYPO3 v11 LTS Released</h3>
                            <p class="news-text-wrap">The latest long-term support version brings exciting new features for enterprise content management.</p>
                        </div>
                        <div class="article">
                            <h3>Security Update Available</h3>
                            <p class="news-text-wrap">A critical security update has been released. Please update your installations promptly.</p>
                        </div>
                    </div>
                </div>
            ''',
        },
        'contact': {
            'title': 'Contact - TYPO3 Corporate Site',
            'nav_active': 'contact',
            'content': '''
                <div class="ce-bodytext">
                    <h2>Contact Us</h2>
                    <form method="post" action="{prefix}index.php?id=contact&amp;type=submit" class="powermail">
                        <div class="powermail_fieldwrap">
                            <label for="name">Name</label>
                            <input type="text" name="tx_powermail_pi1[field][name]" id="name" class="powermail_input" />
                        </div>
                        <div class="powermail_fieldwrap">
                            <label for="email">Email</label>
                            <input type="email" name="tx_powermail_pi1[field][email]" id="email" class="powermail_input" />
                        </div>
                        <div class="powermail_fieldwrap">
                            <label for="message">Message</label>
                            <textarea name="tx_powermail_pi1[field][message]" id="message" class="powermail_textarea"></textarea>
                        </div>
                        <div class="powermail_fieldwrap">
                            <input type="submit" value="Send Message" class="powermail_submit" />
                        </div>
                    </form>
                </div>
            ''',
        },
    }

    page = pages.get(page_id, pages['home'])
    content = page['content'].replace('{prefix}', abs_ref_prefix)

    nav_items = [
        ('home', 'Home'),
        ('about', 'About'),
        ('news', 'News'),
        ('contact', 'Contact'),
    ]

    nav_html = ''
    for nav_id, nav_label in nav_items:
        active_class = ' class="active"' if nav_id == page.get('nav_active', '') else ''
        nav_html += '<li{active}><a href="{prefix}index.php/{nav_id}">{label}</a></li>\n'.format(
            active=active_class,
            prefix=abs_ref_prefix,
            nav_id=nav_id,
            label=nav_label,
        )

    html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="generator" content="TYPO3 CMS">
    <title>{title}</title>
    <link rel="stylesheet" type="text/css" href="{prefix}typo3temp/assets/compressed/merged-be0f83a742.css" media="all">
    <link rel="stylesheet" type="text/css" href="{prefix}typo3conf/ext/bootstrap_package/Resources/Public/Css/theme.min.css" media="all">
    <link rel="shortcut icon" href="{prefix}favicon.ico" type="image/x-icon">
    <script src="{prefix}typo3temp/assets/compressed/merged-a1b2c3d4e5.js" type="text/javascript"></script>
    <script src="{prefix}typo3conf/ext/bootstrap_package/Resources/Public/JavaScript/Dist/bootstrap.bundle.min.js" type="text/javascript"></script>
</head>
<body>
    <div id="page" class="page">
        <header class="navbar navbar-default">
            <div class="container">
                <div class="navbar-header">
                    <a class="navbar-brand" href="{prefix}index.php/home">
                        <img src="{prefix}fileadmin/templates/images/logo.svg" alt="TYPO3 Corporate" height="40">
                    </a>
                </div>
                <nav class="navbar-collapse">
                    <ul class="nav navbar-nav">
                        {nav}
                    </ul>
                </nav>
            </div>
        </header>
        <main class="main-content">
            <div class="container">
                <div class="content-main">
                    {content}
                </div>
            </div>
        </main>
        <footer class="footer">
            <div class="container">
                <p>&copy; 2024 TYPO3 Corporate Site. Powered by <a href="{prefix}index.php/home">TYPO3 CMS</a></p>
            </div>
        </footer>
    </div>
</body>
</html>'''.format(
        title=page['title'],
        prefix=abs_ref_prefix,
        nav=nav_html,
        content=content,
    )

    return html


def verify_cached_page(cache_identifier):
    """
    Verify a cached page by rendering it in a headless browser.
    Simulates a real visitor accessing the cached content.
    """
    if cache_identifier not in page_cache:
        return None, 'Cache entry not found'

    cached = page_cache[cache_identifier]
    html_content = cached['html']

    fn = 'static/' + os.urandom(16).encode('hex') + '.html'
    host = os.environ.get('APP_HOST', 'localhost')
    port = os.environ.get('APP_PORT', '5000')
    url = 'http://{0}:{1}/{2}'.format(host, port, fn)

    try:
        proc = subprocess.Popen(
            ['timeout', '8', 'phantomjs', 'check.js'],
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE
        )
        of = open(fn, 'w')
        of.write(html_content)
        of.close()

        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
    finally:
        try:
            os.unlink(fn)
        except OSError:
            pass

    return result, None


@app.route('/')
def root():
    """Redirect to the frontend homepage."""
    return redirect('/index.php/home')


@app.route('/index.php')
@app.route('/index.php/')
@app.route('/index.php/<path:page_path>')
def frontend_page(page_path='home'):
    """
    Main frontend page renderer. Simulates TYPO3 frontend output.
    config.absRefPrefix=auto derives the prefix from server environment.
    """
    # Parse page identifier
    parts = page_path.split('/')
    page_id = parts[-1] if parts else 'home'
    if page_id not in ('home', 'about', 'news', 'contact'):
        page_id = 'home'

    # Determine absRefPrefix from environment
    abs_ref_prefix = determine_abs_ref_prefix()

    # Render page content
    html = render_page(page_id, abs_ref_prefix)

    # Store in page cache (cache key based on page_id only, simulating
    # how TYPO3 caches pages - PATH_INFO variations overwrite the same cache entry)
    cache_key = get_cache_key(page_id)
    page_cache[cache_key] = {
        'html': html,
        'timestamp': time.time(),
        'page_id': page_id,
    }

    response = make_response(html)
    response.headers['Content-Type'] = 'text/html; charset=utf-8'
    response.headers['X-TYPO3-Cache'] = 'miss'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response


@app.route('/typo3temp/assets/compressed/<path:filename>')
@app.route('/typo3conf/ext/<path:ext_path>')
@app.route('/fileadmin/<path:file_path>')
def static_resources(filename=None, ext_path=None, file_path=None):
    """Serve static resources."""
    return Response('', status=404)


@app.route('/favicon.ico')
def favicon():
    return Response('', status=404)


@app.route('/typo3/install.php')
def install_blocked():
    return Response('Access denied', status=403)


@app.route('/typo3/')
@app.route('/typo3/index.php')
def typo3_backend():
    """TYPO3 Backend login page."""
    html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>TYPO3 CMS Login</title>
    <style>
        body { font-family: 'Source Sans Pro', Helvetica, Arial, sans-serif; background: #313131; color: #fff; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .login-box { background: #424242; padding: 40px; border-radius: 2px; width: 360px; box-shadow: 0 2px 10px rgba(0,0,0,.3); }
        h1 { font-size: 18px; margin-bottom: 20px; font-weight: normal; }
        .logo { text-align: center; margin-bottom: 20px; }
        .logo span { font-size: 24px; color: #ff8700; }
        input[type="text"], input[type="password"] { width: 100%; padding: 10px; margin: 5px 0 15px; border: 1px solid #555; background: #515151; color: #fff; border-radius: 2px; box-sizing: border-box; }
        button { background: #ff8700; color: #fff; border: none; padding: 10px 20px; width: 100%; cursor: pointer; border-radius: 2px; font-size: 14px; }
        button:hover { background: #e67a00; }
        .info { font-size: 11px; color: #888; margin-top: 15px; text-align: center; }
    </style>
</head>
<body>
    <div class="login-box">
        <div class="logo"><span>TYPO3</span> CMS</div>
        <h1>Login to the Backend</h1>
        <form method="post">
            <input type="text" name="username" placeholder="Username" autocomplete="username">
            <input type="password" name="p_field" placeholder="Password" autocomplete="current-password">
            <button type="submit">Login</button>
        </form>
        <div class="info">TYPO3 CMS 11.5.24</div>
    </div>
</body>
</html>'''
    return make_response(html)


@app.route('/typo3/cache/admin', methods=['GET', 'POST'])
def cache_admin():
    """
    Cache management interface for inspecting and verifying cached pages.
    Renders cached content in a headless browser to check for content integrity.
    """
    if request.method == 'GET':
        entries = []
        for cid, data in page_cache.items():
            entries.append({
                'identifier': cid,
                'page_id': data.get('page_id', 'unknown'),
                'cached_at': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data['timestamp'])),
                'age_seconds': int(time.time() - data['timestamp']),
            })

        html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>TYPO3 Cache Management</title>
    <style>
        body { font-family: 'Source Sans Pro', Helvetica, Arial, sans-serif; background: #fafafa; color: #333; margin: 0; padding: 20px; }
        .module-header { background: #424242; color: #fff; padding: 15px 20px; margin: -20px -20px 20px; }
        .module-header h1 { font-size: 18px; font-weight: normal; margin: 0; }
        .module-header .typo3-badge { color: #ff8700; }
        table { width: 100%; border-collapse: collapse; background: #fff; box-shadow: 0 1px 3px rgba(0,0,0,.12); }
        th { background: #e0e0e0; padding: 10px 15px; text-align: left; font-weight: 600; font-size: 13px; }
        td { padding: 10px 15px; border-bottom: 1px solid #eee; font-size: 13px; }
        .btn { display: inline-block; padding: 5px 12px; background: #ff8700; color: #fff; text-decoration: none; border-radius: 2px; font-size: 12px; border: none; cursor: pointer; }
        .btn:hover { background: #e67a00; }
        .btn-danger { background: #c83c3c; }
        .btn-danger:hover { background: #a52a2a; }
        .empty-state { text-align: center; padding: 40px; color: #888; }
        form.inline { display: inline; }
        .info-box { background: #e8f4fd; border: 1px solid #b8daff; padding: 12px 15px; border-radius: 2px; margin-bottom: 20px; font-size: 13px; }
    </style>
</head>
<body>
    <div class="module-header">
        <h1><span class="typo3-badge">TYPO3</span> &rsaquo; Cache Management</h1>
    </div>
    <div class="info-box">
        Cached page entries are listed below. Use "Verify" to check cached content integrity by rendering in a headless browser.
    </div>
    <table>
        <thead>
            <tr>
                <th>Cache ID</th>
                <th>Page</th>
                <th>Cached At</th>
                <th>Age</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>'''

        if entries:
            for entry in entries:
                html += '''
            <tr>
                <td><code>{identifier}</code></td>
                <td>{page_id}</td>
                <td>{cached_at}</td>
                <td>{age_seconds}s</td>
                <td>
                    <form class="inline" method="post">
                        <input type="hidden" name="action" value="verify">
                        <input type="hidden" name="identifier" value="{identifier}">
                        <button type="submit" class="btn">Verify</button>
                    </form>
                    <form class="inline" method="post">
                        <input type="hidden" name="action" value="flush">
                        <input type="hidden" name="identifier" value="{identifier}">
                        <button type="submit" class="btn btn-danger">Flush</button>
                    </form>
                </td>
            </tr>'''.format(**entry)
        else:
            html += '''
            <tr>
                <td colspan="5" class="empty-state">No cached pages. Visit the frontend to populate the cache.</td>
            </tr>'''

        html += '''
        </tbody>
    </table>
</body>
</html>'''
        return make_response(html)

    # POST actions
    action = request.form.get('action', '')
    identifier = request.form.get('identifier', '')

    if action == 'flush' and identifier:
        if identifier in page_cache:
            del page_cache[identifier]
        return redirect('/typo3/cache/admin')

    elif action == 'flush_all':
        page_cache.clear()
        return redirect('/typo3/cache/admin')

    elif action == 'verify' and identifier:
        result, error = verify_cached_page(identifier)

        if error:
            msg = '<p style="color:#c83c3c;">Error: {0}</p>'.format(cgi.escape(str(error)))
        elif result == 'XSS':
            msg = '<p style="color:#c83c3c;">&#9888; XSS detected in cached content! Compromised data: <code>{0}</code></p>'.format(flag)
        elif result:
            msg = '<p style="color:#ff8700;">Cache content rendered with output: <code>{0}</code></p>'.format(cgi.escape(str(result)))
        else:
            msg = '<p style="color:#2d8a0e;">&#10003; Cache content verified successfully. No issues detected.</p>'

        html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Cache Verification Result</title>
    <style>
        body {{ font-family: 'Source Sans Pro', Helvetica, Arial, sans-serif; background: #fafafa; padding: 20px; }}
        .module-header {{ background: #424242; color: #fff; padding: 15px 20px; margin: -20px -20px 20px; }}
        .module-header h1 {{ font-size: 18px; font-weight: normal; margin: 0; }}
        .module-header .typo3-badge {{ color: #ff8700; }}
        .result-box {{ background: #fff; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,.12); margin-bottom: 20px; }}
        .btn {{ display: inline-block; padding: 8px 16px; background: #ff8700; color: #fff; text-decoration: none; border-radius: 2px; }}
        code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 2px; }}
    </style>
</head>
<body>
    <div class="module-header">
        <h1><span class="typo3-badge">TYPO3</span> &rsaquo; Cache Verification</h1>
    </div>
    <div class="result-box">
        <h3>Verification Result for <code>{identifier}</code></h3>
        {msg}
    </div>
    <a href="/typo3/cache/admin" class="btn">&larr; Back to Cache Management</a>
</body>
</html>'''.format(identifier=cgi.escape(identifier), msg=msg)
        return make_response(html)

    return redirect('/typo3/cache/admin')


@app.route('/ping')
def ping():
    """Health check endpoint."""
    return 'pong'


@app.errorhandler(404)
def not_found(e):
    return Response(
        '<!DOCTYPE html><html><head><title>404 Not Found</title></head>'
        '<body><h1>Not Found</h1><p>The requested URL was not found on this server.</p>'
        '<hr><address>TYPO3 CMS</address></body></html>',
        status=404, mimetype='text/html')


@app.errorhandler(500)
def server_error(e):
    return Response(
        '<!DOCTYPE html><html><head><title>500 Internal Server Error</title></head>'
        '<body><h1>Internal Server Error</h1></body></html>',
        status=500, mimetype='text/html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
