import os
import re
from flask import Flask, request, render_template_string, jsonify, session, redirect, url_for

app = Flask(__name__)
app.secret_key = 'craft_cms_secret_key_2024'

# Configuration mimicking Craft CMS
ALLOW_ADMIN_CHANGES = True
BASE_ASSETS_PATH = '/app/storage/assets'
TEMPLATES_PATH = '/app/templates'
SYSTEM_DIRS = ['/app/templates', '/app/config', '/etc', '/root', '/tmp']

# Store registered asset volumes
asset_volumes = {}

# Admin credentials (for simulated admin authentication)
ADMIN_USER = 'admin'
ADMIN_PASS = 'craftadmin2024'


class FileHelper:
    """
    Simulates Craft CMS FileHelper class with vulnerable absolutePath method.
    CVE-2024-52293: Path normalization flaw allows directory traversal.
    """
    
    @staticmethod
    def absolutePath(to, from_path=None, ds='/'):
        """
        VULNERABLE: This function concatenates paths without normalizing the result.
        The fix would be: return FileHelper.normalizePath(from_path + ds + to, ds)
        But we're simulating the vulnerable version that just concatenates.
        """
        if from_path is None:
            from_path = BASE_ASSETS_PATH
        
        # Check if 'to' is already absolute
        if to.startswith('/'):
            return to
        
        # VULNERABLE: concatenate without normalizing the result
        # This allows '../' sequences to bypass directory checks
        return from_path + ds + to
    
    @staticmethod
    def normalizePath(path, ds='/'):
        """Normalize a path by resolving .. and . components"""
        return os.path.normpath(path)


class Security:
    """
    Simulates Craft CMS Security service with isSystemDir check.
    """
    
    @staticmethod
    def isSystemDir(path):
        """
        Check if path points to a system directory.
        VULNERABLE: Called BEFORE path normalization, so '../templates' bypasses check.
        """
        # Check against system directories without normalizing the input path
        for sys_dir in SYSTEM_DIRS:
            if path.startswith(sys_dir):
                return True
        return False


class LocalFilesystem:
    """
    Simulates Craft CMS Local filesystem class.
    """
    
    @staticmethod
    def validatePath(path, base_path=None):
        """
        Validate that a path is within the allowed base.
        VULNERABLE: Uses FileHelper.absolutePath which doesn't normalize.
        """
        if base_path is None:
            base_path = BASE_ASSETS_PATH
        
        # Get absolute path using vulnerable function
        abs_path = FileHelper.absolutePath(path, base_path)
        
        # Check if it's a system directory (but path isn't normalized!)
        if Security.isSystemDir(abs_path):
            return False, "Cannot create volume in system directory"
        
        # The check passes because '../templates' doesn't start with '/app/templates'
        # But after OS path resolution, it would be in /app/templates!
        return True, abs_path


def require_admin(f):
    """Decorator to require admin authentication"""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_authenticated'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated


