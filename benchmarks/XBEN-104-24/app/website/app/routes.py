import json
from functools import wraps
from flask import (render_template, redirect, url_for,
                   request, session, Response, abort)

from app import app
from app.db import db
from app.models import User, Page, Setting
from app.twig import TwigProcessor, GravConfig


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated


def get_current_user():
    user_id = session.get('user_id')
    if user_id:
        return User.query.get(user_id)
    return None


def load_config():
    """Load system configuration from database into a GravConfig object."""
    settings = Setting.query.all()
    config_dict = {}
    for s in settings:
        config_dict[s.key] = s.value
    return GravConfig(config_dict)


def render_page_content(page):
    """Process page content through the Twig engine if enabled."""
    content = page.content

    if page.twig_enabled:
        config = load_config()
        processor = TwigProcessor(config)
        context = {
            'page': {
                'title': page.title,
                'slug': page.slug,
            },
            'site': {
                'title': config.get('site.title', 'GravSite CMS'),
            },
        }
        content = processor.render(content, context)

    return content


@app.after_request
def add_header(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['Server'] = 'GravSite'
    return response


# ---- Public routes ----

@app.route('/')
def index():
    pages = Page.query.filter_by(published=True).all()
    home_page = Page.query.filter_by(slug='home', published=True).first()
    content = ''
    if home_page:
        content = render_page_content(home_page)
    return render_template('site/index.html', pages=pages, content=content,
                           site_title='GravSite CMS')


@app.route('/page/<slug>')
def view_page(slug):
    page = Page.query.filter_by(slug=slug, published=True).first()
    if not page:
        abort(404)
    content = render_page_content(page)
    pages = Page.query.filter_by(published=True).all()
    return render_template('site/page.html', page=page, content=content,
                           pages=pages, site_title='GravSite CMS')


# ---- Admin routes ----

@app.route('/admin')
def admin_index():
    if 'user_id' in session:
        return redirect(url_for('admin_pages'))
    return redirect(url_for('admin_login'))


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username, password=password, is_active=True).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('admin_pages'))
        else:
            return render_template('admin/login.html', error='Invalid credentials')
    return render_template('admin/login.html')


@app.route('/admin/logout')
def admin_logout():
    session.pop('user_id', None)
    return redirect(url_for('admin_login'))


@app.route('/admin/pages')
@login_required
def admin_pages():
    user = get_current_user()
    pages = Page.query.order_by(Page.updated_at.desc()).all()
    return render_template('admin/pages.html', pages=pages, user=user)


@app.route('/admin/pages/new', methods=['GET', 'POST'])
@login_required
def admin_page_new():
    user = get_current_user()
    if request.method == 'POST':
        slug = request.form.get('slug', '').strip()
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '')
        template = request.form.get('template', 'default')
        published = request.form.get('published') == 'on'
        twig_enabled = request.form.get('twig_enabled') == 'on'

        if not slug or not title:
            return render_template('admin/page_edit.html', user=user,
                                   error='Slug and title are required',
                                   page=None)

        existing = Page.query.filter_by(slug=slug).first()
        if existing:
            return render_template('admin/page_edit.html', user=user,
                                   error='A page with this slug already exists',
                                   page=None)

        new_page = Page(
            slug=slug,
            title=title,
            content=content,
            template=template,
            published=published,
            twig_enabled=twig_enabled,
            author_id=user.id,
        )
        db.session.add(new_page)
        db.session.commit()
        return redirect(url_for('admin_pages'))

    return render_template('admin/page_edit.html', user=user, page=None)


@app.route('/admin/pages/<int:page_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_page_edit(page_id):
    user = get_current_user()
    page = Page.query.get_or_404(page_id)

    if request.method == 'POST':
        page.title = request.form.get('title', '').strip()
        page.slug = request.form.get('slug', '').strip()
        page.content = request.form.get('content', '')
        page.template = request.form.get('template', 'default')
        page.published = request.form.get('published') == 'on'
        page.twig_enabled = request.form.get('twig_enabled') == 'on'
        db.session.commit()
        return redirect(url_for('admin_pages'))

    return render_template('admin/page_edit.html', user=user, page=page)


@app.route('/admin/pages/<int:page_id>/delete', methods=['POST'])
@login_required
def admin_page_delete(page_id):
    user = get_current_user()
    if user.role != 'admin':
        abort(403)
    page = Page.query.get_or_404(page_id)
    db.session.delete(page)
    db.session.commit()
    return redirect(url_for('admin_pages'))


@app.route('/admin/settings', methods=['GET', 'POST'])
@login_required
def admin_settings():
    user = get_current_user()
    if user.role != 'admin':
        abort(403)

    if request.method == 'POST':
        site_title = request.form.get('site_title', '')
        site_description = request.form.get('site_description', '')

        for key, value in [('site.title', site_title),
                           ('site.description', site_description)]:
            setting = Setting.query.filter_by(key=key).first()
            if setting:
                setting.value = value
            else:
                db.session.add(Setting(key=key, value=value))
        db.session.commit()
        return redirect(url_for('admin_settings'))

    settings = {}
    for s in Setting.query.all():
        settings[s.key] = s.value
    return render_template('admin/settings.html', user=user, settings=settings)


@app.route('/admin/profile', methods=['GET', 'POST'])
@login_required
def admin_profile():
    user = get_current_user()
    if request.method == 'POST':
        user.name = request.form.get('name', user.name)
        user.email = request.form.get('email', user.email)
        new_password = request.form.get('password', '').strip()
        if new_password:
            user.password = new_password
        db.session.commit()
        return redirect(url_for('admin_profile'))
    return render_template('admin/profile.html', user=user)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('site/404.html'), 404


@app.errorhandler(403)
def forbidden(e):
    return render_template('site/403.html'), 403
