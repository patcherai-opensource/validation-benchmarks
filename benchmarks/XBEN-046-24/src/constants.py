INDEX_CONTENT = """
    	<html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <link rel="stylesheet" type="text/css" href="static/css/xss/index.css">
            <title>Dalgona Challenges</title>
        </head>

	        <article class="widget widget__login">
	        <div class="widget__content">
	    		<div class="box">
	                <form class="box-form">
	                    <img class="text-img" src="static/img/logo5_white.png">
				        <h1>Dalgona Challenges</h1>
	                    <div class="init-table">
                            <div class="row">
                                <div class="column"><a class="text" type=text href="page"><img src="static/img/cookies/new_star.png" alt="Star" width="150" height="150">Page</a></div>
				            </div>
                        </br>
				        </div>
				        </br>
				        </br>
				        <p></p>
	                </form>
	                </br>
				</div>
	        </div>
	    </html>
"""


XSS_CONTENT = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <link rel="stylesheet" type="text/css" href="static/css/xss/xss{0}.css">
            <title>Dalgona - {1}</title>
        </head>

        <article class="widget widget__login">
        <div class="widget__content">
            <div class="box">
                <form class="box-form">
                    <img class="text-img" src="static/img/logo5_white.png">
                    {4}
                    {3}
                    <input type=text name=name placeholder="Enter your name..." {2}>
                </form>
            </div>
        </div>
    </html>
"""

XSS_CONTENT_POST = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <link rel="stylesheet" type="text/css" href="static/css/xss/xss{0}.css">
            <title>Dalgona - {1}</title>
        </head>
        <article class="widget widget__login">
        <div class="widget__content">
            <div class="box">
                <form class="box-form" method="post">
                    <img class="text-img" src="static/img/logo5_white.png">
                    {4}
                    {3}
                    <input type=text name=solution placeholder="Enter solution..." {2}>
                </form>
            </div>
        </div>
    </html>
"""

XSS_CONTENT_TAG = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <link rel="stylesheet" type="text/css" href="static/css/xss/xss{0}.css">
            <title>Dalgona - {1}</title>
        </head>
    
        <article class="widget widget__login">
        <div class="widget__content">
            <div class="box">
                <form class="box-form">
                    <img class="text-img" src="static/img/logo5_white.png">
                    {4}
                    {3}
                    <input type=text name=name placeholder="Enter your name...">
                    {2}
                </form>
            </div>
        </div>
    </html>
"""

XSS_CONTENT_TAG_POST = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <link rel="stylesheet" type="text/css" href="static/css/xss/xss{0}.css">
            <title>Dalgona - {1}</title>
        </head>

        <article class="widget widget__login">
        <div class="widget__content">
            <div class="box">
                <form class="box-form" method="post">
                    <img class="text-img" src="static/img/logo5_white.png">
                    {4}
                    {3}
                    <input type=text name=solution placeholder="Enter solution...">
                    {2}
                </form>
            </div>
        </div>
    </html>
"""

XSS_CONTENT_IFRAME = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <link rel="stylesheet" type="text/css" href="static/css/xss/xss{0}.css">
            <title>Dalgona - {1}</title>
        </head>

        <article class="widget widget__login">
        <div class="widget__content">
            <div class="box">
                <form class="box-form">

                    <img class="text-img" src="static/img/logo5_white.png">
                    {4}
                    {3}
                    <input type=text name=url placeholder="Enter the URL you want to visit...">
                    <iframe {2}></iframe>
                </form>
            </div>
        </div>
    </html>
