INDEX_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenRefine</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: #f5f5f5;
            margin: 0;
            padding: 0;
        }
        .header {
            background-color: #2196F3;
            color: white;
            padding: 15px 20px;
            display: flex;
            align-items: center;
        }
        .header h1 {
            margin: 0;
            font-size: 24px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .nav {
            background-color: white;
            border-bottom: 1px solid #ddd;
            padding: 10px 20px;
        }
        .nav a {
            color: #333;
            text-decoration: none;
            margin-right: 20px;
            padding: 5px 10px;
        }
        .nav a:hover {
            background-color: #f0f0f0;
            border-radius: 3px;
        }
        .card {
            background: white;
            border-radius: 4px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12);
            padding: 20px;
            margin-bottom: 20px;
        }
        .card h2 {
            margin-top: 0;
            color: #333;
        }
        .btn {
            display: inline-block;
            padding: 10px 20px;
            background-color: #2196F3;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            border: none;
            cursor: pointer;
        }
        .btn:hover {
            background-color: #1976D2;
        }
        .btn-secondary {
            background-color: #757575;
        }
        .btn-secondary:hover {
            background-color: #616161;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>OpenRefine</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/projects">Projects</a>
        <a href="/connect/google">Connect to Google</a>
    </div>
    <div class="container">
        <div class="card">
            <h2>Welcome to OpenRefine</h2>
            <p>OpenRefine is a powerful tool for working with messy data: cleaning it; transforming it from one format into another; and extending it with web services and external data.</p>
        </div>
        <div class="card">
            <h2>Extensions</h2>
            <p>The GData extension allows you to import data from Google Sheets and export refined data back to Google services.</p>
            <a href="/connect/google" class="btn">Connect Google Account</a>
        </div>
    </div>
</body>
</html>
"""

GOOGLE_CONNECT_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Connect Google Account - OpenRefine</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: #f5f5f5;
            margin: 0;
            padding: 0;
        }
        .header {
            background-color: #2196F3;
            color: white;
            padding: 15px 20px;
        }
        .header h1 {
            margin: 0;
            font-size: 24px;
        }
        .nav {
            background-color: white;
            border-bottom: 1px solid #ddd;
            padding: 10px 20px;
        }
        .nav a {
            color: #333;
            text-decoration: none;
            margin-right: 20px;
            padding: 5px 10px;
        }
        .container {
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
        }
        .card {
            background: white;
            border-radius: 4px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12);
            padding: 30px;
        }
        .card h2 {
            margin-top: 0;
            color: #333;
        }
        .google-btn {
            display: inline-flex;
            align-items: center;
            padding: 12px 24px;
            background-color: #4285f4;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            font-size: 16px;
            margin-top: 15px;
        }
        .google-btn:hover {
            background-color: #357abd;
        }
        .info {
            background-color: #e3f2fd;
            border-left: 4px solid #2196F3;
            padding: 15px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>OpenRefine</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/projects">Projects</a>
        <a href="/connect/google">Connect to Google</a>
    </div>
    <div class="container">
        <div class="card">
            <h2>Connect Your Google Account</h2>
            <p>Link your Google account to import data from Google Sheets and export your refined data.</p>
            <div class="info">
                <strong>Note:</strong> You will be redirected to Google to authorize OpenRefine to access your data. The callback URL will be <code>/extension/gdata/authorized</code>.
            </div>
            <p>After authorization, you'll be able to:</p>
            <ul>
                <li>Import spreadsheets from Google Sheets</li>
                <li>Export data to Google Sheets</li>
                <li>Access Google Drive files</li>
            </ul>
            <a href="#" class="google-btn" onclick="alert('Google OAuth is not configured for this demo instance'); return false;">
                Sign in with Google
            </a>
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
    <title>Projects - OpenRefine</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: #f5f5f5;
            margin: 0;
            padding: 0;
        }
        .header {
            background-color: #2196F3;
            color: white;
            padding: 15px 20px;
        }
        .header h1 {
            margin: 0;
            font-size: 24px;
        }
        .nav {
            background-color: white;
            border-bottom: 1px solid #ddd;
            padding: 10px 20px;
        }
        .nav a {
            color: #333;
            text-decoration: none;
            margin-right: 20px;
            padding: 5px 10px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        .card {
            background: white;
            border-radius: 4px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12);
            padding: 20px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            text-align: left;
            padding: 12px;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #f5f5f5;
        }
        .empty-state {
            text-align: center;
            padding: 40px;
            color: #757575;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>OpenRefine</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/projects">Projects</a>
        <a href="/connect/google">Connect to Google</a>
    </div>
    <div class="container">
        <div class="card">
            <h2>Your Projects</h2>
            <table>
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Modified</th>
                        <th>Rows</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td colspan="4" class="empty-state">
                            No projects found. Create a new project or import data to get started.
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""

OAUTH_CALLBACK_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Authorization - OpenRefine GData Extension</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: #f5f5f5;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }}
        .card {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 40px;
            max-width: 500px;
            text-align: center;
        }}
        .spinner {{
            border: 4px solid #f3f3f3;
            border-top: 4px solid #2196F3;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }}
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        .error {{
            color: #d32f2f;
            background-color: #ffebee;
            padding: 15px;
            border-radius: 4px;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="card">
        <h2>Processing Authorization</h2>
        <div class="spinner"></div>
        <p>Please wait while we complete the authorization process...</p>
        <script>
            var state = JSON.parse(window.atob("{state}"));
            var windowName = state.winname;
            var callbackName = state.cb;
            var error = "{error}";
            
            if (error) {{
                document.querySelector('.spinner').style.display = 'none';
                document.querySelector('p').innerHTML = '<div class="error">Authorization failed: ' + error + '</div>';
            }} else {{
                if (window.opener && window.opener[callbackName]) {{
                    window.opener[callbackName](state);
                }}
                setTimeout(function() {{
                    window.close();
                }}, 2000);
            }}
        </script>
    </div>
</body>
</html>
"""

OAUTH_SUCCESS_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Authorization Complete - OpenRefine</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: #f5f5f5;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }}
        .card {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 40px;
            max-width: 500px;
            text-align: center;
        }}
        .success {{
            color: #2e7d32;
            background-color: #e8f5e9;
            padding: 15px;
            border-radius: 4px;
            margin-top: 20px;
            word-break: break-all;
        }}
        .checkmark {{
            color: #4caf50;
            font-size: 48px;
        }}
    </style>
</head>
<body>
    <div class="card">
        <div class="checkmark">&#10004;</div>
        <h2>Authorization Complete</h2>
        <p>Your session has been verified.</p>
        <div class="success">{flag}</div>
    </div>
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
