import os
import json
from flask import Flask, render_template, request, send_file, abort, Response
from pathlib import Path

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24).hex()

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / 'static'
POSTS_DIR = BASE_DIR / 'posts'
CDN_CACHE_DIR = BASE_DIR / 'cdn_cache'


def get_posts():
    posts_file = BASE_DIR / 'posts.json'
    with open(posts_file, 'r') as f:
        return json.load(f)


def get_post_content(post_id):
    posts_file = POSTS_DIR / f'{post_id}.html'
    if posts_file.exists():
        with open(posts_file, 'r') as f:
            return f.read()
    return None


def get_from_cache(base_cache_dir, path):
    cache_path = base_cache_dir / path
    normalized = cache_path.resolve()
    
    if normalized.exists() and normalized.is_file():
        return normalized
    return None


def get_data(base_cache_dir, path):
    file_path = get_from_cache(base_cache_dir, path)
    if file_path:
        with open(file_path, 'rb') as f:
            return f.read()
    return None


@app.route('/')
def index():
    posts = get_posts()
    page = request.args.get('page', 1, type=int)
    per_page = 5
    total_posts = len(posts)
    total_pages = (total_posts + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page
    display_posts = posts[start:end]
    return render_template('index.html', 
                         posts=display_posts, 
                         page=page, 
                         total_pages=total_pages)


@app.route('/post/<post_id>')
def view_post(post_id):
    posts = get_posts()
    post = next((p for p in posts if p['post_url'].replace('.php', '') == post_id), None)
    if post:
        content = get_post_content(post_id)
        if content:
            return render_template('post.html', post=post, content=content)
    return render_template('post.html', post=None, content=None)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    errors = {}
    success = False
    form_data = {'name': '', 'email': '', 'message': ''}
    
    if request.method == 'POST':
        form_data['name'] = request.form.get('name', '').strip()
        form_data['email'] = request.form.get('email', '').strip()
        form_data['message'] = request.form.get('message', '').strip()
        
        if not form_data['name']:
            errors['name'] = 'Please enter your name.'
        if not form_data['email']:
            errors['email'] = 'Please enter your email address.'
        if not form_data['message']:
            errors['message'] = 'Please enter your message.'
        
        if not errors:
            success = True
    
    return render_template('contact.html', errors=errors, success=success, form_data=form_data)


@app.route('/static/<path:filename>')
def serve_static(filename):
    file_path = STATIC_DIR / filename
    if file_path.exists() and file_path.is_file():
        return send_file(file_path)
    abort(404)


@app.route('/_solara/cdn/<path:path>')
def cdn(path):
    data = get_data(CDN_CACHE_DIR, path)
    if data:
        content_type = 'application/octet-stream'
        if path.endswith('.js'):
            content_type = 'application/javascript'
        elif path.endswith('.css'):
            content_type = 'text/css'
        elif path.endswith('.html'):
            content_type = 'text/html'
        elif path.endswith('.json'):
            content_type = 'application/json'
        elif path.endswith('.txt'):
            content_type = 'text/plain'
        return Response(data, mimetype=content_type)
    abort(404)


@app.route('/static/public/<path:path>')
def static_public(path):
    public_dir = STATIC_DIR / 'public'
    file_path = public_dir / path
    resolved = file_path.resolve()
    
    if resolved.exists() and resolved.is_file():
        return send_file(resolved)
    abort(404)


@app.route('/static/assets/<path:path>')
def static_assets(path):
    assets_dir = STATIC_DIR / 'assets'
    file_path = assets_dir / path
    resolved = file_path.resolve()
    
    if resolved.exists() and resolved.is_file():
        return send_file(resolved)
    abort(404)


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', error_code=404, error_message='Page not found'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error_code=500, error_message='Internal server error'), 500


if __name__ == '__main__':
    CDN_CACHE_DIR.mkdir(exist_ok=True)
    app.run(host='0.0.0.0', port=80, debug=False)
