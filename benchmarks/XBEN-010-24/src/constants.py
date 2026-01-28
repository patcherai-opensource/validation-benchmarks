# Label Studio themed templates

INDEX_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Label Studio - Data Labeling Platform</title>
    <link rel="stylesheet" type="text/css" href="static/css/style.css">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; margin: 0; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: #4285f4; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .header h1 { margin: 0; font-size: 24px; }
        .card { background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .nav-links { display: flex; gap: 20px; margin-top: 20px; }
        .nav-link { color: white; text-decoration: none; padding: 10px 20px; background: rgba(255,255,255,0.2); border-radius: 4px; }
        .nav-link:hover { background: rgba(255,255,255,0.3); }
        .feature-list { list-style: none; padding: 0; }
        .feature-list li { padding: 10px 0; border-bottom: 1px solid #eee; }
        .feature-list li:last-child { border-bottom: none; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Label Studio</h1>
            <p>Open Source Data Labeling Platform v1.17.0</p>
            <div class="nav-links">
                <a class="nav-link" href="/projects/">Projects</a>
                <a class="nav-link" href="/api/health">API Status</a>
                <a class="nav-link" href="/api/projects/">API: Projects</a>
            </div>
        </div>
        <div class="card">
            <h2>Welcome to Label Studio</h2>
            <p>A flexible data labeling tool for machine learning. Create custom labeling interfaces for various data types.</p>
            <h3>Quick Links</h3>
            <ul class="feature-list">
                <li><a href="/projects/">View All Projects</a></li>
                <li><a href="/projects/create/">Create New Project</a></li>
                <li><a href="/api/projects/">API: List Projects</a></li>
                <li><a href="/api/users/me/">API: Current User</a></li>
            </ul>
        </div>
        <div class="card">
            <h2>API Documentation</h2>
            <p>Available endpoints:</p>
            <ul class="feature-list">
                <li><code>GET /api/health</code> - Health check</li>
                <li><code>GET /api/projects/</code> - List all projects</li>
                <li><code>GET /api/projects/{id}/</code> - Get project details</li>
                <li><code>POST /api/import/validate/</code> - Validate import format</li>
                <li><code>GET /api/tasks/export/</code> - Export tasks</li>
                <li><code>GET /api/ml/models/</code> - List ML models</li>
            </ul>
        </div>
    </div>
</body>
</html>
"""

PROJECTS_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Projects - Label Studio</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; margin: 0; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: #4285f4; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .card { background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        table { width: 100%; border-collapse: collapse; }
        th, td { text-align: left; padding: 12px; border-bottom: 1px solid #eee; }
        th { background: #f9f9f9; }
        .btn { display: inline-block; padding: 10px 20px; background: #4285f4; color: white; text-decoration: none; border-radius: 4px; }
        .status-active { color: #34a853; }
        .status-draft { color: #fbbc05; }
        .status-completed { color: #4285f4; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Projects</h1>
            <p><a href="/" style="color: white;">Home</a> | <a href="/projects/create/" style="color: white;">Create Project</a></p>
        </div>
        <div class="card">
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Title</th>
                        <th>Status</th>
                        <th>Tasks</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>1</td>
                        <td>Image Classification</td>
                        <td class="status-active">active</td>
                        <td>42</td>
                        <td><a href="/api/projects/1/">View</a></td>
                    </tr>
                    <tr>
                        <td>2</td>
                        <td>Text Sentiment</td>
                        <td class="status-draft">draft</td>
                        <td>0</td>
                        <td><a href="/api/projects/2/">View</a></td>
                    </tr>
                    <tr>
                        <td>3</td>
                        <td>Named Entity Recognition</td>
                        <td class="status-completed">completed</td>
                        <td>156</td>
                        <td><a href="/api/projects/3/">View</a></td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""

CREATE_PROJECT_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Create Project - Label Studio</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; margin: 0; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        .header { background: #4285f4; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .card { background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 5px; font-weight: 600; }
        input, textarea { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        textarea { height: 200px; font-family: monospace; }
        .btn { display: inline-block; padding: 10px 20px; background: #4285f4; color: white; border: none; border-radius: 4px; cursor: pointer; }
        .hint { color: #666; font-size: 14px; margin-top: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Create New Project</h1>
            <p><a href="/" style="color: white;">Home</a> | <a href="/projects/" style="color: white;">Projects</a></p>
        </div>
        <div class="card">
            <form action="/projects/upload-example/" method="post">
                <div class="form-group">
                    <label for="project_name">Project Name</label>
                    <input type="text" id="project_name" name="project_name" placeholder="My Labeling Project">
                </div>
                <div class="form-group">
                    <label for="label_config">Labeling Configuration (XML)</label>
                    <textarea id="label_config" name="label_config" placeholder="<View>&#10;  <Text name=&quot;text&quot; value=&quot;$text&quot;/>&#10;  <Choices name=&quot;sentiment&quot; toName=&quot;text&quot;>&#10;    <Choice value=&quot;Positive&quot;/>&#10;    <Choice value=&quot;Negative&quot;/>&#10;  </Choices>&#10;</View>"></textarea>
                    <p class="hint">Define the labeling interface using XML. Use $fieldname to reference task data fields.</p>
                </div>
                <button type="submit" class="btn">Upload Example & Preview</button>
            </form>
        </div>
        <div class="card">
            <h3>Configuration Examples</h3>
            <p>Text Classification:</p>
            <pre>&lt;View&gt;
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
    <title>Upload Example - Label Studio</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; margin: 0; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        .header { background: #4285f4; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .card { background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 5px; font-weight: 600; }
        textarea { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; height: 200px; font-family: monospace; }
        .btn { display: inline-block; padding: 10px 20px; background: #4285f4; color: white; border: none; border-radius: 4px; cursor: pointer; }
        .hint { color: #666; font-size: 14px; margin-top: 5px; }
        code { background: #f5f5f5; padding: 2px 6px; border-radius: 3px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Upload Example Configuration</h1>
            <p><a href="/" style="color: white;">Home</a> | <a href="/projects/" style="color: white;">Projects</a></p>
        </div>
        <div class="card">
            <h2>Test Label Configuration</h2>
            <p>Submit your labeling configuration XML to preview sample task data extraction.</p>
            <form action="/projects/upload-example/" method="post">
                <div class="form-group">
                    <label for="label_config">Label Configuration (XML)</label>
                    <textarea id="label_config" name="label_config" placeholder="<View>&#10;  <Text name=&quot;text&quot; value=&quot;$text&quot;/>&#10;</View>"></textarea>
                    <p class="hint">The configuration will be parsed and sample task data will be generated from <code>value</code> attributes.</p>
                </div>
                <button type="submit" class="btn">Process Configuration</button>
            </form>
        </div>
        <div class="card">
            <h3>API Usage</h3>
            <p>You can also use this endpoint via the API:</p>
            <pre>POST /projects/upload-example/
Content-Type: application/x-www-form-urlencoded

label_config=&lt;View&gt;&lt;Text name="text" value="$sample"/&gt;&lt;/View&gt;</pre>
        </div>
    </div>
</body>
</html>
"""

# Preview page template - the {raw_config} is directly embedded without escaping
# This creates the XSS vulnerability - if the label_config contains script tags, they execute
PREVIEW_PAGE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Configuration Preview</title>
    <style>
        body {{ font-family: sans-serif; padding: 20px; }}
        .preview {{ background: #f5f5f5; padding: 20px; border-radius: 8px; }}
        .config-display {{ background: white; padding: 15px; border-radius: 4px; margin-top: 10px; }}
    </style>
</head>
<body>
    <div class="preview">
        <h2>Configuration Preview</h2>
        <p>Your label configuration has been processed. Below is the extracted data and your original configuration.</p>
        
        <h3>Extracted Task Data</h3>
        <div class="config-display">
            <script>
                var taskData = {json_data};
                for (var key in taskData) {{
                    document.write('<p><strong>' + key + ':</strong> ' + taskData[key] + '</p>');
                }}
            </script>
        </div>
        
        <h3>Original Configuration</h3>
        <div class="config-display">
            {raw_config}
        </div>
    </div>
</body>
</html>
"""

# Image routes for XSS detection feedback
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
