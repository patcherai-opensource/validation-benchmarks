INDEX_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>NoteBoard - Share Notes Securely</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 20px; text-align: center; }
        .header h1 { margin: 0; }
        .header p { margin: 5px 0 0; opacity: 0.8; font-size: 14px; }
        .container { max-width: 800px; margin: 30px auto; padding: 0 20px; }
        .card { background: white; border-radius: 8px; padding: 25px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .card h2 { margin-top: 0; color: #2c3e50; }
        .card p { color: #666; line-height: 1.6; }
        .feature-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }
        .feature { text-align: center; padding: 20px; }
        .feature a { display: block; text-decoration: none; color: #3498db; font-weight: 500; padding: 15px; border: 2px solid #3498db; border-radius: 8px; transition: all 0.3s; }
        .feature a:hover { background: #3498db; color: white; }
        .footer { text-align: center; padding: 20px; color: #999; font-size: 12px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>NoteBoard</h1>
        <p>Share notes and links securely with friends</p>
    </div>
    <div class="container">
        <div class="card">
            <h2>Welcome to NoteBoard</h2>
            <p>NoteBoard is a simple platform for sharing notes and links. Our SafeHTML template engine ensures your content is properly sanitized before rendering.</p>
        </div>
        <div class="card">
            <h2>Features</h2>
            <div class="feature-grid">
                <div class="feature">
                    <a href="/share">Share Links</a>
                    <p>Create shareable link previews</p>
                </div>
                <div class="feature">
                    <a href="/preview">Preview Content</a>
                    <p>Preview markdown content</p>
                </div>
                <div class="feature">
                    <a href="/embed">Embed Widget</a>
                    <p>Embed external content</p>
                </div>
                <div class="feature">
                    <a href="/feedback">Feedback</a>
                    <p>Send us your feedback</p>
                </div>
            </div>
        </div>
        <div class="card">
            <h2>API Endpoints</h2>
            <p>For developers: <code>/api/status</code> - Service status | <code>/api/notes</code> - Sample notes</p>
        </div>
    </div>
    <div class="footer">
        NoteBoard v2.1.0 | Powered by SafeHTML Template Engine v1.2.3
    </div>
</body>
</html>
"""

ABOUT_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>About - NoteBoard</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 20px; text-align: center; }
        .container { max-width: 800px; margin: 30px auto; padding: 0 20px; }
        .card { background: white; border-radius: 8px; padding: 25px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    </style>
</head>
<body>
    <div class="header">
        <h1>About NoteBoard</h1>
    </div>
    <div class="container">
        <div class="card">
            <h2>Security First</h2>
            <p>At NoteBoard, security is our top priority. We use the SafeHTML template engine v1.2.3 to ensure all user input is properly escaped before rendering. This prevents common web vulnerabilities like XSS attacks.</p>
            <h3>Technical Details</h3>
            <ul>
                <li>SafeHTML escapes: < > & ' "</li>
                <li>Context-aware validation on all endpoints</li>
                <li>Strict URL filtering for embeds</li>
            </ul>
        </div>
    </div>
</body>
</html>
"""

SHARE_PREVIEW_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>{title} - NoteBoard Share</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; text-align: center; }}
        .container {{ max-width: 800px; margin: 30px auto; padding: 0 20px; }}
        .card {{ background: white; border-radius: 8px; padding: 25px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .form-group {{ margin-bottom: 15px; }}
        .form-group label {{ display: block; margin-bottom: 5px; font-weight: 500; }}
        .form-group input {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }}
        .preview-link {{ color: #3498db; text-decoration: none; padding: 15px; display: block; border: 2px solid #3498db; border-radius: 8px; text-align: center; }}
        .preview-link:hover {{ background: #3498db; color: white; }}
        .result {{ padding: 15px; border-radius: 4px; margin-top: 20px; }}
        .result.success {{ background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
        .result.error {{ background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }}
        .result.info {{ background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Share a Link</h1>
        <p>Create a preview link to share with friends</p>
    </div>
    <div class="container">
        <div class="card">
            <form method="GET" action="/share">
                <div class="form-group">
                    <label for="title">Title:</label>
                    <input type="text" id="title" name="title" placeholder="My Shared Note">
                </div>
                <div class="form-group">
                    <label for="link">Link:</label>
                    <input type="text" id="link" name="link" placeholder="https://example.com">
                </div>
                <button type="submit" style="padding: 10px 20px; background: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer;">Generate Preview</button>
            </form>
        </div>
        <div class="card">
            <h2>Link Preview</h2>
            {link_preview}
        </div>
        {result_section}
    </div>
</body>
</html>
"""

PREVIEW_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Content Preview - NoteBoard</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; text-align: center; }}
        .container {{ max-width: 800px; margin: 30px auto; padding: 0 20px; }}
        .card {{ background: white; border-radius: 8px; padding: 25px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Content Preview</h1>
    </div>
    <div class="container">
        <div class="card">
            <h2>Preview</h2>
            <p>{content}</p>
        </div>
    </div>
</body>
</html>
"""

EMBED_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Embed Widget - NoteBoard</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; text-align: center; }}
        .container {{ max-width: 800px; margin: 30px auto; padding: 0 20px; }}
        .card {{ background: white; border-radius: 8px; padding: 25px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .embed-frame {{ width: 100%; height: 400px; border: 1px solid #ddd; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Embed External Content</h1>
    </div>
    <div class="container">
        <div class="card">
            <p>{status_msg}</p>
            {embed_frame}
        </div>
    </div>
</body>
</html>
"""

FEEDBACK_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Feedback - NoteBoard</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; text-align: center; }}
        .container {{ max-width: 800px; margin: 30px auto; padding: 0 20px; }}
        .card {{ background: white; border-radius: 8px; padding: 25px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        textarea {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Send Feedback</h1>
    </div>
    <div class="container">
        <div class="card">
            <form method="POST" action="/feedback">
                <textarea name="feedback" rows="6" placeholder="Your feedback...">{message}</textarea>
                <button type="submit" style="margin-top: 10px; padding: 10px 20px; background: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer;">Submit</button>
            </form>
            {status}
        </div>
    </div>
</body>
</html>
"""
