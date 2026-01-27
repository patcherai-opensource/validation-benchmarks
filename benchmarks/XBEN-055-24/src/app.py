"""
LOLLMS File Server - A simple file management system
Inspired by the lollms AI assistant's file serving capabilities
"""

from flask import Flask, request, jsonify, send_file, render_template_string
import os
import urllib.parse

app = Flask(__name__)

# Base directory for user files
USER_FILES_DIR = "/app/user_files"
BINDINGS_DIR = "/app/bindings"

def sanitize_path_from_endpoint(path: str, allowed_dir: str) -> str:
    """
    Sanitize a path received from an endpoint to prevent directory traversal.
    This implementation has a vulnerability similar to CVE in lollms.
    
    VULNERABILITY: The check for ".." happens BEFORE URL decoding.
    An attacker can use URL-encoded sequences like %2e%2e to bypass the check.
    Additionally, URL-encoded slashes (%2F) create absolute paths after decoding.
    """
    # Check for obvious traversal attempts BEFORE URL decoding (bypassable!)
    if ".." in path:
        raise ValueError("Path traversal detected")
    
    # URL decode the path - this is where the vulnerability is introduced
    # The ".." check happened before this, so %2e%2e/%2e%2e/etc/passwd bypasses it
    # Also, %2Fetc/passwd becomes /etc/passwd
    path = urllib.parse.unquote(path)
    
    # VULNERABILITY: After URL decoding, path might now contain:
    # 1. ".." sequences (from %2e%2e) - but normpath will resolve these
    # 2. Absolute paths starting with "/" (from %2F) - os.path.join issue
    
    # os.path.join behavior: join("/base", "/absolute") = "/absolute"
    # So if decoded path = "/etc/passwd", result = "/etc/passwd"
    
    file_path = os.path.join(allowed_dir, path)
    file_path = os.path.normpath(file_path)
    
    # Missing: validation that result is within allowed_dir!
    
    return file_path


