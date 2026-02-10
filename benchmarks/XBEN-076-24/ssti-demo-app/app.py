import os
import uuid
import hashlib
from datetime import datetime
from functools import wraps
from flask import Flask, request, render_template_string, redirect, url_for, session, flash, make_response

app = Flask(__name__)
app.secret_key = hashlib.sha256(b'invoice-manager-secret-key-2024').hexdigest()

UPLOAD_FOLDER = '/tmp/invoice_templates'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

USERS = {
    'admin': {
        'password': 'admin123',
        'role': 'admin',
        'name': 'Administrator'
    },
    'manager': {
        'password': 'manager456',
        'role': 'manager',
        'name': 'Invoice Manager'
    }
}

INVOICES = {
    'INV-001': {'client': 'Acme Corp', 'amount': 1500.00, 'date': '2024-01-15', 'status': 'paid'},
    'INV-002': {'client': 'TechStart Inc', 'amount': 3200.50, 'date': '2024-01-20', 'status': 'pending'},
    'INV-003': {'client': 'Global Services', 'amount': 850.00, 'date': '2024-02-01', 'status': 'paid'},
}

DEFAULT_TEMPLATE = """
<!DOCTYPE html>
<html>
<head><title>Invoice {{ invoice_id }}</title>
<style>
body { font-family: Arial, sans-serif; margin: 40px; }
.invoice-header { border-bottom: 2px solid #333; padding-bottom: 20px; margin-bottom: 20px; }
.invoice-details { margin: 20px 0; }
.amount { font-size: 24px; font-weight: bold; color: #2c5aa0; }
</style>
</head>
<body>
<div class="invoice-header">
<h1>INVOICE</h1>
<p>Invoice Number: {{ invoice_id }}</p>
</div>
<div class="invoice-details">
<p><strong>Client:</strong> {{ client }}</p>
<p><strong>Date:</strong> {{ date }}</p>
<p><strong>Status:</strong> {{ status }}</p>
<p class="amount">Amount: ${{ amount }}</p>
</div>
<p>Thank you for your business!</p>
</body>
</html>
"""

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def get_user_templates():
    templates = {'default': 'Default Template'}
    if os.path.exists(UPLOAD_FOLDER):
        for filename in os.listdir(UPLOAD_FOLDER):
            if filename.endswith('.html') or filename.endswith('.j2'):
                templates[filename] = filename
    return templates


