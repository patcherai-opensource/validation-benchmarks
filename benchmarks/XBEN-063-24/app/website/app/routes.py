from flask import render_template, redirect, url_for, request, session, Response, jsonify
from functools import wraps

from app import app
from app.db import db
from app.models import User, Page, SiteConfig
from app.template_engine import render_page_content


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('login'))
        user = User.query.get(user_id)
        if not user or not user.is_active:
            session.pop('user_id', None)
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


@app.context_processor
def inject_nav():
    nav_pages = Page.query.filter_by(published=True).order_by(Page.created_at.asc()).all()
    return dict(nav_pages=nav_pages)


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    return response


@app.route('/')
def index():
    pages = Page.query.filter_by(published=True).order_by(Page.created_at.desc()).all()
    site_title = _get_site_config('site_title', 'NovaCMS')
    return render_template('index.html', pages=pages, site_title=site_title)


@app.route('/page/<slug>')
def view_page(slug):
    page = Page.query.filter_by(slug=slug, published=True).first()
    if not page:
        return render_template('404.html'), 404

    if page.template_processing:
        rendered_content = render_page_content(page.content, {
            'page': page,
            'site_title': _get_site_config('site_title', 'NovaCMS'),
        })
    else:
        rendered_content = page.content

    site_title = _get_site_config('site_title', 'NovaCMS')
    return render_template('page.html', page=page, rendered_content=rendered_content,
                           site_title=site_title)


@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    if session.get('user_id'):
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username, password=password).first()
        if user and user.is_active:
            session['user_id'] = user.id
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin/login.html', error='Invalid credentials')
    return render_template('admin/login.html')


@app.route('/admin/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))


@app.route('/admin')
@login_required
def admin_dashboard():
    user = User.query.get(session['user_id'])
    pages = Page.query.order_by(Page.updated_at.desc()).all()
    total_pages = Page.query.count()
    published_count = Page.query.filter_by(published=True).count()
    return render_template('admin/dashboard.html', user=user, pages=pages,
                           total_pages=total_pages, published_count=published_count)


@app.route('/admin/pages')
@login_required
def admin_pages():
    user = User.query.get(session['user_id'])
    pages = Page.query.order_by(Page.updated_at.desc()).all()
    return render_template('admin/pages.html', user=user, pages=pages)


@app.route('/admin/pages/new', methods=['GET', 'POST'])
@login_required
def admin_page_new():
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        slug = request.form.get('slug', '').strip()
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '')
        template_processing = request.form.get('template_processing') == 'on'
        published = request.form.get('published') == 'on'

        if not slug or not title:
            return render_template('admin/page_edit.html', user=user,
                                   error='Slug and title are required', page=None)

        existing = Page.query.filter_by(slug=slug).first()
        if existing:
            return render_template('admin/page_edit.html', user=user,
                                   error='A page with this slug already exists', page=None)

        page = Page(
            slug=slug,
            title=title,
            content=content,
            template_processing=template_processing,
            published=published,
            author_id=user.id
        )
        db.session.add(page)
        db.session.commit()
        return redirect(url_for('admin_pages'))

    return render_template('admin/page_edit.html', user=user, page=None)


@app.route('/admin/pages/<int:page_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_page_edit(page_id):
    user = User.query.get(session['user_id'])
    page = Page.query.get_or_404(page_id)

    if request.method == 'POST':
        page.title = request.form.get('title', '').strip()
        page.slug = request.form.get('slug', '').strip()
        page.content = request.form.get('content', '')
        page.template_processing = request.form.get('template_processing') == 'on'
        page.published = request.form.get('published') == 'on'
        db.session.commit()
        return redirect(url_for('admin_pages'))

    return render_template('admin/page_edit.html', user=user, page=page)


@app.route('/admin/pages/<int:page_id>/preview', methods=['POST'])
@login_required
def admin_page_preview(page_id):
    page = Page.query.get_or_404(page_id)
    content = request.form.get('content', page.content)
    template_processing = request.form.get('template_processing') == 'on'

    if template_processing:
        rendered = render_page_content(content, {
            'page': page,
            'site_title': _get_site_config('site_title', 'NovaCMS'),
        })
    else:
        rendered = content

    return jsonify({'html': rendered})


@app.route('/admin/pages/preview', methods=['POST'])
@login_required
def admin_page_preview_new():
    content = request.form.get('content', '')
    template_processing = request.form.get('template_processing') == 'on'

    if template_processing:
        rendered = render_page_content(content, {
            'page': None,
            'site_title': _get_site_config('site_title', 'NovaCMS'),
        })
    else:
        rendered = content

    return jsonify({'html': rendered})


@app.route('/admin/pages/<int:page_id>/delete', methods=['POST'])
@login_required
def admin_page_delete(page_id):
    page = Page.query.get_or_404(page_id)
    db.session.delete(page)
    db.session.commit()
    return redirect(url_for('admin_pages'))


@app.route('/admin/settings', methods=['GET', 'POST'])
@login_required
def admin_settings():
    user = User.query.get(session['user_id'])
    if user.role != 'admin':
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        site_title = request.form.get('site_title', 'NovaCMS')
        _set_site_config('site_title', site_title)
        return redirect(url_for('admin_settings'))

    site_title = _get_site_config('site_title', 'NovaCMS')
    return render_template('admin/settings.html', user=user, site_title=site_title)


@app.route('/admin/profile', methods=['GET', 'POST'])
@login_required
def admin_profile():
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        user.name = request.form.get('name', user.name)
        user.email = request.form.get('email', user.email)
        new_password = request.form.get('new_password', '').strip()
        if new_password:
            user.password = new_password
        db.session.commit()
        return render_template('admin/profile.html', user=user, success='Profile updated')
    return render_template('admin/profile.html', user=user)


def _get_site_config(key, default=''):
    config = SiteConfig.query.filter_by(key=key).first()
    if config:
        return config.value
    return default


def _set_site_config(key, value):
    config = SiteConfig.query.filter_by(key=key).first()
    if config:
        config.value = value
    else:
        config = SiteConfig(key=key, value=value)
        db.session.add(config)
    db.session.commit()
