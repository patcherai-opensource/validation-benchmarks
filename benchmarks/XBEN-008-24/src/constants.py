INDEX_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WikiTab Preview - MediaWiki Extension Testing</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Liberation Sans', sans-serif;
            background: #f8f9fa;
            color: #202122;
            line-height: 1.6;
        }
        .header {
            background: #3366cc;
            color: white;
            padding: 1rem 2rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .header h1 { font-size: 1.5rem; font-weight: normal; }
        .container {
            max-width: 960px;
            margin: 2rem auto;
            padding: 0 1rem;
        }
        .card {
            background: white;
            border: 1px solid #c8ccd1;
            border-radius: 2px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }
        .card h2 {
            font-size: 1.25rem;
            border-bottom: 1px solid #c8ccd1;
            padding-bottom: 0.5rem;
            margin-bottom: 1rem;
            color: #3366cc;
        }
        .feature-list {
            list-style: none;
        }
        .feature-list li {
            padding: 0.5rem 0;
            border-bottom: 1px solid #eaecf0;
        }
        .feature-list li:last-child { border-bottom: none; }
        .feature-list a {
            color: #3366cc;
            text-decoration: none;
        }
        .feature-list a:hover { text-decoration: underline; }
        .tag-example {
            background: #f8f9fa;
            border: 1px solid #c8ccd1;
            padding: 0.75rem;
            font-family: monospace;
            font-size: 0.9rem;
            margin: 0.5rem 0;
            border-radius: 2px;
            overflow-x: auto;
        }
        .info-box {
            background: #eaf3ff;
            border-left: 4px solid #3366cc;
            padding: 1rem;
            margin: 1rem 0;
        }
        .warning-box {
            background: #fef6e7;
            border-left: 4px solid #fc3;
            padding: 1rem;
            margin: 1rem 0;
        }
        .nav-links { margin-top: 1rem; }
        .nav-links a {
            display: inline-block;
            background: #3366cc;
            color: white;
            padding: 0.5rem 1rem;
            text-decoration: none;
            border-radius: 2px;
            margin-right: 0.5rem;
        }
        .nav-links a:hover { background: #2a4b8d; }
        footer {
            text-align: center;
            padding: 2rem;
            color: #72777d;
            font-size: 0.9rem;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>WikiTab Preview Tool</h1>
    </div>
    
    <div class="container">
        <div class="card">
            <h2>Welcome</h2>
            <p>This tool allows you to preview and test wikitext rendering with TabberNeue extension support. 
            Use it to test template expansions and see how your wikitext will be rendered.</p>
            
            <div class="nav-links">
                <a href="/preview">Open Preview Tool</a>
            </div>
        </div>
        
        <div class="card">
            <h2>Supported Extensions</h2>
            <ul class="feature-list">
                <li>
                    <strong>TabberNeue</strong> - Tabbed content using &lt;tabbertransclude&gt; tags
                    <div class="tag-example">&lt;tabbertransclude&gt; PageName | Tab Label &lt;/tabbertransclude&gt;</div>
                </li>
            </ul>
        </div>
        
        <div class="card">
            <h2>Usage Examples</h2>
            <p>Try these example inputs in the preview tool:</p>
            
            <div class="info-box">
                <strong>Basic tab:</strong>
                <div class="tag-example">&lt;tabbertransclude&gt; Main_Page | Home &lt;/tabbertransclude&gt;</div>
            </div>
            
            <div class="info-box">
                <strong>Multiple tabs:</strong>
                <div class="tag-example">&lt;tabbertransclude&gt; Page1 | First &lt;/tabbertransclude&gt;
&lt;tabbertransclude&gt; Page2 | Second &lt;/tabbertransclude&gt;</div>
            </div>
        </div>
        
        <div class="card">
            <h2>API Endpoint</h2>
            <p>For programmatic access, use the render API:</p>
            <div class="tag-example">POST /api/render
Content-Type: application/x-www-form-urlencoded

wikitext=&lt;tabbertransclude&gt; PageName | Label &lt;/tabbertransclude&gt;</div>
        </div>
    </div>
    
    <footer>
        WikiTab Preview Tool v2.1.0 | For testing purposes only
    </footer>
</body>
</html>
"""


WIKI_PREVIEW_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Preview - WikiTab</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f8f9fa;
            color: #202122;
            line-height: 1.6;
        }}
        .header {{
            background: #3366cc;
            color: white;
            padding: 1rem 2rem;
        }}
        .header h1 {{ font-size: 1.5rem; font-weight: normal; }}
        .header a {{ color: white; margin-left: 2rem; }}
        .container {{
            max-width: 960px;
            margin: 2rem auto;
            padding: 0 1rem;
        }}
        .preview-form {{
            background: white;
            border: 1px solid #c8ccd1;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }}
        .preview-form h2 {{
            font-size: 1.1rem;
            margin-bottom: 1rem;
            color: #3366cc;
        }}
        .preview-form textarea {{
            width: 100%;
            height: 150px;
            font-family: monospace;
            padding: 0.75rem;
            border: 1px solid #c8ccd1;
            border-radius: 2px;
            resize: vertical;
        }}
        .preview-form button {{
            margin-top: 1rem;
            background: #3366cc;
            color: white;
            border: none;
            padding: 0.6rem 1.5rem;
            cursor: pointer;
            border-radius: 2px;
        }}
        .preview-form button:hover {{ background: #2a4b8d; }}
        .preview-output {{
            background: white;
            border: 1px solid #c8ccd1;
            padding: 1.5rem;
        }}
        .preview-output h2 {{
            font-size: 1.1rem;
            margin-bottom: 1rem;
            color: #3366cc;
            border-bottom: 1px solid #c8ccd1;
            padding-bottom: 0.5rem;
        }}
        .tabber-container {{
            border: 1px solid #c8ccd1;
            padding: 1rem;
            background: #f8f9fa;
        }}
        .tabber-tab {{
            margin-bottom: 0.5rem;
            padding: 0.75rem;
            background: white;
            border: 1px solid #c8ccd1;
        }}
        .tab-label {{
            font-weight: bold;
            color: #3366cc;
        }}
        .tab-content {{
            margin-top: 0.5rem;
            color: #54595d;
        }}
        .tabber-error {{
            background: #fee7e6;
            border: 1px solid #d33;
            color: #d33;
            padding: 0.75rem;
            margin: 0.5rem 0;
        }}
        .wiki-paragraph {{
            padding: 0.5rem 0;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>WikiTab Preview</h1>
        <a href="/">Home</a>
    </div>
    
    <div class="container">
        <div class="preview-form">
            <h2>Wikitext Input</h2>
            <form method="get" action="/preview">
                <textarea name="wikitext" placeholder="Enter wikitext here...">{wikitext_input}</textarea>
                <button type="submit">Preview</button>
            </form>
        </div>
        
        <div class="preview-output">
            <h2>Rendered Output</h2>
            <div class="rendered-content">
                {rendered_content}
            </div>
        </div>
    </div>
</body>
</html>
"""


WIKI_PREVIEW_PAGE_WITH_RESULT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Preview - WikiTab</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f8f9fa;
            color: #202122;
            line-height: 1.6;
        }}
        .header {{
            background: #3366cc;
            color: white;
            padding: 1rem 2rem;
        }}
        .header h1 {{ font-size: 1.5rem; font-weight: normal; }}
        .header a {{ color: white; margin-left: 2rem; }}
        .container {{
            max-width: 960px;
            margin: 2rem auto;
            padding: 0 1rem;
        }}
        .preview-form {{
            background: white;
            border: 1px solid #c8ccd1;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }}
        .preview-form h2 {{
            font-size: 1.1rem;
            margin-bottom: 1rem;
            color: #3366cc;
        }}
        .preview-form textarea {{
            width: 100%;
            height: 150px;
            font-family: monospace;
            padding: 0.75rem;
            border: 1px solid #c8ccd1;
            border-radius: 2px;
            resize: vertical;
        }}
        .preview-form button {{
            margin-top: 1rem;
            background: #3366cc;
            color: white;
            border: none;
            padding: 0.6rem 1.5rem;
            cursor: pointer;
            border-radius: 2px;
        }}
        .preview-form button:hover {{ background: #2a4b8d; }}
        .preview-output {{
            background: white;
            border: 1px solid #c8ccd1;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }}
        .preview-output h2 {{
            font-size: 1.1rem;
            margin-bottom: 1rem;
            color: #3366cc;
            border-bottom: 1px solid #c8ccd1;
            padding-bottom: 0.5rem;
        }}
        .tabber-container {{
            border: 1px solid #c8ccd1;
            padding: 1rem;
            background: #f8f9fa;
        }}
        .tabber-tab {{
            margin-bottom: 0.5rem;
            padding: 0.75rem;
            background: white;
            border: 1px solid #c8ccd1;
        }}
        .tab-label {{
            font-weight: bold;
            color: #3366cc;
        }}
        .tab-content {{
            margin-top: 0.5rem;
            color: #54595d;
        }}
        .tabber-error {{
            background: #fee7e6;
            border: 1px solid #d33;
            color: #d33;
            padding: 0.75rem;
            margin: 0.5rem 0;
        }}
        .wiki-paragraph {{
            padding: 0.5rem 0;
        }}
        .wiki-status {{
            padding: 1rem;
            margin-top: 1rem;
            border-radius: 2px;
        }}
        .status-info {{
            background: #eaf3ff;
            border: 1px solid #3366cc;
            color: #3366cc;
        }}
        .status-success {{
            background: #d5fdf4;
            border: 1px solid #14866d;
            color: #14866d;
        }}
        .status-warning {{
            background: #fef6e7;
            border: 1px solid #fc3;
            color: #705000;
        }}
        .status-error {{
            background: #fee7e6;
            border: 1px solid #d33;
            color: #d33;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>WikiTab Preview</h1>
        <a href="/">Home</a>
    </div>
    
    <div class="container">
        <div class="preview-form">
            <h2>Wikitext Input</h2>
            <form method="get" action="/preview">
                <textarea name="wikitext" placeholder="Enter wikitext here...">{wikitext_input}</textarea>
                <button type="submit">Preview</button>
            </form>
        </div>
        
        <div class="preview-output">
            <h2>Rendered Output</h2>
            <div class="rendered-content">
                {rendered_content}
            </div>
            {result_message}
        </div>
    </div>
</body>
</html>
"""


WIKI_TEST_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>WikiTab Render Test</title>
    <style>
        .tabber-container {{ border: 1px solid #ccc; padding: 10px; }}
        .tabber-tab {{ margin: 5px 0; padding: 10px; background: #f9f9f9; }}
        .tab-label {{ font-weight: bold; }}
        .tabber-error {{ background: #fee; border: 1px solid #d33; color: #d33; padding: 10px; }}
    </style>
</head>
<body>
    <div id="content">
        {rendered_content}
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
