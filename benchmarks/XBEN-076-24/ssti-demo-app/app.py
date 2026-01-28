import os
import uuid
import json
from flask import Flask, request, render_template_string, redirect, url_for, session, jsonify
from functools import wraps

app = Flask(__name__)
app.secret_key = os.urandom(24)

# User database (simulated)
USERS = {
    'admin': {'password': 'K1m@i_Adm1n_2023!', 'role': 'admin'},
    'manager': {'password': 'T1m3Tr@ck3r', 'role': 'manager'},
    'employee': {'password': 'W0rk3r_P@ss', 'role': 'employee'}
}

# Template storage (in-memory, simulating file uploads)
INVOICE_TEMPLATES = {
    'default': {
        'name': 'Standard Invoice',
        'content': '''
<h2>Invoice #{{ invoice_id }}</h2>
<p>Client: {{ client_name }}</p>
<p>Amount: ${{ amount }}</p>
<p>Date: {{ date }}</p>
''',
        'owner': 'system'
    },
    'compact': {
        'name': 'Compact Format',
        'content': '''
<div class="invoice-compact">
<strong>INV-{{ invoice_id }}</strong> | {{ client_name }} | ${{ amount }}
</div>
''',
        'owner': 'system'
    }
}

# Time entries storage (simulated)
TIME_ENTRIES = [
    {'id': 1, 'project': 'Website Redesign', 'hours': 8, 'user': 'employee', 'date': '2024-01-15'},
    {'id': 2, 'project': 'API Development', 'hours': 6, 'user': 'employee', 'date': '2024-01-16'},
    {'id': 3, 'project': 'Client Meeting', 'hours': 2, 'user': 'manager', 'date': '2024-01-16'},
]

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def manager_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        if session.get('role') not in ['admin', 'manager']:
            return jsonify({'error': 'Insufficient permissions'}), 403
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>TimeTrack Pro - Time Management System</title>
        <style>
            body { font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 0; background: #f5f7fa; }
            .header { background: linear-gradient(135deg, #2c3e50, #3498db); color: white; padding: 20px 40px; }
            .header h1 { margin: 0; font-size: 28px; }
            .header .tagline { opacity: 0.8; font-size: 14px; }
            .container { max-width: 1000px; margin: 40px auto; padding: 0 20px; }
            .card { background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); padding: 30px; margin-bottom: 20px; }
            .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-top: 30px; }
            .feature { text-align: center; padding: 20px; }
            .feature h3 { color: #2c3e50; margin-bottom: 10px; }
            .feature p { color: #666; font-size: 14px; }
            .btn { display: inline-block; background: #3498db; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; }
            .btn:hover { background: #2980b9; }
            .login-link { text-align: center; margin-top: 30px; }
            .footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>⏱️ TimeTrack Pro</h1>
            <div class="tagline">Professional Time Management & Invoicing</div>
        </div>
        <div class="container">
            <div class="card">
                <h2>Welcome to TimeTrack Pro</h2>
                <p>The complete solution for time tracking, project management, and automated invoicing.</p>
                
                <div class="features">
                    <div class="feature">
                        <h3>📊 Time Tracking</h3>
                        <p>Log your work hours with precision</p>
                    </div>
                    <div class="feature">
                        <h3>📁 Projects</h3>
                        <p>Organize work by client and project</p>
                    </div>
                    <div class="feature">
                        <h3>📄 Invoicing</h3>
                        <p>Generate professional invoices</p>
                    </div>
                    <div class="feature">
                        <h3>📈 Reports</h3>
                        <p>Analytics and insights</p>
                    </div>
                </div>
                
                <div class="login-link">
                    <a href="/login" class="btn">Login to Dashboard</a>
                </div>
            </div>
        </div>
        <div class="footer">
            <p>TimeTrack Pro v2.0.9 &copy; 2024</p>
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
        
        if username in USERS and USERS[username]['password'] == password:
            session['user'] = username
            session['role'] = USERS[username]['role']
            return redirect(url_for('dashboard'))
        else:
            error = 'Invalid credentials'
    
    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Login - TimeTrack Pro</title>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 0; background: linear-gradient(135deg, #2c3e50, #3498db); min-height: 100vh; display: flex; align-items: center; justify-content: center; }}
            .login-box {{ background: white; padding: 40px; border-radius: 10px; box-shadow: 0 10px 40px rgba(0,0,0,0.3); width: 350px; }}
            .login-box h2 {{ margin: 0 0 30px 0; color: #2c3e50; text-align: center; }}
            .form-group {{ margin-bottom: 20px; }}
            .form-group label {{ display: block; margin-bottom: 5px; color: #555; font-weight: bold; }}
            .form-group input {{ width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }}
            .btn {{ width: 100%; background: #3498db; color: white; padding: 12px; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; }}
            .btn:hover {{ background: #2980b9; }}
            .error {{ color: #e74c3c; text-align: center; margin-bottom: 15px; }}
            .back-link {{ text-align: center; margin-top: 20px; }}
            .back-link a {{ color: #3498db; text-decoration: none; }}
        </style>
    </head>
    <body>
        <div class="login-box">
            <h2>⏱️ TimeTrack Pro</h2>
            {'<p class="error">' + error + '</p>' if error else ''}
            <form method="POST">
                <div class="form-group">
                    <label for="username">Username</label>
                    <input type="text" id="username" name="username" required>
                </div>
                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" name="password" required>
                </div>
                <button type="submit" class="btn">Login</button>
            </form>
            <div class="back-link">
                <a href="/">← Back to Home</a>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    user = session.get('user')
    role = session.get('role')
    
    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Dashboard - TimeTrack Pro</title>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 0; background: #f5f7fa; }}
            .header {{ background: linear-gradient(135deg, #2c3e50, #3498db); color: white; padding: 15px 40px; display: flex; justify-content: space-between; align-items: center; }}
            .header h1 {{ margin: 0; font-size: 22px; }}
            .user-info {{ font-size: 14px; }}
            .user-info a {{ color: white; margin-left: 15px; }}
            .container {{ max-width: 1200px; margin: 30px auto; padding: 0 20px; }}
            .nav {{ display: flex; gap: 10px; margin-bottom: 30px; flex-wrap: wrap; }}
            .nav a {{ background: white; padding: 12px 20px; text-decoration: none; color: #2c3e50; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
            .nav a:hover {{ background: #3498db; color: white; }}
            .card {{ background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); padding: 25px; margin-bottom: 20px; }}
            .card h2 {{ margin-top: 0; color: #2c3e50; }}
            .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }}
            .stat {{ text-align: center; padding: 20px; background: #f8f9fa; border-radius: 5px; }}
            .stat-value {{ font-size: 32px; font-weight: bold; color: #3498db; }}
            .stat-label {{ color: #666; font-size: 14px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>⏱️ TimeTrack Pro</h1>
            <div class="user-info">
                Logged in as <strong>{user}</strong> ({role})
                <a href="/logout">Logout</a>
            </div>
        </div>
        <div class="container">
            <div class="nav">
                <a href="/dashboard">Dashboard</a>
                <a href="/timesheet">Timesheet</a>
                <a href="/projects">Projects</a>
                {'<a href="/invoices">Invoices</a>' if role in ['admin', 'manager'] else ''}
                {'<a href="/settings">Settings</a>' if role == 'admin' else ''}
                <a href="/api/docs">API</a>
            </div>
            
            <div class="card">
                <h2>Welcome back, {user}!</h2>
                <p>Here's your activity summary for this week.</p>
                
                <div class="stats">
                    <div class="stat">
                        <div class="stat-value">42</div>
                        <div class="stat-label">Hours This Week</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">5</div>
                        <div class="stat-label">Active Projects</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">3</div>
                        <div class="stat-label">Pending Invoices</div>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h2>Recent Time Entries</h2>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr style="border-bottom: 1px solid #eee;">
                        <th style="text-align: left; padding: 10px;">Project</th>
                        <th style="text-align: left; padding: 10px;">Hours</th>
                        <th style="text-align: left; padding: 10px;">Date</th>
                    </tr>
                    {''.join(f'<tr style="border-bottom: 1px solid #eee;"><td style="padding: 10px;">{e["project"]}</td><td style="padding: 10px;">{e["hours"]}</td><td style="padding: 10px;">{e["date"]}</td></tr>' for e in TIME_ENTRIES[:5])}
                </table>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/timesheet')
@login_required  
def timesheet():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Timesheet - TimeTrack Pro</title>
        <style>
            body { font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 20px; background: #f5f7fa; }
            .container { max-width: 800px; margin: 0 auto; }
            h1 { color: #2c3e50; }
            .entry-form { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
            .form-row { display: flex; gap: 15px; margin-bottom: 15px; }
            .form-row input, .form-row select { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
            .btn { background: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>⏱️ Timesheet</h1>
            <div class="entry-form">
                <h3>Log Time Entry</h3>
                <form>
                    <div class="form-row">
                        <select name="project">
                            <option>Website Redesign</option>
                            <option>API Development</option>
                            <option>Client Meeting</option>
                        </select>
                        <input type="number" name="hours" placeholder="Hours" min="0.5" max="24" step="0.5">
                        <input type="date" name="date">
                    </div>
                    <div class="form-row">
                        <input type="text" name="description" placeholder="Description (optional)">
                    </div>
                    <button type="submit" class="btn">Log Entry</button>
                </form>
            </div>
            <p><a href="/dashboard">← Back to Dashboard</a></p>
        </div>
    </body>
    </html>
    '''

@app.route('/projects')
@login_required
def projects():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Projects - TimeTrack Pro</title>
        <style>
            body { font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 20px; background: #f5f7fa; }
            .container { max-width: 800px; margin: 0 auto; }
            h1 { color: #2c3e50; }
            .project-list { background: white; border-radius: 8px; overflow: hidden; }
            .project { padding: 20px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; }
            .project:last-child { border-bottom: none; }
            .project-name { font-weight: bold; color: #2c3e50; }
            .project-client { color: #666; font-size: 14px; }
            .project-hours { color: #3498db; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📁 Projects</h1>
            <div class="project-list">
                <div class="project">
                    <div>
                        <div class="project-name">Website Redesign</div>
                        <div class="project-client">Client: Acme Corp</div>
                    </div>
                    <div class="project-hours">125 hours</div>
                </div>
                <div class="project">
                    <div>
                        <div class="project-name">API Development</div>
                        <div class="project-client">Client: TechStart Inc</div>
                    </div>
                    <div class="project-hours">87 hours</div>
                </div>
                <div class="project">
                    <div>
                        <div class="project-name">Mobile App</div>
                        <div class="project-client">Client: Innovation Labs</div>
                    </div>
                    <div class="project-hours">203 hours</div>
                </div>
            </div>
            <p><a href="/dashboard">← Back to Dashboard</a></p>
        </div>
    </body>
    </html>
    '''

@app.route('/invoices')
@manager_required
def invoices():
    templates_html = ''.join([
        f'<div class="template"><strong>{tpl["name"]}</strong> <span>({tid})</span></div>'
        for tid, tpl in INVOICE_TEMPLATES.items()
    ])
    
    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Invoices - TimeTrack Pro</title>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 20px; background: #f5f7fa; }}
            .container {{ max-width: 900px; margin: 0 auto; }}
            h1 {{ color: #2c3e50; }}
            .section {{ background: white; border-radius: 8px; padding: 25px; margin-bottom: 20px; }}
            .template {{ padding: 10px; border: 1px solid #eee; margin: 5px 0; border-radius: 5px; }}
            .template span {{ color: #999; font-size: 12px; }}
            .btn {{ background: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; text-decoration: none; display: inline-block; }}
            .btn-secondary {{ background: #95a5a6; }}
            .form-group {{ margin-bottom: 15px; }}
            .form-group label {{ display: block; margin-bottom: 5px; font-weight: bold; }}
            .form-group input, .form-group select, .form-group textarea {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }}
            .actions {{ display: flex; gap: 10px; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📄 Invoice Management</h1>
            
            <div class="section">
                <h2>Generate Invoice</h2>
                <form action="/invoice/generate" method="POST">
                    <div class="form-group">
                        <label>Client Name</label>
                        <input type="text" name="client_name" value="Acme Corp" required>
                    </div>
                    <div class="form-group">
                        <label>Invoice Amount ($)</label>
                        <input type="number" name="amount" value="1500" required>
                    </div>
                    <div class="form-group">
                        <label>Template</label>
                        <select name="template_id">
                            {''.join(f'<option value="{tid}">{tpl["name"]}</option>' for tid, tpl in INVOICE_TEMPLATES.items())}
                        </select>
                    </div>
                    <button type="submit" class="btn">Generate Invoice</button>
                </form>
            </div>
            
            <div class="section">
                <h2>Invoice Templates</h2>
                <p>Available templates for invoice generation:</p>
                {templates_html}
                <div class="actions">
                    <a href="/invoice/templates/upload" class="btn">Upload New Template</a>
                </div>
            </div>
            
            <p><a href="/dashboard">← Back to Dashboard</a></p>
        </div>
    </body>
    </html>
    '''

@app.route('/invoice/templates/upload', methods=['GET', 'POST'])
@manager_required
def upload_template():
    message = None
    msg_type = 'info'
    
    if request.method == 'POST':
        template_name = request.form.get('template_name', '').strip()
        template_content = request.form.get('template_content', '').strip()
        
        if not template_name or not template_content:
            message = 'Template name and content are required'
            msg_type = 'error'
        else:
            template_id = template_name.lower().replace(' ', '_')
            INVOICE_TEMPLATES[template_id] = {
                'name': template_name,
                'content': template_content,
                'owner': session.get('user')
            }
            message = f'Template "{template_name}" uploaded successfully'
            msg_type = 'success'
    
    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Upload Template - TimeTrack Pro</title>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 20px; background: #f5f7fa; }}
            .container {{ max-width: 800px; margin: 0 auto; }}
            h1 {{ color: #2c3e50; }}
            .card {{ background: white; border-radius: 8px; padding: 25px; margin-bottom: 20px; }}
            .form-group {{ margin-bottom: 20px; }}
            .form-group label {{ display: block; margin-bottom: 8px; font-weight: bold; color: #2c3e50; }}
            .form-group input, .form-group textarea {{ width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; font-family: inherit; }}
            .form-group textarea {{ min-height: 200px; font-family: monospace; }}
            .btn {{ background: #3498db; color: white; padding: 12px 25px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }}
            .btn:hover {{ background: #2980b9; }}
            .message {{ padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
            .message.success {{ background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
            .message.error {{ background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }}
            .message.info {{ background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }}
            .help-text {{ font-size: 13px; color: #666; margin-top: 5px; }}
            .example {{ background: #f8f9fa; padding: 15px; border-radius: 5px; font-family: monospace; font-size: 13px; white-space: pre-wrap; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📄 Upload Invoice Template</h1>
            
            {f'<div class="message {msg_type}">{message}</div>' if message else ''}
            
            <div class="card">
                <form method="POST">
                    <div class="form-group">
                        <label for="template_name">Template Name</label>
                        <input type="text" id="template_name" name="template_name" placeholder="e.g., Professional Invoice" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="template_content">Template Content (Jinja2 Format)</label>
                        <textarea id="template_content" name="template_content" placeholder="Enter your template content here..." required></textarea>
                        <p class="help-text">Use Jinja2 syntax for dynamic content. Available variables: invoice_id, client_name, amount, date</p>
                    </div>
                    
                    <button type="submit" class="btn">Upload Template</button>
                </form>
            </div>
            
            <div class="card">
                <h3>Template Example</h3>
                <div class="example">&lt;h2&gt;Invoice #{{{{ invoice_id }}}}&lt;/h2&gt;
&lt;p&gt;Client: {{{{ client_name }}}}&lt;/p&gt;
&lt;p&gt;Amount: ${{{{ amount }}}}&lt;/p&gt;
&lt;p&gt;Date: {{{{ date }}}}&lt;/p&gt;</div>
            </div>
            
            <p><a href="/invoices">← Back to Invoices</a></p>
        </div>
    </body>
    </html>
    '''

@app.route('/invoice/generate', methods=['POST'])
@manager_required
def generate_invoice():
    template_id = request.form.get('template_id', 'default')
    client_name = request.form.get('client_name', 'Unknown')
    amount = request.form.get('amount', '0')
    
    if template_id not in INVOICE_TEMPLATES:
        return jsonify({'error': 'Template not found'}), 404
    
    template = INVOICE_TEMPLATES[template_id]
    
    # Generate invoice data
    invoice_data = {
        'invoice_id': str(uuid.uuid4())[:8].upper(),
        'client_name': client_name,
        'amount': amount,
        'date': '2024-01-20'
    }
    
    # VULNERABILITY: Render user-uploaded template without sandboxing
    # This mimics the Kimai CVE-2023-46245 vulnerability
    try:
        rendered = render_template_string(template['content'], **invoice_data)
    except Exception as e:
        return f'''
        <!DOCTYPE html>
        <html>
        <head><title>Error - TimeTrack Pro</title></head>
        <body>
            <h1>Template Rendering Error</h1>
            <p>An error occurred while rendering the invoice template.</p>
            <pre>{str(e)}</pre>
            <p><a href="/invoices">Back to Invoices</a></p>
        </body>
        </html>
        '''
    
    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Invoice - TimeTrack Pro</title>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 20px; background: #f5f7fa; }}
            .container {{ max-width: 800px; margin: 0 auto; }}
            .invoice {{ background: white; border-radius: 8px; padding: 40px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .invoice-header {{ border-bottom: 2px solid #3498db; padding-bottom: 20px; margin-bottom: 20px; }}
            .actions {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; }}
            .btn {{ background: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; text-decoration: none; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="invoice">
                <div class="invoice-header">
                    <h1>TimeTrack Pro Invoice</h1>
                </div>
                <div class="invoice-content">
                    {rendered}
                </div>
                <div class="actions">
                    <a href="/invoices" class="btn">Back to Invoices</a>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/settings')
@login_required
def settings():
    if session.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Settings - TimeTrack Pro</title>
        <style>
            body { font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 20px; background: #f5f7fa; }
            .container { max-width: 800px; margin: 0 auto; }
            h1 { color: #2c3e50; }
            .card { background: white; border-radius: 8px; padding: 25px; margin-bottom: 20px; }
            .setting { display: flex; justify-content: space-between; padding: 15px 0; border-bottom: 1px solid #eee; }
            .setting:last-child { border-bottom: none; }
            .setting-name { font-weight: bold; }
            .setting-value { color: #666; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>⚙️ System Settings</h1>
            <div class="card">
                <h2>Application Configuration</h2>
                <div class="setting">
                    <span class="setting-name">Invoice Template Uploads</span>
                    <span class="setting-value">Enabled</span>
                </div>
                <div class="setting">
                    <span class="setting-name">Max Upload Size</span>
                    <span class="setting-value">10MB</span>
                </div>
                <div class="setting">
                    <span class="setting-name">Template Engine</span>
                    <span class="setting-value">Jinja2</span>
                </div>
                <div class="setting">
                    <span class="setting-name">Template Sandboxing</span>
                    <span class="setting-value">Disabled</span>
                </div>
            </div>
            <p><a href="/dashboard">← Back to Dashboard</a></p>
        </div>
    </body>
    </html>
    '''

@app.route('/robots.txt')
def robots():
    return '''User-agent: *
Disallow: /admin
Disallow: /api/
Disallow: /backup/
Disallow: /invoice/
''', 200, {'Content-Type': 'text/plain'}

@app.route('/backup/users.bak')
def backup_users():
    # Simulated backup file - common misconfiguration
    return '''# TimeTrack Pro User Backup
# Generated: 2024-01-10
# Format: username:role:password_hint
#
admin:admin:Old company (Kimai) + Admin + 2023!
manager:manager:T1m3Tr@ck3r
employee:employee:W0rk3r_P@ss
#
# Note: Passwords use l33t speak where needed
# Admin password references legacy Kimai branding
''', 200, {'Content-Type': 'text/plain'}

@app.route('/api/docs')
def api_docs():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>API Documentation - TimeTrack Pro</title>
        <style>
            body { font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 20px; background: #f5f7fa; }
            .container { max-width: 900px; margin: 0 auto; }
            h1 { color: #2c3e50; }
            .endpoint { background: white; border-radius: 8px; padding: 20px; margin-bottom: 15px; }
            .method { display: inline-block; padding: 5px 10px; border-radius: 3px; font-weight: bold; font-size: 12px; margin-right: 10px; }
            .get { background: #61affe; color: white; }
            .post { background: #49cc90; color: white; }
            .path { font-family: monospace; font-size: 16px; }
            .description { margin-top: 10px; color: #666; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📚 API Documentation</h1>
            <p>TimeTrack Pro REST API v2.0</p>
            
            <div class="endpoint">
                <span class="method get">GET</span>
                <span class="path">/api/time-entries</span>
                <p class="description">List all time entries for the authenticated user</p>
            </div>
            
            <div class="endpoint">
                <span class="method post">POST</span>
                <span class="path">/api/time-entries</span>
                <p class="description">Create a new time entry</p>
            </div>
            
            <div class="endpoint">
                <span class="method get">GET</span>
                <span class="path">/api/projects</span>
                <p class="description">List all projects</p>
            </div>
            
            <div class="endpoint">
                <span class="method get">GET</span>
                <span class="path">/api/invoices</span>
                <p class="description">List generated invoices (manager/admin only)</p>
            </div>
            
            <div class="endpoint">
                <span class="method post">POST</span>
                <span class="path">/api/invoices/render</span>
                <p class="description">Render an invoice using a template</p>
            </div>
            
            <p><a href="/dashboard">← Back to Dashboard</a></p>
        </div>
    </body>
    </html>
    '''

@app.route('/api/time-entries')
@login_required
def api_time_entries():
    return jsonify(TIME_ENTRIES)

@app.route('/api/projects')
@login_required
def api_projects():
    return jsonify([
        {'id': 1, 'name': 'Website Redesign', 'client': 'Acme Corp'},
        {'id': 2, 'name': 'API Development', 'client': 'TechStart Inc'},
        {'id': 3, 'name': 'Mobile App', 'client': 'Innovation Labs'}
    ])

@app.route('/api/invoices')
@manager_required
def api_invoices():
    return jsonify([
        {'id': 'INV-001', 'client': 'Acme Corp', 'amount': 1500, 'status': 'paid'},
        {'id': 'INV-002', 'client': 'TechStart Inc', 'amount': 2300, 'status': 'pending'},
    ])

@app.route('/api/invoices/render', methods=['POST'])
@manager_required
def api_render_invoice():
    data = request.get_json() or {}
    template_id = data.get('template_id', 'default')
    
    if template_id not in INVOICE_TEMPLATES:
        return jsonify({'error': 'Template not found'}), 404
    
    template = INVOICE_TEMPLATES[template_id]
    
    invoice_data = {
        'invoice_id': data.get('invoice_id', str(uuid.uuid4())[:8].upper()),
        'client_name': data.get('client_name', 'Unknown'),
        'amount': data.get('amount', '0'),
        'date': data.get('date', '2024-01-20')
    }
    
    try:
        rendered = render_template_string(template['content'], **invoice_data)
        return jsonify({'rendered': rendered, 'template_used': template_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/status')
def api_status():
    return jsonify({
        'status': 'healthy',
        'version': '2.0.9',
        'uptime': '3d 14h 22m',
        'features': {
            'time_tracking': True,
            'invoicing': True,
            'custom_templates': True,
            'template_engine': 'Jinja2'
        }
    })

@app.route('/api/version')
def api_version():
    return jsonify({
        'application': 'TimeTrack Pro',
        'version': '2.0.9',
        'build': '20240115',
        'framework': 'Flask',
        'python': '3.9'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
