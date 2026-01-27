from flask import Flask, request, render_template_string, redirect, url_for, jsonify, session
import os
import re

app = Flask(__name__)
app.secret_key = 'craftcms_admin_secret_key_2024'

# Simulated CraftCMS-like environment
STORAGE_BASE = '/app/storage'
TEMPLATES_DIR = '/app/templates'
ALLOWED_TEMPLATES_DIR = '/app/user_templates'

# Create directories on startup
os.makedirs(STORAGE_BASE, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)
os.makedirs(ALLOWED_TEMPLATES_DIR, exist_ok=True)

# Simple admin authentication
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'craftadmin2024'

def is_authenticated():
    return session.get('authenticated', False)

def validate_path(base_dir, relative_path):
    """
    Vulnerable path validation - similar to CVE-2024-52293
    Does NOT properly normalize the path before validation
    """
    # BUG: Concatenates without normalizing, allowing traversal
    full_path = base_dir + '/' + relative_path
    
    # This check is bypassed because path isn't normalized
    if full_path.startswith(base_dir):
        return full_path
    return None

def is_system_dir(path):
    """Check if path is a sensitive system directory"""
    system_dirs = ['/etc', '/var', '/tmp', '/root', '/proc']
    # Vulnerable: doesn't normalize path before checking
    for sys_dir in system_dirs:
        if path.startswith(sys_dir):
            return True
    return False

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AssetForge CMS - Digital Asset Management</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
            .header { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); color: white; padding: 20px 40px; }
            .header h1 { margin: 0; font-size: 24px; }
            .header .version { font-size: 12px; color: #888; }
            .container { max-width: 1200px; margin: 40px auto; padding: 0 20px; }
            .card { background: white; border-radius: 8px; padding: 30px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .card h2 { margin-top: 0; color: #333; border-bottom: 2px solid #e94560; padding-bottom: 10px; display: inline-block; }
            .btn { display: inline-block; padding: 12px 24px; background: #e94560; color: white; text-decoration: none; border-radius: 4px; margin-right: 10px; }
            .btn:hover { background: #d63d56; }
            .btn-secondary { background: #16213e; }
            .feature-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 20px; }
            .feature { padding: 20px; background: #f8f9fa; border-radius: 8px; }
            .feature h3 { color: #e94560; margin-top: 0; }
            footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🔧 AssetForge CMS</h1>
            <span class="version">v4.12.1 - Enterprise Digital Asset Management</span>
        </div>
        <div class="container">
            <div class="card">
                <h2>Welcome to AssetForge</h2>
                <p>The powerful, flexible content management system for modern digital experiences.</p>
                <p>AssetForge provides enterprise-grade asset management with flexible volume configuration, 
                   custom template rendering, and seamless content delivery.</p>
                <div style="margin-top: 20px;">
                    <a href="/admin/login" class="btn">Admin Panel</a>
                    <a href="/preview" class="btn btn-secondary">Template Preview</a>
                </div>
            </div>
            
            <div class="card">
                <h2>Features</h2>
                <div class="feature-grid">
                    <div class="feature">
                        <h3>📁 Asset Volumes</h3>
                        <p>Create custom storage volumes with flexible path configuration for organizing your digital assets.</p>
                    </div>
                    <div class="feature">
                        <h3>📝 Template Engine</h3>
                        <p>Powerful Jinja2-based template rendering with custom variable support.</p>
                    </div>
                    <div class="feature">
                        <h3>🔒 Security</h3>
                        <p>Role-based access control and path validation for secure asset management.</p>
                    </div>
                    <div class="feature">
                        <h3>⚡ Performance</h3>
                        <p>Optimized for speed with efficient template caching and asset delivery.</p>
                    </div>
                </div>
            </div>
        </div>
        <footer>
            <p>&copy; 2024 AssetForge CMS. All rights reserved. | <a href="/admin/login">Administrator Login</a></p>
        </footer>
    </body>
    </html>
    '''

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['authenticated'] = True
            session['username'] = username
            return redirect(url_for('admin_dashboard'))
        else:
            error = 'Invalid credentials. Please try again.'
    
    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>AssetForge Admin Login</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, sans-serif; background: #1a1a2e; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }}
            .login-box {{ background: white; padding: 40px; border-radius: 8px; width: 350px; box-shadow: 0 4px 20px rgba(0,0,0,0.3); }}
            .login-box h2 {{ margin: 0 0 30px 0; color: #333; text-align: center; }}
            .login-box input {{ width: 100%; padding: 12px; margin-bottom: 15px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }}
            .login-box button {{ width: 100%; padding: 12px; background: #e94560; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }}
            .login-box button:hover {{ background: #d63d56; }}
            .error {{ color: #e94560; margin-bottom: 15px; text-align: center; }}
            .logo {{ text-align: center; font-size: 32px; margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        <div class="login-box">
            <div class="logo">🔧</div>
            <h2>AssetForge Admin</h2>
            {'<p class="error">' + error + '</p>' if error else ''}
            <form method="POST">
                <input type="text" name="username" placeholder="Username" required>
                <input type="password" name="password" placeholder="Password" required>
                <button type="submit">Sign In</button>
            </form>
            <p style="text-align: center; color: #666; font-size: 12px; margin-top: 20px;">
                Default credentials for demo: admin / craftadmin2024
            </p>
        </div>
    </body>
    </html>
    '''

@app.route('/admin/dashboard')
def admin_dashboard():
    if not is_authenticated():
        return redirect(url_for('admin_login'))
    
    # List existing volumes
    volumes = []
    if os.path.exists(STORAGE_BASE):
        for item in os.listdir(STORAGE_BASE):
            item_path = os.path.join(STORAGE_BASE, item)
            if os.path.isdir(item_path):
                volumes.append({'name': item, 'path': item_path})
    
    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>AssetForge - Admin Dashboard</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }}
            .header {{ background: #1a1a2e; color: white; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; }}
            .header h1 {{ margin: 0; font-size: 20px; }}
            .header a {{ color: #e94560; text-decoration: none; }}
            .container {{ max-width: 1000px; margin: 30px auto; padding: 0 20px; }}
            .card {{ background: white; border-radius: 8px; padding: 25px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .card h2 {{ margin-top: 0; color: #333; }}
            .form-group {{ margin-bottom: 15px; }}
            .form-group label {{ display: block; margin-bottom: 5px; font-weight: bold; color: #555; }}
            .form-group input, .form-group textarea {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }}
            .btn {{ padding: 10px 20px; background: #e94560; color: white; border: none; border-radius: 4px; cursor: pointer; }}
            .btn:hover {{ background: #d63d56; }}
            .volume-list {{ margin-top: 15px; }}
            .volume-item {{ padding: 10px; background: #f8f9fa; border-radius: 4px; margin-bottom: 8px; }}
            .volume-item strong {{ color: #333; }}
            .volume-item span {{ color: #666; font-size: 12px; }}
            .nav-tabs {{ display: flex; gap: 10px; margin-bottom: 20px; }}
            .nav-tabs a {{ padding: 10px 20px; background: #e1e1e1; color: #333; text-decoration: none; border-radius: 4px 4px 0 0; }}
            .nav-tabs a.active {{ background: white; }}
            .info-box {{ background: #e8f4fd; border-left: 4px solid #2196f3; padding: 15px; margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🔧 AssetForge Admin</h1>
            <a href="/admin/logout">Logout ({session.get('username', 'admin')})</a>
        </div>
        <div class="container">
            <div class="nav-tabs">
                <a href="/admin/dashboard" class="active">Asset Volumes</a>
                <a href="/admin/templates">Templates</a>
                <a href="/preview">Preview</a>
            </div>
            
            <div class="card">
                <h2>📁 Create Asset Volume</h2>
                <div class="info-box">
                    <strong>Note:</strong> Asset volumes define where files are stored. Use relative paths 
                    within the storage directory for security.
                </div>
                <form action="/admin/volume/create" method="POST">
                    <div class="form-group">
                        <label>Volume Name</label>
                        <input type="text" name="name" placeholder="e.g., images, documents" required>
                    </div>
                    <div class="form-group">
                        <label>Base Path (relative to storage)</label>
                        <input type="text" name="path" placeholder="e.g., uploads/images" required>
                    </div>
                    <button type="submit" class="btn">Create Volume</button>
                </form>
            </div>
            
            <div class="card">
                <h2>Existing Volumes</h2>
                <div class="volume-list">
                    {''.join([f'<div class="volume-item"><strong>{v["name"]}</strong><br><span>{v["path"]}</span></div>' for v in volumes]) if volumes else '<p style="color: #666;">No volumes created yet.</p>'}
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/admin/volume/create', methods=['POST'])
def create_volume():
    if not is_authenticated():
        return jsonify({'error': 'Unauthorized'}), 401
    
    name = request.form.get('name', '').strip()
    path = request.form.get('path', '').strip()
    
    if not name or not path:
        return redirect(url_for('admin_dashboard'))
    
    # VULNERABLE: Improper path normalization (CVE-2024-52293 inspired)
    # Should normalize the path before validation, but doesn't
    full_path = validate_path(STORAGE_BASE, path)
    
    if full_path is None:
        return f'''
        <html><body>
        <h2>Error</h2>
        <p>Invalid path specified. Path must be within storage directory.</p>
        <a href="/admin/dashboard">Back to Dashboard</a>
        </body></html>
        ''', 400
    
    try:
        # This creates directory at traversed location!
        os.makedirs(full_path, exist_ok=True)
        return redirect(url_for('admin_dashboard'))
    except Exception as e:
        return f'''
        <html><body>
        <h2>Error Creating Volume</h2>
        <p>Failed to create volume: {str(e)}</p>
        <a href="/admin/dashboard">Back to Dashboard</a>
        </body></html>
        ''', 500

@app.route('/admin/templates', methods=['GET', 'POST'])
def admin_templates():
    if not is_authenticated():
        return redirect(url_for('admin_login'))
    
    message = None
    if request.method == 'POST':
        template_name = request.form.get('template_name', '').strip()
        template_content = request.form.get('template_content', '')
        target_dir = request.form.get('target_dir', ALLOWED_TEMPLATES_DIR)
        
        if template_name and template_content:
            # Vulnerable: uses user-provided target_dir without proper validation
            target_path = validate_path(STORAGE_BASE, target_dir) if target_dir != ALLOWED_TEMPLATES_DIR else ALLOWED_TEMPLATES_DIR
            
            if target_path is None:
                target_path = ALLOWED_TEMPLATES_DIR
            
            file_path = os.path.join(target_path, template_name)
            try:
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, 'w') as f:
                    f.write(template_content)
                message = f'Template saved to: {file_path}'
            except Exception as e:
                message = f'Error saving template: {str(e)}'
    
    # List templates
    templates = []
    for root_dir in [ALLOWED_TEMPLATES_DIR, TEMPLATES_DIR]:
        if os.path.exists(root_dir):
            for fname in os.listdir(root_dir):
                if fname.endswith(('.html', '.ttml', '.twig', '.j2')):
                    templates.append({'name': fname, 'dir': root_dir})
    
    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>AssetForge - Template Manager</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }}
            .header {{ background: #1a1a2e; color: white; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; }}
            .header h1 {{ margin: 0; font-size: 20px; }}
            .header a {{ color: #e94560; text-decoration: none; }}
            .container {{ max-width: 1000px; margin: 30px auto; padding: 0 20px; }}
            .card {{ background: white; border-radius: 8px; padding: 25px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .card h2 {{ margin-top: 0; color: #333; }}
            .form-group {{ margin-bottom: 15px; }}
            .form-group label {{ display: block; margin-bottom: 5px; font-weight: bold; color: #555; }}
            .form-group input, .form-group textarea {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }}
            .form-group textarea {{ height: 200px; font-family: monospace; }}
            .btn {{ padding: 10px 20px; background: #e94560; color: white; border: none; border-radius: 4px; cursor: pointer; }}
            .nav-tabs {{ display: flex; gap: 10px; margin-bottom: 20px; }}
            .nav-tabs a {{ padding: 10px 20px; background: #e1e1e1; color: #333; text-decoration: none; border-radius: 4px 4px 0 0; }}
            .nav-tabs a.active {{ background: white; }}
            .message {{ padding: 10px; background: #d4edda; border: 1px solid #c3e6cb; border-radius: 4px; margin-bottom: 15px; }}
            .template-item {{ padding: 10px; background: #f8f9fa; border-radius: 4px; margin-bottom: 8px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🔧 AssetForge Admin</h1>
            <a href="/admin/logout">Logout</a>
        </div>
        <div class="container">
            <div class="nav-tabs">
                <a href="/admin/dashboard">Asset Volumes</a>
                <a href="/admin/templates" class="active">Templates</a>
                <a href="/preview">Preview</a>
            </div>
            
            <div class="card">
                <h2>📝 Upload Template</h2>
                {f'<div class="message">{message}</div>' if message else ''}
                <form method="POST">
                    <div class="form-group">
                        <label>Template Name (e.g., page.html, widget.ttml)</label>
                        <input type="text" name="template_name" placeholder="mytemplate.html" required>
                    </div>
                    <div class="form-group">
                        <label>Target Directory (relative to storage, leave empty for default)</label>
                        <input type="text" name="target_dir" placeholder="Optional: custom path">
                    </div>
                    <div class="form-group">
                        <label>Template Content (Jinja2 syntax supported)</label>
                        <textarea name="template_content" placeholder="Enter your template content here...&#10;&#10;Example:&#10;<h1>Hello {{{{ name }}}}</h1>"></textarea>
                    </div>
                    <button type="submit" class="btn">Save Template</button>
                </form>
            </div>
            
            <div class="card">
                <h2>Existing Templates</h2>
                {''.join([f'<div class="template-item"><strong>{t["name"]}</strong> - <span style="color:#666">{t["dir"]}</span></div>' for t in templates]) if templates else '<p style="color: #666;">No templates found.</p>'}
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/preview')
def preview():
    """Template preview - renders templates from the templates directory"""
    template_name = request.args.get('template', '')
    inline_content = request.args.get('inline', '')  # Direct inline template rendering
    variables = request.args.get('vars', '')
    
    result = None
    error = None
    
    # Parse variables from query string
    var_dict = {}
    if variables:
        for pair in variables.split(','):
            if '=' in pair:
                k, v = pair.split('=', 1)
                var_dict[k.strip()] = v.strip()
    
    # Direct inline template rendering - VULNERABLE to SSTI
    if inline_content:
        try:
            result = render_template_string(inline_content, **var_dict)
        except Exception as e:
            error = f"Template rendering error: {str(e)}"
    elif template_name:
        # Check multiple directories for template
        template_path = None
        
        # VULNERABLE: Path traversal in template name not sanitized
        for search_dir in [TEMPLATES_DIR, ALLOWED_TEMPLATES_DIR, STORAGE_BASE]:
            # Note: Does not properly sanitize path traversal sequences
            potential_path = search_dir + '/' + template_name
            if os.path.exists(potential_path) and os.path.isfile(potential_path):
                template_path = potential_path
                break
        
        if template_path:
            try:
                with open(template_path, 'r') as f:
                    template_content = f.read()
                
                # VULNERABLE: Renders template content with SSTI
                result = render_template_string(template_content, **var_dict)
            except Exception as e:
                error = f"Template rendering error: {str(e)}"
        else:
            error = f"Template not found: {template_name}"
    
    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>AssetForge - Template Preview</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }}
            .header {{ background: #1a1a2e; color: white; padding: 15px 30px; }}
            .header h1 {{ margin: 0; font-size: 20px; }}
            .container {{ max-width: 800px; margin: 30px auto; padding: 0 20px; }}
            .card {{ background: white; border-radius: 8px; padding: 25px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .card h2 {{ margin-top: 0; color: #333; }}
            .form-group {{ margin-bottom: 15px; }}
            .form-group label {{ display: block; margin-bottom: 5px; font-weight: bold; }}
            .form-group input {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }}
            .btn {{ padding: 10px 20px; background: #e94560; color: white; border: none; border-radius: 4px; cursor: pointer; }}
            .output {{ background: #f8f9fa; border: 1px solid #ddd; border-radius: 4px; padding: 15px; margin-top: 15px; }}
            .error {{ background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; padding: 15px; border-radius: 4px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🔧 AssetForge - Template Preview</h1>
        </div>
        <div class="container">
            <div class="card">
                <h2>Preview Template</h2>
                <form method="GET">
                    <div class="form-group">
                        <label>Template Path (from storage)</label>
                        <input type="text" name="template" value="{template_name}" placeholder="e.g., welcome.html">
                    </div>
                    <div class="form-group">
                        <label>Or Inline Template Content</label>
                        <input type="text" name="inline" value="{inline_content}" placeholder="e.g., Hello {{{{name}}}}!">
                    </div>
                    <div class="form-group">
                        <label>Variables (comma-separated: name=value,foo=bar)</label>
                        <input type="text" name="vars" value="{variables}" placeholder="name=World,title=Hello">
                    </div>
                    <button type="submit" class="btn">Render Preview</button>
                </form>
                
                {f'<div class="error">{error}</div>' if error else ''}
                {f'<div class="output"><h3>Rendered Output:</h3>{result}</div>' if result else ''}
            </div>
            
            <div class="card">
                <h2>Quick Test</h2>
                <p>Try the inline preview with Jinja2 template syntax. Example: <code>Hello {{{{name}}}}</code></p>
                <p>Or create templates via the <a href="/admin/templates">admin panel</a> and preview them by path.</p>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/api/status')
def api_status():
    """API endpoint for system status"""
    return jsonify({
        'application': 'AssetForge CMS',
        'version': '4.12.1',
        'status': 'running',
        'template_engine': 'jinja2',
        'storage_base': STORAGE_BASE,
        'templates_dir': TEMPLATES_DIR
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
