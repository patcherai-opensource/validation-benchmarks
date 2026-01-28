# DataView Wiki - Collaborative Data Platform

INDEX_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>DataView Wiki - Collaborative Data Platform</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 20px;
            min-height: 100vh;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            padding: 40px;
        }
        h1 {
            color: #667eea;
            margin-bottom: 10px;
        }
        .subtitle {
            color: #666;
            margin-bottom: 30px;
        }
        .nav-links {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }
        .nav-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 6px;
            text-decoration: none;
            color: #333;
            border: 2px solid #e9ecef;
            transition: all 0.3s;
        }
        .nav-card:hover {
            border-color: #667eea;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(102,126,234,0.2);
        }
        .nav-card h3 {
            margin: 0 0 10px 0;
            color: #667eea;
        }
        .nav-card p {
            margin: 0;
            font-size: 14px;
            color: #666;
        }
        .footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e9ecef;
            color: #999;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>DataView Wiki</h1>
        <p class="subtitle">Collaborative data viewing and management platform</p>
        
        <div class="nav-links">
            <a href="/data/entries" class="nav-card">
                <h3>Data Entries</h3>
                <p>View and manage stored data entries</p>
            </a>
            <a href="/livedata" class="nav-card">
                <h3>Live Data</h3>
                <p>Create and preview live data tables</p>
            </a>
            <a href="/profile" class="nav-card">
                <h3>User Profile</h3>
                <p>Manage your account settings</p>
            </a>
            <a href="/api/status" class="nav-card">
                <h3>API Status</h3>
                <p>View API documentation and status</p>
            </a>
        </div>
        
        <div class="footer">
            DataView Wiki v2.3.1 | Powered by Flask | 2024
        </div>
    </div>
</body>
</html>
"""

LIVEDATA_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Live Data - DataView Wiki</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            padding: 40px;
        }}
        h1 {{
            color: #667eea;
            margin-bottom: 10px;
        }}
        .subtitle {{
            color: #666;
            margin-bottom: 20px;
        }}
        .form-section {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 6px;
            margin-bottom: 20px;
        }}
        .form-section h3 {{
            margin-top: 0;
            color: #333;
        }}
        label {{
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
            color: #333;
        }}
        input[type="text"], textarea, select {{
            width: 100%;
            padding: 10px;
            margin-bottom: 15px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
            box-sizing: border-box;
        }}
        textarea {{
            height: 100px;
            resize: vertical;
        }}
        button {{
            background: #667eea;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            transition: background 0.3s;
        }}
        button:hover {{
            background: #5a6fd6;
        }}
        .preview-section {{
            margin-top: 30px;
            padding: 20px;
            background: #fff;
            border: 2px solid #667eea;
            border-radius: 6px;
        }}
        .preview-section h3 {{
            color: #667eea;
            margin-top: 0;
        }}
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        .data-table th, .data-table td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        .data-table th {{
            background: #667eea;
            color: white;
        }}
        .data-table tr:hover {{
            background: #f5f5f5;
        }}
        .info-box {{
            background: #e7f1ff;
            border: 1px solid #b8daff;
            border-radius: 4px;
            padding: 15px;
            margin-bottom: 20px;
        }}
        .info-box p {{
            margin: 0;
            color: #004085;
        }}
        a {{
            color: #667eea;
        }}
        .back-link {{
            display: inline-block;
            margin-bottom: 20px;
        }}
        .result-box {{
            margin-top: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 6px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <a href="/" class="back-link">&larr; Back to Home</a>
        <h1>Live Data Macro</h1>
        <p class="subtitle">Create dynamic data tables with customizable display options</p>
        
        <div class="info-box">
            <p><strong>Note:</strong> The Live Data macro allows you to display data with different rendering modes. 
            Use the <code>displayer</code> option to control how cell content is rendered: 
            <code>text</code> for plain text or <code>html</code> for rich HTML content.</p>
        </div>
        
        <form method="POST" action="/livedata/render">
            <div class="form-section">
                <h3>Data Entry</h3>
                <label for="title">Title:</label>
                <input type="text" id="title" name="title" placeholder="Enter entry title...">
                
                <label for="content">Content:</label>
                <textarea id="content" name="content" placeholder="Enter content data..."></textarea>
                
                <label for="displayer">Display Mode:</label>
                <select id="displayer" name="displayer">
                    <option value="text">Text (Plain text rendering)</option>
                    <option value="html">HTML (Rich content rendering)</option>
                </select>
            </div>
            
            <button type="submit">Render Preview</button>
        </form>
        
        {0}
    </div>
</body>
</html>
"""

LIVEDATA_PREVIEW = """
<div class="preview-section">
    <h3>Live Data Preview</h3>
    <table class="data-table">
        <thead>
            <tr>
                <th>Property</th>
                <th>Value</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Title</td>
                <td>{0}</td>
            </tr>
            <tr>
                <td>Content</td>
                <td>{1}</td>
            </tr>
        </tbody>
    </table>
    <div class="result-box">
        {2}
    </div>
</div>
"""

