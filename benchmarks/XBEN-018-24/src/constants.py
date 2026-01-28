# WebDAV Directory Browser Templates
# Simulating WsgiDAV-like interface for CTF

INDEX_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>WebDAV Directory Browser</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #eee;
            margin: 0;
            padding: 0;
            min-height: 100vh;
        }
        .container {
            max-width: 1000px;
            margin: 0 auto;
            padding: 40px 20px;
        }
        .header {
            text-align: center;
            margin-bottom: 40px;
        }
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            color: #4da6ff;
        }
        .header p {
            color: #888;
            font-size: 1.1em;
        }
        .nav {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-bottom: 40px;
            flex-wrap: wrap;
        }
        .nav a {
            background: #2d2d44;
            color: #fff;
            padding: 15px 30px;
            text-decoration: none;
            border-radius: 8px;
            transition: all 0.3s;
        }
        .nav a:hover {
            background: #4da6ff;
            transform: translateY(-2px);
        }
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 40px;
        }
        .feature-card {
            background: rgba(45, 45, 68, 0.8);
            padding: 25px;
            border-radius: 12px;
            border: 1px solid #3d3d5c;
        }
        .feature-card h3 {
            color: #4da6ff;
            margin-top: 0;
        }
        .footer {
            text-align: center;
            margin-top: 60px;
            padding: 20px;
            color: #666;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>&#128193; WebDAV Directory Browser</h1>
            <p>Secure file management and sharing platform</p>
            <p style="font-size: 0.8em; color: #555;">Version 3.1.0</p>
        </div>
        
        <div class="nav">
            <a href="/browse">Browse Files</a>
            <a href="/upload">Upload</a>
            <a href="/settings">Settings</a>
            <a href="/help">Help</a>
            <a href="/about">About</a>
        </div>
        
        <div class="features">
            <div class="feature-card">
                <h3>&#128274; Secure Access</h3>
                <p>Role-based access control with authentication support for multiple realms.</p>
            </div>
            <div class="feature-card">
                <h3>&#128194; Directory Listing</h3>
                <p>Browse and manage your files with our intuitive directory browser interface.</p>
            </div>
            <div class="feature-card">
                <h3>&#128259; WebDAV Protocol</h3>
                <p>Full WebDAV compliance for seamless integration with desktop clients.</p>
            </div>
            <div class="feature-card">
                <h3>&#128196; File Preview</h3>
                <p>Preview documents and images directly in your browser.</p>
            </div>
        </div>
        
        <div class="footer">
            <p>WebDAV Directory Browser &copy; 2024 | <a href="/login" style="color: #4da6ff;">Admin Login</a></p>
        </div>
    </div>
</body>
</html>
"""

BROWSE_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Browse Files - WebDAV Browser</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #1a1a2e;
            color: #eee;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
        }}
        .breadcrumb {{
            background: #2d2d44;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}
        .breadcrumb a {{
            color: #4da6ff;
            text-decoration: none;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: #2d2d44;
            border-radius: 8px;
            overflow: hidden;
        }}
        th, td {{
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid #3d3d5c;
        }}
        th {{
            background: #1a1a2e;
            color: #4da6ff;
        }}
        tr:hover {{
            background: rgba(77, 166, 255, 0.1);
        }}
        a {{
            color: #4da6ff;
            text-decoration: none;
        }}
        .back-link {{
            display: inline-block;
            margin-bottom: 20px;
            color: #888;
        }}
        .info-box {{
            background: #2d2d44;
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
            font-size: 0.9em;
            color: #888;
        }}
    </style>
</head>
<body>
    <div class="container">
        <a href="/" class="back-link">&larr; Back to Home</a>
        
        <h1>&#128193; Directory Browser</h1>
        
        <div class="breadcrumb">
            <strong>Path:</strong> <a href="/browse">{path}</a>
        </div>
        
        <table>
            <tr>
                <th>Type</th>
                <th>Name</th>
                <th>Size</th>
                <th>Modified</th>
            </tr>
            <tr><td>&#128193;</td><td>Documents</td><td>-</td><td>2024-01-15 10:30:00</td></tr>
            <tr><td>&#128193;</td><td>Images</td><td>-</td><td>2024-01-14 08:22:00</td></tr>
            <tr><td>&#128193;</td><td>Projects</td><td>-</td><td>2024-01-13 16:45:00</td></tr>
            <tr><td>&#128196;</td><td>readme.txt</td><td>2.4 KB</td><td>2024-01-12 11:00:00</td></tr>
            <tr><td>&#128196;</td><td>config.json</td><td>1.1 KB</td><td>2024-01-11 09:15:00</td></tr>
            <tr><td>&#128196;</td><td>backup.zip</td><td>15.7 MB</td><td>2024-01-10 14:30:00</td></tr>
        </table>
        
        <div class="info-box">
            <p><strong>Note:</strong> You are browsing as an anonymous user. <a href="/login">Log in</a> for full access.</p>
        </div>
    </div>
</body>
</html>
"""

PROFILE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Directory Browser - WebDAV</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #1a1a2e;
            color: #eee;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
        }
        .user-info {
            background: #2d2d44;
            padding: 15px 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .user-info .auth-details {
            font-size: 0.95em;
        }
        .breadcrumb {
            background: #2d2d44;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            background: #2d2d44;
            border-radius: 8px;
            overflow: hidden;
        }
        th, td {
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid #3d3d5c;
        }
        th {
            background: #1a1a2e;
            color: #4da6ff;
        }
        tr:hover {
            background: rgba(77, 166, 255, 0.1);
        }
        a {
            color: #4da6ff;
            text-decoration: none;
        }
        .back-link {
            display: inline-block;
            margin-bottom: 20px;
            color: #888;
        }
    </style>
</head>
<body>
    <div class="container">
        <a href="/" class="back-link">&larr; Back to Home</a>
        
        <h1>&#128193; Directory Browser</h1>
        
        <div class="user-info">
            <div class="auth-details">
                Authenticated user: "<strong>{{ user_name }}</strong>", 
                realm: "<strong>{{ realm }}</strong>", 
                access: <strong>{{ access_mode }}</strong>
            </div>
            <a href="/login">Switch User</a>
        </div>
        
        <div class="breadcrumb">
            <strong>Path:</strong> <a href="/browse/profile">{{ path }}</a>
        </div>
        
        <table>
            <tr>
                <th>Type</th>
                <th>Name</th>
                <th>Size</th>
                <th>Modified</th>
            </tr>
            {{ file_rows }}
        </table>
    </div>
</body>
</html>
"""

ABOUT_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>About - WebDAV Browser</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #1a1a2e;
            color: #eee;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 700px;
            margin: 0 auto;
        }
        a { color: #4da6ff; text-decoration: none; }
        .back-link { display: inline-block; margin-bottom: 20px; color: #888; }
        .content { background: #2d2d44; padding: 30px; border-radius: 12px; }
        h2 { color: #4da6ff; margin-top: 30px; }
        .version { color: #888; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="container">
        <a href="/" class="back-link">&larr; Back to Home</a>
        <div class="content">
            <h1>About WebDAV Directory Browser</h1>
            <p class="version">Version 3.1.0</p>
            
            <h2>Overview</h2>
            <p>WebDAV Directory Browser is a web-based file management interface that provides 
            directory browsing capabilities for WebDAV-enabled servers.</p>
            
            <h2>Features</h2>
            <ul>
                <li>Directory listing and navigation</li>
                <li>File upload and download</li>
                <li>User authentication with realm support</li>
                <li>Access control management</li>
            </ul>
            
            <h2>Technical Information</h2>
            <p>Built with Python/Flask and Jinja2 templating engine.</p>
            <p>WebDAV protocol compliance: RFC 4918</p>
            
            <h2>Contact</h2>
            <p>For support, please contact: admin@webdav-browser.local</p>
        </div>
    </div>
</body>
</html>
"""

HELP_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Help - WebDAV Browser</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #1a1a2e;
            color: #eee;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 700px;
            margin: 0 auto;
        }
        a { color: #4da6ff; text-decoration: none; }
        .back-link { display: inline-block; margin-bottom: 20px; color: #888; }
        .content { background: #2d2d44; padding: 30px; border-radius: 12px; }
        h2 { color: #4da6ff; margin-top: 30px; }
        code { background: #1a1a2e; padding: 2px 8px; border-radius: 4px; }
        pre { background: #1a1a2e; padding: 15px; border-radius: 8px; overflow-x: auto; }
    </style>
</head>
<body>
    <div class="container">
        <a href="/" class="back-link">&larr; Back to Home</a>
        <div class="content">
            <h1>Help & Documentation</h1>
            
            <h2>Getting Started</h2>
            <p>Navigate to the <a href="/browse">Browse Files</a> page to view the directory listing.</p>
            
            <h2>URL Parameters</h2>
            <p>The directory browser supports the following URL parameters:</p>
            <ul>
                <li><code>path</code> - Directory path to browse</li>
                <li><code>user</code> - Username for authentication context</li>
                <li><code>realm</code> - Authentication realm</li>
                <li><code>access</code> - Access mode (read-only, read-write)</li>
            </ul>
            
            <h2>API Endpoints</h2>
            <pre>
GET /api/status  - Server status
GET /api/files   - List files as JSON
            </pre>
            
            <h2>WebDAV Clients</h2>
            <p>You can connect using any WebDAV-compatible client:</p>
            <ul>
                <li>Windows Explorer (Map Network Drive)</li>
                <li>macOS Finder (Connect to Server)</li>
                <li>Cyberduck, WinSCP, or similar</li>
            </ul>
        </div>
    </div>
</body>
</html>
"""

LOGIN_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Login - WebDAV Browser</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #eee;
            margin: 0;
            padding: 0;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .login-box {
            background: #2d2d44;
            padding: 40px;
            border-radius: 12px;
            width: 350px;
        }
        h1 { text-align: center; color: #4da6ff; margin-bottom: 30px; }
        input[type="text"], input[type="password"] {
            width: 100%;
            padding: 12px;
            margin-bottom: 15px;
            border: 1px solid #3d3d5c;
            border-radius: 6px;
            background: #1a1a2e;
            color: #eee;
            box-sizing: border-box;
        }
        button {
            width: 100%;
            padding: 12px;
            background: #4da6ff;
            border: none;
            border-radius: 6px;
            color: #fff;
            font-size: 1em;
            cursor: pointer;
        }
        button:hover { background: #3d96ef; }
        .back-link { display: block; text-align: center; margin-top: 20px; color: #888; }
        a { color: #4da6ff; text-decoration: none; }
    </style>
</head>
<body>
    <div class="login-box">
        <h1>&#128274; Login</h1>
        <form method="POST">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <input type="text" name="realm" placeholder="Realm (optional)">
            <button type="submit">Sign In</button>
        </form>
        <a href="/" class="back-link">&larr; Back to Home</a>
    </div>
</body>
</html>
"""

SETTINGS_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Settings - WebDAV Browser</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #1a1a2e;
            color: #eee;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 700px;
            margin: 0 auto;
        }
        a { color: #4da6ff; text-decoration: none; }
        .back-link { display: inline-block; margin-bottom: 20px; color: #888; }
        .content { background: #2d2d44; padding: 30px; border-radius: 12px; }
        h2 { color: #4da6ff; margin-top: 30px; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #3d3d5c; }
        th { color: #888; }
        .enabled { color: #4CAF50; }
        .disabled { color: #888; }
    </style>
</head>
<body>
    <div class="container">
        <a href="/" class="back-link">&larr; Back to Home</a>
        <div class="content">
            <h1>Server Settings</h1>
            
            <h2>Directory Browser Configuration</h2>
            <table>
                <tr><th>Setting</th><th>Value</th></tr>
                <tr><td>dir_browser.enable</td><td class="enabled">True</td></tr>
                <tr><td>dir_browser.icon</td><td>True</td></tr>
                <tr><td>dir_browser.response_trailer</td><td>True</td></tr>
                <tr><td>dir_browser.show_user</td><td class="enabled">True</td></tr>
                <tr><td>http_authenticator.accept_basic</td><td>True</td></tr>
                <tr><td>http_authenticator.default_to_digest</td><td>True</td></tr>
            </table>
            
            <h2>Server Information</h2>
            <table>
                <tr><th>Property</th><th>Value</th></tr>
                <tr><td>Version</td><td>3.1.0</td></tr>
                <tr><td>Python</td><td>2.7.18</td></tr>
                <tr><td>Template Engine</td><td>Jinja2</td></tr>
                <tr><td>Auto-escape</td><td class="disabled">Disabled</td></tr>
            </table>
            
            <p style="color: #888; font-size: 0.9em; margin-top: 30px;">
                Settings are read-only in demo mode. Contact administrator for changes.
            </p>
        </div>
    </div>
</body>
</html>
"""

UPLOAD_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Upload - WebDAV Browser</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #1a1a2e;
            color: #eee;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
        }
        a { color: #4da6ff; text-decoration: none; }
        .back-link { display: inline-block; margin-bottom: 20px; color: #888; }
        .upload-box {
            background: #2d2d44;
            padding: 40px;
            border-radius: 12px;
            text-align: center;
        }
        .drop-zone {
            border: 2px dashed #3d3d5c;
            border-radius: 12px;
            padding: 60px 40px;
            margin: 20px 0;
        }
        .drop-zone:hover { border-color: #4da6ff; }
        input[type="file"] { display: none; }
        button {
            padding: 12px 30px;
            background: #4da6ff;
            border: none;
            border-radius: 6px;
            color: #fff;
            font-size: 1em;
            cursor: pointer;
            margin-top: 20px;
        }
        button:hover { background: #3d96ef; }
    </style>
</head>
<body>
    <div class="container">
        <a href="/" class="back-link">&larr; Back to Home</a>
        <div class="upload-box">
            <h1>&#128228; Upload Files</h1>
            <form method="POST" enctype="multipart/form-data">
                <div class="drop-zone">
                    <p>&#128196; Drag and drop files here</p>
                    <p style="color: #888;">or</p>
                    <label for="file-input" style="color: #4da6ff; cursor: pointer;">Browse Files</label>
                    <input type="file" id="file-input" name="file">
                </div>
                <button type="submit">Upload</button>
            </form>
        </div>
    </div>
</body>
</html>
"""

# Image routes (kept for compatibility but not used in new design)
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
