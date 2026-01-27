INDEX_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Templar Templates - Demo</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #e8e8e8;
        }
        .container { max-width: 900px; margin: 0 auto; padding: 40px 20px; }
        header { text-align: center; margin-bottom: 50px; }
        h1 { 
            font-size: 2.8em; 
            color: #00d9ff; 
            margin-bottom: 10px;
            text-shadow: 0 0 20px rgba(0,217,255,0.3);
        }
        .tagline { color: #888; font-size: 1.1em; margin-bottom: 30px; }
        .version-badge {
            display: inline-block;
            background: #2a2a4a;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.85em;
            color: #00d9ff;
        }
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 40px 0;
        }
        .feature-card {
            background: rgba(255,255,255,0.05);
            padding: 25px;
            border-radius: 12px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .feature-card h3 { color: #00d9ff; margin-bottom: 10px; }
        .feature-card p { color: #aaa; line-height: 1.6; }
        .demo-section {
            background: rgba(0,0,0,0.3);
            padding: 30px;
            border-radius: 12px;
            margin-top: 30px;
        }
        .demo-section h2 { color: #fff; margin-bottom: 20px; }
        .btn {
            display: inline-block;
            background: #00d9ff;
            color: #1a1a2e;
            padding: 12px 30px;
            border-radius: 6px;
            text-decoration: none;
            font-weight: bold;
            margin: 10px 10px 10px 0;
            transition: all 0.3s;
        }
        .btn:hover { background: #00f7ff; transform: translateY(-2px); }
        .btn-secondary {
            background: transparent;
            border: 2px solid #00d9ff;
            color: #00d9ff;
        }
        .btn-secondary:hover { background: rgba(0,217,255,0.1); }
        footer {
            text-align: center;
            margin-top: 60px;
            padding-top: 30px;
            border-top: 1px solid rgba(255,255,255,0.1);
            color: #666;
        }
        code {
            background: rgba(0,217,255,0.1);
            padding: 2px 8px;
            border-radius: 4px;
            font-family: 'Consolas', monospace;
            color: #00d9ff;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Templar Templates</h1>
            <p class="tagline">Fast, Simple, Secure HTML Template Engine</p>
            <span class="version-badge">v1.9.3</span>
        </header>

        <div class="features">
            <div class="feature-card">
                <h3>Auto-Escaping</h3>
                <p>Built-in XSS protection with automatic HTML entity escaping for <code>&lt;</code>, <code>&gt;</code>, <code>&amp;</code>, quotes and more.</p>
            </div>
            <div class="feature-card">
                <h3>Template Literals</h3>
                <p>Modern JavaScript template literal support for dynamic content rendering.</p>
            </div>
            <div class="feature-card">
                <h3>High Performance</h3>
                <p>Optimized template compilation with intelligent caching for production workloads.</p>
            </div>
        </div>

        <div class="demo-section">
            <h2>Try the Demo</h2>
            <p style="margin-bottom: 20px; color: #aaa;">
                Test our Greeting Card Generator - it demonstrates Templar's template literal 
                rendering with automatic escaping protection.
            </p>
            <a href="/greeting" class="btn">Greeting Generator</a>
            <a href="/docs" class="btn btn-secondary">Documentation</a>
            <a href="/api/info" class="btn btn-secondary">API Info</a>
        </div>

        <footer>
            <p>Templar Templates &copy; 2024 | Built for developers who care about security</p>
        </footer>
    </div>
</body>
</html>
"""


GREETING_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Greeting Generator - Templar Templates</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #e8e8e8;
        }}
        .container {{ max-width: 700px; margin: 0 auto; padding: 40px 20px; }}
        h1 {{ 
            font-size: 2em; 
            color: #00d9ff; 
            margin-bottom: 10px;
            text-align: center;
        }}
        .subtitle {{ 
            text-align: center; 
            color: #888; 
            margin-bottom: 30px; 
        }}
        .form-section {{
            background: rgba(0,0,0,0.3);
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 20px;
        }}
        form {{ display: flex; flex-direction: column; gap: 15px; }}
        label {{ color: #aaa; font-size: 0.9em; }}
        input[type="text"] {{
            width: 100%;
            padding: 12px 15px;
            background: rgba(255,255,255,0.1);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 6px;
            color: #fff;
            font-size: 1em;
        }}
        input[type="text"]:focus {{
            outline: none;
            border-color: #00d9ff;
        }}
        .btn {{
            background: #00d9ff;
            color: #1a1a2e;
            padding: 12px 30px;
            border: none;
            border-radius: 6px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
        }}
        .btn:hover {{ background: #00f7ff; }}
        .greeting-section {{
            background: rgba(255,255,255,0.05);
            padding: 25px;
            border-radius: 12px;
            border: 1px solid rgba(255,255,255,0.1);
        }}
        .greeting-section h3 {{ color: #00d9ff; margin-bottom: 15px; }}
        .greeting-card {{
            background: linear-gradient(135deg, #2a2a4a 0%, #1a1a3e 100%);
            padding: 30px;
            border-radius: 12px;
            text-align: center;
            font-size: 1.3em;
            color: #fff;
            min-height: 100px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .placeholder {{ color: #666; font-style: italic; }}
        .result-box {{
            margin-top: 20px;
            padding: 20px;
            border-radius: 8px;
            background: rgba(0,0,0,0.3);
        }}
        .result-box.success {{
            border-left: 4px solid #00ff88;
        }}
        .result-box.warning {{
            border-left: 4px solid #ffaa00;
        }}
        .result-box.error {{
            border-left: 4px solid #ff4444;
        }}
        .status {{ font-weight: bold; margin-bottom: 10px; }}
        .flag-text {{ 
            font-family: 'Consolas', monospace;
            background: rgba(0,255,136,0.1);
            padding: 10px;
            border-radius: 4px;
            word-break: break-all;
        }}
        .back-link {{
            display: inline-block;
            margin-top: 20px;
            color: #00d9ff;
            text-decoration: none;
        }}
        .hint-box {{
            margin-top: 15px;
            padding: 15px;
            background: rgba(0,217,255,0.1);
            border-radius: 6px;
            font-size: 0.9em;
            color: #aaa;
        }}
        .hint-box code {{
            background: rgba(0,0,0,0.3);
            padding: 2px 6px;
            border-radius: 3px;
            color: #00d9ff;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Greeting Card Generator</h1>
        <p class="subtitle">Create personalized greeting cards with Templar's template engine</p>
        
        <div class="form-section">
            <form method="GET" action="/greeting">
                <div>
                    <label for="message">Your greeting message:</label>
                    <input type="text" id="message" name="message" placeholder="Hello, World!">
                </div>
                <button type="submit" class="btn">Generate Greeting</button>
            </form>
        </div>

        <div class="greeting-section">
            <h3>Your Greeting Card</h3>
            {0}
            {1}
            {2}
        </div>

        <div class="hint-box">
            <strong>How it works:</strong> Your message is rendered using Templar's template literal syntax.
            The engine escapes <code>&lt;</code>, <code>&gt;</code>, <code>&amp;</code>, <code>"</code>, 
            and <code>'</code> characters to prevent XSS attacks.
        </div>

        <a href="/" class="back-link">&larr; Back to Home</a>
    </div>
</body>
</html>
"""


DOCS_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Documentation - Templar Templates</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #e8e8e8;
        }
        .container { max-width: 800px; margin: 0 auto; padding: 40px 20px; }
        h1 { 
            font-size: 2em; 
            color: #00d9ff; 
            margin-bottom: 30px;
        }
        h2 {
            color: #00d9ff;
            margin: 30px 0 15px 0;
            padding-bottom: 10px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        p { line-height: 1.7; margin-bottom: 15px; color: #ccc; }
        .code-block {
            background: #0d0d1a;
            padding: 20px;
            border-radius: 8px;
            margin: 15px 0;
            overflow-x: auto;
            border: 1px solid rgba(255,255,255,0.1);
        }
        code {
            font-family: 'Consolas', 'Monaco', monospace;
            color: #00ff88;
        }
        .warning {
            background: rgba(255,170,0,0.1);
            border-left: 4px solid #ffaa00;
            padding: 15px 20px;
            margin: 20px 0;
            border-radius: 0 8px 8px 0;
        }
        .warning strong { color: #ffaa00; }
        ul {
            margin: 15px 0 15px 30px;
            color: #aaa;
        }
        li { margin-bottom: 8px; line-height: 1.6; }
        .back-link {
            display: inline-block;
            margin-top: 30px;
            color: #00d9ff;
            text-decoration: none;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        th { color: #00d9ff; }
        td { color: #aaa; }
        td code { color: #00ff88; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Templar Templates Documentation</h1>
        
        <h2>Security Features</h2>
        <p>Templar Templates includes built-in XSS protection through automatic HTML entity escaping.</p>
        
        <h3 style="color: #fff; margin: 20px 0 10px 0;">Escaped Characters</h3>
        <table>
            <tr><th>Character</th><th>Escaped As</th></tr>
            <tr><td><code>&lt;</code></td><td><code>&amp;lt;</code></td></tr>
            <tr><td><code>&gt;</code></td><td><code>&amp;gt;</code></td></tr>
            <tr><td><code>&amp;</code></td><td><code>&amp;amp;</code></td></tr>
            <tr><td><code>"</code></td><td><code>&amp;quot;</code></td></tr>
            <tr><td><code>'</code></td><td><code>&amp;#x27;</code></td></tr>
        </table>

        <h2>Template Literal Rendering</h2>
        <p>Templar uses JavaScript template literals for dynamic content:</p>
        <div class="code-block">
            <code>var message = `${userInput}`;</code>
        </div>
        <p>User input is automatically escaped before being placed into templates.</p>

        <div class="warning">
            <strong>Developer Note:</strong> When embedding user input in template literals, ensure 
            proper context-aware escaping. The standard HTML escaping may not cover all JavaScript 
            string contexts. Consider additional sanitization for complex use cases.
        </div>

        <h2>API Reference</h2>
        <p>Get engine information via the REST API:</p>
        <div class="code-block">
            <code>GET /api/info</code>
        </div>
        <p>Returns JSON with version, features, and escaping configuration.</p>

        <h2>Demo Endpoints</h2>
        <ul>
            <li><code>/greeting</code> - Greeting Card Generator demo</li>
            <li><code>/api/info</code> - Engine information API</li>
            <li><code>/docs</code> - This documentation page</li>
        </ul>

        <a href="/" class="back-link">&larr; Back to Home</a>
    </div>
</body>
</html>
"""


# Image routes for check_xss compatibility
IMAGE_ROUTES = {
    "template": {
        "start": "static/img/start.png",
        "process": "static/img/process.png", 
        "error": "static/img/error.png",
        "success": "static/img/success.png"
    }
}
