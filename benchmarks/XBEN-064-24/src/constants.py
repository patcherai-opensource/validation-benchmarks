# Constants for Label Studio simulation
# These are kept for compatibility but may not all be used

INDEX_CONTENT = """
    <html>
        <head>
            <title>Label Studio</title>
        </head>
        <body>
            <h1>Label Studio - Data Labeling Tool</h1>
        </body>
    </html>
"""

# Image routes - kept for compatibility
IMAGE_ROUTES = {
    "xss_easy": {
        "start": "static/img/cookies/new_circle.png",
        "process": "static/img/cookies/error_circle.png",
        "error": "static/img/cookies/error_circle.png",
        "success": "static/img/cookies/success_circle.png"
    }
}
