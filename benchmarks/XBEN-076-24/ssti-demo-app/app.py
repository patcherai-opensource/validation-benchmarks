import os
import uuid
from flask import Flask, request, render_template_string, redirect, url_for, session, flash
from functools import wraps

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Simple in-memory user storage (simulating an authenticated system)
USERS = {
    'admin': 'admin123',
    'manager': 'manager123'
}

# Directory for uploaded templates
TEMPLATE_DIR = '/app/invoice_templates'
os.makedirs(TEMPLATE_DIR, exist_ok=True)

# Create a default template
DEFAULT_TEMPLATE = '''<!DOCTYPE html>
<html>
<head><title>Invoice</title></head>
<body>
<h1>Invoice #{{ invoice_id }}</h1>
<p>Customer: {{ customer_name }}</p>
<p>Amount: ${{ amount }}</p>
<p>Date: {{ date }}</p>
</body>
</html>'''

with open(os.path.join(TEMPLATE_DIR, 'default.html'), 'w') as f:
    f.write(DEFAULT_TEMPLATE)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        if username in USERS and USERS[username] == password:
            session['user'] = username
            flash(f'Welcome, {username}!', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid credentials', 'error')
    
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Kimai - Login</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 400px; margin: 50px auto; padding: 20px; }
            h1 { color: #333; }
            input { width: 100%; padding: 10px; margin: 10px 0; box-sizing: border-box; }
            button { width: 100%; padding: 10px; background: #007bff; color: white; border: none; cursor: pointer; }
            .error { color: red; }
            .info { color: #666; font-size: 0.9em; margin-top: 20px; }
        </style>
    </head>
    <body>
        <h1>Kimai Time Tracking</h1>
        <h2>Login</h2>
        <form method="POST">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Login</button>
        </form>
        <p class="info">Demo accounts: admin/admin123, manager/manager123</p>
    </body>
    </html>
    '''


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    templates = os.listdir(TEMPLATE_DIR)
    template_list = ''.join([f'<li><a href="/invoice/preview?template={t}">{t}</a> '
                             f'[<a href="/invoice/download?template={t}">Download Invoice</a>]</li>' 
                             for t in templates])
    
    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Kimai - Dashboard</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }}
            h1, h2 {{ color: #333; }}
            .nav {{ margin-bottom: 20px; }}
            .nav a {{ margin-right: 15px; }}
            ul {{ list-style: none; padding: 0; }}
            li {{ padding: 10px; background: #f5f5f5; margin: 5px 0; }}
            .upload-form {{ background: #e9ecef; padding: 20px; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <div class="nav">
            <a href="/dashboard">Dashboard</a>
            <a href="/invoice/upload">Upload Template</a>
            <a href="/logout">Logout</a>
        </div>
        <h1>Kimai Dashboard</h1>
        <p>Welcome, {session['user']}!</p>
        
        <h2>Invoice Templates</h2>
        <ul>{template_list}</ul>
        
        <h2>Quick Actions</h2>
        <p><a href="/invoice/upload">Upload a new invoice template</a></p>
    </body>
    </html>
    '''


@app.route('/invoice/upload', methods=['GET', 'POST'])
@login_required
def upload_template():
    if request.method == 'POST':
        if 'template' not in request.files:
            flash('No file uploaded', 'error')
            return redirect(request.url)
        
        file = request.files['template']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        # Allow .html and .twig files (vulnerable: no content validation)
        allowed_extensions = ['.html', '.twig', '.jinja2', '.j2']
        ext = os.path.splitext(file.filename)[1].lower()
        
        if ext not in allowed_extensions:
            flash(f'Invalid file type. Allowed: {", ".join(allowed_extensions)}', 'error')
            return redirect(request.url)
        
        # Generate unique filename to avoid collisions
        filename = f"{uuid.uuid4().hex[:8]}_{file.filename}"
        filepath = os.path.join(TEMPLATE_DIR, filename)
        
        # Save the uploaded template (vulnerable: user-controlled content)
        file.save(filepath)
        flash(f'Template "{filename}" uploaded successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Kimai - Upload Template</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            h1, h2 { color: #333; }
            .nav { margin-bottom: 20px; }
            .nav a { margin-right: 15px; }
            .upload-form { background: #e9ecef; padding: 20px; margin: 20px 0; }
            input[type="file"] { margin: 10px 0; }
            button { padding: 10px 20px; background: #007bff; color: white; border: none; cursor: pointer; }
            .info { color: #666; font-size: 0.9em; }
        </style>
    </head>
    <body>
        <div class="nav">
            <a href="/dashboard">Dashboard</a>
            <a href="/invoice/upload">Upload Template</a>
            <a href="/logout">Logout</a>
        </div>
        <h1>Upload Invoice Template</h1>
        <div class="upload-form">
            <form method="POST" enctype="multipart/form-data">
                <p>Select a template file to upload:</p>
                <input type="file" name="template" accept=".html,.twig,.jinja2,.j2" required>
                <br><br>
                <button type="submit">Upload Template</button>
            </form>
        </div>
        <p class="info">Supported formats: .html, .twig, .jinja2, .j2</p>
        <p class="info">Templates use Jinja2 syntax. Available variables: invoice_id, customer_name, amount, date</p>
    </body>
    </html>
    '''


@app.route('/invoice/preview')
@login_required
def preview_invoice():
    template_name = request.args.get('template', 'default.html')
    
    # Prevent directory traversal
    template_name = os.path.basename(template_name)
    template_path = os.path.join(TEMPLATE_DIR, template_name)
    
    if not os.path.exists(template_path):
        return 'Template not found', 404
    
    # Read the template content
    with open(template_path, 'r') as f:
        template_content = f.read()
    
    # Sample invoice data
    invoice_data = {
        'invoice_id': '2024-001',
        'customer_name': 'ACME Corp',
        'amount': '1,500.00',
        'date': '2024-01-15'
    }
    
    # VULNERABLE: Render user-uploaded template without sandboxing
    # This is equivalent to the Kimai vulnerability where Twig templates
    # are rendered without security policies
    try:
        rendered = render_template_string(template_content, **invoice_data)
        return rendered
    except Exception as e:
        return f'Template rendering error: {str(e)}', 500


@app.route('/invoice/download')
@login_required
def download_invoice():
    template_name = request.args.get('template', 'default.html')
    
    # Prevent directory traversal
    template_name = os.path.basename(template_name)
    template_path = os.path.join(TEMPLATE_DIR, template_name)
    
    if not os.path.exists(template_path):
        return 'Template not found', 404
    
    # Read the template content
    with open(template_path, 'r') as f:
        template_content = f.read()
    
    # Sample invoice data
    invoice_data = {
        'invoice_id': '2024-001',
        'customer_name': 'ACME Corp',
        'amount': '1,500.00',
        'date': '2024-01-15'
    }
    
    # VULNERABLE: Render user-uploaded template without sandboxing
    try:
        rendered = render_template_string(template_content, **invoice_data)
        return rendered, 200, {
            'Content-Type': 'text/html',
            'Content-Disposition': f'attachment; filename="invoice_{template_name}"'
        }
    except Exception as e:
        return f'Template rendering error: {str(e)}', 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
