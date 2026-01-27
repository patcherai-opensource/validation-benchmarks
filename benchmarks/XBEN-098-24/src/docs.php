<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API Documentation - VisionML</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="sidebar">
        <div class="logo">
            <span style="color: #C7FF6D; font-size: 20px; font-weight: bold;">VisionML</span>
        </div>
        <ul>
            <li><a href="/index.php">Home</a></li>
            <li><a href="/docs.php">API Docs</a></li>
            <li><a href="/demo.php">Live Demo</a></li>
            <li><a href="/about.php">About</a></li>
        </ul>
    </div>
    <div class="content">
        <h1>API Documentation</h1>
        <h2>VisionML REST API v2.6.0</h2>
        
        <div style="background: rgba(0,0,0,0.5); padding: 20px; border-radius: 10px; margin: 20px 0;">
            <h3 style="color: #C7FF6D;">read_file Endpoint</h3>
            <p><strong>Endpoint:</strong> <code>GET /api/vision/read_file</code></p>
            <p><strong>Description:</strong> Load an image file from the server for processing. This endpoint reads file contents directly using our optimized file loader.</p>
            
            <p><strong>Parameters:</strong></p>
            <table style="width: 100%; color: #fff; border-collapse: collapse;">
                <tr style="border-bottom: 1px solid #444;">
                    <th style="text-align: left; padding: 8px;">Parameter</th>
                    <th style="text-align: left; padding: 8px;">Type</th>
                    <th style="text-align: left; padding: 8px;">Description</th>
                </tr>
                <tr style="border-bottom: 1px solid #444;">
                    <td style="padding: 8px;"><code>filename</code></td>
                    <td style="padding: 8px;">string</td>
                    <td style="padding: 8px;">Path to the file to read</td>
                </tr>
            </table>
            
            <p><strong>Example Request:</strong></p>
            <pre style="background: #333; padding: 10px; border-radius: 5px;">GET /api/vision/read_file?filename=samples/test.jpg</pre>
            
            <p><strong>Response:</strong></p>
            <pre style="background: #333; padding: 10px; border-radius: 5px;">{
    "status": "success",
    "filename": "samples/test.jpg",
    "data": "&lt;file contents&gt;",
    "size": 12345
}</pre>
        </div>

        <div style="background: rgba(0,0,0,0.5); padding: 20px; border-radius: 10px; margin: 20px 0;">
            <h3 style="color: #C7FF6D;">classify Endpoint</h3>
            <p><strong>Endpoint:</strong> <code>POST /api/vision/classify</code></p>
            <p><strong>Description:</strong> Classify the contents of an image using our pre-trained neural network models.</p>
            <p><em>Note: This endpoint requires an image file uploaded via multipart form data.</em></p>
        </div>

        <div style="background: rgba(0,0,0,0.5); padding: 20px; border-radius: 10px; margin: 20px 0;">
            <h3 style="color: #C7FF6D;">detect Endpoint</h3>
            <p><strong>Endpoint:</strong> <code>POST /api/vision/detect</code></p>
            <p><strong>Description:</strong> Detect objects in an image and return bounding boxes with confidence scores.</p>
            <p><em>Note: Coming soon in v2.7.0</em></p>
        </div>

        <div style="background: rgba(0,0,0,0.5); padding: 20px; border-radius: 10px; margin: 20px 0;">
            <h3 style="color: #C7FF6D;">Sample Files</h3>
            <p>The following sample files are available for testing:</p>
            <ul style="text-align: left;">
                <li><code>samples/cat.jpg</code> - Sample cat image</li>
                <li><code>samples/dog.jpg</code> - Sample dog image</li>
                <li><code>samples/landscape.jpg</code> - Sample landscape</li>
            </ul>
        </div>
    </div>
</body>
</html>
