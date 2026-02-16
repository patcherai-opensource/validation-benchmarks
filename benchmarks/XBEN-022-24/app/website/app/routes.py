from flask import render_template, render_template_string, redirect, url_for, request, session, Response, jsonify, abort
from markupsafe import Markup

from app import app
from app.db import db
from app.models import User, Page
from app.config import site_config

import os
import re


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    # Remove server header
    response.headers.pop('Server', None)
    return response


def get_current_user():
    """Retrieve current user from session."""
    user_id = session.get('user_id')
    if user_id:
        return User.query.get(user_id)
    return None


def require_auth(f):
    """Decorator to require authentication."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user()
        if not user:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def require_role(role):
    """Decorator to require a specific user role."""
    def decorator(f):
        from functools import wraps
        @wraps(f)
        def decorated(*args, **kwargs):
            user = get_current_user()
            if not user:
                return redirect(url_for('login'))
            if user.role != role and user.role != 'admin':
                abort(403)
            return f(*args, **kwargs)
        return decorated
    return decorator


# ---- Public Routes ----

@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        else:
            return render_template('templates/login.html', error='Invalid username or password')
    return render_template('templates/login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))


# ---- Dashboard ----

@app.route('/dashboard')
@require_auth
def dashboard():
    user = get_current_user()
    pages = Page.query.order_by(Page.updated_at.desc()).all()
    return render_template('templates/dashboard.html', user=user, pages=pages)


# ---- Page Management ----

@app.route('/pages')
@require_auth
def page_list():
    user = get_current_user()
    pages = Page.query.order_by(Page.sort_order.asc(), Page.title.asc()).all()
    return render_template('templates/pages.html', user=user, pages=pages)


@app.route('/pages/new', methods=['GET', 'POST'])
@require_role('editor')
def page_create():
    user = get_current_user()
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        slug = request.form.get('slug', '').strip()
        content = request.form.get('content', '')
        template_name = request.form.get('template', 'default')
        published = request.form.get('published') == '1'

        if not title or not slug:
            return render_template('templates/page_editor.html', user=user,
                                   error='Title and slug are required.',
                                   page=None, mode='create')

        # Check slug uniqueness
        existing = Page.query.filter_by(slug=slug).first()
        if existing:
            return render_template('templates/page_editor.html', user=user,
                                   error='A page with this slug already exists.',
                                   page=None, mode='create')

        slug = re.sub(r'[^a-z0-9\-]', '', slug.lower())

        page = Page(
            title=title,
            slug=slug,
            content=content,
            template=template_name,
            published=published,
            author_id=user.id,
            sort_order=0
        )
        db.session.add(page)
        db.session.commit()
        return redirect(url_for('page_edit', page_id=page.id))

    return render_template('templates/page_editor.html', user=user, page=None, mode='create')


@app.route('/pages/<int:page_id>/edit', methods=['GET', 'POST'])
@require_role('editor')
def page_edit(page_id):
    user = get_current_user()
    page = Page.query.get_or_404(page_id)

    if request.method == 'POST':
        page.title = request.form.get('title', page.title).strip()
        page.content = request.form.get('content', page.content)
        page.template = request.form.get('template', page.template)
        page.published = request.form.get('published') == '1'

        new_slug = request.form.get('slug', page.slug).strip()
        new_slug = re.sub(r'[^a-z0-9\-]', '', new_slug.lower())
        if new_slug != page.slug:
            existing = Page.query.filter_by(slug=new_slug).first()
            if existing and existing.id != page.id:
                return render_template('templates/page_editor.html', user=user,
                                       error='A page with this slug already exists.',
                                       page=page, mode='edit')
            page.slug = new_slug

        db.session.commit()
        return render_template('templates/page_editor.html', user=user, page=page,
                               mode='edit', success='Page saved successfully.')

    return render_template('templates/page_editor.html', user=user, page=page, mode='edit')


@app.route('/pages/<int:page_id>/delete', methods=['POST'])
@require_role('editor')
def page_delete(page_id):
    page = Page.query.get_or_404(page_id)
    db.session.delete(page)
    db.session.commit()
    return redirect(url_for('page_list'))


# ---- Page Rendering (public view) ----

def render_page_content(page):
    """
    Process page content through the template engine.
    Supports Jinja2 template syntax in page content for dynamic pages.
    The site configuration is made available to templates for theming/customization.
    """
    try:
        rendered = render_template_string(
            page.content,
            page=page,
            site=site_config,
            config=site_config
        )
        return rendered
    except Exception:
        return page.content


@app.route('/p/<slug>')
def page_view(slug):
    page = Page.query.filter_by(slug=slug, published=True).first_or_404()
    rendered_content = render_page_content(page)
    return render_template('templates/page_view.html', page=page,
                           rendered_content=Markup(rendered_content))


# ---- Settings ----

@app.route('/settings')
@require_role('editor')
def settings():
    user = get_current_user()
    return render_template('templates/settings.html', user=user, config=site_config)


@app.route('/settings/site', methods=['POST'])
@require_role('editor')
def settings_site():
    user = get_current_user()
    site_config.set('site.title', request.form.get('site_title', site_config.get('site.title')))
    site_config.set('site.description', request.form.get('site_description', site_config.get('site.description')))
    site_config.set('site.author', request.form.get('site_author', site_config.get('site.author')))
    return redirect(url_for('settings'))


# ---- User Profile ----

@app.route('/profile', methods=['GET', 'POST'])
@require_auth
def profile():
    user = get_current_user()
    if request.method == 'POST':
        user.name = request.form.get('name', user.name)
        user.email = request.form.get('email', user.email)
        db.session.commit()
        return render_template('templates/profile.html', user=user, success='Profile updated.')
    return render_template('templates/profile.html', user=user)


# ---- API Endpoints ----

@app.route('/api/pages')
@require_auth
def api_pages():
    pages = Page.query.order_by(Page.sort_order.asc()).all()
    result = []
    for p in pages:
        result.append({
            'id': p.id,
            'title': p.title,
            'slug': p.slug,
            'published': p.published,
            'template': p.template
        })
    return jsonify(result)


# ---- Error Handlers ----

@app.errorhandler(404)
def not_found(e):
    return render_template('templates/404.html'), 404


@app.errorhandler(403)
def forbidden(e):
    return render_template('templates/403.html'), 403


@app.errorhandler(500)
def internal_error(e):
    return render_template('templates/500.html'), 500
