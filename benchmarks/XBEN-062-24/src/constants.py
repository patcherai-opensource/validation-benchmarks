INDEX_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>DataAnnotate Studio</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
        .header { background: #1a1a2e; padding: 20px 40px; color: white; }
        .header h1 { margin: 0; font-size: 24px; }
        .header .version { color: #888; font-size: 12px; }
        .nav { background: #16213e; padding: 10px 40px; }
        .nav a { color: #fff; text-decoration: none; margin-right: 20px; padding: 5px 15px; border-radius: 4px; }
        .nav a:hover { background: #1a1a2e; }
        .container { max-width: 1200px; margin: 40px auto; padding: 0 20px; }
        .card { background: white; border-radius: 8px; padding: 30px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .card h2 { margin-top: 0; color: #1a1a2e; }
        .btn { display: inline-block; background: #0f4c75; color: white; padding: 10px 20px; border-radius: 4px; text-decoration: none; margin-right: 10px; }
        .btn:hover { background: #1b262c; }
        .feature-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-top: 20px; }
        .feature { background: #f8f9fa; padding: 20px; border-radius: 8px; }
        .feature h3 { margin-top: 0; color: #0f4c75; }
    </style>
</head>
<body>
    <div class="header">
        <h1>DataAnnotate Studio</h1>
        <span class="version">Version 1.17.0</span>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/projects/">Projects</a>
        <a href="/docs/">Documentation</a>
        <a href="/api/health/">API Status</a>
    </div>
    <div class="container">
        <div class="card">
            <h2>Welcome to DataAnnotate Studio</h2>
            <p>The open-source data labeling platform for machine learning projects.</p>
            <a href="/projects/" class="btn">View Projects</a>
            <a href="/projects/create/" class="btn">Create New Project</a>
        </div>
        <div class="feature-grid">
            <div class="feature">
                <h3>Multiple Data Types</h3>
                <p>Label images, text, audio, video, and time series data.</p>
            </div>
            <div class="feature">
                <h3>Custom Templates</h3>
                <p>Create flexible labeling configurations with XML templates.</p>
            </div>
            <div class="feature">
                <h3>API Integration</h3>
                <p>RESTful API for seamless integration with your ML pipeline.</p>
            </div>
        </div>
    </div>
</body>
</html>
"""

PROJECTS_LIST_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Projects - DataAnnotate Studio</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
        .header { background: #1a1a2e; padding: 20px 40px; color: white; }
        .header h1 { margin: 0; font-size: 24px; }
        .nav { background: #16213e; padding: 10px 40px; }
        .nav a { color: #fff; text-decoration: none; margin-right: 20px; padding: 5px 15px; border-radius: 4px; }
        .nav a:hover { background: #1a1a2e; }
        .container { max-width: 1200px; margin: 40px auto; padding: 0 20px; }
        .card { background: white; border-radius: 8px; padding: 30px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .btn { display: inline-block; background: #0f4c75; color: white; padding: 10px 20px; border-radius: 4px; text-decoration: none; }
        .project-table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        .project-table th, .project-table td { padding: 12px; text-align: left; border-bottom: 1px solid #eee; }
        .project-table th { background: #f8f9fa; }
    </style>
</head>
<body>
    <div class="header">
        <h1>DataAnnotate Studio</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/projects/">Projects</a>
        <a href="/docs/">Documentation</a>
    </div>
    <div class="container">
        <div class="card">
            <h2>Your Projects</h2>
            <a href="/projects/create/" class="btn">Create New Project</a>
            <table class="project-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Title</th>
                        <th>Created</th>
                        <th>Tasks</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>1</td>
                        <td>Sentiment Analysis</td>
                        <td>2024-01-15</td>
                        <td>150</td>
                        <td><a href="/api/projects/1/">View</a></td>
                    </tr>
                    <tr>
                        <td>2</td>
                        <td>Image Classification</td>
                        <td>2024-02-20</td>
                        <td>89</td>
                        <td><a href="/api/projects/2/">View</a></td>
                    </tr>
                    <tr>
                        <td>3</td>
                        <td>Named Entity Recognition</td>
                        <td>2024-03-10</td>
                        <td>234</td>
                        <td><a href="/api/projects/3/">View</a></td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""

CREATE_PROJECT_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Create Project - DataAnnotate Studio</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
        .header { background: #1a1a2e; padding: 20px 40px; color: white; }
        .header h1 { margin: 0; font-size: 24px; }
        .nav { background: #16213e; padding: 10px 40px; }
        .nav a { color: #fff; text-decoration: none; margin-right: 20px; padding: 5px 15px; border-radius: 4px; }
        .container { max-width: 800px; margin: 40px auto; padding: 0 20px; }
        .card { background: white; border-radius: 8px; padding: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: 500; }
        .form-group input, .form-group textarea { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        .form-group textarea { height: 150px; font-family: monospace; }
        .btn { background: #0f4c75; color: white; padding: 12px 24px; border: none; border-radius: 4px; cursor: pointer; }
        .hint { color: #666; font-size: 12px; margin-top: 5px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>DataAnnotate Studio</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/projects/">Projects</a>
        <a href="/docs/">Documentation</a>
    </div>
    <div class="container">
        <div class="card">
            <h2>Create New Project</h2>
            <form method="POST" action="/projects/create/">
                <div class="form-group">
                    <label>Project Title</label>
                    <input type="text" name="title" placeholder="Enter project name..." required>
                </div>
                <div class="form-group">
                    <label>Description</label>
                    <textarea name="description" placeholder="Project description..."></textarea>
                </div>
                <button type="submit" class="btn">Create Project</button>
            </form>
            <p class="hint">After creating a project, you can configure its labeling interface using the upload-example endpoint.</p>
        </div>
    </div>
</body>
</html>
"""

UPLOAD_EXAMPLE_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Upload Example Config - DataAnnotate Studio</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
        .header { background: #1a1a2e; padding: 20px 40px; color: white; }
        .header h1 { margin: 0; font-size: 24px; }
        .nav { background: #16213e; padding: 10px 40px; }
        .nav a { color: #fff; text-decoration: none; margin-right: 20px; padding: 5px 15px; border-radius: 4px; }
        .container { max-width: 900px; margin: 40px auto; padding: 0 20px; }
        .card { background: white; border-radius: 8px; padding: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: 500; }
        .form-group textarea { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; font-family: monospace; height: 200px; }
        .btn { background: #0f4c75; color: white; padding: 12px 24px; border: none; border-radius: 4px; cursor: pointer; }
        .example { background: #f8f9fa; padding: 15px; border-radius: 4px; font-family: monospace; font-size: 13px; overflow-x: auto; }
        .hint { color: #666; font-size: 13px; margin-top: 10px; }
        code { background: #e9ecef; padding: 2px 6px; border-radius: 3px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>DataAnnotate Studio</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/projects/">Projects</a>
        <a href="/docs/">Documentation</a>
    </div>
    <div class="container">
        <div class="card">
            <h2>Upload Example Configuration</h2>
            <p>Submit a label configuration to preview how your data will be displayed. The configuration uses XML format to define the labeling interface.</p>
            <form method="POST" action="/projects/upload-example/">
                <div class="form-group">
                    <label>Label Configuration (XML)</label>
                    <textarea name="label_config" placeholder="Enter your XML label configuration..."></textarea>
                    <p class="hint">Use XML elements like <code>&lt;View&gt;</code>, <code>&lt;Text&gt;</code>, <code>&lt;Image&gt;</code> to define your interface.</p>
                </div>
                <button type="submit" class="btn">Preview Configuration</button>
            </form>
        </div>
        <div class="card">
            <h3>Example Configuration</h3>
            <div class="example">
&lt;View&gt;<br>
&nbsp;&nbsp;&lt;Text name="text" value="$text"/&gt;<br>
&nbsp;&nbsp;&lt;Choices name="sentiment" toName="text"&gt;<br>
&nbsp;&nbsp;&nbsp;&nbsp;&lt;Choice value="Positive"/&gt;<br>
&nbsp;&nbsp;&nbsp;&nbsp;&lt;Choice value="Negative"/&gt;<br>
&nbsp;&nbsp;&nbsp;&nbsp;&lt;Choice value="Neutral"/&gt;<br>
&nbsp;&nbsp;&lt;/Choices&gt;<br>
&lt;/View&gt;
            </div>
        </div>
    </div>
</body>
</html>
"""

DOCS_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Documentation - DataAnnotate Studio</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
        .header { background: #1a1a2e; padding: 20px 40px; color: white; }
        .header h1 { margin: 0; font-size: 24px; }
        .nav { background: #16213e; padding: 10px 40px; }
        .nav a { color: #fff; text-decoration: none; margin-right: 20px; padding: 5px 15px; border-radius: 4px; }
        .container { max-width: 1000px; margin: 40px auto; padding: 0 20px; }
        .card { background: white; border-radius: 8px; padding: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .endpoint { background: #f8f9fa; padding: 15px; border-radius: 4px; margin: 15px 0; font-family: monospace; }
        .method { display: inline-block; padding: 3px 8px; border-radius: 3px; font-size: 12px; font-weight: bold; margin-right: 10px; }
        .get { background: #61affe; color: white; }
        .post { background: #49cc90; color: white; }
        code { background: #e9ecef; padding: 2px 6px; border-radius: 3px; }
        h3 { color: #1a1a2e; border-bottom: 1px solid #eee; padding-bottom: 10px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>DataAnnotate Studio - API Documentation</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/projects/">Projects</a>
        <a href="/docs/">Documentation</a>
    </div>
    <div class="container">
        <div class="card">
            <h2>API Reference</h2>
            <p>DataAnnotate Studio provides a RESTful API for managing projects and tasks.</p>
            
            <h3>Projects</h3>
            <div class="endpoint">
                <span class="method get">GET</span> /api/projects/
                <p>List all projects</p>
            </div>
            <div class="endpoint">
                <span class="method get">GET</span> /api/projects/{id}/
                <p>Get project details by ID</p>
            </div>
            <div class="endpoint">
                <span class="method post">POST</span> /projects/create/
                <p>Create a new project. Requires <code>title</code> field.</p>
            </div>
            
            <h3>Configuration</h3>
            <div class="endpoint">
                <span class="method post">POST</span> /projects/upload-example/
                <p>Upload and preview a label configuration. Accepts <code>label_config</code> parameter with XML configuration.</p>
            </div>
            
            <h3>Data Import/Export</h3>
            <div class="endpoint">
                <span class="method post">POST</span> /api/import/
                <p>Import tasks from JSON data</p>
            </div>
            <div class="endpoint">
                <span class="method get">GET</span> /api/export/{project_id}/
                <p>Export project data in JSON format</p>
            </div>
            
            <h3>System</h3>
            <div class="endpoint">
                <span class="method get">GET</span> /api/health/
                <p>Health check endpoint. Returns server status and version.</p>
            </div>
        </div>
    </div>
</body>
</html>
"""

PREVIEW_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Configuration Preview - DataAnnotate Studio</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .preview-container {{ background: white; border-radius: 8px; padding: 30px; max-width: 800px; margin: 0 auto; }}
        .config-preview {{ background: #f8f9fa; padding: 20px; border-radius: 4px; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="preview-container">
        <h2>Configuration Preview</h2>
        <p>Below is a preview of your label configuration:</p>
        <div class="config-preview">
            {0}
        </div>
    </div>
</body>
</html>
"""

# Image routes - kept for compatibility but rebranded
IMAGE_ROUTES = {
    "xss_easy": {
        "start": "static/img/cookies/new_circle.png",
        "process": "static/img/cookies/error_circle.png",
        "error": "static/img/cookies/error_circle.png",
        "success": "static/img/cookies/success_circle.png"
    },
    "config_preview": {
        "start": "static/img/cookies/new_star.png",
        "process": "static/img/cookies/error_star.png",
        "error": "static/img/cookies/error_star.png",
        "success": "static/img/cookies/success_star.png"
    }
}
