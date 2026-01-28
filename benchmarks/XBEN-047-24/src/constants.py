INDEX_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DCL SSO Client - Demo Portal</title>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
        body { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); min-height: 100vh; color: #fff; }
        .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
        .header { text-align: center; padding: 3rem 0; }
        .header h1 { font-size: 2.5rem; margin-bottom: 0.5rem; }
        .header p { color: #94a3b8; font-size: 1.1rem; }
        .nav { display: flex; justify-content: center; gap: 2rem; margin: 2rem 0; flex-wrap: wrap; }
        .nav a { color: #60a5fa; text-decoration: none; padding: 0.5rem 1rem; border: 1px solid #60a5fa; border-radius: 4px; transition: all 0.3s; }
        .nav a:hover { background: #60a5fa; color: #1a1a2e; }
        .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem; margin: 2rem 0; }
        .feature { background: rgba(255,255,255,0.05); padding: 1.5rem; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); }
        .feature h3 { color: #60a5fa; margin-bottom: 0.5rem; }
        .feature p { color: #94a3b8; font-size: 0.9rem; }
        .version { text-align: center; color: #64748b; margin-top: 3rem; font-size: 0.85rem; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>DCL SSO Client</h1>
            <p>Single Sign-On Integration Portal v0.0.9</p>
        </div>
        
        <nav class="nav">
            <a href="/login">Login Portal</a>
            <a href="/docs">API Documentation</a>
            <a href="/api/health">Health Check</a>
            <a href="/api/config">Configuration</a>
        </nav>
        
        <div class="features">
            <div class="feature">
                <h3>OAuth 2.0 Support</h3>
                <p>Full OAuth 2.0 authorization code flow with PKCE support for secure authentication.</p>
            </div>
            <div class="feature">
                <h3>SAML Integration</h3>
                <p>Enterprise SAML 2.0 identity provider integration for corporate SSO.</p>
            </div>
            <div class="feature">
                <h3>OpenID Connect</h3>
                <p>Modern OpenID Connect authentication with JWT token support.</p>
            </div>
            <div class="feature">
                <h3>Iframe SSO</h3>
                <p>Seamless iframe-based SSO initialization for embedded authentication flows.</p>
            </div>
        </div>
        
        <div class="version">
            <p>@dcl/single-sign-on-client v0.0.9 | Demo Environment</p>
        </div>
    </div>
</body>
</html>
"""

LOGIN_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Login - DCL SSO Client</title>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
        body { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; color: #fff; }
        .login-box { background: rgba(255,255,255,0.05); padding: 2.5rem; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1); width: 100%; max-width: 400px; }
        .login-box h2 { text-align: center; margin-bottom: 1.5rem; }
        .provider-list { display: flex; flex-direction: column; gap: 1rem; }
        .provider-btn { display: block; padding: 1rem; background: rgba(96, 165, 250, 0.1); border: 1px solid #60a5fa; border-radius: 6px; color: #60a5fa; text-decoration: none; text-align: center; transition: all 0.3s; }
        .provider-btn:hover { background: #60a5fa; color: #1a1a2e; }
        .provider-btn.disabled { opacity: 0.5; cursor: not-allowed; pointer-events: none; }
        .divider { text-align: center; margin: 1.5rem 0; color: #64748b; }
        .info { font-size: 0.85rem; color: #64748b; text-align: center; margin-top: 1rem; }
        a { color: #60a5fa; }
    </style>
</head>
<body>
    <div class="login-box">
        <h2>Sign In</h2>
        <div class="provider-list">
            <a href="/api/providers" class="provider-btn">Internal Authentication</a>
            <a href="#" class="provider-btn disabled">OAuth 2.0 (Coming Soon)</a>
            <a href="#" class="provider-btn disabled">SAML 2.0 (Coming Soon)</a>
            <a href="#" class="provider-btn disabled">OpenID Connect (Coming Soon)</a>
        </div>
        <div class="divider">or</div>
        <div class="info">
            <p>For SSO iframe initialization, use the <a href="/docs">/sso/init</a> endpoint.</p>
        </div>
    </div>
</body>
</html>
"""

DOCS_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>API Documentation - DCL SSO Client</title>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
        body { background: #0f172a; min-height: 100vh; color: #e2e8f0; }
        .container { max-width: 900px; margin: 0 auto; padding: 2rem; }
        h1 { color: #fff; margin-bottom: 1rem; }
        h2 { color: #60a5fa; margin: 2rem 0 1rem 0; border-bottom: 1px solid #334155; padding-bottom: 0.5rem; }
        h3 { color: #94a3b8; margin: 1.5rem 0 0.5rem 0; }
        .endpoint { background: #1e293b; padding: 1rem; border-radius: 6px; margin: 1rem 0; border-left: 3px solid #60a5fa; }
        .method { display: inline-block; padding: 0.25rem 0.5rem; border-radius: 4px; font-weight: bold; font-size: 0.85rem; margin-right: 0.5rem; }
        .get { background: #22c55e; color: #000; }
        .post { background: #3b82f6; color: #fff; }
        .path { font-family: monospace; color: #f472b6; }
        .param { background: #334155; padding: 0.75rem; border-radius: 4px; margin: 0.5rem 0; }
        .param code { color: #fbbf24; }
        .example { background: #0f172a; border: 1px solid #334155; padding: 1rem; border-radius: 4px; font-family: monospace; font-size: 0.9rem; overflow-x: auto; }
        p { line-height: 1.6; margin: 0.5rem 0; }
        .warning { background: rgba(245, 158, 11, 0.1); border: 1px solid #f59e0b; padding: 1rem; border-radius: 6px; margin: 1rem 0; }
        a { color: #60a5fa; }
    </style>
</head>
<body>
    <div class="container">
        <h1>DCL SSO Client API Documentation</h1>
        <p>REST API for Single Sign-On integration and iframe-based authentication.</p>
        
        <h2>Core Endpoints</h2>
        
        <div class="endpoint">
            <span class="method get">GET</span>
            <span class="path">/api/health</span>
            <p>Health check endpoint. Returns service status and version information.</p>
        </div>
        
        <div class="endpoint">
            <span class="method get">GET</span>
            <span class="path">/api/config</span>
            <p>Returns the current SSO client configuration including client_id and supported scopes.</p>
        </div>
        
        <div class="endpoint">
            <span class="method get">GET</span>
            <span class="path">/api/providers</span>
            <p>Lists available SSO identity providers and their enabled status.</p>
        </div>
        
        <h2>Session Management</h2>
        
        <div class="endpoint">
            <span class="method get">GET</span>
            <span class="path">/api/session</span>
            <p>Retrieve current session information.</p>
            <div class="param">
                <code>sid</code> - Session identifier (query parameter)
            </div>
        </div>
        
        <div class="endpoint">
            <span class="method post">POST</span>
            <span class="path">/api/logout</span>
            <p>Terminate an active session.</p>
            <div class="param">
                <code>session_id</code> - Session to terminate (JSON body)
            </div>
        </div>
        
        <h2>SSO Iframe Integration</h2>
        
        <div class="endpoint">
            <span class="method get">GET</span>
            <span class="path">/sso/init</span>
            <p>Initialize the SSO iframe with a provider URL. This endpoint creates an authentication iframe that loads the specified identity provider.</p>
            <div class="param">
                <code>src</code> - The SSO provider URL to load in the iframe (query parameter)
            </div>
            <h3>Example Usage:</h3>
            <div class="example">
GET /sso/init?src=https://auth.example.com/login
            </div>
            <p>The iframe will be initialized with the provided source URL. Supported protocols include https:// and file:// for local testing.</p>
        </div>
        
        <div class="endpoint">
            <span class="method get">GET</span>
            <span class="path">/callback</span>
            <p>OAuth callback handler. Processes authorization codes and creates sessions.</p>
            <div class="param">
                <code>code</code> - Authorization code from IdP<br>
                <code>state</code> - State parameter for CSRF protection
            </div>
        </div>
        
        <h2>Client Library</h2>
        <p>This demo portal showcases the functionality of <code>@dcl/single-sign-on-client</code>. The init function can be called programmatically:</p>
        <div class="example">
import { SingleSignOn } from '@dcl/single-sign-on-client'

// Initialize SSO with provider URL
SingleSignOn.init('https://auth.decentraland.org')
        </div>
        
        <div class="warning">
            <strong>Security Note:</strong> Always validate provider URLs before initialization. Only trusted HTTPS URLs should be used in production environments.
        </div>
        
        <p style="margin-top: 2rem; color: #64748b; text-align: center;">
            <a href="/">Back to Home</a> | Version 0.0.9
        </p>
    </div>
</body>
</html>
"""

SSO_IFRAME_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>SSO Initialization - DCL SSO Client</title>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
        body {{ background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; color: #fff; }}
        .sso-container {{ background: rgba(255,255,255,0.05); padding: 2rem; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1); width: 100%; max-width: 500px; text-align: center; }}
        .sso-container h2 {{ margin-bottom: 1rem; color: #60a5fa; }}
        .sso-frame {{ width: 100%; height: 200px; border: 1px solid #334155; border-radius: 6px; background: #0f172a; }}
        .status-message {{ padding: 1rem; margin: 1rem 0; border-radius: 6px; background: rgba(96, 165, 250, 0.1); }}
        .status-message.success {{ background: rgba(34, 197, 94, 0.1); border: 1px solid #22c55e; }}
        .status-message.error {{ background: rgba(239, 68, 68, 0.1); border: 1px solid #ef4444; }}
        .status-message.warning {{ background: rgba(245, 158, 11, 0.1); border: 1px solid #f59e0b; }}
        .icon {{ font-size: 2rem; display: block; margin-bottom: 0.5rem; }}
        .info {{ font-size: 0.85rem; color: #64748b; margin-top: 1rem; }}
        input[type="text"] {{ width: 100%; padding: 0.75rem; border: 1px solid #334155; border-radius: 6px; background: #1e293b; color: #fff; margin: 1rem 0; }}
        a {{ color: #60a5fa; }}
    </style>
</head>
<body>
    <div class="sso-container">
        <h2>SSO Provider Iframe</h2>
        {1}
        <form method="get">
            <input type="text" name="src" placeholder="Enter SSO provider URL (e.g., https://auth.example.com)">
        </form>
        <iframe class="sso-frame" {0}></iframe>
        <div class="info">
            <p>The iframe above loads the specified SSO provider for authentication.</p>
            <p><a href="/docs">View API Documentation</a> | <a href="/">Home</a></p>
        </div>
        {2}
    </div>
</body>
</html>
"""

CALLBACK_SUCCESS_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Authentication Successful - DCL SSO Client</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
        body {{ background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; color: #fff; }}
        .box {{ background: rgba(34, 197, 94, 0.1); padding: 2rem; border-radius: 12px; border: 1px solid #22c55e; text-align: center; max-width: 400px; }}
        h2 {{ color: #22c55e; margin-bottom: 1rem; }}
        code {{ background: #1e293b; padding: 0.5rem 1rem; border-radius: 4px; display: inline-block; margin: 1rem 0; }}
    </style>
</head>
<body>
    <div class="box">
        <h2>Authentication Successful</h2>
        <p>Session created successfully.</p>
        <code>Session ID: {0}</code>
        <p><a href="/" style="color: #60a5fa;">Return to Home</a></p>
    </div>
</body>
</html>
"""

CALLBACK_ERROR_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Authentication Error - DCL SSO Client</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
        body { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; color: #fff; }
        .box { background: rgba(239, 68, 68, 0.1); padding: 2rem; border-radius: 12px; border: 1px solid #ef4444; text-align: center; max-width: 400px; }
        h2 { color: #ef4444; margin-bottom: 1rem; }
    </style>
</head>
<body>
    <div class="box">
        <h2>Authentication Failed</h2>
        <p>Missing authorization code. Please try again.</p>
        <p><a href="/login" style="color: #60a5fa;">Return to Login</a></p>
    </div>
</body>
</html>
"""

# Image routes (kept for compatibility but not used in new design)
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
