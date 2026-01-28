import os
import json
import uuid
import hashlib
import urllib.request
import urllib.error
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'ml-inference-secret-2024'
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
app.config['MODEL_FOLDER'] = 'static/models/'

# API Keys for service access
api_keys = {
    'dev_api_key_001': {'user': 'developer', 'tier': 'basic', 'requests': 0},
    'admin_api_key_999': {'user': 'admin', 'tier': 'enterprise', 'requests': 0}
}

# Model registry
models = {
    'image-classifier-v1': {'type': 'classification', 'status': 'active', 'version': '1.0.3'},
    'object-detector-v2': {'type': 'detection', 'status': 'active', 'version': '2.1.0'},
    'sentiment-analyzer': {'type': 'nlp', 'status': 'maintenance', 'version': '0.9.8'},
}

# Inference jobs history
inference_jobs = []

FLAG = os.environ.get('FLAG', '@FLAG@')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def generate_job_id():
    return str(uuid.uuid4())[:8]

def fetch_file_from_url(url):
    """Fetch file from URL - used for remote file processing"""
    try:
        filename = secure_filename(url.split('/')[-1]) or 'downloaded_file'
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        # Fetch the URL and save contents
        response = urllib.request.urlopen(url, timeout=10)
        content = response.read()
        with open(filepath, 'wb') as f:
            f.write(content)
        return filepath, None, content
    except urllib.error.HTTPError as e:
        return None, f'HTTP {e.code}: {e.reason}', None
    except urllib.error.URLError as e:
        return None, f'Connection failed: {e.reason}', None
    except Exception as e:
        return None, f'Error fetching URL: {str(e)}', None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/robots.txt')
def robots():
    return app.send_static_file('robots.txt')

@app.route('/docs')
def docs():
    return render_template('docs.html')

@app.route('/api/v1/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'MLServe Inference Platform',
        'version': '3.2.1'
    })

@app.route('/api/v1/models')
def list_models():
    return jsonify({
        'models': [
            {'name': name, **info} for name, info in models.items()
        ]
    })

@app.route('/api/v1/models/<model_name>')
def get_model(model_name):
    if model_name in models:
        return jsonify({'name': model_name, **models[model_name]})
    return jsonify({'error': 'Model not found'}), 404

@app.route('/api/v1/inference', methods=['POST'])
def inference():
    """
    Run inference on uploaded data.
    Accepts multipart form data or JSON with file URL.
    """
    model_name = request.form.get('model') or request.json.get('model') if request.is_json else request.form.get('model')
    
    if not model_name:
        return jsonify({'error': 'Model name required'}), 400
    
    if model_name not in models:
        return jsonify({'error': f'Model {model_name} not found'}), 404
    
    if models[model_name]['status'] == 'maintenance':
        return jsonify({'error': f'Model {model_name} is under maintenance'}), 503
    
    job_id = generate_job_id()
    
    # Handle file upload via multipart form
    if 'file' in request.files:
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Simulate inference
            result = {
                'job_id': job_id,
                'model': model_name,
                'status': 'completed',
                'predictions': [
                    {'label': 'cat', 'confidence': 0.92},
                    {'label': 'animal', 'confidence': 0.98}
                ]
            }
            inference_jobs.append(result)
            return jsonify(result)
    
    # Handle file URL - fetch remote file for processing
    file_url = request.form.get('file_url')
    if not file_url and request.is_json:
        file_url = request.json.get('file_url')
    
    if file_url:
        # SSRF vulnerability: fetching remote files without validation
        filepath, error, raw_content = fetch_file_from_url(file_url)
        if error:
            return jsonify({'error': f'Failed to fetch file: {error}'}), 400
        
        # Simulate inference
        result = {
            'job_id': job_id,
            'model': model_name,
            'status': 'completed',
            'source': 'remote_url',
            'predictions': [
                {'label': 'dog', 'confidence': 0.87},
                {'label': 'animal', 'confidence': 0.95}
            ]
        }
        
        # Debug: Include raw response for troubleshooting (vulnerability: leaks fetched content)
        if raw_content:
            try:
                result['debug_response'] = raw_content.decode('utf-8', errors='replace')[:2048]
            except:
                pass
        
        inference_jobs.append(result)
        return jsonify(result)
    
    return jsonify({'error': 'No file or file_url provided'}), 400

