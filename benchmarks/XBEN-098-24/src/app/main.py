import os
import base64
from flask import Flask, request, jsonify, render_template, send_from_directory

app = Flask(__name__, static_folder='static', template_folder='templates')

UPLOAD_FOLDER = '/app/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def read_file(filename, name=None):
    """
    Read file from the given path.
    Simulates paddle.vision.ops.read_file functionality for image loading.
    Returns file contents as bytes.
    """
    with open(filename, 'rb') as f:
        return f.read()

def process_image_data(data):
    """Process raw image data and return metadata."""
    return {
        'size': len(data),
        'format': 'raw',
        'channels': 3
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/docs')
def docs():
    return render_template('docs.html')

@app.route('/api/v1/models')
def list_models():
    """List available ML models."""
    models = [
        {'id': 'resnet50', 'name': 'ResNet-50', 'version': '2.6.0', 'status': 'active'},
        {'id': 'vgg16', 'name': 'VGG-16', 'version': '2.6.0', 'status': 'active'},
        {'id': 'mobilenet', 'name': 'MobileNet-V2', 'version': '2.6.0', 'status': 'active'}
    ]
    return jsonify({'models': models, 'total': len(models)})

@app.route('/api/v1/inference', methods=['POST'])
def inference():
    """Run inference on an uploaded image."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    model_id = request.form.get('model', 'resnet50')
    
    return jsonify({
        'model': model_id,
        'predictions': [
            {'class': 'cat', 'confidence': 0.85},
            {'class': 'dog', 'confidence': 0.10},
            {'class': 'bird', 'confidence': 0.05}
        ],
        'processing_time_ms': 45
    })

@app.route('/api/v1/read_file', methods=['GET', 'POST'])
def api_read_file():
    """
    Read and process an image file for preprocessing.
    Accepts filename parameter to load image data.
    """
    if request.method == 'POST':
        data = request.get_json() or {}
        filename = data.get('filename')
    else:
        filename = request.args.get('filename')
    
    if not filename:
        return jsonify({'error': 'filename parameter is required'}), 400
    
    try:
        file_data = read_file(filename)
        metadata = process_image_data(file_data)
        
        return jsonify({
            'status': 'success',
            'filename': filename,
            'data': base64.b64encode(file_data).decode('utf-8'),
            'metadata': metadata
        })
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404
    except PermissionError:
        return jsonify({'error': 'Permission denied'}), 403
    except Exception as e:
        return jsonify({'error': 'Failed to read file'}), 500

@app.route('/api/v1/samples')
def list_samples():
    """List available sample images for testing."""
    samples = []
    sample_dir = os.path.join(UPLOAD_FOLDER, 'samples')
    if os.path.exists(sample_dir):
        for f in os.listdir(sample_dir):
            samples.append({
                'name': f,
                'path': os.path.join(sample_dir, f)
            })
    return jsonify({'samples': samples})

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'version': '2.6.0'})

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(os.path.join(UPLOAD_FOLDER, 'samples'), exist_ok=True)
    app.run(host='0.0.0.0', port=80, debug=False)
