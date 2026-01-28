INDEX_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenWiki - Home</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 15px 30px; }
        .header h1 { font-size: 24px; display: inline-block; }
        .header .version { font-size: 12px; color: #95a5a6; margin-left: 10px; }
        .nav { background: #34495e; padding: 10px 30px; }
        .nav a { color: #ecf0f1; text-decoration: none; margin-right: 20px; padding: 8px 15px; border-radius: 4px; }
        .nav a:hover { background: #3d566e; }
        .container { max-width: 1200px; margin: 30px auto; padding: 0 20px; }
        .welcome-box { background: white; border-radius: 8px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .welcome-box h2 { color: #2c3e50; margin-bottom: 15px; }
        .welcome-box p { color: #7f8c8d; line-height: 1.6; }
        .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 30px; }
        .feature-card { background: white; border-radius: 8px; padding: 25px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .feature-card h3 { color: #2c3e50; margin-bottom: 10px; }
        .feature-card p { color: #7f8c8d; font-size: 14px; margin-bottom: 15px; }
        .feature-card a { display: inline-block; background: #3498db; color: white; padding: 8px 16px; border-radius: 4px; text-decoration: none; font-size: 14px; }
        .feature-card a:hover { background: #2980b9; }
        .footer { text-align: center; padding: 20px; color: #95a5a6; font-size: 12px; margin-top: 40px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>OpenWiki</h1>
        <span class="version">v4.5.2</span>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/wiki/MainPage">Wiki</a>
        <a href="/search">Search</a>
        <a href="/recent">Recent Changes</a>
        <a href="/tools">Tools</a>
    </div>
    <div class="container">
        <div class="welcome-box">
            <h2>Welcome to OpenWiki</h2>
            <p>OpenWiki is a collaborative wiki platform for teams and communities. Create, edit, and share knowledge with ease.</p>
        </div>
        <div class="features">
            <div class="feature-card">
                <h3>Browse Pages</h3>
                <p>Explore existing wiki pages and documentation.</p>
                <a href="/wiki/MainPage">View Pages</a>
            </div>
            <div class="feature-card">
                <h3>Search Content</h3>
                <p>Find pages and content across the wiki.</p>
                <a href="/search">Search</a>
            </div>
            <div class="feature-card">
                <h3>Recent Activity</h3>
                <p>See the latest changes and updates.</p>
                <a href="/recent">View Activity</a>
            </div>
            <div class="feature-card">
                <h3>Tools</h3>
                <p>Access administrative and utility tools.</p>
                <a href="/tools">Open Tools</a>
            </div>
        </div>
    </div>
    <div class="footer">
        OpenWiki &copy; 2024 - Powered by OpenSource
    </div>
</body>
</html>
"""

WIKI_PAGE_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>OpenWiki - {page_name}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 15px 30px; }
        .header h1 { font-size: 24px; display: inline-block; }
        .header .version { font-size: 12px; color: #95a5a6; margin-left: 10px; }
        .nav { background: #34495e; padding: 10px 30px; }
        .nav a { color: #ecf0f1; text-decoration: none; margin-right: 20px; padding: 8px 15px; border-radius: 4px; }
        .nav a:hover { background: #3d566e; }
        .container { max-width: 1200px; margin: 30px auto; padding: 0 20px; }
        .wiki-content { background: white; border-radius: 8px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .wiki-content h2 { color: #2c3e50; margin-bottom: 15px; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
        .wiki-content p { color: #555; line-height: 1.8; margin-bottom: 15px; }
        .wiki-content ul { margin-left: 30px; color: #555; line-height: 2; }
        .sidebar { margin-top: 20px; background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .sidebar h4 { color: #2c3e50; margin-bottom: 10px; }
        .sidebar a { display: block; color: #3498db; text-decoration: none; padding: 5px 0; font-size: 14px; }
        .footer { text-align: center; padding: 20px; color: #95a5a6; font-size: 12px; margin-top: 40px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>OpenWiki</h1>
        <span class="version">v4.5.2</span>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/wiki/MainPage">Wiki</a>
        <a href="/search">Search</a>
        <a href="/recent">Recent Changes</a>
        <a href="/tools">Tools</a>
    </div>
    <div class="container">
        <div class="wiki-content">
            <h2>{page_name}</h2>
            {content}
        </div>
        <div class="sidebar">
            <h4>Related Pages</h4>
            <a href="/wiki/MainPage">Main Page</a>
            <a href="/wiki/GettingStarted">Getting Started</a>
            <a href="/wiki/Documentation">Documentation</a>
            <a href="/wiki/FAQ">FAQ</a>
        </div>
    </div>
    <div class="footer">
        OpenWiki &copy; 2024 - Powered by OpenSource
    </div>
</body>
</html>
"""

SEARCH_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>OpenWiki - Search</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 15px 30px; }
        .header h1 { font-size: 24px; display: inline-block; }
        .header .version { font-size: 12px; color: #95a5a6; margin-left: 10px; }
        .nav { background: #34495e; padding: 10px 30px; }
        .nav a { color: #ecf0f1; text-decoration: none; margin-right: 20px; padding: 8px 15px; border-radius: 4px; }
        .nav a:hover { background: #3d566e; }
        .container { max-width: 1200px; margin: 30px auto; padding: 0 20px; }
        .search-box { background: white; border-radius: 8px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .search-box h2 { color: #2c3e50; margin-bottom: 20px; }
        .search-box input[type="text"] { width: 70%; padding: 12px 15px; border: 2px solid #ddd; border-radius: 4px; font-size: 16px; }
        .search-box input[type="submit"] { padding: 12px 25px; background: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
        .search-results { margin-top: 20px; }
        .search-results p { color: #7f8c8d; font-style: italic; }
        .footer { text-align: center; padding: 20px; color: #95a5a6; font-size: 12px; margin-top: 40px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>OpenWiki</h1>
        <span class="version">v4.5.2</span>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/wiki/MainPage">Wiki</a>
        <a href="/search">Search</a>
        <a href="/recent">Recent Changes</a>
        <a href="/tools">Tools</a>
    </div>
    <div class="container">
        <div class="search-box">
            <h2>Search Wiki</h2>
            <form method="GET" action="/search">
                <input type="text" name="q" placeholder="Enter search query..." value="{query}">
                <input type="submit" value="Search">
            </form>
            <div class="search-results">
                {results}
            </div>
        </div>
    </div>
    <div class="footer">
        OpenWiki &copy; 2024 - Powered by OpenSource
    </div>
</body>
</html>
"""

RECENT_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>OpenWiki - Recent Changes</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 15px 30px; }
        .header h1 { font-size: 24px; display: inline-block; }
        .header .version { font-size: 12px; color: #95a5a6; margin-left: 10px; }
        .nav { background: #34495e; padding: 10px 30px; }
        .nav a { color: #ecf0f1; text-decoration: none; margin-right: 20px; padding: 8px 15px; border-radius: 4px; }
        .nav a:hover { background: #3d566e; }
        .container { max-width: 1200px; margin: 30px auto; padding: 0 20px; }
        .content-box { background: white; border-radius: 8px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .content-box h2 { color: #2c3e50; margin-bottom: 20px; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
        .change-list { list-style: none; }
        .change-list li { padding: 15px 0; border-bottom: 1px solid #eee; }
        .change-list li:last-child { border-bottom: none; }
        .change-list a { color: #3498db; text-decoration: none; font-weight: 500; }
        .change-list .meta { color: #95a5a6; font-size: 12px; margin-top: 5px; }
        .footer { text-align: center; padding: 20px; color: #95a5a6; font-size: 12px; margin-top: 40px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>OpenWiki</h1>
        <span class="version">v4.5.2</span>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/wiki/MainPage">Wiki</a>
        <a href="/search">Search</a>
        <a href="/recent">Recent Changes</a>
        <a href="/tools">Tools</a>
    </div>
    <div class="container">
        <div class="content-box">
            <h2>Recent Changes</h2>
            <ul class="change-list">
                <li>
                    <a href="/wiki/MainPage">MainPage</a>
                    <div class="meta">Modified 2 hours ago by admin</div>
                </li>
                <li>
                    <a href="/wiki/GettingStarted">Getting Started</a>
                    <div class="meta">Modified 1 day ago by editor</div>
                </li>
                <li>
                    <a href="/wiki/Documentation">Documentation</a>
                    <div class="meta">Modified 3 days ago by admin</div>
                </li>
                <li>
                    <a href="/wiki/FAQ">FAQ</a>
                    <div class="meta">Modified 1 week ago by contributor</div>
                </li>
            </ul>
        </div>
    </div>
    <div class="footer">
        OpenWiki &copy; 2024 - Powered by OpenSource
    </div>
</body>
</html>
"""

TOOLS_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>OpenWiki - Tools</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 15px 30px; }
        .header h1 { font-size: 24px; display: inline-block; }
        .header .version { font-size: 12px; color: #95a5a6; margin-left: 10px; }
        .nav { background: #34495e; padding: 10px 30px; }
        .nav a { color: #ecf0f1; text-decoration: none; margin-right: 20px; padding: 8px 15px; border-radius: 4px; }
        .nav a:hover { background: #3d566e; }
        .container { max-width: 1200px; margin: 30px auto; padding: 0 20px; }
        .content-box { background: white; border-radius: 8px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .content-box h2 { color: #2c3e50; margin-bottom: 20px; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
        .tools-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 20px; }
        .tool-item { background: #f8f9fa; border-radius: 6px; padding: 20px; text-align: center; }
        .tool-item a { color: #3498db; text-decoration: none; font-weight: 500; }
        .tool-item p { color: #7f8c8d; font-size: 12px; margin-top: 8px; }
        .footer { text-align: center; padding: 20px; color: #95a5a6; font-size: 12px; margin-top: 40px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>OpenWiki</h1>
        <span class="version">v4.5.2</span>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/wiki/MainPage">Wiki</a>
        <a href="/search">Search</a>
        <a href="/recent">Recent Changes</a>
        <a href="/tools">Tools</a>
    </div>
    <div class="container">
        <div class="content-box">
            <h2>Wiki Tools</h2>
            <div class="tools-grid">
                <div class="tool-item">
                    <a href="/tools/attach">Attach Files</a>
                    <p>Upload attachments to wiki pages</p>
                </div>
                <div class="tool-item">
                    <a href="/tools/export">Export</a>
                    <p>Export wiki content</p>
                </div>
                <div class="tool-item">
                    <a href="/tools/import">Import</a>
                    <p>Import content from files</p>
                </div>
                <div class="tool-item">
                    <a href="/tools/backup">Backup</a>
                    <p>Create wiki backups</p>
                </div>
            </div>
        </div>
    </div>
    <div class="footer">
        OpenWiki &copy; 2024 - Powered by OpenSource
    </div>
</body>
</html>
"""

ATTACH_TOOL_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>OpenWiki - Attach Files</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 15px 30px; }
        .header h1 { font-size: 24px; display: inline-block; }
        .header .version { font-size: 12px; color: #95a5a6; margin-left: 10px; }
        .nav { background: #34495e; padding: 10px 30px; }
        .nav a { color: #ecf0f1; text-decoration: none; margin-right: 20px; padding: 8px 15px; border-radius: 4px; }
        .nav a:hover { background: #3d566e; }
        .container { max-width: 1200px; margin: 30px auto; padding: 0 20px; }
        .content-box { background: white; border-radius: 8px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .content-box h2 { color: #2c3e50; margin-bottom: 20px; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
        .page-list { list-style: none; }
        .page-list li { padding: 10px 0; border-bottom: 1px solid #eee; }
        .page-list a { color: #3498db; text-decoration: none; }
        .footer { text-align: center; padding: 20px; color: #95a5a6; font-size: 12px; margin-top: 40px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>OpenWiki</h1>
        <span class="version">v4.5.2</span>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/wiki/MainPage">Wiki</a>
        <a href="/search">Search</a>
        <a href="/recent">Recent Changes</a>
        <a href="/tools">Tools</a>
    </div>
    <div class="container">
        <div class="content-box">
            <h2>Attach Files</h2>
            <p style="margin-bottom: 20px; color: #555;">Select a wiki page to attach files to:</p>
            <ul class="page-list">
                <li><a href="/wiki/MainPage/upload">MainPage</a></li>
                <li><a href="/wiki/GettingStarted/upload">Getting Started</a></li>
                <li><a href="/wiki/Documentation/upload">Documentation</a></li>
                <li><a href="/wiki/FAQ/upload">FAQ</a></li>
            </ul>
        </div>
    </div>
    <div class="footer">
        OpenWiki &copy; 2024 - Powered by OpenSource
    </div>
</body>
</html>
"""

# The vulnerable upload form - file parameter is reflected without sanitization
UPLOAD_FORM_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>OpenWiki - Upload File</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; }}
        .header {{ background: #2c3e50; color: white; padding: 15px 30px; }}
        .header h1 {{ font-size: 24px; display: inline-block; }}
        .header .version {{ font-size: 12px; color: #95a5a6; margin-left: 10px; }}
        .nav {{ background: #34495e; padding: 10px 30px; }}
        .nav a {{ color: #ecf0f1; text-decoration: none; margin-right: 20px; padding: 8px 15px; border-radius: 4px; }}
        .nav a:hover {{ background: #3d566e; }}
        .container {{ max-width: 1200px; margin: 30px auto; padding: 0 20px; }}
        .content-box {{ background: white; border-radius: 8px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .content-box h2 {{ color: #2c3e50; margin-bottom: 20px; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        .content-box h3 {{ color: #34495e; margin: 20px 0 15px 0; }}
        .upload-form {{ margin-top: 20px; }}
        .upload-form input[type="file"] {{ margin: 10px 0; }}
        .upload-form input[type="submit"] {{ padding: 10px 20px; background: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer; }}
        .breadcrumb {{ color: #7f8c8d; margin-bottom: 15px; font-size: 14px; }}
        .breadcrumb a {{ color: #3498db; text-decoration: none; }}
        .footer {{ text-align: center; padding: 20px; color: #95a5a6; font-size: 12px; margin-top: 40px; }}
        .result-box {{ background: #f8f9fa; border-radius: 6px; padding: 20px; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>OpenWiki</h1>
        <span class="version">v4.5.2</span>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/wiki/MainPage">Wiki</a>
        <a href="/search">Search</a>
        <a href="/recent">Recent Changes</a>
        <a href="/tools">Tools</a>
    </div>
    <div class="container">
        <div class="content-box">
            <div class="breadcrumb">
                <a href="/">Home</a> &gt; <a href="/tools">Tools</a> &gt; <a href="/tools/attach">Attach</a> &gt; {page_name}
            </div>
            <h2>Upload Attachment</h2>
            <h3>Upload form for file: {file_param}</h3>
            <form class="upload-form" method="POST" enctype="multipart/form-data">
                <p>Select a file to attach to this wiki page:</p>
                <input type="file" name="attachment" accept="*/*"><br><br>
                <input type="submit" value="Upload File">
            </form>
            {result}
        </div>
    </div>
    <div class="footer">
        OpenWiki &copy; 2024 - Powered by OpenSource
    </div>
</body>
</html>
"""

# Result templates for XSS checking
SUCCESS_RESULT = '<div class="result-box" style="background: #d4edda; border: 1px solid #c3e6cb;"><strong>Congratulations!</strong> Flag: {flag}</div>'
FAILED_RESULT = '<div class="result-box" style="background: #f8d7da; border: 1px solid #f5c6cb;"><strong>Upload failed.</strong> Please try again.</div>'
WRONG_ALERT_RESULT = '<div class="result-box" style="background: #fff3cd; border: 1px solid #ffeeba;"><strong>Alert detected:</strong> {alert_msg} (Expected: XSS)</div>'

# Wiki page content for different pages
WIKI_PAGES = {
    "MainPage": """
        <p>Welcome to the OpenWiki main page. This is a collaborative wiki platform where you can create, edit, and share knowledge with your team.</p>
        <p>OpenWiki supports:</p>
        <ul>
            <li>Rich text editing</li>
            <li>File attachments</li>
            <li>Version history</li>
            <li>User permissions</li>
        </ul>
        <p>Get started by exploring the navigation menu or check out the <a href="/wiki/GettingStarted">Getting Started</a> guide.</p>
    """,
    "GettingStarted": """
        <p>This guide will help you get started with OpenWiki.</p>
        <p><strong>Creating Pages:</strong> Click on any link to create a new page. If the page doesn't exist, you'll be prompted to create it.</p>
        <p><strong>Editing:</strong> Each page has an edit button that allows you to modify its content using our rich text editor.</p>
        <p><strong>Attachments:</strong> You can attach files to any wiki page using the <a href="/tools/attach">Attach Files</a> tool.</p>
    """,
    "Documentation": """
        <p>OpenWiki documentation and reference materials.</p>
        <p><strong>API Reference:</strong> OpenWiki provides a REST API for programmatic access.</p>
        <p><strong>Configuration:</strong> The wiki can be configured through the admin panel or configuration files.</p>
        <p><strong>Plugins:</strong> Extend functionality with community plugins.</p>
    """,
    "FAQ": """
        <p><strong>Q: How do I reset my password?</strong></p>
        <p>A: Contact your wiki administrator or use the password reset feature on the login page.</p>
        <p><strong>Q: Can I export my wiki content?</strong></p>
        <p>A: Yes, use the <a href="/tools/export">Export</a> tool to download your content.</p>
        <p><strong>Q: How do I upload files?</strong></p>
        <p>A: Navigate to the page where you want to attach a file and use the <a href="/tools/attach">Attach Files</a> tool.</p>
    """
}
