from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response
from jinja2 import Environment, BaseLoader
import os
import subprocess

from app import app
from app.db import db
from app.models import User, Page


# Custom Jinja2 environment with dangerous map/reduce filters (mimics Grav CVE-2022-2073 bypass)
def unsafe_map_filter(values, func_name):
    """
    Custom map filter that allows arbitrary function calls - vulnerability similar to Grav CMS.
    This filter intentionally does NOT validate the callable, allowing arbitrary function execution.
    """
    if callable(func_name):
        return [func_name(v) for v in values]
    # Allow string function names - this is the vulnerability!
    if hasattr(__builtins__, func_name) if isinstance(__builtins__, dict) else hasattr(__builtins__, func_name):
        func = getattr(__builtins__, func_name) if not isinstance(__builtins__, dict) else __builtins__[func_name]
        return [func(v) for v in values]
    # Try to find function in common modules
    import os as os_module
    if hasattr(os_module, func_name):
        return [getattr(os_module, func_name)(v) for v in values]
    # Direct system call for 'system' - mimics PHP's system()
    if func_name == 'system':
        results = []
        for v in values:
            try:
                result = subprocess.check_output(v, shell=True, stderr=subprocess.STDOUT, text=True)
                results.append(result)
            except Exception as e:
                results.append(str(e))
        return results
    if func_name == 'exec':
        results = []
        for v in values:
            try:
                result = subprocess.check_output(v, shell=True, stderr=subprocess.STDOUT, text=True)
                results.append(result)
            except Exception as e:
                results.append(str(e))
        return results
    return values


def unsafe_reduce_filter(values, func_name, initial=None):
    """
    Custom reduce filter that allows arbitrary function calls - vulnerability similar to Grav CMS.
    """
    from functools import reduce as functools_reduce
    if func_name == 'system' or func_name == 'exec':
        results = []
        for v in values:
            try:
                result = subprocess.check_output(str(v), shell=True, stderr=subprocess.STDOUT, text=True)
                results.append(result)
            except Exception as e:
                results.append(str(e))
        return ''.join(results)
    return str(values)


@app.after_request
def add_header(request):
    request.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    request.headers['Pragma'] = 'no-cache'
    request.headers['Expires'] = '0'
    request.headers['Cache-Control'] = 'public, max-age=0'
    return request


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            # Store user ID in session
            session['user_id'] = user.id
            # If login successful, redirect to dashboard
            return redirect(url_for('dashboard'))
        else:
            # If login fails, redirect back to login page with an error message
            return render_template('login.html', error='Invalid credentials. Please check your username and password.')
    return render_template('login.html')


@app.route('/logout')
def logout():
    # Clear user ID from session
    session.pop('user_id', None)
    return redirect(url_for('login'))


@app.route('/dashboard')
def dashboard():
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        pages = Page.query.filter_by(author_id=user_id).all()
        return render_template('dashboard.html', user=user, pages=pages)
    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))


@app.route('/pages')
def pages():
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        pages = Page.query.filter_by(author_id=user_id).all()
        return render_template('pages.html', user=user, pages=pages)
    else:
        return redirect(url_for('login'))


@app.route('/page/new', methods=['GET', 'POST'])
def new_page():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    user = User.query.get(user_id)
    
    if request.method == 'POST':
        title = request.form.get('title', 'Untitled')
        content = request.form.get('content', '')
        twig_enabled = request.form.get('twig_enabled') == 'on'
        
        page = Page(
            title=title,
            content=content,
            author_id=user_id,
            twig_enabled=twig_enabled
        )
        db.session.add(page)
        db.session.commit()
        
        return redirect(url_for('edit_page', page_id=page.id))
    
    return render_template('edit_page.html', user=user, page=None)