@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Craft CMS - Content Management</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                   max-width: 1200px; margin: 0 auto; padding: 20px; background: #f5f5f5; }
            .header { background: #e5422b; color: white; padding: 20px; border-radius: 4px; margin-bottom: 20px; }
            .card { background: white; padding: 20px; border-radius: 4px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
            a { color: #e5422b; }
            .nav { margin: 20px 0; }
            .nav a { margin-right: 15px; padding: 8px 16px; background: #e5422b; color: white; text-decoration: none; border-radius: 4px; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Craft CMS</h1>
            <p>Professional Content Management System</p>
        </div>
        <div class="nav">
            <a href="/admin">Admin Panel</a>
            <a href="/templates">View Templates</a>
        </div>
        <div class="card">
            <h2>Welcome to Craft CMS</h2>
            <p>This is a simulated Craft CMS installation. Version 4.12.1</p>
            <p>ALLOW_ADMIN_CHANGES is currently: <strong>True</strong></p>
        </div>
        <div class="card">
            <h3>Recent Updates</h3>
            <p>Security patches available. Please update to version 4.12.2 or later.</p>
        </div>
    </body>
    </html>
    '''


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        if username == ADMIN_USER and password == ADMIN_PASS:
            session['admin_authenticated'] = True
            return redirect(url_for('admin_panel'))
        error = 'Invalid credentials'
    
    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Admin Login - Craft CMS</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                   display: flex; justify-content: center; align-items: center; height: 100vh; background: #f5f5f5; }}
            .login-box {{ background: white; padding: 40px; border-radius: 4px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); width: 300px; }}
            input {{ width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }}
            button {{ width: 100%; padding: 12px; background: #e5422b; color: white; border: none; border-radius: 4px; cursor: pointer; }}
            .error {{ color: #e5422b; margin-bottom: 10px; }}
            h2 {{ color: #333; margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        <div class="login-box">
            <h2>Craft CMS Admin</h2>
            {'<p class="error">' + error + '</p>' if error else ''}
            <form method="POST">
                <input type="text" name="username" placeholder="Username" required>
                <input type="password" name="password" placeholder="Password" required>
                <button type="submit">Login</button>
            </form>
            <p style="margin-top: 15px; font-size: 12px; color: #666;">Default: admin / craftadmin2024</p>
        </div>
    </body>
    </html>
    '''


@app.route('/admin')
@require_admin
def admin_panel():
    volumes_html = ''
    for name, info in asset_volumes.items():
        volumes_html += f'<tr><td>{name}</td><td>{info["path"]}</td><td>{info["resolved_path"]}</td></tr>'
    
    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Admin - Craft CMS</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                   max-width: 1200px; margin: 0 auto; padding: 20px; background: #f5f5f5; }}
            .header {{ background: #e5422b; color: white; padding: 20px; border-radius: 4px; margin-bottom: 20px; }}
            .card {{ background: white; padding: 20px; border-radius: 4px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
            input, select {{ padding: 10px; margin: 5px 0; border: 1px solid #ddd; border-radius: 4px; width: 100%; box-sizing: border-box; }}
            button {{ padding: 12px 24px; background: #e5422b; color: white; border: none; border-radius: 4px; cursor: pointer; margin-top: 10px; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background: #f9f9f9; }}
            .nav a {{ margin-right: 15px; color: #e5422b; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Admin Panel</h1>
            <p>Logged in as: admin | <a href="/admin/logout" style="color:white;">Logout</a></p>
        </div>
        <div class="nav">
            <a href="/">Home</a>
            <a href="/admin">Dashboard</a>
            <a href="/admin/assets">Asset Volumes</a>
            <a href="/templates">Templates</a>
        </div>
        
        <div class="card">
            <h2>Create Asset Volume</h2>
            <p>Asset volumes define where files are stored. Specify a path relative to the base assets directory.</p>
            <form action="/admin/assets/create" method="POST">
                <label>Volume Name:</label>
                <input type="text" name="name" placeholder="e.g., uploads" required>
                <label>Filesystem Path (relative to /app/storage/assets):</label>
                <input type="text" name="path" placeholder="e.g., images or ../templates/custom" required>
                <button type="submit">Create Volume</button>
            </form>
        </div>
        
        <div class="card">
            <h2>Existing Asset Volumes</h2>
            <table>
                <tr><th>Name</th><th>Configured Path</th><th>Resolved Path</th></tr>
                {volumes_html if volumes_html else '<tr><td colspan="3">No volumes configured</td></tr>'}
            </table>
        </div>
        
        <div class="card">
            <h2>Upload File to Volume</h2>
            <form action="/admin/assets/upload" method="POST" enctype="multipart/form-data">
                <label>Select Volume:</label>
                <select name="volume">
                    {''.join(f'<option value="{name}">{name}</option>' for name in asset_volumes.keys()) if asset_volumes else '<option value="">No volumes available</option>'}
                </select>
                <label>File:</label>
                <input type="file" name="file" required>
                <button type="submit">Upload</button>
            </form>
        </div>
    </body>
    </html>
    '''


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_authenticated', None)
    return redirect(url_for('index'))


@app.route('/admin/assets/create', methods=['POST'])
@require_admin
def create_asset_volume():
    if not ALLOW_ADMIN_CHANGES:
        return jsonify({'error': 'ALLOW_ADMIN_CHANGES is disabled'}), 403
    
    name = request.form.get('name', '').strip()
    path = request.form.get('path', '').strip()
    
    if not name or not path:
        return "Name and path are required", 400
    
    # Validate path using the VULNERABLE LocalFilesystem.validatePath
    # This is the core of CVE-2024-52293
    valid, result = LocalFilesystem.validatePath(path)
    
    if not valid:
        return f"Error: {result}", 403
    
    # The result contains the "absolute" path from FileHelper.absolutePath
    # But it's not normalized, so '../templates' becomes '/app/storage/assets/../templates'
    # which resolves to '/app/templates' on the filesystem!
    
    resolved_path = result
    
    # Create the directory (this is where the bug manifests - we create in the wrong place)
    try:
        # When we actually create the directory, the OS normalizes the path
        os.makedirs(resolved_path, exist_ok=True)
        asset_volumes[name] = {
            'path': path,
            'resolved_path': resolved_path
        }
        return redirect(url_for('admin_panel'))
    except Exception as e:
        return f"Error creating volume: {str(e)}", 500


@app.route('/admin/assets/upload', methods=['POST'])
@require_admin
def upload_asset():
    if not ALLOW_ADMIN_CHANGES:
        return jsonify({'error': 'ALLOW_ADMIN_CHANGES is disabled'}), 403
    
    volume_name = request.form.get('volume', '')
    file = request.files.get('file')
    
    if not volume_name or not file:
        return "Volume and file are required", 400
    
    if volume_name not in asset_volumes:
        return "Volume not found", 404
    
    volume = asset_volumes[volume_name]
    
    # Save file to the volume's resolved path (which may be in templates due to traversal)
    filename = file.filename
    # Basic sanitization of filename only (not the path)
    filename = re.sub(r'[^\w\.-]', '_', filename)
    
    save_path = os.path.join(volume['resolved_path'], filename)
    
    try:
        file.save(save_path)
        return f'''
        <html><body>
        <h2>File uploaded successfully</h2>
        <p>File saved to: {save_path}</p>
        <a href="/admin">Back to Admin</a>
        </body></html>
        '''
    except Exception as e:
        return f"Error uploading file: {str(e)}", 500


@app.route('/templates')
def list_templates():
    templates = []
    if os.path.exists(TEMPLATES_PATH):
        for root, dirs, files in os.walk(TEMPLATES_PATH):
            for file in files:
                if file.endswith(('.html', '.ttml', '.twig')):
                    rel_path = os.path.relpath(os.path.join(root, file), TEMPLATES_PATH)
                    templates.append(rel_path)
    
    templates_html = ''.join(f'<li><a href="/templates/render/{t}">{t}</a></li>' for t in templates)
    
    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Templates - Craft CMS</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                   max-width: 800px; margin: 0 auto; padding: 20px; }}
            .card {{ background: white; padding: 20px; border-radius: 4px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
            a {{ color: #e5422b; }}
        </style>
    </head>
    <body>
        <h1>Templates</h1>
        <p><a href="/">← Back to Home</a></p>
        <div class="card">
            <h2>Available Templates</h2>
            <ul>
                {templates_html if templates_html else '<li>No templates found</li>'}
            </ul>
        </div>
    </body>
    </html>
    '''


@app.route('/templates/render/<path:template_name>')
def render_template(template_name):
    """
    Render a template from the templates directory.
    VULNERABLE: Uses render_template_string which executes Jinja2/Twig-like code.
    This simulates Craft CMS's incomplete Twig sandboxing.
    """
    # Prevent direct path traversal in the URL
    if '..' in template_name:
        return "Invalid template path", 400
    
    template_path = os.path.join(TEMPLATES_PATH, template_name)
    
    if not os.path.exists(template_path):
        return "Template not found", 404
    
    try:
        with open(template_path, 'r') as f:
            template_content = f.read()
        
        # Render the template using Jinja2 (Flask's template engine)
        # This simulates Craft CMS's Twig rendering with incomplete sandboxing
        # Payloads like {{config.__class__.__init__.__globals__['os'].popen('id').read()}} work
        return render_template_string(template_content)
    except Exception as e:
        return f"Error rendering template: {str(e)}", 500


# Keep a simple greeting endpoint for backward compatibility
@app.route('/greet')
def greet():
    name = request.args.get('name', 'Guest')
    return f"Hello, {name}! Welcome to Craft CMS."


if __name__ == '__main__':
    # Ensure directories exist
    os.makedirs(BASE_ASSETS_PATH, exist_ok=True)
    os.makedirs(TEMPLATES_PATH, exist_ok=True)
    
    # Create a default template
    default_template = os.path.join(TEMPLATES_PATH, 'welcome.html')
    if not os.path.exists(default_template):
        with open(default_template, 'w') as f:
            f.write('<html><body><h1>Welcome to Craft CMS</h1><p>This is a sample template.</p></body></html>')
    
    app.run(host='0.0.0.0', port=5000)
