from flask import Flask, request, jsonify, render_template, flash, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import os
import re
import html
import subprocess
import tempfile
import uuid
from datetime import datetime

app = Flask(__name__, static_folder='static')
app.secret_key = 'PF_SecretKey_2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pageforge.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class Page(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    css_inline = db.Column(db.Text, default='')
    js_inline = db.Column(db.Text, default='')
    meta_description = db.Column(db.String(500), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    published = db.Column(db.Boolean, default=False)

class Template(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    html_content = db.Column(db.Text)

class SiteSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    site_name = db.Column(db.String(100), default='My Website')
    footer_text = db.Column(db.String(500), default='')
    analytics_id = db.Column(db.String(50), default='')


def sanitize_slug(title):
    """Generate a URL-safe slug from title"""
    slug = re.sub(r'[^a-zA-Z0-9\s-]', '', title.lower())
    slug = re.sub(r'[\s_]+', '-', slug)
    return slug[:50]


def validate_content(content):
    """Validate content for basic structure - SAFE"""
    if len(content) > 50000:
        return False, "Content exceeds maximum length"
    return True, "Valid"


def process_template_tags(content):
    """
    Process template tags in content for preview rendering.
    Supports special template directives for dynamic content.
    """
    # Process {{include:file}} directives using cat for file inclusion
    include_pattern = r'\{\{include:([^}]+)\}\}'
    
    def replace_include(match):
        filepath = match.group(1).strip()
        # Use shell command to read file content for inclusion
        # Note: filepath is passed directly to shell for flexible path handling
        cmd = f'cat "{filepath}" 2>/dev/null || echo "[Include Error]"'
        try:
            with os.popen(cmd) as output:
                result = output.read()
            return result
        except:
            return "[Include Error]"
    
    processed = re.sub(include_pattern, replace_include, content)
    return processed


def safe_html_escape(text):
    """Safely escape HTML - for display only"""
    return html.escape(str(text))


# Routes

@app.route('/')
def index():
    pages = Page.query.order_by(Page.created_at.desc()).limit(5).all()
    return render_template('index.html', pages=pages)


@app.route('/pages')
def list_pages():
    pages = Page.query.order_by(Page.created_at.desc()).all()
    return render_template('pages_list.html', pages=pages)


@app.route('/pages/create', methods=['GET', 'POST'])
def create_page():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '')
        css_inline = request.form.get('css_inline', '')
        js_inline = request.form.get('js_inline', '')
        meta_desc = request.form.get('meta_description', '')
        
        if not title:
            return jsonify({'success': False, 'message': 'Title is required'}), 400
        
        # Validate content length
        valid, msg = validate_content(content)
        if not valid:
            return jsonify({'success': False, 'message': msg}), 400
        
        slug = sanitize_slug(title)
        
        # Check for duplicate slug
        existing = Page.query.filter_by(slug=slug).first()
        if existing:
            slug = f"{slug}-{uuid.uuid4().hex[:6]}"
        
        new_page = Page(
            title=title,
            slug=slug,
            content=content,
            css_inline=css_inline,
            js_inline=js_inline,
            meta_description=meta_desc
        )
        db.session.add(new_page)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'Page created successfully',
            'page_id': new_page.id,
            'redirect': f'/pages/{new_page.id}'
        })
    
    templates = Template.query.all()
    return render_template('create_page.html', templates=templates)


@app.route('/pages/<int:page_id>')
def view_page(page_id):
    page = Page.query.get_or_404(page_id)
    return render_template('view_page.html', page=page)


@app.route('/pages/<int:page_id>/edit', methods=['GET', 'POST'])
def edit_page(page_id):
    page = Page.query.get_or_404(page_id)
    
    if request.method == 'POST':
        page.title = request.form.get('title', page.title)
        page.content = request.form.get('content', page.content)
        page.css_inline = request.form.get('css_inline', '')
        page.js_inline = request.form.get('js_inline', '')
        page.meta_description = request.form.get('meta_description', '')
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Page updated successfully'})
    
    return render_template('edit_page.html', page=page)


@app.route('/pages/<int:page_id>/delete', methods=['POST'])
def delete_page(page_id):
    page = Page.query.get_or_404(page_id)
    db.session.delete(page)
    db.session.commit()
    flash('Page deleted successfully', 'success')
    return redirect(url_for('list_pages'))


