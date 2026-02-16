import os
import re
import json
import markdown
from datetime import datetime
from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response, abort
from markupsafe import Markup

from app import app
from app.db import db
from app.models import User, Page
from app.content_security import check_template_safety


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response


@app.route('/')
def index():
    return redirect(url_for('login'))


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
            session['username'] = user.username
            session['role'] = user.role
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    user = User.query.get(user_id)
    pages = Page.query.order_by(Page.sort_order).all()
    return render_template('dashboard.html', user=user, pages=pages)


@app.route('/pages')
def pages_list():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    pages = Page.query.order_by(Page.sort_order).all()
    return render_template('pages_list.html', pages=pages)


@app.route('/pages/new', methods=['GET', 'POST'])
def page_create():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    user = User.query.get(user_id)
    if user.role not in ('admin', 'editor'):
        abort(403)

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        slug = request.form.get('slug', '').strip()
        body = request.form.get('body', '')
        twig_enabled = request.form.get('twig_processing') == 'on'

        if not title or not slug:
            return render_template('page_editor.html', error='Title and slug are required',
                                   title=title, slug=slug, body=body,
                                   twig_enabled=twig_enabled, editing=False)

        existing = Page.query.filter_by(slug=slug).first()
        if existing:
            return render_template('page_editor.html', error='A page with this slug already exists',
                                   title=title, slug=slug, body=body,
                                   twig_enabled=twig_enabled, editing=False)

        max_order = db.session.query(db.func.max(Page.sort_order)).scalar() or 0

        page = Page(
            title=title,
            slug=slug,
            body=body,
            twig_processing=twig_enabled,
            author_id=user_id,
            sort_order=max_order + 1,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(page)
        db.session.commit()

        return redirect(url_for('pages_list'))

    return render_template('page_editor.html', editing=False, title='', slug='', body='',
                           twig_enabled=False)


@app.route('/pages/<slug>/edit', methods=['GET', 'POST'])
def page_edit(slug):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    user = User.query.get(user_id)
    if user.role not in ('admin', 'editor'):
        abort(403)

    page = Page.query.filter_by(slug=slug).first_or_404()

    if request.method == 'POST':
        page.title = request.form.get('title', '').strip()
        page.body = request.form.get('body', '')
        page.twig_processing = request.form.get('twig_processing') == 'on'
        page.updated_at = datetime.utcnow()
        db.session.commit()
        return redirect(url_for('page_view', slug=slug))

    return render_template('page_editor.html', editing=True, page=page,
                           title=page.title, slug=page.slug, body=page.body,
                           twig_enabled=page.twig_processing)


@app.route('/pages/<slug>/delete', methods=['POST'])
def page_delete(slug):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    user = User.query.get(user_id)
    if user.role != 'admin':
        abort(403)

    page = Page.query.filter_by(slug=slug).first_or_404()
    db.session.delete(page)
    db.session.commit()
    return redirect(url_for('pages_list'))


def render_page_content(page):
    """Render page content with optional Twig/template processing."""
    content = page.body

    if page.twig_processing:
        safety_result = check_template_safety(content)
        if not safety_result['safe']:
            return '<div class="alert alert-danger">Template processing blocked: ' + \
                   safety_result['reason'] + '</div>'

        try:
            content = render_template_string(content)
        except Exception:
            return '<div class="alert alert-warning">Template rendering error</div>'

    # Convert markdown to HTML
    html_content = markdown.markdown(content, extensions=['tables', 'fenced_code', 'codehilite'])
    return Markup(html_content)


@app.route('/pages/<slug>')
def page_view(slug):
    page = Page.query.filter_by(slug=slug).first_or_404()
    rendered = render_page_content(page)
    all_pages = Page.query.order_by(Page.sort_order).all()
    return render_template('page_view.html', page=page, rendered_content=rendered, pages=all_pages)


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    user = User.query.get(user_id)

    if request.method == 'POST':
        user.display_name = request.form.get('display_name', user.display_name)
        user.email = request.form.get('email', user.email)
        db.session.commit()
        return redirect(url_for('dashboard'))

    return render_template('profile.html', user=user)


@app.route('/site-config')
def site_config():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    user = User.query.get(user_id)
    if user.role != 'admin':
        abort(403)

    return render_template('site_config.html', user=user)


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', code=404, message='Page not found'), 404


@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', code=403, message='Access denied'), 403


@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', code=500, message='Internal server error'), 500
