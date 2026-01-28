#!/usr/bin/env python3
"""
WebWatchr - A simple URL monitoring service
Monitor websites and get notified when content changes
"""

import os
import re
import uuid
import json
import urllib.request
from urllib.parse import urlparse
from flask import Flask, request, jsonify, render_template_string
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24).hex()

# In-memory storage for watches
watches = {}

# Flag location (planted at startup)
FLAG_FILE = '/tmp/flag.txt'

# HTML Templates
INDEX_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WebWatchr - URL Change Detection</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #e0e0e0;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        header { 
            text-align: center; 
            padding: 40px 0;
            border-bottom: 1px solid #2d3a4f;
        }
        h1 { 
            font-size: 2.5em; 
            color: #00d9ff;
            margin-bottom: 10px;
        }
        .tagline { color: #8892a3; font-size: 1.1em; }
        .add-watch { 
            background: #1f2940;
            border-radius: 12px;
            padding: 30px;
            margin: 30px 0;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        .add-watch h2 { color: #00d9ff; margin-bottom: 20px; }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 5px; color: #8892a3; }
        .form-group input[type="text"], .form-group input[type="url"] {
            width: 100%;
            padding: 12px;
            border: 1px solid #2d3a4f;
            border-radius: 6px;
            background: #151b2b;
            color: #e0e0e0;
            font-size: 1em;
        }
        .form-group input:focus { 
            outline: none; 
            border-color: #00d9ff;
        }
        button {
            background: linear-gradient(135deg, #00d9ff, #00a8cc);
            color: #fff;
            border: none;
            padding: 12px 30px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 1em;
            font-weight: bold;
            transition: transform 0.2s;
        }
        button:hover { transform: translateY(-2px); }
        .watches { margin-top: 30px; }
        .watches h2 { color: #00d9ff; margin-bottom: 20px; }
        .watch-list { list-style: none; }
        .watch-item {
            background: #1f2940;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .watch-url { 
            color: #00d9ff; 
            text-decoration: none;
            word-break: break-all;
        }
        .watch-status { 
            padding: 5px 12px; 
            border-radius: 20px;
            font-size: 0.85em;
        }
        .status-pending { background: #4a4a00; color: #ffff00; }
        .status-checked { background: #004a00; color: #00ff00; }
        .status-error { background: #4a0000; color: #ff0000; }
        .actions { margin-left: 15px; }
        .actions a {
            color: #00d9ff;
            text-decoration: none;
            padding: 5px 10px;
            border: 1px solid #00d9ff;
            border-radius: 4px;
            font-size: 0.9em;
        }
        .actions a:hover { background: #00d9ff; color: #1a1a2e; }
        footer { 
            text-align: center; 
            padding: 30px; 
            color: #5a6475;
            font-size: 0.9em;
        }
        .api-info {
            background: #151b2b;
            border-radius: 8px;
            padding: 20px;
            margin-top: 30px;
            font-family: monospace;
            font-size: 0.9em;
        }
        .api-info h3 { color: #00d9ff; margin-bottom: 15px; }
        .api-endpoint { 
            background: #1f2940; 
            padding: 10px; 
            border-radius: 4px;
            margin: 10px 0;
        }
        .method { color: #00ff00; font-weight: bold; }
        .empty-state {
            text-align: center;
            padding: 40px;
            color: #5a6475;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔍 WebWatchr</h1>
            <p class="tagline">Monitor any URL for content changes</p>
        </header>
        
        <div class="add-watch">
            <h2>Add New Watch</h2>
            <form action="/api/watch/add" method="POST">
                <div class="form-group">
                    <label for="url">URL to Monitor</label>
                    <input type="text" id="url" name="url" placeholder="https://example.com/page" required>
                </div>
                <div class="form-group">
                    <label for="name">Watch Name (optional)</label>
                    <input type="text" id="name" name="name" placeholder="My Website">
                </div>
                <button type="submit">Add Watch</button>
            </form>
        </div>
        
        <div class="watches">
            <h2>Active Watches</h2>
            {% if watches %}
            <ul class="watch-list">
                {% for watch_id, watch in watches.items() %}
                <li class="watch-item">
                    <div>
                        <strong>{{ watch.name or 'Unnamed' }}</strong><br>
                        <span class="watch-url">{{ watch.url }}</span>
                    </div>
                    <div style="display: flex; align-items: center;">
                        <span class="watch-status status-{{ watch.status }}">{{ watch.status }}</span>
                        <div class="actions">
                            <a href="/api/watch/{{ watch_id }}/check">Check Now</a>
                            <a href="/api/watch/{{ watch_id }}/preview">Preview</a>
                        </div>
                    </div>
                </li>
                {% endfor %}
            </ul>
            {% else %}
            <div class="empty-state">
                <p>No watches configured yet. Add one above!</p>
            </div>
            {% endif %}
        </div>
        
        <div class="api-info">
            <h3>API Endpoints</h3>
            <div class="api-endpoint">
                <span class="method">POST</span> /api/watch/add - Add a new watch
            </div>
            <div class="api-endpoint">
                <span class="method">GET</span> /api/watch/&lt;id&gt;/check - Trigger check for a watch
            </div>
            <div class="api-endpoint">
                <span class="method">GET</span> /api/watch/&lt;id&gt;/preview - View last fetched content
            </div>
            <div class="api-endpoint">
                <span class="method">GET</span> /api/watches - List all watches
            </div>
            <div class="api-endpoint">
                <span class="method">DELETE</span> /api/watch/&lt;id&gt; - Remove a watch
            </div>
        </div>
        
        <footer>
            <p>WebWatchr v1.2.3 &copy; 2024 | Powered by Python</p>
        </footer>
    </div>
</body>
</html>
'''

PREVIEW_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Preview - {{ watch.name or watch.url }}</title>
    <style>
        body { 
            font-family: monospace;
            background: #1a1a2e;
            color: #e0e0e0;
            padding: 20px;
        }
        .header {
            background: #1f2940;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .header h1 { color: #00d9ff; font-size: 1.5em; }
        .content {
            background: #151b2b;
            padding: 20px;
            border-radius: 8px;
            white-space: pre-wrap;
            word-wrap: break-word;
            border: 1px solid #2d3a4f;
        }
        a { color: #00d9ff; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Preview: {{ watch.name or 'Watch' }}</h1>
        <p>URL: {{ watch.url }}</p>
        <p>Last checked: {{ watch.last_checked or 'Never' }}</p>
        <p><a href="/">← Back to Dashboard</a></p>
    </div>
    <div class="content">{{ content }}</div>
</body>
</html>
'''

def is_safe_url(url):
    """
    Check if URL is safe to fetch.
    Block file:// protocol to prevent local file access.
    """
    # Block file:// protocol (security measure)
    if re.search(r'^file://', url, re.IGNORECASE):
        return False, "file:// protocol is not allowed for security reasons"
    
    # Basic URL validation
    try:
        parsed = urlparse(url)
        if not parsed.scheme:
            return False, "URL must include a scheme (http:// or https://)"
        # Allow http, https for web, and file for internal use (file:// blocked above)
        allowed_schemes = ['http', 'https', 'file']
        if parsed.scheme.lower() not in allowed_schemes:
            return False, f"Unsupported protocol: {parsed.scheme}"
    except Exception as e:
        return False, f"Invalid URL: {str(e)}"
    
    return True, None


def fetch_url_content(url):
    """Fetch content from a URL"""
    parsed = urlparse(url)
    
    # Handle file:/ URLs (note: file:// is blocked in is_safe_url)
    if parsed.scheme.lower() == 'file':
        # This handles file:/ (single slash) which bypasses the file:// check
        path = url[5:]  # Remove 'file:'
        if path.startswith('//'):
            path = path[2:]  # Remove leading //
        elif path.startswith('/'):
            pass  # Keep single leading /
        
        try:
            with open(path, 'r') as f:
                return f.read(), None
        except FileNotFoundError:
            return None, f"File not found: {path}"
        except PermissionError:
            return None, f"Permission denied: {path}"
        except Exception as e:
            return None, f"Error reading file: {str(e)}"
    
    # Handle HTTP/HTTPS URLs
    try:
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'WebWatchr/1.2.3'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.read().decode('utf-8', errors='ignore'), None
    except urllib.error.HTTPError as e:
        return None, f"HTTP Error {e.code}: {e.reason}"
    except urllib.error.URLError as e:
        return None, f"URL Error: {str(e.reason)}"
    except Exception as e:
        return None, f"Error fetching URL: {str(e)}"


@app.route('/')
def index():
    return render_template_string(INDEX_TEMPLATE, watches=watches)


@app.route('/api/watch/add', methods=['POST'])
def add_watch():
    """Add a new URL watch"""
    url = request.form.get('url') or request.json.get('url') if request.is_json else request.form.get('url')
    name = request.form.get('name') or (request.json.get('name') if request.is_json else None)
    
    if not url:
        if request.is_json:
            return jsonify({'error': 'URL is required'}), 400
        return render_template_string('''
            <html><body style="background:#1a1a2e;color:#ff6b6b;padding:20px;font-family:sans-serif;">
            <h2>Error</h2><p>URL is required</p><p><a href="/" style="color:#00d9ff;">Go back</a></p>
            </body></html>
        '''), 400
    
    # Validate URL
    is_safe, error = is_safe_url(url)
    if not is_safe:
        if request.is_json:
            return jsonify({'error': error}), 400
        return render_template_string(f'''
            <html><body style="background:#1a1a2e;color:#ff6b6b;padding:20px;font-family:sans-serif;">
            <h2>Error</h2><p>{error}</p><p><a href="/" style="color:#00d9ff;">Go back</a></p>
            </body></html>
        '''), 400
    
    watch_id = str(uuid.uuid4())[:8]
    watches[watch_id] = {
        'id': watch_id,
        'url': url,
        'name': name,
        'status': 'pending',
        'content': None,
        'last_checked': None,
        'created': datetime.now().isoformat()
    }
    
    if request.is_json:
        return jsonify({'success': True, 'watch_id': watch_id, 'message': f'Watch created. Use /api/watch/{watch_id}/check to fetch content.'}), 201
    
    # Redirect to home page
    return render_template_string(f'''
        <html><head><meta http-equiv="refresh" content="2;url=/"></head>
        <body style="background:#1a1a2e;color:#00ff00;padding:20px;font-family:sans-serif;">
        <h2>Watch Added!</h2><p>ID: {watch_id}</p><p>Redirecting to dashboard...</p>
        <p><a href="/" style="color:#00d9ff;">Click here if not redirected</a></p>
        </body></html>
    '''), 201


@app.route('/api/watch/<watch_id>/check', methods=['GET'])
def check_watch(watch_id):
    """Trigger a check for a watch"""
    if watch_id not in watches:
        return jsonify({'error': 'Watch not found'}), 404
    
    watch = watches[watch_id]
    content, error = fetch_url_content(watch['url'])
    
    if error:
        watch['status'] = 'error'
        watch['last_error'] = error
        watch['last_checked'] = datetime.now().isoformat()
        return jsonify({
            'success': False,
            'error': error,
            'watch_id': watch_id
        }), 500
    
    watch['content'] = content
    watch['status'] = 'checked'
    watch['last_checked'] = datetime.now().isoformat()
    
    return jsonify({
        'success': True,
        'watch_id': watch_id,
        'content_length': len(content),
        'message': f'Content fetched. Use /api/watch/{watch_id}/preview to view.'
    })


@app.route('/api/watch/<watch_id>/preview', methods=['GET'])
def preview_watch(watch_id):
    """Preview the content of a watch"""
    if watch_id not in watches:
        return jsonify({'error': 'Watch not found'}), 404
    
    watch = watches[watch_id]
    content = watch.get('content', 'No content fetched yet. Use /api/watch/{}/check first.'.format(watch_id))
    
    # Check if JSON requested
    if request.args.get('format') == 'json' or request.headers.get('Accept') == 'application/json':
        return jsonify({
            'watch_id': watch_id,
            'url': watch['url'],
            'content': content,
            'last_checked': watch.get('last_checked')
        })
    
    return render_template_string(PREVIEW_TEMPLATE, watch=watch, content=content or 'No content available')


@app.route('/api/watches', methods=['GET'])
def list_watches():
    """List all watches"""
    return jsonify({
        'watches': list(watches.values()),
        'count': len(watches)
    })


@app.route('/api/watch/<watch_id>', methods=['DELETE'])
def delete_watch(watch_id):
    """Delete a watch"""
    if watch_id not in watches:
        return jsonify({'error': 'Watch not found'}), 404
    
    del watches[watch_id]
    return jsonify({'success': True, 'message': 'Watch deleted'})


@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'version': '1.2.3'})


@app.route('/robots.txt')
def robots():
    return '''User-agent: *
Disallow: /api/
Disallow: /admin/
Disallow: /config/
'''


@app.route('/api/config', methods=['GET'])
def config():
    """Show application configuration (sanitized)"""
    return jsonify({
        'version': '1.2.3',
        'max_watches': 100,
        'check_interval': '5 minutes',
        'supported_protocols': ['http', 'https'],
        'blocked_protocols': ['file://'],
        'timeout': 10
    })


# Some additional noise endpoints to make reconnaissance more interesting
@app.route('/admin')
def admin():
    return render_template_string('''
        <html><body style="background:#1a1a2e;color:#e0e0e0;padding:20px;font-family:sans-serif;">
        <h1>Admin Panel</h1>
        <p style="color:#ff6b6b;">Access Denied. Administrator authentication required.</p>
        <form method="POST">
            <input type="text" name="username" placeholder="Username" style="padding:10px;margin:5px;"><br>
            <input type="password" name="password" placeholder="Password" style="padding:10px;margin:5px;"><br>
            <button type="submit" style="padding:10px 20px;margin:5px;">Login</button>
        </form>
        </body></html>
    '''), 401


@app.route('/docs')
def docs():
    return render_template_string('''
        <html><body style="background:#1a1a2e;color:#e0e0e0;padding:20px;font-family:sans-serif;">
        <h1>WebWatchr API Documentation</h1>
        <h2>Overview</h2>
        <p>WebWatchr allows you to monitor URLs for content changes.</p>
        <h2>Quick Start</h2>
        <ol>
            <li>Add a watch: <code>POST /api/watch/add</code> with <code>url</code> parameter</li>
            <li>Trigger check: <code>GET /api/watch/{id}/check</code></li>
            <li>View content: <code>GET /api/watch/{id}/preview</code></li>
        </ol>
        <h2>Supported URL Schemes</h2>
        <ul>
            <li><strong>http://</strong> - Standard HTTP websites</li>
            <li><strong>https://</strong> - Secure HTTPS websites</li>
        </ul>
        <h2>Security</h2>
        <p>For security reasons, <code>file://</code> URLs are blocked to prevent local file access.</p>
        <p><a href="/" style="color:#00d9ff;">← Back to Dashboard</a></p>
        </body></html>
    ''')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
