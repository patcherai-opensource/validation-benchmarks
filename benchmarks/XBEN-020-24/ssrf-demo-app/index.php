<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VisionML API - Image Classification Service</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
        .api-info { background: #ecf0f1; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .endpoint { background: #2c3e50; color: #3498db; padding: 8px 15px; border-radius: 3px; font-family: monospace; display: inline-block; }
        code { background: #e8e8e8; padding: 2px 6px; border-radius: 3px; }
        pre { background: #2c3e50; color: #ecf0f1; padding: 15px; border-radius: 5px; overflow-x: auto; }
        .demo-form { margin-top: 30px; padding: 20px; border: 1px solid #bdc3c7; border-radius: 5px; }
        input[type="text"] { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #bdc3c7; border-radius: 3px; }
        button { background: #3498db; color: white; padding: 12px 25px; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background: #2980b9; }
        .status { color: #27ae60; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔮 VisionML API</h1>
        <p class="status">● Service Status: Online</p>
        
        <div class="api-info">
            <h3>Image Classification Endpoint</h3>
            <p>Submit images for AI-powered classification using our ML models.</p>
            <p><strong>Endpoint:</strong> <span class="endpoint">POST /api/classify</span></p>
        </div>

        <h3>API Usage</h3>
        <p>Send a POST request with your image. You can provide either:</p>
        <ul>
            <li>A direct file upload (multipart form)</li>
            <li>A URL reference to fetch the image from</li>
        </ul>
        
        <h4>Example Request (JSON with URL):</h4>
        <pre>{
  "image": "https://example.com/sample.jpg"
}</pre>

        <h4>Example Request (Form with URL):</h4>
        <pre>curl -X POST http://localhost:8080/api/classify \
  -F "image=https://example.com/sample.jpg"</pre>

        <div class="demo-form">
            <h3>Try It Out</h3>
            <form action="/api/classify" method="POST">
                <label for="image">Image URL:</label>
                <input type="text" id="image" name="image" placeholder="https://example.com/image.jpg">
                <button type="submit">Classify Image</button>
            </form>
        </div>

        <div class="api-info" style="margin-top: 30px; font-size: 0.9em;">
            <p><strong>Note:</strong> For internal testing, models and configuration are served from <code>internal-service</code>.</p>
        </div>
    </div>
</body>
</html>
