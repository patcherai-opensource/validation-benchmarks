INDEX_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>CrittersCSS - Critical CSS Inlining Service</title>
    <link rel="stylesheet" type="text/css" href="static/css/style.css">
    <style>
        body { font-family: 'Segoe UI', Tahoma, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; margin: 0; padding: 20px; }
        .container { max-width: 900px; margin: 0 auto; }
        .header { text-align: center; color: white; margin-bottom: 40px; }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { opacity: 0.9; }
        .card { background: white; border-radius: 12px; padding: 30px; margin-bottom: 20px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); }
        .card h2 { color: #333; margin-top: 0; }
        .feature-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 20px; }
        .feature { background: #f8f9fa; padding: 20px; border-radius: 8px; }
        .feature h3 { margin-top: 0; color: #667eea; }
        .btn { display: inline-block; padding: 12px 24px; background: #667eea; color: white; text-decoration: none; border-radius: 6px; margin: 5px; transition: all 0.3s; }
        .btn:hover { background: #5a67d8; transform: translateY(-2px); }
        .btn-secondary { background: #6c757d; }
        .nav-links { margin-top: 20px; }
        code { background: #e9ecef; padding: 2px 6px; border-radius: 4px; font-size: 0.9em; }
        .version { font-size: 0.8em; opacity: 0.7; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>CrittersCSS</h1>
            <p>Critical CSS Inlining Service for Server-Side Rendering</p>
            <p class="version">v16.1.1 - Powered by critters 0.0.19</p>
        </div>
        
        <div class="card">
            <h2>Welcome to CrittersCSS</h2>
            <p>Our service helps optimize your web application's CSS delivery by inlining critical styles during server-side rendering. Based on the popular <code>critters</code> npm package used by Angular Universal.</p>
            
            <div class="feature-grid">
                <div class="feature">
                    <h3>Theme Manager</h3>
                    <p>Browse and manage CSS themes for your applications.</p>
                    <a href="/api/themes" class="btn btn-secondary">View Themes API</a>
                </div>
                <div class="feature">
                    <h3>Style Builder</h3>
                    <p>Build custom styles with our interactive editor.</p>
                    <a href="/style-builder" class="btn btn-secondary">Open Builder</a>
                </div>
                <div class="feature">
                    <h3>CSS Preview</h3>
                    <p>Preview how your CSS will be processed and inlined.</p>
                    <a href="/preview" class="btn">Try Preview</a>
                </div>
                <div class="feature">
                    <h3>Documentation</h3>
                    <p>Learn about our CSS inlining API and features.</p>
                    <a href="/docs" class="btn btn-secondary">Read Docs</a>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>Quick Start</h2>
            <p>Use our preview endpoint to test CSS processing:</p>
            <code>GET /preview?css=your-css-content</code>
            <p style="margin-top: 15px;">The service will process your CSS through our inlining pipeline and show how it renders.</p>
        </div>
    </div>
</body>
</html>
"""

DASHBOARD_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard - CrittersCSS</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #1a1a2e; color: #eee; padding: 40px; }
        .container { max-width: 800px; margin: 0 auto; }
        h1 { color: #667eea; }
        .alert { background: #ff6b6b; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-top: 30px; }
        .stat-card { background: #16213e; padding: 20px; border-radius: 8px; text-align: center; }
        .stat-value { font-size: 2em; color: #667eea; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Admin Dashboard</h1>
        <div class="alert">
            <strong>Notice:</strong> This dashboard requires authentication. Please log in to access admin features.
        </div>
        <p>Dashboard functionality is currently under maintenance. Please use the API endpoints directly.</p>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">1,247</div>
                <div>CSS Files Processed</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">89%</div>
                <div>Size Reduction</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">3</div>
                <div>Active Themes</div>
            </div>
        </div>
    </div>
</body>
</html>
"""

DOCS_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>API Documentation - CrittersCSS</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #f8f9fa; padding: 40px; line-height: 1.6; }
        .container { max-width: 900px; margin: 0 auto; background: white; padding: 40px; border-radius: 12px; box-shadow: 0 2px 20px rgba(0,0,0,0.1); }
        h1 { color: #333; border-bottom: 3px solid #667eea; padding-bottom: 10px; }
        h2 { color: #667eea; margin-top: 30px; }
        code { background: #e9ecef; padding: 2px 8px; border-radius: 4px; }
        pre { background: #1a1a2e; color: #98c379; padding: 20px; border-radius: 8px; overflow-x: auto; }
        .endpoint { background: #f1f3f4; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #667eea; }
        .method { display: inline-block; padding: 4px 10px; border-radius: 4px; font-weight: bold; margin-right: 10px; }
        .get { background: #61affe; color: white; }
        .post { background: #49cc90; color: white; }
        .warning { background: #fff3cd; border: 1px solid #ffc107; padding: 15px; border-radius: 8px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>CrittersCSS API Documentation</h1>
        <p>This service provides CSS inlining capabilities similar to Angular Universal's critical CSS processing.</p>
        
        <h2>Available Endpoints</h2>
        
        <div class="endpoint">
            <span class="method get">GET</span> <code>/api/themes</code>
            <p>Returns a list of available CSS themes.</p>
            <pre>{"themes": ["default", "dark", "ocean"], "status": "ok"}</pre>
        </div>
        
        <div class="endpoint">
            <span class="method get">GET</span> <code>/api/theme/{name}</code>
            <p>Get details for a specific theme by name.</p>
            <pre>{"theme": {"name": "Dark Mode", "css": "..."}, "status": "ok"}</pre>
        </div>
        
        <div class="endpoint">
            <span class="method get">GET</span> <code>/preview?css={content}</code>
            <p>Preview CSS processing and inlining. The service processes your CSS input through our critters-based inlining pipeline.</p>
            <p><strong>Parameters:</strong></p>
            <ul>
                <li><code>css</code> - CSS content or stylesheet references to process</li>
            </ul>
        </div>
        
        <div class="endpoint">
            <span class="method post">POST</span> <code>/api/validate-css</code>
            <p>Validate CSS syntax. Send JSON body with <code>css</code> field.</p>
            <pre>{"valid": true, "message": "CSS syntax appears valid"}</pre>
        </div>
        
        <h2>CSS Processing</h2>
        <p>Our service processes CSS input similarly to the critters package used in Angular Universal. The pipeline:</p>
        <ol>
            <li>Parses input CSS and stylesheet references</li>
            <li>Identifies critical above-the-fold styles</li>
            <li>Inlines critical CSS into the HTML output</li>
            <li>Generates deferred loading for remaining styles</li>
        </ol>
        
        <div class="warning">
            <strong>Security Note:</strong> The CSS processor sanitizes script tags and JavaScript protocols. Only valid CSS constructs and stylesheet link elements are processed.
        </div>
        
        <h2>Example Usage</h2>
        <pre>curl "http://localhost:8080/preview?css=body{color:red}"</pre>
        
        <p style="margin-top: 40px; color: #666; font-size: 0.9em;">CrittersCSS v16.1.1 | Based on critters 0.0.19</p>
    </div>
</body>
</html>
"""

STYLE_BUILDER_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Style Builder - CrittersCSS</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 0; }
        .toolbar { background: #16213e; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; }
        .toolbar h1 { margin: 0; font-size: 1.3em; }
        .toolbar a { color: #667eea; text-decoration: none; }
        .main { display: grid; grid-template-columns: 1fr 1fr; height: calc(100vh - 60px); }
        .editor { padding: 20px; background: #0f0f23; }
        .preview-pane { padding: 20px; background: #fff; color: #333; overflow: auto; }
        textarea { width: 100%; height: calc(100% - 100px); background: #1a1a2e; border: 1px solid #333; color: #98c379; font-family: monospace; font-size: 14px; padding: 15px; border-radius: 8px; resize: none; }
        .btn { padding: 10px 20px; background: #667eea; color: white; border: none; border-radius: 6px; cursor: pointer; margin-top: 10px; }
        .btn:hover { background: #5a67d8; }
        h3 { margin-top: 0; color: #667eea; }
        .hint { font-size: 0.85em; color: #666; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="toolbar">
        <h1>Style Builder</h1>
        <a href="/">Back to Home</a>
    </div>
    <div class="main">
        <div class="editor">
            <h3>CSS Editor</h3>
            <textarea id="css-input" placeholder="Enter your CSS here...

Example:
body {
    background: #f0f0f0;
    font-family: Arial, sans-serif;
}

.header {
    color: #333;
    padding: 20px;
}"></textarea>
            <button class="btn" onclick="previewCSS()">Preview Inline Processing</button>
            <p class="hint" style="color: #888;">Your CSS will be processed through our critical CSS inlining pipeline.</p>
        </div>
        <div class="preview-pane">
            <h3>Preview Output</h3>
            <div id="preview-output">
                <p>Enter CSS in the editor and click "Preview" to see the processed output.</p>
            </div>
        </div>
    </div>
    <script>
        function previewCSS() {
            var css = document.getElementById('css-input').value;
            window.location.href = '/preview?css=' + encodeURIComponent(css);
        }
    </script>
</body>
</html>
"""

CSS_PREVIEW_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>CSS Preview - CrittersCSS</title>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; background: #f8f9fa; margin: 0; padding: 20px; }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 12px 12px 0 0; }}
        .header h1 {{ margin: 0 0 10px 0; }}
        .content {{ background: white; padding: 30px; border-radius: 0 0 12px 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
        .result-box {{ padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .result-box.info {{ background: #e3f2fd; border: 1px solid #2196f3; }}
        .result-box.success {{ background: #e8f5e9; border: 1px solid #4caf50; }}
        .result-box.warning {{ background: #fff3e0; border: 1px solid #ff9800; }}
        .result-box.error {{ background: #ffebee; border: 1px solid #f44336; }}
        .processed-css {{ background: #1a1a2e; color: #98c379; padding: 20px; border-radius: 8px; font-family: monospace; white-space: pre-wrap; overflow-x: auto; margin-top: 20px; }}
        .flag-reveal {{ font-weight: bold; font-family: monospace; background: #ffd54f; padding: 10px; border-radius: 4px; display: inline-block; margin-top: 10px; color: #333; }}
        a {{ color: #667eea; }}
        .nav {{ margin-bottom: 20px; }}
    </style>
    <!-- Processed CSS/Stylesheet References -->
    {0}
</head>
<body>
    <div class="container">
        <div class="nav"><a href="/">&larr; Back to Home</a> | <a href="/style-builder">Style Builder</a> | <a href="/docs">Documentation</a></div>
        
        <div class="header">
            <h1>CSS Preview</h1>
            <p>Critical CSS Inlining Results</p>
        </div>
        
        <div class="content">
            <h2>Processing Result</h2>
            {1}
            
            <h3>Processed Input</h3>
            <div class="processed-css">{0}</div>
            
            <p style="margin-top: 30px; color: #666; font-size: 0.9em;">
                Processed by CrittersCSS v16.1.1 (critters 0.0.19)<br>
                The CSS processor handles stylesheet references and inline styles for critical CSS extraction.
            </p>
        </div>
    </div>
    {2}
</body>
</html>
"""

# Legacy content templates (kept for compatibility)
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

XSS_CONTENT_POST = """
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
                <form class="box-form" method="post">
                    <img class="text-img" src="static/img/logo5_white.png">
                    {4}
                    {3}
                    <input type=text name=solution placeholder="Enter solution..." {2}>
                </form>
            </div>
        </div>
    </html>
"""

XSS_CONTENT_TAG = """
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
                    <input type=text name=name placeholder="Enter your name...">
                    {2}
                </form>
            </div>
        </div>
    </html>
"""

XSS_CONTENT_TAG_POST = """
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
                <form class="box-form" method="post">
                    <img class="text-img" src="static/img/logo5_white.png">
                    {4}
                    {3}
                    <input type=text name=solution placeholder="Enter solution...">
                    {2}
                </form>
            </div>
        </div>
    </html>
"""

XSS_CONTENT_IFRAME = """
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
                    <input type=text name=url placeholder="Enter the URL you want to visit...">
                    <iframe {2}></iframe>
                </form>
            </div>
        </div>
    </html>
"""

XSS_CONTENT_TEXTAREA_POST = """
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
                <form class="box-form" method="post">
                    <img class="text-img" src="static/img/logo5_white.png">
                    {4}
                    {3}
                    <br>
                    <textarea name=name cols=50 rows=20 placeholder="Enter your name..."></textarea>
                    {2}
                    <br>
                    <input type=submit value="Submit">
                </form>
            </div>
        </div>
    </html>
"""

# Image routes (keeping legacy structure, adding new css_inline key)
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
    },
    "css_inline": {
        "start": "static/img/cookies/new_star.png",
        "process": "static/img/cookies/error_star.png",
        "error": "static/img/cookies/error_star.png",
        "success": "static/img/cookies/success_star.png"
    }
}
