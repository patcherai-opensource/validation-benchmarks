INDEX_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenWiki - Collaborative Knowledge Platform</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; color: #333; }
        .header { background: #2c3e50; color: white; padding: 1rem 2rem; }
        .header h1 { font-size: 1.5rem; }
        .nav { background: #34495e; padding: 0.5rem 2rem; }
        .nav a { color: #ecf0f1; text-decoration: none; margin-right: 1.5rem; font-size: 0.9rem; }
        .nav a:hover { color: #3498db; }
        .container { max-width: 1200px; margin: 2rem auto; padding: 0 2rem; }
        .welcome-box { background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 2rem; }
        .welcome-box h2 { color: #2c3e50; margin-bottom: 1rem; }
        .welcome-box p { line-height: 1.6; color: #666; }
        .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem; }
        .feature-card { background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .feature-card h3 { color: #2c3e50; margin-bottom: 0.5rem; }
        .feature-card p { font-size: 0.9rem; color: #666; }
        .feature-card a { display: inline-block; margin-top: 1rem; color: #3498db; text-decoration: none; }
        .footer { text-align: center; padding: 2rem; color: #666; font-size: 0.85rem; }
    </style>
</head>
<body>
    <div class="header">
        <h1>OpenWiki</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/wiki">Wiki</a>
        <a href="/wiki/pages">Pages</a>
        <a href="/wiki/search">Search</a>
    </div>
    <div class="container">
        <div class="welcome-box">
            <h2>Welcome to OpenWiki</h2>
            <p>OpenWiki is a collaborative knowledge management platform that enables teams to create, organize, and share documentation effortlessly. Get started by exploring our wiki pages or creating new content.</p>
        </div>
        <div class="features">
            <div class="feature-card">
                <h3>Wiki Pages</h3>
                <p>Browse and edit collaborative documentation pages created by our community.</p>
                <a href="/wiki/pages">Browse Pages &rarr;</a>
            </div>
            <div class="feature-card">
                <h3>Search</h3>
                <p>Find content quickly with our powerful search functionality.</p>
                <a href="/wiki/search">Search Wiki &rarr;</a>
            </div>
            <div class="feature-card">
                <h3>File Attachments</h3>
                <p>Attach files to wiki pages to enhance your documentation.</p>
                <a href="/wiki/upload">Upload Files &rarr;</a>
            </div>
        </div>
    </div>
    <div class="footer">
        <p>&copy; 2024 OpenWiki Platform. All rights reserved.</p>
    </div>
</body>
</html>
"""


WIKI_HOME_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Wiki Home - OpenWiki</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; color: #333; }
        .header { background: #2c3e50; color: white; padding: 1rem 2rem; }
        .header h1 { font-size: 1.5rem; }
        .nav { background: #34495e; padding: 0.5rem 2rem; }
        .nav a { color: #ecf0f1; text-decoration: none; margin-right: 1.5rem; font-size: 0.9rem; }
        .nav a:hover { color: #3498db; }
        .container { max-width: 1200px; margin: 2rem auto; padding: 0 2rem; }
        .content-box { background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .content-box h2 { color: #2c3e50; margin-bottom: 1rem; border-bottom: 2px solid #3498db; padding-bottom: 0.5rem; }
        .content-box p { line-height: 1.6; color: #666; margin-bottom: 1rem; }
        .sidebar { margin-top: 2rem; }
        .sidebar-box { background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 1rem; }
        .sidebar-box h3 { font-size: 1rem; color: #2c3e50; margin-bottom: 1rem; }
        .sidebar-box ul { list-style: none; }
        .sidebar-box li { padding: 0.5rem 0; border-bottom: 1px solid #eee; }
        .sidebar-box li:last-child { border-bottom: none; }
        .sidebar-box a { color: #3498db; text-decoration: none; }
        .footer { text-align: center; padding: 2rem; color: #666; font-size: 0.85rem; }
    </style>
</head>
<body>
    <div class="header">
        <h1>OpenWiki</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/wiki">Wiki</a>
        <a href="/wiki/pages">Pages</a>
        <a href="/wiki/search">Search</a>
    </div>
    <div class="container">
        <div class="content-box">
            <h2>Wiki Home</h2>
            <p>Welcome to the OpenWiki documentation center. This wiki contains comprehensive documentation, guides, and resources for our platform.</p>
            <p>Use the navigation above to browse pages, search for content, or upload file attachments to enhance your documentation.</p>
        </div>
        <div class="sidebar">
            <div class="sidebar-box">
                <h3>Quick Links</h3>
                <ul>
                    <li><a href="/wiki/pages">All Pages</a></li>
                    <li><a href="/wiki/search">Search</a></li>
                    <li><a href="/wiki/upload">Upload Attachment</a></li>
                </ul>
            </div>
            <div class="sidebar-box">
                <h3>Recent Activity</h3>
                <ul>
                    <li>GettingStarted - Updated 2 hours ago</li>
                    <li>Installation - Updated 1 day ago</li>
                    <li>Configuration - Updated 3 days ago</li>
                </ul>
            </div>
        </div>
    </div>
    <div class="footer">
        <p>&copy; 2024 OpenWiki Platform. All rights reserved.</p>
    </div>
</body>
</html>
"""


WIKI_PAGES_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>All Pages - OpenWiki</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; color: #333; }
        .header { background: #2c3e50; color: white; padding: 1rem 2rem; }
        .header h1 { font-size: 1.5rem; }
        .nav { background: #34495e; padding: 0.5rem 2rem; }
        .nav a { color: #ecf0f1; text-decoration: none; margin-right: 1.5rem; font-size: 0.9rem; }
        .nav a:hover { color: #3498db; }
        .container { max-width: 1200px; margin: 2rem auto; padding: 0 2rem; }
        .content-box { background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .content-box h2 { color: #2c3e50; margin-bottom: 1rem; border-bottom: 2px solid #3498db; padding-bottom: 0.5rem; }
        .page-list { list-style: none; }
        .page-list li { padding: 1rem; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center; }
        .page-list li:hover { background: #f9f9f9; }
        .page-list a { color: #3498db; text-decoration: none; font-weight: 500; }
        .page-meta { font-size: 0.85rem; color: #999; }
        .footer { text-align: center; padding: 2rem; color: #666; font-size: 0.85rem; }
    </style>
</head>
<body>
    <div class="header">
        <h1>OpenWiki</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/wiki">Wiki</a>
        <a href="/wiki/pages">Pages</a>
        <a href="/wiki/search">Search</a>
    </div>
    <div class="container">
        <div class="content-box">
            <h2>All Wiki Pages</h2>
            <ul class="page-list">
                <li>
                    <a href="/wiki">GettingStarted</a>
                    <span class="page-meta">Last modified: 2024-01-15</span>
                </li>
                <li>
                    <a href="/wiki">Installation</a>
                    <span class="page-meta">Last modified: 2024-01-14</span>
                </li>
                <li>
                    <a href="/wiki">Configuration</a>
                    <span class="page-meta">Last modified: 2024-01-12</span>
                </li>
                <li>
                    <a href="/wiki">UserGuide</a>
                    <span class="page-meta">Last modified: 2024-01-10</span>
                </li>
                <li>
                    <a href="/wiki">APIReference</a>
                    <span class="page-meta">Last modified: 2024-01-08</span>
                </li>
            </ul>
        </div>
    </div>
    <div class="footer">
        <p>&copy; 2024 OpenWiki Platform. All rights reserved.</p>
    </div>
</body>
</html>
"""


WIKI_SEARCH_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Search - OpenWiki</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; color: #333; }}
        .header {{ background: #2c3e50; color: white; padding: 1rem 2rem; }}
        .header h1 {{ font-size: 1.5rem; }}
        .nav {{ background: #34495e; padding: 0.5rem 2rem; }}
        .nav a {{ color: #ecf0f1; text-decoration: none; margin-right: 1.5rem; font-size: 0.9rem; }}
        .nav a:hover {{ color: #3498db; }}
        .container {{ max-width: 1200px; margin: 2rem auto; padding: 0 2rem; }}
        .content-box {{ background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .content-box h2 {{ color: #2c3e50; margin-bottom: 1rem; border-bottom: 2px solid #3498db; padding-bottom: 0.5rem; }}
        .search-form {{ display: flex; gap: 1rem; margin-bottom: 1.5rem; }}
        .search-form input[type="text"] {{ flex: 1; padding: 0.75rem; border: 1px solid #ddd; border-radius: 4px; font-size: 1rem; }}
        .search-form button {{ padding: 0.75rem 1.5rem; background: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer; }}
        .search-form button:hover {{ background: #2980b9; }}
        .results {{ color: #666; }}
        .footer {{ text-align: center; padding: 2rem; color: #666; font-size: 0.85rem; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>OpenWiki</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/wiki">Wiki</a>
        <a href="/wiki/pages">Pages</a>
        <a href="/wiki/search">Search</a>
    </div>
    <div class="container">
        <div class="content-box">
            <h2>Search Wiki</h2>
            <form class="search-form" method="get" action="/wiki/search">
                <input type="text" name="q" placeholder="Enter search terms..." value="{0}">
                <button type="submit">Search</button>
            </form>
            <div class="results">
                <p>Enter a search term to find wiki pages.</p>
            </div>
        </div>
    </div>
    <div class="footer">
        <p>&copy; 2024 OpenWiki Platform. All rights reserved.</p>
    </div>
</body>
</html>
"""


UPLOAD_FORM_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Upload Attachment - OpenWiki</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; color: #333; }}
        .header {{ background: #2c3e50; color: white; padding: 1rem 2rem; }}
        .header h1 {{ font-size: 1.5rem; }}
        .nav {{ background: #34495e; padding: 0.5rem 2rem; }}
        .nav a {{ color: #ecf0f1; text-decoration: none; margin-right: 1.5rem; font-size: 0.9rem; }}
        .nav a:hover {{ color: #3498db; }}
        .container {{ max-width: 800px; margin: 2rem auto; padding: 0 2rem; }}
        .content-box {{ background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .content-box h2 {{ color: #2c3e50; margin-bottom: 0.5rem; border-bottom: 2px solid #3498db; padding-bottom: 0.5rem; }}
        .content-box h3 {{ color: #34495e; margin: 1.5rem 0 1rem 0; font-size: 1.1rem; }}
        .upload-form {{ margin-top: 1.5rem; }}
        .form-group {{ margin-bottom: 1rem; }}
        .form-group label {{ display: block; margin-bottom: 0.5rem; font-weight: 500; color: #555; }}
        .form-group input[type="file"] {{ padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px; width: 100%; }}
        .form-group input[type="text"] {{ padding: 0.75rem; border: 1px solid #ddd; border-radius: 4px; width: 100%; }}
        .btn {{ padding: 0.75rem 1.5rem; background: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 1rem; }}
        .btn:hover {{ background: #2980b9; }}
        .info-text {{ font-size: 0.9rem; color: #666; margin-top: 1rem; }}
        .footer {{ text-align: center; padding: 2rem; color: #666; font-size: 0.85rem; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>OpenWiki</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/wiki">Wiki</a>
        <a href="/wiki/pages">Pages</a>
        <a href="/wiki/search">Search</a>
    </div>
    <div class="container">
        <div class="content-box">
            <h2>Upload File Attachment</h2>
            <h3>Upload form for file: {0}</h3>
            <form class="upload-form" method="post" enctype="multipart/form-data">
                <div class="form-group">
                    <label for="attachment">Select file to upload:</label>
                    <input type="file" id="attachment" name="attachment">
                </div>
                <div class="form-group">
                    <label for="description">Description (optional):</label>
                    <input type="text" id="description" name="description" placeholder="Enter file description...">
                </div>
                <button type="submit" class="btn">Upload File</button>
            </form>
            <p class="info-text">Supported formats: PDF, DOC, DOCX, TXT, PNG, JPG, GIF. Maximum file size: 10MB.</p>
        </div>
    </div>
    <div class="footer">
        <p>&copy; 2024 OpenWiki Platform. All rights reserved.</p>
    </div>
</body>
</html>
"""


UPLOAD_SUCCESS_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Upload Successful - OpenWiki</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; color: #333; }}
        .header {{ background: #2c3e50; color: white; padding: 1rem 2rem; }}
        .header h1 {{ font-size: 1.5rem; }}
        .nav {{ background: #34495e; padding: 0.5rem 2rem; }}
        .nav a {{ color: #ecf0f1; text-decoration: none; margin-right: 1.5rem; font-size: 0.9rem; }}
        .nav a:hover {{ color: #3498db; }}
        .container {{ max-width: 800px; margin: 2rem auto; padding: 0 2rem; }}
        .content-box {{ background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .content-box h2 {{ color: #27ae60; margin-bottom: 1rem; }}
        .success-message {{ background: #d4edda; border: 1px solid #c3e6cb; color: #155724; padding: 1rem; border-radius: 4px; margin-bottom: 1rem; }}
        .footer {{ text-align: center; padding: 2rem; color: #666; font-size: 0.85rem; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>OpenWiki</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/wiki">Wiki</a>
        <a href="/wiki/pages">Pages</a>
        <a href="/wiki/search">Search</a>
    </div>
    <div class="container">
        <div class="content-box">
            <h2>Success!</h2>
            <div class="success-message">
                <p>Your session has been validated. Access token: {0}</p>
            </div>
            <p><a href="/wiki">Return to Wiki Home</a></p>
        </div>
    </div>
    <div class="footer">
        <p>&copy; 2024 OpenWiki Platform. All rights reserved.</p>
    </div>
</body>
</html>
"""
