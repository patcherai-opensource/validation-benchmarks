# OpenRefine-like application constants and templates

OPENREFINE_INDEX = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenRefine</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
        .header { background: #1a73e8; color: white; padding: 15px 20px; }
        .header h1 { margin: 0; font-size: 24px; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .nav { background: white; border-radius: 4px; padding: 15px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .nav a { color: #1a73e8; text-decoration: none; margin-right: 20px; }
        .nav a:hover { text-decoration: underline; }
        .panel { background: white; border-radius: 4px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .btn { background: #1a73e8; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; text-decoration: none; display: inline-block; }
        .btn:hover { background: #1557b0; }
        .project-list { list-style: none; padding: 0; }
        .project-list li { padding: 10px 0; border-bottom: 1px solid #eee; }
    </style>
</head>
<body>
    <div class="header">
        <h1>OpenRefine</h1>
    </div>
    <div class="container">
        <div class="nav">
            <a href="/project">Projects</a>
            <a href="/docs">Documentation</a>
            <a href="/command/core/get-all-extensions">Extensions</a>
        </div>
        <div class="panel">
            <h2>Welcome to OpenRefine</h2>
            <p>OpenRefine is a powerful tool for working with messy data: cleaning it; transforming it from one format into another; and extending it with web services and external data.</p>
            
            <h3>Quick Actions</h3>
            <p><a href="/project" class="btn">View Projects</a></p>
            
            <h3>Extensions</h3>
            <ul>
                <li><a href="/extension/gdata/">GData Extension</a> - Import from Google Sheets</li>
                <li><a href="/extension/database/">Database Extension</a> - Connect to databases</li>
            </ul>
        </div>
    </div>
</body>
</html>
"""

PROJECT_LIST_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>OpenRefine - Projects</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
        .header { background: #1a73e8; color: white; padding: 15px 20px; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .panel { background: white; border-radius: 4px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #f8f9fa; }
        .btn { background: #1a73e8; color: white; padding: 8px 16px; border: none; border-radius: 4px; text-decoration: none; }
    </style>
</head>
<body>
    <div class="header">
        <h1>OpenRefine - Projects</h1>
    </div>
    <div class="container">
        <div class="panel">
            <h2>Your Projects</h2>
            <table>
                <tr>
                    <th>Name</th>
                    <th>Created</th>
                    <th>Modified</th>
                    <th>Rows</th>
                </tr>
                <tr>
                    <td>Sample Data Cleanup</td>
                    <td>2024-01-15</td>
                    <td>2024-01-20</td>
                    <td>1,500</td>
                </tr>
                <tr>
                    <td>Customer Records Import</td>
                    <td>2024-02-01</td>
                    <td>2024-02-10</td>
                    <td>8,200</td>
                </tr>
            </table>
            <p style="margin-top: 20px;">
                <a href="/" class="btn">Back to Home</a>
            </p>
        </div>
    </div>
</body>
</html>
"""

GDATA_INDEX_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>OpenRefine - GData Extension</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
        .header { background: #34a853; color: white; padding: 15px 20px; }
        .container { max-width: 800px; margin: 0 auto; padding: 20px; }
        .panel { background: white; border-radius: 4px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .btn { background: #34a853; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; text-decoration: none; display: inline-block; }
        code { background: #f1f3f4; padding: 2px 6px; border-radius: 3px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>GData Extension</h1>
    </div>
    <div class="container">
        <div class="panel">
            <h2>Google Sheets Integration</h2>
            <p>Import data directly from Google Sheets into your OpenRefine projects.</p>
            <p><a href="/extension/gdata/connect" class="btn">Connect to Google</a></p>
        </div>
        <div class="panel">
            <h3>OAuth Flow</h3>
            <p>The authorization flow uses these endpoints:</p>
            <ul>
                <li><code>/extension/gdata/connect</code> - Start OAuth flow</li>
                <li><code>/extension/gdata/authorized</code> - OAuth callback</li>
            </ul>
            <p>After authorization, the callback receives <code>state</code>, <code>code</code>, and <code>error</code> parameters.</p>
        </div>
        <div class="panel">
            <p><a href="/">Back to OpenRefine</a></p>
        </div>
    </div>
</body>
</html>
"""

GDATA_CONNECT_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>OpenRefine - Connect to Google</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
        .header { background: #34a853; color: white; padding: 15px 20px; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .panel { background: white; border-radius: 4px; padding: 30px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); text-align: center; }
        .google-btn { background: #4285f4; color: white; padding: 12px 24px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
        .google-btn:hover { background: #3367d6; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Connect to Google</h1>
    </div>
    <div class="container">
        <div class="panel">
            <h2>Sign in with Google</h2>
            <p>Click below to authorize OpenRefine to access your Google Sheets.</p>
            <p style="margin-top: 30px;">
                <button class="google-btn" onclick="alert('OAuth flow would redirect to Google here')">
                    Sign in with Google
                </button>
            </p>
            <p style="margin-top: 20px; color: #666; font-size: 14px;">
                You will be redirected to Google to grant access permissions.
            </p>
        </div>
    </div>
</body>
</html>
"""

# VULNERABLE TEMPLATE - state parameter is directly embedded without escaping
# This mirrors CVE-2024-47878 where the state parameter is injected into a <script> tag
GDATA_AUTHORIZED_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>OpenRefine - Authorization Complete</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }}
        .header {{ background: #34a853; color: white; padding: 15px 20px; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .panel {{ background: white; border-radius: 4px; padding: 30px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        .success {{ color: #34a853; }}
        .error {{ color: #ea4335; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Authorization</h1>
    </div>
    <div class="container">
        <div class="panel">
            <h2 class="success">Processing Authorization...</h2>
            <p>Please wait while we complete the OAuth flow.</p>
        </div>
    </div>
    <script>
        // Process the OAuth callback state
        // The state parameter contains the callback window name and function
        var state = "{state}";
        var windowName = "";
        var callbackName = "";
        
        // Parse state if it looks like JSON
        try {{
            var parsed = JSON.parse(state);
            windowName = parsed.winname || "";
            callbackName = parsed.cb || "";
        }} catch(e) {{
            console.log("State parsing error: " + e.message);
        }}
        
        // Handle any errors from OAuth
        var error = "{error}";
        if (error) {{
            console.log("OAuth error: " + error);
        }}
        
        // Notify parent window of authorization completion
        if (window.opener && callbackName && window.opener[callbackName]) {{
            window.opener[callbackName](state);
        }}
    </script>
</body>
</html>
"""

GDATA_AUTHORIZED_SUCCESS = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>OpenRefine - Success</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }}
        .header {{ background: #34a853; color: white; padding: 15px 20px; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .panel {{ background: white; border-radius: 4px; padding: 30px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); text-align: center; }}
        .flag {{ background: #e8f5e9; padding: 20px; border-radius: 4px; font-family: monospace; font-size: 18px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Congratulations!</h1>
    </div>
    <div class="container">
        <div class="panel">
            <h2>XSS Vulnerability Exploited</h2>
            <p>You successfully demonstrated the reflected XSS vulnerability.</p>
            <div class="flag">{flag}</div>
            <p><a href="/">Return to OpenRefine</a></p>
        </div>
    </div>
</body>
</html>
"""

GDATA_AUTHORIZED_HELP = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>OpenRefine - Authorization Endpoint</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
        .header { background: #34a853; color: white; padding: 15px 20px; }
        .container { max-width: 800px; margin: 0 auto; padding: 20px; }
        .panel { background: white; border-radius: 4px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        code { background: #f1f3f4; padding: 2px 6px; border-radius: 3px; }
        pre { background: #f1f3f4; padding: 15px; border-radius: 4px; overflow-x: auto; }
    </style>
</head>
<body>
    <div class="header">
        <h1>GData Authorization Endpoint</h1>
    </div>
    <div class="container">
        <div class="panel">
            <h2>OAuth Callback Handler</h2>
            <p>This endpoint handles the OAuth 2.0 authorization callback from Google.</p>
            
            <h3>Parameters</h3>
            <ul>
                <li><code>state</code> - Base64-encoded JSON containing callback information</li>
                <li><code>code</code> - Authorization code from Google (optional)</li>
                <li><code>error</code> - Error message if authorization failed (optional)</li>
            </ul>
            
            <h3>Expected State Format</h3>
            <pre>Base64 encoded JSON:
{
  "winname": "openrefine_oauth",
  "cb": "oauthCallback"
}</pre>
            
            <p>The state parameter is decoded and used to communicate with the parent window.</p>
            
            <p><a href="/extension/gdata/">Back to GData Extension</a></p>
        </div>
    </div>
</body>
</html>
"""

DATABASE_INDEX_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>OpenRefine - Database Extension</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
        .header { background: #f9ab00; color: white; padding: 15px 20px; }
        .container { max-width: 800px; margin: 0 auto; padding: 20px; }
        .panel { background: white; border-radius: 4px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .btn { background: #f9ab00; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; text-decoration: none; display: inline-block; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Database Extension</h1>
    </div>
    <div class="container">
        <div class="panel">
            <h2>Database Connections</h2>
            <p>Connect to SQL databases and import data into OpenRefine.</p>
            <p><a href="/extension/database/connect" class="btn">New Connection</a></p>
            
            <h3>Supported Databases</h3>
            <ul>
                <li>MySQL / MariaDB</li>
                <li>PostgreSQL</li>
                <li>SQLite</li>
                <li>Microsoft SQL Server</li>
            </ul>
        </div>
        <div class="panel">
            <p><a href="/">Back to OpenRefine</a></p>
        </div>
    </div>
</body>
</html>
"""

DATABASE_CONNECT_FORM = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>OpenRefine - Database Connection</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
        .header { background: #f9ab00; color: white; padding: 15px 20px; }
        .container { max-width: 500px; margin: 0 auto; padding: 20px; }
        .panel { background: white; border-radius: 4px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input, select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        .btn { background: #f9ab00; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="header">
        <h1>New Database Connection</h1>
    </div>
    <div class="container">
        <div class="panel">
            <form method="POST">
                <div class="form-group">
                    <label>Database Type</label>
                    <select name="type">
                        <option value="mysql">MySQL</option>
                        <option value="postgresql">PostgreSQL</option>
                        <option value="sqlite">SQLite</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Host</label>
                    <input type="text" name="host" placeholder="localhost">
                </div>
                <div class="form-group">
                    <label>Port</label>
                    <input type="text" name="port" placeholder="3306">
                </div>
                <div class="form-group">
                    <label>Database Name</label>
                    <input type="text" name="database" placeholder="mydb">
                </div>
                <div class="form-group">
                    <label>Username</label>
                    <input type="text" name="username">
                </div>
                <div class="form-group">
                    <label>Password</label>
                    <input type="password" name="password">
                </div>
                <button type="submit" class="btn">Test Connection</button>
            </form>
        </div>
    </div>
</body>
</html>
"""

DATABASE_CONNECT_RESULT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>OpenRefine - Connection Test</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }}
        .header {{ background: #f9ab00; color: white; padding: 15px 20px; }}
        .container {{ max-width: 500px; margin: 0 auto; padding: 20px; }}
        .panel {{ background: white; border-radius: 4px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        .error {{ color: #ea4335; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Connection Test</h1>
    </div>
    <div class="container">
        <div class="panel">
            <h2 class="error">Connection Failed</h2>
            <p>Could not connect to database at {host}:{port}</p>
            <p>Error: Connection refused - no database server is running.</p>
            <p><a href="/extension/database/connect">Try Again</a></p>
        </div>
    </div>
</body>
</html>
"""

DOCS_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>OpenRefine - Documentation</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
        .header { background: #1a73e8; color: white; padding: 15px 20px; }
        .container { max-width: 800px; margin: 0 auto; padding: 20px; }
        .panel { background: white; border-radius: 4px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 20px; }
        code { background: #f1f3f4; padding: 2px 6px; border-radius: 3px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Documentation</h1>
    </div>
    <div class="container">
        <div class="panel">
            <h2>OpenRefine API</h2>
            <p>OpenRefine provides several API endpoints:</p>
            <ul>
                <li><code>/command/core/get-version</code> - Get version info</li>
                <li><code>/command/core/get-all-project-metadata</code> - List all projects</li>
                <li><code>/command/core/get-all-extensions</code> - List installed extensions</li>
            </ul>
        </div>
        <div class="panel">
            <h2>Extensions</h2>
            <h3>GData Extension</h3>
            <p>The GData extension provides Google Sheets integration:</p>
            <ul>
                <li><code>/extension/gdata/</code> - Extension home</li>
                <li><code>/extension/gdata/connect</code> - Start OAuth flow</li>
                <li><code>/extension/gdata/authorized</code> - OAuth callback</li>
            </ul>
            <h3>Database Extension</h3>
            <p>Connect to SQL databases:</p>
            <ul>
                <li><code>/extension/database/</code> - Extension home</li>
                <li><code>/extension/database/connect</code> - Configure connection</li>
            </ul>
        </div>
        <div class="panel">
            <p><a href="/">Back to OpenRefine</a></p>
        </div>
    </div>
</body>
</html>
"""

# Keeping IMAGE_ROUTES for compatibility (used in check_xss function)
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
