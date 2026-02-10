from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response
from jinja2 import Environment, FileSystemLoader, BaseLoader

from app import app
from app.db import db
from app.models import User

import os

# Invoice templates directory - users can upload custom templates
INVOICE_TEMPLATES_DIR = '/var/www/ssti_include_loan_calculator/invoice_templates/'

# Ensure invoice templates directory exists
os.makedirs(INVOICE_TEMPLATES_DIR, exist_ok=True)

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
            return render_template('templates/login.html', error='Invalid username or password')
    return render_template('templates/login.html')


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
        return render_template('templates/home.html', user=user)
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
            return render_template('templates/profile.html', user=user)
    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))


@app.route('/update_profile', methods=['GET', 'POST'])
def update_profile():
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

            # Check if the post request has the file part
            if 'image_profile' in request.files:
                image_profile = request.files['image_profile']
                # If the user does not select a file, the browser submits an empty file without a filename
                if image_profile.filename != '':

                    safe_dir = '/var/www/ssti_include_loan_calculator/app/static/images/'
                    final_path = os.path.realpath(os.path.join(safe_dir, image_profile.filename))

                    if os.path.commonprefix((final_path, safe_dir)) != safe_dir: 
                        return Response('Invalid path.', status=400)

                    image_profile.save(final_path)
                    user.image_profile_filename = image_profile.filename

            db.session.commit()
        return render_template('templates/profile.html', user=user)

    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))


# ============================================================================
# Invoice Template Management (CVE-2023-46245 style vulnerability)
# Users can upload custom invoice templates which are rendered without sandbox
# ============================================================================

@app.route('/invoice_templates')
def invoice_templates():
    """List available invoice templates"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    user = User.query.get(user_id)
    
    # List all templates in the invoice templates directory
    templates = []
    if os.path.exists(INVOICE_TEMPLATES_DIR):
        for f in os.listdir(INVOICE_TEMPLATES_DIR):
            if f.endswith('.html') or f.endswith('.jinja2'):
                templates.append(f)
    
    return render_template('templates/invoice_templates.html', user=user, templates=templates)


@app.route('/upload_invoice_template', methods=['POST'])
def upload_invoice_template():
    """
    Upload a custom invoice template.
    Similar to Kimai's invoice template upload functionality.
    Allows .html and .jinja2 template files.
    """
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    if 'template_file' not in request.files:
        return Response('No template file provided', status=400)
    
    template_file = request.files['template_file']
    
    if template_file.filename == '':
        return Response('No file selected', status=400)
    
    # Allow .html and .jinja2 template files (like Kimai allows .twig files)
    allowed_extensions = ['.html', '.jinja2']
    filename = template_file.filename
    
    if not any(filename.endswith(ext) for ext in allowed_extensions):
        return Response('Only .html and .jinja2 template files are allowed', status=400)
    
    # Sanitize filename to prevent directory traversal
    safe_filename = os.path.basename(filename)
    
    # Save the template file to the invoice templates directory
    template_path = os.path.join(INVOICE_TEMPLATES_DIR, safe_filename)
    template_file.save(template_path)
    
    return redirect(url_for('invoice_templates'))


@app.route('/render_invoice')
def render_invoice():
    """
    Render an invoice using a selected template.
    VULNERABLE: Renders user-uploaded templates without sandboxing.
    This mirrors CVE-2023-46245 where Kimai rendered user-supplied Twig templates.
    """
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    user = User.query.get(user_id)
    template_name = request.args.get('template')
    
    if not template_name:
        return Response('No template specified', status=400)
    
    # Sanitize template name to prevent directory traversal
    safe_template_name = os.path.basename(template_name)
    template_path = os.path.join(INVOICE_TEMPLATES_DIR, safe_template_name)
    
    if not os.path.exists(template_path):
        return Response('Template not found', status=404)
    
    # VULNERABLE: Load and render user-uploaded template without any sandbox
    # This is the same vulnerability pattern as CVE-2023-46245 in Kimai
    # where user-supplied Twig templates were rendered without sandboxing
    try:
        with open(template_path, 'r') as f:
            template_content = f.read()
        
        # Create a Jinja2 environment without sandbox restrictions
        # This allows arbitrary code execution through template injection
        env = Environment(loader=BaseLoader())
        template = env.from_string(template_content)
        
        # Provide invoice context data
        invoice_data = {
            'user': user,
            'loan_amount': user.loan_amount,
            'loan_term_months': user.loan_term_months,
            'monthly_payment': user.monthly_payment,
            'total_payment': user.monthly_payment * user.loan_term_months,
            'invoice_number': f'INV-{user.id}-001',
            'date': '2024-01-15'
        }
        
        # Render the template with invoice data - NO SANDBOX!
        rendered = template.render(**invoice_data)
        return Response(rendered, content_type='text/html')
        
    except Exception as e:
        return Response(f'Error rendering template: {str(e)}', status=500)


@app.route('/delete_invoice_template', methods=['POST'])
def delete_invoice_template():
    """Delete an invoice template"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    template_name = request.form.get('template_name')
    if not template_name:
        return Response('No template specified', status=400)
    
    safe_template_name = os.path.basename(template_name)
    template_path = os.path.join(INVOICE_TEMPLATES_DIR, safe_template_name)
    
    if os.path.exists(template_path):
        os.remove(template_path)
    
    return redirect(url_for('invoice_templates'))


@app.route('/error')
def error():
    error_message = request.args.get('message', 'An error occurred.')
    error_type = request.args.get('error_type', 'not_implemented.html')
    
    # Only allow specific safe error templates
    allowed_templates = ['not_implemented.html', 'generic_error.html']
    
    if error_type not in allowed_templates:
        error_type = 'not_implemented.html'
    
    # Safely construct the template path
    safe_error_type = 'templates/' + error_type
    
    return render_template('templates/error.html', error_message=error_message, error_type=safe_error_type)


@app.route('/loan_details')
def loan_details():
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        return render_template('templates/loan_details.html', loan_amount=user.loan_amount, 
            loan_term_months=user.loan_term_months, monthly_payment=user.monthly_payment)
    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))


@app.route('/total_loan_payments')
def total_loan_payments():
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        # Get payment and term from query parameters
        principal = request.args.get('principal', type=float)
        payment = request.args.get('payment', type=float)
        term = request.args.get('term', type=int)

        # Check if parameters are provided
        if principal is None or payment is None or term is None:
            return Response('Missing principal, payment or term parameters', status=400)

        # Fixed: No longer using render_template_string with user input
        # Instead, safely construct the JSON response
        import json
        response_data = {
            "loan_principal": str(principal),
            "monthly_payment": str(payment),
            "loan_term_amount": str(term),
            "total_loan_payments": str(payment * term)
        }
        
        return Response(json.dumps(response_data), content_type='application/json')

    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))
