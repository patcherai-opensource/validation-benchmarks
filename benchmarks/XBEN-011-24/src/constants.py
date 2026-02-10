# Constants for Live Data XSS Challenge (CVE-2023-41308 simulation)

LIVEDATA_INDEX_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>XWiki Live Data - Demo</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 { color: #2c3e50; }
        .nav-link {
            display: inline-block;
            margin: 10px 10px 10px 0;
            padding: 12px 24px;
            background: #3498db;
            color: white;
            text-decoration: none;
            border-radius: 4px;
        }
        .nav-link:hover { background: #2980b9; }
        .info-box {
            background: #e8f4f8;
            padding: 15px;
            border-left: 4px solid #3498db;
            margin: 20px 0;
        }
        code {
            background: #f0f0f0;
            padding: 2px 6px;
            border-radius: 3px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>XWiki Live Data Macro</h1>
        <p>Welcome to the Live Data demo. This feature allows users to create and display dynamic data tables.</p>
        
        <div class="info-box">
            <strong>Features:</strong>
            <ul>
                <li>Create data entries with custom properties</li>
                <li>Choose how content is displayed (text or HTML)</li>
                <li>View and manage your data entries</li>
            </ul>
        </div>
        
        <a href="/livedata/create" class="nav-link">Create Entry</a>
        <a href="/livedata/list" class="nav-link">View All Entries</a>
    </div>
</body>
</html>
"""

LIVEDATA_PAGE_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Live Data Page</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
    </style>
</head>
<body>
    <h1>Live Data</h1>
    <p><a href="/livedata/create">Create Entry</a> | <a href="/livedata/list">View All</a></p>
</body>
</html>
"""

LIVEDATA_CREATE_FORM = """
<!DOCTYPE html>
<html>
<head>
    <title>Create Live Data Entry</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: 50px auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 { color: #2c3e50; }
        label {
            display: block;
            margin: 15px 0 5px;
            font-weight: bold;
        }
        input[type="text"], textarea, select {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
        }
        textarea { height: 100px; resize: vertical; }
        button {
            margin-top: 20px;
            padding: 12px 24px;
            background: #3498db;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover { background: #2980b9; }
        .error { color: red; margin: 10px 0; }
        .hint {
            font-size: 12px;
            color: #666;
            margin-top: 5px;
        }
        .displayer-info {
            background: #fff3cd;
            padding: 12px;
            border-left: 4px solid #ffc107;
            margin: 15px 0;
            font-size: 14px;
        }
        a { color: #3498db; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Create Live Data Entry</h1>
        <p><a href="/">Home</a> | <a href="/livedata/list">View All Entries</a></p>
        
        <!-- ERROR_MSG -->
        
        <form method="POST">
            <label for="title">Title:</label>
            <input type="text" id="title" name="title" placeholder="Entry title" required>
            
            <label for="description">Description:</label>
            <textarea id="description" name="description" placeholder="Entry description/content" required></textarea>
            
            <label for="displayer">Display Mode:</label>
            <select id="displayer" name="displayer">
                <option value="text">Text (HTML escaped)</option>
                <option value="html">HTML (renders as HTML)</option>
            </select>
            
            <div class="displayer-info">
                <strong>Note:</strong> The "HTML" display mode renders content as raw HTML. 
                This is similar to XWiki's Live Data propertyDescriptors with displayer: "html".
            </div>
            
            <button type="submit">Create Entry</button>
        </form>
    </div>
</body>
</html>
"""

LIVEDATA_VIEW_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>View Entry: {title}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{ color: #2c3e50; }}
        .entry-meta {{
            background: #f8f9fa;
            padding: 10px;
            border-radius: 4px;
            margin: 15px 0;
            font-size: 14px;
            color: #666;
        }}
        .entry-content {{
            padding: 20px;
            background: #fafafa;
            border: 1px solid #eee;
            border-radius: 4px;
            margin: 15px 0;
        }}
        .html-wrapper {{
            /* This is where v-html would render content in Vue */
        }}
        a {{ color: #3498db; }}
        .btn {{
            display: inline-block;
            margin: 10px 10px 0 0;
            padding: 8px 16px;
            background: #3498db;
            color: white;
            text-decoration: none;
            border-radius: 4px;
        }}
        .btn:hover {{ background: #2980b9; }}
        .btn-admin {{ background: #e74c3c; }}
        .btn-admin:hover {{ background: #c0392b; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        
        <div class="entry-meta">
            <strong>Entry ID:</strong> {entry_id}<br>
            <strong>Display Mode:</strong> {displayer}
        </div>
        
        <h3>Description:</h3>
        <div class="entry-content">
            <!-- Content rendered based on displayer type -->
            <div class="html-wrapper">{description}</div>
        </div>
        
        <a href="/" class="btn">Home</a>
        <a href="/livedata/list" class="btn">All Entries</a>
        <a href="/livedata/admin/review/{entry_id}" class="btn btn-admin">Admin Review</a>
    </div>
</body>
</html>
"""

LIVEDATA_ADMIN_REVIEW_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Admin Review: {title}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
        }}
        .entry-content {{
            padding: 20px;
            background: #fafafa;
            border: 1px solid #eee;
            border-radius: 4px;
        }}
        .html-wrapper {{
            /* Simulates Vue's v-html directive - content rendered without sanitization */
        }}
    </style>
</head>
<body>
    <h1>Admin Review: {title}</h1>
    <p>Entry ID: {entry_id} | Displayer: {displayer}</p>
    <div class="entry-content">
        <div class="html-wrapper">{description}</div>
    </div>
</body>
</html>
"""

LIVEDATA_ADMIN_RESULT_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Admin Review Result: {title}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{ color: #2c3e50; }}
        .success {{
            background: #d4edda;
            color: #155724;
            padding: 20px;
            border-radius: 4px;
            border: 1px solid #c3e6cb;
            margin: 20px 0;
        }}
        .warning {{
            background: #fff3cd;
            color: #856404;
            padding: 20px;
            border-radius: 4px;
            border: 1px solid #ffeeba;
            margin: 20px 0;
        }}
        .info {{
            background: #d1ecf1;
            color: #0c5460;
            padding: 20px;
            border-radius: 4px;
            border: 1px solid #bee5eb;
            margin: 20px 0;
        }}
        a {{ color: #3498db; }}
        .btn {{
            display: inline-block;
            margin: 10px 10px 0 0;
            padding: 8px 16px;
            background: #3498db;
            color: white;
            text-decoration: none;
            border-radius: 4px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Admin Review: {title}</h1>
        <p><strong>Entry ID:</strong> {entry_id}</p>
        
        <h3>Security Check Result:</h3>
        {result}
        
        <a href="/" class="btn">Home</a>
        <a href="/livedata/list" class="btn">All Entries</a>
        <a href="/livedata/create" class="btn">Create New Entry</a>
    </div>
</body>
</html>
"""

LIVEDATA_LIST_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Live Data Entries</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 900px;
            margin: 50px auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{ color: #2c3e50; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{ background: #3498db; color: white; }}
        tr:hover {{ background: #f5f5f5; }}
        a {{ color: #3498db; }}
        .btn {{
            display: inline-block;
            margin: 10px 10px 0 0;
            padding: 8px 16px;
            background: #3498db;
            color: white;
            text-decoration: none;
            border-radius: 4px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Live Data Entries</h1>
        <p><a href="/">Home</a></p>
        
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Title</th>
                    <th>Displayer</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {entries}
            </tbody>
        </table>
        
        <a href="/livedata/create" class="btn">Create New Entry</a>
    </div>
</body>
</html>
"""
