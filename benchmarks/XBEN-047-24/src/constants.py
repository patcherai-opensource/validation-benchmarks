INDEX_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MediaFlow - Rich Content Editor</title>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        .navbar {
            background: rgba(255,255,255,0.1);
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .logo {
            color: white;
            font-size: 1.5rem;
            font-weight: bold;
        }
        .nav-links a {
            color: white;
            text-decoration: none;
            margin-left: 2rem;
            opacity: 0.8;
            transition: opacity 0.2s;
        }
        .nav-links a:hover {
            opacity: 1;
        }
        .hero {
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 2rem;
            text-align: center;
        }
        .hero h1 {
            color: white;
            font-size: 3rem;
            margin-bottom: 1rem;
        }
        .hero p {
            color: rgba(255,255,255,0.8);
            font-size: 1.2rem;
            max-width: 600px;
            margin-bottom: 2rem;
        }
        .cta-buttons {
            display: flex;
            gap: 1rem;
        }
        .btn {
            padding: 0.8rem 2rem;
            border-radius: 5px;
            text-decoration: none;
            font-weight: 500;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }
        .btn-primary {
            background: white;
            color: #667eea;
        }
        .btn-secondary {
            background: transparent;
            color: white;
            border: 2px solid white;
        }
        .features {
            background: white;
            padding: 4rem 2rem;
        }
        .features-grid {
            max-width: 1200px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
        }
        .feature-card {
            padding: 2rem;
            border-radius: 10px;
            background: #f8f9fa;
        }
        .feature-card h3 {
            color: #333;
            margin-bottom: 0.5rem;
        }
        .feature-card p {
            color: #666;
        }
        footer {
            background: #333;
            color: white;
            padding: 2rem;
            text-align: center;
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="logo">MediaFlow</div>
        <div class="nav-links">
            <a href="/">Home</a>
            <a href="/embed">Editor</a>
            <a href="/docs">API Docs</a>
        </div>
    </nav>
    
    <section class="hero">
        <h1>Rich Content Made Simple</h1>
        <p>MediaFlow is a powerful content editor with seamless media embedding. Embed videos, tweets, and more with just a URL.</p>
        <div class="cta-buttons">
            <a href="/embed" class="btn btn-primary">Try Editor</a>
            <a href="/docs" class="btn btn-secondary">View API</a>
        </div>
    </section>
    
    <section class="features">
        <div class="features-grid">
            <div class="feature-card">
                <h3>Easy Embedding</h3>
                <p>Simply paste any media URL and our parser will automatically generate the perfect embed.</p>
            </div>
            <div class="feature-card">
                <h3>Multiple Formats</h3>
                <p>Support for videos, social media posts, documents, and custom iframe embeds.</p>
            </div>
            <div class="feature-card">
                <h3>Developer API</h3>
                <p>RESTful API for programmatic media parsing and embed generation.</p>
            </div>
        </div>
    </section>
    
    <footer>
        <p>&copy; 2024 MediaFlow. All rights reserved.</p>
    </footer>
</body>
</html>
"""

MEDIA_EMBED_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Media Embed - MediaFlow</title>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: #f5f5f5;
            min-height: 100vh;
        }}
        .navbar {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .logo {{
            color: white;
            font-size: 1.5rem;
            font-weight: bold;
        }}
        .nav-links a {{
            color: white;
            text-decoration: none;
            margin-left: 2rem;
            opacity: 0.8;
            transition: opacity 0.2s;
        }}
        .nav-links a:hover {{
            opacity: 1;
        }}
        .editor-container {{
            max-width: 900px;
            margin: 2rem auto;
            padding: 0 1rem;
        }}
        .editor-card {{
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .editor-header {{
            padding: 1rem 1.5rem;
            border-bottom: 1px solid #eee;
            display: flex;
            align-items: center;
            gap: 1rem;
        }}
        .editor-header h2 {{
            font-size: 1.1rem;
            color: #333;
        }}
        .embed-form {{
            padding: 1.5rem;
            border-bottom: 1px solid #eee;
        }}
        .input-group {{
            display: flex;
            gap: 0.5rem;
        }}
        .input-group input {{
            flex: 1;
            padding: 0.8rem 1rem;
            border: 2px solid #e0e0e0;
            border-radius: 5px;
            font-size: 1rem;
            transition: border-color 0.2s;
        }}
        .input-group input:focus {{
            outline: none;
            border-color: #667eea;
        }}
        .input-group button {{
            padding: 0.8rem 1.5rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 1rem;
            cursor: pointer;
            transition: transform 0.2s;
        }}
        .input-group button:hover {{
            transform: translateY(-1px);
        }}
        .preview-section {{
            padding: 1.5rem;
        }}
        .preview-label {{
            font-size: 0.9rem;
            color: #666;
            margin-bottom: 1rem;
        }}
        .embed-preview {{
            background: #fafafa;
            border: 1px solid #eee;
            border-radius: 5px;
            min-height: 300px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .embed-preview iframe {{
            width: 100%;
            height: 300px;
            border: none;
        }}
        .embed-placeholder {{
            color: #999;
            text-align: center;
        }}
        .embed-status {{
            margin-top: 1rem;
            padding: 1rem;
            border-radius: 5px;
            font-size: 0.9rem;
        }}
        .embed-status.success {{
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }}
        .embed-status.warning {{
            background: #fff3cd;
            color: #856404;
            border: 1px solid #ffeeba;
        }}
        .embed-status.error {{
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }}
        .help-text {{
            margin-top: 1rem;
            padding: 1rem;
            background: #f8f9fa;
            border-radius: 5px;
            font-size: 0.85rem;
            color: #666;
        }}
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="logo">MediaFlow</div>
        <div class="nav-links">
            <a href="/">Home</a>
            <a href="/embed">Editor</a>
            <a href="/docs">API Docs</a>
        </div>
    </nav>
    
    <div class="editor-container">
        <div class="editor-card">
            <div class="editor-header">
                <h2>Media Embed</h2>
            </div>
            
            <form class="embed-form" method="get" action="/embed">
                <div class="input-group">
                    <input type="text" name="url" placeholder="Paste media URL here (e.g., https://youtube.com/watch?v=...)" autocomplete="off">
                    <button type="submit">Embed</button>
                </div>
            </form>
            
            <div class="preview-section">
                <div class="preview-label">Preview</div>
                <div class="embed-preview">
                    <iframe {0}></iframe>
                </div>
                {1}
            </div>
            
            <div class="help-text">
                <strong>Supported formats:</strong> YouTube, Vimeo, Twitter, and direct URLs to embeddable content.
            </div>
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
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API Documentation - MediaFlow</title>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: #f5f5f5;
            min-height: 100vh;
        }
        .navbar {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .logo {
            color: white;
            font-size: 1.5rem;
            font-weight: bold;
        }
        .nav-links a {
            color: white;
            text-decoration: none;
            margin-left: 2rem;
            opacity: 0.8;
            transition: opacity 0.2s;
        }
        .nav-links a:hover {
            opacity: 1;
        }
        .docs-container {
            max-width: 900px;
            margin: 2rem auto;
            padding: 0 1rem;
        }
        .docs-card {
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 2rem;
            margin-bottom: 1.5rem;
        }
        h1 {
            color: #333;
            margin-bottom: 1rem;
        }
        h2 {
            color: #333;
            margin-bottom: 0.5rem;
            font-size: 1.3rem;
        }
        h3 {
            color: #555;
            margin: 1rem 0 0.5rem;
            font-size: 1.1rem;
        }
        p {
            color: #666;
            line-height: 1.6;
            margin-bottom: 1rem;
        }
        code {
            background: #f4f4f4;
            padding: 0.2rem 0.5rem;
            border-radius: 3px;
            font-family: 'Monaco', 'Consolas', monospace;
            font-size: 0.9rem;
        }
        pre {
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 1rem;
            border-radius: 5px;
            overflow-x: auto;
            margin: 1rem 0;
        }
        pre code {
            background: none;
            padding: 0;
            color: inherit;
        }
        .endpoint {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin: 1rem 0;
        }
        .method {
            padding: 0.3rem 0.6rem;
            border-radius: 3px;
            font-weight: bold;
            font-size: 0.8rem;
        }
        .method.get { background: #61affe; color: white; }
        .method.post { background: #49cc90; color: white; }
        .path {
            font-family: 'Monaco', 'Consolas', monospace;
            color: #333;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
        }
        th, td {
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid #eee;
        }
        th {
            background: #f8f9fa;
            font-weight: 600;
            color: #333;
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="logo">MediaFlow</div>
        <div class="nav-links">
            <a href="/">Home</a>
            <a href="/embed">Editor</a>
            <a href="/docs">API Docs</a>
        </div>
    </nav>
    
    <div class="docs-container">
        <div class="docs-card">
            <h1>MediaFlow API Documentation</h1>
            <p>The MediaFlow API allows you to programmatically parse and embed media content in your applications.</p>
        </div>
        
        <div class="docs-card">
            <h2>Embed Preview</h2>
            <div class="endpoint">
                <span class="method get">GET</span>
                <span class="path">/embed</span>
            </div>
            <p>Renders an interactive embed preview for the given media URL.</p>
            
            <h3>Parameters</h3>
            <table>
                <tr>
                    <th>Name</th>
                    <th>Type</th>
                    <th>Description</th>
                </tr>
                <tr>
                    <td><code>url</code></td>
                    <td>string</td>
                    <td>The media URL to embed</td>
                </tr>
            </table>
            
            <h3>Example</h3>
            <pre><code>GET /embed?url=https://youtube.com/watch?v=dQw4w9WgXcQ</code></pre>
        </div>
        
        <div class="docs-card">
            <h2>Parse Media URL</h2>
            <div class="endpoint">
                <span class="method post">POST</span>
                <span class="path">/api/media/parse</span>
            </div>
            <p>Parses a media URL and returns embed configuration.</p>
            
            <h3>Request Body</h3>
            <pre><code>{
    "url": "https://example.com/media"
}</code></pre>
            
            <h3>Response</h3>
            <pre><code>{
    "success": true,
    "embed": {
        "url": "https://example.com/media",
        "type": "iframe"
    }
}</code></pre>
        </div>
    </div>
</body>
</html>
"""

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
