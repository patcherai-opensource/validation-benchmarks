# Label Studio Community Edition - Configuration Templates

INDEX_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Label Studio - Data Labeling Platform</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }
        .header { background: #2563eb; color: white; padding: 1rem 2rem; }
        .header h1 { font-size: 1.5rem; }
        .container { max-width: 1200px; margin: 2rem auto; padding: 0 1rem; }
        .card { background: white; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); padding: 1.5rem; margin-bottom: 1rem; }
        .card h2 { color: #1f2937; margin-bottom: 1rem; font-size: 1.25rem; }
        .card p { color: #6b7280; margin-bottom: 1rem; }
        a { color: #2563eb; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .nav-links { display: flex; gap: 2rem; margin-top: 1rem; }
        .nav-links a { color: #4b5563; padding: 0.5rem 1rem; border-radius: 4px; background: #e5e7eb; }
        .nav-links a:hover { background: #d1d5db; text-decoration: none; }
        .api-section { background: #fafafa; padding: 1rem; border-radius: 4px; font-family: monospace; font-size: 0.875rem; }
        .endpoint { background: #dbeafe; padding: 0.25rem 0.5rem; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Label Studio</h1>
        <p style="opacity: 0.8; font-size: 0.875rem;">Open Source Data Labeling Platform</p>
    </div>
    <div class="container">
        <div class="card">
            <h2>Welcome to Label Studio</h2>
            <p>Label Studio is an open-source data labeling tool for machine learning projects.</p>
            <div class="nav-links">
                <a href="/api/projects">Projects API</a>
                <a href="/projects/upload-example/">Upload Configuration</a>
                <a href="/user/whoami/">User Info</a>
            </div>
        </div>
        
        <div class="card">
            <h2>API Endpoints</h2>
            <div class="api-section">
                <p><span class="endpoint">GET</span> /api/projects - List all projects</p>
                <p><span class="endpoint">GET</span> /user/whoami/ - Current user info</p>
                <p><span class="endpoint">POST</span> /projects/upload-example/ - Upload label configuration</p>
            </div>
        </div>
        
        <div class="card">
            <h2>Label Configuration</h2>
            <p>Upload your labeling configuration XML to preview task examples. The configuration defines how data will be labeled.</p>
            <p style="margin-top: 0.5rem;"><strong>Example XML format:</strong></p>
            <pre style="background: #1f2937; color: #10b981; padding: 1rem; border-radius: 4px; overflow-x: auto; margin-top: 0.5rem;">
&lt;View&gt;
  &lt;Text name="text" value="$text"/&gt;
  &lt;Choices name="sentiment" toName="text"&gt;
    &lt;Choice value="Positive"/&gt;
    &lt;Choice value="Negative"/&gt;
  &lt;/Choices&gt;
&lt;/View&gt;</pre>
        </div>
    </div>
</body>
</html>
"""

UPLOAD_EXAMPLE_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Upload Configuration - Label Studio</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }
        .header { background: #2563eb; color: white; padding: 1rem 2rem; }
        .header h1 { font-size: 1.5rem; }
        .container { max-width: 800px; margin: 2rem auto; padding: 0 1rem; }
        .card { background: white; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); padding: 1.5rem; }
        .card h2 { color: #1f2937; margin-bottom: 1rem; }
        label { display: block; color: #374151; font-weight: 500; margin-bottom: 0.5rem; }
        textarea { width: 100%; min-height: 200px; padding: 0.75rem; border: 1px solid #d1d5db; border-radius: 4px; font-family: monospace; font-size: 0.875rem; }
        button { background: #2563eb; color: white; padding: 0.75rem 1.5rem; border: none; border-radius: 4px; cursor: pointer; font-size: 1rem; margin-top: 1rem; }
        button:hover { background: #1d4ed8; }
        .info { background: #dbeafe; color: #1e40af; padding: 1rem; border-radius: 4px; margin-bottom: 1rem; font-size: 0.875rem; }
        a { color: #2563eb; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Label Studio</h1>
    </div>
    <div class="container">
        <div class="card">
            <h2>Upload Label Configuration</h2>
            <div class="info">
                Upload your labeling configuration XML. The server will parse the configuration and generate sample task data for preview.
            </div>
            <form method="POST" action="/projects/upload-example/">
                <label for="label_config">Label Configuration (XML)</label>
                <textarea name="label_config" id="label_config" placeholder="<View>
  <Text name=&quot;text&quot; value=&quot;$text&quot;/>
  <Choices name=&quot;sentiment&quot; toName=&quot;text&quot;>
    <Choice value=&quot;Positive&quot;/>
    <Choice value=&quot;Negative&quot;/>
  </Choices>
</View>"></textarea>
                <button type="submit">Upload and Preview</button>
            </form>
            <p style="margin-top: 1rem; color: #6b7280; font-size: 0.875rem;">
                <a href="/">Back to home</a>
            </p>
        </div>
    </div>
</body>
</html>
"""

PREVIEW_RESPONSE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Configuration Preview - Label Studio</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; padding: 2rem; background: #f5f5f5; }}
        .preview {{ background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        h2 {{ color: #1f2937; margin-bottom: 1rem; }}
        .config-display {{ background: #1f2937; color: #10b981; padding: 1rem; border-radius: 4px; overflow-x: auto; white-space: pre-wrap; word-wrap: break-word; }}
        .task-data {{ background: #fafafa; padding: 1rem; border-radius: 4px; margin-top: 1rem; }}
    </style>
</head>
<body>
    <div class="preview">
        <h2>Label Configuration Preview</h2>
        <h3>Configuration:</h3>
        <div class="config-display">{config}</div>
        <h3 style="margin-top: 1rem;">Extracted Task Data:</h3>
        <div class="task-data">
            <pre>{task_json}</pre>
        </div>
    </div>
</body>
</html>
"""

# Legacy constants kept for compatibility
XSS_CONTENT = ""
XSS_CONTENT_POST = ""
XSS_CONTENT_TAG = ""
XSS_CONTENT_TAG_POST = ""
XSS_CONTENT_IFRAME = ""
XSS_CONTENT_TEXTAREA_POST = ""

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
