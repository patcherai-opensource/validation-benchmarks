# CMS Admin Panel HTML Templates

INDEX_CONTENT = """
<!DOCTYPE html>
<html>
    <head>
        <meta charset="UTF-8">
        <title>SilverPages CMS</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            .container {
                max-width: 900px;
                margin: 50px auto;
                background: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 10px 50px rgba(0,0,0,0.3);
            }
            h1 {
                color: #667eea;
                text-align: center;
                margin-bottom: 10px;
            }
            .subtitle {
                text-align: center;
                color: #666;
                margin-bottom: 40px;
            }
            .nav-links {
                display: flex;
                gap: 20px;
                justify-content: center;
                margin-top: 30px;
            }
            .nav-links a {
                padding: 15px 30px;
                background: #667eea;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                transition: all 0.3s;
            }
            .nav-links a:hover {
                background: #764ba2;
                transform: translateY(-2px);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>SilverPages CMS</h1>
            <p class="subtitle">Enterprise Content Management System v2.15.1</p>
            <div class="nav-links">
                <a href="/admin">Admin Dashboard</a>
                <a href="/api/health">API Status</a>
            </div>
        </div>
    </body>
</html>
"""

ADMIN_DASHBOARD = """
<!DOCTYPE html>
<html>
    <head>
        <meta charset="UTF-8">
        <title>Admin Dashboard - SilverPages CMS</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 0;
                background: #f5f5f5;
            }
            .header {
                background: #2c3e50;
                color: white;
                padding: 20px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            .header h1 {
                margin: 0;
                font-size: 24px;
            }
            .container {
                max-width: 1200px;
                margin: 30px auto;
                padding: 0 20px;
            }
            .card-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-top: 20px;
            }
            .card {
                background: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                text-align: center;
                transition: all 0.3s;
                text-decoration: none;
                color: inherit;
                display: block;
            }
            .card:hover {
                transform: translateY(-5px);
                box-shadow: 0 5px 20px rgba(0,0,0,0.2);
            }
            .card-title {
                font-size: 20px;
                font-weight: bold;
                margin-bottom: 10px;
                color: #2c3e50;
            }
            .card-desc {
                color: #7f8c8d;
                font-size: 14px;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>SilverPages CMS - Admin Dashboard</h1>
        </div>
        <div class="container">
            <div class="card-grid">
                <a href="/admin/pages" class="card">
                    <div class="card-title">Pages</div>
                    <div class="card-desc">Manage site pages and content</div>
                </a>
                <a href="/admin/documents" class="card">
                    <div class="card-title">Documents</div>
                    <div class="card-desc">Upload and organize documents</div>
                </a>
                <a href="/admin/users" class="card">
                    <div class="card-title">Users</div>
                    <div class="card-desc">Manage user accounts and permissions</div>
                </a>
                <a href="/admin/settings" class="card">
                    <div class="card-title">Settings</div>
                    <div class="card-desc">Configure system settings</div>
                </a>
            </div>
        </div>
    </body>
</html>
"""

ADMIN_PAGES_LIST = """
<!DOCTYPE html>
<html>
    <head>
        <meta charset="UTF-8">
        <title>Pages - SilverPages CMS</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 0;
                background: #f5f5f5;
            }}
            .header {{
                background: #2c3e50;
                color: white;
                padding: 20px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
            .header h1 {{
                margin: 0;
                font-size: 24px;
            }}
            .container {{
                max-width: 1200px;
                margin: 30px auto;
                padding: 0 20px;
            }}
            .actions {{
                margin-bottom: 20px;
            }}
            .btn {{
                padding: 10px 20px;
                background: #3498db;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                display: inline-block;
            }}
            .btn:hover {{
                background: #2980b9;
            }}
            table {{
                width: 100%;
                background: white;
                border-collapse: collapse;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            th, td {{
                padding: 15px;
                text-align: left;
                border-bottom: 1px solid #ecf0f1;
            }}
            th {{
                background: #34495e;
                color: white;
                font-weight: 600;
            }}
            tr:hover {{
                background: #f8f9fa;
            }}
            a {{
                color: #3498db;
                text-decoration: none;
            }}
            a:hover {{
                text-decoration: underline;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Pages Management</h1>
        </div>
        <div class="container">
            <div class="actions">
                <a href="/admin/pages/add" class="btn">Add New Page</a>
                <a href="/admin" class="btn" style="background: #95a5a6;">Back to Dashboard</a>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Title</th>
                        <th>Status</th>
                        <th>Author</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {}
                </tbody>
            </table>
        </div>
    </body>
</html>
"""

