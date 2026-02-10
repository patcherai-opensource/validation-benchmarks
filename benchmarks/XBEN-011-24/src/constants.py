INDEX_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DataWiki - Enterprise Knowledge Platform</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 1rem 2rem; display: flex; align-items: center; justify-content: space-between; }
        .header h1 { font-size: 1.5rem; }
        .nav { display: flex; gap: 1rem; }
        .nav a { color: white; text-decoration: none; padding: 0.5rem 1rem; border-radius: 4px; }
        .nav a:hover { background: rgba(255,255,255,0.1); }
        .container { max-width: 1200px; margin: 2rem auto; padding: 0 1rem; }
        .hero { background: white; border-radius: 8px; padding: 3rem; text-align: center; margin-bottom: 2rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .hero h2 { font-size: 2rem; margin-bottom: 1rem; color: #2c3e50; }
        .hero p { color: #666; margin-bottom: 2rem; }
        .btn { display: inline-block; background: #3498db; color: white; padding: 0.75rem 1.5rem; border-radius: 4px; text-decoration: none; }
        .btn:hover { background: #2980b9; }
        .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; }
        .feature { background: white; border-radius: 8px; padding: 1.5rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .feature h3 { color: #2c3e50; margin-bottom: 0.5rem; }
        .feature p { color: #666; font-size: 0.9rem; }
        .footer { text-align: center; padding: 2rem; color: #666; font-size: 0.85rem; }
    </style>
</head>
<body>
    <div class="header">
        <h1>DataWiki</h1>
        <nav class="nav">
            <a href="/">Home</a>
            <a href="/wiki">Wiki</a>
            <a href="/wiki/help">Help</a>
        </nav>
    </div>
    <div class="container">
        <div class="hero">
            <h2>Welcome to DataWiki</h2>
            <p>Your enterprise knowledge management and documentation platform</p>
            <a href="/wiki" class="btn">Browse Wiki</a>
        </div>
        <div class="features">
            <div class="feature">
                <h3>Live Data Tables</h3>
                <p>Display and manage dynamic data with our powerful Live Data macro system.</p>
            </div>
            <div class="feature">
                <h3>Collaborative Editing</h3>
                <p>Work together with your team to create and maintain documentation.</p>
            </div>
            <div class="feature">
                <h3>Flexible Formatting</h3>
                <p>Support for multiple display formats including text, HTML, and links.</p>
            </div>
        </div>
    </div>
    <div class="footer">
        <p>&copy; 2024 DataWiki Enterprise Platform</p>
    </div>
</body>
</html>
"""

WIKI_HOME_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Wiki - DataWiki</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 1rem 2rem; display: flex; align-items: center; justify-content: space-between; }
        .header h1 { font-size: 1.5rem; }
        .nav { display: flex; gap: 1rem; }
        .nav a { color: white; text-decoration: none; padding: 0.5rem 1rem; border-radius: 4px; }
        .nav a:hover { background: rgba(255,255,255,0.1); }
        .container { max-width: 1200px; margin: 2rem auto; padding: 0 1rem; }
        .breadcrumb { margin-bottom: 1rem; color: #666; }
        .breadcrumb a { color: #3498db; text-decoration: none; }
        .content { background: white; border-radius: 8px; padding: 2rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .content h2 { color: #2c3e50; margin-bottom: 1rem; }
        .page-list { list-style: none; }
        .page-list li { padding: 0.75rem 0; border-bottom: 1px solid #eee; }
        .page-list a { color: #3498db; text-decoration: none; font-weight: 500; }
        .page-list a:hover { text-decoration: underline; }
        .page-list .desc { color: #666; font-size: 0.9rem; margin-top: 0.25rem; }
    </style>
</head>
<body>
    <div class="header">
        <h1>DataWiki</h1>
        <nav class="nav">
            <a href="/">Home</a>
            <a href="/wiki">Wiki</a>
            <a href="/wiki/help">Help</a>
        </nav>
    </div>
    <div class="container">
        <div class="breadcrumb">
            <a href="/">Home</a> &gt; Wiki
        </div>
        <div class="content">
            <h2>Wiki Pages</h2>
            <ul class="page-list">
                <li>
                    <a href="/wiki/livedata">Project Tracker (Live Data)</a>
                    <div class="desc">Dynamic project tracking table with configurable display options</div>
                </li>
                <li>
                    <a href="/wiki/help">Documentation &amp; Help</a>
                    <div class="desc">Learn how to use DataWiki and the Live Data macro</div>
                </li>
            </ul>
        </div>
    </div>
</body>
</html>
"""

LIVEDATA_VIEW_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Project Tracker - DataWiki</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }}
        .header {{ background: #2c3e50; color: white; padding: 1rem 2rem; display: flex; align-items: center; justify-content: space-between; }}
        .header h1 {{ font-size: 1.5rem; }}
        .nav {{ display: flex; gap: 1rem; }}
        .nav a {{ color: white; text-decoration: none; padding: 0.5rem 1rem; border-radius: 4px; }}
        .nav a:hover {{ background: rgba(255,255,255,0.1); }}
        .container {{ max-width: 1200px; margin: 2rem auto; padding: 0 1rem; }}
        .breadcrumb {{ margin-bottom: 1rem; color: #666; }}
        .breadcrumb a {{ color: #3498db; text-decoration: none; }}
        .content {{ background: white; border-radius: 8px; padding: 2rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .content h2 {{ color: #2c3e50; margin-bottom: 0.5rem; }}
        .page-info {{ color: #666; font-size: 0.9rem; margin-bottom: 1.5rem; }}
        .actions {{ margin-bottom: 1rem; }}
        .btn {{ display: inline-block; background: #3498db; color: white; padding: 0.5rem 1rem; border-radius: 4px; text-decoration: none; font-size: 0.9rem; }}
        .btn:hover {{ background: #2980b9; }}
        .btn-secondary {{ background: #95a5a6; }}
        .btn-secondary:hover {{ background: #7f8c8d; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; }}
        th, td {{ padding: 0.75rem; text-align: left; border-bottom: 1px solid #eee; }}
        th {{ background: #f8f9fa; font-weight: 600; color: #2c3e50; }}
        tr:hover {{ background: #f8f9fa; }}
        .html-wrapper {{ }}
        .alert {{ padding: 1rem; border-radius: 4px; margin-bottom: 1rem; }}
        .alert-success {{ background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
        .alert-error {{ background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }}
        .flag-container {{ background: #fff3cd; color: #856404; border: 1px solid #ffeeba; padding: 1rem; border-radius: 4px; margin-top: 1rem; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>DataWiki</h1>
        <nav class="nav">
            <a href="/">Home</a>
            <a href="/wiki">Wiki</a>
            <a href="/wiki/help">Help</a>
        </nav>
    </div>
    <div class="container">
        <div class="breadcrumb">
            <a href="/">Home</a> &gt; <a href="/wiki">Wiki</a> &gt; Project Tracker
        </div>
        <div class="content">
            <h2>Project Tracker</h2>
            <p class="page-info">A Live Data table displaying project information</p>
            {success_message}
            {error_message}
            <div class="actions">
                <a href="/wiki/livedata/edit" class="btn">Edit Configuration</a>
            </div>
            <table>
                <thead>
                    <tr>{headers}</tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
            <!-- FLAG_PLACEHOLDER -->
        </div>
    </div>
</body>
</html>
"""

LIVEDATA_TEST_PAGE = """
<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body>
<table>
<thead><tr>{headers}</tr></thead>
<tbody>{rows}</tbody>
</table>
</body>
</html>
"""

LIVEDATA_EDIT_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Edit Live Data - DataWiki</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }}
        .header {{ background: #2c3e50; color: white; padding: 1rem 2rem; display: flex; align-items: center; justify-content: space-between; }}
        .header h1 {{ font-size: 1.5rem; }}
        .nav {{ display: flex; gap: 1rem; }}
        .nav a {{ color: white; text-decoration: none; padding: 0.5rem 1rem; border-radius: 4px; }}
        .nav a:hover {{ background: rgba(255,255,255,0.1); }}
        .container {{ max-width: 1200px; margin: 2rem auto; padding: 0 1rem; }}
        .breadcrumb {{ margin-bottom: 1rem; color: #666; }}
        .breadcrumb a {{ color: #3498db; text-decoration: none; }}
        .content {{ background: white; border-radius: 8px; padding: 2rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .content h2 {{ color: #2c3e50; margin-bottom: 1rem; }}
        .form-group {{ margin-bottom: 1.5rem; }}
        .form-group label {{ display: block; margin-bottom: 0.5rem; font-weight: 500; color: #2c3e50; }}
        .form-group textarea {{ width: 100%; height: 400px; padding: 1rem; border: 1px solid #ddd; border-radius: 4px; font-family: 'Monaco', 'Menlo', monospace; font-size: 0.9rem; }}
        .form-group textarea:focus {{ outline: none; border-color: #3498db; }}
        .btn {{ display: inline-block; background: #3498db; color: white; padding: 0.75rem 1.5rem; border-radius: 4px; text-decoration: none; border: none; cursor: pointer; font-size: 1rem; }}
        .btn:hover {{ background: #2980b9; }}
        .btn-secondary {{ background: #95a5a6; margin-left: 0.5rem; }}
        .btn-secondary:hover {{ background: #7f8c8d; }}
        .help-text {{ font-size: 0.85rem; color: #666; margin-top: 0.5rem; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>DataWiki</h1>
        <nav class="nav">
            <a href="/">Home</a>
            <a href="/wiki">Wiki</a>
            <a href="/wiki/help">Help</a>
        </nav>
    </div>
    <div class="container">
        <div class="breadcrumb">
            <a href="/">Home</a> &gt; <a href="/wiki">Wiki</a> &gt; <a href="/wiki/livedata">Project Tracker</a> &gt; Edit
        </div>
        <div class="content">
            <h2>Edit Live Data Configuration</h2>
            <form method="POST" action="/wiki/livedata/edit">
                <div class="form-group">
                    <label for="config">Live Data Configuration (JSON)</label>
                    <textarea name="config" id="config">{config}</textarea>
                    <p class="help-text">Configure the data entries and property descriptors. The displayer field controls how each property is rendered.</p>
                </div>
                <button type="submit" class="btn">Save Changes</button>
                <a href="/wiki/livedata" class="btn btn-secondary">Cancel</a>
            </form>
        </div>
    </div>
</body>
</html>
"""

WIKI_HELP_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Help - DataWiki</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 1rem 2rem; display: flex; align-items: center; justify-content: space-between; }
        .header h1 { font-size: 1.5rem; }
        .nav { display: flex; gap: 1rem; }
        .nav a { color: white; text-decoration: none; padding: 0.5rem 1rem; border-radius: 4px; }
        .nav a:hover { background: rgba(255,255,255,0.1); }
        .container { max-width: 1200px; margin: 2rem auto; padding: 0 1rem; }
        .breadcrumb { margin-bottom: 1rem; color: #666; }
        .breadcrumb a { color: #3498db; text-decoration: none; }
        .content { background: white; border-radius: 8px; padding: 2rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .content h2 { color: #2c3e50; margin-bottom: 1.5rem; }
        .content h3 { color: #2c3e50; margin: 1.5rem 0 0.75rem; }
        .content p { color: #444; line-height: 1.6; margin-bottom: 1rem; }
        .content ul { margin-left: 1.5rem; margin-bottom: 1rem; color: #444; }
        .content li { margin-bottom: 0.5rem; line-height: 1.6; }
        code { background: #f4f4f4; padding: 0.2rem 0.4rem; border-radius: 3px; font-family: 'Monaco', 'Menlo', monospace; font-size: 0.9em; }
        pre { background: #f4f4f4; padding: 1rem; border-radius: 4px; overflow-x: auto; margin: 1rem 0; }
        pre code { padding: 0; background: none; }
    </style>
</head>
<body>
    <div class="header">
        <h1>DataWiki</h1>
        <nav class="nav">
            <a href="/">Home</a>
            <a href="/wiki">Wiki</a>
            <a href="/wiki/help">Help</a>
        </nav>
    </div>
    <div class="container">
        <div class="breadcrumb">
            <a href="/">Home</a> &gt; <a href="/wiki">Wiki</a> &gt; Help
        </div>
        <div class="content">
            <h2>DataWiki Help &amp; Documentation</h2>
            
            <h3>Live Data Macro</h3>
            <p>The Live Data macro allows you to display dynamic data in tabular format. Users with edit permissions can configure the data and display options.</p>
            
            <h3>Configuration Format</h3>
            <p>The Live Data configuration is a JSON object with the following structure:</p>
            <pre><code>{
  "data": {
    "count": 3,
    "entries": [
      {"id": "1", "title": "Example", "description": "Description text"}
    ]
  },
  "meta": {
    "propertyDescriptors": [
      {"id": "title", "displayer": "text"},
      {"id": "description", "displayer": "text"}
    ]
  }
}</code></pre>
            
            <h3>Property Descriptors</h3>
            <p>Each property descriptor controls how a column is displayed:</p>
            <ul>
                <li><code>id</code> - The property name that matches keys in the data entries</li>
                <li><code>displayer</code> - How the value should be rendered:
                    <ul>
                        <li><code>text</code> - Plain text (default, HTML-escaped)</li>
                        <li><code>html</code> - Renders content as HTML</li>
                        <li><code>link</code> - Renders as a hyperlink</li>
                    </ul>
                </li>
            </ul>
            
            <h3>Editing Pages</h3>
            <p>To edit a Live Data page, click the "Edit Configuration" button on any Live Data page. You can modify the data entries and property descriptors to customize the display.</p>
        </div>
    </div>
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
