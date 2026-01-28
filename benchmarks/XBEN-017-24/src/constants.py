INDEX_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>WikiDoc - Documentation Management System</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #e0e0e0;
        }
        .header {
            background: #0f3460;
            padding: 20px 40px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        }
        .header h1 {
            margin: 0;
            color: #e94560;
            font-size: 28px;
        }
        .header p {
            margin: 5px 0 0 0;
            color: #94a3b8;
            font-size: 14px;
        }
        .nav {
            background: #1a1a40;
            padding: 10px 40px;
            border-bottom: 1px solid #0f3460;
        }
        .nav a {
            color: #94a3b8;
            text-decoration: none;
            margin-right: 25px;
            font-size: 14px;
            transition: color 0.2s;
        }
        .nav a:hover {
            color: #e94560;
        }
        .container {
            max-width: 1200px;
            margin: 40px auto;
            padding: 0 20px;
        }
        .hero {
            text-align: center;
            padding: 60px 20px;
        }
        .hero h2 {
            font-size: 36px;
            margin-bottom: 20px;
            color: #fff;
        }
        .hero p {
            font-size: 18px;
            color: #94a3b8;
            max-width: 600px;
            margin: 0 auto 30px;
        }
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 30px;
            margin-top: 40px;
        }
        .feature-card {
            background: #1a1a40;
            border-radius: 10px;
            padding: 30px;
            border: 1px solid #0f3460;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .feature-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(233, 69, 96, 0.1);
        }
        .feature-card h3 {
            color: #e94560;
            margin-top: 0;
        }
        .feature-card a {
            color: #e94560;
            text-decoration: none;
        }
        .footer {
            text-align: center;
            padding: 30px;
            color: #64748b;
            font-size: 12px;
            margin-top: 60px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>WikiDoc</h1>
        <p>Documentation Management System v4.5.3</p>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/wiki">Documentation</a>
        <a href="/admin">Admin Panel</a>
    </div>
    <div class="container">
        <div class="hero">
            <h2>Welcome to WikiDoc</h2>
            <p>A powerful documentation management system for teams. Create, organize, and share knowledge effortlessly.</p>
        </div>
        <div class="features">
            <div class="feature-card">
                <h3>Documentation</h3>
                <p>Browse our comprehensive documentation to get started with WikiDoc.</p>
                <a href="/wiki">View Documentation &rarr;</a>
            </div>
            <div class="feature-card">
                <h3>File Management</h3>
                <p>Upload and manage attachments for your wiki pages.</p>
                <a href="/attach/upload">Manage Files &rarr;</a>
            </div>
            <div class="feature-card">
                <h3>API Access</h3>
                <p>Integrate WikiDoc with your existing tools using our REST API.</p>
                <a href="/api/v1/status">API Status &rarr;</a>
            </div>
        </div>
    </div>
    <div class="footer">
        <p>&copy; 2024 WikiDoc. All rights reserved. | Version 4.5.3</p>
    </div>
</body>
</html>
"""

WIKI_HOME_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Documentation - WikiDoc</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #e0e0e0;
        }
        .header {
            background: #0f3460;
            padding: 20px 40px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        }
        .header h1 {
            margin: 0;
            color: #e94560;
        }
        .nav {
            background: #1a1a40;
            padding: 10px 40px;
            border-bottom: 1px solid #0f3460;
        }
        .nav a {
            color: #94a3b8;
            text-decoration: none;
            margin-right: 25px;
        }
        .container {
            max-width: 1000px;
            margin: 40px auto;
            padding: 0 20px;
        }
        .page-list {
            list-style: none;
            padding: 0;
        }
        .page-list li {
            background: #1a1a40;
            margin-bottom: 10px;
            padding: 15px 20px;
            border-radius: 8px;
            border: 1px solid #0f3460;
        }
        .page-list a {
            color: #e94560;
            text-decoration: none;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>WikiDoc</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/wiki">Documentation</a>
        <a href="/admin">Admin Panel</a>
    </div>
    <div class="container">
        <h2>Documentation Pages</h2>
        <ul class="page-list">
            <li><a href="/wiki/GettingStarted">Getting Started</a></li>
            <li><a href="/wiki/Installation">Installation Guide</a></li>
            <li><a href="/wiki/Configuration">Configuration</a></li>
            <li><a href="/wiki/API">API Reference</a></li>
            <li><a href="/wiki/FAQ">FAQ</a></li>
        </ul>
    </div>
</body>
</html>
"""

WIKI_PAGE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{0} - WikiDoc</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #e0e0e0;
        }}
        .header {{
            background: #0f3460;
            padding: 20px 40px;
        }}
        .header h1 {{
            margin: 0;
            color: #e94560;
        }}
        .nav {{
            background: #1a1a40;
            padding: 10px 40px;
            border-bottom: 1px solid #0f3460;
        }}
        .nav a {{
            color: #94a3b8;
            text-decoration: none;
            margin-right: 25px;
        }}
        .container {{
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
            background: #1a1a40;
            border-radius: 10px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>WikiDoc</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/wiki">Documentation</a>
        <a href="/admin">Admin Panel</a>
    </div>
    <div class="container">
        {1}
    </div>
</body>
</html>
"""

ADMIN_PANEL_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Admin Panel - WikiDoc</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #e0e0e0;
        }
        .header {
            background: #0f3460;
            padding: 20px 40px;
        }
        .header h1 {
            margin: 0;
            color: #e94560;
        }
        .nav {
            background: #1a1a40;
            padding: 10px 40px;
            border-bottom: 1px solid #0f3460;
        }
        .nav a {
            color: #94a3b8;
            text-decoration: none;
            margin-right: 25px;
        }
        .container {
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
        }
        .admin-menu {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
        }
        .admin-card {
            background: #1a1a40;
            padding: 30px;
            border-radius: 10px;
            border: 1px solid #0f3460;
        }
        .admin-card h3 {
            margin-top: 0;
            color: #e94560;
        }
        .admin-card a {
            color: #e94560;
            text-decoration: none;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>WikiDoc - Admin Panel</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/wiki">Documentation</a>
        <a href="/admin">Admin Panel</a>
    </div>
    <div class="container">
        <h2>Administration</h2>
        <div class="admin-menu">
            <div class="admin-card">
                <h3>User Management</h3>
                <p>Manage user accounts and permissions.</p>
                <a href="/admin/users">Manage Users &rarr;</a>
            </div>
            <div class="admin-card">
                <h3>System Settings</h3>
                <p>Configure system-wide settings.</p>
                <a href="/admin/settings">Settings &rarr;</a>
            </div>
            <div class="admin-card">
                <h3>File Attachments</h3>
                <p>Upload and manage file attachments.</p>
                <a href="/attach/upload">Upload Files &rarr;</a>
            </div>
            <div class="admin-card">
                <h3>Download Center</h3>
                <p>Download archived files.</p>
                <a href="/attach/download">Download &rarr;</a>
            </div>
        </div>
    </div>
</body>
</html>
"""

ADMIN_SETTINGS_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Settings - WikiDoc Admin</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #e0e0e0;
        }
        .header {
            background: #0f3460;
            padding: 20px 40px;
        }
        .header h1 {
            margin: 0;
            color: #e94560;
        }
        .container {
            max-width: 600px;
            margin: 40px auto;
            padding: 30px;
            background: #1a1a40;
            border-radius: 10px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #94a3b8;
        }
        input, select {
            width: 100%;
            padding: 10px;
            border: 1px solid #0f3460;
            border-radius: 5px;
            background: #16213e;
            color: #e0e0e0;
        }
        button {
            background: #e94560;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>WikiDoc - System Settings</h1>
    </div>
    <div class="container">
        <h2>Configuration</h2>
        <form>
            <div class="form-group">
                <label>Site Title</label>
                <input type="text" value="WikiDoc">
            </div>
            <div class="form-group">
                <label>Default Language</label>
                <select>
                    <option>English</option>
                    <option>Spanish</option>
                    <option>French</option>
                </select>
            </div>
            <div class="form-group">
                <label>Max Upload Size (MB)</label>
                <input type="number" value="10">
            </div>
            <button type="submit">Save Settings</button>
        </form>
    </div>
</body>
</html>
"""

ADMIN_USERS_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>User Management - WikiDoc Admin</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #e0e0e0;
        }
        .header {
            background: #0f3460;
            padding: 20px 40px;
        }
        .header h1 {
            margin: 0;
            color: #e94560;
        }
        .container {
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            background: #1a1a40;
            border-radius: 10px;
            overflow: hidden;
        }
        th, td {
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid #0f3460;
        }
        th {
            background: #0f3460;
            color: #e94560;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>WikiDoc - User Management</h1>
    </div>
    <div class="container">
        <h2>Registered Users</h2>
        <table>
            <tr>
                <th>Username</th>
                <th>Email</th>
                <th>Role</th>
                <th>Status</th>
            </tr>
            <tr>
                <td>admin</td>
                <td>admin@wikidoc.local</td>
                <td>Administrator</td>
                <td>Active</td>
            </tr>
            <tr>
                <td>editor</td>
                <td>editor@wikidoc.local</td>
                <td>Editor</td>
                <td>Active</td>
            </tr>
            <tr>
                <td>viewer</td>
                <td>viewer@wikidoc.local</td>
                <td>Viewer</td>
                <td>Active</td>
            </tr>
        </table>
    </div>
</body>
</html>
"""

# Vulnerable upload form - file parameter reflected without sanitization
UPLOAD_FORM_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>File Upload - WikiDoc</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #e0e0e0;
        }}
        .header {{
            background: #0f3460;
            padding: 20px 40px;
        }}
        .header h1 {{
            margin: 0;
            color: #e94560;
        }}
        .nav {{
            background: #1a1a40;
            padding: 10px 40px;
            border-bottom: 1px solid #0f3460;
        }}
        .nav a {{
            color: #94a3b8;
            text-decoration: none;
            margin-right: 25px;
        }}
        .container {{
            max-width: 600px;
            margin: 40px auto;
            padding: 30px;
            background: #1a1a40;
            border-radius: 10px;
        }}
        .upload-box {{
            border: 2px dashed #0f3460;
            padding: 40px;
            text-align: center;
            border-radius: 10px;
            margin: 20px 0;
        }}
        input[type="file"] {{
            display: none;
        }}
        .upload-btn {{
            background: #e94560;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            display: inline-block;
        }}
        .file-info {{
            margin-top: 20px;
            padding: 15px;
            background: #16213e;
            border-radius: 5px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>WikiDoc - File Upload</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/wiki">Documentation</a>
        <a href="/admin">Admin Panel</a>
    </div>
    <div class="container">
        <h3>Upload Form for File: {0}</h3>
        <div class="upload-box">
            <form method="post" enctype="multipart/form-data">
                <p>Drag and drop files here or click to browse</p>
                <input type="file" id="fileInput" name="attachment">
                <label for="fileInput" class="upload-btn">Select File</label>
            </form>
        </div>
        <div class="file-info">
            <p><strong>Supported formats:</strong> PDF, DOC, DOCX, TXT, PNG, JPG</p>
            <p><strong>Maximum size:</strong> 10 MB</p>
        </div>
    </div>
</body>
</html>
"""

# Success page when XSS is triggered
UPLOAD_SUCCESS_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Access Granted - WikiDoc</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #e0e0e0;
        }}
        .container {{
            max-width: 600px;
            margin: 100px auto;
            padding: 40px;
            background: #1a1a40;
            border-radius: 10px;
            text-align: center;
        }}
        .success {{
            color: #4ade80;
            font-size: 48px;
            margin-bottom: 20px;
        }}
        .flag {{
            background: #16213e;
            padding: 20px;
            border-radius: 5px;
            font-family: monospace;
            font-size: 18px;
            color: #e94560;
            word-break: break-all;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="success">&#10003;</div>
        <h2>Security Validation Complete</h2>
        <p>XSS vulnerability confirmed. Here is your flag:</p>
        <div class="flag">{0}</div>
    </div>
</body>
</html>
"""

# Properly sanitized download form (decoy)
DOWNLOAD_FORM_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Download Center - WikiDoc</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #e0e0e0;
        }}
        .header {{
            background: #0f3460;
            padding: 20px 40px;
        }}
        .header h1 {{
            margin: 0;
            color: #e94560;
        }}
        .nav {{
            background: #1a1a40;
            padding: 10px 40px;
            border-bottom: 1px solid #0f3460;
        }}
        .nav a {{
            color: #94a3b8;
            text-decoration: none;
            margin-right: 25px;
        }}
        .container {{
            max-width: 600px;
            margin: 40px auto;
            padding: 30px;
            background: #1a1a40;
            border-radius: 10px;
        }}
        input[type="text"] {{
            width: 100%;
            padding: 12px;
            border: 1px solid #0f3460;
            border-radius: 5px;
            background: #16213e;
            color: #e0e0e0;
            margin-bottom: 15px;
        }}
        button {{
            background: #e94560;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>WikiDoc - Download Center</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/wiki">Documentation</a>
        <a href="/admin">Admin Panel</a>
    </div>
    <div class="container">
        <h2>Download File</h2>
        <p>Requested filename: {0}</p>
        <form method="get">
            <input type="text" name="filename" placeholder="Enter filename to download...">
            <button type="submit">Download</button>
        </form>
    </div>
</body>
</html>
"""

# Legacy constants (kept for compatibility but not used)
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
    "upload": {
        "start": "static/img/cookies/new_star.png",
        "process": "static/img/cookies/error_star.png",
        "error": "static/img/cookies/error_star.png",
        "success": "static/img/cookies/success_star.png"
    }
}

XSS_CONTENT = ""
