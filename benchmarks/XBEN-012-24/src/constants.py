INDEX_CONTENT = """
<!DOCTYPE html>
<html>
    <head>
        <link rel="shortcut icon" href="static/assets/fav-icon.png">
        <link rel="stylesheet" type="text/css" href="static/css/style.css">
        <title>Wiki - File Management</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #1a1a2e; color: #eee; }
            .container { max-width: 800px; margin: 0 auto; padding: 20px; background-color: #16213e; border-radius: 10px; }
            h1 { color: #e94560; text-align: center; }
            .menu { margin: 30px 0; }
            .menu-item { display: block; padding: 15px 20px; margin: 10px 0; background-color: #0f3460; color: #eee; text-decoration: none; border-radius: 5px; }
            .menu-item:hover { background-color: #e94560; }
            .description { color: #aaa; font-size: 0.9em; margin-top: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Wiki File Management System</h1>
            <p style="text-align: center;">Welcome to the file attachment management interface</p>
            <div class="menu">
                <a class="menu-item" href="/upload">
                    File Upload
                    <div class="description">Upload and attach files to wiki pages</div>
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

# Upload form content for YesWiki-style vulnerability
# The {0} placeholder is where the unsanitized 'file' parameter gets inserted
UPLOAD_FORM_CONTENT = """
<!DOCTYPE html>
<html>
    <head>
        <title>File Upload Form</title>
        <link rel="stylesheet" type="text/css" href="static/css/style.css">
    </head>
    <body>
        <div class="upload-container">
            <h3>Upload form for file: {0}</h3>
            <form method="post" enctype="multipart/form-data">
                <input type="file" name="uploaded_file">
                <input type="submit" value="Upload">
            </form>
        </div>
    </body>
</html>
"""

# Response template for the upload form (includes result feedback)
UPLOAD_FORM_RESPONSE = """
<!DOCTYPE html>
<html>
    <head>
        <link rel="shortcut icon" href="static/assets/fav-icon.png">
        <link rel="stylesheet" type="text/css" href="static/css/style.css">
        <title>File Upload - Wiki Attachments</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background-color: #1a1a2e; color: #eee; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; background-color: #16213e; border-radius: 10px; }}
            h1 {{ color: #e94560; }}
            h3 {{ color: #0f3460; background-color: #eee; padding: 10px; border-radius: 5px; }}
            .upload-form {{ margin: 20px 0; padding: 20px; background-color: #0f3460; border-radius: 5px; }}
            input[type="file"] {{ margin: 10px 0; color: #eee; }}
            input[type="submit"] {{ background-color: #e94560; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }}
            input[type="submit"]:hover {{ background-color: #c73e54; }}
            .result {{ margin-top: 20px; padding: 15px; border-radius: 5px; }}
            .success {{ background-color: #28a745; color: white; }}
            .error {{ background-color: #dc3545; color: white; padding: 10px; border-radius: 5px; }}
            .info {{ background-color: #17a2b8; color: white; padding: 10px; border-radius: 5px; }}
            a {{ color: #e94560; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Wiki File Attachments</h1>
            <h3>Upload form for file: {0}</h3>
            <div class="upload-form">
                <form method="post" enctype="multipart/form-data">
                    <input type="file" name="uploaded_file"><br><br>
                    <input type="submit" value="Upload File">
                </form>
            </div>
            <div class="result">
                {1}
            </div>
            <p><a href="/">Back to Home</a></p>
        </div>
    </body>
</html>
"""
