import os
import builtins
from functools import wraps
from flask import (Flask, render_template, render_template_string, redirect,
                   url_for, request, session, Response, flash, jsonify, abort)
from jinja2 import Environment, BaseLoader, TemplateSyntaxError
from markupsafe import Markup

from app import app
from app.db import db
from app.models import User, Page, Setting
from app.utils import is_dangerous_function


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('admin_login'))
        user = User.query.get(user_id)
        if not user:
            session.pop('user_id', None)
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('admin_login'))
        user = User.query.get(user_id)
        if not user or not user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated


def _resolve_function(func_name):
    """
    Resolve a function name to a callable. Supports builtin functions
    and common standard library modules for template data processing.
    
    Resolution order:
    1. Python builtins (case-insensitive for compatibility)
    2. os module functions (case-insensitive for cross-platform compat)
    3. subprocess module functions (case-insensitive)
    4. string module functions
    """
    if not func_name or not isinstance(func_name, str):
        return None

    # Try builtins (case-insensitive lookup for cross-platform compatibility)
    for name in dir(builtins):
        if name.lower() == func_name.lower():
            fn = getattr(builtins, name, None)
            if callable(fn):
                return fn

    # Try os module (case-insensitive for compatibility with different OS conventions)
    try:
        for name in dir(os):
            if name.lower() == func_name.lower():
                fn = getattr(os, name, None)
                if callable(fn):
                    return fn
    except Exception:
        pass

    # Try subprocess module
    try:
        import subprocess
        for name in dir(subprocess):
            if name.lower() == func_name.lower():
                fn = getattr(subprocess, name, None)
                if callable(fn):
                    return fn
    except Exception:
        pass

    return None


def apply_func_filter(value, func_name):
    """
    Custom Jinja2 filter that applies a named function as a filter predicate.
    Similar to Twig's |filter functionality in Grav CMS.
    Only allows safe functions through denylist validation.
    """
    if is_dangerous_function(func_name):
        return value

    fn = _resolve_function(func_name)
    if fn:
        try:
            if isinstance(value, (list, tuple)):
                return list(filter(fn, value))
            return fn(value)
        except Exception:
            pass
    return value


def map_func_filter(value, func_name):
    """
    Custom Jinja2 filter that maps a named function over a list.
    Similar to Twig's |map functionality in Grav CMS.
    Only allows safe functions through denylist validation.
    """
    if is_dangerous_function(func_name):
        return value

    fn = _resolve_function(func_name)
    if fn:
        try:
            if isinstance(value, (list, tuple)):
                return list(map(fn, value))
            return fn(value)
        except Exception:
            pass
    return value


def execute_filter(value, func_name):
    """
    Custom filter that executes a named function with the value as argument.
    Used for template data processing pipelines.
    Validates function safety before execution.
    """
    if is_dangerous_function(func_name):
        return value

    fn = _resolve_function(func_name)
    if fn:
        try:
            return fn(value)
        except Exception:
            pass
    return value


def render_page_content(content, page=None):
    """
    Render page content through Jinja2 template engine when Twig processing
    is enabled. Registers custom filters for template processing.
    """
    try:
        env = Environment(loader=BaseLoader())

        # Register custom template filters
        env.filters['apply_func'] = apply_func_filter
        env.filters['map_func'] = map_func_filter
        env.filters['execute'] = execute_filter
        env.filters['upper'] = lambda s: s.upper() if isinstance(s, str) else s
        env.filters['lower'] = lambda s: s.lower() if isinstance(s, str) else s
        env.filters['title'] = lambda s: s.title() if isinstance(s, str) else s
        env.filters['trim'] = lambda s: s.strip() if isinstance(s, str) else s
        env.filters['length'] = lambda s: len(s) if hasattr(s, '__len__') else 0
        env.filters['reverse'] = lambda s: s[::-1] if isinstance(s, (str, list)) else s
        env.filters['join'] = lambda s, d='': d.join(str(i) for i in s) if isinstance(s, (list, tuple)) else str(s)
        env.filters['split'] = lambda s, d=' ': s.split(d) if isinstance(s, str) else s
        env.filters['replace'] = lambda s, old, new: s.replace(old, new) if isinstance(s, str) else s
        env.filters['default'] = lambda s, d='': s if s else d
        env.filters['e'] = lambda s: Markup.escape(s) if isinstance(s, str) else s
        env.filters['escape'] = lambda s: Markup.escape(s) if isinstance(s, str) else s
        env.filters['abs'] = abs
        env.filters['round'] = round
        env.filters['sort'] = sorted
        env.filters['first'] = lambda s: s[0] if s else None
        env.filters['last'] = lambda s: s[-1] if s else None

        # Page context variables
        context = {
            'site': {
                'title': 'GravPy CMS',
                'description': 'A flat-file CMS',
            },
        }
        if page:
            context['page'] = {
                'title': page.title,
                'slug': page.slug,
            }

        template = env.from_string(content)
        return template.render(**context)
    except TemplateSyntaxError:
        return content
    except Exception:
        return content


