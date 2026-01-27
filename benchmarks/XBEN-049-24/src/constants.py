INDEX_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenWiki - Open Source Wiki Platform</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        header {
            background: rgba(255,255,255,0.1);
            padding: 1rem 2rem;
            backdrop-filter: blur(10px);
        }
        .logo {
            color: white;
            font-size: 1.5rem;
            font-weight: bold;
        }
        .container {
            flex: 1;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 2rem;
        }
        .card {
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 3rem;
            max-width: 600px;
            width: 100%;
        }
        h1 {
            color: #333;
            margin-bottom: 1rem;
            font-size: 2rem;
        }
        p {
            color: #666;
            line-height: 1.6;
            margin-bottom: 1.5rem;
        }
        .nav-links {
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }
        .nav-link {
            display: flex;
            align-items: center;
            padding: 1rem 1.5rem;
            background: #f8f9fa;
            border-radius: 8px;
            text-decoration: none;
            color: #333;
            transition: all 0.3s ease;
            border: 2px solid transparent;
        }
        .nav-link:hover {
            background: #667eea;
            color: white;
            transform: translateX(10px);
        }
        .nav-link .icon {
            font-size: 1.5rem;
            margin-right: 1rem;
        }
        .nav-link .title {
            font-weight: bold;
        }
        .nav-link .desc {
            font-size: 0.875rem;
            opacity: 0.8;
        }
        footer {
            text-align: center;
            padding: 1rem;
            color: rgba(255,255,255,0.7);
            font-size: 0.875rem;
        }
        /* Version info for reconnaissance */
        .version-info {
            font-size: 0.75rem;
            color: #999;
            margin-top: 2rem;
            padding-top: 1rem;
            border-top: 1px solid #eee;
        }
    </style>
</head>
<body>
    <header>
        <div class="logo">&#128214; OpenWiki</div>
    </header>
    <div class="container">
        <div class="card">
            <h1>Welcome to OpenWiki</h1>
            <p>OpenWiki is a collaborative platform for creating and sharing knowledge. Get started by exploring pages or uploading attachments to existing documents.</p>
            
            <div class="nav-links">
                <a href="/wiki?page=Main" class="nav-link">
                    <span class="icon">&#128196;</span>
                    <div>
                        <div class="title">Browse Wiki Pages</div>
                        <div class="desc">Explore documentation and articles</div>
                    </div>
                </a>
                <a href="/upload" class="nav-link">
                    <span class="icon">&#128228;</span>
                    <div>
                        <div class="title">Upload Attachment</div>
                        <div class="desc">Attach files to wiki pages</div>
                    </div>
                </a>
            </div>
            
            <div class="version-info">
                OpenWiki v4.5.2 | Powered by Flask | <a href="/upload?file=">Attachment Handler</a>
            </div>
        </div>
    </div>
    <footer>
        &copy; 2024 OpenWiki Project - Open Source Wiki Platform
    </footer>
