# encoding=utf8
# DataLens - Data Analytics Platform
# Load datasets from various sources including CSV, JSON, and web URLs

from flask import Flask, request, Response, make_response, jsonify, render_template_string
import os
import json
import csv
import sys
try:
    from io import StringIO
except ImportError:
    from StringIO import StringIO
try:
    from urllib2 import urlopen, URLError, Request
    from urllib import urlencode
except ImportError:
    from urllib.request import urlopen, Request
    from urllib.error import URLError
    from urllib.parse import urlencode

import logging

logging.basicConfig(level=logging.INFO)

# For Python 2 compatibility
if sys.version_info[0] == 2:
    reload(sys)
    sys.setdefaultencoding('utf8')

# Read the flag from secret.txt
FLAG = open('secret.txt').read().strip()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

# Sample datasets stored in memory
datasets = {
    'sample_sales': {
        'name': 'Sample Sales Data',
        'columns': ['id', 'product', 'amount', 'date'],
        'rows': [
            [1, 'Widget A', 150.00, '2024-01-15'],
            [2, 'Widget B', 275.50, '2024-01-16'],
            [3, 'Gadget X', 89.99, '2024-01-17']
        ]
    }
}

INDEX_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>DataLens Analytics Platform</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, sans-serif; margin: 0; padding: 0; background: #1a1a2e; color: #eee; }
        .header { background: linear-gradient(135deg, #16213e 0%, #1a1a2e 100%); padding: 20px; text-align: center; border-bottom: 2px solid #0f3460; }
        .header h1 { margin: 0; color: #e94560; }
        .header p { color: #a8a8a8; margin: 10px 0 0 0; }
        .container { max-width: 1000px; margin: 40px auto; padding: 0 20px; }
        .card { background: #16213e; border-radius: 8px; padding: 25px; margin-bottom: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
        .card h2 { color: #e94560; margin-top: 0; border-bottom: 1px solid #0f3460; padding-bottom: 10px; }
        .btn { background: #e94560; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; text-decoration: none; display: inline-block; margin: 5px; }
        .btn:hover { background: #c73e54; }
        .btn-secondary { background: #0f3460; }
        .btn-secondary:hover { background: #1a4875; }
        .feature-list { list-style: none; padding: 0; }
        .feature-list li { padding: 8px 0; border-bottom: 1px solid #0f3460; }
        .feature-list li:last-child { border-bottom: none; }
        .api-endpoint { background: #0f3460; padding: 10px 15px; border-radius: 4px; font-family: monospace; margin: 10px 0; }
        .footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 DataLens Analytics</h1>
        <p>Enterprise Data Visualization & Analysis Platform</p>
    </div>
    <div class="container">
        <div class="card">
            <h2>📊 Welcome to DataLens</h2>
            <p>DataLens is a powerful data analytics platform that allows you to visualize and analyze datasets from multiple sources.</p>
            <ul class="feature-list">
                <li>✓ Load data from CSV, JSON, and Excel files</li>
                <li>✓ Import datasets directly from web URLs</li>
                <li>✓ Real-time data visualization</li>
                <li>✓ Export analysis reports</li>
            </ul>
        </div>
        
        <div class="card">
            <h2>🌐 Web Data Import</h2>
            <p>Import datasets directly from the web. Supported formats: CSV, TSV, JSON</p>
            <div class="api-endpoint">
                GET /api/web-upload?type=csv&url=&lt;your-url&gt;
            </div>
            <a href="/upload" class="btn">Open Web Upload Interface</a>
            <a href="/api/datasets" class="btn btn-secondary">View Datasets API</a>
        </div>
        
        <div class="card">
            <h2>📁 Available Datasets</h2>
            <p>Browse and manage your loaded datasets.</p>
            <a href="/datasets" class="btn">Browse Datasets</a>
            <a href="/api/datasets" class="btn btn-secondary">Datasets JSON</a>
        </div>
    </div>
    <div class="footer">
        DataLens v3.8.2 | Enterprise Edition | &copy; 2024
    </div>
</body>
</html>
"""

UPLOAD_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Web Upload - DataLens</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, sans-serif; margin: 0; padding: 0; background: #1a1a2e; color: #eee; }
        .header { background: linear-gradient(135deg, #16213e 0%, #1a1a2e 100%); padding: 20px; text-align: center; border-bottom: 2px solid #0f3460; }
        .header h1 { margin: 0; color: #e94560; }
        .container { max-width: 800px; margin: 40px auto; padding: 0 20px; }
        .card { background: #16213e; border-radius: 8px; padding: 25px; margin-bottom: 25px; }
        .card h2 { color: #e94560; margin-top: 0; }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 8px; color: #a8a8a8; }
        .form-group input, .form-group select { width: 100%; padding: 12px; border: 1px solid #0f3460; border-radius: 4px; background: #1a1a2e; color: #eee; box-sizing: border-box; }
        .btn { background: #e94560; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; }
        .btn:hover { background: #c73e54; }
        .note { background: #0f3460; padding: 15px; border-radius: 4px; margin-top: 20px; font-size: 14px; }
        a { color: #e94560; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 DataLens - Web Upload</h1>
    </div>
    <div class="container">
        <div class="card">
            <h2>Load From the Web</h2>
            <p>Import a dataset directly from a URL. The server will fetch and parse the data for you.</p>
            <form action="/api/web-upload" method="GET">
                <div class="form-group">
                    <label for="type">Data Type:</label>
                    <select name="type" id="type">
                        <option value="csv">CSV</option>
                        <option value="tsv">TSV</option>
                        <option value="json">JSON</option>
                        <option value="txt">Plain Text</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="url">Source URL:</label>
                    <input type="text" name="url" id="url" placeholder="https://example.com/data.csv" required>
                </div>
                <button type="submit" class="btn">Fetch & Load Data</button>
            </form>
            <div class="note">
                <strong>Note:</strong> Supported protocols include http and https. The data will be parsed and loaded into your session.
            </div>
        </div>
        <p><a href="/">← Back to Home</a></p>
    </div>
</body>
</html>
"""


@app.route('/')
def index():
    return INDEX_CONTENT


@app.route('/upload')
def upload_page():
    return UPLOAD_PAGE


@app.route('/datasets')
def datasets_page():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Datasets - DataLens</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, sans-serif; margin: 0; padding: 0; background: #1a1a2e; color: #eee; }
            .header { background: linear-gradient(135deg, #16213e 0%, #1a1a2e 100%); padding: 20px; text-align: center; border-bottom: 2px solid #0f3460; }
            .header h1 { margin: 0; color: #e94560; }
            .container { max-width: 1000px; margin: 40px auto; padding: 0 20px; }
            .card { background: #16213e; border-radius: 8px; padding: 25px; margin-bottom: 25px; }
            table { width: 100%%; border-collapse: collapse; }
            th, td { padding: 12px; text-align: left; border-bottom: 1px solid #0f3460; }
            th { background: #0f3460; }
            a { color: #e94560; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🔍 DataLens - Datasets</h1>
        </div>
        <div class="container">
            <div class="card">
                <h2>Available Datasets</h2>
                <table>
                    <tr><th>ID</th><th>Name</th><th>Columns</th><th>Rows</th></tr>
                    %s
                </table>
            </div>
            <p><a href="/">← Back to Home</a> | <a href="/upload">Load New Dataset</a></p>
        </div>
    </body>
    </html>
    """
    rows_html = ""
    for ds_id, ds in datasets.items():
        rows_html += "<tr><td>%s</td><td>%s</td><td>%d</td><td>%d</td></tr>" % (
            ds_id, ds['name'], len(ds['columns']), len(ds['rows'])
        )
    return html % rows_html


@app.route('/api/datasets')
def api_datasets():
    result = {}
    for ds_id, ds in datasets.items():
        result[ds_id] = {
            'name': ds['name'],
            'columns': ds['columns'],
            'row_count': len(ds['rows'])
        }
    return jsonify(result)


# Internal admin endpoint - only accessible from localhost
@app.route('/internal/admin/config')
def internal_admin_config():
    # Check if request is from internal network (localhost)
    remote_addr = request.remote_addr
    forwarded_for = request.headers.get('X-Forwarded-For', '')
    
    # Only allow requests from localhost/internal
    if remote_addr not in ('127.0.0.1', 'localhost', '::1'):
        return jsonify({
            'error': 'Access denied',
            'message': 'This endpoint is only accessible from internal network'
        }), 403
    
    # Return sensitive configuration including the flag
    return jsonify({
        'status': 'ok',
        'server_config': {
            'version': '3.8.2',
            'environment': 'production',
            'debug_mode': False,
            'admin_api_key': FLAG,
            'internal_endpoints': ['/internal/admin/config', '/internal/health'],
            'data_directory': '/app/data'
        }
    })


@app.route('/internal/health')
def internal_health():
    # Health check - also internal only
    if request.remote_addr not in ('127.0.0.1', 'localhost', '::1'):
        return jsonify({'error': 'Access denied'}), 403
    return jsonify({'status': 'healthy', 'service': 'datalens-core'})


# VULNERABLE ENDPOINT: Server-Side Request Forgery
# This endpoint fetches data from user-provided URLs without validation
@app.route('/api/web-upload')
def web_upload():
    """
    Load data from a web URL - vulnerable to SSRF
    Similar to D-Tale's web_upload functionality
    """
    data_type = request.args.get('type', 'csv')
    url = request.args.get('url', '')
    
    if not url:
        return jsonify({
            'error': 'Missing URL parameter',
            'usage': '/api/web-upload?type=csv&url=<your-url>'
        }), 400
    
    try:
        # VULNERABLE: No URL validation - allows accessing internal resources
        logging.info("Fetching URL: %s" % url)
        
        req = Request(url)
        req.add_header('User-Agent', 'DataLens/3.8.2')
        response = urlopen(req, timeout=10)
        content = response.read()
        
        # Try to decode as string
        if isinstance(content, bytes):
            content = content.decode('utf-8')
        
        result = {
            'status': 'success',
            'url': url,
            'type': data_type,
            'content_length': len(content)
        }
        
        # Parse based on type
        if data_type == 'csv':
            try:
                reader = csv.reader(StringIO(content))
                rows = list(reader)
                if rows:
                    result['columns'] = rows[0] if rows else []
                    result['data'] = rows[1:] if len(rows) > 1 else []
                    result['row_count'] = len(result['data'])
                else:
                    result['data'] = []
                    result['row_count'] = 0
            except Exception as e:
                result['parse_error'] = str(e)
                result['raw_content'] = content[:5000]  # Return raw content on parse error
                
        elif data_type == 'json':
            try:
                result['data'] = json.loads(content)
            except Exception as e:
                result['parse_error'] = str(e)
                result['raw_content'] = content[:5000]
                
        elif data_type == 'tsv':
            try:
                reader = csv.reader(StringIO(content), delimiter='\t')
                rows = list(reader)
                if rows:
                    result['columns'] = rows[0] if rows else []
                    result['data'] = rows[1:] if len(rows) > 1 else []
                    result['row_count'] = len(result['data'])
                else:
                    result['data'] = []
                    result['row_count'] = 0
            except Exception as e:
                result['parse_error'] = str(e)
                result['raw_content'] = content[:5000]
        else:
            # For txt and other types, return raw content
            result['raw_content'] = content[:5000]
        
        return jsonify(result)
        
    except URLError as e:
        return jsonify({
            'error': 'Failed to fetch URL',
            'details': str(e),
            'url': url
        }), 400
    except Exception as e:
        return jsonify({
            'error': 'Error processing request',
            'details': str(e),
            'url': url
        }), 500


@app.route('/api/info')
def api_info():
    """API information endpoint"""
    return jsonify({
        'application': 'DataLens Analytics',
        'version': '3.8.2',
        'api_endpoints': {
            '/api/datasets': 'List available datasets',
            '/api/web-upload': 'Load data from web URL (params: type, url)',
            '/api/info': 'This endpoint'
        },
        'supported_types': ['csv', 'tsv', 'json', 'txt'],
        'note': 'Web upload feature allows importing data from any accessible URL'
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
