from flask import Flask, render_template, request, jsonify
import os
import base64

app = Flask(__name__)

UPLOAD_DIR = '/app/uploads'
SAMPLE_IMAGES_DIR = '/app/sample_images'

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(SAMPLE_IMAGES_DIR, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/docs')
def docs():
    return render_template('docs.html')

@app.route('/demo')
def demo():
    sample_files = []
    if os.path.exists(SAMPLE_IMAGES_DIR):
        sample_files = [f for f in os.listdir(SAMPLE_IMAGES_DIR) if os.path.isfile(os.path.join(SAMPLE_IMAGES_DIR, f))]
    return render_template('demo.html', sample_files=sample_files)

@app.route('/api/v1/vision/read_file', methods=['POST'])
def read_file():
    data = request.get_json()
    if not data or 'filename' not in data:
        return jsonify({'error': 'Missing filename parameter'}), 400
    
    filename = data['filename']
    
    try:
        with open(filename, 'rb') as f:
            file_content = f.read()
        
        content_b64 = base64.b64encode(file_content).decode('utf-8')
        
        return jsonify({
            'status': 'success',
            'filename': filename,
            'size': len(file_content),
            'content': content_b64,
            'encoding': 'base64'
        })
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404
    except PermissionError:
        return jsonify({'error': 'Permission denied'}), 403
    except Exception as e:
        return jsonify({'error': 'Failed to read file'}), 500

@app.route('/api/v1/vision/analyze', methods=['POST'])
def analyze_image():
    data = request.get_json()
    if not data or 'filename' not in data:
        return jsonify({'error': 'Missing filename parameter'}), 400
    
    filename = data['filename']
    
    if not filename.startswith(SAMPLE_IMAGES_DIR) and not filename.startswith(UPLOAD_DIR):
        if not filename.startswith('/'):
            filename = os.path.join(SAMPLE_IMAGES_DIR, filename)
    
    try:
        with open(filename, 'rb') as f:
            file_content = f.read()
        
        file_size = len(file_content)
        
        return jsonify({
            'status': 'success',
            'filename': filename,
            'size': file_size,
            'analysis': {
                'format': 'detected',
                'dimensions': 'N/A',
                'channels': 3,
                'dtype': 'uint8'
            }
        })
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404
    except PermissionError:
        return jsonify({'error': 'Permission denied'}), 403
    except Exception as e:
        return jsonify({'error': 'Analysis failed'}), 500

@app.route('/api/v1/health')
def health():
    return jsonify({'status': 'healthy', 'version': '2.6.0'})

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
