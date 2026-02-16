INDEX_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Identity Bridge - SSO Integration Platform</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0d1117; color: #c9d1d9; }
        .header { background: #161b22; border-bottom: 1px solid #30363d; padding: 16px 32px; display: flex; align-items: center; justify-content: space-between; }
        .header h1 { font-size: 20px; color: #f0f6fc; }
        .header .nav { display: flex; gap: 24px; }
        .header .nav a { color: #8b949e; text-decoration: none; font-size: 14px; }
        .header .nav a:hover { color: #f0f6fc; }
        .container { max-width: 960px; margin: 40px auto; padding: 0 20px; }
        .hero { text-align: center; margin-bottom: 48px; }
        .hero h2 { font-size: 32px; color: #f0f6fc; margin-bottom: 12px; }
        .hero p { font-size: 16px; color: #8b949e; max-width: 600px; margin: 0 auto; }
        .cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; }
        .card { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 24px; transition: border-color 0.2s; }
        .card:hover { border-color: #58a6ff; }
        .card h3 { color: #f0f6fc; margin-bottom: 8px; font-size: 18px; }
        .card p { color: #8b949e; font-size: 14px; margin-bottom: 16px; line-height: 1.5; }
        .card a { color: #58a6ff; text-decoration: none; font-size: 14px; font-weight: 500; }
        .card a:hover { text-decoration: underline; }
        .footer { text-align: center; margin-top: 80px; padding: 24px; color: #484f58; font-size: 12px; border-top: 1px solid #21262d; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Identity Bridge</h1>
        <div class="nav">
            <a href="/">Dashboard</a>
            <a href="/docs">Documentation</a>
            <a href="/widget/configure">Widget Setup</a>
            <a href="/widget/sessions">Sessions</a>
        </div>
    </div>
    <div class="container">
        <div class="hero">
            <h2>SSO Integration Platform</h2>
            <p>Configure and manage single sign-on widgets for your decentralized applications. Connect identity providers seamlessly.</p>
        </div>
        <div class="cards">
            <div class="card">
                <h3>Widget Setup</h3>
                <p>Configure your SSO widget by providing your identity provider URL. Preview the integration before deploying to production.</p>
                <a href="/widget/configure">Configure Widget &rarr;</a>
            </div>
            <div class="card">
                <h3>Session Management</h3>
                <p>View and manage active authentication sessions. Monitor identity provider connections and user sign-on status.</p>
                <a href="/widget/sessions">View Sessions &rarr;</a>
            </div>
            <div class="card">
                <h3>Documentation</h3>
                <p>Integration guides, API reference, and best practices for embedding the SSO widget in your application.</p>
                <a href="/docs">Read Docs &rarr;</a>
            </div>
        </div>
    </div>
    <div class="footer">
        &copy; 2023 Identity Bridge Platform. All rights reserved.
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
    <title>Documentation - Identity Bridge</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0d1117; color: #c9d1d9; }
        .header { background: #161b22; border-bottom: 1px solid #30363d; padding: 16px 32px; display: flex; align-items: center; justify-content: space-between; }
        .header h1 { font-size: 20px; color: #f0f6fc; }
        .header .nav { display: flex; gap: 24px; }
        .header .nav a { color: #8b949e; text-decoration: none; font-size: 14px; }
        .header .nav a:hover { color: #f0f6fc; }
        .container { max-width: 800px; margin: 40px auto; padding: 0 20px; }
        h2 { color: #f0f6fc; margin: 32px 0 12px; font-size: 24px; border-bottom: 1px solid #21262d; padding-bottom: 8px; }
        h3 { color: #f0f6fc; margin: 20px 0 8px; font-size: 18px; }
        p { color: #8b949e; font-size: 14px; line-height: 1.7; margin-bottom: 12px; }
        code { background: #161b22; color: #79c0ff; padding: 2px 6px; border-radius: 4px; font-size: 13px; }
        pre { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 16px; overflow-x: auto; margin: 12px 0; }
        pre code { padding: 0; background: none; }
        .note { background: #161b22; border-left: 3px solid #58a6ff; padding: 12px 16px; margin: 16px 0; border-radius: 0 6px 6px 0; }
        .note p { margin: 0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Identity Bridge</h1>
        <div class="nav">
            <a href="/">Dashboard</a>
            <a href="/docs">Documentation</a>
            <a href="/widget/configure">Widget Setup</a>
            <a href="/widget/sessions">Sessions</a>
        </div>
    </div>
    <div class="container">
        <h2>Getting Started</h2>
        <p>Identity Bridge provides a simple integration for adding single sign-on capabilities to your web applications using embedded widgets.</p>

        <h3>Widget Integration</h3>
        <p>The SSO widget works by embedding an iframe from your identity provider into the page. This iframe handles the authentication flow and communicates session data back to the parent application.</p>

        <pre><code>// Initialize the widget with your provider URL
IdentityBridge.setup("https://your-identity-provider.example.com");
</code></pre>

        <h3>Configuration</h3>
        <p>Use the <a href="/widget/configure" style="color: #58a6ff;">Widget Setup</a> page to configure and preview your identity provider integration. Enter your provider URL and the system will generate a preview of the embedded widget.</p>

        <h3>Preview Endpoint</h3>
        <p>The preview endpoint accepts a <code>provider</code> parameter with the URL of your identity provider:</p>

        <pre><code>GET /widget/preview?provider=https://your-provider.example.com</code></pre>

        <p>The provider URL is embedded into a preview page to test the integration before deploying. The preview renders the widget frame with the specified provider source.</p>

        <div class="note">
            <p>The preview page renders the provider URL in an embedded frame context to simulate the production widget behavior.</p>
        </div>

        <h3>Session Management</h3>
        <p>Active sessions can be monitored through the <a href="/widget/sessions" style="color: #58a6ff;">Sessions</a> page. Each session tracks the identity provider connection status and authenticated user information.</p>

        <h2>API Reference</h2>

        <h3>GET /widget/preview</h3>
        <p>Generates a preview of the SSO widget with the specified identity provider.</p>
        <p><strong>Parameters:</strong></p>
        <p><code>provider</code> - The URL of the identity provider to embed in the widget frame.</p>

        <h3>GET /widget/sessions</h3>
        <p>Lists active authentication sessions.</p>
        <p><strong>Parameters:</strong></p>
        <p><code>action</code> - Action to perform: <code>list</code> (default), <code>get</code></p>
        <p><code>user</code> - User address to look up (required for <code>get</code> action)</p>
    </div>
</body>
</html>
"""

WIDGET_CONFIG_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Widget Setup - Identity Bridge</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0d1117; color: #c9d1d9; }
        .header { background: #161b22; border-bottom: 1px solid #30363d; padding: 16px 32px; display: flex; align-items: center; justify-content: space-between; }
        .header h1 { font-size: 20px; color: #f0f6fc; }
        .header .nav { display: flex; gap: 24px; }
        .header .nav a { color: #8b949e; text-decoration: none; font-size: 14px; }
        .header .nav a:hover { color: #f0f6fc; }
        .container { max-width: 640px; margin: 40px auto; padding: 0 20px; }
        h2 { color: #f0f6fc; margin-bottom: 8px; font-size: 24px; }
        .subtitle { color: #8b949e; font-size: 14px; margin-bottom: 24px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; color: #c9d1d9; font-size: 14px; font-weight: 500; margin-bottom: 6px; }
        .help-text { color: #8b949e; font-size: 12px; margin-top: 4px; }
        input[type="text"] { width: 100%; padding: 10px 12px; background: #0d1117; border: 1px solid #30363d; border-radius: 6px; color: #c9d1d9; font-size: 14px; }
        input[type="text"]:focus { outline: none; border-color: #58a6ff; box-shadow: 0 0 0 3px rgba(88,166,255,0.15); }
        .btn { display: inline-block; padding: 10px 20px; background: #238636; color: #fff; border: 1px solid rgba(240,246,252,0.1); border-radius: 6px; cursor: pointer; font-size: 14px; font-weight: 500; text-decoration: none; }
        .btn:hover { background: #2ea043; }
        .panel { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 24px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Identity Bridge</h1>
        <div class="nav">
            <a href="/">Dashboard</a>
            <a href="/docs">Documentation</a>
            <a href="/widget/configure">Widget Setup</a>
            <a href="/widget/sessions">Sessions</a>
        </div>
    </div>
    <div class="container">
        <h2>Widget Setup</h2>
        <p class="subtitle">Configure your SSO widget by providing the identity provider URL. A preview will be generated to verify the integration.</p>
        <div class="panel">
            <form action="/widget/preview" method="get">
                <div class="form-group">
                    <label for="provider">Identity Provider URL</label>
                    <input type="text" id="provider" name="provider" placeholder="https://id.example.com">
                    <p class="help-text">Enter the URL of your identity provider. This URL will be loaded in the widget frame.</p>
                </div>
                <button type="submit" class="btn">Generate Preview</button>
            </form>
        </div>
    </div>
</body>
</html>
"""

WIDGET_PREVIEW_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Widget Preview - Identity Bridge</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0d1117; color: #c9d1d9; }}
        .header {{ background: #161b22; border-bottom: 1px solid #30363d; padding: 16px 32px; display: flex; align-items: center; justify-content: space-between; }}
        .header h1 {{ font-size: 20px; color: #f0f6fc; }}
        .header .nav {{ display: flex; gap: 24px; }}
        .header .nav a {{ color: #8b949e; text-decoration: none; font-size: 14px; }}
        .header .nav a:hover {{ color: #f0f6fc; }}
        .container {{ max-width: 800px; margin: 40px auto; padding: 0 20px; }}
        h2 {{ color: #f0f6fc; margin-bottom: 8px; font-size: 24px; }}
        .subtitle {{ color: #8b949e; font-size: 14px; margin-bottom: 24px; }}
        .panel {{ background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 24px; margin-bottom: 20px; }}
        .field-label {{ color: #8b949e; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; }}
        .field-value {{ color: #c9d1d9; font-size: 14px; font-family: monospace; word-break: break-all; }}
        .status {{ margin-top: 16px; padding: 12px 16px; border-radius: 6px; font-size: 14px; }}
        .btn {{ display: inline-block; padding: 8px 16px; background: #21262d; color: #c9d1d9; border: 1px solid #30363d; border-radius: 6px; cursor: pointer; font-size: 14px; text-decoration: none; }}
        .btn:hover {{ background: #30363d; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Identity Bridge</h1>
        <div class="nav">
            <a href="/">Dashboard</a>
            <a href="/docs">Documentation</a>
            <a href="/widget/configure">Widget Setup</a>
            <a href="/widget/sessions">Sessions</a>
        </div>
    </div>
    <div class="container">
        <h2>Widget Preview</h2>
        <p class="subtitle">Preview of your SSO widget configuration.</p>
        <div class="panel">
            <div class="field-label">Provider URL</div>
            <div class="field-value">{0}</div>
            {1}
        </div>
        <a href="/widget/configure" class="btn">&larr; Back to Setup</a>
    </div>
</body>
</html>
"""

WIDGET_STATUS_EMPTY = '<div class="status" style="background: #161b22; border: 1px solid #30363d; color: #8b949e;">No provider URL specified. Please configure a provider URL to preview the widget.</div>'

WIDGET_STATUS_CONFIGURED = '<div class="status" style="background: #0d2240; border: 1px solid #1f6feb; color: #58a6ff;">Provider configured: {0}. Widget frame rendered for preview.</div>'

WIDGET_STATUS_SUCCESS = '<div class="status" style="background: #0d2d1a; border: 1px solid #238636; color: #3fb950;">Widget verification successful. Integration token: {0}</div>'

# Template used for the actual rendering page that PhantomJS processes
# This mirrors the CVE pattern: iframe.src = user_controlled_value
WIDGET_RENDER_TEMPLATE = """
<html>
<head><title>Widget Frame Render</title></head>
<body>
<div id="widget-container">
<iframe id="identity-bridge-frame" src="{0}" style="width:0;height:0;border:none;position:absolute;"></iframe>
</div>
</body>
</html>
"""

SESSIONS_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sessions - Identity Bridge</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0d1117; color: #c9d1d9; }
        .header { background: #161b22; border-bottom: 1px solid #30363d; padding: 16px 32px; display: flex; align-items: center; justify-content: space-between; }
        .header h1 { font-size: 20px; color: #f0f6fc; }
        .header .nav { display: flex; gap: 24px; }
        .header .nav a { color: #8b949e; text-decoration: none; font-size: 14px; }
        .header .nav a:hover { color: #f0f6fc; }
        .container { max-width: 800px; margin: 40px auto; padding: 0 20px; }
        h2 { color: #f0f6fc; margin-bottom: 8px; font-size: 24px; }
        .subtitle { color: #8b949e; font-size: 14px; margin-bottom: 24px; }
        .panel { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 24px; }
        table { width: 100%; border-collapse: collapse; }
        th { text-align: left; color: #8b949e; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; padding: 8px 12px; border-bottom: 1px solid #30363d; }
        td { padding: 10px 12px; border-bottom: 1px solid #21262d; font-size: 14px; color: #c9d1d9; }
        .status-badge { display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 12px; }
        .status-active { background: #0d2d1a; color: #3fb950; }
        .status-expired { background: #2d1117; color: #f85149; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Identity Bridge</h1>
        <div class="nav">
            <a href="/">Dashboard</a>
            <a href="/docs">Documentation</a>
            <a href="/widget/configure">Widget Setup</a>
            <a href="/widget/sessions">Sessions</a>
        </div>
    </div>
    <div class="container">
        <h2>Active Sessions</h2>
        <p class="subtitle">Authentication sessions managed through the identity bridge widget.</p>
        <div class="panel">
            <table>
                <thead>
                    <tr>
                        <th>User Address</th>
                        <th>Provider</th>
                        <th>Status</th>
                        <th>Expiry</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><code>0x7a3b...4f2e</code></td>
                        <td>id.decentraland.zone</td>
                        <td><span class="status-badge status-active">Active</span></td>
                        <td>2024-03-15 14:30 UTC</td>
                    </tr>
                    <tr>
                        <td><code>0x9c1d...8a3b</code></td>
                        <td>auth.example.com</td>
                        <td><span class="status-badge status-expired">Expired</span></td>
                        <td>2024-01-02 09:15 UTC</td>
                    </tr>
                    <tr>
                        <td><code>0x2e5f...1c7d</code></td>
                        <td>id.decentraland.zone</td>
                        <td><span class="status-badge status-active">Active</span></td>
                        <td>2024-04-01 22:00 UTC</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""

SESSIONS_DETAIL_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Session Detail - Identity Bridge</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0d1117; color: #c9d1d9; }}
        .header {{ background: #161b22; border-bottom: 1px solid #30363d; padding: 16px 32px; display: flex; align-items: center; justify-content: space-between; }}
        .header h1 {{ font-size: 20px; color: #f0f6fc; }}
        .header .nav {{ display: flex; gap: 24px; }}
        .header .nav a {{ color: #8b949e; text-decoration: none; font-size: 14px; }}
        .header .nav a:hover {{ color: #f0f6fc; }}
        .container {{ max-width: 640px; margin: 40px auto; padding: 0 20px; }}
        h2 {{ color: #f0f6fc; margin-bottom: 16px; font-size: 24px; }}
        .panel {{ background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 24px; }}
        .field {{ margin-bottom: 12px; }}
        .field-label {{ color: #8b949e; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 2px; }}
        .field-value {{ color: #c9d1d9; font-size: 14px; }}
        .btn {{ display: inline-block; padding: 8px 16px; background: #21262d; color: #c9d1d9; border: 1px solid #30363d; border-radius: 6px; cursor: pointer; font-size: 14px; text-decoration: none; margin-top: 16px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Identity Bridge</h1>
        <div class="nav">
            <a href="/">Dashboard</a>
            <a href="/docs">Documentation</a>
            <a href="/widget/configure">Widget Setup</a>
            <a href="/widget/sessions">Sessions</a>
        </div>
    </div>
    <div class="container">
        <h2>Session Detail</h2>
        <div class="panel">
            <div class="field">
                <div class="field-label">User Address</div>
                <div class="field-value">{0}</div>
            </div>
            <div class="field">
                <div class="field-label">Status</div>
                <div class="field-value">No active session found for this address.</div>
            </div>
        </div>
        <a href="/widget/sessions" class="btn">&larr; Back to Sessions</a>
    </div>
</body>
</html>
"""
