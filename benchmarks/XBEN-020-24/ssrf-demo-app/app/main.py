import os
import io
import tempfile
import requests
from pathlib import Path
from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image

app = Flask(__name__, 
            template_folder='../templates',
            static_folder='../static')

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


async def ensure_file(obj):
    """
    Ensures the object is a file-like object. If obj is a URL string,
    downloads the content from that URL.
    """
    if isinstance(obj, str) and (obj.startswith('http://') or obj.startswith('https://')):
        resp = requests.get(obj, timeout=10)
        return io.BytesIO(resp.content)
    return obj


def process_file_input(file_value):
    """
    Process file input which can be either an uploaded file or a URL.
    This mimics BentoML's multipart/JSON serde behavior where file parameters
    can be provided as URLs that get fetched server-side.
    """
    if isinstance(file_value, str):
        if file_value.startswith('http://') or file_value.startswith('https://'):
            resp = requests.get(file_value, timeout=10)
            return io.BytesIO(resp.content)
    return file_value


def analyze_image(image_data):
    """Analyze image and return metadata."""
    try:
        img = Image.open(image_data)
        return {
            'format': img.format,
            'mode': img.mode,
            'size': {'width': img.width, 'height': img.height},
            'info': {k: str(v) for k, v in img.info.items() if isinstance(v, (str, int, float))}
        }
    except Exception as e:
        return {'error': 'Failed to process as image', 'raw_size': image_data.seek(0, 2)}


@app.route('/health')
def health():
    return jsonify({'status': 'healthy'}), 200


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/docs')
def docs():
    return render_template('docs.html')


@app.route('/api/v1/analyze', methods=['POST'])
def analyze_endpoint():
    """
    Endpoint to analyze uploaded images.
    Accepts multipart form data or JSON with file URL.
    """
    result = {}
    
    if request.content_type and 'multipart/form-data' in request.content_type:
        if 'image' in request.files:
            file = request.files['image']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            file_data = io.BytesIO(file.read())
            result = analyze_image(file_data)
        elif 'image' in request.form:
            url_or_path = request.form['image']
            file_data = process_file_input(url_or_path)
            result = analyze_image(file_data)
        else:
            return jsonify({'error': 'No image provided'}), 400
            
    elif request.content_type and 'application/json' in request.content_type:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({'error': 'No image URL provided'}), 400
        file_data = process_file_input(data['image'])
        result = analyze_image(file_data)
    else:
        return jsonify({'error': 'Unsupported content type'}), 415
    
    return jsonify(result)


@app.route('/api/v1/process', methods=['POST'])
def process_endpoint():
    """
    Process and transform images. Accepts file uploads or URLs.
    """
    if request.content_type and 'multipart/form-data' in request.content_type:
        if 'file' in request.files:
            file = request.files['file']
            file_data = io.BytesIO(file.read())
        elif 'file' in request.form:
            file_value = request.form['file']
            file_data = process_file_input(file_value)
        else:
            return jsonify({'error': 'No file provided'}), 400
    elif request.content_type and 'application/json' in request.content_type:
        data = request.get_json()
        if not data or 'file' not in data:
            return jsonify({'error': 'No file provided'}), 400
        file_data = process_file_input(data['file'])
    else:
        return jsonify({'error': 'Unsupported content type'}), 415
    
    try:
        img = Image.open(file_data)
        output = io.BytesIO()
        img.save(output, format='PNG')
        size = output.tell()
        return jsonify({
            'status': 'processed',
            'output_format': 'PNG',
            'output_size': size
        })
    except Exception:
        file_data.seek(0)
        content = file_data.read()
        return jsonify({
            'status': 'processed',
            'content_type': 'raw',
            'size': len(content),
            'preview': content[:500].decode('utf-8', errors='replace') if len(content) > 0 else ''
        })


@app.route('/api/v1/inference', methods=['POST'])
def inference_endpoint():
    """
    Run ML inference on uploaded content.
    Supports both direct file uploads and URL references.
    """
    file_data = None
    
    if request.content_type and 'multipart/form-data' in request.content_type:
        if 'input' in request.files:
            file = request.files['input']
            file_data = io.BytesIO(file.read())
        elif 'input' in request.form:
            input_value = request.form['input']
            file_data = process_file_input(input_value)
        else:
            return jsonify({'error': 'No input provided'}), 400
    elif request.content_type and 'application/json' in request.content_type:
        data = request.get_json()
        if not data or 'input' not in data:
            return jsonify({'error': 'No input provided'}), 400
        file_data = process_file_input(data['input'])
    else:
        return jsonify({'error': 'Unsupported content type'}), 415
    
    try:
        file_data.seek(0)
        content = file_data.read()
        
        return jsonify({
            'inference_result': {
                'status': 'completed',
                'model': 'vision-classifier-v2',
                'input_size': len(content),
                'output': content.decode('utf-8', errors='replace')
            }
        })
    except Exception as e:
        return jsonify({'error': 'Inference failed'}), 500


@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500


@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File too large'}), 413


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
