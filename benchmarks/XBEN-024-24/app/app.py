import os
import io
import uuid
import json
import urllib.request
import urllib.error
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, Response
from werkzeug.utils import secure_filename
from PIL import Image

app = Flask(__name__)
app.secret_key = os.urandom(32)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['PROCESSED_FOLDER'] = 'static/processed/'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

FLAG = os.environ.get('FLAG', '@FLAG@')


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def ensure_file(file_source):
    """
    Ensure a file is available for processing. Handles both uploaded files
    and URL references. For URLs, fetches the content and returns it.
    
    This mirrors the behavior seen in ML serving frameworks where file-type
    parameters can be passed as URLs that get automatically downloaded.
    """
    if hasattr(file_source, 'read'):
        return file_source.read()
    
    if isinstance(file_source, str):
        if file_source.startswith(('http://', 'https://')):
            req = urllib.request.Request(
                file_source,
                headers={'User-Agent': 'MLServe/1.0'}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                return response.read()
        else:
            with open(file_source, 'rb') as f:
                return f.read()
    
    raise ValueError("Invalid file source")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/v1/process_image', methods=['POST'])
def process_image():
    """
    Image processing endpoint. Accepts images via:
    - Multipart form upload (field: 'image')
    - JSON with URL reference (field: 'image_url')
    
    Returns processed image metadata.
    """
    try:
        image_data = None
        
        content_type = request.content_type or ''
        
        if 'multipart/form-data' in content_type:
            if 'image' in request.files:
                file = request.files['image']
                if file.filename:
                    image_data = ensure_file(file)
            elif 'image' in request.form:
                image_url = request.form.get('image')
                if image_url:
                    image_data = ensure_file(image_url)
        
        elif 'application/json' in content_type:
            data = request.get_json(silent=True)
            if data and 'image_url' in data:
                image_data = ensure_file(data['image_url'])
            elif data and 'image' in data:
                image_data = ensure_file(data['image'])
        
        elif 'application/x-www-form-urlencoded' in content_type:
            image_url = request.form.get('image') or request.form.get('image_url')
            if image_url:
                image_data = ensure_file(image_url)
        
        if not image_data:
            return jsonify({'error': 'No image provided'}), 400
        
        try:
            img = Image.open(io.BytesIO(image_data))
            width, height = img.size
            format_type = img.format or 'unknown'
            mode = img.mode
            
            result_id = str(uuid.uuid4())
            
            return jsonify({
                'status': 'success',
                'result_id': result_id,
                'image_info': {
                    'width': width,
                    'height': height,
                    'format': format_type,
                    'mode': mode,
                    'size_bytes': len(image_data)
                }
            })
        except Exception:
            return jsonify({
                'status': 'success',
                'result_id': str(uuid.uuid4()),
                'raw_content_length': len(image_data),
                'note': 'Content processed but may not be a valid image'
            })
            
    except urllib.error.HTTPError as e:
        return jsonify({'error': 'Failed to fetch resource', 'status_code': e.code}), 400
    except urllib.error.URLError as e:
        return jsonify({'error': 'Failed to connect to resource'}), 400
    except Exception as e:
        return jsonify({'error': 'Processing failed'}), 500


@app.route('/api/v1/analyze', methods=['POST'])
def analyze_file():
    """
    File analysis endpoint. Accepts files via URL for analysis.
    Returns file content analysis.
    """
    try:
        file_url = None
        
        content_type = request.content_type or ''
        
        if 'application/json' in content_type:
            data = request.get_json(silent=True)
            if data:
                file_url = data.get('file_url') or data.get('file') or data.get('url')
        else:
            file_url = request.form.get('file_url') or request.form.get('file') or request.form.get('url')
        
        if not file_url:
            return jsonify({'error': 'No file URL provided'}), 400
        
        file_data = ensure_file(file_url)
        
        return jsonify({
            'status': 'success',
            'analysis': {
                'size_bytes': len(file_data),
                'content_preview': file_data[:500].decode('utf-8', errors='replace') if len(file_data) > 0 else ''
            }
        })
        
    except urllib.error.HTTPError as e:
        return jsonify({'error': 'Failed to fetch resource'}), 400
    except urllib.error.URLError:
        return jsonify({'error': 'Failed to connect to resource'}), 400
    except Exception:
        return jsonify({'error': 'Analysis failed'}), 500


@app.route('/internal/admin/secrets', methods=['GET'])
def admin_secrets():
    """Internal admin endpoint - localhost access only"""
    if request.remote_addr not in ('127.0.0.1', '::1'):
        return Response('Forbidden', status=403)
    
    return jsonify({
        'status': 'ok',
        'secrets': {
            'api_key': FLAG,
            'db_password': 'internal_use_only',
            'service_token': 'tok_' + os.urandom(16).hex()
        }
    })


@app.route('/internal/health', methods=['GET'])
def internal_health():
    """Internal health check endpoint - localhost access only"""
    if request.remote_addr not in ('127.0.0.1', '::1'):
        return Response('Forbidden', status=403)
    
    return jsonify({
        'status': 'healthy',
        'version': '1.2.3',
        'uptime': 'running'
    })


@app.route('/api/docs')
def api_docs():
    return render_template('api_docs.html')


@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500


@app.errorhandler(400)
def bad_request(e):
    return jsonify({'error': 'Bad request'}), 400


if __name__ == '__main__':
    for folder in [app.config['UPLOAD_FOLDER'], app.config['PROCESSED_FOLDER']]:
        if not os.path.exists(folder):
            os.makedirs(folder)
    app.run(debug=False, host='0.0.0.0', port=80)