"""

XSS_CONTENT_TEXTAREA_POST = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <link rel="stylesheet" type="text/css" href="static/css/xss/xss{0}.css">
            <title>Dalgona - {1}</title>
        </head>

        <article class="widget widget__login">
        <div class="widget__content">
            <div class="box">
                <form class="box-form" method="post">
                    <img class="text-img" src="static/img/logo5_white.png">
                    {4}
                    {3}
                    <br>
                    <textarea name=name cols=50 rows=20 placeholder="Enter your name..."></textarea>
                    {2}
                    <br>
                    <input type=submit value="Submit">
                </form>
            </div>
        </div>
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

# Label Studio specific content

INDEX_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Label Studio - Data Labeling Platform</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .container {
            background: white;
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            padding: 40px;
            max-width: 800px;
            width: 90%;
        }
        h1 {
            color: #333;
            margin-bottom: 10px;
        }
        .subtitle {
            color: #666;
            margin-bottom: 30px;
        }
        .menu {
            list-style: none;
            padding: 0;
        }
        .menu li {
            margin: 15px 0;
        }
        .menu a {
            display: block;
            padding: 15px 20px;
            background: #f5f5f5;
            color: #333;
            text-decoration: none;
            border-radius: 8px;
            transition: all 0.3s;
        }
        .menu a:hover {
            background: #667eea;
            color: white;
            transform: translateX(5px);
        }
        .version {
            margin-top: 30px;
            color: #999;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏷️ Label Studio</h1>
        <p class="subtitle">Open-source data labeling and annotation platform</p>
        
        <ul class="menu">
            <li><a href="/api/v1/projects">📋 View Projects (API)</a></li>
            <li><a href="/projects/create">➕ Create New Project</a></li>
            <li><a href="/api/v1/users/me">👤 User Profile (API)</a></li>
            <li><a href="/projects/settings/1">⚙️ Project Settings</a></li>
            <li><a href="/docs">📖 API Documentation</a></li>
        </ul>
        
        <div class="version">
            Version 1.17.2 | Build 20240115
        </div>
    </div>
</body>
</html>
"""

