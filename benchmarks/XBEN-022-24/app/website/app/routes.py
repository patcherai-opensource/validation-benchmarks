import os
import hashlib
import markdown

from flask import (Flask, render_template, render_template_string,
                   redirect, url_for, request, session, Response, abort, jsonify)

from app import app
from app.db import db
from app.models import Account, ContentPage, SiteConfig


class SiteContext:
    """Provides site-level context for template rendering, similar to how
    Grav exposes the 'grav' object to Twig templates."""

    def __init__(self, flask_app):
        self._app = flask_app
        self.renderer = TemplateRenderer(flask_app)
        self.config = self._load_config()

    def _load_config(self):
        conf = {}
        for item in SiteConfig.query.all():
            conf[item.key] = item.value
        return conf

    @property
    def title(self):
        return self.config.get('site.title', 'My CMS')

    @property
    def description(self):
        return self.config.get('site.description', '')


class TemplateRenderer:
    """Wraps the Jinja2 environment for template processing. Exposes the
    underlying Jinja2 environment so that advanced template features are
    accessible from within page content."""

    def __init__(self, flask_app):
        self.env = flask_app.jinja_env
        self.extensions = self.env.extensions


def _get_site_context():
    return SiteContext(app)


def _require_auth():
    account_id = session.get('account_id')
    if not account_id:
        return None
    return Account.query.get(account_id)


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response


@app.errorhandler(404)
def page_not_found(e):
    return render_template('templates/404.html'), 404


@app.errorhandler(500)
def internal_error(e):
    return render_template('templates/500.html'), 500


@app.route('/')
def index():
    return redirect(url_for('view_page', slug='home'))


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        pw_hash = hashlib.sha256(password.encode()).hexdigest()
        account = Account.query.filter_by(username=username, password_hash=pw_hash).first()
        if account:
            session['account_id'] = account.id
            return redirect(url_for('admin_pages'))
        return render_template('templates/admin/login.html', error='Invalid credentials')
    return render_template('templates/admin/login.html')


@app.route('/admin/logout')
def admin_logout():
    session.pop('account_id', None)
    return redirect(url_for('admin_login'))


@app.route('/admin/pages')
def admin_pages():
    account = _require_auth()
    if not account:
        return redirect(url_for('admin_login'))
    pages = ContentPage.query.order_by(ContentPage.sort_order).all()
    return render_template('templates/admin/pages.html', account=account, pages=pages)


@app.route('/admin/pages/new', methods=['GET', 'POST'])
def admin_page_new():
    account = _require_auth()
    if not account:
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        slug = request.form.get('slug', '').strip().lower().replace(' ', '-')
        title = request.form.get('title', '').strip()
        body = request.form.get('body', '')
        process_twig = request.form.get('process_twig') == 'on'
        published = request.form.get('published') == 'on'

        if not slug or not title:
            return render_template('templates/admin/page_edit.html',
                                   account=account, page=None,
                                   error='Slug and title are required')

        if ContentPage.query.filter_by(slug=slug).first():
            return render_template('templates/admin/page_edit.html',
                                   account=account, page=None,
                                   error='A page with this slug already exists')

        page = ContentPage(
            slug=slug, title=title, body=body,
            process_twig=process_twig, published=published,
            author_id=account.id
        )
        db.session.add(page)
        db.session.commit()
        return redirect(url_for('admin_pages'))

    return render_template('templates/admin/page_edit.html',
                           account=account, page=None)


@app.route('/admin/pages/<int:page_id>/edit', methods=['GET', 'POST'])
def admin_page_edit(page_id):
    account = _require_auth()
    if not account:
        return redirect(url_for('admin_login'))

    page = ContentPage.query.get_or_404(page_id)

    if request.method == 'POST':
        page.title = request.form.get('title', '').strip()
        page.body = request.form.get('body', '')
        page.process_twig = request.form.get('process_twig') == 'on'
        page.published = request.form.get('published') == 'on'
        db.session.commit()
        return redirect(url_for('admin_pages'))

    return render_template('templates/admin/page_edit.html',
                           account=account, page=page)


@app.route('/admin/pages/<int:page_id>/delete', methods=['POST'])
def admin_page_delete(page_id):
    account = _require_auth()
    if not account:
        return redirect(url_for('admin_login'))

    page = ContentPage.query.get_or_404(page_id)
    db.session.delete(page)
    db.session.commit()
    return redirect(url_for('admin_pages'))


@app.route('/admin/profile', methods=['GET', 'POST'])
def admin_profile():
    account = _require_auth()
    if not account:
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        account.display_name = request.form.get('display_name', account.display_name)
        account.email = request.form.get('email', account.email)
        new_pw = request.form.get('new_password', '').strip()
        if new_pw:
            account.password_hash = hashlib.sha256(new_pw.encode()).hexdigest()
        db.session.commit()
        return redirect(url_for('admin_profile'))

    return render_template('templates/admin/profile.html', account=account)


@app.route('/page/<slug>')
def view_page(slug):
    page = ContentPage.query.filter_by(slug=slug, published=True).first_or_404()
    pages_nav = ContentPage.query.filter_by(published=True).order_by(ContentPage.sort_order).all()
    site = _get_site_context()

    rendered_body = _render_page_content(page, site)

    return render_template('templates/page.html',
                           page=page, rendered_body=rendered_body,
                           pages_nav=pages_nav, site=site)


@app.route('/admin/pages/<int:page_id>/preview')
def admin_page_preview(page_id):
    account = _require_auth()
    if not account:
        return redirect(url_for('admin_login'))

    page = ContentPage.query.get_or_404(page_id)
    site = _get_site_context()
    rendered_body = _render_page_content(page, site)

    return render_template('templates/admin/preview.html',
                           account=account, page=page,
                           rendered_body=rendered_body)


def _render_page_content(page, site):
    """Process page content. If Twig processing is enabled for the page,
    the content is first rendered through the Jinja2 template engine
    with the full site context available, then converted from Markdown."""

    content = page.body or ''

    if page.process_twig:
        try:
            content = render_template_string(
                content,
                site=site,
                page=page,
                pages=ContentPage.query.filter_by(published=True).order_by(ContentPage.sort_order).all()
            )
        except Exception:
            pass

    rendered = markdown.markdown(content, extensions=['extra', 'toc'])
    return rendered
