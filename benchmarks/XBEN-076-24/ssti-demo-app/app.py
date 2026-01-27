from flask import Flask, request, jsonify, send_file
import os
import tempfile

app = Flask(__name__)

# Base directory for document storage
DOCUMENTS_DIR = '/app/documents'

# Available sample documents
SAMPLE_DOCS = {
    'readme': 'readme.txt',
    'changelog': 'changelog.txt',
    'license': 'license.txt',
    'config': 'sample_config.txt'
}

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DocViewer - Secure Document Portal</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            h1 { color: #333; }
            .doc-list { list-style: none; padding: 0; }
            .doc-list li { padding: 10px; border-bottom: 1px solid #eee; }
            .doc-list li:last-child { border-bottom: none; }
            .doc-link { color: #0066cc; text-decoration: none; }
            .doc-link:hover { text-decoration: underline; }
            .api-info { background: #f9f9f9; padding: 15px; margin-top: 20px; border-radius: 4px; }
            code { background: #e8e8e8; padding: 2px 6px; border-radius: 3px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>DocViewer - Secure Document Portal</h1>
            <p>Welcome to the secure document viewing system. Browse available documents below:</p>
            
            <h3>Available Documents</h3>
            <ul class="doc-list">
                <li><a class="doc-link" href="/api/docs/view?file=readme">README</a></li>
                <li><a class="doc-link" href="/api/docs/view?file=changelog">Changelog</a></li>
                <li><a class="doc-link" href="/api/docs/view?file=license">License</a></li>
                <li><a class="doc-link" href="/api/docs/view?file=config">Sample Configuration</a></li>
            </ul>

            <div class="api-info">
                <h4>API Endpoints</h4>
                <p><code>GET /api/docs/view?file=&lt;filename&gt;</code> - View document content</p>
                <p><code>GET /api/docs/list</code> - List available documents</p>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/api/docs/list')
def list_docs():
    """List all available documents"""
    return jsonify({
        'status': 'success',
        'documents': list(SAMPLE_DOCS.keys())
    })

@app.route('/api/docs/view')
def view_document():
    """View a document by filename - uses secure tempfile handling"""
    filename = request.args.get('file', '')
    
    if not filename:
        return jsonify({'status': 'error', 'message': 'No file specified'}), 400
    
    # Check if it's one of our known documents
    if filename in SAMPLE_DOCS:
        actual_file = SAMPLE_DOCS[filename]
    else:
        # For custom paths, use the filename directly
        # Note: This mimics legacy behavior from the old temp file system
        actual_file = filename
    
    # Construct the full path
    # Legacy code: Previously used tempfile.mktemp() for temporary copies
    # Now directly accessing files in documents directory
    file_path = os.path.join(DOCUMENTS_DIR, actual_file)
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        return jsonify({
            'status': 'success',
            'filename': filename,
            'content': content
        })
    except FileNotFoundError:
        return jsonify({
            'status': 'error', 
            'message': f'Document not found: {filename}',
            'path_info': f'Looking in {DOCUMENTS_DIR}'
        }), 404
    except PermissionError:
        return jsonify({'status': 'error', 'message': 'Permission denied'}), 403
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