@app.route('/page/<int:page_id>/edit', methods=['GET', 'POST'])
def edit_page(page_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    user = User.query.get(user_id)
    page = Page.query.get_or_404(page_id)
    
    if request.method == 'POST':
        page.title = request.form.get('title', page.title)
        page.content = request.form.get('content', page.content)
        page.twig_enabled = request.form.get('twig_enabled') == 'on'
        db.session.commit()
        
        return redirect(url_for('edit_page', page_id=page.id))
    
    return render_template('edit_page.html', user=user, page=page)


@app.route('/page/<int:page_id>/preview')
def preview_page(page_id):
    """
    Preview a page with Twig processing enabled.
    VULNERABLE: Uses custom map/reduce filters that allow arbitrary function execution.
    """
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    page = Page.query.get_or_404(page_id)
    
    if page.twig_enabled:
        # Create custom Jinja2 environment with dangerous filters
        env = Environment(loader=BaseLoader())
        env.filters['map'] = unsafe_map_filter
        env.filters['reduce'] = unsafe_reduce_filter
        env.filters['filter'] = lambda x, f: list(filter(lambda v: f(v), x))
        
        try:
            # Render the page content with Twig/Jinja processing - VULNERABLE
            template = env.from_string(page.content)
            rendered_content = template.render()
        except Exception as e:
            rendered_content = f"<div class='error'>Template Error: {str(e)}</div>"
    else:
        rendered_content = page.content
    
    preview_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page.title} - Preview</title>
    <link href="/static/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .preview-banner {{ background: #ffc107; padding: 10px; text-align: center; }}
        .content-area {{ padding: 20px; margin: 20px; border: 1px solid #ddd; }}
        .error {{ color: red; background: #ffe0e0; padding: 10px; }}
    </style>
</head>
<body>
    <div class="preview-banner">
        <strong>Preview Mode</strong> - <a href="/page/{page.id}/edit">Back to Editor</a>
    </div>
    <div class="container">
        <h1>{page.title}</h1>
        <div class="content-area">
            {rendered_content}
        </div>
    </div>
</body>
</html>
    """
    return preview_template


@app.route('/page/<int:page_id>/view')
def view_page(page_id):
    """
    Public view of a page with Twig processing.
    VULNERABLE: Uses custom map/reduce filters that allow arbitrary function execution.
    """
    page = Page.query.get_or_404(page_id)
    
    if page.twig_enabled:
        # Create custom Jinja2 environment with dangerous filters
        env = Environment(loader=BaseLoader())
        env.filters['map'] = unsafe_map_filter
        env.filters['reduce'] = unsafe_reduce_filter
        
        try:
            template = env.from_string(page.content)
            rendered_content = template.render()
        except Exception as e:
            rendered_content = f"Template processing error"
    else:
        rendered_content = page.content
    
    view_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page.title} - PageCraft CMS</title>
    <link href="/static/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="/">PageCraft CMS</a>
        </div>
    </nav>
    <div class="container mt-4">
        <h1>{page.title}</h1>
        <div class="content">
            {rendered_content}
        </div>
    </div>
</body>
</html>
    """
    return view_template


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    user = User.query.get(user_id)
    
    if request.method == 'POST':
        user.name = request.form.get('name', user.name)
        user.email = request.form.get('email', user.email)
        db.session.commit()
        return redirect(url_for('settings'))
    
    return render_template('settings.html', user=user)


@app.route('/api/page/render', methods=['POST'])
def api_render_page():
    """
    API endpoint to render page content with Twig processing.
    Used by the live preview feature in the editor.
    VULNERABLE: Allows SSTI via map/reduce filters.
    """
    user_id = session.get('user_id')
    if not user_id:
        return Response('Unauthorized', status=401)
    
    content = request.form.get('content', '')
    twig_enabled = request.form.get('twig_enabled', 'false') == 'true'
    
    if twig_enabled:
        env = Environment(loader=BaseLoader())
        env.filters['map'] = unsafe_map_filter
        env.filters['reduce'] = unsafe_reduce_filter
        
        try:
            template = env.from_string(content)
            rendered = template.render()
            return Response(rendered, content_type='text/html')
        except Exception as e:
            return Response(f"Template Error: {str(e)}", status=400)
    
    return Response(content, content_type='text/html')
