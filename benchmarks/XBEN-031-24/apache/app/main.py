import os
from flask import Flask, render_template, request, abort, jsonify
from urllib.parse import unquote

app = Flask(__name__)
app.secret_key = os.urandom(24)

SHARED_ROOT = "/app/shared"


def normalize_path(path_str):
    """Normalize a path by resolving .. and . components."""
    path_str = path_str.replace('\\', '/')
    
    components = []
    for part in path_str.split('/'):
        if part == '..':
            if components:
                components.pop()
        elif part and part != '.':
            components.append(part)
    
    return '/'.join(components)


def is_descendant_path(base_path, target_path):
    """Check if target_path is a descendant of base_path."""
    base_normalized = normalize_path(base_path)
    target_normalized = normalize_path(target_path)
    
    if not target_normalized.startswith(base_normalized):
        return False
    
    remainder = target_normalized[len(base_normalized):]
    if remainder and not remainder.startswith('/'):
        return False
        
    return True


def resolve_file(base_path, relative_path, scope="descendent"):
    """Resolve a file path relative to a base path with scope restriction."""
    if relative_path.startswith('/'):
        target_path = relative_path
    else:
        target_path = base_path.rstrip('/') + '/' + relative_path
    
    if scope == "descendent":
        if not is_descendant_path(base_path, target_path):
            return None, "Path is outside allowed scope"
    
    decoded_path = unquote(target_path)
    actual_path = os.path.normpath(decoded_path)
    
    return actual_path, None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/files')
@app.route('/files/')
@app.route('/files/<path:filepath>')
def browse_files(filepath=''):
    """File browser endpoint."""
    try:
        full_path = os.path.join(SHARED_ROOT, filepath)
        full_path = os.path.normpath(full_path)
        
        if not full_path.startswith(SHARED_ROOT):
            abort(403)
        
        if not os.path.exists(full_path):
            abort(404)
            
        if os.path.isfile(full_path):
            return render_template('file_content.html', 
                                   content=open(full_path).read(),
                                   filename=os.path.basename(full_path))
        
        items = []
        for item in sorted(os.listdir(full_path)):
            item_path = os.path.join(full_path, item)
            items.append({
                'name': item,
                'is_dir': os.path.isdir(item_path),
                'path': os.path.join(filepath, item) if filepath else item
            })
        
        parent_path = os.path.dirname(filepath) if filepath else None
        
        return render_template('file_browser.html', 
                               items=items, 
                               current_path=filepath,
                               parent_path=parent_path)
    except Exception:
        abort(500)


@app.route('/api/v1/files/download')
def download_file():
    """File download API endpoint."""
    file_path = request.args.get('path', '')
    
    if not file_path:
        return jsonify({'error': 'Missing path parameter'}), 400
    
    resolved_path, error = resolve_file(SHARED_ROOT, file_path, scope="descendent")
    
    if error:
        return jsonify({'error': 'Access denied: ' + error}), 403
    
    if not os.path.exists(resolved_path):
        return jsonify({'error': 'File not found'}), 404
    
    if os.path.isdir(resolved_path):
        return jsonify({'error': 'Cannot download directory'}), 400
    
    try:
        with open(resolved_path, 'r') as f:
            content = f.read()
        return jsonify({
            'filename': os.path.basename(resolved_path),
            'content': content
        })
    except Exception:
        return jsonify({'error': 'Error reading file'}), 500


@app.route('/api/v1/files/list')
def list_files_api():
    """API endpoint to list files in the shared directory"""
    subpath = request.args.get('path', '')
    
    resolved_path, error = resolve_file(SHARED_ROOT, subpath, scope="descendent")
    
    if error:
        return jsonify({'error': 'Access denied'}), 403
    
    if not os.path.exists(resolved_path):
        return jsonify({'error': 'Path not found'}), 404
    
    if not os.path.isdir(resolved_path):
        return jsonify({'error': 'Not a directory'}), 400
    
    try:
        items = []
        for item in sorted(os.listdir(resolved_path)):
            item_full = os.path.join(resolved_path, item)
            items.append({
                'name': item,
                'type': 'directory' if os.path.isdir(item_full) else 'file'
            })
        return jsonify({'path': subpath, 'items': items})
    except Exception:
        return jsonify({'error': 'Error listing directory'}), 500


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/help')
def help_page():
    return render_template('help.html')


@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', error_code=403, message='Access Forbidden'), 403


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', error_code=404, message='Not Found'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error_code=500, message='Internal Server Error'), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
