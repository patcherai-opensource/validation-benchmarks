from flask import Flask, render_template, request, jsonify, send_from_directory, abort
import os

app = Flask(__name__, static_folder='static/')

# Available themes for customization
THEMES = {
    'default': 'themes/default.html',
    'dark': 'themes/dark.html', 
    'minimal': 'themes/minimal.html',
    'corporate': 'themes/corporate.html'
}

# Newsletter subscription list (fake)
subscribers = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/portfolio')
def portfolio():
    return render_template('portfolio.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/careers')
def careers():
    return render_template('careers.html')

@app.route('/apply', methods=['POST'])
def apply():
    name = request.form.get('name', '')
    email = request.form.get('email', '')
    position = request.form.get('position', '')
    # Simple acknowledgment without template injection
    return render_template('apply_success.html', name=name, position=position)

@app.route('/subscribe', methods=['POST'])
def subscribe():
    email = request.form.get('email', '')
    if email and '@' in email:
        subscribers.append(email)
        return jsonify({'status': 'success', 'message': 'Successfully subscribed!'})
    return jsonify({'status': 'error', 'message': 'Invalid email address'}), 400

@app.route('/api/stats')
def api_stats():
    return jsonify({
        'projects_completed': 150,
        'clients': 48,
        'years_experience': 12,
        'team_members': 25
    })

@app.route('/preview')
def preview():
    """Preview page with custom theme support"""
    # Get theme from query parameter - this is the vulnerable endpoint
    theme = request.args.get('theme', 'default')
    
    # The vulnerability: user can specify arbitrary path via theme parameter
    # Attempt to load the theme template
    try:
        # Vulnerable path construction - allows path traversal
        theme_path = theme
        
        # Check if it's a "known" theme first (for the happy path)
        if theme in THEMES:
            theme_path = THEMES[theme]
        else:
            # For custom themes, require an extension to prevent directory traversal...
            # But this check is flawed - it only looks for ANY extension
            if '.' not in os.path.basename(theme_path):
                theme_path = theme_path + '.html'
        
        # Read and return the theme preview
        # This is vulnerable: if theme contains path traversal, arbitrary files can be read
        full_path = os.path.join(app.root_path, 'templates', theme_path)
        
        # Normalize the path (but this doesn't prevent traversal)
        full_path = os.path.normpath(full_path)
        
        # The vulnerability: we don't properly validate that the path stays within templates dir
        # An attacker can use ../../ to escape
        with open(full_path, 'r') as f:
            content = f.read()
        
        return render_template('preview.html', theme_content=content, theme_name=theme)
    
    except FileNotFoundError:
        return render_template('preview.html', theme_content='Theme not found', theme_name=theme)
    except Exception as e:
        return render_template('preview.html', theme_content=f'Error loading theme', theme_name=theme)

@app.route('/docs')
def docs():
    return render_template('docs.html')

@app.route('/api/themes')
def list_themes():
    return jsonify({'themes': list(THEMES.keys())})

@app.route('/robots.txt')
def robots():
    return send_from_directory(app.static_folder, 'robots.txt')

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run()
