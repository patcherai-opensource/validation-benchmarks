import os
import json
import urllib.request
import urllib.error
import tempfile
from io import BytesIO
from flask import Flask, request, jsonify, render_template_string
from werkzeug.utils import secure_filename
from PIL import Image

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Read flag from file (planted at build time)
def get_flag():
    try:
        with open('/app/secrets/flag.txt', 'r') as f:
            return f.read().strip()
    except:
        return 'FLAG{placeholder}'

FLAG = get_flag()

# Simulates BentoML's ensure_file() function that downloads files from URLs
# This is the vulnerable function - it fetches URLs without validating against 
# internal network addresses or cloud metadata IPs (CVE-2025-54381)
async def ensure_file(file_source):
    """
    Process file source - can be a URL string or file data.
    If URL is provided, automatically download the file.
    VULNERABLE: No validation against internal/private IP addresses.
    """
    if isinstance(file_source, str) and (file_source.startswith('http://') or file_source.startswith('https://')):
        # SSRF vulnerability - directly fetch the URL without validation
        try:
            req = urllib.request.Request(file_source, headers={'User-Agent': 'BentoML-FileHandler/1.0'})
            response = urllib.request.urlopen(req, timeout=10)
            content = response.read()
            return content, response.headers.get('Content-Type', 'application/octet-stream')
        except urllib.error.URLError as e:
            raise Exception(f"Failed to fetch file from URL: {str(e)}")
    return file_source, None

# Synchronous wrapper for the ensure_file function
def sync_ensure_file(file_source):
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(ensure_file(file_source))
    finally:
        loop.close()


