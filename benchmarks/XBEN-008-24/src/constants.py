INDEX_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WikiTab - Collaborative Wiki Platform</title>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .header { background: rgba(255,255,255,0.95); padding: 15px 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header-content { max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 24px; font-weight: bold; color: #667eea; text-decoration: none; }
        .nav-links a { margin-left: 25px; color: #555; text-decoration: none; font-size: 14px; }
        .nav-links a:hover { color: #667eea; }
        .main { max-width: 1200px; margin: 40px auto; padding: 0 20px; }
        .hero { background: white; border-radius: 12px; padding: 50px; text-align: center; margin-bottom: 30px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }
        .hero h1 { font-size: 36px; color: #333; margin-bottom: 15px; }
        .hero p { color: #666; font-size: 18px; margin-bottom: 30px; }
        .btn { display: inline-block; padding: 12px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 6px; font-weight: 500; transition: all 0.3s; }
        .btn:hover { background: #5a6fd6; transform: translateY(-2px); }
        .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 25px; margin-top: 30px; }
        .feature-card { background: white; border-radius: 10px; padding: 30px; box-shadow: 0 4px 15px rgba(0,0,0,0.08); }
        .feature-card h3 { color: #333; margin-bottom: 10px; }
        .feature-card p { color: #666; font-size: 14px; line-height: 1.6; }
        .footer { text-align: center; padding: 30px; color: rgba(255,255,255,0.8); font-size: 14px; }
    </style>
</head>
<body>
    <header class="header">
        <div class="header-content">
            <a href="/" class="logo">WikiTab</a>
            <nav class="nav-links">
                <a href="/wiki/preview">Editor</a>
                <a href="/wiki/help">Documentation</a>
            </nav>
        </div>
    </header>
    <main class="main">
        <section class="hero">
            <h1>Welcome to WikiTab</h1>
            <p>A powerful wiki platform with advanced tab and content transclusion features</p>
            <a href="/wiki/preview" class="btn">Open Editor</a>
        </section>
        <div class="features">
            <div class="feature-card">
                <h3>Rich Markup Support</h3>
                <p>Use our extended wiki markup syntax to create dynamic content with tabs, transclusions, and more.</p>
            </div>
            <div class="feature-card">
                <h3>Tab Transclusion</h3>
                <p>Embed content from other pages using the tabbertransclude tag for organized, tabbed displays.</p>
            </div>
            <div class="feature-card">
                <h3>Live Preview</h3>
                <p>See your changes in real-time with our instant preview system.</p>
            </div>
        </div>
    </main>
    <footer class="footer">
        <p>WikiTab Platform v2.3.1</p>
    </footer>
</body>
</html>
"""


WIKI_EDITOR_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WikiTab Editor - Preview</title>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f6fa; min-height: 100vh; }}
        .header {{ background: white; padding: 15px 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header-content {{ max-width: 1400px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; }}
        .logo {{ font-size: 24px; font-weight: bold; color: #667eea; text-decoration: none; }}
        .nav-links a {{ margin-left: 25px; color: #555; text-decoration: none; font-size: 14px; }}
        .nav-links a:hover {{ color: #667eea; }}
        .main {{ max-width: 1400px; margin: 30px auto; padding: 0 20px; }}
        .editor-container {{ display: grid; grid-template-columns: 1fr 1fr; gap: 25px; }}
        .panel {{ background: white; border-radius: 10px; box-shadow: 0 2px 15px rgba(0,0,0,0.08); overflow: hidden; }}
        .panel-header {{ background: #667eea; color: white; padding: 15px 20px; font-weight: 600; }}
        .panel-body {{ padding: 20px; }}
        textarea {{ width: 100%; height: 300px; border: 1px solid #ddd; border-radius: 6px; padding: 15px; font-family: 'Monaco', 'Consolas', monospace; font-size: 14px; resize: vertical; }}
        textarea:focus {{ outline: none; border-color: #667eea; }}
        .btn {{ display: inline-block; padding: 12px 30px; background: #667eea; color: white; border: none; border-radius: 6px; font-weight: 500; cursor: pointer; font-size: 14px; }}
        .btn:hover {{ background: #5a6fd6; }}
        .preview-content {{ min-height: 300px; padding: 15px; border: 1px solid #eee; border-radius: 6px; background: #fafafa; }}
        .tabber-container {{ border: 1px solid #ddd; border-radius: 6px; margin: 10px 0; }}
        .tabber-tab {{ padding: 15px; border-bottom: 1px solid #eee; }}
        .tabber-tab:last-child {{ border-bottom: none; }}
        .tabber-error {{ color: #c0392b; background: #fdedec; padding: 10px 15px; border-radius: 4px; margin: 10px 0; border-left: 4px solid #c0392b; }}
        .tab-content {{ color: #666; }}
        .wiki-success {{ background: #d4edda; color: #155724; padding: 15px; border-radius: 6px; margin-top: 15px; border: 1px solid #c3e6cb; font-family: monospace; }}
        .help-text {{ font-size: 12px; color: #888; margin-top: 10px; }}
        .form-actions {{ margin-top: 15px; }}
    </style>
</head>
<body>
    <header class="header">
        <div class="header-content">
            <a href="/" class="logo">WikiTab</a>
            <nav class="nav-links">
                <a href="/wiki/preview">Editor</a>
                <a href="/wiki/help">Documentation</a>
            </nav>
        </div>
    </header>
    <main class="main">
        <div class="editor-container">
            <div class="panel">
                <div class="panel-header">Wiki Markup Editor</div>
                <div class="panel-body">
                    <form method="POST" action="/wiki/preview">
                        <textarea name="content" placeholder="Enter your wiki markup here...">{0}</textarea>
                        <p class="help-text">Use &lt;tabbertransclude&gt;PageName | AnotherPage&lt;/tabbertransclude&gt; to create tabbed content.</p>
                        <div class="form-actions">
                            <button type="submit" class="btn">Preview</button>
                        </div>
                    </form>
                </div>
            </div>
            <div class="panel">
                <div class="panel-header">Preview Output</div>
                <div class="panel-body">
                    <div class="preview-content">{1}</div>
                    {2}
                </div>
            </div>
        </div>
    </main>
</body>
</html>
"""


WIKI_PREVIEW_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Preview</title>
    <style>
        .tabber-container {{ border: 1px solid #ddd; border-radius: 6px; margin: 10px 0; }}
        .tabber-tab {{ padding: 15px; border-bottom: 1px solid #eee; }}
        .tabber-tab:last-child {{ border-bottom: none; }}
        .tabber-error {{ color: #c0392b; background: #fdedec; padding: 10px 15px; border-radius: 4px; margin: 10px 0; }}
        .tab-content {{ color: #666; }}
    </style>
</head>
<body>
{0}
</body>
</html>
"""


WIKI_HELP_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WikiTab Documentation</title>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f6fa; min-height: 100vh; }
        .header { background: white; padding: 15px 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header-content { max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 24px; font-weight: bold; color: #667eea; text-decoration: none; }
        .nav-links a { margin-left: 25px; color: #555; text-decoration: none; font-size: 14px; }
        .nav-links a:hover { color: #667eea; }
        .main { max-width: 900px; margin: 40px auto; padding: 0 20px; }
        .doc-section { background: white; border-radius: 10px; padding: 30px; margin-bottom: 25px; box-shadow: 0 2px 15px rgba(0,0,0,0.08); }
        .doc-section h2 { color: #333; margin-bottom: 20px; border-bottom: 2px solid #667eea; padding-bottom: 10px; }
        .doc-section h3 { color: #555; margin: 20px 0 10px; }
        .doc-section p { color: #666; line-height: 1.8; margin-bottom: 15px; }
        .doc-section code { background: #f0f0f0; padding: 2px 8px; border-radius: 4px; font-family: 'Monaco', 'Consolas', monospace; font-size: 13px; }
        .code-block { background: #2d3436; color: #dfe6e9; padding: 20px; border-radius: 8px; font-family: 'Monaco', 'Consolas', monospace; font-size: 13px; overflow-x: auto; margin: 15px 0; }
        .example { background: #f8f9fa; border-left: 4px solid #667eea; padding: 15px 20px; margin: 15px 0; border-radius: 0 8px 8px 0; }
        .note { background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px 20px; margin: 15px 0; border-radius: 0 8px 8px 0; }
        .note strong { color: #856404; }
    </style>
</head>
<body>
    <header class="header">
        <div class="header-content">
            <a href="/" class="logo">WikiTab</a>
            <nav class="nav-links">
                <a href="/wiki/preview">Editor</a>
                <a href="/wiki/help">Documentation</a>
            </nav>
        </div>
    </header>
    <main class="main">
        <div class="doc-section">
            <h2>TabberTransclude Tag</h2>
            <p>The <code>&lt;tabbertransclude&gt;</code> tag allows you to embed content from other wiki pages in a tabbed format. This is useful for organizing related content that spans multiple pages.</p>
            
            <h3>Basic Syntax</h3>
            <div class="code-block">&lt;tabbertransclude&gt;PageName | AnotherPage | ThirdPage&lt;/tabbertransclude&gt;</div>
            
            <h3>How It Works</h3>
            <p>The tag parser splits the content by the pipe character (<code>|</code>) and treats each segment as a page name to transclude. The content from each page is then displayed in a tabbed interface.</p>
            
            <div class="example">
                <strong>Example:</strong><br>
                <code>&lt;tabbertransclude&gt;Introduction | Getting Started | Advanced Topics&lt;/tabbertransclude&gt;</code><br><br>
                This creates three tabs containing content from the Introduction, Getting Started, and Advanced Topics pages.
            </div>
            
            <h3>Page Name Validation</h3>
            <p>Page names must follow standard wiki naming conventions:</p>
            <ul style="margin-left: 20px; color: #666; line-height: 2;">
                <li>Must not be empty</li>
                <li>Cannot contain special characters: <code>&lt; &gt; [ ] { } | #</code></li>
                <li>Maximum length: 255 characters</li>
            </ul>
            
            <div class="note">
                <strong>Note:</strong> If a page name is invalid, an error message will be displayed in place of the tab content, showing the problematic page name.
            </div>
        </div>
        
        <div class="doc-section">
            <h2>Single Page Transclusion</h2>
            <p>You can also transclude a single page without the pipe separator:</p>
            <div class="code-block">&lt;tabbertransclude&gt;MainPage&lt;/tabbertransclude&gt;</div>
        </div>
        
        <div class="doc-section">
            <h2>API Usage</h2>
            <p>The preview endpoint accepts both GET and POST requests:</p>
            <div class="code-block">GET /wiki/preview?content=&lt;tabbertransclude&gt;Page1&lt;/tabbertransclude&gt;
POST /wiki/preview (content in form body)</div>
        </div>
    </main>
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
    },
    "wiki": {
        "start": "static/img/cookies/new_star.png",
        "process": "static/img/cookies/error_star.png",
        "error": "static/img/cookies/error_star.png",
        "success": "static/img/cookies/success_star.png"
    }
}
