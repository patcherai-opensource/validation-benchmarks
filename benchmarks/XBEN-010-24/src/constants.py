INDEX_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>TplRender - Template Engine</title>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Arial, sans-serif; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); min-height: 100vh; color: #eee; }
        .container { max-width: 1000px; margin: 0 auto; padding: 40px 20px; }
        header { text-align: center; margin-bottom: 40px; }
        header h1 { font-size: 2.5em; color: #00d4ff; margin-bottom: 10px; }
        header p { color: #888; font-size: 1.1em; }
        .nav { display: flex; justify-content: center; gap: 20px; margin-bottom: 40px; }
        .nav a { color: #00d4ff; text-decoration: none; padding: 10px 20px; border: 1px solid #00d4ff; border-radius: 5px; transition: all 0.3s; }
        .nav a:hover { background: #00d4ff; color: #1a1a2e; }
        .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 40px; }
        .feature { background: rgba(255,255,255,0.05); padding: 25px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.1); }
        .feature h3 { color: #00d4ff; margin-bottom: 10px; }
        .feature p { color: #aaa; line-height: 1.6; }
        footer { text-align: center; margin-top: 60px; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>TplRender</h1>
            <p>Modern Template Rendering Engine v2.4.1</p>
        </header>
        <nav class="nav">
            <a href="/preview">Preview</a>
            <a href="/render">Render</a>
            <a href="/docs">Documentation</a>
            <a href="/api/v1/status">API Status</a>
        </nav>
        <div class="features">
            <div class="feature">
                <h3>Template Preview</h3>
                <p>Test your templates with variable substitution before deployment.</p>
            </div>
            <div class="feature">
                <h3>Safe Rendering</h3>
                <p>Render templates with automatic JavaScript escaping for security.</p>
            </div>
            <div class="feature">
                <h3>REST API</h3>
                <p>Programmatic access to template operations via our REST API.</p>
            </div>
            <div class="feature">
                <h3>ES6 Support</h3>
                <p>Modern JavaScript template literal support for dynamic content.</p>
            </div>
        </div>
        <footer>
            <p>&copy; 2024 TplRender - Template Engine</p>
        </footer>
    </div>
</body>
</html>
"""


DOCS_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>TplRender - Documentation</title>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Arial, sans-serif; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); min-height: 100vh; color: #eee; }
        .container { max-width: 900px; margin: 0 auto; padding: 40px 20px; }
        h1 { color: #00d4ff; margin-bottom: 30px; }
        h2 { color: #00d4ff; margin: 30px 0 15px 0; font-size: 1.3em; }
        .nav { margin-bottom: 30px; }
        .nav a { color: #00d4ff; margin-right: 20px; }
        .section { background: rgba(255,255,255,0.05); padding: 25px; border-radius: 10px; margin-bottom: 20px; border: 1px solid rgba(255,255,255,0.1); }
        code { background: #2a2a4a; padding: 2px 8px; border-radius: 4px; font-family: 'Consolas', monospace; color: #00ff88; }
        pre { background: #2a2a4a; padding: 15px; border-radius: 8px; overflow-x: auto; margin: 10px 0; }
        pre code { padding: 0; background: none; }
        p { line-height: 1.7; color: #ccc; margin-bottom: 10px; }
        ul { margin-left: 20px; color: #ccc; }
        li { margin-bottom: 8px; }
    </style>
</head>
<body>
    <div class="container">
        <nav class="nav">
            <a href="/">&larr; Home</a>
            <a href="/preview">Preview</a>
            <a href="/render">Render</a>
        </nav>
        <h1>Documentation</h1>
        
        <div class="section">
            <h2>JavaScript Escaping</h2>
            <p>TplRender applies JavaScript string escaping to protect against injection attacks. The following characters are escaped:</p>
            <ul>
                <li><code>\\</code> &rarr; <code>\\\\</code></li>
                <li><code>'</code> &rarr; <code>\\'</code></li>
                <li><code>"</code> &rarr; <code>\\"</code></li>
                <li><code>&lt;</code> &rarr; <code>\\x3C</code></li>
                <li><code>&gt;</code> &rarr; <code>\\x3E</code></li>
                <li><code>&amp;</code> &rarr; <code>\\x26</code></li>
                <li><code>\\r</code> &rarr; <code>\\\\r</code></li>
                <li><code>\\n</code> &rarr; <code>\\\\n</code></li>
            </ul>
        </div>

        <div class="section">
            <h2>Template Preview</h2>
            <p>The preview endpoint allows testing template rendering with custom values. Uses ES6 template literals for modern string interpolation.</p>
            <pre><code>POST /preview
Content-Type: application/x-www-form-urlencoded

value=your_test_value&template=greeting</code></pre>
        </div>

        <div class="section">
            <h2>Safe Render</h2>
            <p>The render endpoint provides secure template rendering with full escaping for production use.</p>
            <pre><code>POST /render
Content-Type: application/x-www-form-urlencoded

message=your_message</code></pre>
        </div>

        <div class="section">
            <h2>API Endpoints</h2>
            <ul>
                <li><code>GET /api/v1/status</code> - Engine status</li>
                <li><code>GET /api/v1/templates</code> - List templates</li>
                <li><code>GET /api/v1/templates/{id}</code> - Template details</li>
            </ul>
        </div>

        <div class="section">
            <h2>Security Testing</h2>
            <p>The preview endpoint includes a built-in XSS detection system. If the rendered output triggers an <code>alert('XSS')</code>, the security check will pass and display a success message.</p>
        </div>
    </div>
</body>
</html>
"""


PREVIEW_FORM_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>TplRender - Template Preview</title>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Arial, sans-serif; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); min-height: 100vh; color: #eee; }
        .container { max-width: 700px; margin: 0 auto; padding: 40px 20px; }
        h1 { color: #00d4ff; margin-bottom: 10px; }
        .subtitle { color: #888; margin-bottom: 30px; }
        .nav { margin-bottom: 30px; }
        .nav a { color: #00d4ff; margin-right: 20px; }
        .form-box { background: rgba(255,255,255,0.05); padding: 30px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.1); }
        label { display: block; margin-bottom: 8px; color: #aaa; }
        textarea { width: 100%; height: 150px; padding: 15px; border: 1px solid #333; border-radius: 8px; background: #1a1a2e; color: #eee; font-family: 'Consolas', monospace; font-size: 14px; resize: vertical; }
        textarea:focus { outline: none; border-color: #00d4ff; }
        select { width: 100%; padding: 12px; border: 1px solid #333; border-radius: 8px; background: #1a1a2e; color: #eee; margin-bottom: 20px; }
        button { background: #00d4ff; color: #1a1a2e; padding: 12px 30px; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; font-weight: bold; }
        button:hover { background: #00b8e6; }
        .info { background: rgba(0, 212, 255, 0.1); border: 1px solid rgba(0, 212, 255, 0.3); padding: 15px; border-radius: 8px; margin-top: 20px; color: #88ccff; }
    </style>
</head>
<body>
    <div class="container">
        <nav class="nav">
            <a href="/">&larr; Home</a>
            <a href="/docs">Docs</a>
            <a href="/render">Render</a>
        </nav>
        <h1>Template Preview</h1>
        <p class="subtitle">Test template rendering with variable substitution</p>
        
        <div class="form-box">
            <form method="POST" action="/preview">
                <label for="template">Template:</label>
                <select name="template" id="template">
                    <option value="greeting">Greeting Template</option>
                    <option value="welcome">Welcome Template</option>
                    <option value="notification">Notification Template</option>
                </select>
                
                <label for="value">Value:</label>
                <textarea name="value" id="value" placeholder="Enter a value to substitute in the template..."></textarea>
                <br><br>
                <button type="submit">Preview Template</button>
            </form>
            <div class="info">
                <strong>Note:</strong> Values are JavaScript-escaped before rendering to prevent injection attacks.
            </div>
        </div>
    </div>
</body>
</html>
"""


PREVIEW_RESULT_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>TplRender - Preview Result</title>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Arial, sans-serif; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); min-height: 100vh; color: #eee; }}
        .container {{ max-width: 700px; margin: 0 auto; padding: 40px 20px; }}
        h1 {{ color: #00d4ff; margin-bottom: 10px; }}
        .subtitle {{ color: #888; margin-bottom: 30px; }}
        .nav {{ margin-bottom: 30px; }}
        .nav a {{ color: #00d4ff; margin-right: 20px; }}
        .result-box {{ padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        .result-box.success {{ background: rgba(0, 255, 100, 0.1); border: 1px solid rgba(0, 255, 100, 0.3); color: #88ff88; }}
        .result-box.error {{ background: rgba(255, 100, 100, 0.1); border: 1px solid rgba(255, 100, 100, 0.3); color: #ff8888; }}
        .result-box.warning {{ background: rgba(255, 200, 0, 0.1); border: 1px solid rgba(255, 200, 0, 0.3); color: #ffcc00; }}
        .result-box.info {{ background: rgba(0, 212, 255, 0.1); border: 1px solid rgba(0, 212, 255, 0.3); color: #88ccff; }}
        .icon {{ font-size: 1.2em; margin-right: 10px; }}
        .preview-output {{ background: rgba(255,255,255,0.05); padding: 20px; border-radius: 8px; margin-top: 20px; border: 1px solid rgba(255,255,255,0.1); }}
        .rendered-template {{ padding: 15px; background: #2a2a4a; border-radius: 5px; }}
        .input-echo {{ background: rgba(255,255,255,0.03); padding: 15px; border-radius: 8px; margin-bottom: 20px; }}
        .input-echo label {{ color: #888; display: block; margin-bottom: 5px; }}
        .input-echo code {{ background: #2a2a4a; padding: 8px 12px; border-radius: 4px; display: block; word-break: break-all; color: #00ff88; }}
    </style>
</head>
<body>
    <div class="container">
        <nav class="nav">
            <a href="/">&larr; Home</a>
            <a href="/preview">New Preview</a>
            <a href="/docs">Docs</a>
        </nav>
        <h1>Preview Result</h1>
        <p class="subtitle">Template rendering output</p>
        
        <div class="input-echo">
            <label>Escaped Input:</label>
            <code>{0}</code>
        </div>
        
        {1}
    </div>
</body>
</html>
"""


RENDER_FORM_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>TplRender - Safe Render</title>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Arial, sans-serif; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); min-height: 100vh; color: #eee; }
        .container { max-width: 700px; margin: 0 auto; padding: 40px 20px; }
        h1 { color: #00d4ff; margin-bottom: 10px; }
        .subtitle { color: #888; margin-bottom: 30px; }
        .nav { margin-bottom: 30px; }
        .nav a { color: #00d4ff; margin-right: 20px; }
        .form-box { background: rgba(255,255,255,0.05); padding: 30px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.1); }
        label { display: block; margin-bottom: 8px; color: #aaa; }
        input[type="text"] { width: 100%; padding: 15px; border: 1px solid #333; border-radius: 8px; background: #1a1a2e; color: #eee; font-size: 14px; }
        input[type="text"]:focus { outline: none; border-color: #00d4ff; }
        button { background: #00d4ff; color: #1a1a2e; padding: 12px 30px; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; font-weight: bold; margin-top: 20px; }
        button:hover { background: #00b8e6; }
        .info { background: rgba(0, 255, 100, 0.1); border: 1px solid rgba(0, 255, 100, 0.3); padding: 15px; border-radius: 8px; margin-top: 20px; color: #88ff88; }
    </style>
</head>
<body>
    <div class="container">
        <nav class="nav">
            <a href="/">&larr; Home</a>
            <a href="/docs">Docs</a>
            <a href="/preview">Preview</a>
        </nav>
        <h1>Safe Render</h1>
        <p class="subtitle">Production-ready template rendering with full escaping</p>
        
        <div class="form-box">
            <form method="POST" action="/render">
                <label for="message">Message:</label>
                <input type="text" name="message" id="message" placeholder="Enter your message...">
                <button type="submit">Render</button>
            </form>
            <div class="info">
                <strong>Secure:</strong> This endpoint uses comprehensive escaping including template literal protection.
            </div>
        </div>
    </div>
</body>
</html>
"""


RENDER_OUTPUT_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>TplRender - Render Output</title>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Arial, sans-serif; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); min-height: 100vh; color: #eee; }}
        .container {{ max-width: 700px; margin: 0 auto; padding: 40px 20px; }}
        h1 {{ color: #00d4ff; margin-bottom: 10px; }}
        .subtitle {{ color: #888; margin-bottom: 30px; }}
        .nav {{ margin-bottom: 30px; }}
        .nav a {{ color: #00d4ff; margin-right: 20px; }}
        .render-output {{ background: rgba(255,255,255,0.05); padding: 20px; border-radius: 8px; margin-top: 20px; border: 1px solid rgba(255,255,255,0.1); }}
        .input-echo {{ background: rgba(255,255,255,0.03); padding: 15px; border-radius: 8px; margin-bottom: 20px; }}
        .input-echo label {{ color: #888; display: block; margin-bottom: 5px; }}
        .input-echo code {{ background: #2a2a4a; padding: 8px 12px; border-radius: 4px; display: block; word-break: break-all; color: #00ff88; }}
    </style>
</head>
<body>
    <div class="container">
        <nav class="nav">
            <a href="/">&larr; Home</a>
            <a href="/render">New Render</a>
            <a href="/preview">Preview</a>
        </nav>
        <h1>Render Output</h1>
        <p class="subtitle">Safely rendered template</p>
        
        <div class="input-echo">
            <label>Escaped Input:</label>
            <code>{0}</code>
        </div>
        
        {1}
    </div>
</body>
</html>
"""


# Image routes - kept for compatibility but unused in new design
IMAGE_ROUTES = {
    "preview": {
        "start": "static/img/cookies/new_star.png",
        "process": "static/img/cookies/error_star.png",
        "error": "static/img/cookies/error_star.png",
        "success": "static/img/cookies/success_star.png"
    }
}
