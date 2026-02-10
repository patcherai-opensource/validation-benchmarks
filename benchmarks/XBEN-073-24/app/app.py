from flask import Flask, render_template, request, jsonify
import os
import base64

app = Flask(__name__)

# Simulated ML Vision API - mimicking PaddlePaddle's vision.ops functionality
# This is a simplified ML image processing service

# Storage for uploaded images
UPLOAD_DIR = '/tmp/uploads'
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/v1/vision/info')
def api_info():
    """API documentation endpoint"""
    return jsonify({
        "service": "ML Vision Processing API",
        "version": "2.6.0",
        "endpoints": {
            "/api/v1/vision/read_file": {
                "method": "POST",
                "description": "Read an image file for processing",
                "parameters": {
                    "filename": "Path to the image file"
                }
            },
            "/api/v1/vision/process": {
                "method": "POST", 
                "description": "Process an uploaded image"
            }
        }
    })

# Vulnerable endpoint - mimics paddle.vision.ops.read_file
# CVE-2024-1603: Arbitrary file read via unsanitized filename parameter
@app.route('/api/v1/vision/read_file', methods=['POST'])
def read_file():
    """
    Read file content - simulates paddle.vision.ops.read_file
    This function accepts a filename and returns its content as bytes.
    
    VULNERABLE: No validation or sanitization on filename parameter.
    Allows arbitrary file reads through path traversal.
    """
    data = request.get_json()
    if not data or 'filename' not in data:
        return jsonify({"error": "Missing 'filename' parameter"}), 400
    
    filename = data['filename']
    
    # Vulnerable: Direct file read without path validation
    # This mimics the vulnerable paddle.vision.ops.read_file behavior
    try:
        with open(filename, 'rb') as f:
            content = f.read()
        
        # Return file content as base64 encoded (simulating tensor bytes)
        return jsonify({
            "status": "success",
            "filename": filename,
            "size": len(content),
            "content": base64.b64encode(content).decode('utf-8'),
            "content_type": "tensor_bytes"
        })
    except FileNotFoundError:
        return jsonify({"error": f"File not found: {filename}"}), 404
    except PermissionError:
        return jsonify({"error": f"Permission denied: {filename}"}), 403
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/vision/process', methods=['POST'])
def process_image():
    """Process an uploaded image through the ML pipeline"""
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400
    
    image = request.files['image']
    if image.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    # Save and simulate processing
    filepath = os.path.join(UPLOAD_DIR, os.path.basename(image.filename))
    image.save(filepath)
    
    return jsonify({
        "status": "success",
        "message": "Image processed successfully",
        "filepath": filepath,
        "predictions": [
            {"label": "sample_class", "confidence": 0.95}
        ]
    })

# Alternative endpoint for GET-based file reading (also vulnerable)
@app.route('/api/v1/vision/preview')
def preview_file():
    """Preview file content via GET request"""
    filename = request.args.get('filename')
    if not filename:
        return jsonify({"error": "Missing 'filename' parameter"}), 400
    
    try:
        with open(filename, 'rb') as f:
            content = f.read()
        
        return jsonify({
            "status": "success",
            "filename": filename,
            "content": base64.b64encode(content).decode('utf-8')
        })
    except FileNotFoundError:
        return jsonify({"error": f"File not found: {filename}"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