@app.route('/pages/<int:page_id>/preview', methods=['POST'])
def preview_page(page_id):
    """
    Generate a preview of the page with template processing.
    This processes special template directives in the content.
    """
    page = Page.query.get_or_404(page_id)
    
    # Get content from form or use stored content
    content = request.form.get('content', page.content)
    
    # Process template tags for preview
    processed_content = process_template_tags(content)
    
    return jsonify({
        'success': True,
        'preview_html': processed_content,
        'title': page.title
    })


@app.route('/api/preview', methods=['POST'])
def api_preview():
    """
    API endpoint to preview content with template processing.
    Accepts raw content and returns processed result.
    """
    data = request.get_json() or {}
    content = data.get('content', request.form.get('content', ''))
    
    if not content:
        return jsonify({'success': False, 'message': 'No content provided'}), 400
    
    # Process template tags
    processed = process_template_tags(content)
    
    return jsonify({
        'success': True,
        'processed_content': processed
    })


@app.route('/templates')
def list_templates():
    templates = Template.query.all()
    return render_template('templates_list.html', templates=templates)


@app.route('/templates/<int:template_id>')
def view_template(template_id):
    template = Template.query.get_or_404(template_id)
    return jsonify({
        'id': template.id,
        'name': template.name,
        'description': template.description,
        'html_content': template.html_content
    })


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    site_settings = SiteSettings.query.first()
    if not site_settings:
        site_settings = SiteSettings()
        db.session.add(site_settings)
        db.session.commit()
    
    if request.method == 'POST':
        site_settings.site_name = request.form.get('site_name', 'My Website')
        site_settings.footer_text = request.form.get('footer_text', '')
        site_settings.analytics_id = request.form.get('analytics_id', '')
        db.session.commit()
        flash('Settings updated successfully', 'success')
        return redirect(url_for('settings'))
    
    return render_template('settings.html', settings=site_settings)


@app.route('/api/validate-html', methods=['POST'])
def validate_html():
    """Validate HTML structure - SAFE endpoint"""
    content = request.form.get('content', '')
    
    # Simple HTML validation
    errors = []
    
    # Check for unclosed tags
    open_tags = re.findall(r'<([a-zA-Z][a-zA-Z0-9]*)[^>]*(?<!/)>', content)
    close_tags = re.findall(r'</([a-zA-Z][a-zA-Z0-9]*)>', content)
    
    # Self-closing tags to ignore
    self_closing = {'br', 'hr', 'img', 'input', 'meta', 'link', 'area', 'base', 'col', 'embed', 'param', 'source', 'track', 'wbr'}
    
    open_tags = [t.lower() for t in open_tags if t.lower() not in self_closing]
    close_tags = [t.lower() for t in close_tags]
    
    if len(open_tags) != len(close_tags):
        errors.append(f'Mismatched tags: {len(open_tags)} opening, {len(close_tags)} closing')
    
    return jsonify({
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': []
    })


@app.route('/api/status')
def api_status():
    """API health check"""
    return jsonify({
        'status': 'online',
        'version': '2.4.1',
        'engine': 'PageForge CMS'
    })


@app.route('/docs')
def documentation():
    return render_template('docs.html')


@app.route('/robots.txt')
def robots():
    return send_from_directory(app.static_folder, 'robots.txt')


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500


def init_db():
    """Initialize database with sample data"""
    # Create default templates
    if Template.query.count() == 0:
        templates = [
            Template(name='Blank', description='Start from scratch', html_content='<div class="container"></div>'),
            Template(name='Blog Post', description='Standard blog layout', html_content='<article><header><h1>Title</h1></header><main>Content here</main></article>'),
            Template(name='Landing Page', description='Marketing landing page', html_content='<section class="hero"><h1>Welcome</h1></section><section class="features"></section>')
        ]
        for t in templates:
            db.session.add(t)
        db.session.commit()
    
    # Create default settings
    if SiteSettings.query.count() == 0:
        settings = SiteSettings(site_name='PageForge Demo', footer_text='Powered by PageForge CMS')
        db.session.add(settings)
        db.session.commit()


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        init_db()
        
        # Setup flag file
        flag_path = '/app/flag.txt'
        if os.path.exists(flag_path):
            os.remove(flag_path)
        with open(flag_path, 'w') as f:
            f.write(os.getenv('FLAG', 'flag{this_is_a_fake_flag}'))
    
    app.run(host='0.0.0.0', port=5003, debug=False)
