<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WikiStyle CMS - API Documentation</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 900px; margin: 0 auto; }
        .header {
            background: white;
            padding: 20px 30px;
            border-radius: 10px 10px 0 0;
            border-bottom: 3px solid #667eea;
        }
        .header h1 { color: #333; font-size: 24px; }
        .nav {
            background: #f8f9fa;
            padding: 10px 30px;
            display: flex;
            gap: 20px;
        }
        .nav a {
            color: #667eea;
            text-decoration: none;
            padding: 8px 15px;
            border-radius: 5px;
        }
        .nav a:hover { background: #e9ecef; }
        .nav a.active { background: #667eea; color: white; }
        .content {
            background: white;
            padding: 30px;
            border-radius: 0 0 10px 10px;
        }
        .endpoint {
            border: 1px solid #ddd;
            border-radius: 8px;
            margin-bottom: 20px;
            overflow: hidden;
        }
        .endpoint-header {
            background: #f8f9fa;
            padding: 15px 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .method {
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
            color: white;
        }
        .method.get { background: #28a745; }
        .method.post { background: #007bff; }
        .endpoint-path { font-family: monospace; font-size: 14px; }
        .endpoint-body { padding: 20px; }
        .endpoint-body p { margin-bottom: 10px; }
        pre {
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            font-size: 13px;
        }
        .param-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }
        .param-table th, .param-table td {
            padding: 10px;
            border: 1px solid #ddd;
            text-align: left;
        }
        .param-table th { background: #f8f9fa; }
        .footer { text-align: center; color: white; margin-top: 20px; opacity: 0.8; }
        .note { background: #fff3cd; border: 1px solid #ffc107; padding: 10px; border-radius: 5px; margin: 15px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>WikiStyle CMS</h1>
        </div>
        <div class="nav">
            <a href="/">Dashboard</a>
            <a href="/themes.php">Themes</a>
            <a href="/presets.php">CSS Presets</a>
            <a href="/api-docs.php" class="active">API Docs</a>
            <a href="/about.php">About</a>
        </div>
        <div class="content">
            <h2 style="margin-bottom: 20px;">API Documentation</h2>
            <p style="margin-bottom: 30px;">WikiStyle CMS provides a REST API for programmatic theme management.</p>
            
            <div class="endpoint">
                <div class="endpoint-header">
                    <span class="method post">POST</span>
                    <span class="endpoint-path">/api/auth/login</span>
                </div>
                <div class="endpoint-body">
                    <p>Authenticate and obtain a session for API access.</p>
                    <table class="param-table">
                        <tr><th>Parameter</th><th>Type</th><th>Description</th></tr>
                        <tr><td>username</td><td>string</td><td>User's username</td></tr>
                        <tr><td>password</td><td>string</td><td>User's password</td></tr>
                    </table>
                    <p style="margin-top: 15px;"><strong>Example:</strong></p>
                    <pre>curl -X POST http://localhost/api/auth/login \
  -d "username=user&amp;password=pass" -c cookies.txt</pre>
                </div>
            </div>
            
            <div class="endpoint">
                <div class="endpoint-header">
                    <span class="method get">GET</span>
                    <span class="endpoint-path">/api/auth/status</span>
                </div>
                <div class="endpoint-body">
                    <p>Check current authentication status.</p>
                    <pre>{"authenticated": true, "user": "editor"}</pre>
                </div>
            </div>
            
            <div class="endpoint">
                <div class="endpoint-header">
                    <span class="method get">GET</span>
                    <span class="endpoint-path">/api/templates/list</span>
                </div>
                <div class="endpoint-body">
                    <p>List all available theme presets.</p>
                    <pre>{"presets": [{"name": "default", "primary": "#667eea"}...]}</pre>
                </div>
            </div>
            
            <div class="endpoint">
                <div class="endpoint-header">
                    <span class="method post">POST</span>
                    <span class="endpoint-path">/api/templates/custom-presets/{filename}</span>
                </div>
                <div class="endpoint-body">
                    <p>Create a new custom CSS preset. Requires authentication.</p>
                    <div class="note">
                        <strong>Note:</strong> The filename parameter should end with .css extension for proper styling.
                    </div>
                    <table class="param-table">
                        <tr><th>Parameter</th><th>Type</th><th>Description</th></tr>
                        <tr><td>primary-color</td><td>string</td><td>Primary theme color (hex)</td></tr>
                        <tr><td>secondary-color</td><td>string</td><td>Secondary theme color (hex)</td></tr>
                        <tr><td>text-color</td><td>string</td><td>Text color (hex)</td></tr>
                        <tr><td>background-color</td><td>string</td><td>Background color (hex)</td></tr>
                        <tr><td>custom-css</td><td>string</td><td>Additional custom CSS rules</td></tr>
                    </table>
                    <p style="margin-top: 15px;"><strong>Example:</strong></p>
                    <pre>curl -X POST "http://localhost/api/templates/custom-presets/mytheme.css" \
  -d "primary-color=#ff0000" -b cookies.txt</pre>
                    <p style="margin-top: 10px;"><strong>Response:</strong></p>
                    <pre>{"success": true, "path": "/custom/css-presets/mytheme.css"}</pre>
                </div>
            </div>
            
            <div class="endpoint">
                <div class="endpoint-header">
                    <span class="method get">GET</span>
                    <span class="endpoint-path">/api/system/info</span>
                </div>
                <div class="endpoint-body">
                    <p>Get system information and version details.</p>
                    <pre>{"version": "4.5.3", "php_version": "5.x.x", "features": [...]}</pre>
                </div>
            </div>
        </div>
        <div class="footer">
            <p>WikiStyle CMS v4.5.3 | Theme Manager Module</p>
        </div>
    </div>
</body>
</html>
