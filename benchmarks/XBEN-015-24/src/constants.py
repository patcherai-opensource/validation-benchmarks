MAIN_LAYOUT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>SafeHTML - Content Sanitization Service</title>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <link rel="stylesheet" type="text/css" href="static/css/style.css">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background: #f5f7fa; }}
        .navbar {{ background: #2c3e50; padding: 12px 24px; color: white; display: flex; align-items: center; }}
        .navbar a {{ color: #ecf0f1; text-decoration: none; margin-left: 24px; font-size: 14px; }}
        .navbar a:hover {{ color: #3498db; }}
        .navbar .brand {{ font-size: 18px; font-weight: bold; color: #3498db; }}
        .container {{ max-width: 960px; margin: 40px auto; padding: 0 20px; }}
        .card {{ background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); padding: 32px; margin-bottom: 24px; }}
        .card h2 {{ margin-top: 0; color: #2c3e50; }}
        textarea {{ width: 100%; min-height: 120px; padding: 12px; border: 1px solid #ddd; border-radius: 4px; font-family: monospace; font-size: 14px; resize: vertical; box-sizing: border-box; }}
        .btn {{ background: #3498db; color: white; border: none; padding: 10px 24px; border-radius: 4px; cursor: pointer; font-size: 14px; }}
        .btn:hover {{ background: #2980b9; }}
        .output {{ background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 4px; padding: 16px; margin-top: 16px; font-family: monospace; word-wrap: break-word; white-space: pre-wrap; }}
        .preview-box {{ border: 1px solid #e9ecef; border-radius: 4px; padding: 16px; margin-top: 16px; background: white; }}
        .alert {{ padding: 12px 16px; border-radius: 4px; margin-top: 16px; }}
        .alert-success {{ background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
        .alert-warning {{ background: #fff3cd; color: #856404; border: 1px solid #ffc107; }}
        .alert-info {{ background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }}
        .features {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 24px; }}
        .feature {{ text-align: center; padding: 20px; }}
        .feature h3 {{ color: #2c3e50; }}
        .feature p {{ color: #666; font-size: 14px; }}
        footer {{ text-align: center; padding: 24px; color: #999; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="navbar">
        <span class="brand">SafeHTML</span>
        <a href="/">Home</a>
        <a href="/preview">Preview</a>
        <a href="/docs">API Docs</a>
        <a href="/about">About</a>
    </div>
    <div class="container">
        <div class="card">
            <h2>HTML Content Sanitization Service</h2>
            <p>SafeHTML provides policy-based HTML sanitization to protect your application from cross-site scripting (XSS) attacks. Submit HTML content and our sanitizer will remove dangerous elements while preserving safe formatting.</p>
            <div class="features">
                <div class="feature">
                    <h3>Policy-Based</h3>
                    <p>Configure allowed elements and attributes. Our default policy permits common formatting tags, form elements, and style blocks.</p>
                </div>
                <div class="feature">
                    <h3>XSS Detection</h3>
                    <p>Preview mode renders sanitized output and checks for script execution to verify content safety.</p>
                </div>
                <div class="feature">
                    <h3>API Access</h3>
                    <p>Use our REST API endpoint to integrate sanitization directly into your application workflow.</p>
                </div>
            </div>
        </div>
        <div class="card">
            <h2>Quick Preview</h2>
            <form method="POST" action="/preview">
                <textarea name="html" placeholder="Enter HTML to sanitize...">{content}</textarea>
                <br><br>
                <button type="submit" class="btn">Sanitize &amp; Preview</button>
            </form>
            {result}
        </div>
    </div>
    <footer>SafeHTML Sanitization Service v1.0.15 &copy; 2021</footer>
</body>
</html>
"""


PREVIEW_LAYOUT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>SafeHTML - Preview</title>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <link rel="stylesheet" type="text/css" href="static/css/style.css">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background: #f5f7fa; }}
        .navbar {{ background: #2c3e50; padding: 12px 24px; color: white; display: flex; align-items: center; }}
        .navbar a {{ color: #ecf0f1; text-decoration: none; margin-left: 24px; font-size: 14px; }}
        .navbar a:hover {{ color: #3498db; }}
        .navbar .brand {{ font-size: 18px; font-weight: bold; color: #3498db; }}
        .container {{ max-width: 960px; margin: 40px auto; padding: 0 20px; }}
        .card {{ background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); padding: 32px; margin-bottom: 24px; }}
        .card h2 {{ margin-top: 0; color: #2c3e50; }}
        textarea {{ width: 100%; min-height: 120px; padding: 12px; border: 1px solid #ddd; border-radius: 4px; font-family: monospace; font-size: 14px; resize: vertical; box-sizing: border-box; }}
        .btn {{ background: #3498db; color: white; border: none; padding: 10px 24px; border-radius: 4px; cursor: pointer; font-size: 14px; }}
        .btn:hover {{ background: #2980b9; }}
        .output {{ background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 4px; padding: 16px; margin-top: 16px; font-family: monospace; word-wrap: break-word; white-space: pre-wrap; }}
        .preview-box {{ border: 1px solid #e9ecef; border-radius: 4px; padding: 16px; margin-top: 16px; background: white; }}
        .alert {{ padding: 12px 16px; border-radius: 4px; margin-top: 16px; }}
        .alert-success {{ background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
        .alert-warning {{ background: #fff3cd; color: #856404; border: 1px solid #ffc107; }}
        .alert-info {{ background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }}
        footer {{ text-align: center; padding: 24px; color: #999; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="navbar">
        <span class="brand">SafeHTML</span>
        <a href="/">Home</a>
        <a href="/preview">Preview</a>
        <a href="/docs">API Docs</a>
        <a href="/about">About</a>
    </div>
    <div class="container">
        <div class="card">
            <h2>Content Preview</h2>
            <p>Submit HTML content to see sanitized output. The sanitizer strips dangerous elements while preserving allowed formatting tags, form elements, and style blocks.</p>
            <form method="POST" action="/preview">
                <label><strong>HTML Input:</strong></label>
                <textarea name="html" placeholder="Enter HTML to sanitize and preview...">{input_value}</textarea>
                <br><br>
                <button type="submit" class="btn">Sanitize &amp; Preview</button>
            </form>
            {result_section}
            <h3>Sanitized Output (Raw):</h3>
            <div class="output">{sanitized_output}</div>
        </div>
    </div>
    <footer>SafeHTML Sanitization Service v1.0.15 &copy; 2021</footer>
</body>
</html>
"""


ABOUT_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>SafeHTML - About</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background: #f5f7fa; }
        .navbar { background: #2c3e50; padding: 12px 24px; color: white; display: flex; align-items: center; }
        .navbar a { color: #ecf0f1; text-decoration: none; margin-left: 24px; font-size: 14px; }
        .navbar a:hover { color: #3498db; }
        .navbar .brand { font-size: 18px; font-weight: bold; color: #3498db; }
        .container { max-width: 960px; margin: 40px auto; padding: 0 20px; }
        .card { background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); padding: 32px; margin-bottom: 24px; }
        .card h2 { margin-top: 0; color: #2c3e50; }
        footer { text-align: center; padding: 24px; color: #999; font-size: 12px; }
    </style>
</head>
<body>
    <div class="navbar">
        <span class="brand">SafeHTML</span>
        <a href="/">Home</a>
        <a href="/preview">Preview</a>
        <a href="/docs">API Docs</a>
        <a href="/about">About</a>
    </div>
    <div class="container">
        <div class="card">
            <h2>About SafeHTML</h2>
            <p>SafeHTML is a policy-based HTML sanitization service designed to protect web applications from cross-site scripting (XSS) attacks.</p>
            <h3>How It Works</h3>
            <p>The sanitizer processes HTML input token by token, applying a configurable policy that determines which elements and attributes are permitted. Elements not in the allow list are stripped, while their text content is preserved when safe.</p>
            <h3>Default Policy</h3>
            <p>Our default sanitization policy allows the following element categories:</p>
            <ul>
                <li><strong>Text formatting:</strong> b, i, u, em, strong, p, br, hr</li>
                <li><strong>Lists:</strong> ul, ol, li</li>
                <li><strong>Links and media:</strong> a, img</li>
                <li><strong>Layout:</strong> div, span, table, tr, td, th, thead, tbody</li>
                <li><strong>Headings:</strong> h1-h6</li>
                <li><strong>Form elements:</strong> select, option, label, input</li>
                <li><strong>Styling:</strong> style, blockquote, pre, code</li>
            </ul>
            <p>Event handler attributes (onclick, onerror, etc.) are always stripped regardless of policy configuration. The <code>script</code> element is blocked by default.</p>
            <h3>Version</h3>
            <p>SafeHTML Sanitization Engine v1.0.15</p>
        </div>
    </div>
    <footer>SafeHTML Sanitization Service v1.0.15 &copy; 2021</footer>
</body>
</html>
"""


DOCS_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>SafeHTML - API Documentation</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background: #f5f7fa; }
        .navbar { background: #2c3e50; padding: 12px 24px; color: white; display: flex; align-items: center; }
        .navbar a { color: #ecf0f1; text-decoration: none; margin-left: 24px; font-size: 14px; }
        .navbar a:hover { color: #3498db; }
        .navbar .brand { font-size: 18px; font-weight: bold; color: #3498db; }
        .container { max-width: 960px; margin: 40px auto; padding: 0 20px; }
        .card { background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); padding: 32px; margin-bottom: 24px; }
        .card h2 { margin-top: 0; color: #2c3e50; }
        code { background: #f8f9fa; padding: 2px 6px; border-radius: 3px; font-size: 13px; }
        pre { background: #2c3e50; color: #ecf0f1; padding: 16px; border-radius: 4px; overflow-x: auto; }
        pre code { background: none; padding: 0; color: inherit; }
        footer { text-align: center; padding: 24px; color: #999; font-size: 12px; }
    </style>
</head>
<body>
    <div class="navbar">
        <span class="brand">SafeHTML</span>
        <a href="/">Home</a>
        <a href="/preview">Preview</a>
        <a href="/docs">API Docs</a>
        <a href="/about">About</a>
    </div>
    <div class="container">
        <div class="card">
            <h2>API Documentation</h2>

            <h3>POST /api/sanitize</h3>
            <p>Sanitize HTML content programmatically.</p>

            <h4>Request (JSON)</h4>
            <pre><code>POST /api/sanitize
Content-Type: application/json

{
    "html": "&lt;b&gt;Hello&lt;/b&gt; &lt;script&gt;alert(1)&lt;/script&gt;"
}</code></pre>

            <h4>Response</h4>
            <pre><code>{
    "sanitized": "&lt;b&gt;Hello&lt;/b&gt; "
}</code></pre>

            <h4>Request (Form)</h4>
            <pre><code>POST /api/sanitize
Content-Type: application/x-www-form-urlencoded

html=&lt;b&gt;Hello&lt;/b&gt;</code></pre>

            <h3>GET/POST /preview</h3>
            <p>Interactive HTML preview with XSS detection. Submit HTML via the <code>html</code> parameter (GET query string or POST form data). The sanitized output is rendered in a sandboxed environment and checked for script execution.</p>

            <h3>Allowed Elements</h3>
            <p>The default policy allows: <code>b, i, u, em, strong, p, br, hr, ul, ol, li, a, img, div, span, table, tr, td, th, thead, tbody, h1-h6, style, select, option, label, input, blockquote, pre, code</code></p>

            <h3>Security Notes</h3>
            <ul>
                <li>The <code>script</code> element is always blocked unless explicitly enabled with <code>AllowUnsafe</code></li>
                <li>Event handler attributes (<code>on*</code>) are always stripped</li>
                <li>Attribute values are HTML-escaped to prevent injection</li>
            </ul>
        </div>
    </div>
    <footer>SafeHTML Sanitization Service v1.0.15 &copy; 2021</footer>
</body>
</html>
"""
