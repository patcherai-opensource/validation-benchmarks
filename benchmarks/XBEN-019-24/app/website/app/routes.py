import os
import mimetypes
from urllib.parse import unquote

from flask import render_template, request, redirect, abort, Response, make_response

from app import app

CONTENT_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'public')


def process_path(path):
    """
    Process the given resource path.
    Replaces backslash with forward slash, collapses duplicate slashes,
    and strips leading slashes and control characters.
    """
    path = path.replace('\\', '/')

    cleaned = []
    prev = ''
    for ch in path:
        if ch == '/' and prev == '/':
            continue
        cleaned.append(ch)
        prev = ch
    path = ''.join(cleaned)

    slash = False
    for i, ch in enumerate(path):
        if ch == '/':
            slash = True
        elif ord(ch) > 32 and ord(ch) != 127:
            if i == 0 or (i == 1 and slash):
                return path
            return ('/' + path[i:]) if slash else path[i:]
    return '/' if slash else ''


def clean_path(path):
    """
    Normalize the path by resolving '.' and '..' sequences.
    """
    if not path:
        return path
    path = path.replace('\\', '/')
    prefix = ''
    if path.startswith('/'):
        prefix = '/'
        path = path[1:]
    parts = path.split('/')
    result = []
    for part in parts:
        if part == '' or part == '.':
            continue
        elif part == '..':
            if result and result[-1] != '..':
                result.pop()
            else:
                result.append('..')
        else:
            result.append(part)
    return prefix + '/'.join(result)


def is_invalid_path(path):
    """
    Identifies invalid resource paths. Rejects paths that contain
    WEB-INF/META-INF, protocol handlers, or directory traversal
    sequences that remain after path normalization.
    """
    if 'WEB-INF' in path or 'META-INF' in path:
        return True
    if '://' in path:
        return True
    if '..' in path and '../' in clean_path(path):
        return True
    return False


def is_invalid_encoded_path(path):
    """
    Check whether the given path contains encoded traversal sequences.
    Specifically checks for percent-encoded path separators and known
    traversal patterns in the encoded form.
    """
    if '%' not in path:
        return False
    lower_path = path.lower()
    if '%2f' in lower_path or '%5c' in lower_path:
        return True
    return False


def resolve_resource(raw_path):
    """
    Resolve a resource path against the content root.
    Processes the raw path string, validates it, decodes for file
    resolution, and verifies the resource is under the content location.
    """
    path = process_path(raw_path)

    if not path or path == '/':
        return None

    if is_invalid_path(path):
        return None

    if is_invalid_encoded_path(path):
        return None

    decoded_path = unquote(path)

    if decoded_path.startswith('/'):
        decoded_path = decoded_path[1:]

    resource_path = CONTENT_ROOT + '/' + decoded_path

    if not os.path.isfile(resource_path):
        return None

    if not resource_path.startswith(CONTENT_ROOT):
        return None

    return resource_path


@app.route('/')
def index():
    return redirect('/portal/login')


@app.route('/portal/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        if not username or not password:
            return render_template('login.html', error='Please provide credentials.')
        return render_template('login.html', error='Invalid username or password.')
    return render_template('login.html')


@app.route('/portal/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/actuator/health')
def health():
    return Response('{"status":"UP"}', mimetype='application/json')


@app.route('/actuator/info')
def app_info():
    return Response(
        '{"app":{"name":"Spring Content Service","version":"6.1.14"}}',
        mimetype='application/json'
    )


@app.before_request
def handle_content_request():
    """
    Functional resource handler for static content.
    Intercepts requests to /content/** and serves resources from
    the public content directory. Uses raw URI for proper path
    validation before decoding.
    """
    raw_uri = request.environ.get('RAW_URI') or request.environ.get('REQUEST_URI', '')
    query_idx = raw_uri.find('?')
    if query_idx != -1:
        raw_uri = raw_uri[:query_idx]

    prefix = '/content/'
    if not raw_uri.startswith(prefix):
        return None

    raw_path = raw_uri[len(prefix):]
    if not raw_path:
        abort(404)

    resource_path = resolve_resource(raw_path)
    if resource_path is None:
        abort(404)

    content_type = mimetypes.guess_type(resource_path)[0] or 'application/octet-stream'

    try:
        with open(resource_path, 'rb') as f:
            data = f.read()
        resp = make_response(data)
        resp.headers['Content-Type'] = content_type
        resp.headers['Cache-Control'] = 'public, max-age=3600'
        return resp
    except (IOError, OSError):
        abort(404)


@app.errorhandler(404)
def not_found(e):
    return Response(
        '{"timestamp":"","status":404,"error":"Not Found","path":""}',
        status=404,
        mimetype='application/json'
    )


@app.errorhandler(500)
def server_error(e):
    return Response(
        '{"timestamp":"","status":500,"error":"Internal Server Error","path":""}',
        status=500,
        mimetype='application/json'
    )
