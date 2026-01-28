INDEX_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>DataLabel Studio - Open Source Data Labeling</title>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background: #f5f7fa; }
        .header { background: #1a73e8; color: white; padding: 20px; }
        .header h1 { margin: 0; font-size: 24px; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .card { background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); padding: 24px; margin-bottom: 20px; }
        .card h2 { margin-top: 0; color: #333; }
        .nav { display: flex; gap: 20px; margin-top: 30px; }
        .nav a { color: #1a73e8; text-decoration: none; padding: 12px 24px; border: 1px solid #1a73e8; border-radius: 4px; }
        .nav a:hover { background: #1a73e8; color: white; }
        .feature-list { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-top: 20px; }
        .feature { padding: 20px; background: #f8f9fa; border-radius: 4px; }
        .api-section { margin-top: 40px; }
        .api-endpoints { font-family: monospace; background: #282c34; color: #abb2bf; padding: 20px; border-radius: 4px; }
        .api-endpoints div { margin: 8px 0; }
        .method { color: #98c379; }
        .path { color: #61afef; }
    </style>
</head>
<body>
    <div class="header">
        <div class="container">
            <h1>DataLabel Studio</h1>
            <p>Enterprise-grade data annotation platform</p>
        </div>
    </div>
    <div class="container">
        <div class="card">
            <h2>Welcome to DataLabel Studio</h2>
            <p>Create ML training datasets with a powerful labeling interface. Configure custom annotation templates, manage projects, and export labeled data.</p>
            <div class="nav">
                <a href="/api/projects">View Projects</a>
                <a href="/api/templates">Label Templates</a>
                <a href="/projects/upload-example/">Upload Config</a>
            </div>
        </div>
        
        <div class="card">
            <h2>Features</h2>
            <div class="feature-list">
                <div class="feature">
                    <h3>Image Labeling</h3>
                    <p>Bounding boxes, polygons, and semantic segmentation</p>
                </div>
                <div class="feature">
                    <h3>Text Annotation</h3>
                    <p>NER, classification, and sentiment analysis</p>
                </div>
                <div class="feature">
                    <h3>Audio Transcription</h3>
                    <p>Speech-to-text and audio classification</p>
                </div>
            </div>
        </div>
        
        <div class="card api-section">
            <h2>API Endpoints</h2>
            <div class="api-endpoints">
                <div><span class="method">GET</span> <span class="path">/api/health</span> - Health check</div>
                <div><span class="method">GET</span> <span class="path">/api/projects</span> - List all projects</div>
                <div><span class="method">GET</span> <span class="path">/api/projects/:id</span> - Get project details</div>
                <div><span class="method">GET</span> <span class="path">/api/templates</span> - List label templates</div>
                <div><span class="method">GET</span> <span class="path">/api/users</span> - List users</div>
                <div><span class="method">POST</span> <span class="path">/projects/upload-example/</span> - Upload label config</div>
                <div><span class="method">GET</span> <span class="path">/api/export/:id</span> - Export project data</div>
            </div>
        </div>
        
        <div class="card">
            <h2>Quick Start</h2>
            <p>Create a label configuration using XML format:</p>
            <pre style="background: #f1f3f4; padding: 15px; border-radius: 4px; overflow-x: auto;">
&lt;View&gt;
  &lt;Image name="img" value="$image"/&gt;
  &lt;RectangleLabels name="label" toName="img"&gt;
    &lt;Label value="Cat"/&gt;
    &lt;Label value="Dog"/&gt;
  &lt;/RectangleLabels&gt;
&lt;/View&gt;</pre>
        </div>
    </div>
</body>
</html>
"""

UPLOAD_EXAMPLE_FORM = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Upload Label Configuration - DataLabel Studio</title>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background: #f5f7fa; }
        .header { background: #1a73e8; color: white; padding: 20px; }
        .header h1 { margin: 0; font-size: 24px; }
        .container { max-width: 800px; margin: 0 auto; padding: 20px; }
        .card { background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); padding: 24px; margin-bottom: 20px; }
        .card h2 { margin-top: 0; color: #333; }
        textarea { width: 100%; height: 200px; font-family: monospace; padding: 12px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        button { background: #1a73e8; color: white; border: none; padding: 12px 24px; border-radius: 4px; cursor: pointer; font-size: 16px; }
        button:hover { background: #1557b0; }
        .breadcrumb { margin-bottom: 20px; }
        .breadcrumb a { color: #1a73e8; text-decoration: none; }
        .example { background: #f8f9fa; padding: 15px; border-radius: 4px; margin: 15px 0; font-family: monospace; font-size: 13px; }
        .note { background: #fff3cd; border: 1px solid #ffc107; padding: 12px; border-radius: 4px; margin-top: 15px; }
    </style>
</head>
<body>
    <div class="header">
        <div class="container">
            <h1>DataLabel Studio</h1>
        </div>
    </div>
    <div class="container">
        <div class="breadcrumb">
            <a href="/">Home</a> &gt; Upload Label Configuration
        </div>
        <div class="card">
            <h2>Upload Label Configuration</h2>
            <p>Enter your label configuration XML to generate sample task data. The configuration defines how data should be annotated.</p>
            
            <form method="POST">
                <label for="label_config"><strong>Label Configuration (XML):</strong></label>
                <textarea name="label_config" id="label_config" placeholder="Enter your label config XML here..."></textarea>
                <div class="note">
                    <strong>Note:</strong> The configuration must be valid XML format with View as the root element.
                </div>
                <br><br>
                <button type="submit">Upload and Parse Configuration</button>
            </form>
            
            <h3>Example Configuration</h3>
            <div class="example">
&lt;View&gt;<br>
&nbsp;&nbsp;&lt;Text name="text" value="$text"/&gt;<br>
&nbsp;&nbsp;&lt;Choices name="sentiment" toName="text"&gt;<br>
&nbsp;&nbsp;&nbsp;&nbsp;&lt;Choice value="Positive"/&gt;<br>
&nbsp;&nbsp;&nbsp;&nbsp;&lt;Choice value="Negative"/&gt;<br>
&nbsp;&nbsp;&lt;/Choices&gt;<br>
&lt;/View&gt;
            </div>
        </div>
    </div>
</body>
</html>
"""

UPLOAD_RESPONSE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Configuration Preview - DataLabel Studio</title>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background: #f5f7fa; }}
        .header {{ background: #1a73e8; color: white; padding: 20px; }}
        .header h1 {{ margin: 0; font-size: 24px; }}
        .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
        .card {{ background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); padding: 24px; margin-bottom: 20px; }}
        .card h2 {{ margin-top: 0; color: #333; }}
        pre {{ background: #282c34; color: #abb2bf; padding: 20px; border-radius: 4px; overflow-x: auto; }}
        .breadcrumb {{ margin-bottom: 20px; }}
        .breadcrumb a {{ color: #1a73e8; text-decoration: none; }}
        .config-preview {{ background: #f8f9fa; padding: 15px; border-radius: 4px; margin: 15px 0; font-family: monospace; white-space: pre-wrap; word-break: break-all; }}
        .alert {{ padding: 15px; border-radius: 4px; margin-top: 15px; }}
        .alert-info {{ background: #d1ecf1; border: 1px solid #bee5eb; color: #0c5460; }}
        .alert-warning {{ background: #fff3cd; border: 1px solid #ffc107; color: #856404; }}
    </style>
</head>
<body>
    <div class="header">
        <div class="container">
            <h1>DataLabel Studio</h1>
        </div>
    </div>
    <div class="container">
        <div class="breadcrumb">
            <a href="/">Home</a> &gt; <a href="/projects/upload-example/">Upload</a> &gt; Preview
        </div>
        <div class="card">
            <h2>Configuration Parsed Successfully</h2>
            <p>The following task data was extracted from your label configuration:</p>
            
            <h3>Extracted Task Data (JSON)</h3>
            <pre>{0}</pre>
            
            <h3>Original Configuration</h3>
            <div class="config-preview">{1}</div>
            
            <div class="alert alert-info">
                Configuration processed. You can now use this template to create annotation tasks.
            </div>
        </div>
    </div>
</body>
</html>
"""

UPLOAD_SUCCESS_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Configuration Validated - DataLabel Studio</title>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background: #f5f7fa; }}
        .header {{ background: #1a73e8; color: white; padding: 20px; }}
        .header h1 {{ margin: 0; font-size: 24px; }}
        .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
        .card {{ background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); padding: 24px; margin-bottom: 20px; }}
        .card h2 {{ margin-top: 0; color: #333; }}
        .success {{ background: #d4edda; border: 1px solid #c3e6cb; color: #155724; padding: 20px; border-radius: 4px; }}
        .flag {{ font-family: monospace; background: #f8f9fa; padding: 10px; border-radius: 4px; margin-top: 10px; }}
    </style>
</head>
<body>
    <div class="header">
        <div class="container">
            <h1>DataLabel Studio</h1>
        </div>
    </div>
    <div class="container">
        <div class="card">
            <h2>Configuration Validated</h2>
            <div class="success">
                <strong>Success!</strong> Your label configuration has been validated.
                <div class="flag">{0}</div>
            </div>
        </div>
    </div>
</body>
</html>
"""

# Legacy support - keeping original templates for compatibility
IMAGE_ROUTES = {
    "xss_easy": {
        "start": "static/img/cookies/new_circle.png",
        "process": "static/img/cookies/error_circle.png",
        "error": "static/img/cookies/error_circle.png",
        "success": "static/img/cookies/success_circle.png"
    },
    "xss_easy_med": {
        "start": "static/img/cookies/new_triangle.png",
        "process": "static/img/cookies/error_triangle.png",
        "error": "static/img/cookies/error_triangle.png",
        "success": "static/img/cookies/success_triangle.png"
    },
    "xss_medium": {
        "start": "static/img/cookies/new_star.png",
        "process": "static/img/cookies/error_star.png",
        "error": "static/img/cookies/error_star.png",
        "success": "static/img/cookies/success_star.png"
    },
    "xss_hard": {
        "start": "static/img/cookies/new_umbrella.png",
        "process": "static/img/cookies/error_umbrella.png",
        "error": "static/img/cookies/error_umbrella.png",
        "success": "static/img/cookies/success_umbrella.png"
    }
}
