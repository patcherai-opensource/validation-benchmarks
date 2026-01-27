INDEX_CONTENT = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <title>Label Studio - Data Labeling Platform</title>
        </head>
        <body style="background: #1a1a2e; color: white; font-family: Arial, sans-serif;">
            <div style="max-width: 800px; margin: 50px auto; padding: 20px; text-align: center;">
                <h1>Label Studio</h1>
                <p>Open Source Data Labeling Platform</p>
                <div style="margin: 30px 0;">
                    <a href="/projects/upload-example/" style="display: inline-block; padding: 15px 30px; background: #4a4a6a; color: white; text-decoration: none; border-radius: 5px; margin: 10px;">Upload Example Config</a>
                </div>
                <div style="margin: 30px 0;">
                    <a href="/projects/" style="display: inline-block; padding: 15px 30px; background: #4a4a6a; color: white; text-decoration: none; border-radius: 5px; margin: 10px;">View Projects</a>
                </div>
                <p><small>Version 1.17.0</small></p>
            </div>
        </body>
    </html>
"""

# Template for the upload config page
UPLOAD_CONFIG_PAGE = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <title>Label Studio - Upload Example Configuration</title>
        </head>
        <body style="background: #1a1a2e; color: white; font-family: Arial, sans-serif;">
            <div style="max-width: 900px; margin: 50px auto; padding: 20px;">
                <h1>Upload Label Configuration</h1>
                <p>Submit your XML label configuration to preview example task data.</p>
                {result_section}
                <form method="post" style="margin: 20px 0;">
                    <label for="label_config">Label Configuration (XML):</label><br>
                    <textarea name="label_config" id="label_config" cols="80" rows="15" 
                        placeholder='<View>
  <Text name="text" value="$text"/>
  <Choices name="sentiment" toName="text">
    <Choice value="Positive"/>
    <Choice value="Negative"/>
  </Choices>
</View>'
                        style="background: #2a2a4a; color: white; border: 1px solid #4a4a6a; padding: 10px; font-family: monospace;">{config_value}</textarea>
                    <br><br>
                    <input type="submit" value="Generate Example" style="padding: 10px 30px; background: #4a4a6a; color: white; border: none; cursor: pointer; border-radius: 5px;">
                </form>
                {preview_section}
            </div>
        </body>
    </html>
"""

# Template for projects list page
PROJECTS_PAGE = """
    <html>
        <head>
            <link rel="shortcut icon" href="static/assets/fav-icon.png">
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <title>Label Studio - Projects</title>
        </head>
        <body style="background: #1a1a2e; color: white; font-family: Arial, sans-serif;">
            <div style="max-width: 900px; margin: 50px auto; padding: 20px;">
                <h1>Projects</h1>
                <p>No projects found. <a href="/projects/upload-example/" style="color: #7a7aaa;">Upload a configuration</a> to get started.</p>
                <div style="margin-top: 30px; padding: 20px; background: #2a2a4a; border-radius: 5px;">
                    <h3>Getting Started</h3>
                    <p>1. Navigate to <a href="/projects/upload-example/" style="color: #7a7aaa;">Upload Example Config</a></p>
                    <p>2. Enter your XML labeling configuration</p>
                    <p>3. Preview generated task data</p>
                </div>
            </div>
        </body>
    </html>
"""

# Image routes for XSS check results
IMAGE_ROUTES = {
    "label_studio": {
        "start": "static/img/cookies/new_star.png",
        "process": "static/img/cookies/error_star.png",
        "error": "static/img/cookies/error_star.png",
        "success": "static/img/cookies/success_star.png"
    }
}
