INDEX_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Label Studio - Data Labeling Platform</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            margin: 0;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container {
            background: white;
            border-radius: 12px;
            padding: 40px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            max-width: 600px;
            width: 90%;
        }
        h1 {
            color: #1f2937;
            margin-bottom: 10px;
        }
        .subtitle {
            color: #6b7280;
            margin-bottom: 30px;
        }
        .nav-links {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        .nav-link {
            display: flex;
            align-items: center;
            padding: 15px 20px;
            background: #f3f4f6;
            border-radius: 8px;
            text-decoration: none;
            color: #374151;
            transition: all 0.2s;
        }
        .nav-link:hover {
            background: #e5e7eb;
            transform: translateX(5px);
        }
        .nav-link .icon {
            width: 40px;
            height: 40px;
            background: #667eea;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 15px;
            color: white;
            font-size: 20px;
        }
        .version {
            margin-top: 30px;
            text-align: center;
            color: #9ca3af;
            font-size: 14px;
        }
        .api-docs {
            margin-top: 20px;
            padding: 15px;
            background: #fef3c7;
            border-radius: 8px;
            font-size: 14px;
        }
        .api-docs code {
            background: #fde68a;
            padding: 2px 6px;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Label Studio</h1>
        <p class="subtitle">Open Source Data Labeling Platform</p>
        
        <div class="nav-links">
            <a href="/projects/upload-example/" class="nav-link">
                <div class="icon">&#128194;</div>
                <div>
                    <strong>Upload Example Config</strong>
                    <br><small>Upload and preview labeling configurations</small>
                </div>
            </a>
            <a href="/api/projects/" class="nav-link">
                <div class="icon">&#128196;</div>
                <div>
                    <strong>Projects API</strong>
                    <br><small>View available labeling projects</small>
                </div>
            </a>
            <a href="/api/version/" class="nav-link">
                <div class="icon">&#9881;</div>
                <div>
                    <strong>Version Info</strong>
                    <br><small>Check API version and status</small>
                </div>
            </a>
        </div>
        
        <div class="api-docs">
            <strong>API Documentation:</strong><br>
            POST <code>/projects/upload-example/</code> with <code>label_config</code> parameter to upload and validate labeling configurations.
        </div>
        
        <div class="version">
            Label Studio v1.17.0 (Community Edition)
        </div>
    </div>
</body>
</html>
"""


UPLOAD_EXAMPLE_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Upload Example - Label Studio</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            margin: 0;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container {
            background: white;
            border-radius: 12px;
            padding: 40px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            max-width: 700px;
            width: 90%;
        }
        h1 {
            color: #1f2937;
            margin-bottom: 10px;
        }
        .subtitle {
            color: #6b7280;
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #374151;
        }
        textarea {
            width: 100%;
            height: 200px;
            padding: 12px;
            border: 2px solid #e5e7eb;
            border-radius: 8px;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 13px;
            resize: vertical;
            box-sizing: border-box;
        }
        textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        button {
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            transition: background 0.2s;
        }
        button:hover {
            background: #5a67d8;
        }
        .example {
            margin-top: 20px;
            padding: 15px;
            background: #f3f4f6;
            border-radius: 8px;
        }
        .example code {
            display: block;
            white-space: pre-wrap;
            font-size: 12px;
        }
        .back-link {
            display: inline-block;
            margin-bottom: 20px;
            color: #667eea;
            text-decoration: none;
        }
        .back-link:hover {
            text-decoration: underline;
        }
        .hint {
            margin-top: 15px;
            padding: 10px;
            background: #fef3c7;
            border-radius: 6px;
            font-size: 13px;
            color: #92400e;
        }
    </style>
</head>
<body>
    <div class="container">
        <a href="/" class="back-link">&larr; Back to Home</a>
        <h1>Upload Label Configuration</h1>
        <p class="subtitle">Submit your XML labeling configuration to generate sample tasks</p>
        
        <form method="POST" action="/projects/upload-example/">
            <div class="form-group">
                <label for="label_config">Label Configuration (XML):</label>
                <textarea name="label_config" id="label_config" placeholder="Enter your labeling configuration XML here..."></textarea>
            </div>
            <button type="submit">Upload & Preview</button>
        </form>
        
        <div class="example">
            <strong>Example Configuration:</strong>
            <code>&lt;View&gt;
  &lt;Text name="text" value="$text"/&gt;
  &lt;Choices name="sentiment" toName="text"&gt;
    &lt;Choice value="Positive"/&gt;
    &lt;Choice value="Negative"/&gt;
  &lt;/Choices&gt;
&lt;/View&gt;</code>
        </div>
        
        <div class="hint">
            <strong>Note:</strong> The configuration will be validated and rendered to preview how your labeling interface will appear.
        </div>
    </div>
</body>
</html>
"""


RENDER_CONFIG_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Label Studio - Config Preview</title>
</head>
<body>
    <div id="label-studio-root">
        <div class="config-preview">
            <input type="text" name="config" value="{0}">
        </div>
    </div>
</body>
</html>
"""


# Image routes for XSS feedback (keeping these for compatibility)
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


# Legacy XSS content templates (keeping for reference, not used in new version)
XSS_CONTENT = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <link rel="stylesheet" type="text/css" href="static/css/xss/xss{0}.css">
            <title>Dalgona - {1}</title>
        </head>

        <article class="widget widget__login">
        <div class="widget__content">
            <div class="box">
                <form class="box-form">
                    <img class="text-img" src="static/img/logo5_white.png">
                    {4}
                    {3}
                    <input type=text name=name placeholder="Enter your name..." {2}>
                </form>
            </div>
        </div>
    </html>
"""
