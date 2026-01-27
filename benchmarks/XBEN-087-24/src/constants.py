INDEX_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Angular SSR Preview Tool</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            color: #e0e0e0;
        }
        .container {
            max-width: 800px;
            padding: 40px;
            text-align: center;
        }
        h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(90deg, #dd1144, #ff6b6b);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .subtitle {
            color: #888;
            margin-bottom: 30px;
            font-size: 1.1em;
        }
        .feature-box {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 30px;
            margin: 20px 0;
        }
        .feature-box h2 {
            color: #ff6b6b;
            margin-bottom: 15px;
        }
        .feature-box p {
            color: #aaa;
            line-height: 1.6;
        }
        .btn {
            display: inline-block;
            background: linear-gradient(90deg, #dd1144, #ff6b6b);
            color: white;
            padding: 15px 40px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            margin-top: 20px;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(221, 17, 68, 0.3);
        }
        .version {
            color: #666;
            margin-top: 30px;
            font-size: 0.9em;
        }
        .warning-banner {
            background: rgba(255, 193, 7, 0.1);
            border: 1px solid rgba(255, 193, 7, 0.3);
            border-radius: 8px;
            padding: 15px;
            margin: 20px 0;
            color: #ffc107;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Angular Universal SSR Preview</h1>
        <p class="subtitle">Critical CSS Inlining Tool - Development Preview</p>
        
        <div class="warning-banner">
            <strong>Development Build</strong> - This preview tool demonstrates server-side rendering with critical CSS inlining.
        </div>
        
        <div class="feature-box">
            <h2>Critical CSS Inliner</h2>
            <p>Preview how your stylesheets will be inlined during server-side rendering. 
            This tool simulates the critters CSS inlining process used by Angular Universal 
            to optimize above-the-fold content loading.</p>
            <a href="/preview" class="btn">Open CSS Preview Tool</a>
        </div>
        
        <p class="version">Angular Universal Preview v16.1.1 | critters v0.0.19</p>
    </div>
</body>
</html>
"""


SSR_PREVIEW_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Critical CSS Inliner - Angular Universal</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            padding: 40px;
            color: #e0e0e0;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .header h1 {{
            font-size: 2em;
            background: linear-gradient(90deg, #dd1144, #ff6b6b);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .header p {{
            color: #888;
            margin-top: 10px;
        }}
        .main-panel {{
            max-width: 900px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 30px;
        }}
        .input-section {{
            margin-bottom: 25px;
        }}
        .input-section label {{
            display: block;
            color: #aaa;
            margin-bottom: 10px;
            font-weight: 500;
        }}
        .input-section input {{
            width: 100%;
            padding: 15px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            background: rgba(0, 0, 0, 0.3);
            color: #fff;
            font-size: 1em;
        }}
        .input-section input:focus {{
            outline: none;
            border-color: #dd1144;
        }}
        .btn {{
            background: linear-gradient(90deg, #dd1144, #ff6b6b);
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            font-size: 1em;
        }}
        .result-panel {{
            margin: 20px 0;
            padding: 20px;
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.05);
        }}
        .result-panel.success {{
            background: rgba(40, 167, 69, 0.2);
            border: 1px solid rgba(40, 167, 69, 0.5);
        }}
        .result-panel.error {{
            background: rgba(220, 53, 69, 0.2);
            border: 1px solid rgba(220, 53, 69, 0.5);
        }}
        .result-panel.warning {{
            background: rgba(255, 193, 7, 0.2);
            border: 1px solid rgba(255, 193, 7, 0.5);
        }}
        .status-message {{
            font-weight: 500;
            margin-bottom: 10px;
        }}
        .flag-output {{
            font-family: monospace;
            background: rgba(0, 0, 0, 0.3);
            padding: 10px;
            border-radius: 4px;
            word-break: break-all;
        }}
        .hint {{
            color: #aaa;
            font-size: 0.9em;
        }}
        .preview-container {{
            margin-top: 20px;
        }}
        .preview-container h3 {{
            color: #ff6b6b;
            margin: 15px 0 10px;
            font-size: 1.1em;
        }}
        .code-block {{
            background: rgba(0, 0, 0, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 6px;
            padding: 15px;
            overflow-x: auto;
        }}
        .code-block pre {{
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 0.9em;
            color: #98c379;
            white-space: pre-wrap;
            word-break: break-all;
        }}
        .live-preview {{
            background: rgba(255, 255, 255, 0.03);
            border: 1px dashed rgba(255, 255, 255, 0.2);
            border-radius: 6px;
            padding: 20px;
        }}
        .live-preview p {{
            color: #aaa;
        }}
        .info-box {{
            background: rgba(0, 123, 255, 0.1);
            border: 1px solid rgba(0, 123, 255, 0.3);
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 20px;
            color: #6db3f2;
            font-size: 0.9em;
        }}
        .back-link {{
            display: inline-block;
            color: #888;
            text-decoration: none;
            margin-bottom: 20px;
        }}
        .back-link:hover {{
            color: #ff6b6b;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Critical CSS Inliner Preview</h1>
        <p>Test how stylesheets are processed during Angular Universal SSR</p>
    </div>
    
    <div class="main-panel">
        <a href="/" class="back-link">&larr; Back to Home</a>
        
        <div class="info-box">
            <strong>How it works:</strong> Enter a stylesheet URL and the tool will generate 
            the inlined CSS output as it would appear in server-side rendered HTML. 
            The critters library processes external stylesheets and inlines critical CSS 
            with appropriate onload handlers for deferred loading.
        </div>
        
        <form class="input-section" method="get" action="/preview">
            <label for="stylesheet">Stylesheet URL:</label>
            <input type="text" id="stylesheet" name="stylesheet" placeholder="https://example.com/styles.css" autocomplete="off">
            <br><br>
            <button type="submit" class="btn">Generate Inline CSS</button>
        </form>
        
        {result}
        
        {preview_area}
    </div>
</body>
</html>
"""


# Legacy constants kept for compatibility
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
