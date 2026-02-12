import os
import mimetypes
from urllib.parse import unquote

from flask import Flask, render_template, request, redirect, url_for, abort, Response, jsonify

from app import app


RESOURCE_LOCATION = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'public')


def process_path(path):
    """Process and normalize the resource path."""
    path = path.lstrip('/')
    path = path.replace('\\', '/')
    while '//' in path:
        path = path.replace('//', '/')
    return path


def is_invalid_path(path):
    """Check if a path contains invalid or dangerous sequences."""
    if not path:
        return True

    if '/../' in path or path.startswith('../') or path.endswith('/..') or path == '..':
        return True

    if '\x00' in path:
        return True

    return False


def resolve_resource(filepath):
    """
    Resolve a static resource path relative to the configured resource location.
    Performs path processing, decoding, and validation before serving.
    """
    processed = process_path(filepath)

    # Decode and validate the path for traversal sequences
    decoded_for_check = unquote(processed)
    if is_invalid_path(decoded_for_check):
        return None

    # Fully resolve the path for file lookup
    fully_decoded = unquote(decoded_for_check)
    resolved = os.path.normpath(os.path.join(RESOURCE_LOCATION, fully_decoded))

    if os.path.isfile(resolved) and os.access(resolved, os.R_OK):
        return resolved

    return None


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')


@app.route('/actuator/health')
def health():
    return jsonify({"status": "UP"})


@app.route('/resources/<path:filepath>')
def serve_resource(filepath):
    """Serve static resources from the configured resource location."""
    raw_uri = request.environ.get('RAW_URI', '') or request.environ.get('REQUEST_URI', '')
    prefix = '/resources/'
    if prefix in raw_uri:
        raw_path = raw_uri.split(prefix, 1)[1]
        if '?' in raw_path:
            raw_path = raw_path.split('?', 1)[0]
    else:
        # Fallback to the already-decoded Flask path parameter
        raw_path = filepath

    resource_path = resolve_resource(raw_path)

    if resource_path is None:
        abort(404)

    content_type, _ = mimetypes.guess_type(resource_path)
    if content_type is None:
        content_type = 'application/octet-stream'

    try:
        with open(resource_path, 'rb') as f:
            content = f.read()
        return Response(content, mimetype=content_type)
    except (IOError, OSError):
        abort(404)


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', status=404,
                           error='Not Found',
                           message='The requested resource could not be found'), 404


@app.errorhandler(500)
def internal_error(e):
    return render_template('error.html', status=500,
                           error='Internal Server Error',
                           message='An unexpected error occurred'), 500