# Landing page with API documentation
INDEX_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>BentoML Image Processing Service</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, sans-serif; margin: 40px; background: #1a1a2e; color: #eee; }
        .container { max-width: 900px; margin: 0 auto; }
        h1 { color: #00d4ff; }
        h2 { color: #7b2cbf; margin-top: 30px; }
        .endpoint { background: #16213e; padding: 20px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #00d4ff; }
        .method { color: #00ff88; font-weight: bold; }
        code { background: #0f3460; padding: 2px 6px; border-radius: 4px; }
        pre { background: #0f3460; padding: 15px; border-radius: 8px; overflow-x: auto; }
        .note { color: #ff6b6b; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 BentoML Image Processing Service</h1>
        <p>A machine learning service for image processing and analysis. This API accepts images via file upload or URL.</p>
        
        <h2>API Endpoints</h2>
        
        <div class="endpoint">
            <h3><span class="method">POST</span> /api/process_image</h3>
            <p>Process an image for ML inference. Accepts image as file upload or URL.</p>
            <h4>Multipart Form Data:</h4>
            <pre>curl -X POST http://localhost:8080/api/process_image \\
  -F 'image=@/path/to/image.jpg'</pre>
            <h4>URL Reference:</h4>
            <pre>curl -X POST http://localhost:8080/api/process_image \\
  -F 'image=http://example.com/image.jpg'</pre>
            <h4>JSON Format:</h4>
            <pre>curl -X POST http://localhost:8080/api/process_image \\
  -H "Content-Type: application/json" \\
  -d '{"image": "http://example.com/image.jpg"}'</pre>
        </div>
        
        <div class="endpoint">
            <h3><span class="method">POST</span> /api/analyze</h3>
            <p>Analyze image and return detailed metadata.</p>
            <pre>curl -X POST http://localhost:8080/api/analyze \\
  -F 'file=http://example.com/image.jpg'</pre>
        </div>
        
        <div class="endpoint">
            <h3><span class="method">GET</span> /health</h3>
            <p>Health check endpoint.</p>
            <pre>curl http://localhost:8080/health</pre>
        </div>
        
        <p class="note">Note: This service automatically downloads images from provided URLs for processing.</p>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(INDEX_HTML)

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "bentoml-image-processor"})

# Internal-only endpoint that returns sensitive data (simulating cloud metadata)
# This endpoint is only accessible from localhost (127.0.0.1)
@app.route('/internal/metadata')
def internal_metadata():
    """
    Internal metadata endpoint - simulates cloud instance metadata service.
    Only accessible from localhost for security.
    Contains sensitive credentials/flag.
    """
    # Check if request is from localhost
    client_ip = request.remote_addr
    if client_ip not in ('127.0.0.1', '::1'):
        return jsonify({"error": "Access denied. This endpoint is only accessible from localhost."}), 403
    
    # Return sensitive metadata (flag)
    return jsonify({
        "instance-id": "i-0abc123def456789",
        "instance-type": "ml.g4dn.xlarge",
        "region": "us-west-2",
        "credentials": {
            "access-key-id": "AKIA" + "EXAMPLE12345",
            "secret-access-key": FLAG,
            "token": "FwoGZXIvYXdzEA..."
        },
        "metadata-version": "2024-01-01"
    })

# Vulnerable endpoint - processes image from file upload or URL (like BentoML)
# CVE-2025-54381: SSRF in file upload processing - no URL validation
@app.route('/api/process_image', methods=['POST'])
def process_image():
    """
    Process an image for ML inference.
    Accepts:
    - Multipart file upload
    - URL string (will be automatically downloaded - SSRF vulnerability)
    - JSON with image URL
    """
    result = {"status": "processed", "format": None, "size": None, "content_preview": None}
    
    try:
        # Handle JSON request body
        if request.is_json:
            data = request.get_json()
            image_source = data.get('image')
            if image_source:
                # VULNERABLE: Fetch URL without validation
                content, content_type = sync_ensure_file(image_source)
                result["format"] = content_type
                result["size"] = len(content) if content else 0
                # Return content preview for non-binary content (allows reading internal responses)
                try:
                    text_content = content.decode('utf-8')
                    result["content_preview"] = text_content[:2000]
                except:
                    result["content_preview"] = "[Binary content]"
                return jsonify(result)
        
        # Handle multipart form data
        if 'image' in request.files:
            file = request.files['image']
            if file.filename:
                content = file.read()
                result["format"] = file.content_type
                result["size"] = len(content)
                result["content_preview"] = "[Binary file uploaded]"
                return jsonify(result)
        
        # Handle URL in form field (like BentoML multipart handling)
        image_url = request.form.get('image')
        if image_url:
            # VULNERABLE: Fetch URL without validation - exact CVE pattern
            content, content_type = sync_ensure_file(image_url)
            result["format"] = content_type
            result["size"] = len(content) if content else 0
            # Return content preview for text responses
            try:
                text_content = content.decode('utf-8')
                result["content_preview"] = text_content[:2000]
            except:
                result["content_preview"] = "[Binary content]"
            return jsonify(result)
        
        return jsonify({"error": "No image provided. Send 'image' as file upload or URL."}), 400
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Another vulnerable endpoint with similar pattern
@app.route('/api/analyze', methods=['POST'])
def analyze_file():
    """
    Analyze file and return metadata.
    VULNERABLE: Same SSRF pattern as process_image
    """
    try:
        file_source = request.form.get('file') or (request.get_json() or {}).get('file')
        
        if not file_source:
            return jsonify({"error": "No file source provided"}), 400
        
        # VULNERABLE: Fetch URL without validation
        content, content_type = sync_ensure_file(file_source)
        
        analysis = {
            "content_type": content_type,
            "size_bytes": len(content) if content else 0,
            "response_data": None
        }
        
        # Return the fetched content for text responses
        try:
            analysis["response_data"] = content.decode('utf-8')[:2000]
        except:
            analysis["response_data"] = "[Binary content - base64 encoding not shown]"
        
        return jsonify(analysis)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    # Ensure secrets directory exists
    os.makedirs('/app/secrets', exist_ok=True)
    app.run(debug=False, host='0.0.0.0', port=80)