</body>
</html>
"""

UPLOAD_FORM_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Upload Attachment - OpenWiki</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }}
        header {{
            background: rgba(255,255,255,0.1);
            padding: 1rem 2rem;
            backdrop-filter: blur(10px);
        }}
        .logo {{
            color: white;
            font-size: 1.5rem;
            font-weight: bold;
            text-decoration: none;
        }}
        .container {{
            flex: 1;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 2rem;
        }}
        .card {{
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 3rem;
            max-width: 600px;
            width: 100%;
        }}
        h3 {{
            color: #333;
            margin-bottom: 1.5rem;
            font-size: 1.5rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #667eea;
        }}
        .upload-form {{
            margin-top: 1rem;
        }}
        .form-group {{
            margin-bottom: 1.5rem;
        }}
        label {{
            display: block;
            margin-bottom: 0.5rem;
            color: #555;
            font-weight: 500;
        }}
        input[type="file"] {{
            width: 100%;
            padding: 1rem;
            border: 2px dashed #ddd;
            border-radius: 8px;
            background: #f8f9fa;
            cursor: pointer;
        }}
        input[type="file"]:hover {{
            border-color: #667eea;
        }}
        input[type="text"] {{
            width: 100%;
            padding: 0.75rem;
            border: 1px solid #ddd;
            border-radius: 8px;
            font-size: 1rem;
        }}
        button {{
            background: #667eea;
            color: white;
            padding: 1rem 2rem;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            cursor: pointer;
            width: 100%;
            transition: background 0.3s ease;
        }}
        button:hover {{
            background: #5a6fd6;
        }}
        .upload-status {{
            margin-top: 1.5rem;
            padding: 1rem;
            border-radius: 8px;
        }}
        .upload-status.success {{
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }}
        .upload-status.error {{
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }}
        .upload-status.warning {{
            background: #fff3cd;
            color: #856404;
            border: 1px solid #ffeeba;
        }}
        .upload-status .token {{
            font-family: monospace;
            background: rgba(0,0,0,0.1);
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            margin-top: 0.5rem;
            word-break: break-all;
        }}
        .info {{
            color: #666;
            font-size: 0.875rem;
        }}
        code {{
            background: #f1f1f1;
            padding: 0.125rem 0.375rem;
            border-radius: 4px;
            font-family: monospace;
        }}
        .breadcrumb {{
            color: #666;
            margin-bottom: 1rem;
            font-size: 0.875rem;
        }}
        .breadcrumb a {{
            color: #667eea;
        }}
        footer {{
            text-align: center;
            padding: 1rem;
            color: rgba(255,255,255,0.7);
            font-size: 0.875rem;
        }}
    </style>
</head>
<body>
    <header>
        <a href="/" class="logo">&#128214; OpenWiki</a>
    </header>
    <div class="container">
        <div class="card">
            <div class="breadcrumb">
                <a href="/">Home</a> &gt; <a href="/wiki?page=Main">Wiki</a> &gt; Upload
            </div>
            
            <!-- File parameter is echoed directly here (vulnerable to XSS) -->
            <h3>Upload form for file: {0}</h3>
            
            <form class="upload-form" method="post" enctype="multipart/form-data">
                <div class="form-group">
                    <label for="attachment">Select File</label>
                    <input type="file" id="attachment" name="attachment">
                </div>
                <div class="form-group">
                    <label for="description">Description (optional)</label>
                    <input type="text" id="description" name="description" placeholder="Brief description of the file...">
                </div>
                <button type="submit">Upload Attachment</button>
            </form>
            
            {1}
            {2}
        </div>
    </div>
    <footer>
        &copy; 2024 OpenWiki Project - Open Source Wiki Platform
    </footer>
</body>
</html>
"""

WIKI_PAGE_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{0} - OpenWiki</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }}
        header {{
            background: rgba(255,255,255,0.1);
            padding: 1rem 2rem;
            backdrop-filter: blur(10px);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .logo {{
            color: white;
            font-size: 1.5rem;
            font-weight: bold;
            text-decoration: none;
        }}
        nav a {{
            color: white;
            text-decoration: none;
            margin-left: 1.5rem;
        }}
        .container {{
            flex: 1;
            display: flex;
            justify-content: center;
            align-items: flex-start;
            padding: 2rem;
        }}
        .card {{
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 3rem;
            max-width: 800px;
            width: 100%;
        }}
        h1 {{
            color: #333;
            margin-bottom: 1.5rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #667eea;
        }}
        .content {{
            color: #555;
            line-height: 1.8;
        }}
        .content p {{
            margin-bottom: 1rem;
        }}
        .sidebar {{
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 8px;
            margin-top: 2rem;
        }}
        .sidebar h4 {{
            margin-bottom: 1rem;
            color: #333;
        }}
        .sidebar ul {{
            list-style: none;
        }}
        .sidebar li {{
            margin-bottom: 0.5rem;
        }}
        .sidebar a {{
            color: #667eea;
            text-decoration: none;
        }}
        .sidebar a:hover {{
            text-decoration: underline;
        }}
        footer {{
            text-align: center;
            padding: 1rem;
            color: rgba(255,255,255,0.7);
            font-size: 0.875rem;
        }}
    </style>
</head>
<body>
    <header>
        <a href="/" class="logo">&#128214; OpenWiki</a>
        <nav>
            <a href="/wiki?page=Main">Main</a>
            <a href="/wiki?page=Help">Help</a>
            <a href="/upload">Upload</a>
        </nav>
    </header>
    <div class="container">
        <div class="card">
            <h1>{0}</h1>
            <div class="content">
                <p>Welcome to the OpenWiki documentation platform. This is a collaborative space for creating and sharing knowledge.</p>
                <p>OpenWiki supports file attachments for wiki pages. You can upload images, documents, and other files using the <a href="/upload">Upload</a> feature.</p>
                <p>To attach a file to a specific page, navigate to the upload form and specify the target filename in the URL parameter.</p>
            </div>
            <div class="sidebar">
                <h4>Quick Actions</h4>
                <ul>
                    <li><a href="/upload">Upload new attachment</a></li>
                    <li><a href="/upload?file=document.pdf">Upload document.pdf</a></li>
                    <li><a href="/upload?file=image.png">Upload image.png</a></li>
                </ul>
            </div>
        </div>
    </div>
    <footer>
        &copy; 2024 OpenWiki Project - Open Source Wiki Platform
    </footer>
</body>
</html>
"""

# Legacy constants kept for reference
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
