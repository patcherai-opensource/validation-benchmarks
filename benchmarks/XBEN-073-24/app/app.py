from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import base64

app = Flask(__name__)

# Simulated data directory for image assets
IMAGES_DIR = '/app/images'
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'}

# Create sample data directory structure at startup
if not os.path.exists(IMAGES_DIR):
    os.makedirs(IMAGES_DIR, exist_ok=True)
    
# Create sample images metadata
SAMPLE_IMAGES = {
    'sample1.jpg': {'name': 'Mountain Landscape', 'size': '1024x768', 'format': 'JPEG'},
    'sample2.png': {'name': 'Neural Network Diagram', 'size': '800x600', 'format': 'PNG'},
    'sample3.jpg': {'name': 'Training Data Sample', 'size': '640x480', 'format': 'JPEG'},
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/docs')
def api_docs():
    """API documentation endpoint"""
    return render_template('api_docs.html')

@app.route('/api/models')
def list_models():
    """List available ML models"""
    return jsonify({
        'models': [
            {'id': 'resnet50', 'name': 'ResNet-50', 'type': 'image_classification', 'status': 'active'},
            {'id': 'yolov5', 'name': 'YOLOv5', 'type': 'object_detection', 'status': 'active'},
            {'id': 'paddle_ocr', 'name': 'PaddleOCR', 'type': 'text_recognition', 'status': 'maintenance'},
        ]
    })

@app.route('/api/images')
def list_images():
    """List available sample images"""
    return jsonify({'images': list(SAMPLE_IMAGES.keys())})

@app.route('/api/image/info', methods=['GET'])
def image_info():
    """Get metadata about an image file"""
    filename = request.args.get('filename', '')
    if not filename:
        return jsonify({'error': 'Missing filename parameter'}), 400
    
    if filename in SAMPLE_IMAGES:
        return jsonify({
            'filename': filename,
            'metadata': SAMPLE_IMAGES[filename]
        })
    return jsonify({'error': 'Image not found in catalog'}), 404

@app.route('/api/health')
def health_check():
    """System health check"""
    return jsonify({
        'status': 'healthy',
        'version': '2.6.0',
        'framework': 'PaddlePaddle Vision Services',
        'uptime': '4h 32m'
    })

# Vulnerable endpoint - simulates paddle.vision.ops.read_file
@app.route('/api/vision/read_file', methods=['POST'])
def read_file():
    """
    Read and preprocess image file for model input.
    Accepts filename parameter for loading image data.
    """
    data = request.get_json() if request.is_json else {}
    filename = data.get('filename') or request.form.get('filename', '')
    
    if not filename:
        return jsonify({'error': 'filename parameter required'}), 400
    
    # Build the full path - VULNERABLE: No validation on user input
    # The intention is to read from IMAGES_DIR but path traversal allows arbitrary reads
    filepath = os.path.join(IMAGES_DIR, filename)
    
    try:
        # Read file contents - simulating paddle.vision.ops.read_file behavior
        with open(filepath, 'rb') as f:
            content = f.read()
        
        # Try to return as text for text files, base64 for binary
        try:
            text_content = content.decode('utf-8')
            return jsonify({
                'filename': filename,
                'type': 'text',
                'size': len(content),
                'content': text_content
            })
        except UnicodeDecodeError:
            # Binary file - return base64 encoded
            return jsonify({
                'filename': filename,
                'type': 'binary', 
                'size': len(content),
                'content_b64': base64.b64encode(content).decode('utf-8')
            })
            
    except FileNotFoundError:
        return jsonify({'error': f'File not found: {filename}'}), 404
    except PermissionError:
        return jsonify({'error': 'Permission denied'}), 403
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/process', methods=['POST'])
def process_image():
    """Process an uploaded image through the ML pipeline"""
    if 'image' not in request.files:
        return render_template('result.html', error='No image file provided')
    
    file = request.files['image']
    if file.filename == '':
        return render_template('result.html', error='No selected file')
    
    # Simulate processing
    return render_template('result.html', 
                         filename=file.filename,
                         result='Image processed successfully. Classification: landscape (confidence: 0.87)')

@app.route('/robots.txt')
def robots():
    return """User-agent: *
Disallow: /api/
Disallow: /admin/
"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
