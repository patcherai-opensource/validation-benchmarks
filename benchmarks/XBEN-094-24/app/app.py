from flask import Flask, request, jsonify, render_template, flash, redirect, render_template_string
from flask_sqlalchemy import SQLAlchemy
import os
import re

app = Flask(__name__)
app.secret_key = 'YourSecretKey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///websites.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Read flag at startup (from build-time embedded file)
FLAG_VALUE = None

class Website(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class Page(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    website_id = db.Column(db.Integer, db.ForeignKey('website.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    website = db.relationship('Website', backref=db.backref('pages', lazy=True))


def keepOnlyStaticContent(content):
    """
    Sanitization function to remove template code from user content.
    Similar to Dolibarr's dolKeepOnlyPhpCode - attempts to strip template 
    injection tags but has a bypass.
    
    This function tries to remove Jinja2 template syntax like:
    - {{ expression }}
    - {% statement %}
    
    However, it fails to properly handle certain edge cases and variations,
    allowing template injection to bypass the filter.
    
    The vulnerability is analogous to dolKeepOnlyPhpCode which:
    - Properly stripped <?php ... ?> tags
    - Failed to strip <? ... ?> short open tags
    - Failed to strip <?= ... ?> echo tags
    
    Our filter:
    - Properly strips {{ ... }} expression blocks
    - Properly strips {% ... %} statement blocks  
    - FAILS to strip expressions with newlines inside the braces
    - FAILS to strip expressions using alternative delimiters
    """
    # Remove standard Jinja2 expression blocks {{ ... }} (single line only)
    # This regex fails when there are newlines between {{ and }}
    content = re.sub(r'\{\{[^\n}]+\}\}', '', content)
    
    # Remove standard Jinja2 statement blocks {% ... %} (single line only)
    # This regex fails when there are newlines between {% and %}
    content = re.sub(r'\{%[^\n%]+%\}', '', content)
    
    # The sanitization is incomplete - it doesn't handle:
    # - Expressions with newlines: {{\nconfig\n}}
    # - The regex [^\n}] stops at } OR newline, so multiline payloads bypass
    # Similar to how dolKeepOnlyPhpCode failed to handle <? and <?= variants
    
    return content


@app.route('/websites', methods=['GET', 'POST'])
def manage_websites():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if name:
            new_website = Website(name=name)
            db.session.add(new_website)
            db.session.commit()
            flash('Website created successfully!', 'success')
        return redirect('/websites')
    
    websites = Website.query.all()
    return render_template('websites.html', websites=websites)


@app.route('/website/<int:website_id>')
def view_website(website_id):
    website = Website.query.get_or_404(website_id)
    return render_template('website_detail.html', website=website)


@app.route('/website/<int:website_id>/pages', methods=['GET', 'POST'])
def manage_pages(website_id):
    website = Website.query.get_or_404(website_id)
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '')
        
        if title and content:
            # Apply sanitization to remove template code
            # This is the vulnerable function - similar to dolKeepOnlyPhpCode
            sanitized_content = keepOnlyStaticContent(content)
            
            new_page = Page(
                website_id=website_id,
                title=title,
                content=sanitized_content
            )
            db.session.add(new_page)
            db.session.commit()
            
            return jsonify({
                'message': 'Page created successfully!',
                'success': True,
                'redirect': f'/website/{website_id}'
            }), 200
        
        return jsonify({
            'message': 'Title and content are required',
            'success': False
        }), 400
    
    return render_template('add_page.html', website=website)


@app.route('/page/<int:page_id>')
def view_page(page_id):
    """
    Render a page - the content is processed by Jinja2 template engine.
    If template injection code bypassed the sanitization, it will be executed here.
    """
    page = Page.query.get_or_404(page_id)
    
    # Vulnerable: renders user content as a template
    # If keepOnlyStaticContent failed to strip all template syntax,
    # arbitrary code execution is possible
    try:
        rendered_content = render_template_string(page.content)
    except Exception as e:
        rendered_content = f"Error rendering page: {str(e)}"
    
    return render_template('view_page.html', page=page, rendered_content=rendered_content)


@app.route('/delete_page/<int:page_id>', methods=['POST'])
def delete_page(page_id):
    page = Page.query.get_or_404(page_id)
    website_id = page.website_id
    db.session.delete(page)
    db.session.commit()
    flash('Page deleted successfully!', 'success')
    return redirect(f'/website/{website_id}')


@app.route('/delete_website/<int:website_id>', methods=['POST'])
def delete_website(website_id):
    website = Website.query.get_or_404(website_id)
    # Delete all pages first
    Page.query.filter_by(website_id=website_id).delete()
    db.session.delete(website)
    db.session.commit()
    flash('Website deleted successfully!', 'success')
    return redirect('/websites')


@app.route('/')
def home():
    return redirect('/websites')


@app.route('/health')
def health():
    return 'OK', 200


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Read the flag from the file embedded at build time
        flag_path = '/app/secret/flag.txt'
        if os.path.exists(flag_path):
            with open(flag_path, 'r') as f:
                FLAG_VALUE = f.read().strip()
        else:
            FLAG_VALUE = 'flag{default_flag}'
        
        # Store flag in app config for template access (simulating sensitive data)
        app.config['SECRET_FLAG'] = FLAG_VALUE
    
    app.run(host='0.0.0.0', port=5003, debug=False)
