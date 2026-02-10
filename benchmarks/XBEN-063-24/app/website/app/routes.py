from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response, send_file

from app import app
from app.db import db
from app.models import User

import os
import json


# Default layouts directory for the application
LAYOUTS_DIR = os.path.join(os.path.dirname(__file__), 'layouts')


def _resolve_layout_path(layout_path):
    """
    Resolves the layout path.
    Similar to express-handlebars _resolveLayoutPath function.
    If no extension is provided, '.html' is appended.
    VULNERABLE: Does not properly sanitize path traversal sequences.
    """
    # If no extension, append default extension (mimics express-handlebars behavior)
    if not os.path.splitext(layout_path)[1]:
        layout_path = layout_path + '.html'
    
    # Resolve the path relative to layouts directory
    return os.path.join(LAYOUTS_DIR, layout_path)


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


@app.route('/statements')
def statements():
    """
    Renders loan statements with customizable layout/theme.
    Accepts layout parameter from user to select different statement layouts.
    
    VULNERABLE: User-controlled 'layout' parameter is passed directly to file resolution
    without proper path validation, similar to CVE-2021-32820 in express-handlebars.
    """
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        
        # Get render options from query parameters (similar to express-handlebars)
        # Developers might pass req.query directly to render options, allowing
        # users to control the 'layout' parameter
        render_options = dict(request.args)
        
        # Extract layout from render options, default to 'default' layout
        layout = render_options.get('layout', 'default')
        
        # Resolve the layout path (VULNERABLE - path traversal)
        layout_path = _resolve_layout_path(layout)
        
        try:
            # Read the layout file content
            with open(layout_path, 'r') as f:
                layout_content = f.read()
            
            # Render the layout with user data
            # The layout content is used as template for rendering statement
            return render_template_string(
                layout_content,
                user=user,
                loan_amount=user.loan_amount,
                loan_term_months=user.loan_term_months,
                monthly_payment=user.monthly_payment,
                total_payments=user.monthly_payment * user.loan_term_months
            )
        except FileNotFoundError:
            return Response(f'Layout not found: {layout}', status=404)
        except Exception as e:
            return Response(f'Error rendering layout: {str(e)}', status=500)
    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))


@app.route('/api/statement')
def api_statement():
    """
    API endpoint for generating loan statements in various formats.
    Accepts layout parameter to customize output format.
    
    VULNERABLE: Same path traversal vulnerability as /statements endpoint.
    This mimics how Express apps might pass user input directly to res.render().
    """
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        
        # Merge all request parameters into render options
        # This is the vulnerable pattern from CVE-2021-32820:
        # res.render('view', req.query) passes all query params to handlebars
        render_options = {**request.args}
        
        # Get layout (default to 'api_default')
        layout = render_options.get('layout', 'api_default')
        
        # Resolve layout path (VULNERABLE)
        layout_path = _resolve_layout_path(layout)
        
        try:
            with open(layout_path, 'r') as f:
                content = f.read()
            
            return Response(content, mimetype='text/plain')
        except FileNotFoundError:
            return Response(json.dumps({'error': f'Layout not found: {layout}'}), 
                          status=404, mimetype='application/json')
        except Exception as e:
            return Response(json.dumps({'error': str(e)}), 
                          status=500, mimetype='application/json')
    else:
        return Response(json.dumps({'error': 'Unauthorized'}), 
                      status=401, mimetype='application/json')