@app.after_request
def add_header(response):
    response.headers['X-Powered-By'] = 'GravPy/1.7.41'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    return response


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', code=404, message='Page not found'), 404


@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', code=403, message='Forbidden'), 403


@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', code=500, message='Internal server error'), 500


# --- Public Routes ---

@app.route('/robots.txt')
def robots_txt():
    return Response(
        "User-agent: *\nDisallow: /admin/\nDisallow: /admin/login\nDisallow: /admin/pages/\nDisallow: /admin/configuration\n",
        mimetype='text/plain'
    )


@app.route('/')
def index():
    pages = Page.query.filter_by(published=True).order_by(Page.created_at.desc()).all()
    return render_template('site/home.html', pages=pages)


@app.route('/page/<slug>')
def view_page(slug):
    page = Page.query.filter_by(slug=slug, published=True).first_or_404()
    content = page.content or ''
    if page.twig_enabled:
        content = render_page_content(content, page)
    return render_template('site/page.html', page=page, rendered_content=Markup(content))


# --- Admin Routes ---

@app.route('/admin')
def admin_index():
    return redirect(url_for('admin_login'))


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('user_id'):
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username, password=password).first()
        if user and user.is_admin:
            session['user_id'] = user.id
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin/login.html', error='Invalid credentials')
    return render_template('admin/login.html')


@app.route('/admin/logout')
def admin_logout():
    session.pop('user_id', None)
    return redirect(url_for('admin_login'))


@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    user = User.query.get(session['user_id'])
    pages = Page.query.order_by(Page.updated_at.desc()).all()
    return render_template('admin/dashboard.html', user=user, pages=pages)


@app.route('/admin/pages')
@admin_required
def admin_pages():
    user = User.query.get(session['user_id'])
    pages = Page.query.order_by(Page.updated_at.desc()).all()
    return render_template('admin/pages.html', user=user, pages=pages)


@app.route('/admin/pages/new', methods=['GET', 'POST'])
@admin_required
def admin_page_new():
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        slug = request.form.get('slug', '').strip()
        content = request.form.get('content', '')
        twig_enabled = request.form.get('twig_enabled') == 'on'
        published = request.form.get('published') == 'on'

        if not title or not slug:
            return render_template('admin/page_edit.html', user=user, page=None,
                                   error='Title and slug are required')

        existing = Page.query.filter_by(slug=slug).first()
        if existing:
            return render_template('admin/page_edit.html', user=user, page=None,
                                   error='A page with this slug already exists')

        page = Page(
            title=title,
            slug=slug,
            content=content,
            twig_enabled=twig_enabled,
            published=published,
            author_id=user.id
        )
        db.session.add(page)
        db.session.commit()
        flash('Page created successfully', 'success')
        return redirect(url_for('admin_page_edit', page_id=page.id))

    return render_template('admin/page_edit.html', user=user, page=None)


@app.route('/admin/pages/<int:page_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_page_edit(page_id):
    user = User.query.get(session['user_id'])
    page = Page.query.get_or_404(page_id)

    if request.method == 'POST':
        page.title = request.form.get('title', '').strip()
        page.slug = request.form.get('slug', '').strip()
        page.content = request.form.get('content', '')
        page.twig_enabled = request.form.get('twig_enabled') == 'on'
        page.published = request.form.get('published') == 'on'
        db.session.commit()
        flash('Page updated successfully', 'success')
        return redirect(url_for('admin_page_edit', page_id=page.id))

    return render_template('admin/page_edit.html', user=user, page=page)


@app.route('/admin/pages/<int:page_id>/preview')
@admin_required
def admin_page_preview(page_id):
    page = Page.query.get_or_404(page_id)
    content = page.content or ''
    if page.twig_enabled:
        content = render_page_content(content, page)
    return render_template('site/page.html', page=page, rendered_content=Markup(content), preview=True)


@app.route('/admin/pages/<int:page_id>/delete', methods=['POST'])
@admin_required
def admin_page_delete(page_id):
    page = Page.query.get_or_404(page_id)
    db.session.delete(page)
    db.session.commit()
    flash('Page deleted', 'success')
    return redirect(url_for('admin_pages'))


@app.route('/admin/configuration')
@admin_required
def admin_configuration():
    user = User.query.get(session['user_id'])
    settings = Setting.query.all()
    return render_template('admin/configuration.html', user=user, settings=settings)


@app.route('/admin/users')
@admin_required
def admin_users():
    user = User.query.get(session['user_id'])
    users = User.query.all()
    return render_template('admin/users.html', user=user, users=users)
