# XWiki Live Data Dashboard - Template Constants

INDEX_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>XWiki Live Data Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; justify-content: center; align-items: center; }
        .container { background: white; border-radius: 10px; box-shadow: 0 15px 35px rgba(0,0,0,0.2); padding: 40px; max-width: 600px; width: 90%; }
        .logo { text-align: center; margin-bottom: 30px; }
        .logo h1 { color: #333; font-size: 28px; margin-bottom: 10px; }
        .logo p { color: #666; font-size: 14px; }
        .nav-links { display: flex; flex-direction: column; gap: 15px; }
        .nav-link { display: block; padding: 20px; background: #f8f9fa; border-radius: 8px; text-decoration: none; color: #333; transition: all 0.3s ease; border-left: 4px solid #667eea; }
        .nav-link:hover { background: #667eea; color: white; transform: translateX(5px); }
        .nav-link h3 { margin-bottom: 5px; }
        .nav-link p { font-size: 13px; opacity: 0.8; }
        .footer { text-align: center; margin-top: 30px; color: #666; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            <h1>XWiki Live Data</h1>
            <p>Dynamic Data Visualization Platform</p>
        </div>
        <div class="nav-links">
            <a href="/livedata" class="nav-link">
                <h3>Live Data Dashboard</h3>
                <p>View and manage dynamic data entries</p>
            </a>
            <a href="/livedata/create" class="nav-link">
                <h3>Create Entry</h3>
                <p>Add new data entries with custom display options</p>
            </a>
            <a href="/api/livedata/config" class="nav-link">
                <h3>API Configuration</h3>
                <p>View available displayer types and properties</p>
            </a>
        </div>
        <div class="footer">
            <p>XWiki Platform Live Data Macro v13.10.9</p>
        </div>
    </div>
</body>
</html>
"""

LIVEDATA_DASHBOARD = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Live Data Dashboard - XWiki</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; min-height: 100vh; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px 40px; }
        .header h1 { font-size: 24px; }
        .header p { opacity: 0.8; margin-top: 5px; }
        .main { padding: 40px; max-width: 1200px; margin: 0 auto; }
        .card { background: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); padding: 30px; margin-bottom: 20px; }
        .card h2 { color: #333; margin-bottom: 20px; border-bottom: 2px solid #667eea; padding-bottom: 10px; }
        .info-box { background: #e8f4f8; border-left: 4px solid #17a2b8; padding: 15px; margin: 20px 0; border-radius: 4px; }
        .info-box code { background: #d4edda; padding: 2px 6px; border-radius: 3px; font-family: monospace; }
        .btn { display: inline-block; padding: 12px 24px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; transition: background 0.3s; }
        .btn:hover { background: #5a6fd6; }
        pre { background: #2d2d2d; color: #f8f8f2; padding: 15px; border-radius: 5px; overflow-x: auto; font-size: 13px; }
        .api-section { margin-top: 30px; }
        .api-section h3 { color: #333; margin-bottom: 15px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Live Data Dashboard</h1>
        <p>Manage and display dynamic content with configurable displayers</p>
    </div>
    <div class="main">
        <div class="card">
            <h2>About Live Data Macro</h2>
            <p>The Live Data macro allows you to display dynamic data with various rendering options. Configure how each property is displayed using displayer types.</p>
            
            <div class="info-box">
                <strong>Available Displayers:</strong>
                <ul style="margin-top: 10px; margin-left: 20px;">
                    <li><code>text</code> - Plain text (escaped)</li>
                    <li><code>link</code> - Hyperlink format</li>
                    <li><code>html</code> - Raw HTML rendering</li>
                    <li><code>number</code> - Formatted numbers</li>
                </ul>
            </div>
            
            <a href="/livedata/create" class="btn">Create New Entry</a>
        </div>
        
        <div class="card api-section">
            <h2>API Usage</h2>
            <h3>Create Entry with JSON</h3>
            <p>POST to <code>/livedata/create</code> with JSON body:</p>
            <pre>{
  "entries": [
    {
      "title": "My Entry",
      "content": "Entry content here"
    }
  ],
  "meta": {
    "propertyDescriptors": [
      {
        "id": "content",
        "displayer": "text"
      }
    ]
  }
}</pre>
            <h3 style="margin-top: 20px;">Form Submission</h3>
            <p>POST to <code>/livedata/create</code> with form data:</p>
            <pre>title=My Entry&amp;content=Entry content&amp;displayer=text</pre>
        </div>
    </div>
</body>
</html>
"""

LIVEDATA_CREATE_FORM = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Create Entry - XWiki Live Data</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; min-height: 100vh; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px 40px; }
        .header h1 { font-size: 24px; }
        .main { padding: 40px; max-width: 800px; margin: 0 auto; }
        .card { background: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); padding: 30px; }
        .card h2 { color: #333; margin-bottom: 20px; }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 8px; color: #555; font-weight: 500; }
        .form-group input, .form-group textarea, .form-group select { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 5px; font-size: 14px; }
        .form-group textarea { min-height: 120px; resize: vertical; }
        .form-group select { background: white; }
        .form-group small { color: #888; font-size: 12px; margin-top: 5px; display: block; }
        .btn { display: inline-block; padding: 12px 24px; background: #667eea; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; transition: background 0.3s; }
        .btn:hover { background: #5a6fd6; }
        .back-link { display: inline-block; margin-bottom: 20px; color: #667eea; text-decoration: none; }
        .back-link:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Create Live Data Entry</h1>
    </div>
    <div class="main">
        <a href="/livedata" class="back-link">&larr; Back to Dashboard</a>
        <div class="card">
            <h2>New Entry</h2>
            <form method="POST" action="/livedata/create">
                <div class="form-group">
                    <label for="title">Title</label>
                    <input type="text" id="title" name="title" placeholder="Enter entry title..." required>
                </div>
                <div class="form-group">
                    <label for="content">Content</label>
                    <textarea id="content" name="content" placeholder="Enter content..."></textarea>
                    <small>Content will be rendered according to the selected displayer type</small>
                </div>
                <div class="form-group">
                    <label for="displayer">Content Displayer</label>
                    <select id="displayer" name="displayer">
                        <option value="text">text - Plain Text (escaped)</option>
                        <option value="link">link - Hyperlink</option>
                        <option value="html">html - Raw HTML</option>
                        <option value="number">number - Formatted Number</option>
                    </select>
                    <small>Defines how the content property will be rendered when viewed</small>
                </div>
                <button type="submit" class="btn">Create Entry</button>
            </form>
        </div>
    </div>
</body>
</html>
"""

LIVEDATA_VIEW_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{title} - XWiki Live Data</title>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; padding: 20px; background: #f5f5f5; }}
        .entry {{ background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .entry h1 {{ color: #333; margin-bottom: 15px; }}
        .content {{ color: #555; line-height: 1.6; }}
    </style>
</head>
<body>
    <div class="entry">
        <h1>{title}</h1>
        <div class="content">{content}</div>
    </div>
</body>
</html>
"""

LIVEDATA_RESULT_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Entry Result - XWiki Live Data</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; min-height: 100vh; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px 40px; }}
        .header h1 {{ font-size: 24px; }}
        .main {{ padding: 40px; max-width: 800px; margin: 0 auto; }}
        .card {{ background: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); padding: 30px; }}
        .result {{ margin: 20px 0; }}
        .back-link {{ display: inline-block; margin-top: 20px; color: #667eea; text-decoration: none; }}
        .back-link:hover {{ text-decoration: underline; }}
        .alert {{ padding: 15px; border-radius: 5px; margin: 10px 0; }}
        .alert-success {{ background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
        .alert-info {{ background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }}
        .alert-warning {{ background: #fff3cd; color: #856404; border: 1px solid #ffeeba; }}
        .flag {{ font-family: monospace; background: #f8f9fa; padding: 10px; border-radius: 5px; word-break: break-all; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Entry Processing Result</h1>
    </div>
    <div class="main">
        <div class="card">
            <h2>Result</h2>
            <div class="result">
                {message}
            </div>
            <a href="/livedata/create" class="back-link">&larr; Create Another Entry</a>
        </div>
    </div>
</body>
</html>
"""

LIVEDATA_SUCCESS_RESPONSE = """
<div class="alert alert-success">
    <strong>XSS Vulnerability Confirmed!</strong>
    <p>Your payload was executed successfully in the viewer's browser context.</p>
    <p>This demonstrates the stored XSS vulnerability in the Live Data macro when using the HTML displayer.</p>
    <p class="flag"><strong>Flag:</strong> {flag}</p>
</div>
"""

LIVEDATA_PARTIAL_RESPONSE = """
<div class="alert alert-info">
    <strong>Content Rendered</strong>
    <p>JavaScript alert triggered with message: <code>{result}</code></p>
    <p>Expected alert message: <code>XSS</code></p>
</div>
"""

LIVEDATA_ENTRY_CREATED = """
<div class="alert alert-warning">
    <strong>Entry Created</strong>
    <p>Your entry was stored and rendered for viewers.</p>
    <p>Content displayer: active</p>
</div>
"""

# Keep some legacy constants for compatibility
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