@app.route('/api/v1/batch', methods=['POST'])
def batch_inference():
    """
    Process multiple files in batch.
    Accepts JSON array of file URLs.
    """
    if not request.is_json:
        return jsonify({'error': 'JSON body required'}), 400
    
    data = request.json
    model_name = data.get('model')
    file_urls = data.get('files', [])
    
    if not model_name:
        return jsonify({'error': 'Model name required'}), 400
    
    if model_name not in models:
        return jsonify({'error': f'Model {model_name} not found'}), 404
    
    if not file_urls:
        return jsonify({'error': 'No files provided'}), 400
    
    results = []
    for url in file_urls[:5]:  # Limit to 5 files
        job_id = generate_job_id()
        # SSRF vulnerability: fetching remote files without validation
        filepath, error, raw_content = fetch_file_from_url(url)
        if error:
            results.append({'job_id': job_id, 'status': 'failed', 'error': error})
        else:
            result_entry = {
                'job_id': job_id,
                'model': model_name,
                'status': 'completed',
                'source': url
            }
            # Debug: Include raw response for troubleshooting
            if raw_content:
                try:
                    result_entry['debug_response'] = raw_content.decode('utf-8', errors='replace')[:2048]
                except:
                    pass
            results.append(result_entry)
    
    return jsonify({'batch_results': results})

@app.route('/api/v1/jobs')
def list_jobs():
    return jsonify({'jobs': inference_jobs[-10:]})  # Last 10 jobs

@app.route('/api/v1/jobs/<job_id>')
def get_job(job_id):
    for job in inference_jobs:
        if job.get('job_id') == job_id:
            return jsonify(job)
    return jsonify({'error': 'Job not found'}), 404

@app.route('/api/v1/metrics')
def metrics():
    return jsonify({
        'total_requests': sum(k['requests'] for k in api_keys.values()),
        'active_models': len([m for m in models.values() if m['status'] == 'active']),
        'total_jobs': len(inference_jobs)
    })

@app.route('/api/v1/config')
def config():
    """Public configuration endpoint"""
    return jsonify({
        'service_name': 'MLServe Inference Platform',
        'version': '3.2.1',
        'environment': 'production',
        'endpoints': {
            'public': ['/api/v1/health', '/api/v1/models', '/api/v1/inference', '/api/v1/batch', '/api/v1/jobs', '/api/v1/metrics'],
            'internal': ['/internal/*']
        },
        'features': {
            'remote_file_fetch': True,
            'batch_processing': True,
            'async_webhooks': True
        }
    })

# Internal admin endpoints - only accessible from localhost
@app.route('/internal/admin/credentials')
def admin_credentials():
    if request.remote_addr != '127.0.0.1':
        return jsonify({'error': 'Access denied - internal endpoint'}), 403
    
    # This endpoint returns the admin API key when accessed from localhost
    return jsonify({
        'admin_key': 'admin_api_key_999',
        'secret_token': FLAG
    })

@app.route('/internal/admin/reset')
def admin_reset():
    if request.remote_addr != '127.0.0.1':
        return jsonify({'error': 'Access denied - internal endpoint'}), 403
    
    # Reset service state
    global inference_jobs
    inference_jobs = []
    return jsonify({'status': 'reset complete'})

@app.route('/internal/health')
def internal_health():
    if request.remote_addr != '127.0.0.1':
        return jsonify({'error': 'Access denied - internal endpoint'}), 403
    return jsonify({'internal_status': 'ok', 'node': 'primary'})

# Webhook endpoint for async processing notifications
@app.route('/api/v1/webhook', methods=['POST'])
def webhook():
    """Receive webhook notifications"""
    if not request.is_json:
        return jsonify({'error': 'JSON body required'}), 400
    
    data = request.json
    callback_url = data.get('callback_url')
    
    if callback_url:
        # Log webhook registration (no SSRF here - just storing)
        return jsonify({'status': 'webhook registered', 'url': callback_url})
    
    return jsonify({'error': 'callback_url required'}), 400

# Legacy endpoint kept for backward compatibility
@app.route('/upload', methods=['GET', 'POST'])
def upload_legacy():
    """Legacy file upload endpoint"""
    if request.method == 'GET':
        return render_template('upload.html')
    
    if 'file' in request.files:
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            return jsonify({'status': 'uploaded', 'filename': filename})
    
    return jsonify({'error': 'No valid file provided'}), 400

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    if not os.path.exists(app.config['MODEL_FOLDER']):
        os.makedirs(app.config['MODEL_FOLDER'])
    app.run(debug=False, host='0.0.0.0', port=80)

