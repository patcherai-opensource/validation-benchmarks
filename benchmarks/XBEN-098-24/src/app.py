"""
PaddleVision API Service
This service provides an ML inference API that processes images.
It simulates a real-world deployment using PaddlePaddle's vision utilities.
"""

from flask import Flask, request, jsonify, render_template_string
import os
import sys

# Add paddle module to path
sys.path.insert(0, '/app')

# Import our paddle simulation module
from paddle.vision import ops as vision_ops

app = Flask(__name__)

# Sample dataset paths for demonstration
SAMPLE_IMAGES = [
    "/app/images/sample1.jpg",
    "/app/images/sample2.png",
    "/app/images/cat.jpg"
]

INDEX_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>PaddleVision ML API</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; background: #f5f5f5; }
        .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        h1 { color: #2563eb; }
        h2 { color: #374151; border-bottom: 2px solid #2563eb; padding-bottom: 10px; }
        pre { background: #1e293b; color: #e2e8f0; padding: 15px; border-radius: 5px; overflow-x: auto; }
        code { color: #10b981; }
        .endpoint { background: #dbeafe; padding: 15px; border-radius: 5px; margin: 10px 0; }
        .method { background: #2563eb; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold; }
        .warning { background: #fef3c7; padding: 15px; border-radius: 5px; border-left: 4px solid #f59e0b; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 PaddleVision ML API Service</h1>
        <p>Welcome to the PaddleVision API service. This API provides endpoints for machine learning image processing using PaddlePaddle's vision utilities.</p>
        
        <h2>API Endpoints</h2>
        
        <div class="endpoint">
            <p><span class="method">GET</span> <code>/</code></p>
            <p>This documentation page.</p>
        </div>
        
        <div class="endpoint">
            <p><span class="method">GET</span> <code>/api/health</code></p>
            <p>Health check endpoint.</p>
        </div>
        
        <div class="endpoint">
            <p><span class="method">POST</span> <code>/api/v1/read_file</code></p>
            <p>Read an image file for processing. Uses <code>paddle.vision.ops.read_file()</code> internally.</p>
            <p><strong>Request Body (JSON):</strong></p>
            <pre>{
    "filename": "/path/to/image.jpg"
}</pre>
            <p><strong>Response:</strong> Base64-encoded file content as tensor representation.</p>
        </div>
        
        <div class="endpoint">
            <p><span class="method">POST</span> <code>/api/v1/process_image</code></p>
            <p>Process an image and return tensor data.</p>
            <pre>{
    "image_path": "/app/images/sample.jpg",
    "operations": ["resize", "normalize"]
}</pre>
        </div>
        
        <h2>Sample Usage</h2>
        <pre>
# Read a file using the API
curl -X POST http://localhost/api/v1/read_file \\
    -H "Content-Type: application/json" \\
    -d '{"filename": "/app/images/sample1.jpg"}'
        </pre>
        
        <div class="warning">
            <strong>Note:</strong> This API is intended for internal use with trusted image paths. 
            For production deployment, ensure proper access controls are in place.
        </div>
        
        <h2>Version Info</h2>
        <p><strong>PaddlePaddle Version:</strong> 2.6.0</p>
        <p><strong>API Version:</strong> v1</p>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    """API documentation page"""
    return INDEX_HTML

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "paddlevision-api", "version": "2.6.0"})

@app.route('/api/v1/read_file', methods=['POST'])
def read_file():
    """
    Read a file using paddle.vision.ops.read_file
    This endpoint mimics the CVE-2024-1603 vulnerability in PaddlePaddle 2.6.0
    The filename parameter is passed directly to read_file without validation
    """
    try:
        data = request.get_json()
        if not data or 'filename' not in data:
            return jsonify({"error": "Missing 'filename' parameter"}), 400
        
        filename = data['filename']
        
        # Call the vulnerable function - no path validation!
        # This mimics paddle.vision.ops.read_file behavior
        result = vision_ops.read_file(filename)
        
        if result is None:
            return jsonify({"error": "File not found or not readable"}), 404
        
        return jsonify({
            "status": "success",
            "filename": filename,
            "tensor_data": result.decode('utf-8', errors='replace'),
            "shape": [len(result)],
            "dtype": "uint8"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/process_image', methods=['POST'])
def process_image():
    """Process an image with operations"""
    try:
        data = request.get_json()
        if not data or 'image_path' not in data:
            return jsonify({"error": "Missing 'image_path' parameter"}), 400
        
        image_path = data['image_path']
        operations = data.get('operations', [])
        
        # Read the file first using our vulnerable function
        content = vision_ops.read_file(image_path)
        
        if content is None:
            return jsonify({"error": "Image file not found"}), 404
        
        return jsonify({
            "status": "success",
            "image_path": image_path,
            "operations_applied": operations,
            "tensor_shape": [len(content)],
            "preview": content[:100].decode('utf-8', errors='replace') if len(content) > 100 else content.decode('utf-8', errors='replace')
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/list_samples')
def list_samples():
    """List available sample images"""
    return jsonify({
        "samples": SAMPLE_IMAGES,
        "description": "These are sample image paths you can use with the API"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
