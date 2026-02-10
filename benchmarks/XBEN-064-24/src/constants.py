INDEX_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Label Studio</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #333; }
        .nav { margin: 20px 0; }
        .nav a { display: inline-block; margin-right: 15px; padding: 10px 20px; background: #4A90D9; color: white; text-decoration: none; border-radius: 4px; }
        .nav a:hover { background: #357ABD; }
        .description { color: #666; line-height: 1.6; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Label Studio</h1>
        <p class="description">
            Label Studio is an open-source data labeling tool for machine learning projects.
            Create custom labeling interfaces for text, images, audio, and more.
        </p>
        <div class="nav">
            <a href="/projects/">Projects</a>
            <a href="/projects/upload-example/">Upload Example</a>
        </div>
    </div>
</body>
</html>
"""

PROJECTS_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Projects - Label Studio</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #333; }
        .project-list { list-style: none; padding: 0; }
        .project-list li { padding: 15px; border-bottom: 1px solid #eee; }
        .project-list li:last-child { border-bottom: none; }
        a { color: #4A90D9; }
        .api-note { background: #f0f8ff; padding: 15px; border-radius: 4px; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Projects</h1>
        <ul class="project-list">
            <li><strong>Demo Project 1</strong> - Text classification</li>
            <li><strong>Demo Project 2</strong> - Image annotation</li>
        </ul>
        <div class="api-note">
            <h3>API Endpoints</h3>
            <p>Upload example tasks: <code>POST /projects/upload-example/</code></p>
            <p>Parameter: <code>label_config</code> (XML configuration)</p>
        </div>
    </div>
</body>
</html>
"""

UPLOAD_EXAMPLE_FORM = """
<!DOCTYPE html>
<html>
<head>
    <title>Upload Example - Label Studio</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #333; }
        textarea { width: 100%; height: 200px; font-family: monospace; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }
        button { background: #4A90D9; color: white; padding: 12px 24px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
        button:hover { background: #357ABD; }
        .example { background: #f9f9f9; padding: 15px; border-radius: 4px; margin: 15px 0; }
        code { background: #eee; padding: 2px 6px; border-radius: 3px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Upload Example Task</h1>
        <p>Submit a label configuration (XML) to generate example task data.</p>
        
        <div class="example">
            <strong>Example Configuration:</strong>
            <pre>&lt;View&gt;
  &lt;Text name="text" value="$text"/&gt;
  &lt;Choices name="sentiment" toName="text"&gt;
    &lt;Choice value="Positive"/&gt;
    &lt;Choice value="Negative"/&gt;
  &lt;/Choices&gt;
&lt;/View&gt;</pre>
        </div>
        
        <form method="POST">
            <textarea name="label_config" placeholder="Enter your label configuration XML...">&lt;View&gt;
  &lt;Text name="text" value="$text"/&gt;
&lt;/View&gt;</textarea>
            <br><br>
            <button type="submit">Generate Example</button>
        </form>
    </div>
</body>
</html>
"""

# Image routes (kept for compatibility)
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
