import os
import re
import uuid
import hashlib
from datetime import datetime
from urllib.parse import urlparse
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

app = Flask(__name__)
app.secret_key = os.urandom(24)

watches = {}

def is_safe_url(url):
    """
    Validate URL to prevent local file access.
    Block file:// protocol to prevent reading local files.
    """
    if re.search(r'^file://', url, re.IGNORECASE):
        return False
    return True

def fetch_url_content(url):
    """
    Fetch content from a URL for change detection.
    Supports http, https, and file protocols.
    """
    parsed = urlparse(url)
    
    if parsed.scheme in ['http', 'https']:
        try:
            import urllib.request
            req = urllib.request.Request(url, headers={'User-Agent': 'ChangeWatcher/1.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                return response.read().decode('utf-8', errors='replace')[:50000]
        except Exception as e:
            return f"Error fetching URL: {str(e)}"
    
    elif parsed.scheme == 'file':
        try:
            filepath = parsed.path
            if not filepath:
                filepath = '/' + parsed.netloc + (parsed.path or '')
            with open(filepath, 'r') as f:
                return f.read()[:50000]
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    return "Unsupported protocol"

def generate_watch_id():
    return str(uuid.uuid4())[:8]

@app.route('/')
def index():
    sorted_watches = sorted(watches.values(), key=lambda x: x.get('created_at', ''), reverse=True)
    return render_template('index.html', watches=sorted_watches)

@app.route('/watch/add', methods=['POST'])
def add_watch():
    url = request.form.get('url', '').strip()
    name = request.form.get('name', '').strip() or url[:50]
    
    if not url:
        flash('URL is required', 'error')
        return redirect(url_for('index'))
    
    if not is_safe_url(url):
        flash('File protocol URLs are not allowed for security reasons', 'error')
        return redirect(url_for('index'))
    
    watch_id = generate_watch_id()
    watches[watch_id] = {
        'id': watch_id,
        'url': url,
        'name': name,
        'created_at': datetime.now().isoformat(),
        'last_checked': None,
        'content': None,
        'content_hash': None,
        'status': 'pending'
    }
    
    flash('Watch added successfully. Click "Check Now" to fetch the content.', 'success')
    return redirect(url_for('index'))

@app.route('/watch/<watch_id>/check', methods=['POST'])
def check_watch(watch_id):
    if watch_id not in watches:
        flash('Watch not found', 'error')
        return redirect(url_for('index'))
    
    watch = watches[watch_id]
    content = fetch_url_content(watch['url'])
    
    old_hash = watch.get('content_hash')
    new_hash = hashlib.md5(content.encode()).hexdigest()
    
    watch['content'] = content
    watch['content_hash'] = new_hash
    watch['last_checked'] = datetime.now().isoformat()
    watch['status'] = 'changed' if old_hash and old_hash != new_hash else 'checked'
    
    return redirect(url_for('view_watch', watch_id=watch_id))

@app.route('/watch/<watch_id>')
def view_watch(watch_id):
    if watch_id not in watches:
        flash('Watch not found', 'error')
        return redirect(url_for('index'))
    
    watch = watches[watch_id]
    return render_template('view.html', watch=watch)

@app.route('/watch/<watch_id>/delete', methods=['POST'])
def delete_watch(watch_id):
    if watch_id in watches:
        del watches[watch_id]
        flash('Watch deleted successfully', 'success')
    return redirect(url_for('index'))

@app.route('/api/watches', methods=['GET'])
def api_list_watches():
    return jsonify(list(watches.values()))

@app.route('/api/watches', methods=['POST'])
def api_add_watch():
    data = request.get_json() or {}
    url = data.get('url', '').strip()
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    if not is_safe_url(url):
        return jsonify({'error': 'File protocol URLs are not allowed'}), 403
    
    watch_id = generate_watch_id()
    watches[watch_id] = {
        'id': watch_id,
        'url': url,
        'name': data.get('name', url[:50]),
        'created_at': datetime.now().isoformat(),
        'last_checked': None,
        'content': None,
        'content_hash': None,
        'status': 'pending'
    }
    
    return jsonify(watches[watch_id]), 201

@app.route('/api/watches/<watch_id>/check', methods=['POST'])
def api_check_watch(watch_id):
    if watch_id not in watches:
        return jsonify({'error': 'Watch not found'}), 404
    
    watch = watches[watch_id]
    content = fetch_url_content(watch['url'])
    
    old_hash = watch.get('content_hash')
    new_hash = hashlib.md5(content.encode()).hexdigest()
    
    watch['content'] = content
    watch['content_hash'] = new_hash
    watch['last_checked'] = datetime.now().isoformat()
    watch['status'] = 'changed' if old_hash and old_hash != new_hash else 'checked'
    
    return jsonify(watch)

@app.route('/api/watches/<watch_id>', methods=['GET'])
def api_get_watch(watch_id):
    if watch_id not in watches:
        return jsonify({'error': 'Watch not found'}), 404
    return jsonify(watches[watch_id])

@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', error='Page not found'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error='Internal server error'), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
