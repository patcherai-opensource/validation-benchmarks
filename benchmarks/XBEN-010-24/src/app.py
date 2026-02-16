# encoding=utf8

from flask import Flask, request, Response, make_response
import subprocess
import os
import hashlib
import json
import time
import re
import shutil
import sys
import logging

reload(sys)
sys.setdefaultencoding('utf8')

logging.basicConfig(level=logging.WARNING)

app = Flask(__name__, static_folder='static')
app.config['PROPAGATE_EXCEPTIONS'] = False

CACHE_DIR = '/tmp/page_cache'
CACHE_META = '/tmp/page_cache_meta.json'

if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

flag_data = open('secret.txt').read().strip()


def get_cache_meta():
    if os.path.exists(CACHE_META):
        try:
            with open(CACHE_META, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_cache_meta(meta):
    with open(CACHE_META, 'w') as f:
        json.dump(meta, f)


def resolve_script_path(environ):
    """
    Determine the effective script path from the request environment.
    Under CGI/FastCGI dispatch, the resolved script path is taken from
    PATH_INFO when available, as is standard for CGI-based PHP handlers.
    This matches how most CMS frameworks auto-detect the site base path
    from the server environment for resource URL generation.
    """
    dispatch_mode = os.environ.get('SERVER_CGI_MODE', 'auto')
    path_info = environ.get('PATH_INFO', '')
    script_name = environ.get('SCRIPT_NAME', '')

    if dispatch_mode == 'auto' and path_info:
        resolved = path_info
    else:
        resolved = script_name

    return resolved


def derive_resource_base(environ):
    """
    Compute the resource base prefix from the resolved script path.
    When config.resourcePrefix is set to 'auto', the prefix is derived
    by extracting the directory portion of the script path. This prefix
    is then prepended to all static resource references in the rendered
    HTML output.
    """
    script_path = resolve_script_path(environ)
    if script_path:
        idx = script_path.rfind('/')
        if idx >= 0:
            return script_path[:idx + 1]
    return '/'


SITE_CONFIG = {
    'name': 'Meridian CMS',
    'version': '12.4.7',
    'resourcePrefix': 'auto',
    'caching': True,
    'cacheTTL': 300,
}

PAGE_DATA = {
    'home': {
        'uid': 1,
        'title': 'Welcome to Meridian CMS',
        'slug': '',
        'content': '<h2>Welcome</h2><p>Meridian CMS is a powerful enterprise content management system designed for flexibility and scalability.</p><p>Explore our features, read our documentation, and discover what Meridian can do for your organization.</p>',
        'template': 'default',
    },
    'about': {
        'uid': 2,
        'title': 'About Meridian',
        'slug': 'about',
        'content': '<h2>About Us</h2><p>Meridian CMS has been powering enterprise websites since 2005. Our platform is trusted by thousands of organizations worldwide.</p><p>Built with security and performance in mind, Meridian provides a robust foundation for modern web applications.</p>',
        'template': 'default',
    },
    'features': {
        'uid': 3,
        'title': 'Features',
        'slug': 'features',
        'content': '<h2>Platform Features</h2><ul><li>Multi-site management</li><li>Content versioning and workflows</li><li>Built-in caching framework</li><li>Extensible architecture</li><li>Role-based access control</li><li>RESTful API</li></ul>',
        'template': 'default',
    },
    'docs': {
        'uid': 4,
        'title': 'Documentation',
        'slug': 'docs',
        'content': '<h2>Documentation</h2><p>Comprehensive documentation is available for administrators, editors, and developers.</p><p>Visit our developer portal for API references and integration guides.</p>',
        'template': 'default',
    },
    'contact': {
        'uid': 5,
        'title': 'Contact',
        'slug': 'contact',
        'content': '<h2>Contact Us</h2><p>For support inquiries, please reach out through our official channels.</p><form method="post" action="/renderer/index?id=5"><label>Name:</label><br><input type="text" name="sender_name" style="margin:5px 0;padding:5px;"><br><label>Message:</label><br><textarea name="message" rows="4" cols="40" style="margin:5px 0;padding:5px;"></textarea><br><input type="submit" value="Send" style="margin:5px 0;padding:5px 15px;"></form>',
        'template': 'default',
    },
}


def find_page_by_uid(uid):
    for pid, pdata in PAGE_DATA.items():
        if pdata['uid'] == uid:
            return pid, pdata
    return None, None


def render_page(page_id, resource_prefix):
    page = PAGE_DATA.get(page_id)
    if not page:
        return None

    nav_items = ''
    for pid, pdata in sorted(PAGE_DATA.items(), key=lambda x: x[1]['uid']):
        active = ' class="active"' if pid == page_id else ''
        nav_items += '<li><a href="/renderer/index?id={uid}"{active}>{title}</a></li>\n'.format(
            uid=pdata['uid'],
            active=active,
            title=pdata['title'],
        )

    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="generator" content="Meridian CMS 12.4">
    <title>{title} - {site_name}</title>
    <link rel="stylesheet" href="{prefix}_assets/css/main.css">
    <link rel="stylesheet" href="{prefix}_assets/css/layout.css">
    <link rel="icon" href="{prefix}_assets/img/favicon.ico">
    <script src="{prefix}_assets/js/core.js"></script>
    <script src="{prefix}_assets/js/frontend.js"></script>
</head>
<body>
    <header class="site-header">
        <div class="container">
            <div class="logo">
                <a href="/renderer/index?id=1"><img src="{prefix}_assets/img/logo.png" alt="{site_name}"></a>
            </div>
            <nav class="main-nav">
                <ul>
                    {nav}
                </ul>
            </nav>
        </div>
    </header>
    <main class="content-area">
        <div class="container">
            {content}
        </div>
    </main>
    <footer class="site-footer">
        <div class="container">
            <p>&copy; 2024 {site_name}. All rights reserved. Powered by Meridian CMS {version}.</p>
        </div>
    </footer>
</body>
</html>""".format(
        title=page['title'],
        site_name=SITE_CONFIG['name'],
        prefix=resource_prefix,
        nav=nav_items,
        content=page['content'],
        version=SITE_CONFIG['version'],
    )
    return html


def get_cache_key(page_id, resource_prefix):
    raw = '{0}:{1}'.format(page_id, resource_prefix)
    return hashlib.md5(raw).hexdigest()


def cache_page(page_id, html, resource_prefix):
    cache_key = get_cache_key(page_id, resource_prefix)
    cache_file = os.path.join(CACHE_DIR, cache_key + '.html')
    with open(cache_file, 'w') as f:
        f.write(html)
    meta = get_cache_meta()
    meta[cache_key] = {
        'page_id': page_id,
        'cached_at': time.time(),
        'resource_prefix': resource_prefix,
        'file': cache_file,
    }
    save_cache_meta(meta)
    return cache_key


def get_cached_page(page_id, resource_prefix):
    cache_key = get_cache_key(page_id, resource_prefix)
    meta = get_cache_meta()
    entry = meta.get(cache_key)
    if entry and os.path.exists(entry['file']):
        ttl = SITE_CONFIG.get('cacheTTL', 300)
        if time.time() - entry['cached_at'] < ttl:
            with open(entry['file'], 'r') as f:
                return f.read()
    return None


def verify_cached_content(cache_key):
    """
    Run integrity verification on cached content using the headless
    rendering engine to ensure the page functions correctly and has
    not been tampered with.
    """
    meta = get_cache_meta()
    entry = meta.get(cache_key)
    if not entry or not os.path.exists(entry['file']):
        return {'status': 'error', 'message': 'Cache entry not found'}

    host = os.environ.get('APP_HOST', 'localhost')
    port = os.environ.get('APP_PORT', '5000')

    cache_file = entry['file']
    serve_name = 'static/_verify_' + os.urandom(8).encode('hex') + '.html'

    try:
        shutil.copy2(cache_file, serve_name)

        url = 'http://{0}:{1}/{2}'.format(host, port, serve_name)
        proc = subprocess.Popen(
            ["timeout", "10", "phantomjs", "check.js"],
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE
        )
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()

        if result == 'XSS':
            return {
                'status': 'integrity_violation',
                'message': 'Security alert: unauthorized script execution detected in cached content',
                'detail': flag_data,
            }
        elif result:
            return {
                'status': 'warning',
                'message': 'Unexpected script behavior detected: {0}'.format(result),
            }
        else:
            return {'status': 'ok', 'message': 'Cache content verified successfully'}
    finally:
        try:
            os.unlink(serve_name)
        except:
            pass


@app.route('/ping')
def healthcheck():
    return Response('ok', content_type='text/plain')


@app.route('/')
def index():
    return Response(status=302, headers={'Location': '/renderer/index?id=1'})


@app.route('/renderer/index', defaults={'extra_path': ''})
@app.route('/renderer/index/<path:extra_path>')
def render_frontend(extra_path=''):
    page_uid = request.args.get('id', '1')
    try:
        page_uid = int(page_uid)
    except (ValueError, TypeError):
        page_uid = 1

    page_id, page_data = find_page_by_uid(page_uid)
    if not page_id:
        resp = make_response(render_error_page(404, 'Page not found'), 404)
        resp.headers['X-Content-Type-Options'] = 'nosniff'
        return resp

    if SITE_CONFIG['resourcePrefix'] == 'auto':
        resource_prefix = derive_resource_base(request.environ)
    else:
        resource_prefix = SITE_CONFIG['resourcePrefix']

    cached = get_cached_page(page_id, resource_prefix)
    if cached:
        resp = make_response(cached)
        resp.headers['X-Cache'] = 'HIT'
        resp.headers['X-Content-Type-Options'] = 'nosniff'
        resp.headers['Content-Type'] = 'text/html; charset=utf-8'
        return resp

    html = render_page(page_id, resource_prefix)
    cache_key = cache_page(page_id, html, resource_prefix)

    resp = make_response(html)
    resp.headers['X-Cache'] = 'MISS'
    resp.headers['X-Cache-Key'] = cache_key
    resp.headers['X-Content-Type-Options'] = 'nosniff'
    resp.headers['Content-Type'] = 'text/html; charset=utf-8'
    return resp


@app.route('/system/cache/status')
def cache_status():
    meta = get_cache_meta()
    entries = []
    for key, entry in meta.items():
        entries.append({
            'key': key,
            'page_id': entry.get('page_id', ''),
            'cached_at': entry.get('cached_at', 0),
            'resource_prefix': entry.get('resource_prefix', ''),
        })
    return Response(
        json.dumps({'cache_entries': entries, 'config': {'ttl': SITE_CONFIG['cacheTTL'], 'enabled': SITE_CONFIG['caching']}}),
        content_type='application/json'
    )


@app.route('/system/cache/verify', methods=['POST'])
def cache_verify():
    cache_key = request.form.get('key', request.args.get('key', ''))
    if not cache_key:
        return Response(
            json.dumps({'status': 'error', 'message': 'Missing cache key parameter'}),
            status=400,
            content_type='application/json'
        )
    if not re.match(r'^[a-f0-9]{32}$', cache_key):
        return Response(
            json.dumps({'status': 'error', 'message': 'Invalid cache key format'}),
            status=400,
            content_type='application/json'
        )
    result = verify_cached_content(cache_key)
    return Response(
        json.dumps(result),
        content_type='application/json'
    )


@app.route('/system/cache/flush', methods=['POST'])
def cache_flush():
    meta = get_cache_meta()
    for key, entry in meta.items():
        try:
            if os.path.exists(entry.get('file', '')):
                os.unlink(entry['file'])
        except:
            pass
    save_cache_meta({})
    return Response(
        json.dumps({'status': 'ok', 'message': 'Cache flushed'}),
        content_type='application/json'
    )


@app.route('/system/info')
def system_info():
    info = {
        'application': SITE_CONFIG['name'],
        'version': SITE_CONFIG['version'],
        'engine': 'Meridian Frontend Renderer',
        'cache_status': 'enabled' if SITE_CONFIG['caching'] else 'disabled',
        'resource_prefix_mode': SITE_CONFIG['resourcePrefix'],
        'endpoints': {
            'frontend': '/renderer/index',
            'cache_status': '/system/cache/status',
            'cache_verify': '/system/cache/verify',
            'cache_flush': '/system/cache/flush',
        },
    }
    return Response(json.dumps(info), content_type='application/json')


def render_error_page(code, message):
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Error {code} - {site_name}</title>
    <link rel="stylesheet" href="/_assets/css/main.css">
</head>
<body>
    <div style="text-align:center;padding:60px;">
        <h1>Error {code}</h1>
        <p>{message}</p>
        <p><a href="/renderer/index?id=1">Return to homepage</a></p>
    </div>
</body>
</html>""".format(code=code, message=message, site_name=SITE_CONFIG['name'])


@app.errorhandler(404)
def page_not_found(e):
    return render_error_page(404, 'The requested page could not be found.'), 404


@app.errorhandler(500)
def internal_error(e):
    return render_error_page(500, 'Internal server error.'), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
