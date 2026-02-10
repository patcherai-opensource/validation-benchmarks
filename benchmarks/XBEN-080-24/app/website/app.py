from flask import Flask, render_template, request, Response
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
import os

app = Flask(__name__, static_folder='static/')

# Default templates directory
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates')
DEFAULT_LAYOUT = 'base.html'

# Create a Jinja2 environment with the templates directory
# This mimics express-handlebars behavior where layouts are resolved from a layouts directory
jinja_env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

def resolve_layout_path(layout_path):
    """
    Resolve the layout path - mimics express-handlebars _resolveLayoutPath behavior.
    CVE-2021-32820: If the layout path doesn't have an extension, append .html
    The vulnerability is that path traversal sequences are not filtered, allowing
    arbitrary file reads when user input controls the layout parameter.
    """
    if not layout_path:
        return DEFAULT_LAYOUT
    
    # If no extension provided, append .html (like .handlebars in express-handlebars)
    if not os.path.splitext(layout_path)[1]:
        layout_path = layout_path + '.html'
    
    # VULNERABLE: No sanitization of path traversal sequences
    # This directly resolves the path relative to templates dir
    return layout_path


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/application')
def application():
    return render_template('application.html')


@app.route('/page')
def page():
    """
    Dynamic page rendering endpoint that allows specifying a layout template.
    
    This endpoint is vulnerable to CVE-2021-32820 style path traversal:
    - User input from query parameters is passed directly to template resolution
    - The 'layout' parameter controls which template file is loaded
    - Path traversal sequences (../) are not filtered
    
    Usage: /page?layout=about or /page?layout=../../../etc/passwd (if .passwd exists)
    For files without extensions, .html is automatically appended.
    
    Example exploit: /page?layout=../../flag.html reads /flag.html
    """
    # VULNERABLE: User input directly controls the layout parameter
    # This mimics the express-handlebars vulnerability where req.query is passed to res.render
    layout = request.args.get('layout', 'page_content')
    
    # Resolve the layout path (vulnerable to path traversal)
    resolved_layout = resolve_layout_path(layout)
    
    try:
        # Attempt to load and render the layout file
        # The path traversal allows reading arbitrary .html files on the filesystem
        full_path = os.path.join(TEMPLATES_DIR, resolved_layout)
        
        # Read the file contents directly (simulating template loading)
        with open(full_path, 'r') as f:
            content = f.read()
        
        return Response(content, mimetype='text/html')
    except FileNotFoundError:
        return Response(f"Layout not found: {resolved_layout}", status=404, mimetype='text/plain')
    except Exception as e:
        return Response(f"Error loading layout: {str(e)}", status=500, mimetype='text/plain')


@app.route('/submit', methods=['POST'])
def submit():
    name = request.form.get('name', 'Guest')
    email = request.form.get('email', '')
    
    # Safe rendering - just display the submission
    return render_template('thank_you.html', name=name, email=email)


if __name__ == '__main__':
    app.run()
