INDEX_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenWiki - Collaborative Knowledge Platform</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; color: #333; }
        .header { background: #2c3e50; color: white; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { font-size: 1.5em; }
        .nav { display: flex; gap: 20px; }
        .nav a { color: white; text-decoration: none; padding: 8px 15px; border-radius: 4px; transition: background 0.3s; }
        .nav a:hover { background: rgba(255,255,255,0.1); }
        .container { max-width: 1200px; margin: 30px auto; padding: 0 20px; }
        .welcome-box { background: white; border-radius: 8px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 30px; }
        .welcome-box h2 { color: #2c3e50; margin-bottom: 15px; }
        .welcome-box p { line-height: 1.6; color: #666; }
        .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 30px; }
        .feature-card { background: white; border-radius: 8px; padding: 25px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .feature-card h3 { color: #2c3e50; margin-bottom: 10px; }
        .feature-card a { color: #3498db; text-decoration: none; }
        .feature-card a:hover { text-decoration: underline; }
        .sidebar { background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .sidebar h3 { color: #2c3e50; margin-bottom: 15px; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
        .sidebar ul { list-style: none; }
        .sidebar li { padding: 8px 0; border-bottom: 1px solid #eee; }
        .sidebar a { color: #3498db; text-decoration: none; }
        .main-grid { display: grid; grid-template-columns: 1fr 300px; gap: 30px; }
        @media (max-width: 768px) { .main-grid { grid-template-columns: 1fr; } }
        .footer { background: #2c3e50; color: white; text-align: center; padding: 20px; margin-top: 50px; }
    </style>
</head>
<body>
    <header class="header">
        <h1>OpenWiki</h1>
        <nav class="nav">
            <a href="/">Home</a>
            <a href="/pages">Pages</a>
            <a href="/tools/attach">Attachments</a>
            <a href="/api/status">API Status</a>
            <a href="/help">Help</a>
        </nav>
    </header>
    
    <div class="container">
        <div class="main-grid">
            <div>
                <div class="welcome-box">
                    <h2>Welcome to OpenWiki</h2>
                    <p>OpenWiki is a collaborative knowledge platform that allows teams to create, share, and manage documentation. Get started by browsing existing pages or creating new content.</p>
                </div>
                
                <div class="features">
                    <div class="feature-card">
                        <h3>Pages</h3>
                        <p>Browse and edit wiki pages. Create documentation for your projects.</p>
                        <p><a href="/pages">View all pages &rarr;</a></p>
                    </div>
                    <div class="feature-card">
                        <h3>File Attachments</h3>
                        <p>Upload and manage file attachments for your wiki pages.</p>
                        <p><a href="/tools/attach">Manage attachments &rarr;</a></p>
                    </div>
                    <div class="feature-card">
                        <h3>Search</h3>
                        <p>Search across all wiki content to find what you need.</p>
                        <p><a href="/search">Search wiki &rarr;</a></p>
                    </div>
                    <div class="feature-card">
                        <h3>API</h3>
                        <p>RESTful API for programmatic access to wiki content.</p>
                        <p><a href="/api/status">API documentation &rarr;</a></p>
                    </div>
                </div>
            </div>
            
            <div class="sidebar">
                <h3>Quick Links</h3>
                <ul>
                    <li><a href="/pages/MainPage">Main Page</a></li>
                    <li><a href="/pages/GettingStarted">Getting Started</a></li>
                    <li><a href="/tools/attach">File Upload</a></li>
                    <li><a href="/pages/RecentChanges">Recent Changes</a></li>
                </ul>
                <h3 style="margin-top: 20px;">System Info</h3>
                <ul>
                    <li>Version: 4.5.2</li>
                    <li>Pages: 127</li>
                    <li>Attachments: 43</li>
                </ul>
            </div>
        </div>
    </div>
    
    <footer class="footer">
        <p>&copy; 2024 OpenWiki - Powered by OpenWiki Engine v4.5.2</p>
    </footer>
</body>
</html>
"""

PAGES_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>OpenWiki - Pages</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; color: #333; }
        .header { background: #2c3e50; color: white; padding: 15px 30px; }
        .header h1 { font-size: 1.5em; display: inline; }
        .nav { float: right; }
        .nav a { color: white; text-decoration: none; padding: 8px 15px; margin-left: 10px; }
        .container { max-width: 1000px; margin: 30px auto; padding: 0 20px; }
        .page-list { background: white; border-radius: 8px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .page-list h2 { margin-bottom: 20px; color: #2c3e50; }
        .page-list ul { list-style: none; }
        .page-list li { padding: 12px; border-bottom: 1px solid #eee; }
        .page-list a { color: #3498db; text-decoration: none; }
        .page-meta { color: #999; font-size: 0.9em; margin-left: 10px; }
    </style>
</head>
<body>
    <header class="header">
        <h1>OpenWiki</h1>
        <nav class="nav">
            <a href="/">Home</a>
            <a href="/pages">Pages</a>
            <a href="/tools/attach">Attachments</a>
        </nav>
    </header>
    <div class="container">
        <div class="page-list">
            <h2>Wiki Pages</h2>
            <ul>
                <li><a href="/pages/MainPage">MainPage</a><span class="page-meta">Last modified: 2024-01-15</span></li>
                <li><a href="/pages/GettingStarted">GettingStarted</a><span class="page-meta">Last modified: 2024-01-14</span></li>
                <li><a href="/pages/Installation">Installation</a><span class="page-meta">Last modified: 2024-01-12</span></li>
                <li><a href="/pages/Configuration">Configuration</a><span class="page-meta">Last modified: 2024-01-10</span></li>
                <li><a href="/pages/APIReference">APIReference</a><span class="page-meta">Last modified: 2024-01-08</span></li>
                <li><a href="/pages/Troubleshooting">Troubleshooting</a><span class="page-meta">Last modified: 2024-01-05</span></li>
            </ul>
        </div>
    </div>
</body>
</html>
"""

PAGE_VIEW_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>OpenWiki - {0}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; color: #333; }}
        .header {{ background: #2c3e50; color: white; padding: 15px 30px; }}
        .header h1 {{ font-size: 1.5em; display: inline; }}
        .nav {{ float: right; }}
        .nav a {{ color: white; text-decoration: none; padding: 8px 15px; margin-left: 10px; }}
        .container {{ max-width: 1000px; margin: 30px auto; padding: 0 20px; }}
        .page-content {{ background: white; border-radius: 8px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .page-content h2 {{ margin-bottom: 20px; color: #2c3e50; }}
        .page-content p {{ line-height: 1.8; margin-bottom: 15px; }}
    </style>
</head>
<body>
    <header class="header">
        <h1>OpenWiki</h1>
        <nav class="nav">
            <a href="/">Home</a>
            <a href="/pages">Pages</a>
            <a href="/tools/attach">Attachments</a>
        </nav>
    </header>
    <div class="container">
        <div class="page-content">
            <h2>{0}</h2>
            <p>{1}</p>
        </div>
    </div>
</body>
</html>
"""

API_STATUS_CONTENT = """
{
    "status": "operational",
    "version": "4.5.2",
    "endpoints": {
        "/api/status": "GET - System status",
        "/api/pages": "GET - List pages",
        "/api/pages/<name>": "GET - Get page content",
        "/api/attachments": "GET - List attachments"
    },
    "uptime": "127 hours",
    "database": "connected"
}
"""

SEARCH_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>OpenWiki - Search</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; color: #333; }
        .header { background: #2c3e50; color: white; padding: 15px 30px; }
        .header h1 { font-size: 1.5em; display: inline; }
        .nav { float: right; }
        .nav a { color: white; text-decoration: none; padding: 8px 15px; margin-left: 10px; }
        .container { max-width: 1000px; margin: 30px auto; padding: 0 20px; }
        .search-box { background: white; border-radius: 8px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .search-box h2 { margin-bottom: 20px; color: #2c3e50; }
        .search-box input[type=text] { width: 70%; padding: 12px; border: 1px solid #ddd; border-radius: 4px; }
        .search-box button { padding: 12px 24px; background: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer; }
        .results { margin-top: 20px; }
        .results p { color: #666; }
    </style>
</head>
<body>
    <header class="header">
        <h1>OpenWiki</h1>
        <nav class="nav">
            <a href="/">Home</a>
            <a href="/pages">Pages</a>
            <a href="/tools/attach">Attachments</a>
        </nav>
    </header>
    <div class="container">
        <div class="search-box">
            <h2>Search Wiki</h2>
            <form method="GET" action="/search">
                <input type="text" name="q" placeholder="Enter search query...">
                <button type="submit">Search</button>
            </form>
            <div class="results">
                <p>{0}</p>
            </div>
        </div>
    </div>
</body>
</html>
"""

HELP_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>OpenWiki - Help</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; color: #333; }
        .header { background: #2c3e50; color: white; padding: 15px 30px; }
        .header h1 { font-size: 1.5em; display: inline; }
        .nav { float: right; }
        .nav a { color: white; text-decoration: none; padding: 8px 15px; margin-left: 10px; }
        .container { max-width: 1000px; margin: 30px auto; padding: 0 20px; }
        .help-content { background: white; border-radius: 8px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .help-content h2 { margin-bottom: 20px; color: #2c3e50; }
        .help-content h3 { margin-top: 20px; margin-bottom: 10px; color: #34495e; }
        .help-content p { line-height: 1.8; margin-bottom: 15px; }
        .help-content code { background: #f0f0f0; padding: 2px 6px; border-radius: 3px; }
    </style>
</head>
<body>
    <header class="header">
        <h1>OpenWiki</h1>
        <nav class="nav">
            <a href="/">Home</a>
            <a href="/pages">Pages</a>
            <a href="/tools/attach">Attachments</a>
        </nav>
    </header>
    <div class="container">
        <div class="help-content">
            <h2>OpenWiki Help</h2>
            <h3>Uploading Files</h3>
            <p>To upload files, navigate to the <a href="/tools/attach">Attachments</a> section. You can upload files by specifying a filename and selecting the file to upload.</p>
            <h3>Managing Pages</h3>
            <p>Pages can be created and edited through the Pages section. Use wiki markup for formatting.</p>
            <h3>API Access</h3>
            <p>The API provides programmatic access to wiki content. Check <code>/api/status</code> for available endpoints.</p>
        </div>
    </div>
</body>
</html>
"""

# Upload form - this is where the vulnerable endpoint content goes
UPLOAD_FORM_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>OpenWiki - File Upload</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; color: #333; }}
        .header {{ background: #2c3e50; color: white; padding: 15px 30px; }}
        .header h1 {{ font-size: 1.5em; display: inline; }}
        .nav {{ float: right; }}
        .nav a {{ color: white; text-decoration: none; padding: 8px 15px; margin-left: 10px; }}
        .container {{ max-width: 800px; margin: 30px auto; padding: 0 20px; }}
        .upload-box {{ background: white; border-radius: 8px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .upload-box h2 {{ margin-bottom: 10px; color: #2c3e50; }}
        .upload-box h3 {{ margin-bottom: 20px; color: #34495e; font-weight: normal; }}
        .form-group {{ margin-bottom: 20px; }}
        .form-group label {{ display: block; margin-bottom: 8px; font-weight: 600; }}
        .form-group input[type=text], .form-group input[type=file] {{ width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 4px; }}
        .form-group button {{ padding: 12px 24px; background: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer; }}
        .form-group button:hover {{ background: #2980b9; }}
        .info-box {{ background: #e8f4f8; padding: 15px; border-radius: 4px; margin-top: 20px; }}
        .info-box p {{ color: #2c3e50; font-size: 0.9em; }}
        .result-box {{ margin-top: 20px; padding: 15px; border-radius: 4px; }}
    </style>
</head>
<body>
    <header class="header">
        <h1>OpenWiki</h1>
        <nav class="nav">
            <a href="/">Home</a>
            <a href="/pages">Pages</a>
            <a href="/tools/attach">Attachments</a>
        </nav>
    </header>
    <div class="container">
        <div class="upload-box">
            <h2>Attachment Manager</h2>
            <h3>Upload form for file: {0}</h3>
            {1}
            <form method="POST" enctype="multipart/form-data" action="/tools/attach/upload">
                <div class="form-group">
                    <label for="filename">Filename:</label>
                    <input type="text" id="filename" name="filename" placeholder="Enter filename..." {2}>
                </div>
                <div class="form-group">
                    <label for="file">Select file:</label>
                    <input type="file" id="file" name="file">
                </div>
                <div class="form-group">
                    <button type="submit">Upload File</button>
                </div>
            </form>
            <div class="info-box">
                <p><strong>Note:</strong> Maximum file size is 10MB. Supported formats: jpg, png, gif, pdf, doc, docx, txt</p>
            </div>
        </div>
    </div>
</body>
</html>
"""

# Legacy route - decoy endpoint
ATTACH_LIST_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>OpenWiki - Attachments</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; color: #333; }
        .header { background: #2c3e50; color: white; padding: 15px 30px; }
        .header h1 { font-size: 1.5em; display: inline; }
        .nav { float: right; }
        .nav a { color: white; text-decoration: none; padding: 8px 15px; margin-left: 10px; }
        .container { max-width: 1000px; margin: 30px auto; padding: 0 20px; }
        .attach-box { background: white; border-radius: 8px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .attach-box h2 { margin-bottom: 20px; color: #2c3e50; }
        .attach-list { list-style: none; }
        .attach-list li { padding: 12px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; }
        .attach-list a { color: #3498db; text-decoration: none; }
        .upload-btn { display: inline-block; background: #3498db; color: white; padding: 10px 20px; border-radius: 4px; text-decoration: none; margin-bottom: 20px; }
        .upload-btn:hover { background: #2980b9; }
        .file-size { color: #999; font-size: 0.9em; }
    </style>
</head>
<body>
    <header class="header">
        <h1>OpenWiki</h1>
        <nav class="nav">
            <a href="/">Home</a>
            <a href="/pages">Pages</a>
            <a href="/tools/attach">Attachments</a>
        </nav>
    </header>
    <div class="container">
        <div class="attach-box">
            <h2>File Attachments</h2>
            <a href="/tools/attach/upload" class="upload-btn">Upload New File</a>
            <ul class="attach-list">
                <li><a href="#">readme.pdf</a><span class="file-size">125 KB</span></li>
                <li><a href="#">logo.png</a><span class="file-size">45 KB</span></li>
                <li><a href="#">architecture.jpg</a><span class="file-size">890 KB</span></li>
                <li><a href="#">notes.txt</a><span class="file-size">2 KB</span></li>
                <li><a href="#">presentation.pdf</a><span class="file-size">2.3 MB</span></li>
            </ul>
        </div>
    </div>
</body>
</html>
"""

# Image routes (kept for backwards compatibility with check_xss function)
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
