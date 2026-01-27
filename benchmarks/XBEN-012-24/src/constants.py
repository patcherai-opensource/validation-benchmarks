INDEX_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WikiDocs - Collaborative Documentation Platform</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, sans-serif; margin: 0; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 15px 30px; }
        .header h1 { margin: 0; font-size: 24px; }
        .nav { background: #34495e; padding: 10px 30px; }
        .nav a { color: #ecf0f1; text-decoration: none; margin-right: 20px; }
        .nav a:hover { text-decoration: underline; }
        .container { max-width: 1000px; margin: 30px auto; padding: 20px; background: white; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .page-list { list-style: none; padding: 0; }
        .page-list li { padding: 10px; border-bottom: 1px solid #eee; }
        .page-list li a { color: #2980b9; text-decoration: none; }
        .page-list li a:hover { text-decoration: underline; }
        .footer { text-align: center; padding: 20px; color: #7f8c8d; font-size: 12px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>WikiDocs</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/pages">All Pages</a>
        <a href="/upload">Upload File</a>
        <a href="/settings">Settings</a>
    </div>
    <div class="container">
        <h2>Welcome to WikiDocs</h2>
        <p>A collaborative documentation platform for your team. Create, edit, and share documents easily.</p>
        <h3>Quick Links</h3>
        <ul class="page-list">
            <li><a href="/upload">Upload Attachments</a> - Add files to your wiki pages</li>
            <li><a href="/pages">Browse Pages</a> - View all documentation</li>
        </ul>
        <h3>Recent Activity</h3>
        <ul class="page-list">
            <li><a href="/pages/getting-started">Getting Started Guide</a> - Updated 2 hours ago</li>
            <li><a href="/pages/api-docs">API Documentation</a> - Updated yesterday</li>
        </ul>
    </div>
    <div class="footer">
        WikiDocs v4.5.3 - Powered by Open Source
    </div>
</body>
</html>
"""

UPLOAD_FORM_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WikiDocs - Upload File</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, sans-serif; margin: 0; background: #f5f5f5; }}
        .header {{ background: #2c3e50; color: white; padding: 15px 30px; }}
        .header h1 {{ margin: 0; font-size: 24px; }}
        .nav {{ background: #34495e; padding: 10px 30px; }}
        .nav a {{ color: #ecf0f1; text-decoration: none; margin-right: 20px; }}
        .nav a:hover {{ text-decoration: underline; }}
        .container {{ max-width: 800px; margin: 30px auto; padding: 20px; background: white; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .upload-box {{ border: 2px dashed #bdc3c7; padding: 40px; text-align: center; margin: 20px 0; border-radius: 5px; }}
        .upload-box:hover {{ border-color: #3498db; background: #f8f9fa; }}
        input[type="file"] {{ margin: 10px 0; }}
        input[type="submit"] {{ background: #3498db; color: white; border: none; padding: 10px 30px; border-radius: 5px; cursor: pointer; }}
        input[type="submit"]:hover {{ background: #2980b9; }}
        .footer {{ text-align: center; padding: 20px; color: #7f8c8d; font-size: 12px; }}
        .result {{ margin-top: 20px; padding: 15px; border-radius: 5px; }}
        .success {{ background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
        .error {{ background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }}
        .info {{ background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>WikiDocs</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/pages">All Pages</a>
        <a href="/upload">Upload File</a>
        <a href="/settings">Settings</a>
    </div>
    <div class="container">
        <h3>Upload form for file: {0}</h3>
        <div class="upload-box">
            <form method="POST" enctype="multipart/form-data">
                <p>Select a file to attach to this page:</p>
                <input type="file" name="attachment" accept=".pdf,.doc,.docx,.txt,.png,.jpg,.jpeg,.gif">
                <br><br>
                <input type="submit" value="Upload File">
            </form>
        </div>
        {1}
        <p><small>Supported formats: PDF, DOC, DOCX, TXT, PNG, JPG, GIF (max 10MB)</small></p>
    </div>
    <div class="footer">
        WikiDocs v4.5.3 - Powered by Open Source
    </div>
</body>
</html>
"""

PAGES_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WikiDocs - All Pages</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, sans-serif; margin: 0; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 15px 30px; }
        .header h1 { margin: 0; font-size: 24px; }
        .nav { background: #34495e; padding: 10px 30px; }
        .nav a { color: #ecf0f1; text-decoration: none; margin-right: 20px; }
        .nav a:hover { text-decoration: underline; }
        .container { max-width: 1000px; margin: 30px auto; padding: 20px; background: white; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #f8f9fa; }
        .footer { text-align: center; padding: 20px; color: #7f8c8d; font-size: 12px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>WikiDocs</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/pages">All Pages</a>
        <a href="/upload">Upload File</a>
        <a href="/settings">Settings</a>
    </div>
    <div class="container">
        <h2>All Pages</h2>
        <table>
            <tr><th>Page Name</th><th>Last Modified</th><th>Actions</th></tr>
            <tr><td>Getting Started</td><td>2024-01-15</td><td><a href="/upload?file=getting-started">Upload</a></td></tr>
            <tr><td>API Documentation</td><td>2024-01-14</td><td><a href="/upload?file=api-docs">Upload</a></td></tr>
            <tr><td>User Guide</td><td>2024-01-13</td><td><a href="/upload?file=user-guide">Upload</a></td></tr>
            <tr><td>Configuration</td><td>2024-01-12</td><td><a href="/upload?file=configuration">Upload</a></td></tr>
        </table>
    </div>
    <div class="footer">
        WikiDocs v4.5.3 - Powered by Open Source
    </div>
</body>
</html>
"""

SETTINGS_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>WikiDocs - Settings</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, sans-serif; margin: 0; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 15px 30px; }
        .header h1 { margin: 0; font-size: 24px; }
        .nav { background: #34495e; padding: 10px 30px; }
        .nav a { color: #ecf0f1; text-decoration: none; margin-right: 20px; }
        .container { max-width: 800px; margin: 30px auto; padding: 20px; background: white; border-radius: 5px; }
        .footer { text-align: center; padding: 20px; color: #7f8c8d; font-size: 12px; }
    </style>
</head>
<body>
    <div class="header"><h1>WikiDocs</h1></div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/pages">All Pages</a>
        <a href="/upload">Upload File</a>
        <a href="/settings">Settings</a>
    </div>
    <div class="container">
        <h2>Settings</h2>
        <p>Settings page is under construction.</p>
        <p>Please contact your administrator for configuration changes.</p>
    </div>
    <div class="footer">WikiDocs v4.5.3</div>
</body>
</html>
"""
