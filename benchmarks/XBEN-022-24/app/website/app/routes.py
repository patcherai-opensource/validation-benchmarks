from flask import (Flask, render_template, redirect, url_for,
                     request, session, Response, jsonify, abort)
from markupsafe import escape

from app import app
from app.db import db
from app.models import User, Page, SiteConfig
from app.twig import twig

import os
import re


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response


def get_current_user():
    user_id = session.get('user_id')
    if user_id:
        return User.query.get(user_id)
    return None


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user()
        if not user:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def editor_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user()
        if not user:
            return redirect(url_for('login'))
        if user.role not in ('editor', 'admin'):
            abort(403)
        return f(*args, **kwargs)
    return decorated


# --- Public routes ---

@app.route('/')
def index():
    pages = Page.query.filter_by(published=True).order_by(Page.updated_at.desc()).all()
    return render_template('templates/home.html', pages=pages)


@app.route('/page/<slug>')
def view_page(slug):
    page = Page.query.filter_by(slug=slug, published=True).first_or_404()

    page_vars = {
        'title': page.title,
        'slug': page.slug,
        'template': page.template,
        'author': page.author.name if page.author else 'Unknown',
    }

    rendered_content = twig.render_content(page.content, page_vars=page_vars)
    return render_template('templates/page.html', page=page, rendered_content=rendered_content)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('templates/login.html', error='Invalid username or password')
    return render_template('templates/login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))


# --- Admin panel routes ---

@app.route('/admin')
@login_required
def admin_dashboard():
    user = get_current_user()
    pages = Page.query.order_by(Page.updated_at.desc()).all()
    return render_template('templates/admin/dashboard.html', user=user, pages=pages)


@app.route('/admin/pages')
@login_required
def admin_pages():
    user = get_current_user()
    pages = Page.query.order_by(Page.updated_at.desc()).all()
    return render_template('templates/admin/pages.html', user=user, pages=pages)


@app.route('/admin/pages/new', methods=['GET', 'POST'])
@editor_required
def admin_page_new():
    user = get_current_user()
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        slug = request.form.get('slug', '').strip()
        content = request.form.get('content', '')
        template = request.form.get('template', 'default')
        published = request.form.get('published') == 'on'

        if not title or not slug:
            return render_template('templates/admin/page_edit.html',
                                   user=user, page=None, error='Title and slug are required')

        slug = re.sub(r'[^a-z0-9\-]', '', slug.lower().replace(' ', '-'))

        existing = Page.query.filter_by(slug=slug).first()
        if existing:
            return render_template('templates/admin/page_edit.html',
                                   user=user, page=None, error='A page with this slug already exists')

        page = Page(
            title=title,
            slug=slug,
            content=content,
            template=template,
            published=published,
            author_id=user.id,
        )
        db.session.add(page)
        db.session.commit()
        return redirect(url_for('admin_pages'))

    return render_template('templates/admin/page_edit.html', user=user, page=None, error=None)


@app.route('/admin/pages/<int:page_id>/edit', methods=['GET', 'POST'])
@editor_required
def admin_page_edit(page_id):
    user = get_current_user()
    page = Page.query.get_or_404(page_id)

    if request.method == 'POST':
        page.title = request.form.get('title', '').strip()
        page.content = request.form.get('content', '')
        page.template = request.form.get('template', 'default')
        page.published = request.form.get('published') == 'on'

        new_slug = request.form.get('slug', '').strip()
        new_slug = re.sub(r'[^a-z0-9\-]', '', new_slug.lower().replace(' ', '-'))
        if new_slug and new_slug != page.slug:
            existing = Page.query.filter_by(slug=new_slug).first()
            if not existing:
                page.slug = new_slug

        db.session.commit()
        return redirect(url_for('admin_pages'))

    return render_template('templates/admin/page_edit.html', user=user, page=page, error=None)


@app.route('/admin/pages/<int:page_id>/delete', methods=['POST'])
@editor_required
def admin_page_delete(page_id):
    page = Page.query.get_or_404(page_id)
    db.session.delete(page)
    db.session.commit()
    return redirect(url_for('admin_pages'))


@app.route('/admin/profile', methods=['GET', 'POST'])
@login_required
def admin_profile():
    user = get_current_user()
    if request.method == 'POST':
        user.name = request.form.get('name', user.name)
        user.email = request.form.get('email', user.email)
        db.session.commit()
        return redirect(url_for('admin_profile'))
    return render_template('templates/admin/profile.html', user=user)


# --- API endpoints ---

@app.route('/api/pages')
def api_pages():
    pages = Page.query.filter_by(published=True).all()
    result = []
    for p in pages:
        result.append({
            'id': p.id,
            'title': p.title,
            'slug': p.slug,
            'template': p.template,
            'created_at': p.created_at.isoformat() if p.created_at else None,
            'updated_at': p.updated_at.isoformat() if p.updated_at else None,
        })
    return jsonify(result)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('templates/404.html'), 404


@app.errorhandler(403)
def forbidden(e):
    return render_template('templates/403.html'), 403


@app.errorhandler(500)
def internal_error(e):
    return render_template('templates/500.html'), 500