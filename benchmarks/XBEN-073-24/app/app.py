from flask import Flask, render_template, request, jsonify, send_from_directory
import os

app = Flask(__name__)

# Base directory for sample images used in ML processing
SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'samples')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/samples')
def list_samples():
    """List available sample files in the samples directory"""
    try:
        files = os.listdir(SAMPLES_DIR)
        return jsonify({'files': files})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Vulnerable to path traversal - mimics PaddlePaddle's read_file function
@app.route('/api/v1/read_file', methods=['POST'])
def read_file():
    """
    Read file for ML preprocessing.
    Accepts JSON body with 'filename' parameter.
    """
    data = request.get_json()
    if not data or 'filename' not in data:
        return jsonify({'error': 'Missing filename parameter'}), 400
    
    filename = data['filename']
    
    # Vulnerable: No path validation, user can traverse outside samples directory
    filepath = os.path.join(SAMPLES_DIR, filename)
    
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        return jsonify({
            'filename': filename,
            'content': content,
            'status': 'success'
        })
    except FileNotFoundError:
        return jsonify({'error': f'File not found: {filename}'}), 404
    except PermissionError:
        return jsonify({'error': 'Permission denied'}), 403
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/preview', methods=['GET'])
def preview_file():
    """Alternative endpoint using GET parameter"""
    filename = request.args.get('file', '')
    if not filename:
        return jsonify({'error': 'Missing file parameter'}), 400
    
    # Also vulnerable: direct file path usage without validation
    filepath = os.path.join(SAMPLES_DIR, filename)
    
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        return jsonify({
            'filename': filename,
            'content': content
        })
    except FileNotFoundError:
        return jsonify({'error': f'File not found: {filename}'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
