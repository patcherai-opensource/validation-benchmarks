INDEX_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Label Studio - Data Labeling Platform</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif; background: #f5f7fa; color: #333; }
        .header { background: #1a1a2e; padding: 15px 30px; display: flex; align-items: center; justify-content: space-between; }
        .header h1 { color: #fff; font-size: 24px; font-weight: 600; }
        .header nav a { color: #fff; text-decoration: none; margin-left: 30px; font-size: 14px; }
        .header nav a:hover { color: #4caf50; }
        .container { max-width: 1200px; margin: 0 auto; padding: 40px 20px; }
        .hero { text-align: center; padding: 60px 0; }
        .hero h2 { font-size: 36px; margin-bottom: 20px; color: #1a1a2e; }
        .hero p { font-size: 18px; color: #666; max-width: 600px; margin: 0 auto 30px; }
        .btn { display: inline-block; padding: 12px 30px; background: #4caf50; color: #fff; text-decoration: none; border-radius: 5px; font-weight: 500; transition: background 0.3s; }
        .btn:hover { background: #388e3c; }
        .features { display: grid; grid-template-columns: repeat(3, 1fr); gap: 30px; margin-top: 60px; }
        .feature { background: #fff; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .feature h3 { margin-bottom: 15px; color: #1a1a2e; }
        .feature p { color: #666; font-size: 14px; line-height: 1.6; }
        .quick-links { margin-top: 40px; text-align: center; }
        .quick-links a { margin: 0 15px; color: #4caf50; text-decoration: none; }
        .quick-links a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Label Studio</h1>
        <nav>
            <a href="/projects/">Projects</a>
            <a href="/api/projects/">API</a>
            <a href="#">Documentation</a>
        </nav>
    </div>
    <div class="container">
        <div class="hero">
            <h2>Open Source Data Labeling</h2>
            <p>Label Studio is an open source data labeling tool for labeling and exploring multiple types of data.</p>
            <a href="/projects/create/" class="btn">Create New Project</a>
        </div>
        <div class="features">
            <div class="feature">
                <h3>Multiple Data Types</h3>
                <p>Support for images, audio, text, time series, and more. Configure custom labeling interfaces with XML.</p>
            </div>
            <div class="feature">
                <h3>Machine Learning Integration</h3>
                <p>Connect your ML models for pre-annotations and active learning workflows.</p>
            </div>
            <div class="feature">
                <h3>Team Collaboration</h3>
                <p>Invite team members, assign tasks, and track annotation progress in real-time.</p>
            </div>
        </div>
        <div class="quick-links">
            <a href="/projects/">View Projects</a>
            <a href="/projects/upload-example/">Upload Example</a>
            <a href="/api/projects/">API Explorer</a>
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
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif; background: #f5f7fa; color: #333; }
        .header { background: #1a1a2e; padding: 15px 30px; display: flex; align-items: center; justify-content: space-between; }
        .header h1 { color: #fff; font-size: 24px; font-weight: 600; }
        .header nav a { color: #fff; text-decoration: none; margin-left: 30px; font-size: 14px; }
        .container { max-width: 1200px; margin: 0 auto; padding: 40px 20px; }
        h2 { margin-bottom: 30px; }
        .project-list { display: grid; gap: 20px; }
        .project { background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); display: flex; justify-content: space-between; align-items: center; }
        .project h3 { font-size: 18px; margin-bottom: 5px; }
        .project p { color: #666; font-size: 14px; }
        .project .tasks { color: #4caf50; font-weight: 500; }
        .btn { padding: 10px 20px; background: #4caf50; color: #fff; text-decoration: none; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Label Studio</h1>
        <nav>
            <a href="/">Home</a>
            <a href="/projects/">Projects</a>
            <a href="/api/projects/">API</a>
        </nav>
    </div>
    <div class="container">
        <h2>Your Projects</h2>
        <div class="project-list">
            <div class="project">
                <div>
                    <h3>Text Classification</h3>
                    <p>Sentiment analysis for customer reviews</p>
                </div>
                <span class="tasks">150 tasks</span>
            </div>
            <div class="project">
                <div>
                    <h3>Image Labeling</h3>
                    <p>Object detection in product images</p>
                </div>
                <span class="tasks">89 tasks</span>
            </div>
            <div class="project">
                <div>
                    <h3>NER Annotation</h3>
                    <p>Named entity recognition in documents</p>
                </div>
                <span class="tasks">243 tasks</span>
            </div>
        </div>
        <div style="margin-top: 30px;">
            <a href="/projects/create/" class="btn">Create New Project</a>
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
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif; background: #f5f7fa; color: #333; }
        .header { background: #1a1a2e; padding: 15px 30px; display: flex; align-items: center; justify-content: space-between; }
        .header h1 { color: #fff; font-size: 24px; font-weight: 600; }
        .header nav a { color: #fff; text-decoration: none; margin-left: 30px; font-size: 14px; }
        .container { max-width: 800px; margin: 0 auto; padding: 40px 20px; }
        h2 { margin-bottom: 30px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; font-weight: 500; }
        input[type="text"], textarea { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 5px; font-size: 14px; }
        textarea { min-height: 150px; font-family: monospace; }
        .btn { padding: 12px 30px; background: #4caf50; color: #fff; border: none; border-radius: 5px; cursor: pointer; font-size: 14px; }
        .btn:hover { background: #388e3c; }
        .help-text { font-size: 12px; color: #666; margin-top: 5px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Label Studio</h1>
        <nav>
            <a href="/">Home</a>
            <a href="/projects/">Projects</a>
            <a href="/api/projects/">API</a>
        </nav>
    </div>
    <div class="container">
        <h2>Create New Project</h2>
        <form method="POST" action="/projects/create/">
            <div class="form-group">
                <label for="name">Project Name</label>
                <input type="text" id="name" name="name" placeholder="Enter project name">
            </div>
            <div class="form-group">
                <label for="description">Description</label>
                <input type="text" id="description" name="description" placeholder="Brief description of your project">
            </div>
            <div class="form-group">
                <label for="label_config">Labeling Configuration (XML)</label>
                <textarea id="label_config" name="label_config" placeholder="<View>&#10;  <Text name=&quot;text&quot; value=&quot;$text&quot;/>&#10;  <Choices name=&quot;sentiment&quot; toName=&quot;text&quot;>&#10;    <Choice value=&quot;positive&quot;/>&#10;    <Choice value=&quot;negative&quot;/>&#10;  </Choices>&#10;</View>"></textarea>
                <p class="help-text">Define the labeling interface using Label Studio XML format</p>
            </div>
            <button type="submit" class="btn">Create Project</button>
        </form>
        <p style="margin-top: 20px; font-size: 14px;">
            Need to test your config first? <a href="/projects/upload-example/">Try Upload Example</a>
        </p>
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
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif; background: #f5f7fa; color: #333; }
        .header { background: #1a1a2e; padding: 15px 30px; display: flex; align-items: center; justify-content: space-between; }
        .header h1 { color: #fff; font-size: 24px; font-weight: 600; }
        .header nav a { color: #fff; text-decoration: none; margin-left: 30px; font-size: 14px; }
        .container { max-width: 900px; margin: 0 auto; padding: 40px 20px; }
        h2 { margin-bottom: 10px; }
        .subtitle { color: #666; margin-bottom: 30px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; font-weight: 500; }
        textarea { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 5px; font-size: 14px; font-family: monospace; min-height: 200px; }
        .btn { padding: 12px 30px; background: #4caf50; color: #fff; border: none; border-radius: 5px; cursor: pointer; font-size: 14px; }
        .btn:hover { background: #388e3c; }
        .help-text { font-size: 12px; color: #666; margin-top: 5px; }
        .example-box { background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 30px; }
        .example-box h3 { margin-bottom: 15px; font-size: 16px; }
        .example-box pre { background: #f8f9fa; padding: 15px; border-radius: 5px; overflow-x: auto; font-size: 13px; }
        #response { margin-top: 20px; padding: 15px; background: #fff; border-radius: 5px; display: none; }
        #response pre { white-space: pre-wrap; word-wrap: break-word; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Label Studio</h1>
        <nav>
            <a href="/">Home</a>
            <a href="/projects/">Projects</a>
            <a href="/api/projects/">API</a>
        </nav>
    </div>
    <div class="container">
        <h2>Upload Example Using Config</h2>
        <p class="subtitle">Test your labeling configuration by uploading sample data. The system will parse your config and generate sample task data.</p>
        
        <div class="example-box">
            <h3>Example Configuration</h3>
            <pre>&lt;View&gt;
  &lt;Text name="text" value="$text"/&gt;
  &lt;Choices name="sentiment" toName="text"&gt;
    &lt;Choice value="positive"/&gt;
    &lt;Choice value="negative"/&gt;
    &lt;Choice value="neutral"/&gt;
  &lt;/Choices&gt;
&lt;/View&gt;</pre>
        </div>
        
        <form method="POST" action="/projects/upload-example/" id="uploadForm">
            <div class="form-group">
                <label for="label_config">Label Configuration (XML)</label>
                <textarea id="label_config" name="label_config" placeholder="Enter your labeling configuration XML here..."></textarea>
                <p class="help-text">The configuration will be parsed and sample task data will be generated based on the defined interface.</p>
            </div>
            <button type="submit" class="btn">Generate Sample Data</button>
        </form>
        
        <div id="response">
            <h3>Response:</h3>
            <pre id="responseContent"></pre>
        </div>
    </div>
    
    <script>
        document.getElementById('uploadForm').addEventListener('submit', function(e) {
            e.preventDefault();
            var formData = new FormData(this);
            fetch('/projects/upload-example/', {
                method: 'POST',
                body: formData
            })
            .then(response => response.text())
            .then(data => {
                document.getElementById('response').style.display = 'block';
                document.getElementById('responseContent').textContent = data;
            });
        });
    </script>
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
