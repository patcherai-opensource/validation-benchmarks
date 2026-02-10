from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response
import subprocess
import os
from functools import reduce as builtin_reduce

from app import app
from app.db import db
from app.models import User, Page


# Register custom Jinja2 filters that mimic Twig's map/reduce/filter functionality
# VULNERABLE: These filters do not properly validate the callable argument,
# allowing arbitrary function execution similar to CVE-2022-2073 bypass

def unsafe_map_filter(iterable, func_name):
    """
    Custom map filter that applies a function to each element.
    VULNERABLE: Does not validate func_name, allows arbitrary callables.
    Similar to Twig's map() filter vulnerability in Grav CMS.
    """
    # Resolve the function by name - DANGEROUS!
    if callable(func_name):
        func = func_name
    else:
        # Look up function by name in various namespaces
        func = None
        # Check builtins
        import builtins
        if hasattr(builtins, func_name):
            func = getattr(builtins, func_name)
        # Check os module for system functions
        elif hasattr(os, func_name):
            func = getattr(os, func_name)
        # Check subprocess for shell commands
        elif func_name == 'system':
            # Mimic PHP's system() function behavior
            def system_func(cmd):
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                return result.stdout + result.stderr
            func = system_func
        elif func_name == 'exec':
            # Mimic PHP's exec() function
            def exec_func(cmd):
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                return result.stdout
            func = exec_func
        elif func_name == 'passthru':
            # Mimic PHP's passthru() function
            def passthru_func(cmd):
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                return result.stdout + result.stderr
            func = passthru_func
        elif func_name == 'shell_exec':
            # Mimic PHP's shell_exec() function  
            def shell_exec_func(cmd):
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                return result.stdout
            func = shell_exec_func
        elif func_name == 'popen':
            # Mimic PHP's popen() - read output
            def popen_func(cmd):
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                return result.stdout
            func = popen_func
    
    if func is None:
        return list(iterable)
    
    return [func(item) for item in iterable]


def unsafe_reduce_filter(iterable, func_name, initial=None):
    """
    Custom reduce filter that reduces an iterable using a function.
    VULNERABLE: Does not validate func_name, allows arbitrary callables.
    Similar to Twig's reduce() filter vulnerability in Grav CMS.
    """
    # For RCE, we actually want to apply the function to each element
    # This mimics the CVE behavior where reduce can execute commands
    if func_name == 'system' or func_name == 'exec' or func_name == 'passthru' or func_name == 'shell_exec' or func_name == 'popen':
        # Execute the command(s) in the iterable
        results = []
        for cmd in iterable:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            results.append(result.stdout + result.stderr)
        return ''.join(results)
    
    # Default reduce behavior
    func = None
    import builtins
    if hasattr(builtins, func_name):
        func = getattr(builtins, func_name)
    
    if func is None:
        return str(list(iterable))
    
    if initial is not None:
        return builtin_reduce(func, iterable, initial)
    return builtin_reduce(func, iterable)


def unsafe_filter_filter(iterable, func_name):
    """
    Custom filter that filters elements using a function.
    VULNERABLE: Similar to map, does not validate func_name properly.
    """
    func = None
    import builtins
    if hasattr(builtins, func_name):
        func = getattr(builtins, func_name)
    
    if func is None:
        return list(iterable)
    
    return [item for item in iterable if func(item)]


# Register the vulnerable filters with the app
app.jinja_env.filters['map'] = unsafe_map_filter
app.jinja_env.filters['reduce'] = unsafe_reduce_filter
app.jinja_env.filters['filter'] = unsafe_filter_filter


@app.after_request
def add_header(request):
    request.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    request.headers['Pragma'] = 'no-cache'
    request.headers['Expires'] = '0'
    request.headers['Cache-Control'] = 'public, max-age=0'
    return request


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
            # Store user ID in session
            session['user_id'] = user.id
            # If login successful, redirect to home page
            return redirect(url_for('home'))
        else:
            # If login fails, redirect back to login page with an error message
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')


@app.route('/logout')
def logout():
    # Clear user ID from session
    session.pop('user_id', None)
    return redirect(url_for('login'))


@app.route('/home')
def home():
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        return render_template('home.html', user=user)
    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if request.method == 'POST':
            # Update user's profile with new values
            user.name = request.form['name']
            user.lastname = request.form['lastname']
            user.email = request.form['email']
            user.loan_amount = float(request.form['loan_amount'])
            user.loan_term_months = int(request.form['loan_term_months'])
            user.monthly_payment = float(request.form['monthly_payment'])
            db.session.commit()
            return redirect(url_for('home'))  # Redirect to home page after profile update
        else:
            # Render profile template with user's information for GET request
            return render_template('profile.html', user=user)
    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))


@app.route('/loan_details')
def loan_details():
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        return render_template('loan_details.html', loan_amount=user.loan_amount, 
            loan_term_months=user.loan_term_months, monthly_payment=user.monthly_payment)
    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))


# Page management - similar to Grav CMS page editing functionality
@app.route('/pages')
def list_pages():
    """List all pages - requires authentication"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    pages = Page.query.all()
    return render_template('pages.html', pages=pages)


@app.route('/pages/new', methods=['GET', 'POST'])
def new_page():
    """Create a new page - requires authentication"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form.get('title', 'Untitled')
        content = request.form.get('content', '')
        twig_enabled = request.form.get('twig_enabled') == 'on'
        
        page = Page(
            title=title,
            content=content,
            twig_enabled=twig_enabled,
            author_id=user_id
        )
        db.session.add(page)
        db.session.commit()
        
        return redirect(url_for('view_page', page_id=page.id))
    
    return render_template('page_edit.html', page=None)


@app.route('/pages/<int:page_id>')
def view_page(page_id):
    """View a page - processes Twig/Jinja2 if enabled"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    page = Page.query.get_or_404(page_id)
    
    # If Twig processing is enabled, render the content as a template
    # This is the VULNERABLE code path - similar to Grav CMS
    if page.twig_enabled:
        try:
            # VULNERABLE: User content is rendered as a Jinja2 template
            # The custom map/reduce filters can be exploited here
            rendered_content = render_template_string(page.content)
        except Exception as e:
            rendered_content = f"Template Error: {str(e)}"
    else:
        rendered_content = page.content
    
    return render_template('page_view.html', page=page, rendered_content=rendered_content)


@app.route('/pages/<int:page_id>/edit', methods=['GET', 'POST'])
def edit_page(page_id):
    """Edit a page - requires authentication"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    page = Page.query.get_or_404(page_id)
    
    if request.method == 'POST':
        page.title = request.form.get('title', page.title)
        page.content = request.form.get('content', page.content)
        page.twig_enabled = request.form.get('twig_enabled') == 'on'
        db.session.commit()
        
        return redirect(url_for('view_page', page_id=page.id))
    
    return render_template('page_edit.html', page=page)


@app.route('/pages/<int:page_id>/preview', methods=['POST'])
def preview_page(page_id):
    """Preview page content with Twig processing - VULNERABLE endpoint"""
    user_id = session.get('user_id')
    if not user_id:
        return Response('Unauthorized', status=401)
    
    content = request.form.get('content', '')
    twig_enabled = request.form.get('twig_enabled') == 'on'
    
    if twig_enabled:
        try:
            # VULNERABLE: Preview renders user content as template
            rendered_content = render_template_string(content)
        except Exception as e:
            rendered_content = f"Template Error: {str(e)}"
    else:
        rendered_content = content
    
    return rendered_content
