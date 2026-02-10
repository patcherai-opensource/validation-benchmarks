INDEX_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AuthConnect - Enterprise SSO Solutions</title>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .navbar { background: rgba(255,255,255,0.1); padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; backdrop-filter: blur(10px); }
        .logo { color: white; font-size: 1.5rem; font-weight: bold; text-decoration: none; }
        .nav-links { display: flex; gap: 2rem; }
        .nav-links a { color: rgba(255,255,255,0.9); text-decoration: none; transition: color 0.3s; }
        .nav-links a:hover { color: white; }
        .hero { text-align: center; padding: 4rem 2rem; color: white; }
        .hero h1 { font-size: 3rem; margin-bottom: 1rem; }
        .hero p { font-size: 1.25rem; opacity: 0.9; max-width: 600px; margin: 0 auto 2rem; }
        .cta-button { background: white; color: #667eea; padding: 1rem 2rem; border-radius: 50px; text-decoration: none; font-weight: bold; transition: transform 0.3s, box-shadow 0.3s; display: inline-block; }
        .cta-button:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(0,0,0,0.2); }
        .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; padding: 4rem 2rem; max-width: 1200px; margin: 0 auto; }
        .feature-card { background: white; border-radius: 20px; padding: 2rem; text-align: center; box-shadow: 0 10px 40px rgba(0,0,0,0.1); }
        .feature-card h3 { color: #333; margin: 1rem 0; }
        .feature-card p { color: #666; }
        .feature-icon { font-size: 3rem; }
        .footer { text-align: center; padding: 2rem; color: rgba(255,255,255,0.7); }
    </style>
</head>
<body>
    <nav class="navbar">
        <a href="/" class="logo">AuthConnect</a>
        <div class="nav-links">
            <a href="/">Home</a>
            <a href="/demo">Widget Demo</a>
            <a href="/api/providers">API</a>
        </div>
    </nav>
    
    <section class="hero">
        <h1>Enterprise Single Sign-On</h1>
        <p>Seamlessly integrate authentication across your applications with our lightweight SSO widget. One login, unlimited access.</p>
        <a href="/demo" class="cta-button">Try Widget Demo</a>
    </section>
    
    <section class="features">
        <div class="feature-card">
            <div class="feature-icon">🔐</div>
            <h3>Secure Authentication</h3>
            <p>Industry-standard OAuth 2.0 and OpenID Connect protocols for maximum security.</p>
        </div>
        <div class="feature-card">
            <div class="feature-icon">⚡</div>
            <h3>Easy Integration</h3>
            <p>Add SSO to your app in minutes with our simple JavaScript widget.</p>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🌐</div>
            <h3>Multiple Providers</h3>
            <p>Support for Google, GitHub, Azure AD, and custom identity providers.</p>
        </div>
    </section>
    
    <footer class="footer">
        <p>&copy; 2024 AuthConnect. Enterprise SSO Solutions.</p>
    </footer>
</body>
</html>
"""


SSO_DEMO_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SSO Widget Demo - AuthConnect</title>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif; background: #f5f7fa; min-height: 100vh; }
        .navbar { background: #667eea; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; }
        .logo { color: white; font-size: 1.5rem; font-weight: bold; text-decoration: none; }
        .nav-links { display: flex; gap: 2rem; }
        .nav-links a { color: rgba(255,255,255,0.9); text-decoration: none; }
        .container { max-width: 800px; margin: 2rem auto; padding: 0 1rem; }
        .demo-panel { background: white; border-radius: 12px; padding: 2rem; box-shadow: 0 4px 20px rgba(0,0,0,0.1); margin-bottom: 2rem; }
        .demo-panel h2 { color: #333; margin-bottom: 1rem; }
        .demo-panel p { color: #666; margin-bottom: 1.5rem; }
        .form-group { margin-bottom: 1rem; }
        .form-group label { display: block; color: #333; font-weight: 500; margin-bottom: 0.5rem; }
        .form-group input { width: 100%; padding: 0.75rem; border: 2px solid #e1e5eb; border-radius: 8px; font-size: 1rem; transition: border-color 0.3s; }
        .form-group input:focus { outline: none; border-color: #667eea; }
        .btn { background: #667eea; color: white; padding: 0.75rem 1.5rem; border: none; border-radius: 8px; font-size: 1rem; cursor: pointer; transition: background 0.3s; }
        .btn:hover { background: #5a6fd6; }
        .code-block { background: #1e1e1e; color: #d4d4d4; padding: 1.5rem; border-radius: 8px; overflow-x: auto; font-family: 'Monaco', 'Menlo', monospace; font-size: 0.875rem; margin: 1rem 0; }
        .code-comment { color: #6a9955; }
        .code-string { color: #ce9178; }
        .code-keyword { color: #569cd6; }
        .preview-frame { width: 100%; height: 400px; border: 2px solid #e1e5eb; border-radius: 8px; background: white; }
        .warning-box { background: #fff3cd; border: 1px solid #ffc107; border-radius: 8px; padding: 1rem; margin-bottom: 1rem; }
        .warning-box p { color: #856404; margin: 0; }
    </style>
</head>
<body>
    <nav class="navbar">
        <a href="/" class="logo">AuthConnect</a>
        <div class="nav-links">
            <a href="/">Home</a>
            <a href="/demo">Widget Demo</a>
            <a href="/api/providers">API</a>
        </div>
    </nav>
    
    <div class="container">
        <div class="demo-panel">
            <h2>SSO Widget Integration Demo</h2>
            <p>Test the SSO widget by providing an identity provider URL. The widget will initialize an authentication iframe with the specified provider.</p>
            
            <form id="sso-form" action="/widget/init" method="GET">
                <div class="form-group">
                    <label for="provider">Identity Provider URL</label>
                    <input type="text" id="provider" name="provider" placeholder="https://your-identity-provider.com/auth" value="">
                </div>
                <button type="submit" class="btn">Initialize SSO Widget</button>
            </form>
        </div>
        
        <div class="demo-panel">
            <h2>Integration Code</h2>
            <p>Add SSO authentication to your application with just a few lines of code:</p>
            <div class="code-block">
<span class="code-comment">// Import the SSO client library</span>
<span class="code-keyword">import</span> { SingleSignOn } <span class="code-keyword">from</span> <span class="code-string">'@authconnect/sso-client'</span>;

<span class="code-comment">// Initialize with your identity provider URL</span>
SingleSignOn.init(<span class="code-string">'https://your-provider.com/auth'</span>);

<span class="code-comment">// Handle authentication callback</span>
SingleSignOn.onAuthenticated((user) => {
  console.log(<span class="code-string">'User authenticated:'</span>, user);
});
            </div>
        </div>
        
        <div class="demo-panel">
            <h2>Available Providers</h2>
            <p>We support integration with major identity providers:</p>
            <ul style="list-style: none; padding: 0; margin-top: 1rem;">
                <li style="padding: 0.5rem 0; border-bottom: 1px solid #eee;">Google - <code>https://accounts.google.com</code></li>
                <li style="padding: 0.5rem 0; border-bottom: 1px solid #eee;">GitHub - <code>https://github.com/login</code></li>
                <li style="padding: 0.5rem 0; border-bottom: 1px solid #eee;">Azure AD - <code>https://login.microsoftonline.com</code></li>
                <li style="padding: 0.5rem 0;">Custom - Any OAuth 2.0 / OpenID Connect provider</li>
            </ul>
        </div>
    </div>
</body>
</html>
"""


SSO_WIDGET_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SSO Authentication - AuthConnect</title>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif; background: #f5f7fa; min-height: 100vh; display: flex; flex-direction: column; }}
        .navbar {{ background: #667eea; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; }}
        .logo {{ color: white; font-size: 1.5rem; font-weight: bold; text-decoration: none; }}
        .nav-links {{ display: flex; gap: 2rem; }}
        .nav-links a {{ color: rgba(255,255,255,0.9); text-decoration: none; }}
        .widget-container {{ flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 2rem; }}
        .widget-box {{ background: white; border-radius: 16px; padding: 2rem; box-shadow: 0 10px 40px rgba(0,0,0,0.1); width: 100%; max-width: 500px; text-align: center; }}
        .widget-box h2 {{ color: #333; margin-bottom: 1rem; }}
        .auth-iframe {{ width: 100%; height: 300px; border: 1px solid #e1e5eb; border-radius: 8px; background: #fafafa; }}
        .status {{ padding: 1rem; border-radius: 8px; margin-top: 1rem; }}
        .status.success {{ background: #d4edda; color: #155724; word-break: break-all; }}
        .status.error {{ background: #f8d7da; color: #721c24; }}
        .back-link {{ margin-top: 1rem; }}
        .back-link a {{ color: #667eea; text-decoration: none; }}
    </style>
</head>
<body>
    <nav class="navbar">
        <a href="/" class="logo">AuthConnect</a>
        <div class="nav-links">
            <a href="/">Home</a>
            <a href="/demo">Widget Demo</a>
            <a href="/api/providers">API</a>
        </div>
    </nav>
    
    <div class="widget-container">
        <div class="widget-box">
            <h2>Single Sign-On</h2>
            <p style="color: #666; margin-bottom: 1.5rem;">Authenticating with your identity provider...</p>
            <iframe class="auth-iframe" src="{provider_src}" sandbox="allow-scripts allow-same-origin allow-forms"></iframe>
            {status_message}
            <div class="back-link">
                <a href="/demo">&larr; Back to Demo</a>
            </div>
        </div>
    </div>
    {callback_result}
</body>
</html>
"""


SSO_WIDGET_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>SSO Widget</title>
</head>
<body>
    <iframe id="sso-provider-frame" src="{provider_src}"></iframe>
    <script>
        window.addEventListener('message', function(event) {{
            if (event.data && event.data.type === 'auth_response') {{
                window.parent.postMessage(event.data, '*');
            }}
        }});
    </script>
</body>
</html>
"""


IMAGE_ROUTES = {
    "xss_easy": {
        "start": "static/img/cookies/new_circle.png",
        "process": "static/img/cookies/error_circle.png",
        "error": "static/img/cookies/error_circle.png",
        "success": "static/img/cookies/success_circle.png"
    }
}
