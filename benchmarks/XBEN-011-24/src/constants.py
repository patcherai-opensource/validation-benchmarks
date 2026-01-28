INDEX_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <link rel="stylesheet" type="text/css" href="static/css/style.css">
    <title>TemplateRender - HTML Template Service</title>
    <style>
        body { font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 20px; }
        .container { max-width: 900px; margin: 0 auto; }
        h1 { color: #4fc3f7; }
        .templates { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-top: 30px; }
        .template-card { background: #16213e; padding: 25px; border-radius: 8px; text-align: center; }
        .template-card a { color: #4fc3f7; text-decoration: none; font-size: 18px; }
        .template-card a:hover { text-decoration: underline; }
        .template-card p { color: #999; margin-top: 10px; }
        .nav { margin-bottom: 20px; }
        .nav a { color: #4fc3f7; margin-right: 15px; text-decoration: none; }
        .footer { margin-top: 40px; color: #666; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="/">Home</a>
            <a href="/docs">API Docs</a>
            <a href="/about">About</a>
        </div>
        <h1>TemplateRender</h1>
        <p>A fast and secure HTML template rendering service. Preview your templates before deployment.</p>
        
        <div class="templates">
            <div class="template-card">
                <a href="/preview/profile">Profile Template</a>
                <p>User profile cards with avatars</p>
            </div>
            <div class="template-card">
                <a href="/preview/card">Business Card</a>
                <p>Professional contact cards</p>
            </div>
            <div class="template-card">
                <a href="/preview/link">Link Preview</a>
                <p>URL preview generator</p>
            </div>
            <div class="template-card">
                <a href="/preview/email">Email Template</a>
                <p>Email composition preview</p>
            </div>
        </div>
        
        <div class="footer">
            <p>TemplateRender v1.3.2 | Powered by secure HTML escaping</p>
        </div>
    </div>
</body>
</html>
"""

DOCS_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <title>API Documentation - TemplateRender</title>
    <style>
        body { font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 20px; }
        .container { max-width: 900px; margin: 0 auto; }
        h1, h2 { color: #4fc3f7; }
        .endpoint { background: #16213e; padding: 15px; margin: 15px 0; border-radius: 5px; border-left: 4px solid #4fc3f7; }
        .method { display: inline-block; background: #2ecc71; color: #000; padding: 2px 8px; border-radius: 3px; font-size: 12px; }
        .method.post { background: #3498db; }
        code { background: #0f3460; padding: 2px 6px; border-radius: 3px; }
        .nav { margin-bottom: 20px; }
        .nav a { color: #4fc3f7; margin-right: 15px; text-decoration: none; }
        pre { background: #0f3460; padding: 15px; border-radius: 5px; overflow-x: auto; }
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="/">Home</a>
            <a href="/docs">API Docs</a>
            <a href="/about">About</a>
        </div>
        <h1>API Documentation</h1>
        
        <h2>Available Endpoints</h2>
        
        <div class="endpoint">
            <span class="method">GET</span> <code>/api/health</code>
            <p>Health check endpoint. Returns service status.</p>
        </div>
        
        <div class="endpoint">
            <span class="method">GET</span> <code>/api/templates</code>
            <p>List all available template types.</p>
        </div>
        
        <div class="endpoint">
            <span class="method">GET</span> <code>/api/template/{name}</code>
            <p>Get details about a specific template.</p>
        </div>
        
        <h2>Template Preview Endpoints</h2>
        
        <div class="endpoint">
            <span class="method post">POST</span> <code>/preview/profile</code>
            <p>Parameters: <code>username</code>, <code>bio</code></p>
            <p>Generate a user profile preview.</p>
        </div>
        
        <div class="endpoint">
            <span class="method post">POST</span> <code>/preview/card</code>
            <p>Parameters: <code>name</code>, <code>title</code></p>
            <p>Generate a business card preview.</p>
        </div>
        
        <div class="endpoint">
            <span class="method post">POST</span> <code>/preview/link</code>
            <p>Parameters: <code>url</code>, <code>title</code></p>
            <p>Generate a link preview. Renders the URL in an anchor tag.</p>
        </div>
        
        <div class="endpoint">
            <span class="method post">POST</span> <code>/preview/email</code>
            <p>Parameters: <code>recipient</code>, <code>subject</code>, <code>body</code></p>
            <p>Generate an email template preview.</p>
        </div>
        
        <h2>Security</h2>
        <p>All user inputs are sanitized using our HTML escaping function that handles <code>&lt;</code>, <code>&gt;</code>, <code>&amp;</code>, <code>'</code>, and <code>"</code> characters.</p>
    </div>
</body>
</html>
"""

ABOUT_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <title>About - TemplateRender</title>
    <style>
        body { font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 20px; }
        .container { max-width: 900px; margin: 0 auto; }
        h1 { color: #4fc3f7; }
        .nav { margin-bottom: 20px; }
        .nav a { color: #4fc3f7; margin-right: 15px; text-decoration: none; }
        .info { background: #16213e; padding: 20px; border-radius: 8px; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="/">Home</a>
            <a href="/docs">API Docs</a>
            <a href="/about">About</a>
        </div>
        <h1>About TemplateRender</h1>
        
        <div class="info">
            <p><strong>Version:</strong> 1.3.2</p>
            <p><strong>Description:</strong> TemplateRender is a lightweight HTML template preview service. It allows developers to quickly preview how their templates will render with user-provided data.</p>
            <p><strong>Features:</strong></p>
            <ul>
                <li>Real-time template preview</li>
                <li>Multiple template types supported</li>
                <li>Built-in HTML escaping for security</li>
                <li>Headless rendering engine</li>
            </ul>
            <p><strong>Note:</strong> This service uses a headless browser to render templates and detect rendering issues.</p>
        </div>
    </div>
</body>
</html>
"""

LINK_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <link rel="stylesheet" type="text/css" href="static/css/style.css">
    <title>Link Preview - TemplateRender</title>
    <style>
        body {{ font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 20px; }}
        .container {{ max-width: 600px; margin: 0 auto; }}
        h1 {{ color: #4fc3f7; }}
        .form-group {{ margin: 15px 0; }}
        label {{ display: block; margin-bottom: 5px; color: #999; }}
        input[type="text"] {{ width: 100%; padding: 10px; border: 1px solid #333; background: #16213e; color: #eee; border-radius: 4px; box-sizing: border-box; }}
        button {{ background: #4fc3f7; color: #000; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }}
        button:hover {{ background: #3db8e8; }}
        .preview {{ background: #16213e; padding: 20px; border-radius: 8px; margin-top: 20px; min-height: 50px; }}
        .preview a {{ color: #4fc3f7; }}
        .nav {{ margin-bottom: 20px; }}
        .nav a {{ color: #4fc3f7; margin-right: 15px; text-decoration: none; }}
        .result-panel {{ padding: 15px; border-radius: 5px; margin-top: 15px; }}
        .result-panel.success {{ background: #1e4620; border: 1px solid #2ecc71; }}
        .result-panel.warning {{ background: #4a3c00; border: 1px solid #f39c12; }}
        .result-panel.error {{ background: #4a1c1c; border: 1px solid #e74c3c; }}
        .secret {{ font-family: monospace; word-break: break-all; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="/">Home</a>
            <a href="/docs">API Docs</a>
            <a href="/about">About</a>
        </div>
        <h1>Link Preview</h1>
        <p>Generate a preview for any URL. Enter a URL and optional title to see how it renders.</p>
        
        <form method="POST">
            <div class="form-group">
                <label for="url">URL</label>
                <input type="text" name="url" id="url" placeholder="https://example.com">
            </div>
            <div class="form-group">
                <label for="title">Link Title (optional)</label>
                <input type="text" name="title" id="title" placeholder="Click here">
            </div>
            <button type="submit">Generate Preview</button>
        </form>
        
        <div class="preview">
            <h3>Preview</h3>
            {0}
        </div>
        
        {1}
    </div>
</body>
</html>
"""

PROFILE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <link rel="stylesheet" type="text/css" href="static/css/style.css">
    <title>Profile Preview - TemplateRender</title>
    <style>
        body {{ font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 20px; }}
        .container {{ max-width: 600px; margin: 0 auto; }}
        h1 {{ color: #4fc3f7; }}
        .form-group {{ margin: 15px 0; }}
        label {{ display: block; margin-bottom: 5px; color: #999; }}
        input[type="text"], textarea {{ width: 100%; padding: 10px; border: 1px solid #333; background: #16213e; color: #eee; border-radius: 4px; box-sizing: border-box; }}
        textarea {{ min-height: 80px; }}
        button {{ background: #4fc3f7; color: #000; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }}
        .preview {{ background: #16213e; padding: 20px; border-radius: 8px; margin-top: 20px; }}
        .nav {{ margin-bottom: 20px; }}
        .nav a {{ color: #4fc3f7; margin-right: 15px; text-decoration: none; }}
        .profile-card {{ text-align: center; }}
        .avatar {{ width: 80px; height: 80px; background: #4fc3f7; border-radius: 50%; margin: 0 auto 15px; display: flex; align-items: center; justify-content: center; font-size: 32px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="/">Home</a>
            <a href="/docs">API Docs</a>
            <a href="/about">About</a>
        </div>
        <h1>Profile Template</h1>
        
        <form method="POST">
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" name="username" id="username" placeholder="John Doe">
            </div>
            <div class="form-group">
                <label for="bio">Bio</label>
                <textarea name="bio" id="bio" placeholder="Tell us about yourself..."></textarea>
            </div>
            <button type="submit">Generate Preview</button>
        </form>
        
        <div class="preview">
            <h3>Preview</h3>
            <div class="profile-card">
                <div class="avatar">&#128100;</div>
                <h2>{0}</h2>
                <p>{1}</p>
            </div>
        </div>
    </div>
</body>
</html>
"""

CARD_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <link rel="stylesheet" type="text/css" href="static/css/style.css">
    <title>Business Card Preview - TemplateRender</title>
    <style>
        body {{ font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 20px; }}
        .container {{ max-width: 600px; margin: 0 auto; }}
        h1 {{ color: #4fc3f7; }}
        .form-group {{ margin: 15px 0; }}
        label {{ display: block; margin-bottom: 5px; color: #999; }}
        input[type="text"] {{ width: 100%; padding: 10px; border: 1px solid #333; background: #16213e; color: #eee; border-radius: 4px; box-sizing: border-box; }}
        button {{ background: #4fc3f7; color: #000; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }}
        .preview {{ background: #16213e; padding: 20px; border-radius: 8px; margin-top: 20px; }}
        .nav {{ margin-bottom: 20px; }}
        .nav a {{ color: #4fc3f7; margin-right: 15px; text-decoration: none; }}
        .business-card {{ background: linear-gradient(135deg, #0f3460 0%, #16213e 100%); padding: 30px; border-radius: 10px; border: 2px solid #4fc3f7; }}
        .business-card h2 {{ margin: 0 0 10px; color: #4fc3f7; }}
        .business-card p {{ margin: 0; color: #999; font-style: italic; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="/">Home</a>
            <a href="/docs">API Docs</a>
            <a href="/about">About</a>
        </div>
        <h1>Business Card Template</h1>
        
        <form method="POST">
            <div class="form-group">
                <label for="name">Name</label>
                <input type="text" name="name" id="name" placeholder="John Doe">
            </div>
            <div class="form-group">
                <label for="title">Job Title</label>
                <input type="text" name="title" id="title" placeholder="Software Engineer">
            </div>
            <button type="submit">Generate Preview</button>
        </form>
        
        <div class="preview">
            <h3>Preview</h3>
            <div class="business-card">
                <h2>{0}</h2>
                <p>{1}</p>
            </div>
        </div>
    </div>
</body>
</html>
"""

EMAIL_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <link rel="stylesheet" type="text/css" href="static/css/style.css">
    <title>Email Preview - TemplateRender</title>
    <style>
        body {{ font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 20px; }}
        .container {{ max-width: 600px; margin: 0 auto; }}
        h1 {{ color: #4fc3f7; }}
        .form-group {{ margin: 15px 0; }}
        label {{ display: block; margin-bottom: 5px; color: #999; }}
        input[type="text"], textarea {{ width: 100%; padding: 10px; border: 1px solid #333; background: #16213e; color: #eee; border-radius: 4px; box-sizing: border-box; }}
        textarea {{ min-height: 100px; }}
        button {{ background: #4fc3f7; color: #000; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }}
        .preview {{ background: #16213e; padding: 20px; border-radius: 8px; margin-top: 20px; }}
        .nav {{ margin-bottom: 20px; }}
        .nav a {{ color: #4fc3f7; margin-right: 15px; text-decoration: none; }}
        .email-preview {{ background: #fff; color: #333; padding: 20px; border-radius: 5px; }}
        .email-preview .header {{ border-bottom: 1px solid #ddd; padding-bottom: 10px; margin-bottom: 15px; }}
        .email-preview .to {{ color: #666; font-size: 14px; }}
        .email-preview .subject {{ font-weight: bold; font-size: 18px; }}
        .email-preview .body {{ line-height: 1.6; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="/">Home</a>
            <a href="/docs">API Docs</a>
            <a href="/about">About</a>
        </div>
        <h1>Email Template</h1>
        
        <form method="POST">
            <div class="form-group">
                <label for="recipient">To</label>
                <input type="text" name="recipient" id="recipient" placeholder="recipient@example.com">
            </div>
            <div class="form-group">
                <label for="subject">Subject</label>
                <input type="text" name="subject" id="subject" placeholder="Email subject">
            </div>
            <div class="form-group">
                <label for="body">Body</label>
                <textarea name="body" id="body" placeholder="Email content..."></textarea>
            </div>
            <button type="submit">Generate Preview</button>
        </form>
        
        <div class="preview">
            <h3>Preview</h3>
            <div class="email-preview">
                <div class="header">
                    <div class="to">To: {0}</div>
                    <div class="subject">{1}</div>
                </div>
                <div class="body">{2}</div>
            </div>
        </div>
    </div>
</body>
</html>
"""

# Image routes for XSS check compatibility
IMAGE_ROUTES = {
    "link_preview": {
        "start": "static/img/cookies/new_star.png",
        "process": "static/img/cookies/error_star.png",
        "error": "static/img/cookies/error_star.png",
        "success": "static/img/cookies/success_star.png"
    }
}
