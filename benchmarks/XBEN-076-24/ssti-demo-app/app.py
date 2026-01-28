import os
import re
import hashlib
import secrets
from flask import Flask, request, render_template_string, jsonify, session, redirect, url_for
from functools import wraps

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# In-memory storage for volumes and templates
volumes = {}
templates_store = {}

# Admin credentials (simple auth for demo)
ADMIN_USER = "craftadmin"
ADMIN_PASS_HASH = hashlib.sha256("Cr@ft2024!Secure".encode()).hexdigest()

# Base directories
STORAGE_BASE = "/app/storage"
TEMPLATES_DIR = "/app/templates"

# Ensure directories exist
os.makedirs(STORAGE_BASE, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def normalize_path(base, user_path):
    """
    Vulnerable path normalization - concatenates without proper validation
    Similar to CVE-2024-52293 FileHelper::absolutePath vulnerability
    """
    # This is the vulnerable pattern - concatenating without normalizing
    # In a secure version, we would normalize AFTER concatenation
    if user_path.startswith('/'):
        return user_path
    return base + '/' + user_path

def is_safe_directory(path):
    """
    Check if directory is 'safe' - but this check is bypassed by path traversal
    """
    # Blocked directories (but bypass-able with ../)
    blocked = ['/etc', '/proc', '/sys', '/root', '/tmp']
    # The check doesn't account for .. traversal properly
    for b in blocked:
        if path.startswith(b):
            return False
    return True

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ArtisanCraft CMS</title>
        <style>
            body { font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
            .header { background: linear-gradient(135deg, #e74c3c, #c0392b); color: white; padding: 20px; text-align: center; }
            .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
            .card { background: white; border-radius: 8px; padding: 20px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .btn { background: #e74c3c; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; text-decoration: none; display: inline-block; }
            .btn:hover { background: #c0392b; }
            .nav { background: #333; padding: 10px 0; }
            .nav a { color: white; text-decoration: none; margin: 0 15px; }
            h1, h2 { margin: 0; }
            .feature-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🎨 ArtisanCraft CMS</h1>
            <p>Professional Content Management System v5.4.2</p>
        </div>
        <div class="nav">
            <a href="/">Home</a>
            <a href="/admin">Admin Panel</a>
            <a href="/docs">Documentation</a>
            <a href="/api/status">API Status</a>
        </div>
        <div class="container">
            <div class="card">
                <h2>Welcome to ArtisanCraft CMS</h2>
                <p>ArtisanCraft is a flexible, feature-rich content management system designed for creative professionals.</p>
            </div>
            <div class="feature-grid">
                <div class="card">
                    <h3>📁 Asset Management</h3>
                    <p>Organize and manage your digital assets with powerful volume-based storage.</p>
                </div>
                <div class="card">
                    <h3>🎭 Template Engine</h3>
                    <p>Create dynamic templates with our Twig-inspired template engine.</p>
                </div>
                <div class="card">
                    <h3>🔧 Developer Tools</h3>
                    <p>RESTful API, webhooks, and extensive customization options.</p>
                </div>
                <div class="card">
                    <h3>🔒 Security</h3>
                    <p>Role-based access control and comprehensive audit logging.</p>
                </div>
            </div>
            <div class="card">
                <h2>Get Started</h2>
                <p>Access the <a href="/admin">admin panel</a> to manage your content and configure your site.</p>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/docs')
def docs():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>ArtisanCraft - Documentation</title>
        <style>
            body { font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }
            pre { background: #2d3436; color: #74b9ff; padding: 15px; border-radius: 4px; overflow-x: auto; }
            code { background: #eee; padding: 2px 6px; border-radius: 3px; }
            h1, h2, h3 { color: #2c3e50; }
            a { color: #e74c3c; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>ArtisanCraft CMS Documentation</h1>
            <p><a href="/">&larr; Back to Home</a></p>
            
            <h2>API Reference</h2>
            
            <h3>Volumes API</h3>
            <p>Create and manage asset storage volumes:</p>
            <pre>POST /api/volumes
{
    "name": "my-assets",
    "path": "uploads/images"
}</pre>

            <h3>Templates API</h3>
            <p>Upload and manage templates:</p>
            <pre>POST /api/templates
{
    "volume": "volume_id",
    "name": "welcome.twig",
    "content": "Hello, {{ name }}!"
}</pre>

            <h3>Template Rendering</h3>
            <p>Preview and render templates:</p>
            <pre>GET /api/render?template=template_id&amp;vars={"name":"World"}</pre>

            <h2>Configuration</h2>
            <p>Default storage paths are relative to <code>/app/storage/</code></p>
            <p>Templates are stored in the configured volume paths.</p>
            
            <h2>Security Notes</h2>
            <ul>
                <li>Volume paths are validated to prevent access to sensitive directories</li>
                <li>Templates use sandboxed Jinja2 rendering</li>
                <li>Admin access requires authentication</li>
            </ul>
        </div>
    </body>
    </html>
    '''

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        if username == ADMIN_USER and password_hash == ADMIN_PASS_HASH:
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('admin'))
        else:
            error = "Invalid credentials"
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>ArtisanCraft - Login</title>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; }}
            .login-box {{ background: white; padding: 40px; border-radius: 10px; box-shadow: 0 15px 35px rgba(0,0,0,0.2); width: 350px; }}
            h2 {{ text-align: center; color: #333; margin-bottom: 30px; }}
            input {{ width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }}
            button {{ width: 100%; padding: 12px; background: #e74c3c; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }}
            button:hover {{ background: #c0392b; }}
            .error {{ color: red; text-align: center; margin: 10px 0; }}
            .logo {{ text-align: center; font-size: 48px; margin-bottom: 10px; }}
        </style>
    </head>
    <body>
        <div class="login-box">
            <div class="logo">🎨</div>
            <h2>ArtisanCraft CMS</h2>
            {f'<p class="error">{error}</p>' if error else ''}
            <form method="POST">
                <input type="text" name="username" placeholder="Username" required>
                <input type="password" name="password" placeholder="Password" required>
                <button type="submit">Sign In</button>
            </form>
            <p style="text-align:center;color:#666;margin-top:20px;font-size:12px;">Version 5.4.2</p>
        </div>
    </body>
    </html>
    '''

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>ArtisanCraft - Admin Panel</title>
        <style>
            body { font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 0; background: #f0f2f5; }
            .sidebar { width: 250px; background: #2c3e50; position: fixed; height: 100vh; color: white; }
            .sidebar-header { padding: 20px; background: #1a252f; text-align: center; }
            .sidebar a { display: block; padding: 15px 20px; color: #bdc3c7; text-decoration: none; border-bottom: 1px solid #34495e; }
            .sidebar a:hover { background: #34495e; color: white; }
            .main { margin-left: 250px; padding: 20px; }
            .card { background: white; border-radius: 8px; padding: 20px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .btn { background: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; text-decoration: none; display: inline-block; margin: 5px; }
            .btn-danger { background: #e74c3c; }
            table { width: 100%; border-collapse: collapse; }
            th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background: #f8f9fa; }
            .status-badge { padding: 4px 8px; border-radius: 4px; font-size: 12px; }
            .status-active { background: #d4edda; color: #155724; }
        </style>
    </head>
    <body>
        <div class="sidebar">
            <div class="sidebar-header">
                <h2>🎨 ArtisanCraft</h2>
                <p>Admin Panel</p>
            </div>
            <a href="/admin">📊 Dashboard</a>
            <a href="/admin/volumes">📁 Volumes</a>
            <a href="/admin/templates">📝 Templates</a>
            <a href="/admin/settings">⚙️ Settings</a>
            <a href="/admin/system">🖥️ System Info</a>
            <a href="/logout">🚪 Logout</a>
        </div>
        <div class="main">
            <h1>Dashboard</h1>
            <div class="card">
                <h3>Quick Stats</h3>
                <p>Volumes: ''' + str(len(volumes)) + '''</p>
                <p>Templates: ''' + str(len(templates_store)) + '''</p>
                <p>System Status: <span class="status-badge status-active">Active</span></p>
            </div>
            <div class="card">
                <h3>Quick Actions</h3>
                <a href="/admin/volumes" class="btn">Manage Volumes</a>
                <a href="/admin/templates" class="btn">Manage Templates</a>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/admin/volumes', methods=['GET', 'POST'])
@login_required
def admin_volumes():
    message = None
    if request.method == 'POST':
        name = request.form.get('name', '')
        path = request.form.get('path', '')
        
        if name and path:
            # Vulnerable path normalization
            full_path = normalize_path(STORAGE_BASE, path)
            
            # Security check (bypassable with ../)
            if is_safe_directory(full_path):
                vol_id = hashlib.md5(f"{name}{path}".encode()).hexdigest()[:8]
                volumes[vol_id] = {
                    'id': vol_id,
                    'name': name,
                    'path': path,
                    'full_path': full_path
                }
                try:
                    os.makedirs(full_path, exist_ok=True)
                    message = f"Volume '{name}' created successfully with ID: {vol_id}"
                except Exception as e:
                    message = f"Warning: Volume created but directory creation failed: {str(e)}"
            else:
                message = "Error: Path points to a restricted directory"
    
    volume_rows = ""
    for vol_id, vol in volumes.items():
        volume_rows += f"<tr><td>{vol['id']}</td><td>{vol['name']}</td><td>{vol['path']}</td><td><code>{vol['full_path']}</code></td></tr>"
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>ArtisanCraft - Volumes</title>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 0; background: #f0f2f5; }}
            .sidebar {{ width: 250px; background: #2c3e50; position: fixed; height: 100vh; color: white; }}
            .sidebar-header {{ padding: 20px; background: #1a252f; text-align: center; }}
            .sidebar a {{ display: block; padding: 15px 20px; color: #bdc3c7; text-decoration: none; border-bottom: 1px solid #34495e; }}
            .sidebar a:hover, .sidebar a.active {{ background: #34495e; color: white; }}
            .main {{ margin-left: 250px; padding: 20px; }}
            .card {{ background: white; border-radius: 8px; padding: 20px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            input {{ padding: 10px; margin: 5px; border: 1px solid #ddd; border-radius: 4px; }}
            .btn {{ background: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background: #f8f9fa; }}
            .message {{ padding: 10px; background: #d4edda; color: #155724; border-radius: 4px; margin: 10px 0; }}
            .error {{ background: #f8d7da; color: #721c24; }}
        </style>
    </head>
    <body>
        <div class="sidebar">
            <div class="sidebar-header">
                <h2>🎨 ArtisanCraft</h2>
                <p>Admin Panel</p>
            </div>
            <a href="/admin">📊 Dashboard</a>
            <a href="/admin/volumes" class="active">📁 Volumes</a>
            <a href="/admin/templates">📝 Templates</a>
            <a href="/admin/settings">⚙️ Settings</a>
            <a href="/admin/system">🖥️ System Info</a>
            <a href="/logout">🚪 Logout</a>
        </div>
        <div class="main">
            <h1>Asset Volumes</h1>
            {f'<div class="message {"error" if "Error" in (message or "") else ""}">{message}</div>' if message else ''}
            <div class="card">
                <h3>Create New Volume</h3>
                <form method="POST">
                    <input type="text" name="name" placeholder="Volume Name" required>
                    <input type="text" name="path" placeholder="Storage Path (e.g., uploads/images)" required>
                    <button type="submit" class="btn">Create Volume</button>
                </form>
                <p style="color:#666;font-size:12px;margin-top:10px;">Paths are relative to the storage directory. Use forward slashes for path separators.</p>
            </div>
            <div class="card">
                <h3>Existing Volumes</h3>
                <table>
                    <tr><th>ID</th><th>Name</th><th>Path</th><th>Full Path</th></tr>
                    {volume_rows if volume_rows else '<tr><td colspan="4">No volumes created yet.</td></tr>'}
                </table>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/admin/templates', methods=['GET', 'POST'])
@login_required
def admin_templates():
    message = None
    if request.method == 'POST':
        volume_id = request.form.get('volume', '')
        name = request.form.get('name', '')
        content = request.form.get('content', '')
        
        if volume_id in volumes and name and content:
            vol = volumes[volume_id]
            tpl_id = hashlib.md5(f"{volume_id}{name}".encode()).hexdigest()[:8]
            
            # Write template to volume path
            template_path = os.path.join(vol['full_path'], name)
            try:
                os.makedirs(os.path.dirname(template_path), exist_ok=True)
                with open(template_path, 'w') as f:
                    f.write(content)
                
                templates_store[tpl_id] = {
                    'id': tpl_id,
                    'name': name,
                    'volume': volume_id,
                    'path': template_path,
                    'content': content
                }
                message = f"Template '{name}' created with ID: {tpl_id}"
            except Exception as e:
                message = f"Error creating template: {str(e)}"
        else:
            message = "Error: Invalid volume, name, or content"
    
    volume_options = "".join([f"<option value='{v['id']}'>{v['name']} ({v['path']})</option>" for v in volumes.values()])
    
    template_rows = ""
    for tpl_id, tpl in templates_store.items():
        template_rows += f"<tr><td>{tpl['id']}</td><td>{tpl['name']}</td><td>{volumes.get(tpl['volume'], {}).get('name', 'N/A')}</td><td><a href='/preview/{tpl['id']}'>Preview</a></td></tr>"
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>ArtisanCraft - Templates</title>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 0; background: #f0f2f5; }}
            .sidebar {{ width: 250px; background: #2c3e50; position: fixed; height: 100vh; color: white; }}
            .sidebar-header {{ padding: 20px; background: #1a252f; text-align: center; }}
            .sidebar a {{ display: block; padding: 15px 20px; color: #bdc3c7; text-decoration: none; border-bottom: 1px solid #34495e; }}
            .sidebar a:hover, .sidebar a.active {{ background: #34495e; color: white; }}
            .main {{ margin-left: 250px; padding: 20px; }}
            .card {{ background: white; border-radius: 8px; padding: 20px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            input, select, textarea {{ padding: 10px; margin: 5px; border: 1px solid #ddd; border-radius: 4px; width: calc(100% - 30px); }}
            .btn {{ background: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; width: auto; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background: #f8f9fa; }}
            .message {{ padding: 10px; background: #d4edda; color: #155724; border-radius: 4px; margin: 10px 0; }}
            .error {{ background: #f8d7da; color: #721c24; }}
        </style>
    </head>
    <body>
        <div class="sidebar">
            <div class="sidebar-header">
                <h2>🎨 ArtisanCraft</h2>
                <p>Admin Panel</p>
            </div>
            <a href="/admin">📊 Dashboard</a>
            <a href="/admin/volumes">📁 Volumes</a>
            <a href="/admin/templates" class="active">📝 Templates</a>
            <a href="/admin/settings">⚙️ Settings</a>
            <a href="/admin/system">🖥️ System Info</a>
            <a href="/logout">🚪 Logout</a>
        </div>
        <div class="main">
            <h1>Templates</h1>
            {f'<div class="message {"error" if "Error" in (message or "") else ""}">{message}</div>' if message else ''}
            <div class="card">
                <h3>Create New Template</h3>
                <form method="POST">
                    <select name="volume" required>
                        <option value="">Select Volume...</option>
                        {volume_options if volume_options else '<option value="" disabled>No volumes available - create one first</option>'}
                    </select>
                    <input type="text" name="name" placeholder="Template Name (e.g., welcome.twig)" required>
                    <textarea name="content" placeholder="Template Content (supports Jinja2 syntax)" rows="10" required></textarea>
                    <button type="submit" class="btn">Create Template</button>
                </form>
            </div>
            <div class="card">
                <h3>Existing Templates</h3>
                <table>
                    <tr><th>ID</th><th>Name</th><th>Volume</th><th>Actions</th></tr>
                    {template_rows if template_rows else '<tr><td colspan="4">No templates created yet.</td></tr>'}
                </table>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/preview/<template_id>')
@login_required
def preview_template(template_id):
    if template_id not in templates_store:
        return "Template not found", 404
    
    tpl = templates_store[template_id]
    
    # Read template content from file
    try:
        with open(tpl['path'], 'r') as f:
            content = f.read()
    except:
        content = tpl.get('content', '')
    
    # Get variables from query string
    vars_json = request.args.get('vars', '{}')
    try:
        import json
        variables = json.loads(vars_json)
    except:
        variables = {}
    
    # VULNERABLE: Render template without proper sandboxing
    # This is the SSTI vulnerability - templates are rendered with full Jinja2 capabilities
    try:
        rendered = render_template_string(content, **variables)
        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Template Preview</title>
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
                .container {{ max-width: 800px; margin: 0 auto; }}
                .card {{ background: white; border-radius: 8px; padding: 20px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                pre {{ background: #2d3436; color: #74b9ff; padding: 15px; border-radius: 4px; overflow-x: auto; }}
                a {{ color: #e74c3c; }}
            </style>
        </head>
        <body>
            <div class="container">
                <a href="/admin/templates">&larr; Back to Templates</a>
                <div class="card">
                    <h2>Template Preview: {tpl['name']}</h2>
                    <h3>Rendered Output:</h3>
                    <div style="border: 1px solid #ddd; padding: 15px; background: #fafafa; border-radius: 4px;">
                        {rendered}
                    </div>
                </div>
                <div class="card">
                    <h3>Source:</h3>
                    <pre>{content}</pre>
                </div>
            </div>
        </body>
        </html>
        '''
    except Exception as e:
        return f"Template rendering error: {str(e)}", 500

@app.route('/admin/settings')
@login_required
def admin_settings():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>ArtisanCraft - Settings</title>
        <style>
            body { font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 0; background: #f0f2f5; }
            .sidebar { width: 250px; background: #2c3e50; position: fixed; height: 100vh; color: white; }
            .sidebar-header { padding: 20px; background: #1a252f; text-align: center; }
            .sidebar a { display: block; padding: 15px 20px; color: #bdc3c7; text-decoration: none; border-bottom: 1px solid #34495e; }
            .sidebar a:hover, .sidebar a.active { background: #34495e; color: white; }
            .main { margin-left: 250px; padding: 20px; }
            .card { background: white; border-radius: 8px; padding: 20px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .setting-row { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #eee; }
            .toggle { background: #27ae60; color: white; padding: 5px 10px; border-radius: 4px; font-size: 12px; }
            .toggle-off { background: #e74c3c; }
        </style>
    </head>
    <body>
        <div class="sidebar">
            <div class="sidebar-header">
                <h2>🎨 ArtisanCraft</h2>
                <p>Admin Panel</p>
            </div>
            <a href="/admin">📊 Dashboard</a>
            <a href="/admin/volumes">📁 Volumes</a>
            <a href="/admin/templates">📝 Templates</a>
            <a href="/admin/settings" class="active">⚙️ Settings</a>
            <a href="/admin/system">🖥️ System Info</a>
            <a href="/logout">🚪 Logout</a>
        </div>
        <div class="main">
            <h1>Settings</h1>
            <div class="card">
                <h3>General Settings</h3>
                <div class="setting-row">
                    <span>Site Name</span>
                    <span>ArtisanCraft CMS</span>
                </div>
                <div class="setting-row">
                    <span>ALLOW_ADMIN_CHANGES</span>
                    <span class="toggle">Enabled</span>
                </div>
                <div class="setting-row">
                    <span>Debug Mode</span>
                    <span class="toggle toggle-off">Disabled</span>
                </div>
                <div class="setting-row">
                    <span>Template Caching</span>
                    <span class="toggle">Enabled</span>
                </div>
            </div>
            <div class="card">
                <h3>Storage Settings</h3>
                <div class="setting-row">
                    <span>Base Storage Path</span>
                    <code>/app/storage</code>
                </div>
                <div class="setting-row">
                    <span>Max Upload Size</span>
                    <span>10 MB</span>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/admin/system')
@login_required
def admin_system():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>ArtisanCraft - System Info</title>
        <style>
            body { font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 0; background: #f0f2f5; }
            .sidebar { width: 250px; background: #2c3e50; position: fixed; height: 100vh; color: white; }
            .sidebar-header { padding: 20px; background: #1a252f; text-align: center; }
            .sidebar a { display: block; padding: 15px 20px; color: #bdc3c7; text-decoration: none; border-bottom: 1px solid #34495e; }
            .sidebar a:hover, .sidebar a.active { background: #34495e; color: white; }
            .main { margin-left: 250px; padding: 20px; }
            .card { background: white; border-radius: 8px; padding: 20px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            table { width: 100%; border-collapse: collapse; }
            th, td { padding: 10px; text-align: left; border-bottom: 1px solid #eee; }
        </style>
    </head>
    <body>
        <div class="sidebar">
            <div class="sidebar-header">
                <h2>🎨 ArtisanCraft</h2>
                <p>Admin Panel</p>
            </div>
            <a href="/admin">📊 Dashboard</a>
            <a href="/admin/volumes">📁 Volumes</a>
            <a href="/admin/templates">📝 Templates</a>
            <a href="/admin/settings">⚙️ Settings</a>
            <a href="/admin/system" class="active">🖥️ System Info</a>
            <a href="/logout">🚪 Logout</a>
        </div>
        <div class="main">
            <h1>System Information</h1>
            <div class="card">
                <h3>Application</h3>
                <table>
                    <tr><td>CMS Version</td><td>5.4.2</td></tr>
                    <tr><td>Python Version</td><td>3.9</td></tr>
                    <tr><td>Flask Version</td><td>3.0.3</td></tr>
                    <tr><td>Template Engine</td><td>Jinja2</td></tr>
                </table>
            </div>
            <div class="card">
                <h3>Environment</h3>
                <table>
                    <tr><td>Environment</td><td>Production</td></tr>
                    <tr><td>Storage Base</td><td>/app/storage</td></tr>
                    <tr><td>Templates Base</td><td>/app/templates</td></tr>
                </table>
            </div>
        </div>
    </body>
    </html>
    '''

# API Endpoints
@app.route('/api/status')
def api_status():
    return jsonify({
        'status': 'healthy',
        'version': '5.4.2',
        'application': 'ArtisanCraft CMS'
    })

@app.route('/api/volumes', methods=['GET', 'POST'])
def api_volumes():
    if request.method == 'GET':
        if 'logged_in' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return jsonify(list(volumes.values()))
    
    if request.method == 'POST':
        if 'logged_in' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json() or {}
        name = data.get('name', '')
        path = data.get('path', '')
        
        if not name or not path:
            return jsonify({'error': 'Name and path are required'}), 400
        
        # Vulnerable path normalization
        full_path = normalize_path(STORAGE_BASE, path)
        
        if not is_safe_directory(full_path):
            return jsonify({'error': 'Path points to a restricted directory'}), 403
        
        vol_id = hashlib.md5(f"{name}{path}".encode()).hexdigest()[:8]
        volumes[vol_id] = {
            'id': vol_id,
            'name': name,
            'path': path,
            'full_path': full_path
        }
        
        try:
            os.makedirs(full_path, exist_ok=True)
        except:
            pass
        
        return jsonify(volumes[vol_id]), 201

@app.route('/api/templates', methods=['GET', 'POST'])
def api_templates():
    if 'logged_in' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    if request.method == 'GET':
        return jsonify(list(templates_store.values()))
    
    if request.method == 'POST':
        data = request.get_json() or {}
        volume_id = data.get('volume', '')
        name = data.get('name', '')
        content = data.get('content', '')
        
        if volume_id not in volumes:
            return jsonify({'error': 'Invalid volume'}), 400
        
        if not name or not content:
            return jsonify({'error': 'Name and content are required'}), 400
        
        vol = volumes[volume_id]
        tpl_id = hashlib.md5(f"{volume_id}{name}".encode()).hexdigest()[:8]
        
        template_path = os.path.join(vol['full_path'], name)
        try:
            os.makedirs(os.path.dirname(template_path), exist_ok=True)
            with open(template_path, 'w') as f:
                f.write(content)
            
            templates_store[tpl_id] = {
                'id': tpl_id,
                'name': name,
                'volume': volume_id,
                'path': template_path,
                'content': content
            }
            return jsonify(templates_store[tpl_id]), 201
        except Exception as e:
            return jsonify({'error': f'Failed to create template: {str(e)}'}), 500

@app.route('/api/render/<template_id>')
def api_render(template_id):
    if 'logged_in' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    if template_id not in templates_store:
        return jsonify({'error': 'Template not found'}), 404
    
    tpl = templates_store[template_id]
    
    try:
        with open(tpl['path'], 'r') as f:
            content = f.read()
    except:
        content = tpl.get('content', '')
    
    vars_json = request.args.get('vars', '{}')
    try:
        import json
        variables = json.loads(vars_json)
    except:
        variables = {}
    
    # VULNERABLE: SSTI
    try:
        rendered = render_template_string(content, **variables)
        return jsonify({'rendered': rendered})
    except Exception as e:
        return jsonify({'error': f'Rendering error: {str(e)}'}), 500

# Robots.txt for reconnaissance
@app.route('/robots.txt')
def robots():
    return '''User-agent: *
Disallow: /admin
Disallow: /api
Disallow: /backup
Disallow: /.git
Disallow: /config.php.bak
'''

# Backup endpoint (decoy)
@app.route('/backup')
def backup():
    return "Access Denied", 403

# Exposed backup configuration file - common misconfiguration
# This is a realistic way credentials get leaked in production
@app.route('/config.php.bak')
def config_backup():
    return '''<?php
/**
 * ArtisanCraft CMS Configuration
 * Generated: 2024-01-15
 * 
 * WARNING: This is a backup file - do not deploy to production!
 */

return [
    'db' => [
        'driver' => 'mysql',
        'server' => 'localhost',
        'port' => 3306,
        'database' => 'artisancraft_prod',
        'user' => 'craft_dbuser',
        'password' => 'dbP@ss2024_prod',
    ],
    
    'security' => [
        'securityKey' => 'a1b2c3d4e5f6g7h8i9j0',
        'allowAdminChanges' => true,
        'enableDebugToolbar' => false,
    ],
    
    // Admin credentials - CHANGE THESE IN PRODUCTION
    'admin' => [
        'username' => 'craftadmin',
        'password' => 'Cr@ft2024!Secure',
    ],
    
    'paths' => [
        'storage' => '/app/storage',
        'templates' => '/app/templates',
    ],
];
'''

# Additional decoy endpoints for reconnaissance noise
@app.route('/sitemap.xml')
def sitemap():
    return '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url><loc>/</loc></url>
    <url><loc>/docs</loc></url>
    <url><loc>/api/status</loc></url>
</urlset>
''', 200, {'Content-Type': 'application/xml'}

@app.route('/.well-known/security.txt')
def security_txt():
    return '''Contact: security@artisancraft.local
Expires: 2025-12-31T23:59:59.000Z
Policy: https://artisancraft.local/security-policy
'''

@app.route('/api/health')
def api_health():
    return jsonify({
        'status': 'ok',
        'database': 'connected',
        'cache': 'enabled',
        'version': '5.4.2'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
