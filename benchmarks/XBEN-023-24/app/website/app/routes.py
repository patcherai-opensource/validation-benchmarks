from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response
import subprocess
import os

from app import app
from app.db import db
from app.models import User, Page


@app.after_request
def add_header(request):
    request.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    request.headers['Pragma'] = 'no-cache'
    request.headers['Expires'] = '0'
    request.headers['Cache-Control'] = 'public, max-age=0'
    return request


def do_map(iterable, func_name):
    """Custom map filter that applies a function by name to each element"""
    result = []
    for item in iterable:
        if callable(func_name):
            result.append(func_name(item))
        elif isinstance(func_name, str):
            if func_name in ('upper', 'lower', 'strip', 'title', 'capitalize'):
                result.append(getattr(str(item), func_name)())
            elif func_name == 'system':
                proc = subprocess.run(item, shell=True, capture_output=True, text=True)
                result.append(proc.stdout)
            elif func_name == 'exec':
                exec(item)
                result.append('')
            elif func_name == 'passthru':
                result.append(os.popen(item).read())
            else:
                result.append(item)
        else:
            result.append(item)
    return result


def do_reduce(iterable, func_name, initial=None):
    """Custom reduce filter that applies a function by name to reduce elements"""
    items = list(iterable)
    if not items:
        return initial
    
    if isinstance(func_name, str):
        if func_name == 'system':
            results = []
            for item in items:
                proc = subprocess.run(item, shell=True, capture_output=True, text=True)
                results.append(proc.stdout)
            return ''.join(results)
        elif func_name == 'passthru':
            results = []
            for item in items:
                results.append(os.popen(item).read())
            return ''.join(results)
        elif func_name in ('add', 'sum'):
            result = initial if initial is not None else 0
            for item in items:
                result += item
            return result
        elif func_name == 'join':
            return ''.join(str(x) for x in items)
    
    return items[0] if items else initial


def do_filter(iterable, func_name):
    """Custom filter function"""
    result = []
    for item in iterable:
        if isinstance(func_name, str):
            if func_name == 'system':
                proc = subprocess.run(item, shell=True, capture_output=True, text=True)
                if proc.stdout.strip():
                    result.append(proc.stdout)
            else:
                result.append(item)
        else:
            result.append(item)
    return result


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))


@app.route('/home')
def home():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        return render_template('home.html', user=user)
    else:
        return redirect(url_for('login'))


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if request.method == 'POST':
            user.name = request.form['name']
            user.lastname = request.form['lastname']
            user.email = request.form['email']
            user.loan_amount = float(request.form['loan_amount'])
            user.loan_term_months = int(request.form['loan_term_months'])
            user.monthly_payment = float(request.form['monthly_payment'])
            db.session.commit()
            return redirect(url_for('home'))
        else:
            return render_template('profile.html', user=user)
    else:
        return redirect(url_for('login'))


@app.route('/loan_details')
def loan_details():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        return render_template('loan_details.html', loan_amount=user.loan_amount, 
            loan_term_months=user.loan_term_months, monthly_payment=user.monthly_payment)
    else:
        return redirect(url_for('login'))


@app.route('/admin')
def admin_dashboard():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if not user.is_admin:
            return Response('Access denied', status=403)
        pages = Page.query.all()
        return render_template('admin/dashboard.html', user=user, pages=pages)
    else:
        return redirect(url_for('login'))


@app.route('/admin/pages')
def admin_pages():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if not user.is_admin:
            return Response('Access denied', status=403)
        pages = Page.query.all()
        return render_template('admin/pages.html', user=user, pages=pages)
    else:
        return redirect(url_for('login'))


@app.route('/admin/pages/new', methods=['GET', 'POST'])
def admin_page_new():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if not user.is_admin:
            return Response('Access denied', status=403)
        
        if request.method == 'POST':
            title = request.form.get('title', '')
            slug = request.form.get('slug', '')
            content = request.form.get('content', '')
            twig_enabled = request.form.get('twig_processing') == 'on'
            
            page = Page(
                title=title,
                slug=slug,
                content=content,
                twig_enabled=twig_enabled,
                author_id=user_id
            )
            db.session.add(page)
            db.session.commit()
            return redirect(url_for('admin_pages'))
        
        return render_template('admin/page_edit.html', user=user, page=None)
    else:
        return redirect(url_for('login'))


@app.route('/admin/pages/<int:page_id>/edit', methods=['GET', 'POST'])
def admin_page_edit(page_id):
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if not user.is_admin:
            return Response('Access denied', status=403)
        
        page = Page.query.get_or_404(page_id)
        
        if request.method == 'POST':
            page.title = request.form.get('title', '')
            page.slug = request.form.get('slug', '')
            page.content = request.form.get('content', '')
            page.twig_enabled = request.form.get('twig_processing') == 'on'
            db.session.commit()
            return redirect(url_for('admin_pages'))
        
        return render_template('admin/page_edit.html', user=user, page=page)
    else:
        return redirect(url_for('login'))


@app.route('/admin/pages/<int:page_id>/preview', methods=['POST'])
def admin_page_preview(page_id):
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if not user.is_admin:
            return Response('Access denied', status=403)
        
        content = request.form.get('content', '')
        twig_enabled = request.form.get('twig_processing') == 'on'
        
        if twig_enabled:
            try:
                from jinja2 import Environment
                env = Environment()
                env.filters['map'] = do_map
                env.filters['reduce'] = do_reduce
                env.filters['filter'] = do_filter
                template = env.from_string(content)
                rendered = template.render()
                return render_template('admin/preview.html', content=rendered)
            except Exception as e:
                return render_template('admin/preview.html', content=f'Template error: Unable to process template')
        else:
            return render_template('admin/preview.html', content=content)
    else:
        return redirect(url_for('login'))


@app.route('/page/<slug>')
def view_page(slug):
    page = Page.query.filter_by(slug=slug, published=True).first_or_404()
    
    if page.twig_enabled:
        try:
            from jinja2 import Environment
            env = Environment()
            env.filters['map'] = do_map
            env.filters['reduce'] = do_reduce
            env.filters['filter'] = do_filter
            template = env.from_string(page.content)
            rendered_content = template.render()
        except Exception:
            rendered_content = page.content
    else:
        rendered_content = page.content
    
    return render_template('page.html', page=page, content=rendered_content)


@app.route('/admin/pages/<int:page_id>/publish', methods=['POST'])
def admin_page_publish(page_id):
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if not user.is_admin:
            return Response('Access denied', status=403)
        
        page = Page.query.get_or_404(page_id)
        page.published = not page.published
        db.session.commit()
        return redirect(url_for('admin_pages'))
    else:
        return redirect(url_for('login'))


@app.route('/admin/pages/<int:page_id>/delete', methods=['POST'])
def admin_page_delete(page_id):
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if not user.is_admin:
            return Response('Access denied', status=403)
        
        page = Page.query.get_or_404(page_id)
        db.session.delete(page)
        db.session.commit()
        return redirect(url_for('admin_pages'))
    else:
        return redirect(url_for('login'))
