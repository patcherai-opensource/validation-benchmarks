from flask import (Flask, render_template, redirect, url_for,
                   request, session, Response, flash, jsonify, abort)
from jinja2 import Environment, BaseLoader, TemplateSyntaxError, UndefinedError
from datetime import datetime
from functools import wraps

from app import app
from app.db import db
from app.models import User, Page, SiteConfig
from app.utils import sanitize_template_content
from app.twig_extension import register_twig_extensions

import json
import re


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('admin_login'))
        user = User.query.get(user_id)
        if not user or not user.is_active:
            session.pop('user_id', None)
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated


def get_current_user():
    user_id = session.get('user_id')
    if user_id:
        return User.query.get(user_id)
    return None


@app.after_request
def add_header(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500


# --- Public routes (front-end site) ---

@app.route('/')
def index():
    pages = Page.query.filter_by(published=True).order_by(Page.updated_at.desc()).all()
    site_title = _get_config('site.title', 'Grav CMS')
    return render_template('site/index.html', pages=pages, site_title=site_title)


@app.route('/page/<slug>')
def view_page(slug):
    page = Page.query.filter_by(slug=slug, published=True).first_or_404()
    site_title = _get_config('site.title', 'Grav CMS')

    rendered_content = page.content
    if page.process_twig:
        try:
            rendered_content = _render_twig_content(page.content)
        except Exception:
            rendered_content = page.content

    return render_template('site/page.html', page=page,
                           rendered_content=rendered_content,
                           site_title=site_title)


# --- Admin panel routes ---

@app.route('/admin')
@app.route('/admin/')
def admin_index():
    if session.get('user_id'):
        return redirect(url_for('admin_dashboard'))
    return redirect(url_for('admin_login'))


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        user = User.query.filter_by(username=username, password=password).first()
        if user and user.is_active:
            session['user_id'] = user.id
            user.last_login = datetime.utcnow()
            db.session.commit()
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password', 'error')
            return render_template('admin/login.html')

    return render_template('admin/login.html')


@app.route('/admin/logout')
def admin_logout():
    session.pop('user_id', None)
    return redirect(url_for('admin_login'))


@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    user = get_current_user()
    pages = Page.query.order_by(Page.updated_at.desc()).all()
    total_published = Page.query.filter_by(published=True).count()
    total_drafts = Page.query.filter_by(published=False).count()
    return render_template('admin/dashboard.html', user=user, pages=pages,
                           total_published=total_published, total_drafts=total_drafts)


@app.route('/admin/pages')
@login_required
def admin_pages():
    user = get_current_user()
    pages = Page.query.order_by(Page.updated_at.desc()).all()
    return render_template('admin/pages.html', user=user, pages=pages)


@app.route('/admin/pages/new', methods=['GET', 'POST'])
@login_required
def admin_page_new():
    user = get_current_user()

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        slug = request.form.get('slug', '').strip()
        content = request.form.get('content', '')
        template = request.form.get('template', 'default')
        published = request.form.get('published') == 'on'
        process_twig = request.form.get('process_twig') == 'on'
        meta_description = request.form.get('meta_description', '').strip()
        category = request.form.get('category', 'general').strip()

        if not title or not slug:
            flash('Title and slug are required', 'error')
            return render_template('admin/page_edit.html', user=user, page=None,
                                   form_data=request.form)

        existing = Page.query.filter_by(slug=slug).first()
        if existing:
            flash('A page with this slug already exists', 'error')
            return render_template('admin/page_edit.html', user=user, page=None,
                                   form_data=request.form)

        page = Page(
            title=title,
            slug=slug,
            content=content,
            template=template,
            published=published,
            process_twig=process_twig,
            author_id=user.id,
            meta_description=meta_description,
            category=category
        )
        db.session.add(page)
        db.session.commit()

        flash('Page created successfully', 'success')
        return redirect(url_for('admin_page_edit', page_id=page.id))

    return render_template('admin/page_edit.html', user=user, page=None,
                           form_data={})


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
        page.process_twig = request.form.get('process_twig') == 'on'
        page.meta_description = request.form.get('meta_description', '').strip()
        page.category = request.form.get('category', 'general').strip()
        page.updated_at = datetime.utcnow()

        db.session.commit()
        flash('Page saved successfully', 'success')
        return redirect(url_for('admin_page_edit', page_id=page.id))

    return render_template('admin/page_edit.html', user=user, page=page,
                           form_data={})


@app.route('/admin/pages/<int:page_id>/delete', methods=['POST'])
@login_required
def admin_page_delete(page_id):
    page = Page.query.get_or_404(page_id)
    db.session.delete(page)
    db.session.commit()
    flash('Page deleted', 'success')
    return redirect(url_for('admin_pages'))


@app.route('/admin/pages/<int:page_id>/preview', methods=['POST'])
@login_required
def admin_page_preview(page_id):
    """Preview page with Twig processing."""
    user = get_current_user()
    page = Page.query.get_or_404(page_id)
    content = request.form.get('content', page.content)
    process_twig = request.form.get('process_twig') == 'on'

    rendered_content = content
    error_msg = None

    if process_twig:
        try:
            rendered_content = _render_twig_content(content)
        except ValueError as e:
            error_msg = str(e)
            rendered_content = content
        except Exception as e:
            error_msg = 'Template processing error'
            rendered_content = content

    return render_template('admin/preview.html', user=user, page=page,
                           rendered_content=rendered_content, error_msg=error_msg)


@app.route('/admin/config', methods=['GET', 'POST'])
@login_required
def admin_config():
    user = get_current_user()
    if user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        for key in ['site.title', 'site.description', 'site.author',
                     'system.twig.cache', 'system.pages.theme']:
            value = request.form.get(key, '')
            config = SiteConfig.query.filter_by(key=key).first()
            if config:
                config.value = value
            else:
                config = SiteConfig(key=key, value=value)
                db.session.add(config)
        db.session.commit()
        flash('Configuration saved', 'success')

    configs = {c.key: c.value for c in SiteConfig.query.all()}
    return render_template('admin/config.html', user=user, configs=configs)


@app.route('/admin/users')
@login_required
def admin_users():
    user = get_current_user()
    if user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('admin_dashboard'))
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', user=user, users=users)


# --- API endpoints ---

@app.route('/api/pages', methods=['GET'])
def api_pages():
    pages = Page.query.filter_by(published=True).all()
    return jsonify([{
        'id': p.id,
        'title': p.title,
        'slug': p.slug,
        'category': p.category,
        'created_at': p.created_at.isoformat() if p.created_at else None,
        'updated_at': p.updated_at.isoformat() if p.updated_at else None
    } for p in pages])


# --- Helper functions ---

def _render_twig_content(content):
    """
    Render page content with Twig/Jinja2 processing enabled.
    Applies security checks before rendering.
    """
    sanitize_template_content(content)

    env = Environment(loader=BaseLoader())
    register_twig_extensions(env)

    template = env.from_string(content)
    result = template.render(
        site={'title': _get_config('site.title', 'Grav CMS')},
        page={'title': 'Preview'},
    )
    return result


def _get_config(key, default=''):
    config = SiteConfig.query.filter_by(key=key).first()
    return config.value if config else default
