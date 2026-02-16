import os
import subprocess
from functools import wraps

from flask import (render_template, redirect, url_for,
                   request, session)
from markupsafe import Markup
from jinja2.sandbox import SandboxedEnvironment
from jinja2 import BaseLoader, TemplateSyntaxError, UndefinedError

from app import app
from app.db import db
from app.models import User, Page
from app.config import site_config


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('login'))
        user = User.query.get(user_id)
        if not user:
            session.pop('user_id', None)
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def get_current_user():
    user_id = session.get('user_id')
    if user_id:
        return User.query.get(user_id)
    return None


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response


@app.route('/')
def index():
    return redirect(url_for('dashboard'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('user_id'):
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    user = get_current_user()
    my_pages = Page.query.filter_by(author_id=user.id).order_by(Page.updated_at.desc()).all()
    recent_published = Page.query.filter_by(published=True).order_by(Page.updated_at.desc()).limit(10).all()
    return render_template('dashboard.html', user=user, my_pages=my_pages,
                           recent_published=recent_published)


@app.route('/pages')
@login_required
def list_pages():
    user = get_current_user()
    pages = Page.query.order_by(Page.updated_at.desc()).all()
    return render_template('pages.html', user=user, pages=pages)


@app.route('/pages/new', methods=['GET', 'POST'])
@login_required
def create_page():
    user = get_current_user()
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        slug = request.form.get('slug', '').strip().lower().replace(' ', '-')
        body = request.form.get('body', '')
        process_twig = request.form.get('process_twig') == '1'
        published = request.form.get('published') == '1'

        if not title or not slug:
            return render_template('edit_page.html', user=user, error='Title and slug are required',
                                   page=None, title=title, slug=slug, body=body,
                                   process_twig=process_twig, published=published)

        existing = Page.query.filter_by(slug=slug).first()
        if existing:
            return render_template('edit_page.html', user=user, error='A page with this slug already exists',
                                   page=None, title=title, slug=slug, body=body,
                                   process_twig=process_twig, published=published)

        page = Page(
            title=title,
            slug=slug,
            body=body,
            process_twig=process_twig,
            published=published,
            author_id=user.id
        )
        db.session.add(page)
        db.session.commit()
        if published:
            return redirect(url_for('view_page', slug=slug))
        return redirect(url_for('preview_page', slug=slug))

    return render_template('edit_page.html', user=user, page=None, title='', slug='', body='',
                           process_twig=False, published=False, error=None)


@app.route('/pages/<slug>/edit', methods=['GET', 'POST'])
@login_required
def edit_page(slug):
    user = get_current_user()
    page = Page.query.filter_by(slug=slug).first_or_404()

    if request.method == 'POST':
        page.title = request.form.get('title', '').strip()
        page.body = request.form.get('body', '')
        page.process_twig = request.form.get('process_twig') == '1'
        page.published = request.form.get('published') == '1'
        db.session.commit()
        if page.published:
            return redirect(url_for('view_page', slug=page.slug))
        return redirect(url_for('preview_page', slug=page.slug))

    return render_template('edit_page.html', user=user, page=page, title=page.title,
                           slug=page.slug, body=page.body, process_twig=page.process_twig,
                           published=page.published, error=None)


def _resolve_function(name, config):
    """Resolve a function name against the allowed_functions configuration."""
    allowed = config.get('template.allowed_functions')
    if not isinstance(allowed, list) or name not in allowed:
        return None

    import builtins
    fn = getattr(builtins, name, None)
    if fn and callable(fn):
        return fn

    parts = name.split('.')
    if len(parts) == 2:
        try:
            mod = __import__(parts[0])
            fn = getattr(mod, parts[1], None)
            if fn and callable(fn):
                return fn
        except ImportError:
            pass
    return None


def _safe_call(config, name, *args):
    """Invoke a function by name if it is in the allowed_functions list."""
    fn = _resolve_function(name, config)
    if fn is None:
        return ''
    result = fn(*args)
    if hasattr(result, 'read'):
        return result.read()
    if isinstance(result, bytes):
        return result.decode('utf-8', errors='replace')
    return result


def render_page_content(page):
    """Render page content, optionally processing template directives in a sandbox."""
    content = page.body

    if not page.process_twig:
        escaped = content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        return Markup('<div class="page-content">{}</div>'.format(escaped))

    env = SandboxedEnvironment(loader=BaseLoader(), autoescape=False)

    template_vars = {
        'config': site_config,
        'site_name': site_config.get('site.title'),
        'page': {
            'title': page.title,
            'slug': page.slug,
        },
        'now': __import__('datetime').datetime.now(),
        'call': lambda name, *args: _safe_call(site_config, name, *args),
    }

    try:
        tmpl = env.from_string(content)
        rendered = tmpl.render(**template_vars)
    except TemplateSyntaxError:
        rendered = '<div class="alert alert-warning">Template syntax error</div>'
    except UndefinedError:
        rendered = '<div class="alert alert-warning">Template variable error</div>'
    except Exception:
        rendered = '<div class="alert alert-warning">An error occurred while rendering this page</div>'

    return Markup(rendered)


@app.route('/p/<slug>')
def view_page(slug):
    page = Page.query.filter_by(slug=slug, published=True).first_or_404()
    rendered_content = render_page_content(page)
    return render_template('view_page.html', page=page, rendered_content=rendered_content)


@app.route('/pages/<slug>/preview')
@login_required
def preview_page(slug):
    user = get_current_user()
    page = Page.query.filter_by(slug=slug).first_or_404()
    rendered_content = render_page_content(page)
    return render_template('view_page.html', page=page, rendered_content=rendered_content, preview=True)


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = get_current_user()
    if request.method == 'POST':
        user.display_name = request.form.get('display_name', user.display_name)
        user.email = request.form.get('email', user.email)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('profile.html', user=user)


@app.route('/settings')
@login_required
def settings():
    user = get_current_user()
    return render_template('settings.html', user=user, config=site_config)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500
