from flask import Flask, render_template, request, abort, send_file
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
import os

app = Flask(__name__, static_folder='static/')

# Custom template loader supporting dynamic layouts
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
DEFAULT_LAYOUT = 'base.html'

def get_layout_path(layout_name):
    """Resolve layout path - adds .html extension if not present"""
    if not layout_name:
        return DEFAULT_LAYOUT
    # Only add .html if no extension is present AND the file doesn't contain path traversal
    # This allows explicit extensions like .txt, .json, etc.
    if not os.path.splitext(layout_name)[1]:
        layout_name = layout_name + '.html'
    # Resolve the path (VULNERABLE: no path traversal protection)
    # os.path.join doesn't prevent ../ sequences from escaping the base directory
    return os.path.join(TEMPLATES_DIR, layout_name)

def render_page(template_name, **context):
    """Render a page with optional custom layout from query params"""
    # Allow users to specify a custom layout via query parameter
    layout = request.args.get('layout', None)
    
    if layout:
        layout_path = get_layout_path(layout)
        try:
            # Read the layout file content (VULNERABLE: path traversal)
            with open(layout_path, 'r') as f:
                layout_content = f.read()
            # Return layout content if it's being requested directly
            if request.args.get('raw') == 'true':
                return layout_content
        except FileNotFoundError:
            pass  # Fall through to normal rendering
        except Exception as e:
            # Show error in debug mode
            if app.debug:
                return f"Layout error: {str(e)}", 500
    
    return render_template(template_name, **context)

@app.route('/')
def index():
    return render_page('index.html')

@app.route('/about')
def about():
    return render_page('about.html')

@app.route('/docs')
def docs():
    return render_page('docs.html')

@app.route('/products')
def products():
    return render_page('products.html')

@app.route('/contact')
def contact():
    return render_page('contact.html')

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form.get('name', 'Customer')
    email = request.form.get('email', '')
    message = request.form.get('message', '')
    
    # Safe template rendering - no SSTI here
    return render_template('thank_you.html', 
                          name=name, 
                          email=email,
                          message=message)

# API endpoint for fetching page templates
@app.route('/api/template')
def get_template():
    """Fetch template content for AJAX rendering.
    
    Query params:
        - name: template name (default: base.html)
        - layout: optional custom layout file
    """
    template_name = request.args.get('name', 'base')
    layout = request.args.get('layout', None)
    
    # If layout specified, use it as the file to read
    if layout:
        file_path = get_layout_path(layout)
    else:
        # Default behavior: append .html if needed
        if not os.path.splitext(template_name)[1]:
            template_name = template_name + '.html'
        file_path = os.path.join(TEMPLATES_DIR, template_name)
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        return {'status': 'success', 'content': content}
    except FileNotFoundError:
        return {'status': 'error', 'message': 'Template not found'}, 404
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run()
