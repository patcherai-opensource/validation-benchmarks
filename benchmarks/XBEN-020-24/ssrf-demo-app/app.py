"""
ML Model Inference Service - Image Processing API

This service demonstrates a BentoML-style file upload processing API
that accepts images for ML model inference. Files can be provided either
as direct uploads or as URLs that will be fetched automatically.
"""

from flask import Flask, request, render_template, jsonify
import httpx
import io
import os
from PIL import Image
import tempfile
import json

app = Flask(__name__)

# Simulated model inference function
def process_image(image_data: bytes) -> dict:
    """Process an image through our ML model"""
    try:
        # Try to parse as image
        img = Image.open(io.BytesIO(image_data))
        return {
            "status": "success",
            "format": img.format,
            "size": img.size,
            "mode": img.mode,
            "prediction": "processed_successfully"
        }
    except Exception as e:
        # If not an image, return the raw content (for debugging)
        return {
            "status": "processed",
            "raw_content": image_data.decode('utf-8', errors='replace'),
            "note": "Content processed but not recognized as image format"
        }


def ensure_file(obj):
    """
    BentoML-style file handling - if the input is a URL string,
    automatically fetch the content from that URL.
    
    This mimics the vulnerable ensure_file() function from BentoML's
    serde.py that would fetch URLs without validation.
    """
    if isinstance(obj, str):
        # If it's a URL, fetch the content
        if obj.startswith('http://') or obj.startswith('https://'):
            # VULNERABLE: No validation of URL targets
            # This allows SSRF to internal services
            client = httpx.Client(timeout=10.0)
            resp = client.get(obj)
            return resp.content
        else:
            # Treat as file path (not supported in this demo)
            raise ValueError("File paths not supported, use URLs or direct upload")
    else:
        # It's already file content
        return obj


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/v1/process_image', methods=['POST'])
def process_image_endpoint():
    """
    ML Model Inference Endpoint
    
    Accepts images via:
    - Multipart form upload (file field)
    - JSON body with URL reference ({"image": "http://..."})
    
    The service automatically downloads files from URLs if provided.
    """
    try:
        content_type = request.content_type or ''
        
        if 'multipart/form-data' in content_type:
            # Handle multipart form data
            # Check if 'image' field contains a URL string or an actual file
            if 'image' in request.form:
                # URL provided as form field value
                url_or_path = request.form['image']
                file_content = ensure_file(url_or_path)
            elif 'image' in request.files:
                # Actual file uploaded
                uploaded_file = request.files['image']
                file_content = uploaded_file.read()
            else:
                return jsonify({"error": "No 'image' field provided"}), 400
                
        elif 'application/json' in content_type:
            # Handle JSON request with URL reference
            data = request.get_json()
            if not data or 'image' not in data:
                return jsonify({"error": "JSON body must contain 'image' field"}), 400
            
            image_ref = data['image']
            file_content = ensure_file(image_ref)
            
        else:
            return jsonify({
                "error": "Unsupported Content-Type",
                "hint": "Use multipart/form-data or application/json"
            }), 415
        
        # Process the image through our ML model
        result = process_image(file_content)
        return jsonify(result)
        
    except httpx.HTTPError as e:
        return jsonify({"error": f"Failed to fetch URL: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/health')
def health():
    return jsonify({"status": "healthy"})


@app.route('/api/docs')
def api_docs():
    """API documentation endpoint"""
    return jsonify({
        "service": "ML Image Processing API",
        "version": "1.0.0",
        "endpoints": {
            "/": "Web interface",
            "/api/v1/process_image": {
                "method": "POST",
                "description": "Process an image through ML model",
                "accepts": [
                    "multipart/form-data with 'image' field (file or URL)",
                    "application/json with {'image': 'url'}"
                ],
                "example_multipart": "curl -X POST -F 'image=http://example.com/img.jpg' /api/v1/process_image",
                "example_json": "curl -X POST -H 'Content-Type: application/json' -d '{\"image\": \"http://example.com/img.jpg\"}' /api/v1/process_image"
            }
        }
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
