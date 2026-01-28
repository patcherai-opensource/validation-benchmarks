# WikiBase Templates

WIKI_PAGE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - WikiBase</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; max-width: 1200px; margin: 0 auto; padding: 20px; background: #f6f6f6; }}
        .wiki-header {{ background: #0645ad; color: white; padding: 15px 20px; margin: -20px -20px 20px -20px; }}
        .wiki-header h1 {{ margin: 0; font-size: 1.5em; }}
        .wiki-header a {{ color: white; text-decoration: none; }}
        .wiki-nav {{ background: #fafafa; border: 1px solid #ddd; padding: 10px 15px; margin-bottom: 20px; }}
        .wiki-nav a {{ margin-right: 15px; color: #0645ad; text-decoration: none; }}
        .wiki-nav a:hover {{ text-decoration: underline; }}
        .wiki-content {{ background: white; padding: 20px; border: 1px solid #ddd; }}
        .wiki-content h1 {{ border-bottom: 1px solid #a2a9b1; padding-bottom: 0.3em; }}
        .wiki-content h2 {{ border-bottom: 1px solid #eee; padding-bottom: 0.2em; }}
        .wiki-content a {{ color: #0645ad; }}
        .wiki-content code {{ background: #f8f9fa; padding: 2px 6px; border-radius: 3px; font-family: monospace; }}
        .wiki-content pre {{ background: #f8f9fa; padding: 15px; overflow-x: auto; border: 1px solid #eaecf0; }}
        .wiki-footer {{ margin-top: 20px; padding-top: 10px; border-top: 1px solid #ddd; font-size: 0.9em; color: #666; }}
        .tabinclude-content {{ background: #f9f9f9; border: 1px solid #ddd; padding: 10px; margin: 10px 0; }}
        .tabinclude-error {{ background: #fee; border: 1px solid #c00; color: #c00; padding: 10px; margin: 10px 0; }}
        .tabinclude-warning {{ background: #ffc; border: 1px solid #cc0; color: #660; padding: 10px; margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="wiki-header">
        <h1><a href="/wiki/Main_Page">WikiBase</a></h1>
    </div>
    <div class="wiki-nav">
        <a href="/wiki/Main_Page">Main Page</a>
        <a href="/wiki/Special:AllPages">All Pages</a>
        <a href="/wiki/Special:RecentChanges">Recent Changes</a>
        <a href="/wiki/Special:Preview">Preview Tool</a>
        <a href="/api/pages">API</a>
    </div>
    <div class="wiki-content">
        {content}
    </div>
    <div class="wiki-footer">
        <p>WikiBase v2.3.1 | Page: {page_name}</p>
    </div>
</body>
</html>
"""

WIKI_NOT_FOUND_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Page Not Found - WikiBase</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; max-width: 1200px; margin: 0 auto; padding: 20px; background: #f6f6f6; }}
        .wiki-header {{ background: #0645ad; color: white; padding: 15px 20px; margin: -20px -20px 20px -20px; }}
        .wiki-header h1 {{ margin: 0; font-size: 1.5em; }}
        .wiki-header a {{ color: white; text-decoration: none; }}
        .wiki-nav {{ background: #fafafa; border: 1px solid #ddd; padding: 10px 15px; margin-bottom: 20px; }}
        .wiki-nav a {{ margin-right: 15px; color: #0645ad; text-decoration: none; }}
        .wiki-content {{ background: white; padding: 20px; border: 1px solid #ddd; }}
        .error-box {{ background: #fee; border: 1px solid #c00; padding: 20px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="wiki-header">
        <h1><a href="/wiki/Main_Page">WikiBase</a></h1>
    </div>
    <div class="wiki-nav">
        <a href="/wiki/Main_Page">Main Page</a>
        <a href="/wiki/Special:AllPages">All Pages</a>
        <a href="/wiki/Special:Preview">Preview Tool</a>
    </div>
    <div class="wiki-content">
        <h1>Page Not Found</h1>
        <div class="error-box">
            <p>The page <strong>{page_name}</strong> does not exist.</p>
            <p>You can <a href="/wiki/Special:AllPages">browse all pages</a> or return to the <a href="/wiki/Main_Page">main page</a>.</p>
        </div>
    </div>
</body>
</html>
"""

PREVIEW_PAGE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Preview Markup - WikiBase</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; max-width: 1200px; margin: 0 auto; padding: 20px; background: #f6f6f6; }}
        .wiki-header {{ background: #0645ad; color: white; padding: 15px 20px; margin: -20px -20px 20px -20px; }}
        .wiki-header h1 {{ margin: 0; font-size: 1.5em; }}
        .wiki-header a {{ color: white; text-decoration: none; }}
        .wiki-nav {{ background: #fafafa; border: 1px solid #ddd; padding: 10px 15px; margin-bottom: 20px; }}
        .wiki-nav a {{ margin-right: 15px; color: #0645ad; text-decoration: none; }}
        .wiki-content {{ background: white; padding: 20px; border: 1px solid #ddd; }}
        .preview-form {{ margin-bottom: 20px; }}
        .preview-form textarea {{ width: 100%; height: 150px; font-family: monospace; padding: 10px; border: 1px solid #ccc; }}
        .preview-form button {{ background: #0645ad; color: white; border: none; padding: 10px 20px; cursor: pointer; margin-top: 10px; }}
        .preview-form button:hover {{ background: #0056b3; }}
        .preview-result {{ background: #f9f9f9; border: 1px solid #ddd; padding: 20px; margin-top: 20px; }}
        .preview-result h3 {{ margin-top: 0; border-bottom: 1px solid #ddd; padding-bottom: 10px; }}
        .success-message {{ background: #dff0d8; border: 1px solid #3c763d; color: #3c763d; padding: 15px; margin: 15px 0; }}
        .info-message {{ background: #d9edf7; border: 1px solid #31708f; color: #31708f; padding: 15px; margin: 15px 0; }}
        .tabinclude-content {{ background: #f9f9f9; border: 1px solid #ddd; padding: 10px; margin: 10px 0; }}
        .tabinclude-error {{ background: #fee; border: 1px solid #c00; color: #c00; padding: 10px; margin: 10px 0; }}
        .tabinclude-warning {{ background: #ffc; border: 1px solid #cc0; color: #660; padding: 10px; margin: 10px 0; }}
        .help-text {{ background: #f0f0f0; padding: 15px; margin: 20px 0; border-left: 4px solid #0645ad; }}
    </style>
</head>
<body>
    <div class="wiki-header">
        <h1><a href="/wiki/Main_Page">WikiBase</a></h1>
    </div>
    <div class="wiki-nav">
        <a href="/wiki/Main_Page">Main Page</a>
        <a href="/wiki/Special:AllPages">All Pages</a>
        <a href="/wiki/Help:Templates">Help:Templates</a>
    </div>
    <div class="wiki-content">
        <h1>Special:Preview</h1>
        <p>Use this tool to preview how wiki markup will be rendered. This is useful for testing templates before publishing.</p>
        
        <div class="help-text">
            <strong>Tip:</strong> You can use the <code>&lt;tabinclude&gt;</code> tag to include content from other pages:
            <pre>&lt;tabinclude&gt;PageName | Display Label&lt;/tabinclude&gt;</pre>
        </div>
        
        {flag_message}
        
        <form class="preview-form" method="POST">
            <label for="markup"><strong>Enter wiki markup:</strong></label><br><br>
            <textarea name="markup" id="markup" placeholder="Enter your wiki markup here...">{markup}</textarea>
            <br>
            <button type="submit">Preview</button>
        </form>
        
        <div class="preview-result">
            <h3>Rendered Output:</h3>
            <div id="rendered-content">
                {rendered}
            </div>
        </div>
    </div>
</body>
</html>
"""

PREVIEW_RESULT_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <style>
        .tabinclude-content {{ background: #f9f9f9; border: 1px solid #ddd; padding: 10px; margin: 10px 0; }}
        .tabinclude-error {{ background: #fee; border: 1px solid #c00; color: #c00; padding: 10px; margin: 10px 0; }}
        .tabinclude-warning {{ background: #ffc; border: 1px solid #cc0; color: #660; padding: 10px; margin: 10px 0; }}
    </style>
</head>
<body>
    <h2>Preview</h2>
    <div class="preview-content">
        {rendered}
    </div>
</body>
</html>
"""

RECENT_CHANGES_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Recent Changes - WikiBase</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; max-width: 1200px; margin: 0 auto; padding: 20px; background: #f6f6f6; }}
        .wiki-header {{ background: #0645ad; color: white; padding: 15px 20px; margin: -20px -20px 20px -20px; }}
        .wiki-header h1 {{ margin: 0; font-size: 1.5em; }}
        .wiki-header a {{ color: white; text-decoration: none; }}
        .wiki-nav {{ background: #fafafa; border: 1px solid #ddd; padding: 10px 15px; margin-bottom: 20px; }}
        .wiki-nav a {{ margin-right: 15px; color: #0645ad; text-decoration: none; }}
        .wiki-content {{ background: white; padding: 20px; border: 1px solid #ddd; }}
        .change-item {{ border-bottom: 1px solid #eee; padding: 10px 0; }}
        .change-item:last-child {{ border-bottom: none; }}
        .change-date {{ color: #666; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="wiki-header">
        <h1><a href="/wiki/Main_Page">WikiBase</a></h1>
    </div>
    <div class="wiki-nav">
        <a href="/wiki/Main_Page">Main Page</a>
        <a href="/wiki/Special:AllPages">All Pages</a>
        <a href="/wiki/Special:Preview">Preview Tool</a>
    </div>
    <div class="wiki-content">
        <h1>Recent Changes</h1>
        <div class="change-item">
            <span class="change-date">2024-01-15 14:32</span> - 
            <a href="/wiki/Help:Templates">Help:Templates</a> - Updated tabinclude documentation
        </div>
        <div class="change-item">
            <span class="change-date">2024-01-15 10:15</span> - 
            <a href="/wiki/API_Reference">API Reference</a> - Added preview endpoint
        </div>
        <div class="change-item">
            <span class="change-date">2024-01-14 16:45</span> - 
            <a href="/wiki/Main_Page">Main Page</a> - Updated welcome message
        </div>
        <div class="change-item">
            <span class="change-date">2024-01-14 09:22</span> - 
            <a href="/wiki/Documentation">Documentation</a> - Initial content
        </div>
    </div>
</body>
</html>
"""

ALL_PAGES_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>All Pages - WikiBase</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; max-width: 1200px; margin: 0 auto; padding: 20px; background: #f6f6f6; }}
        .wiki-header {{ background: #0645ad; color: white; padding: 15px 20px; margin: -20px -20px 20px -20px; }}
        .wiki-header h1 {{ margin: 0; font-size: 1.5em; }}
        .wiki-header a {{ color: white; text-decoration: none; }}
        .wiki-nav {{ background: #fafafa; border: 1px solid #ddd; padding: 10px 15px; margin-bottom: 20px; }}
        .wiki-nav a {{ margin-right: 15px; color: #0645ad; text-decoration: none; }}
        .wiki-content {{ background: white; padding: 20px; border: 1px solid #ddd; }}
        .wiki-content ul {{ list-style: none; padding: 0; }}
        .wiki-content li {{ padding: 5px 0; border-bottom: 1px solid #eee; }}
        .wiki-content li:last-child {{ border-bottom: none; }}
        .wiki-content a {{ color: #0645ad; text-decoration: none; }}
        .wiki-content a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="wiki-header">
        <h1><a href="/wiki/Main_Page">WikiBase</a></h1>
    </div>
    <div class="wiki-nav">
        <a href="/wiki/Main_Page">Main Page</a>
        <a href="/wiki/Special:RecentChanges">Recent Changes</a>
        <a href="/wiki/Special:Preview">Preview Tool</a>
    </div>
    <div class="wiki-content">
        <h1>All Pages</h1>
        <ul>
            {pages_list}
        </ul>
    </div>
</body>
</html>
"""

# Keep IMAGE_ROUTES for compatibility (though not used in new version)
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
