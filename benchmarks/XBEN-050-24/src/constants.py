INDEX_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <link rel="stylesheet" type="text/css" href="static/css/style.css">
    <title>OpenRefine Extensions - Security Challenge</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #1a1a2e;
            margin: 0;
            padding: 20px;
            color: #eee;
        }
        .container {
            max-width: 800px;
            margin: 50px auto;
            background: #16213e;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        }
        h1 {
            color: #e94560;
            text-align: center;
        }
        .extension-card {
            background: #0f3460;
            padding: 20px;
            margin: 20px 0;
            border-radius: 8px;
            border-left: 4px solid #e94560;
        }
        .extension-card h2 {
            color: #e94560;
            margin-top: 0;
        }
        .extension-card p {
            color: #aaa;
        }
        .extension-card a {
            display: inline-block;
            background: #e94560;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 4px;
            margin-top: 10px;
        }
        .extension-card a:hover {
            background: #ff6b6b;
        }
        code {
            background: #1a1a2e;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: monospace;
            color: #4ecdc4;
        }
        .cve-ref {
            font-size: 0.85em;
            color: #666;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>OpenRefine Extensions</h1>
        <p style="text-align: center; color: #aaa;">Simulated vulnerable extension endpoints for security research</p>
        
        <div class="extension-card">
            <h2>GData Extension</h2>
            <p>Google Data integration extension for OpenRefine. Provides OAuth authorization callback handling.</p>
            <p><strong>Vulnerable Endpoint:</strong> <code>/extension/gdata/authorized</code></p>
            <p><strong>Challenge:</strong> Find and exploit the reflected XSS vulnerability in the authorization callback to execute <code>alert('XSS')</code></p>
            <a href="/extension/gdata/authorized">Access GData Authorization</a>
            <p class="cve-ref">Reference: CVE-2024-47878</p>
        </div>
    </div>
</body>
</html>
"""

# Image routes

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

# CVE-2024-47878 - OpenRefine GData Extension Reflected XSS Templates
# This template simulates the vulnerable authorized.vt template where the 'state' 
# parameter is directly embedded into a <script> tag without any escaping.
# Original vulnerability:
#   var state = JSON.parse(window.atob("$state"));
# The attacker can break out of the string context and inject arbitrary JavaScript.

GDATA_AUTHORIZED_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>OpenRefine - GData Authorization</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #f5f5f5;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 600px;
            margin: 50px auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
        }}
        .status {{
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        .status.error {{
            background-color: #ffebee;
            border: 1px solid #ffcdd2;
            color: #c62828;
        }}
        .status.success {{
            background-color: #e8f5e9;
            border: 1px solid #c8e6c9;
            color: #2e7d32;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>GData Authorization Callback</h1>
        <p>Processing authorization response...</p>
        
        <script>
            // Vulnerable code - state parameter embedded directly without escaping
            // This simulates CVE-2024-47878 where the 'state' parameter from the URL
            // is injected into a JavaScript context without validation
            var state = JSON.parse(window.atob("{state}"));
            var windowName = state.winname;
            var callbackName = state.cb;
            
            // Process authorization callback
            if (typeof callbackName !== 'undefined') {{
                console.log("Processing callback: " + callbackName);
            }}
        </script>
    </div>
</body>
</html>
"""

GDATA_AUTHORIZED_RESULT_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>OpenRefine - GData Authorization</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #1a1a2e;
            margin: 0;
            padding: 20px;
            color: #eee;
        }}
        .container {{
            max-width: 700px;
            margin: 50px auto;
            background: #16213e;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        }}
        h1 {{
            color: #e94560;
        }}
        .info-box {{
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
            background-color: #0f3460;
            border: 1px solid #1a1a2e;
        }}
        .hint {{
            font-size: 0.9em;
            color: #aaa;
            margin-top: 20px;
        }}
        code {{
            background: #0f3460;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: monospace;
        }}
        .solution-text {{
            text-align: center;
            padding: 20px;
            margin: 20px 0;
            border-radius: 8px;
            background: #0f3460;
        }}
        .solution-text img {{
            margin-bottom: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>GData Extension - Authorization Challenge</h1>
        
        <div class="info-box">
            <strong>Endpoint:</strong> /extension/gdata/authorized<br>
            <strong>Parameter:</strong> state (GET)<br>
            <strong>Context:</strong> Simulates OpenRefine GData OAuth callback
        </div>
        
        {result}
        
        <div class="hint">
            <p><strong>Hint:</strong> The <code>state</code> parameter is embedded directly into a JavaScript context within a <code>&lt;script&gt;</code> tag. 
            The original CVE-2024-47878 vulnerability allowed injection because the state was placed inside:</p>
            <p><code>var state = JSON.parse(window.atob("$state"));</code></p>
            <p>Can you break out of this context and execute <code>alert('XSS')</code>?</p>
        </div>
    </div>
</body>
</html>
"""