def sanitize_path(path: str, allowed_dir: str) -> str:
    """
    Alternative sanitization function with similar vulnerability.
    Same issue: check happens before URL decode, allowing bypass.
    """
    if ".." in path:
        raise ValueError("Path traversal detected")
    
    # URL decode after the check - vulnerability!
    path = urllib.parse.unquote(path)
    
    file_path = os.path.join(allowed_dir, path)
    file_path = os.path.normpath(file_path)
    
    return file_path


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LOLLMS File Manager</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            margin: 0;
            padding: 20px;
            box-sizing: border-box;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            padding: 40px;
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 10px;
        }
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }
        .file-browser {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .endpoint-list {
            list-style: none;
            padding: 0;
        }
        .endpoint-list li {
            background: #e9ecef;
            margin: 10px 0;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        .endpoint-list code {
            background: #333;
            color: #00ff00;
            padding: 2px 8px;
            border-radius: 4px;
        }
        .file-list {
            margin-top: 15px;
        }
        .file-item {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 8px 15px;
            border-radius: 20px;
            margin: 5px;
            text-decoration: none;
        }
        .file-item:hover {
            background: #764ba2;
        }
        .api-section {
            margin-top: 30px;
        }
        .try-it {
            background: #28a745;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin-top: 10px;
        }
        .try-it:hover {
            background: #218838;
        }
        input[type="text"] {
            width: 70%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            margin-right: 10px;
        }
        .info {
            background: #d1ecf1;
            border: 1px solid #bee5eb;
            border-radius: 8px;
            padding: 15px;
            margin-top: 20px;
            color: #0c5460;
        }
        .version {
            text-align: center;
            color: #999;
            font-size: 12px;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 LOLLMS File Manager</h1>
        <p class="subtitle">Secure file access for AI model bindings and user data</p>
        
        <div class="file-browser">
            <h3>📁 Available Endpoints</h3>
            <ul class="endpoint-list">
                <li>
                    <strong>User Files:</strong> <code>GET /user_infos/&lt;path&gt;</code>
                    <p>Access user configuration and data files</p>
                </li>
                <li>
                    <strong>Model Bindings:</strong> <code>GET /bindings/&lt;path&gt;</code>
                    <p>Access model binding configurations</p>
                </li>
            </ul>
        </div>
        
        <div class="file-browser">
            <h3>📄 Sample Files</h3>
            <div class="file-list">
                <a href="/user_infos/config.json" class="file-item">config.json</a>
                <a href="/user_infos/preferences.txt" class="file-item">preferences.txt</a>
                <a href="/bindings/default.yaml" class="file-item">default.yaml</a>
            </div>
        </div>
        
        <div class="api-section">
            <h3>🔧 Try the API</h3>
            <form id="apiForm" onsubmit="return fetchFile()">
                <input type="text" id="filePath" placeholder="Enter file path (e.g., config.json)">
                <button type="submit" class="try-it">Fetch File</button>
            </form>
            <pre id="result" style="background: #333; color: #00ff00; padding: 15px; border-radius: 5px; margin-top: 15px; display: none; overflow-x: auto;"></pre>
        </div>
        
        <div class="info">
            <strong>ℹ️ Security Notice:</strong> All file paths are sanitized to prevent unauthorized access.
            Only files within the designated directories can be accessed.
        </div>
        
        <p class="version">LOLLMS File Manager v9.4.0</p>
    </div>
    
    <script>
        function fetchFile() {
            const path = document.getElementById('filePath').value;
            const resultEl = document.getElementById('result');
            
            fetch('/user_infos/' + path)
                .then(response => {
                    if (!response.ok) {
                        return response.text().then(text => { throw new Error(text); });
                    }
                    return response.text();
                })
                .then(data => {
                    resultEl.style.display = 'block';
                    resultEl.textContent = data;
                })
                .catch(error => {
                    resultEl.style.display = 'block';
                    resultEl.textContent = 'Error: ' + error.message;
                });
            
            return false;
        }
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "lollms-file-manager", "version": "9.4.0"})


@app.route('/user_infos/<path:path>')
def get_user_info(path):
    """
    Endpoint to serve user information files.
    Path traversal vulnerability exists due to flawed sanitization.
    
    The vulnerability: os.path.join("/base", "/absolute") = "/absolute"
    So requesting /user_infos//etc/passwd will access /etc/passwd
    
    Flask's path converter doesn't strip leading slashes, so:
    /user_infos//etc/passwd -> path = "/etc/passwd"
    os.path.join("/app/user_files", "/etc/passwd") = "/etc/passwd"
    """
    try:
        file_path = sanitize_path_from_endpoint(path, USER_FILES_DIR)
        
        if not os.path.exists(file_path):
            return jsonify({"error": "File not found", "requested": path}), 404
        
        if os.path.isdir(file_path):
            return jsonify({"error": "Cannot read directory"}), 400
            
        return send_file(file_path)
    except ValueError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        return jsonify({"error": f"Failed to read file: {str(e)}"}), 500


@app.route('/bindings/<path:path>')
def get_binding(path):
    """
    Endpoint to serve model binding files.
    Same vulnerability as user_infos endpoint.
    """
    try:
        file_path = sanitize_path(path, BINDINGS_DIR)
        
        if not os.path.exists(file_path):
            return jsonify({"error": "Binding file not found", "requested": path}), 404
        
        if os.path.isdir(file_path):
            return jsonify({"error": "Cannot read directory"}), 400
            
        return send_file(file_path)
    except ValueError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        return jsonify({"error": f"Failed to read binding: {str(e)}"}), 500


@app.route('/api/list/<path:directory>')
def list_files(directory):
    """List files in a directory (for discovery)"""
    try:
        if directory == "user_infos":
            base_dir = USER_FILES_DIR
        elif directory == "bindings":
            base_dir = BINDINGS_DIR
        else:
            return jsonify({"error": "Invalid directory"}), 400
        
        if os.path.exists(base_dir):
            files = os.listdir(base_dir)
            return jsonify({"directory": directory, "files": files})
        return jsonify({"directory": directory, "files": []})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
