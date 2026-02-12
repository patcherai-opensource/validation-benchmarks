from flask import (Flask, render_template, render_template_string,
                   redirect, url_for, request, session, Response, abort, jsonify)
from functools import wraps
import os

from app import app
from app.db import db
from app.models import User, Page, Config


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated


def get_site_config():
    configs = Config.query.all()
    site = {}
    for c in configs:
        site[c.key] = c.value
    return site


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    return response


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error_code=404,
                           error_message='Page not found'), 404


@app.errorhandler(500)
def internal_error(e):
    return render_template('error.html', error_code=500,
                           error_message='Internal server error'), 500


# ---- Frontend routes (public pages) ----

@app.route('/')
def index():
    pages = Page.query.filter_by(visible=True, routable=True).order_by(Page.order).all()
    home = Page.query.filter_by(slug='home').first()
    site = get_site_config()
    content_html = ''
    if home:
        content_html = home.content
    return render_template('frontend/page.html', page=home, pages=pages, site=site,
                           content_html=content_html)


@app.route('/page/<slug>')
def view_page(slug):
    page = Page.query.filter_by(slug=slug, routable=True).first()
    if not page:
        abort(404)
    pages = Page.query.filter_by(visible=True, routable=True).order_by(Page.order).all()
    site = get_site_config()

    content_html = page.content

    # Process Twig/Jinja2 if enabled for this page
    # Pages with twig processing enabled will have their content rendered
    # through the template engine with the site context available
    if page.process_twig:
        try:
            twig_context = {
                'site': site,
                'page': {
                    'title': page.title,
                    'slug': page.slug,
                    'template': page.template,
                },
                'grav': {
                    'version': '1.7.44',
                    'twig': {
                        'twig': app.jinja_env
                    }
                },
                'pages': [{'title': p.title, 'slug': p.slug} for p in pages],
            }
            content_html = render_template_string(content_html, **twig_context)
        except Exception:
            pass

    return render_template('frontend/page.html', page=page, pages=pages, site=site,
                           content_html=content_html)


# ---- Admin panel routes ----

@app.route('/admin')
def admin_redirect():
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username, password=password).first()
        if user:
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
@login_required
def admin_dashboard():
    user = User.query.get(session['user_id'])
    pages = Page.query.order_by(Page.order).all()
    site = get_site_config()
    return render_template('admin/dashboard.html', user=user, pages=pages, site=site)


@app.route('/admin/pages')
@login_required
def admin_pages():
    user = User.query.get(session['user_id'])
    pages = Page.query.order_by(Page.order).all()
    site = get_site_config()
    return render_template('admin/pages.html', user=user, pages=pages, site=site)


@app.route('/admin/pages/new', methods=['GET', 'POST'])
@login_required
def admin_page_new():
    user = User.query.get(session['user_id'])
    site = get_site_config()

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        slug = request.form.get('slug', '').strip()
        content = request.form.get('content', '')
        template = request.form.get('template', 'default')
        process_twig = request.form.get('process_twig') == 'on'
        visible = request.form.get('visible') == 'on'
        routable = request.form.get('routable') == 'on'

        if not title or not slug:
            return render_template('admin/page_edit.html', user=user, site=site,
                                   error='Title and slug are required',
                                   page=None, is_new=True)

        # Check slug uniqueness
        existing = Page.query.filter_by(slug=slug).first()
        if existing:
            return render_template('admin/page_edit.html', user=user, site=site,
                                   error='A page with this slug already exists',
                                   page=None, is_new=True)

        max_order = db.session.query(db.func.max(Page.order)).scalar() or 0
        page = Page(
            slug=slug,
            title=title,
            content=content,
            template=template,
            process_twig=process_twig,
            visible=visible,
            routable=routable,
            author_id=user.id,
            order=max_order + 1
        )
        db.session.add(page)
        db.session.commit()
        return redirect(url_for('admin_pages'))

    return render_template('admin/page_edit.html', user=user, site=site,
                           page=None, is_new=True)


@app.route('/admin/pages/<int:page_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_page_edit(page_id):
    user = User.query.get(session['user_id'])
    page = Page.query.get_or_404(page_id)
    site = get_site_config()

    if request.method == 'POST':
        page.title = request.form.get('title', page.title).strip()
        page.content = request.form.get('content', page.content)
        page.template = request.form.get('template', page.template)
        page.process_twig = request.form.get('process_twig') == 'on'
        page.visible = request.form.get('visible') == 'on'
        page.routable = request.form.get('routable') == 'on'
        db.session.commit()
        return redirect(url_for('admin_pages'))

    return render_template('admin/page_edit.html', user=user, page=page,
                           site=site, is_new=False)


@app.route('/admin/pages/<int:page_id>/delete', methods=['POST'])
@login_required
def admin_page_delete(page_id):
    user = User.query.get(session['user_id'])
    # Only admins can delete pages
    if user.role != 'admin':
        abort(403)
    page = Page.query.get_or_404(page_id)
    db.session.delete(page)
    db.session.commit()
    return redirect(url_for('admin_pages'))


@app.route('/admin/config')
@login_required
def admin_config():
    user = User.query.get(session['user_id'])
    if user.role != 'admin':
        abort(403)
    configs = Config.query.all()
    site = get_site_config()
    return render_template('admin/config.html', user=user, configs=configs, site=site)


@app.route('/admin/config/update', methods=['POST'])
@login_required
def admin_config_update():
    user = User.query.get(session['user_id'])
    if user.role != 'admin':
        abort(403)
    for key in request.form:
        config = Config.query.filter_by(key=key).first()
        if config:
            config.value = request.form[key]
    db.session.commit()
    return redirect(url_for('admin_config'))


@app.route('/admin/users')
@login_required
def admin_users():
    user = User.query.get(session['user_id'])
    if user.role != 'admin':
        abort(403)
    users = User.query.all()
    site = get_site_config()
    return render_template('admin/users.html', user=user, users=users, site=site)


# Preview endpoint for pages - renders content through template engine
@app.route('/admin/pages/<int:page_id>/preview')
@login_required
def admin_page_preview(page_id):
    page = Page.query.get_or_404(page_id)
    pages = Page.query.filter_by(visible=True, routable=True).order_by(Page.order).all()
    site = get_site_config()

    content_html = page.content

    if page.process_twig:
        try:
            twig_context = {
                'site': site,
                'page': {
                    'title': page.title,
                    'slug': page.slug,
                    'template': page.template,
                },
                'grav': {
                    'version': '1.7.44',
                    'twig': {
                        'twig': app.jinja_env
                    }
                },
                'pages': [{'title': p.title, 'slug': p.slug} for p in pages],
            }
            content_html = render_template_string(content_html, **twig_context)
        except Exception:
            pass

    return render_template('frontend/page.html', page=page, pages=pages, site=site,
                           content_html=content_html)
