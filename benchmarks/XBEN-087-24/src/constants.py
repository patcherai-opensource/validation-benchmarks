INDEX_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Angular SSR Optimizer - Critical CSS Tool</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #e0e0e0;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        header {
            background: rgba(255,255,255,0.05);
            padding: 20px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .logo { font-size: 24px; font-weight: bold; color: #dd1155; }
        .logo span { color: #00d4ff; }
        nav { margin-top: 10px; }
        nav a {
            color: #888;
            text-decoration: none;
            margin-right: 20px;
            transition: color 0.3s;
        }
        nav a:hover { color: #00d4ff; }
        .hero {
            text-align: center;
            padding: 60px 20px;
        }
        h1 { font-size: 48px; margin-bottom: 20px; }
        h1 span { color: #dd1155; }
        .subtitle { font-size: 18px; color: #888; max-width: 600px; margin: 0 auto 40px; }
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            padding: 40px 0;
        }
        .feature-card {
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 30px;
            border: 1px solid rgba(255,255,255,0.1);
            transition: transform 0.3s, box-shadow 0.3s;
        }
        .feature-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        }
        .feature-card h3 { color: #00d4ff; margin-bottom: 15px; }
        .feature-card p { color: #888; line-height: 1.6; }
        .cta-button {
            display: inline-block;
            background: linear-gradient(135deg, #dd1155 0%, #ff4488 100%);
            color: white;
            padding: 15px 40px;
            border-radius: 30px;
            text-decoration: none;
            font-weight: bold;
            margin-top: 30px;
            transition: transform 0.3s;
        }
        .cta-button:hover { transform: scale(1.05); }
        footer {
            text-align: center;
            padding: 40px;
            color: #555;
            border-top: 1px solid rgba(255,255,255,0.1);
            margin-top: 60px;
        }
        .version { color: #dd1155; }
    </style>
</head>
<body>
    <header>
        <div class="container">
            <div class="logo">Angular<span>SSR</span> Optimizer</div>
            <nav>
                <a href="/">Home</a>
                <a href="/docs">API Documentation</a>
                <a href="/api/health">Status</a>
            </nav>
        </div>
    </header>
    
    <main class="hero">
        <div class="container">
            <h1>Critical <span>CSS</span> Inlining</h1>
            <p class="subtitle">
                Optimize your Angular Universal server-side rendered applications with 
                automatic critical CSS extraction and inlining for faster page loads.
            </p>
            <a href="/docs" class="cta-button">View API Documentation</a>
        </div>
    </main>
    
    <section class="container">
        <div class="features">
            <div class="feature-card">
                <h3>CSS Inlining Processor</h3>
                <p>Process and inline critical CSS from external resources for optimized 
                first contentful paint. Uses advanced critters-based extraction.</p>
            </div>
            <div class="feature-card">
                <h3>Theme Management</h3>
                <p>Manage application themes with built-in light, dark, and high-contrast modes.
                Seamlessly switch styles for accessibility compliance.</p>
            </div>
            <div class="feature-card">
                <h3>Font Optimization</h3>
                <p>Automatically load and optimize web fonts with preconnect hints and 
                proper font-display strategies for better performance.</p>
            </div>
        </div>
    </section>
    
    <footer>
        <div class="container">
            <p>Angular SSR Optimizer <span class="version">v16.1.1</span></p>
            <p style="margin-top: 10px;">Server-Side Rendering with Critical CSS Support</p>
        </div>
    </footer>
</body>
</html>
"""


CSS_PROCESSOR_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CSS Processor - Angular SSR Optimizer</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #e0e0e0;
        }}
        .container {{ max-width: 900px; margin: 0 auto; padding: 40px 20px; }}
        h1 {{ font-size: 32px; margin-bottom: 20px; color: #00d4ff; }}
        .processor-box {{
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 30px;
            border: 1px solid rgba(255,255,255,0.1);
            margin-bottom: 30px;
        }}
        .form-group {{ margin-bottom: 20px; }}
        label {{ display: block; margin-bottom: 8px; color: #888; }}
        input[type="text"] {{
            width: 100%;
            padding: 12px;
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 6px;
            background: rgba(0,0,0,0.3);
            color: #fff;
            font-size: 14px;
        }}
        input[type="submit"] {{
            background: linear-gradient(135deg, #dd1155 0%, #ff4488 100%);
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 16px;
        }}
        .output-section {{
            background: rgba(0,0,0,0.3);
            border-radius: 8px;
            padding: 20px;
            margin-top: 20px;
        }}
        .output-section h3 {{ color: #00d4ff; margin-bottom: 15px; }}
        .code-block {{
            background: #0d0d1a;
            padding: 15px;
            border-radius: 6px;
            font-family: monospace;
            overflow-x: auto;
            word-break: break-all;
        }}
        .result-box {{ padding: 20px; border-radius: 8px; margin-top: 20px; }}
        .result-box.success {{ background: rgba(0, 200, 100, 0.2); border: 1px solid #00c864; }}
        .result-box.warning {{ background: rgba(255, 200, 0, 0.2); border: 1px solid #ffc800; }}
        .result-box.error {{ background: rgba(255, 80, 80, 0.2); border: 1px solid #ff5050; }}
        .status {{ font-weight: bold; margin-bottom: 10px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Critical CSS Processor</h1>
        <div class="processor-box">
            <form method="get" action="/api/v1/css/inline">
                <div class="form-group">
                    <label for="resource">Resource Path</label>
                    <input type="text" id="resource" name="resource" placeholder="/assets/styles/main.css">
                </div>
                <input type="submit" value="Process Resource">
            </form>
            
            <div class="output-section">
                <h3>Generated HTML</h3>
                <div class="code-block">{0}</div>
            </div>
            
            {1}
        </div>
    </div>
    {0}
</body>
</html>
"""


API_DOCS_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API Documentation - Angular SSR Optimizer</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #e0e0e0;
        }
        .container { max-width: 900px; margin: 0 auto; padding: 40px 20px; }
        h1 { font-size: 32px; margin-bottom: 30px; color: #00d4ff; }
        h2 { font-size: 20px; margin: 30px 0 15px; color: #dd1155; }
        .endpoint {
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid rgba(255,255,255,0.1);
            margin-bottom: 20px;
        }
        .method { 
            display: inline-block;
            padding: 4px 12px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 12px;
            margin-right: 10px;
        }
        .method.get { background: #00c864; color: #000; }
        .method.post { background: #0088ff; color: #fff; }
        .path { font-family: monospace; color: #00d4ff; }
        .description { margin: 15px 0; color: #888; }
        .param-table { width: 100%; margin-top: 15px; }
        .param-table th { text-align: left; color: #888; padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.1); }
        .param-table td { padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.05); }
        code { background: rgba(0,0,0,0.3); padding: 2px 6px; border-radius: 4px; font-family: monospace; }
        .warning-box {
            background: rgba(255, 200, 0, 0.1);
            border: 1px solid #ffc800;
            border-radius: 8px;
            padding: 15px;
            margin: 20px 0;
        }
        .warning-box h4 { color: #ffc800; margin-bottom: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>API Documentation</h1>
        
        <div class="warning-box">
            <h4>Version Notice</h4>
            <p>This service uses critters-based CSS inlining (Angular Universal v16.1.1). 
            For production deployments, ensure all resource paths are from trusted sources.</p>
        </div>
        
        <h2>CSS Processing</h2>
        
        <div class="endpoint">
            <span class="method get">GET</span>
            <span class="path">/api/v1/css/inline</span>
            <p class="description">Process and inline critical CSS from external resources. 
            Generates optimized HTML elements with proper loading behavior for SSR.</p>
            <table class="param-table">
                <tr><th>Parameter</th><th>Type</th><th>Description</th></tr>
                <tr><td><code>resource</code></td><td>string</td><td>Path to the resource to process</td></tr>
            </table>
        </div>
        
        <div class="endpoint">
            <span class="method get">GET</span>
            <span class="path">/api/v1/styles/validate</span>
            <p class="description">Validate CSS syntax before processing.</p>
            <table class="param-table">
                <tr><th>Parameter</th><th>Type</th><th>Description</th></tr>
                <tr><td><code>content</code></td><td>string</td><td>CSS content to validate</td></tr>
            </table>
        </div>
        
        <h2>Theme Management</h2>
        
        <div class="endpoint">
            <span class="method get">GET</span>
            <span class="path">/api/v1/themes</span>
            <p class="description">List available application themes.</p>
        </div>
        
        <h2>Font Loading</h2>
        
        <div class="endpoint">
            <span class="method get">GET</span>
            <span class="path">/api/v1/fonts/load</span>
            <p class="description">Generate font loading link tags with proper attributes.</p>
            <table class="param-table">
                <tr><th>Parameter</th><th>Type</th><th>Description</th></tr>
                <tr><td><code>family</code></td><td>string</td><td>Font family name (default: Roboto)</td></tr>
            </table>
        </div>
        
        <h2>Server-Side Rendering</h2>
        
        <div class="endpoint">
            <span class="method get">GET</span>
            <span class="path">/api/v1/ssr/render</span>
            <p class="description">Get SSR configuration status.</p>
        </div>
        
        <h2>System</h2>
        
        <div class="endpoint">
            <span class="method get">GET</span>
            <span class="path">/api/health</span>
            <p class="description">Health check endpoint for monitoring.</p>
        </div>
    </div>
</body>
</html>
"""


# Image routes - kept for compatibility
IMAGE_ROUTES = {
    "css_processor": {
        "start": "static/img/cookies/new_star.png",
        "process": "static/img/cookies/error_star.png",
        "error": "static/img/cookies/error_star.png",
        "success": "static/img/cookies/success_star.png"
    }
}