DATA_ENTRIES_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Data Entries - DataView Wiki</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 20px;
            min-height: 100vh;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            padding: 40px;
        }
        h1 { color: #667eea; }
        .data-list {
            list-style: none;
            padding: 0;
        }
        .data-item {
            padding: 15px;
            background: #f8f9fa;
            margin-bottom: 10px;
            border-radius: 6px;
            border-left: 4px solid #667eea;
        }
        .data-item h4 {
            margin: 0 0 5px 0;
            color: #333;
        }
        .data-item p {
            margin: 0;
            color: #666;
            font-size: 14px;
        }
        a { color: #667eea; }
        .back-link { display: inline-block; margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <a href="/" class="back-link">&larr; Back to Home</a>
        <h1>Data Entries</h1>
        <p>Browse stored data entries in the wiki.</p>
        
        <ul class="data-list">
            <li class="data-item">
                <h4>Product Catalog</h4>
                <p>Last modified: 2024-01-15 | Entries: 156</p>
            </li>
            <li class="data-item">
                <h4>User Directory</h4>
                <p>Last modified: 2024-01-14 | Entries: 42</p>
            </li>
            <li class="data-item">
                <h4>Configuration Settings</h4>
                <p>Last modified: 2024-01-10 | Entries: 23</p>
            </li>
        </ul>
        
        <p><a href="/livedata">Create new Live Data table &rarr;</a></p>
    </div>
</body>
</html>
"""

PROFILE_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>User Profile - DataView Wiki</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 20px;
            min-height: 100vh;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            padding: 40px;
        }
        h1 { color: #667eea; }
        .profile-info {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 6px;
        }
        .profile-info p { margin: 10px 0; }
        .profile-info strong { color: #333; }
        a { color: #667eea; }
        .back-link { display: inline-block; margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <a href="/" class="back-link">&larr; Back to Home</a>
        <h1>User Profile</h1>
        
        <div class="profile-info">
            <p><strong>Username:</strong> guest</p>
            <p><strong>Role:</strong> Viewer</p>
            <p><strong>Joined:</strong> 2024-01-01</p>
            <p><strong>Script Rights:</strong> Disabled</p>
        </div>
        
        <p style="margin-top: 20px; color: #666; font-size: 14px;">
            Note: Script rights are required for some advanced features.
            Contact an administrator to request elevated permissions.
        </p>
    </div>
</body>
</html>
"""

API_STATUS_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>API Status - DataView Wiki</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 20px;
            min-height: 100vh;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            padding: 40px;
        }
        h1 { color: #667eea; }
        .endpoint {
            background: #f8f9fa;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 6px;
            font-family: monospace;
        }
        .method {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 12px;
            margin-right: 10px;
        }
        .get { background: #28a745; color: white; }
        .post { background: #007bff; color: white; }
        code {
            background: #e9ecef;
            padding: 2px 6px;
            border-radius: 3px;
        }
        a { color: #667eea; }
        .back-link { display: inline-block; margin-bottom: 20px; }
        .status-ok { color: #28a745; }
    </style>
</head>
<body>
    <div class="container">
        <a href="/" class="back-link">&larr; Back to Home</a>
        <h1>API Status</h1>
        <p><span class="status-ok">&#10003;</span> All systems operational</p>
        
        <h3>Available Endpoints</h3>
        
        <div class="endpoint">
            <span class="method get">GET</span>
            <code>/</code> - Home page
        </div>
        <div class="endpoint">
            <span class="method get">GET</span>
            <code>/data/entries</code> - List data entries
        </div>
        <div class="endpoint">
            <span class="method get">GET</span>
            <span class="method post">POST</span>
            <code>/livedata</code> - Live Data macro interface
        </div>
        <div class="endpoint">
            <span class="method post">POST</span>
            <code>/livedata/render</code> - Render live data preview
        </div>
        <div class="endpoint">
            <span class="method get">GET</span>
            <code>/profile</code> - User profile
        </div>
        <div class="endpoint">
            <span class="method get">GET</span>
            <code>/api/status</code> - This page
        </div>
        
        <h3>Configuration</h3>
        <p>Server: Flask 1.1.4</p>
        <p>Renderer: PhantomJS (headless browser for content preview)</p>
    </div>
</body>
</html>
"""

ABOUT_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>About - DataView Wiki</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 20px;
            min-height: 100vh;
        }
        .container {
            max-width: 700px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            padding: 40px;
        }
        h1 { color: #667eea; }
        a { color: #667eea; }
        .back-link { display: inline-block; margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <a href="/" class="back-link">&larr; Back to Home</a>
        <h1>About DataView Wiki</h1>
        
        <p>DataView Wiki is a collaborative platform for viewing and managing structured data. 
        It provides powerful features for data visualization including the Live Data macro 
        for creating dynamic, interactive tables.</p>
        
        <h3>Key Features</h3>
        <ul>
            <li>Live Data macro for dynamic content rendering</li>
            <li>Multiple display modes (text, HTML)</li>
            <li>Collaborative editing capabilities</li>
            <li>Role-based access control</li>
        </ul>
        
        <h3>Version History</h3>
        <ul>
            <li><strong>v2.3.1</strong> - Security improvements to content rendering</li>
            <li><strong>v2.3.0</strong> - Added HTML displayer mode for rich content</li>
            <li><strong>v2.2.0</strong> - Live Data macro enhancements</li>
        </ul>
    </div>
</body>
</html>
"""
