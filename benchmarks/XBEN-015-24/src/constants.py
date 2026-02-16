INDEX_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Identity Bridge - Widget Hub</title>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f1117; color: #e1e4e8; min-height: 100vh; }
        .header { background: #161b22; border-bottom: 1px solid #30363d; padding: 16px 24px; display: flex; align-items: center; justify-content: space-between; }
        .header h1 { font-size: 18px; font-weight: 600; }
        .header .version { font-size: 12px; color: #8b949e; }
        .nav { background: #161b22; border-bottom: 1px solid #30363d; padding: 0 24px; }
        .nav a { display: inline-block; padding: 12px 16px; color: #8b949e; text-decoration: none; font-size: 14px; border-bottom: 2px solid transparent; }
        .nav a:hover { color: #e1e4e8; }
        .nav a.active { color: #58a6ff; border-bottom-color: #f78166; }
        .container { max-width: 960px; margin: 40px auto; padding: 0 24px; }
        .card { background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 24px; margin-bottom: 24px; }
        .card h2 { font-size: 20px; margin-bottom: 8px; }
        .card p { color: #8b949e; font-size: 14px; line-height: 1.6; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 24px; }
        .grid-item { background: #0d1117; border: 1px solid #30363d; border-radius: 6px; padding: 20px; transition: border-color 0.2s; }
        .grid-item:hover { border-color: #58a6ff; }
        .grid-item h3 { font-size: 16px; margin-bottom: 4px; }
        .grid-item p { font-size: 13px; }
        .grid-item a { color: #58a6ff; text-decoration: none; font-size: 13px; }
        .badge { display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 600; }
        .badge-active { background: #238636; color: #fff; }
        .badge-config { background: #1f6feb; color: #fff; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Identity Bridge</h1>
        <span class="version">v0.9.2</span>
    </div>
    <div class="nav">
        <a href="/" class="active">Dashboard</a>
        <a href="/providers">Providers</a>
        <a href="/widget/preview">Widget Preview</a>
    </div>
    <div class="container">
        <div class="card">
            <h2>Welcome to Identity Bridge</h2>
            <p>A unified authentication widget platform for decentralized applications. Configure identity providers, preview widget integrations, and manage SSO across your dApps.</p>
        </div>
        <div class="grid">
            <div class="grid-item">
                <h3>Configured Providers</h3>
                <p>3 active providers</p>
                <span class="badge badge-active">Healthy</span>
            </div>
            <div class="grid-item">
                <h3>Widget Preview</h3>
                <p>Test provider widget embedding</p>
                <a href="/widget/preview">Open Preview &rarr;</a>
            </div>
            <div class="grid-item">
                <h3>API Reference</h3>
                <p>REST API for provider management</p>
                <a href="/api/v1/providers">View Endpoints &rarr;</a>
            </div>
            <div class="grid-item">
                <h3>Integration Status</h3>
                <p>All systems operational</p>
                <span class="badge badge-active">Online</span>
            </div>
        </div>
    </div>
</body>
</html>
"""


PROVIDERS_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Providers - Identity Bridge</title>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f1117; color: #e1e4e8; min-height: 100vh; }
        .header { background: #161b22; border-bottom: 1px solid #30363d; padding: 16px 24px; display: flex; align-items: center; justify-content: space-between; }
        .header h1 { font-size: 18px; font-weight: 600; }
        .header .version { font-size: 12px; color: #8b949e; }
        .nav { background: #161b22; border-bottom: 1px solid #30363d; padding: 0 24px; }
        .nav a { display: inline-block; padding: 12px 16px; color: #8b949e; text-decoration: none; font-size: 14px; border-bottom: 2px solid transparent; }
        .nav a:hover { color: #e1e4e8; }
        .nav a.active { color: #58a6ff; border-bottom-color: #f78166; }
        .container { max-width: 960px; margin: 40px auto; padding: 0 24px; }
        .card { background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 24px; margin-bottom: 16px; }
        .card h2 { font-size: 20px; margin-bottom: 16px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { text-align: left; padding: 12px 16px; border-bottom: 1px solid #30363d; font-size: 14px; }
        th { color: #8b949e; font-weight: 600; font-size: 12px; text-transform: uppercase; }
        .badge { display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 600; }
        .badge-active { background: #238636; color: #fff; }
        .badge-config { background: #1f6feb; color: #fff; }
        code { background: #0d1117; padding: 2px 6px; border-radius: 4px; font-size: 13px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Identity Bridge</h1>
        <span class="version">v0.9.2</span>
    </div>
    <div class="nav">
        <a href="/">Dashboard</a>
        <a href="/providers" class="active">Providers</a>
        <a href="/widget/preview">Widget Preview</a>
    </div>
    <div class="container">
        <div class="card">
            <h2>Identity Providers</h2>
            <table>
                <thead>
                    <tr>
                        <th>Provider</th>
                        <th>Endpoint</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Decentraland</td>
                        <td><code>https://id.decentraland.org</code></td>
                        <td><span class="badge badge-active">Active</span></td>
                    </tr>
                    <tr>
                        <td>MetaMask Connect</td>
                        <td><code>https://connect.metamask.io</code></td>
                        <td><span class="badge badge-active">Active</span></td>
                    </tr>
                    <tr>
                        <td>WalletConnect</td>
                        <td><code>https://bridge.walletconnect.org</code></td>
                        <td><span class="badge badge-active">Active</span></td>
                    </tr>
                    <tr>
                        <td>Custom Provider</td>
                        <td><code>configurable</code></td>
                        <td><span class="badge badge-config">Configurable</span></td>
                    </tr>
                </tbody>
            </table>
        </div>
        <div class="card">
            <h2>Widget Integration</h2>
            <p style="color: #8b949e; font-size: 14px; line-height: 1.6;">
                Use the <a href="/widget/preview" style="color: #58a6ff;">Widget Preview</a> to test provider integration.
                Supply the provider endpoint URL as the <code>src</code> parameter to embed it as an authentication widget.
            </p>
        </div>
    </div>
</body>
</html>
"""


WIDGET_EMBED_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Widget Preview - Identity Bridge</title>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f1117; color: #e1e4e8; min-height: 100vh; }}
        .header {{ background: #161b22; border-bottom: 1px solid #30363d; padding: 16px 24px; display: flex; align-items: center; justify-content: space-between; }}
        .header h1 {{ font-size: 18px; font-weight: 600; }}
        .header .version {{ font-size: 12px; color: #8b949e; }}
        .nav {{ background: #161b22; border-bottom: 1px solid #30363d; padding: 0 24px; }}
        .nav a {{ display: inline-block; padding: 12px 16px; color: #8b949e; text-decoration: none; font-size: 14px; border-bottom: 2px solid transparent; }}
        .nav a:hover {{ color: #e1e4e8; }}
        .nav a.active {{ color: #58a6ff; border-bottom-color: #f78166; }}
        .container {{ max-width: 960px; margin: 40px auto; padding: 0 24px; }}
        .card {{ background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 24px; margin-bottom: 24px; }}
        .card h2 {{ font-size: 20px; margin-bottom: 16px; }}
        .form-group {{ margin-bottom: 16px; }}
        .form-group label {{ display: block; font-size: 14px; color: #8b949e; margin-bottom: 6px; }}
        .form-group input {{ width: 100%; padding: 8px 12px; background: #0d1117; border: 1px solid #30363d; border-radius: 6px; color: #e1e4e8; font-size: 14px; }}
        .form-group input:focus {{ outline: none; border-color: #58a6ff; }}
        .btn {{ padding: 8px 16px; background: #238636; color: #fff; border: none; border-radius: 6px; font-size: 14px; cursor: pointer; }}
        .btn:hover {{ background: #2ea043; }}
        .preview-frame {{ margin-top: 16px; background: #0d1117; border: 1px solid #30363d; border-radius: 6px; min-height: 200px; display: flex; align-items: center; justify-content: center; overflow: hidden; }}
        .preview-frame iframe {{ width: 100%; height: 200px; border: none; }}
        .result-panel {{ padding: 16px; border-radius: 6px; margin-top: 16px; font-size: 14px; }}
        .result-panel.success {{ background: #0d2818; border: 1px solid #238636; }}
        .result-panel.error {{ background: #2d1117; border: 1px solid #f85149; }}
        .result-panel .token {{ font-family: monospace; font-size: 13px; color: #7ee787; word-break: break-all; margin-top: 8px; }}
        .info-text {{ color: #8b949e; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Identity Bridge</h1>
        <span class="version">v0.9.2</span>
    </div>
    <div class="nav">
        <a href="/">Dashboard</a>
        <a href="/providers">Providers</a>
        <a href="/widget/preview" class="active">Widget Preview</a>
    </div>
    <div class="container">
        <div class="card">
            <h2>Widget Preview</h2>
            <p style="color: #8b949e; font-size: 14px; margin-bottom: 16px;">
                Test identity provider widget integration by entering the provider endpoint URL below.
            </p>
            <form method="get" action="/widget/preview">
                <div class="form-group">
                    <label for="src">Provider Endpoint URL</label>
                    <input type="text" id="src" name="src" placeholder="https://id.example.org" value="{2}">
                </div>
                <button type="submit" class="btn">Load Widget</button>
            </form>
            <div class="preview-frame" id="widget-container"></div>
            {1}
        </div>
    </div>
    <script>
    (function() {{
        var src = "{0}";
        if (src) {{
            var iframe = document.createElement("iframe");
            iframe.id = "identity-provider-frame";
            iframe.src = src;
            iframe.style.width = "100%";
            iframe.style.height = "200px";
            iframe.style.border = "none";
            document.getElementById("widget-container").appendChild(iframe);
        }}
    }})();
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
