<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API Documentation - Aimeos CMS</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f7fa; }
        .navbar { background: #2c3e50; padding: 15px 30px; color: white; display: flex; justify-content: space-between; align-items: center; }
        .navbar h1 { font-size: 1.5em; }
        .navbar nav a { color: #ecf0f1; text-decoration: none; margin-left: 20px; }
        .container { max-width: 900px; margin: 30px auto; padding: 0 20px; }
        .card { background: white; border-radius: 8px; padding: 30px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.08); }
        .card h2 { color: #2c3e50; margin-bottom: 15px; }
        .card h3 { color: #34495e; margin: 20px 0 10px 0; }
        .card p { color: #555; line-height: 1.6; margin-bottom: 10px; }
        code { background: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-family: monospace; }
        pre { background: #2c3e50; color: #ecf0f1; padding: 15px; border-radius: 5px; overflow-x: auto; margin: 15px 0; }
        .method { display: inline-block; padding: 3px 8px; border-radius: 3px; font-weight: bold; font-size: 0.9em; margin-right: 10px; }
        .method.get { background: #61affe; color: white; }
        .method.post { background: #49cc90; color: white; }
        table { width: 100%; border-collapse: collapse; margin: 15px 0; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #eee; }
        th { background: #f8f9fa; }
        .warning { background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 15px 0; }
    </style>
</head>
<body>
    <div class="navbar">
        <h1>🎨 Aimeos CMS - API Docs</h1>
        <nav>
            <a href="/">Home</a>
            <a href="/admin/">Admin Panel</a>
            <a href="/docs/">Documentation</a>
        </nav>
    </div>
    
    <div class="container">
        <div class="card">
            <h2>Media API Reference</h2>
            <p>The Media API provides programmatic access to upload and manage media files in Aimeos CMS.</p>
            
            <h3>Base URL</h3>
            <code>/api/media</code>
            
            <h3>Authentication</h3>
            <p>All API endpoints require authentication via API key. Include it as:</p>
            <ul style="margin-left: 20px; color: #555;">
                <li><code>X-API-Key</code> header, or</li>
                <li><code>api_key</code> query parameter</li>
            </ul>
        </div>
        
        <div class="card">
            <h2>Endpoints</h2>
            
            <h3><span class="method get">GET</span> /api/media</h3>
            <p>Returns API information and available endpoints.</p>
            
            <h3><span class="method post">POST</span> /api/media/upload</h3>
            <p>Upload a media file to the server.</p>
            
            <h4>Parameters</h4>
            <table>
                <tr>
                    <th>Name</th>
                    <th>Type</th>
                    <th>Required</th>
                    <th>Description</th>
                </tr>
                <tr>
                    <td><code>file</code></td>
                    <td>file</td>
                    <td>Yes</td>
                    <td>The file to upload (multipart/form-data)</td>
                </tr>
                <tr>
                    <td><code>media.url</code></td>
                    <td>string</td>
                    <td>No</td>
                    <td>Custom storage path for the file. If not provided, files are stored in the default upload directory.</td>
                </tr>
            </table>
            
            <h4>Example Request</h4>
            <pre>curl -X POST \
  -H "X-API-Key: aimeos_dev_key" \
  -F "file=@product-image.jpg" \
  -F "media.url=/products/images/" \
  http://localhost:8080/api/media/upload</pre>
            
            <h4>Success Response</h4>
            <pre>{
  "status": "success",
  "message": "File uploaded successfully",
  "file": {
    "name": "product-image.jpg",
    "url": "/products/images/product-image.jpg",
    "mime": "image/jpeg",
    "size": 45678
  }
}</pre>
            
            <div class="warning">
                <strong>⚠️ Note:</strong> The <code>media.url</code> parameter allows specifying custom upload paths. Ensure proper access controls are in place when using this feature.
            </div>
        </div>
        
        <div class="card">
            <h2>Error Responses</h2>
            
            <h3>401 Unauthorized</h3>
            <pre>{
  "status": "error",
  "message": "Authentication required. Provide X-API-Key header or api_key parameter."
}</pre>
            
            <h3>400 Bad Request</h3>
            <pre>{
  "status": "error",
  "message": "No file uploaded or upload error"
}</pre>
        </div>
    </div>
</body>
</html>
