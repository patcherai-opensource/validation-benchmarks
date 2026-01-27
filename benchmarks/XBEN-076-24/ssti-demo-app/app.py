from flask import Flask, request, render_template_string, redirect, url_for, jsonify
import os
import uuid
import re

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/app/templates_custom'
app.config['MAX_CONTENT_LENGTH'] = 64 * 1024  # 64KB max

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# In-memory template storage (simulates database)
templates_db = {}

def get_allowed_extensions():
    return {'twig', 'html', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in get_allowed_extensions()

@app.route('/')
def index():
    template_list = ""
    for tid, tdata in templates_db.items():
        template_list += f'<tr><td>{tdata["name"]}</td><td>{tdata["type"]}</td><td><a href="/invoice/preview/{tid}">Preview</a> | <a href="/invoice/download/{tid}">Download</a></td></tr>'
    
    if not template_list:
        template_list = '<tr><td colspan="3">No templates uploaded yet.</td></tr>'
    
    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>InvoiceGen Pro - Template Manager</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
            .container {{ max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
            h2 {{ color: #34495e; margin-top: 30px; }}
            .upload-form {{ background: #ecf0f1; padding: 20px; border-radius: 5px; margin: 20px 0; }}
            input[type="file"], input[type="text"] {{ padding: 10px; margin: 5px 0; width: 100%; box-sizing: border-box; }}
            button {{ background: #3498db; color: white; padding: 12px 25px; border: none; border-radius: 4px; cursor: pointer; margin-top: 10px; }}
            button:hover {{ background: #2980b9; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background: #3498db; color: white; }}
            tr:hover {{ background: #f5f5f5; }}
            a {{ color: #3498db; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
            .info {{ background: #e8f4f8; padding: 15px; border-left: 4px solid #3498db; margin: 15px 0; }}
            .footer {{ margin-top: 30px; color: #7f8c8d; font-size: 12px; text-align: center; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>InvoiceGen Pro</h1>
            <p>Professional invoice template management system. Upload custom templates and generate beautiful invoices.</p>
            
            <div class="info">
                <strong>Supported formats:</strong> .twig, .html, .txt templates<br>
                <strong>Template variables:</strong> Use {{{{ company_name }}}}, {{{{ invoice_date }}}}, {{{{ total }}}} in your templates.
            </div>
            
            <h2>Upload New Template</h2>
            <div class="upload-form">
                <form action="/invoice/document_upload" method="POST" enctype="multipart/form-data">
                    <label>Template Name:</label>
                    <input type="text" name="template_name" placeholder="My Invoice Template" required>
                    <label>Template File (.twig, .html, .txt):</label>
                    <input type="file" name="template_file" accept=".twig,.html,.txt" required>
                    <button type="submit">Upload Template</button>
                </form>
            </div>
            
            <h2>Your Templates</h2>
            <table>
                <tr>
                    <th>Template Name</th>
                    <th>Type</th>
                    <th>Actions</th>
                </tr>
                {template_list}
            </table>
            
            <div class="footer">
                InvoiceGen Pro v2.0.9 | &copy; 2024 InvoiceGen Systems
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/invoice/document_upload', methods=['POST'])
def upload_document():
    if 'template_file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['template_file']
    template_name = request.form.get('template_name', 'Unnamed Template')
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Allowed: .twig, .html, .txt"}), 400
    
    # Generate unique template ID
    template_id = str(uuid.uuid4())[:8]
    
    # Get file extension
    file_ext = file.filename.rsplit('.', 1)[1].lower()
    
    # Read template content
    content = file.read().decode('utf-8', errors='ignore')
    
    # Store template
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{template_id}.{file_ext}")
    with open(filepath, 'w') as f:
        f.write(content)
    
    templates_db[template_id] = {
        "name": template_name,
        "type": file_ext,
        "path": filepath
    }
    
    return redirect(url_for('index'))

@app.route('/invoice/preview/<template_id>')
def preview_template(template_id):
    if template_id not in templates_db:
        return jsonify({"error": "Template not found"}), 404
    
    template_data = templates_db[template_id]
    
    try:
        with open(template_data['path'], 'r') as f:
            template_content = f.read()
    except FileNotFoundError:
        return jsonify({"error": "Template file not found"}), 404
    
    # Sample invoice data for preview
    sample_data = {
        'company_name': 'Acme Corporation',
        'invoice_date': '2024-01-15',
        'invoice_number': 'INV-2024-0042',
        'customer_name': 'John Smith',
        'items': [
            {'description': 'Consulting Services', 'quantity': 10, 'price': 150},
            {'description': 'Software License', 'quantity': 1, 'price': 500}
        ],
        'subtotal': 2000,
        'tax': 200,
        'total': 2200
    }
    
    # Render the template with Jinja2 (VULNERABLE: no sandboxing)
    try:
        rendered = render_template_string(template_content, **sample_data)
        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Template Preview - {template_data["name"]}</title>
            <style>
                body {{ font-family: 'Segoe UI', sans-serif; margin: 20px; background: #f5f5f5; }}
                .preview-container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .preview-header {{ background: #3498db; color: white; padding: 15px; margin: -30px -30px 20px -30px; border-radius: 8px 8px 0 0; }}
                .back-link {{ display: inline-block; margin-top: 20px; color: #3498db; }}
            </style>
        </head>
        <body>
            <div class="preview-container">
                <div class="preview-header">
                    <h2>Preview: {template_data["name"]}</h2>
                </div>
                <div class="preview-content">
                    {rendered}
                </div>
                <a href="/" class="back-link">&larr; Back to Template Manager</a>
            </div>
        </body>
        </html>
        '''
    except Exception as e:
        return jsonify({"error": f"Template rendering error: {str(e)}"}), 500

@app.route('/invoice/download/<template_id>')
def download_template(template_id):
    if template_id not in templates_db:
        return jsonify({"error": "Template not found"}), 404
    
    template_data = templates_db[template_id]
    
    try:
        with open(template_data['path'], 'r') as f:
            template_content = f.read()
    except FileNotFoundError:
        return jsonify({"error": "Template file not found"}), 404
    
    # Sample invoice data
    invoice_data = {
        'company_name': 'Acme Corporation',
        'invoice_date': '2024-01-15',
        'invoice_number': 'INV-2024-0042',
        'customer_name': 'John Smith',
        'items': [
            {'description': 'Consulting Services', 'quantity': 10, 'price': 150},
            {'description': 'Software License', 'quantity': 1, 'price': 500}
        ],
        'subtotal': 2000,
        'tax': 200,
        'total': 2200
    }
    
    # Render and return as downloadable (VULNERABLE: no sandboxing)
    try:
        rendered = render_template_string(template_content, **invoice_data)
        response = app.make_response(rendered)
        response.headers['Content-Type'] = 'text/html'
        response.headers['Content-Disposition'] = f'attachment; filename=invoice_{template_id}.html'
        return response
    except Exception as e:
        return jsonify({"error": f"Template rendering error: {str(e)}"}), 500

@app.route('/api/templates')
def list_templates():
    """API endpoint to list all templates"""
    result = []
    for tid, tdata in templates_db.items():
        result.append({
            "id": tid,
            "name": tdata["name"],
            "type": tdata["type"]
        })
    return jsonify({"templates": result})

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "version": "2.0.9"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