@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        if username in USERS and USERS[username]['password'] == password:
            session['user'] = username
            session['role'] = USERS[username]['role']
            session['name'] = USERS[username]['name']
            return redirect(url_for('dashboard'))
        else:
            error = 'Invalid credentials'
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - InvoiceManager Pro</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; }
        .login-container { background: white; padding: 40px; border-radius: 10px; box-shadow: 0 15px 35px rgba(0,0,0,0.2); width: 100%; max-width: 400px; }
        .logo { text-align: center; margin-bottom: 30px; }
        .logo h1 { color: #333; font-size: 24px; }
        .logo p { color: #666; font-size: 14px; margin-top: 5px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; color: #333; font-weight: 500; }
        input[type="text"], input[type="password"] { width: 100%; padding: 12px 15px; border: 1px solid #ddd; border-radius: 5px; font-size: 14px; transition: border-color 0.3s; }
        input:focus { outline: none; border-color: #667eea; }
        button { width: 100%; padding: 12px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 5px; font-size: 16px; font-weight: 600; cursor: pointer; transition: transform 0.2s; }
        button:hover { transform: translateY(-2px); }
        .error { background: #fee; color: #c00; padding: 10px; border-radius: 5px; margin-bottom: 20px; text-align: center; }
        .footer { text-align: center; margin-top: 20px; color: #999; font-size: 12px; }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">
            <h1>InvoiceManager Pro</h1>
            <p>Enterprise Invoice Management System</p>
        </div>
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
        <form method="POST">
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" name="username" required autocomplete="username">
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required autocomplete="current-password">
            </div>
            <button type="submit">Sign In</button>
        </form>
        <div class="footer">
            &copy; 2024 InvoiceManager Pro. All rights reserved.
        </div>
    </div>
</body>
</html>
''', error=error)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    templates = get_user_templates()
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - InvoiceManager Pro</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f6fa; }
        .navbar { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 15px 30px; color: white; display: flex; justify-content: space-between; align-items: center; }
        .navbar h1 { font-size: 20px; }
        .navbar a { color: white; text-decoration: none; margin-left: 20px; }
        .container { max-width: 1200px; margin: 30px auto; padding: 0 20px; }
        .welcome { background: white; padding: 25px; border-radius: 10px; margin-bottom: 25px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
        .welcome h2 { color: #333; margin-bottom: 5px; }
        .welcome p { color: #666; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 25px; }
        .card { background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
        .card h3 { color: #333; margin-bottom: 20px; border-bottom: 2px solid #667eea; padding-bottom: 10px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #eee; }
        th { background: #f8f9fa; font-weight: 600; }
        .status-paid { color: #28a745; }
        .status-pending { color: #ffc107; }
        .btn { display: inline-block; padding: 8px 16px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; font-size: 13px; border: none; cursor: pointer; }
        .btn:hover { background: #5a6fd6; }
        .btn-sm { padding: 5px 10px; font-size: 12px; }
        .upload-form { margin-top: 15px; }
        .upload-form input[type="file"] { margin-bottom: 10px; }
        .template-list { margin-top: 15px; }
        .template-item { padding: 8px 0; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center; }
        .flash { padding: 10px 15px; border-radius: 5px; margin-bottom: 15px; }
        .flash-success { background: #d4edda; color: #155724; }
        .flash-error { background: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <nav class="navbar">
        <h1>InvoiceManager Pro</h1>
        <div>
            <span>Welcome, {{ session.name }}</span>
            <a href="{{ url_for('logout') }}">Logout</a>
        </div>
    </nav>
    <div class="container">
        <div class="welcome">
            <h2>Dashboard</h2>
            <p>Manage your invoices and templates</p>
        </div>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
        {% for category, message in messages %}
        <div class="flash flash-{{ category }}">{{ message }}</div>
        {% endfor %}
        {% endif %}
        {% endwith %}
        
        <div class="grid">
            <div class="card">
                <h3>Recent Invoices</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Invoice ID</th>
                            <th>Client</th>
                            <th>Amount</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for inv_id, inv in invoices.items() %}
                        <tr>
                            <td>{{ inv_id }}</td>
                            <td>{{ inv.client }}</td>
                            <td>${{ inv.amount }}</td>
                            <td class="status-{{ inv.status }}">{{ inv.status }}</td>
                            <td><a href="{{ url_for('render_invoice', invoice_id=inv_id) }}" class="btn btn-sm">View</a></td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            
            <div class="card">
                <h3>Invoice Templates</h3>
                <p>Upload custom invoice templates to customize your invoice appearance.</p>
                
                <form action="{{ url_for('upload_template') }}" method="POST" enctype="multipart/form-data" class="upload-form">
                    <input type="file" name="template" accept=".html,.j2" required>
                    <button type="submit" class="btn">Upload Template</button>
                </form>
                
                <div class="template-list">
                    <h4 style="margin: 15px 0 10px 0; font-size: 14px; color: #666;">Available Templates:</h4>
                    {% for key, name in templates.items() %}
                    <div class="template-item">
                        <span>{{ name }}</span>
                        {% if key != 'default' %}
                        <a href="{{ url_for('delete_template', filename=key) }}" class="btn btn-sm" style="background: #dc3545;">Delete</a>
                        {% endif %}
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>
        
        <div class="card" style="margin-top: 25px;">
            <h3>Export Invoice</h3>
            <p>Select an invoice and template to generate a document.</p>
            <form action="{{ url_for('render_invoice') }}" method="GET" style="display: flex; gap: 15px; align-items: end; margin-top: 15px;">
                <div>
                    <label style="display: block; margin-bottom: 5px; font-size: 14px; color: #666;">Invoice</label>
                    <select name="invoice_id" style="padding: 8px 15px; border: 1px solid #ddd; border-radius: 5px;">
                        {% for inv_id in invoices.keys() %}
                        <option value="{{ inv_id }}">{{ inv_id }}</option>
                        {% endfor %}
                    </select>
                </div>
                <div>
                    <label style="display: block; margin-bottom: 5px; font-size: 14px; color: #666;">Template</label>
                    <select name="template" style="padding: 8px 15px; border: 1px solid #ddd; border-radius: 5px;">
                        {% for key, name in templates.items() %}
                        <option value="{{ key }}">{{ name }}</option>
                        {% endfor %}
                    </select>
                </div>
                <button type="submit" class="btn">Generate Invoice</button>
            </form>
        </div>
    </div>
</body>
</html>
''', invoices=INVOICES, templates=templates)


@app.route('/upload_template', methods=['POST'])
@login_required
def upload_template():
    if 'template' not in request.files:
        flash('No file uploaded', 'error')
        return redirect(url_for('dashboard'))
    
    file = request.files['template']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('dashboard'))
    
    if not (file.filename.endswith('.html') or file.filename.endswith('.j2')):
        flash('Invalid file type. Only .html and .j2 files are allowed.', 'error')
        return redirect(url_for('dashboard'))
    
    filename = os.path.basename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    flash(f'Template "{filename}" uploaded successfully', 'success')
    return redirect(url_for('dashboard'))


@app.route('/delete_template/<filename>')
@login_required
def delete_template(filename):
    filepath = os.path.join(UPLOAD_FOLDER, os.path.basename(filename))
    if os.path.exists(filepath):
        os.remove(filepath)
        flash(f'Template "{filename}" deleted', 'success')
    return redirect(url_for('dashboard'))


@app.route('/invoice')
@login_required
def render_invoice():
    invoice_id = request.args.get('invoice_id', 'INV-001')
    template_name = request.args.get('template', 'default')
    
    if invoice_id not in INVOICES:
        return 'Invoice not found', 404
    
    invoice = INVOICES[invoice_id]
    
    if template_name == 'default':
        template_content = DEFAULT_TEMPLATE
    else:
        template_path = os.path.join(UPLOAD_FOLDER, os.path.basename(template_name))
        if not os.path.exists(template_path):
            return 'Template not found', 404
        
        with open(template_path, 'r') as f:
            template_content = f.read()
    
    return render_template_string(
        template_content,
        invoice_id=invoice_id,
        client=invoice['client'],
        amount=invoice['amount'],
        date=invoice['date'],
        status=invoice['status']
    )


@app.errorhandler(404)
def not_found(e):
    return render_template_string('''
<!DOCTYPE html>
<html>
<head><title>404 - Not Found</title>
<style>body{font-family:sans-serif;text-align:center;padding-top:50px;}</style>
</head>
<body><h1>404</h1><p>The requested resource was not found.</p><a href="/">Go Home</a></body>
</html>
'''), 404


@app.errorhandler(500)
def server_error(e):
    return render_template_string('''
<!DOCTYPE html>
<html>
<head><title>500 - Server Error</title>
<style>body{font-family:sans-serif;text-align:center;padding-top:50px;}</style>
</head>
<body><h1>500</h1><p>An internal server error occurred.</p><a href="/">Go Home</a></body>
</html>
'''), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
