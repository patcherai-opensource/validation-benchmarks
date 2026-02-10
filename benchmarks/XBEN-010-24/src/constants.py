INDEX_CONTENT = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <title>Label Studio</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #1a1a2e; color: #eee; }
                .container { max-width: 800px; margin: 0 auto; text-align: center; }
                h1 { color: #00d4ff; }
                .nav-card { background: #16213e; padding: 30px; border-radius: 10px; margin: 20px; display: inline-block; }
                .nav-card a { color: #00d4ff; text-decoration: none; font-size: 18px; }
                .nav-card:hover { background: #0f3460; }
                .nav-card img { width: 100px; height: 100px; margin-bottom: 10px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Label Studio</h1>
                <p>Welcome to Label Studio - Data Labeling Platform</p>
                <div class="nav-card">
                    <a href="/projects/upload-example/">
                        <img src="static/img/cookies/new_star.png" alt="Upload">
                        <br>Upload Example
                    </a>
                </div>
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

# Label Studio upload-example templates (for CVE vulnerability simulation)

UPLOAD_EXAMPLE_FORM = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <title>Label Studio - Upload Example</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #1a1a2e; color: #eee; }
                .container { max-width: 800px; margin: 0 auto; }
                h1 { color: #00d4ff; }
                textarea { width: 100%; height: 200px; margin: 10px 0; background: #16213e; color: #eee; border: 1px solid #0f3460; padding: 10px; font-family: monospace; }
                input[type="submit"] { background: #00d4ff; color: #1a1a2e; border: none; padding: 10px 30px; cursor: pointer; font-size: 16px; }
                input[type="submit"]:hover { background: #00a8cc; }
                .description { background: #16213e; padding: 20px; border-radius: 5px; margin: 20px 0; }
                code { background: #0f3460; padding: 2px 6px; border-radius: 3px; }
                pre { background: #0f3460; padding: 15px; border-radius: 5px; overflow-x: auto; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Label Studio - Upload Example Configuration</h1>
                <div class="description">
                    <p>This endpoint allows you to upload a label configuration and preview sample task data.</p>
                    <p>The <code>label_config</code> parameter accepts XML configuration that defines labeling interfaces.</p>
                    <p>Example configuration:</p>
                    <pre>&lt;View&gt;
  &lt;Text name="text" value="$text"/&gt;
  &lt;Choices name="sentiment" toName="text"&gt;
    &lt;Choice value="Positive"/&gt;
    &lt;Choice value="Negative"/&gt;
  &lt;/Choices&gt;
&lt;/View&gt;</pre>
                </div>
                <form method="POST">
                    <label for="label_config">Label Configuration (XML):</label>
                    <textarea name="label_config" id="label_config" placeholder="Enter your XML label configuration here..."></textarea>
                    <br>
                    <input type="submit" value="Upload Configuration">
                </form>
            </div>
        </body>
    </html>
"""

UPLOAD_EXAMPLE_RESULT = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <title>Label Studio - Task Preview</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background: #1a1a2e; color: #eee; }}
                .container {{ max-width: 800px; margin: 0 auto; }}
                h1 {{ color: #00d4ff; }}
                .task-data {{ background: #16213e; padding: 20px; border-radius: 5px; margin: 20px 0; }}
                .preview {{ background: #0f3460; padding: 20px; border-radius: 5px; margin: 20px 0; }}
                a {{ color: #00d4ff; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Label Studio - Sample Task Data</h1>
                <div class="task-data">
                    <h3>Extracted Task Data (JSON):</h3>
                    <pre>{0}</pre>
                </div>
                <div class="preview">
                    <h3>Task Preview:</h3>
                    <div id="task-preview"></div>
                </div>
                <script>
                    // VULNERABLE: Unsafely rendering JSON data into the DOM
                    var taskData = {0};
                    var previewDiv = document.getElementById('task-preview');
                    for (var key in taskData) {{
                        // SINK: innerHTML assignment without proper escaping
                        previewDiv.innerHTML += '<p><strong>' + key + ':</strong> ' + taskData[key] + '</p>';
                    }}
                </script>
                <p><a href="/projects/upload-example/">Try another configuration</a></p>
            </div>
        </body>
    </html>
"""

UPLOAD_EXAMPLE_SUCCESS = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <title>Label Studio - Success!</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background: #1a1a2e; color: #eee; }}
                .container {{ max-width: 800px; margin: 0 auto; }}
                h1 {{ color: #00ff00; }}
                .success {{ background: #16213e; padding: 20px; border-radius: 5px; margin: 20px 0; border: 2px solid #00ff00; }}
                .flag {{ font-family: monospace; font-size: 24px; color: #00ff00; background: #0f3460; padding: 15px; border-radius: 5px; }}
                a {{ color: #00d4ff; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Congratulations! XSS Successful!</h1>
                <div class="success">
                    <p>You have successfully exploited the reflected XSS vulnerability!</p>
                    <p class="flag">{0}</p>
                </div>
                <div class="task-data">
                    <h3>Task Data that triggered XSS:</h3>
                    <pre>{1}</pre>
                </div>
                <p><a href="/projects/upload-example/">Try again</a></p>
            </div>
        </body>
    </html>
"""
