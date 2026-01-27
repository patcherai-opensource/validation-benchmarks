import os
import re
import uuid
import urllib.request
from flask import Flask, render_template, request, jsonify, redirect, url_for
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)

# In-memory storage for watches
watches = {}

# Flag stored in environment variable
FLAG = os.environ.get('FLAG', 'FLAG{test_flag_placeholder}')

# Configuration - file URIs are disabled by default
ALLOW_FILE_URI = os.environ.get('ALLOW_FILE_URI', 'false').lower() == 'true'

def is_safe_url(url):
    """
    Validate URL to prevent file:// access when ALLOW_FILE_URI is False.
    
    VULNERABILITY: Only checks for 'file://' (two slashes) but file:/ (one slash)
    is also a valid file URI per RFC 8089.
    """
    if not ALLOW_FILE_URI:
        # Flawed check - only blocks file:// but not file:/
        if re.search(r'^file://', url, re.IGNORECASE):
            return False
    return True

def fetch_content(url):
    """
    Fetch content from the given URL.
    Supports http://, https://, and file:// (if allowed) protocols.
    """
    try:
        # File URI handling
        if url.lower().startswith('file:'):
            # Extract file path from file URI
            # Handle both file:// and file:/ formats
            if url.lower().startswith('file://'):
                filepath = url[7:]  # Remove 'file://'
            else:
                filepath = url[5:]  # Remove 'file:'
            
            # Handle localhost prefix
            if filepath.startswith('/localhost'):
                filepath = filepath[10:]
            elif filepath.startswith('localhost'):
                filepath = filepath[9:]
                
            with open(filepath, 'r') as f:
                return f.read()
        
        # HTTP/HTTPS handling
        req = urllib.request.Request(url, headers={'User-Agent': 'PageWatcher/1.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.read().decode('utf-8', errors='replace')
    except Exception as e:
        return f"Error fetching content: {str(e)}"

@app.route('/')
def index():
    """Main page showing all watches."""
    return render_template('index.html', watches=watches)

@app.route('/api/watches', methods=['GET'])
def list_watches():
    """API endpoint to list all watches."""
    watch_list = []
    for watch_id, watch in watches.items():
        watch_list.append({
            'id': watch_id,
            'url': watch['url'],
            'title': watch['title'],
            'created_at': watch['created_at'],
            'last_checked': watch.get('last_checked'),
            'status': watch.get('status', 'pending')
        })
    return jsonify({'watches': watch_list})

@app.route('/api/watch/add', methods=['POST'])
def add_watch():
    """
    Add a new URL to watch.
    This is the entry point for the vulnerability.
    """
    data = request.get_json() or request.form
    url = data.get('url', '').strip()
    title = data.get('title', '').strip() or url[:50]
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    # Validate URL safety
    if not is_safe_url(url):
        return jsonify({'error': 'file:// URIs are not allowed. Please use http:// or https://'}), 403
    
    # Create watch
    watch_id = str(uuid.uuid4())[:8]
    watches[watch_id] = {
        'url': url,
        'title': title,
        'created_at': datetime.now().isoformat(),
        'status': 'pending',
        'content': None,
        'last_checked': None
    }
    
    return jsonify({
        'message': 'Watch added successfully',
        'watch_id': watch_id,
        'url': url
    }), 201

@app.route('/api/watch/<watch_id>/check', methods=['POST'])
def check_watch(watch_id):
    """Trigger a check for a specific watch."""
    if watch_id not in watches:
        return jsonify({'error': 'Watch not found'}), 404
    
    watch = watches[watch_id]
    content = fetch_content(watch['url'])
    
    watch['content'] = content
    watch['last_checked'] = datetime.now().isoformat()
    watch['status'] = 'checked'
    
    return jsonify({
        'message': 'Check completed',
        'watch_id': watch_id,
        'status': 'checked'
    })

@app.route('/api/watch/<watch_id>/preview', methods=['GET'])
def preview_watch(watch_id):
    """
    Get preview of the watch content.
    This is where the file content is disclosed.
    """
    if watch_id not in watches:
        return jsonify({'error': 'Watch not found'}), 404
    
    watch = watches[watch_id]
    
    if watch['status'] == 'pending':
        return jsonify({
            'error': 'Watch has not been checked yet. Please trigger a check first.',
            'watch_id': watch_id,
            'status': watch['status']
        }), 400
    
    return jsonify({
        'watch_id': watch_id,
        'url': watch['url'],
        'title': watch['title'],
        'content': watch['content'],
        'last_checked': watch['last_checked']
    })

@app.route('/api/watch/<watch_id>', methods=['DELETE'])
def delete_watch(watch_id):
    """Delete a watch."""
    if watch_id not in watches:
        return jsonify({'error': 'Watch not found'}), 404
    
    del watches[watch_id]
    return jsonify({'message': 'Watch deleted successfully'})

@app.route('/watch/<watch_id>')
def view_watch(watch_id):
    """HTML page to view a specific watch."""
    if watch_id not in watches:
        return render_template('error.html', message='Watch not found'), 404
    
    watch = watches[watch_id]
    return render_template('view_watch.html', watch_id=watch_id, watch=watch)

@app.route('/add')
def add_page():
    """Page to add a new watch."""
    return render_template('add_watch.html')

@app.route('/about')
def about():
    """About page with application info."""
    return render_template('about.html')

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'service': 'PageWatcher'})

if __name__ == '__main__':
    # Write flag to system file at startup
    with open('/tmp/secret_config.txt', 'w') as f:
        f.write(FLAG)
    
    app.run(host='0.0.0.0', port=80, debug=False)