ADMIN_ADD_PAGE = """
<!DOCTYPE html>
<html>
    <head>
        <meta charset="UTF-8">
        <title>Add Page - SilverPages CMS</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 0;
                background: #f5f5f5;
            }}
            .header {{
                background: #2c3e50;
                color: white;
                padding: 20px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
            .header h1 {{
                margin: 0;
                font-size: 24px;
            }}
            .container {{
                max-width: 800px;
                margin: 30px auto;
                padding: 30px;
                background: white;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .form-group {{
                margin-bottom: 20px;
            }}
            label {{
                display: block;
                margin-bottom: 5px;
                font-weight: 600;
                color: #2c3e50;
            }}
            input[type="text"], select {{
                width: 100%;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
                box-sizing: border-box;
            }}
            .btn {{
                padding: 12px 30px;
                background: #27ae60;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
            }}
            .btn:hover {{
                background: #229954;
            }}
            .error {{
                color: #e74c3c;
                padding: 10px;
                background: #fadbd8;
                border-radius: 4px;
                margin-bottom: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Add New Page</h1>
        </div>
        <div class="container">
            {}
            <form method="POST">
                <div class="form-group">
                    <label for="title">Page Title *</label>
                    <input type="text" id="title" name="title" placeholder="Enter page title" required>
                </div>
                <div class="form-group">
                    <label for="slug">URL Slug *</label>
                    <input type="text" id="slug" name="slug" placeholder="page-url-slug" required>
                </div>
                <div class="form-group">
                    <label for="parent">Parent Page</label>
                    <select id="parent" name="parent">
                        {}
                    </select>
                </div>
                <button type="submit" class="btn">Create Page</button>
            </form>
        </div>
    </body>
</html>
"""

CHOOSE_PARENT_VIEW = """
<!DOCTYPE html>
<html>
    <head>
        <meta charset="UTF-8">
        <title>Choose Parent Page - SilverPages CMS</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 0;
                background: #f5f5f5;
            }}
            .header {{
                background: #2c3e50;
                color: white;
                padding: 20px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
            .header h1 {{
                margin: 0;
                font-size: 24px;
            }}
            .container {{
                max-width: 900px;
                margin: 30px auto;
                padding: 30px;
                background: white;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            h2 {{
                color: #2c3e50;
                margin-bottom: 20px;
            }}
            .parent-option {{
                padding: 15px;
                margin: 10px 0;
                border: 1px solid #ddd;
                border-radius: 5px;
                background: #fafafa;
            }}
            .parent-option:hover {{
                background: #f0f0f0;
                cursor: pointer;
            }}
            .breadcrumb {{
                color: #7f8c8d;
                font-size: 14px;
                margin-left: 10px;
            }}
            .alert {{
                padding: 15px;
                margin: 20px 0;
                border-radius: 5px;
            }}
            .alert-success {{
                background: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }}
            .alert-warning {{
                background: #fff3cd;
                color: #856404;
                border: 1px solid #ffeaa7;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Move Page: {}</h1>
        </div>
        <div class="container">
            <h2>Choose a parent page</h2>
            <p>Select where this page should be moved in the page hierarchy:</p>
            <form method="POST">
                {}
                <button type="submit" style="margin-top: 20px; padding: 10px 30px; background: #3498db; color: white; border: none; border-radius: 5px; cursor: pointer;">Move Page</button>
            </form>
        </div>
    </body>
</html>
"""

INSPECT_VIEW = """
<!DOCTYPE html>
<html>
    <head>
        <meta charset="UTF-8">
        <title>Inspect Page - SilverPages CMS</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 0;
                background: #f5f5f5;
            }}
            .header {{
                background: #2c3e50;
                color: white;
                padding: 20px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
            .header h1 {{
                margin: 0;
                font-size: 24px;
            }}
            .container {{
                max-width: 900px;
                margin: 30px auto;
                padding: 30px;
                background: white;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .page-title {{
                color: #2c3e50;
                margin-bottom: 30px;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
            }}
            .detail-row {{
                padding: 15px;
                margin: 10px 0;
                background: #f8f9fa;
                border-left: 4px solid #3498db;
            }}
            .detail-label {{
                font-weight: 600;
                color: #2c3e50;
                display: inline-block;
                width: 120px;
            }}
            .detail-value {{
                color: #7f8c8d;
            }}
            .alert {{
                padding: 15px;
                margin: 20px 0;
                border-radius: 5px;
            }}
            .alert-success {{
                background: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }}
            .alert-warning {{
                background: #fff3cd;
                color: #856404;
                border: 1px solid #ffeaa7;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Inspect Page Details</h1>
        </div>
        <div class="container">
            {}
            <div class="detail-row">
                <span class="detail-label">URL Slug:</span>
                <span class="detail-value">{}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Status:</span>
                <span class="detail-value">{}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Author:</span>
                <span class="detail-value">{}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Parent Page:</span>
                <span class="detail-value">{}</span>
            </div>
        </div>
    </body>
</html>
"""