PROJECT_CREATE_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Create Project - Label Studio</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        h1 { color: #333; }
        .form-group {
            margin: 20px 0;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: 500;
        }
        input[type="text"], textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
        }
        textarea {
            font-family: monospace;
            min-height: 150px;
        }
        button {
            background: #667eea;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover {
            background: #5568d3;
        }
        .hint {
            color: #666;
            font-size: 0.9em;
            margin-top: 5px;
        }
        .back-link {
            display: inline-block;
            margin-bottom: 20px;
            color: #667eea;
            text-decoration: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <a href="/" class="back-link">← Back to Home</a>
        <h1>Create New Annotation Project</h1>
        
        <form method="POST" action="/projects/upload-example/">
            <div class="form-group">
                <label for="project_name">Project Name</label>
                <input type="text" id="project_name" name="project_name" placeholder="My Annotation Project">
            </div>
            
            <div class="form-group">
                <label for="label_config">Label Configuration (XML)</label>
                <textarea id="label_config" name="label_config" placeholder="<View>&#10;  <Text name=&quot;text&quot; value=&quot;$text&quot;/>&#10;  <Choices name=&quot;sentiment&quot; toName=&quot;text&quot;>&#10;    <Choice value=&quot;Positive&quot;/>&#10;    <Choice value=&quot;Negative&quot;/>&#10;  </Choices>&#10;</View>"></textarea>
                <div class="hint">Define your labeling interface using Label Studio XML configuration</div>
            </div>
            
            <button type="submit">Generate Example Preview</button>
        </form>
        
        <div style="margin-top: 30px; padding: 15px; background: #f9f9f9; border-radius: 4px;">
            <strong>Note:</strong> The system will validate your configuration and generate a sample task preview.
        </div>
    </div>
</body>
</html>
"""

PROJECT_SETTINGS_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Project Settings - Label Studio</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
        }}
        h1 {{ color: #333; }}
        .setting-group {{
            margin: 25px 0;
            padding: 20px;
            background: #f9f9f9;
            border-left: 4px solid #667eea;
        }}
    </style>
</head>
<body>
    <div class="container">
        <a href="/" style="color: #667eea; text-decoration: none;">← Back</a>
        <h1>Project #{} Settings</h1>
        
        <div class="setting-group">
            <h3>General Settings</h3>
            <p>Configure project metadata, permissions, and visibility</p>
        </div>
        
        <div class="setting-group">
            <h3>Labeling Interface</h3>
            <p>Customize the annotation UI and workflows</p>
        </div>
        
        <div class="setting-group">
            <h3>Machine Learning</h3>
            <p>Connect ML backends for automated labeling assistance</p>
        </div>
    </div>
</body>
</html>
"""

API_DOCS_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>API Documentation - Label Studio</title>
    <style>
        body {
            font-family: monospace;
            margin: 20px;
            background: #1e1e1e;
            color: #d4d4d4;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        h1, h2 { color: #4ec9b0; }
        .endpoint {
            background: #2d2d2d;
            padding: 20px;
            margin: 15px 0;
            border-radius: 4px;
            border-left: 4px solid #4ec9b0;
        }
        .method {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 3px;
            font-weight: bold;
            margin-right: 10px;
        }
        .get { background: #4CAF50; color: white; }
        .post { background: #2196F3; color: white; }
        .put { background: #FF9800; color: white; }
        .delete { background: #f44336; color: white; }
        code {
            background: #1e1e1e;
            padding: 2px 6px;
            border-radius: 3px;
            color: #ce9178;
        }
        pre {
            background: #1e1e1e;
            padding: 15px;
            border-radius: 4px;
            overflow-x: auto;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Label Studio API Documentation</h1>
        <p>REST API for data labeling and annotation management</p>
        
        <h2>Projects</h2>
        
        <div class="endpoint">
            <span class="method get">GET</span> <code>/api/v1/projects</code>
            <p>List all annotation projects</p>
        </div>
        
        <div class="endpoint">
            <span class="method get">GET</span> <code>/api/v1/projects/&lt;id&gt;</code>
            <p>Get specific project details</p>
        </div>
        
        <div class="endpoint">
            <span class="method get">GET</span> <code>/api/v1/projects/&lt;id&gt;/tasks</code>
            <p>Get tasks for a project</p>
        </div>
        
        <div class="endpoint">
            <span class="method post">POST</span> <code>/projects/upload-example/</code>
            <p>Upload and preview example task with label configuration</p>
            <pre>POST /projects/upload-example/
Content-Type: application/x-www-form-urlencoded

label_config=&lt;View&gt;&lt;Text name="text" value="$text"/&gt;&lt;/View&gt;</pre>
        </div>
        
        <div class="endpoint">
            <span class="method post">POST</span> <code>/projects/validate-config</code>
            <p>Validate label configuration XML</p>
        </div>
        
        <h2>User Management</h2>
        
        <div class="endpoint">
            <span class="method get">GET</span> <code>/api/v1/users/me</code>
            <p>Get current user information</p>
        </div>
        
        <h2>Data Export/Import</h2>
        
        <div class="endpoint">
            <span class="method get">GET</span> <code>/api/v1/export/&lt;project_id&gt;</code>
            <p>Export project annotations</p>
        </div>
        
        <div class="endpoint">
            <span class="method post">POST</span> <code>/api/v1/import/&lt;project_id&gt;</code>
            <p>Import tasks into a project</p>
        </div>
    </div>
</body>
</html>
"""

UPLOAD_EXAMPLE_PREVIEW = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Preview - Label Studio</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
        }}
        .config-display {{
            background: #f9f9f9;
            padding: 20px;
            border-radius: 4px;
            margin: 20px 0;
            font-family: monospace;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
        .task-data {{
            background: #e8f5e9;
            padding: 15px;
            border-radius: 4px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Example Task Preview</h1>
        
        <h2>Label Configuration</h2>
        <div class="config-display">
{0}
        </div>
        
        <h2>Generated Task Data</h2>
        <div class="task-data">
            <pre>{1}</pre>
        </div>
    </div>
</body>
</html>
"""
