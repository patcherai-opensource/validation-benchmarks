INDEX_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Label Studio - Data Labeling Platform</title>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif; background: #f5f7fa; color: #333; }
        .navbar { background: #1a1a2e; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; }
        .navbar-brand { color: #fff; font-size: 1.5rem; font-weight: bold; text-decoration: none; }
        .navbar-nav { display: flex; gap: 1.5rem; }
        .navbar-nav a { color: #ccc; text-decoration: none; transition: color 0.2s; }
        .navbar-nav a:hover { color: #fff; }
        .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
        .hero { text-align: center; padding: 4rem 0; }
        .hero h1 { font-size: 2.5rem; margin-bottom: 1rem; color: #1a1a2e; }
        .hero p { font-size: 1.2rem; color: #666; margin-bottom: 2rem; }
        .btn { display: inline-block; padding: 0.75rem 1.5rem; border-radius: 6px; text-decoration: none; font-weight: 500; transition: all 0.2s; }
        .btn-primary { background: #4f46e5; color: #fff; }
        .btn-primary:hover { background: #4338ca; }
        .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; margin-top: 3rem; }
        .feature-card { background: #fff; padding: 2rem; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.08); }
        .feature-card h3 { margin-bottom: 0.5rem; color: #1a1a2e; }
        .feature-card p { color: #666; }
        .footer { text-align: center; padding: 2rem; color: #999; margin-top: 3rem; }
    </style>
</head>
<body>
    <nav class="navbar">
        <a href="/" class="navbar-brand">Label Studio</a>
        <div class="navbar-nav">
            <a href="/projects">Projects</a>
            <a href="/projects/upload-example/">Upload Example</a>
            <a href="#">Documentation</a>
            <a href="#">Settings</a>
        </div>
    </nav>
    
    <div class="container">
        <div class="hero">
            <h1>Welcome to Label Studio</h1>
            <p>The most flexible data labeling platform for machine learning projects</p>
            <a href="/projects" class="btn btn-primary">View Projects</a>
        </div>
        
        <div class="features">
            <div class="feature-card">
                <h3>Multi-type Data Support</h3>
                <p>Label images, audio, text, time series, and multi-domain data types with ease.</p>
            </div>
            <div class="feature-card">
                <h3>Flexible Configuration</h3>
                <p>Customize your labeling interface using our powerful XML-based configuration system.</p>
            </div>
            <div class="feature-card">
                <h3>Easy Integration</h3>
                <p>Connect with your ML pipelines and export labeled data in multiple formats.</p>
            </div>
        </div>
    </div>
    
    <div class="footer">
        <p>&copy; 2024 Label Studio. All rights reserved.</p>
    </div>
</body>
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

PROJECTS_LIST_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Projects - Label Studio</title>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif; background: #f5f7fa; color: #333; }
        .navbar { background: #1a1a2e; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; }
        .navbar-brand { color: #fff; font-size: 1.5rem; font-weight: bold; text-decoration: none; }
        .navbar-nav { display: flex; gap: 1.5rem; }
        .navbar-nav a { color: #ccc; text-decoration: none; transition: color 0.2s; }
        .navbar-nav a:hover { color: #fff; }
        .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
        .page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; }
        .page-header h1 { font-size: 1.8rem; color: #1a1a2e; }
        .btn { display: inline-block; padding: 0.75rem 1.5rem; border-radius: 6px; text-decoration: none; font-weight: 500; transition: all 0.2s; border: none; cursor: pointer; }
        .btn-primary { background: #4f46e5; color: #fff; }
        .btn-primary:hover { background: #4338ca; }
        .project-card { background: #fff; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.08); margin-bottom: 1rem; }
        .project-card h3 { margin-bottom: 0.5rem; color: #1a1a2e; }
        .project-card p { color: #666; font-size: 0.9rem; }
        .project-meta { display: flex; gap: 1rem; margin-top: 1rem; font-size: 0.8rem; color: #999; }
    </style>
</head>
<body>
    <nav class="navbar">
        <a href="/" class="navbar-brand">Label Studio</a>
        <div class="navbar-nav">
            <a href="/projects">Projects</a>
            <a href="/projects/upload-example/">Upload Example</a>
            <a href="#">Documentation</a>
            <a href="#">Settings</a>
        </div>
    </nav>
    
    <div class="container">
        <div class="page-header">
            <h1>Projects</h1>
            <a href="/projects/upload-example/" class="btn btn-primary">Create Project</a>
        </div>
        
        <div class="project-card">
            <h3>Image Classification Demo</h3>
            <p>Sample project for image classification tasks with pre-labeled data.</p>
            <div class="project-meta">
                <span>Tasks: 150</span>
                <span>Completed: 89</span>
                <span>Created: Dec 15, 2024</span>
            </div>
        </div>
        
        <div class="project-card">
            <h3>Text Sentiment Analysis</h3>
            <p>NLP project for analyzing customer feedback sentiment.</p>
            <div class="project-meta">
                <span>Tasks: 500</span>
                <span>Completed: 234</span>
                <span>Created: Dec 10, 2024</span>
            </div>
        </div>
        
        <div class="project-card">
            <h3>Named Entity Recognition</h3>
            <p>Extract entities from news articles for information retrieval.</p>
            <div class="project-meta">
                <span>Tasks: 320</span>
                <span>Completed: 78</span>
                <span>Created: Nov 28, 2024</span>
            </div>
        </div>
    </div>
</body>
</html>
"""

PROJECT_DETAIL_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Project {project_id} - Label Studio</title>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif; background: #f5f7fa; color: #333; }}
        .navbar {{ background: #1a1a2e; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; }}
        .navbar-brand {{ color: #fff; font-size: 1.5rem; font-weight: bold; text-decoration: none; }}
        .navbar-nav {{ display: flex; gap: 1.5rem; }}
        .navbar-nav a {{ color: #ccc; text-decoration: none; transition: color 0.2s; }}
        .navbar-nav a:hover {{ color: #fff; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 2rem; }}
        .page-header {{ margin-bottom: 2rem; }}
        .page-header h1 {{ font-size: 1.8rem; color: #1a1a2e; }}
        .card {{ background: #fff; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.08); margin-bottom: 1rem; }}
    </style>
</head>
<body>
    <nav class="navbar">
        <a href="/" class="navbar-brand">Label Studio</a>
        <div class="navbar-nav">
            <a href="/projects">Projects</a>
            <a href="/projects/upload-example/">Upload Example</a>
            <a href="#">Documentation</a>
            <a href="#">Settings</a>
        </div>
    </nav>
    
    <div class="container">
        <div class="page-header">
            <h1>Project {project_id}</h1>
        </div>
        
        <div class="card">
            <h3>Project Details</h3>
            <p>Project ID: {project_id}</p>
            <p>Status: Active</p>
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
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif; background: #f5f7fa; color: #333; }
        .navbar { background: #1a1a2e; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; }
        .navbar-brand { color: #fff; font-size: 1.5rem; font-weight: bold; text-decoration: none; }
        .navbar-nav { display: flex; gap: 1.5rem; }
        .navbar-nav a { color: #ccc; text-decoration: none; transition: color 0.2s; }
        .navbar-nav a:hover { color: #fff; }
        .container { max-width: 800px; margin: 0 auto; padding: 2rem; }
        .page-header { margin-bottom: 2rem; }
        .page-header h1 { font-size: 1.8rem; color: #1a1a2e; margin-bottom: 0.5rem; }
        .page-header p { color: #666; }
        .form-card { background: #fff; padding: 2rem; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.08); }
        .form-group { margin-bottom: 1.5rem; }
        .form-group label { display: block; margin-bottom: 0.5rem; font-weight: 500; color: #1a1a2e; }
        .form-group textarea { width: 100%; padding: 0.75rem; border: 1px solid #ddd; border-radius: 6px; font-family: monospace; font-size: 0.9rem; resize: vertical; }
        .form-group textarea:focus { outline: none; border-color: #4f46e5; }
        .btn { display: inline-block; padding: 0.75rem 1.5rem; border-radius: 6px; text-decoration: none; font-weight: 500; transition: all 0.2s; border: none; cursor: pointer; font-size: 1rem; }
        .btn-primary { background: #4f46e5; color: #fff; }
        .btn-primary:hover { background: #4338ca; }
        .help-text { font-size: 0.85rem; color: #666; margin-top: 0.5rem; }
        .example-config { background: #f8f9fa; padding: 1rem; border-radius: 6px; font-family: monospace; font-size: 0.85rem; margin-top: 1rem; }
    </style>
</head>
<body>
    <nav class="navbar">
        <a href="/" class="navbar-brand">Label Studio</a>
        <div class="navbar-nav">
            <a href="/projects">Projects</a>
            <a href="/projects/upload-example/">Upload Example</a>
            <a href="#">Documentation</a>
            <a href="#">Settings</a>
        </div>
    </nav>
    
    <div class="container">
        <div class="page-header">
            <h1>Upload Example Configuration</h1>
            <p>Test your label configuration with sample task data</p>
        </div>
        
        <div class="form-card">
            <form method="POST" action="/projects/upload-example/">
                <div class="form-group">
                    <label for="label_config">Label Configuration (XML)</label>
                    <textarea id="label_config" name="label_config" rows="12" placeholder="Enter your label configuration XML..."></textarea>
                    <p class="help-text">Paste your XML label configuration to preview task data structure.</p>
                </div>
                
                <button type="submit" class="btn btn-primary">Upload & Preview</button>
            </form>
            
            <div class="example-config">
                <strong>Example Configuration:</strong><br><br>
                &lt;View&gt;<br>
                &nbsp;&nbsp;&lt;Text name="text" value="$text"/&gt;<br>
                &nbsp;&nbsp;&lt;Choices name="sentiment" toName="text"&gt;<br>
                &nbsp;&nbsp;&nbsp;&nbsp;&lt;Choice value="positive"/&gt;<br>
                &nbsp;&nbsp;&nbsp;&nbsp;&lt;Choice value="negative"/&gt;<br>
                &nbsp;&nbsp;&lt;/Choices&gt;<br>
                &lt;/View&gt;
            </div>
        </div>
    </div>
</body>
</html>
"""

UPLOAD_RESULT_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Configuration Preview - Label Studio</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif; background: #f5f7fa; color: #333; }}
        .container {{ max-width: 800px; margin: 0 auto; padding: 2rem; }}
        .preview-box {{ background: #fff; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.08); }}
        .json-preview {{ background: #1a1a2e; color: #e0e0e0; padding: 1rem; border-radius: 6px; font-family: monospace; white-space: pre-wrap; word-break: break-all; }}
        .task-item {{ padding: 0.5rem; background: #f8f9fa; margin: 0.5rem 0; border-radius: 4px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="preview-box">
            <h3>Task Data Preview</h3>
            <div class="json-preview" id="task-data">{json_data}</div>
            <div id="rendered-data"></div>
        </div>
    </div>
    <script type="text/javascript">
        (function() {{
            var jsonStr = document.getElementById('task-data').textContent;
            try {{
                var taskData = JSON.parse(jsonStr);
                var container = document.getElementById('rendered-data');
                if (taskData) {{
                    for (var key in taskData) {{
                        if (taskData.hasOwnProperty(key)) {{
                            var value = taskData[key];
                            if (typeof value === 'string') {{
                                container.innerHTML += '<div class="task-item"><strong>' + key + ':</strong> ' + value + '</div>';
                            }}
                        }}
                    }}
                }}
            }} catch(e) {{
                console.log('Failed to parse task data');
            }}
        }})();
    </script>
</body>
</html>
"""

UPLOAD_RESULT_PAGE_WITH_MESSAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Configuration Preview - Label Studio</title>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif; background: #f5f7fa; color: #333; }}
        .navbar {{ background: #1a1a2e; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; }}
        .navbar-brand {{ color: #fff; font-size: 1.5rem; font-weight: bold; text-decoration: none; }}
        .navbar-nav {{ display: flex; gap: 1.5rem; }}
        .navbar-nav a {{ color: #ccc; text-decoration: none; transition: color 0.2s; }}
        .navbar-nav a:hover {{ color: #fff; }}
        .container {{ max-width: 800px; margin: 0 auto; padding: 2rem; }}
        .page-header {{ margin-bottom: 2rem; }}
        .page-header h1 {{ font-size: 1.8rem; color: #1a1a2e; }}
        .alert {{ padding: 1rem; border-radius: 6px; margin-bottom: 1rem; }}
        .alert-success {{ background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
        .alert-info {{ background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }}
        .preview-box {{ background: #fff; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.08); }}
        .json-preview {{ background: #1a1a2e; color: #e0e0e0; padding: 1rem; border-radius: 6px; font-family: monospace; white-space: pre-wrap; word-break: break-all; margin-bottom: 1rem; }}
        .task-item {{ padding: 0.5rem; background: #f8f9fa; margin: 0.5rem 0; border-radius: 4px; }}
        .btn {{ display: inline-block; padding: 0.75rem 1.5rem; border-radius: 6px; text-decoration: none; font-weight: 500; transition: all 0.2s; }}
        .btn-secondary {{ background: #6c757d; color: #fff; }}
        .btn-secondary:hover {{ background: #5a6268; }}
    </style>
</head>
<body>
    <nav class="navbar">
        <a href="/" class="navbar-brand">Label Studio</a>
        <div class="navbar-nav">
            <a href="/projects">Projects</a>
            <a href="/projects/upload-example/">Upload Example</a>
            <a href="#">Documentation</a>
            <a href="#">Settings</a>
        </div>
    </nav>
    
    <div class="container">
        <div class="page-header">
            <h1>Configuration Preview</h1>
        </div>
        
        {result_message}
        
        <div class="preview-box">
            <h3>Task Data Structure</h3>
            <div class="json-preview" id="task-data">{json_data}</div>
            <h4>Rendered Preview:</h4>
            <div id="rendered-data"></div>
        </div>
        
        <a href="/projects/upload-example/" class="btn btn-secondary">Try Another Configuration</a>
    </div>
    
    <script type="text/javascript">
        (function() {{
            var jsonStr = document.getElementById('task-data').textContent;
            try {{
                var taskData = JSON.parse(jsonStr);
                var container = document.getElementById('rendered-data');
                if (taskData) {{
                    for (var key in taskData) {{
                        if (taskData.hasOwnProperty(key)) {{
                            var value = taskData[key];
                            if (typeof value === 'string') {{
                                container.innerHTML += '<div class="task-item"><strong>' + key + ':</strong> ' + value + '</div>';
                            }}
                        }}
                    }}
                }}
            }} catch(e) {{
                console.log('Failed to parse task data');
            }}
        }})();
    </script>
</body>
</html>
"""