ADMIN_SETTINGS = """
<!DOCTYPE html>
<html>
    <head>
        <meta charset="UTF-8">
        <title>Settings - SilverPages CMS</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 0;
                background: #f5f5f5;
            }
            .header {
                background: #2c3e50;
                color: white;
                padding: 20px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            .header h1 {
                margin: 0;
                font-size: 24px;
            }
            .container {
                max-width: 900px;
                margin: 30px auto;
                padding: 30px;
                background: white;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .setting-group {
                padding: 20px;
                margin: 15px 0;
                border: 1px solid #ecf0f1;
                border-radius: 5px;
            }
            .setting-title {
                font-weight: 600;
                color: #2c3e50;
                margin-bottom: 10px;
            }
            .setting-desc {
                color: #7f8c8d;
                font-size: 14px;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>System Settings</h1>
        </div>
        <div class="container">
            <div class="setting-group">
                <div class="setting-title">Site Configuration</div>
                <div class="setting-desc">Manage global site settings and preferences</div>
            </div>
            <div class="setting-group">
                <div class="setting-title">Security Settings</div>
                <div class="setting-desc">Configure authentication and security policies</div>
            </div>
            <div class="setting-group">
                <div class="setting-title">Email Configuration</div>
                <div class="setting-desc">Setup email notifications and SMTP settings</div>
            </div>
        </div>
    </body>
</html>
"""

ADMIN_USERS = """
<!DOCTYPE html>
<html>
    <head>
        <meta charset="UTF-8">
        <title>Users - SilverPages CMS</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 0;
                background: #f5f5f5;
            }
            .header {
                background: #2c3e50;
                color: white;
                padding: 20px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            .header h1 {
                margin: 0;
                font-size: 24px;
            }
            .container {
                max-width: 1000px;
                margin: 30px auto;
                padding: 30px;
                background: white;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            table {
                width: 100%;
                border-collapse: collapse;
            }
            th, td {
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #ecf0f1;
            }
            th {
                background: #34495e;
                color: white;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>User Management</h1>
        </div>
        <div class="container">
            <table>
                <thead>
                    <tr>
                        <th>Username</th>
                        <th>Role</th>
                        <th>Status</th>
                        <th>Last Login</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>admin</td>
                        <td>Administrator</td>
                        <td>Active</td>
                        <td>2024-01-27 10:32</td>
                    </tr>
                    <tr>
                        <td>editor1</td>
                        <td>Editor</td>
                        <td>Active</td>
                        <td>2024-01-26 15:20</td>
                    </tr>
                    <tr>
                        <td>viewer</td>
                        <td>Viewer</td>
                        <td>Active</td>
                        <td>2024-01-25 09:15</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </body>
</html>
"""

ADMIN_DOCUMENTS = """
<!DOCTYPE html>
<html>
    <head>
        <meta charset="UTF-8">
        <title>Documents - SilverPages CMS</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 0;
                background: #f5f5f5;
            }
            .header {
                background: #2c3e50;
                color: white;
                padding: 20px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            .header h1 {
                margin: 0;
                font-size: 24px;
            }
            .container {
                max-width: 1000px;
                margin: 30px auto;
                padding: 30px;
                background: white;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .doc-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
                gap: 20px;
                margin-top: 20px;
            }
            .doc-card {
                padding: 20px;
                border: 1px solid #ecf0f1;
                border-radius: 5px;
                text-align: center;
            }
            .doc-icon {
                font-size: 48px;
                color: #3498db;
                margin-bottom: 10px;
            }
            .doc-name {
                font-weight: 600;
                color: #2c3e50;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Document Library</h1>
        </div>
        <div class="container">
            <div class="doc-grid">
                <div class="doc-card">
                    <div class="doc-icon">📄</div>
                    <div class="doc-name">Annual Report 2023.pdf</div>
                </div>
                <div class="doc-card">
                    <div class="doc-icon">📊</div>
                    <div class="doc-name">Q4 Analytics.xlsx</div>
                </div>
                <div class="doc-card">
                    <div class="doc-icon">🖼️</div>
                    <div class="doc-name">Logo Assets.zip</div>
                </div>
            </div>
        </div>
    </body>
</html>
"""
