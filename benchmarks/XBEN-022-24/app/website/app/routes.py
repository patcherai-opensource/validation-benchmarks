from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response, send_file
from werkzeug.utils import secure_filename
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from app import app
from app.db import db
from app.models import User

import os
import io

@app.after_request
def add_header(request):
    request.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    request.headers['Pragma'] = 'no-cache'
    request.headers['Expires'] = '0'
    request.headers['Cache-Control'] = 'public, max-age=0'
    return request



# Directory for user-uploaded templates
UPLOAD_TEMPLATE_DIR = '/var/www/kimai_tracker/uploads/templates/'

# Allowed extensions for template uploads
ALLOWED_TEMPLATE_EXTENSIONS = {'j2', 'jinja2', 'twig', 'html'}

def allowed_template_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_TEMPLATE_EXTENSIONS


@app.route('/robots.txt')
def robots():
    return send_file('/var/www/kimai_tracker/app/static/robots.txt', mimetype='text/plain')


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

                    safe_dir = '/var/www/kimai_tracker/app/static/images/'
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


@app.route('/error')
def error():
    error_message = request.args.get('message', 'An error occurred.')
    error_type = 'templates/' + request.args.get('error_type', None)

    safe_dir = '/var/www/kimai_tracker/app/static/'
    final_path = os.path.realpath(os.path.join(safe_dir, error_type))

    if os.path.commonprefix((final_path, safe_dir)) != safe_dir: 
        return Response('Trying to load a template located outside the static directory.', status=400)

    return render_template('templates/error.html', error_message=error_message, error_type=final_path[len(safe_dir):])


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


@app.route('/api/timesheet/calculate')
def timesheet_calculate():
    """API endpoint to calculate timesheet totals"""
    user_id = session.get('user_id')
    if user_id:
        # Get parameters
        hours = request.args.get('hours', type=float, default=0)
        rate = request.args.get('rate', type=float, default=0)
        
        result = {
            "hours_worked": hours,
            "hourly_rate": rate,
            "total_amount": hours * rate,
            "status": "calculated"
        }
        return Response(str(result).replace("'", '"'), content_type='application/json')
    else:
        return redirect(url_for('login'))


@app.route('/invoice/templates', methods=['GET'])
def list_invoice_templates():
    """List uploaded invoice templates"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    user = User.query.get(user_id)
    user_template_dir = os.path.join(UPLOAD_TEMPLATE_DIR, str(user_id))
    
    templates = []
    if os.path.exists(user_template_dir):
        for f in os.listdir(user_template_dir):
            if allowed_template_file(f):
                templates.append(f)
    
    return render_template('templates/invoice_templates.html', templates=templates, user=user)


@app.route('/invoice/upload', methods=['GET', 'POST'])
def upload_invoice_template():
    """Upload custom invoice template"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    user = User.query.get(user_id)
    
    if request.method == 'POST':
        if 'template_file' not in request.files:
            return render_template('templates/upload_template.html', user=user, 
                                 error='No file selected')
        
        file = request.files['template_file']
        
        if file.filename == '':
            return render_template('templates/upload_template.html', user=user,
                                 error='No file selected')
        
        if file and allowed_template_file(file.filename):
            filename = secure_filename(file.filename)
            
            # Create user-specific template directory
            user_template_dir = os.path.join(UPLOAD_TEMPLATE_DIR, str(user_id))
            os.makedirs(user_template_dir, exist_ok=True)
            
            filepath = os.path.join(user_template_dir, filename)
            file.save(filepath)
            
            return redirect(url_for('list_invoice_templates'))
        else:
            return render_template('templates/upload_template.html', user=user,
                                 error='Invalid file type. Allowed: .j2, .jinja2, .twig, .html')
    
    return render_template('templates/upload_template.html', user=user)


@app.route('/invoice/render/<template_name>')
def render_invoice(template_name):
    """Render an invoice using a user-uploaded template"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    user = User.query.get(user_id)
    
    # Load user's template directory
    user_template_dir = os.path.join(UPLOAD_TEMPLATE_DIR, str(user_id))
    
    if not os.path.exists(user_template_dir):
        return Response('No templates uploaded', status=404)
    
    template_path = os.path.join(user_template_dir, secure_filename(template_name))
    
    if not os.path.exists(template_path):
        return Response('Template not found', status=404)
    
    try:
        with open(template_path, 'r') as f:
            template_content = f.read()
        
        # Prepare invoice context data
        invoice_data = {
            'user': user,
            'invoice_number': f'INV-{user_id}-001',
            'company_name': 'Time Tracker Inc.',
            'hours_logged': 40.0,
            'hourly_rate': user.monthly_payment / 160.0 if user.monthly_payment else 25.0,
            'total_amount': user.monthly_payment if user.monthly_payment else 4000.0,
            'date': '2024-01-15'
        }
        
        rendered = render_template_string(template_content, **invoice_data)
        return Response(rendered, content_type='text/html')
        
    except Exception as e:
        return Response(f'Error rendering template: {str(e)}', status=500)


@app.route('/invoice/download/<template_name>')
def download_invoice(template_name):
    """Download rendered invoice as HTML file"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    user = User.query.get(user_id)
    user_template_dir = os.path.join(UPLOAD_TEMPLATE_DIR, str(user_id))
    
    if not os.path.exists(user_template_dir):
        return Response('No templates uploaded', status=404)
    
    template_path = os.path.join(user_template_dir, secure_filename(template_name))
    
    if not os.path.exists(template_path):
        return Response('Template not found', status=404)
    
    try:
        with open(template_path, 'r') as f:
            template_content = f.read()
        
        invoice_data = {
            'user': user,
            'invoice_number': f'INV-{user_id}-001',
            'company_name': 'Time Tracker Inc.',
            'hours_logged': 40.0,
            'hourly_rate': user.monthly_payment / 160.0 if user.monthly_payment else 25.0,
            'total_amount': user.monthly_payment if user.monthly_payment else 4000.0,
            'date': '2024-01-15'
        }
        
        rendered = render_template_string(template_content, **invoice_data)
        
        # Return as downloadable file
        return Response(
            rendered,
            mimetype='text/html',
            headers={'Content-Disposition': f'attachment; filename=invoice_{template_name}.html'}
        )
        
    except Exception as e:
        return Response(f'Error: {str(e)}', status=500)


@app.route('/api/projects')
def api_projects():
    """API endpoint to list projects (noise endpoint)"""
    user_id = session.get('user_id')
    if not user_id:
        return Response('{"error": "unauthorized"}', status=401, content_type='application/json')
    
    projects = [
        {"id": 1, "name": "Website Redesign", "status": "active"},
        {"id": 2, "name": "Mobile App", "status": "completed"},
        {"id": 3, "name": "API Integration", "status": "active"}
    ]
    return Response(str(projects).replace("'", '"'), content_type='application/json')


@app.route('/api/activities')
def api_activities():
    """API endpoint to list activities (noise endpoint)"""
    user_id = session.get('user_id')
    if not user_id:
        return Response('{"error": "unauthorized"}', status=401, content_type='application/json')
    
    activities = [
        {"id": 1, "name": "Development", "billable": True},
        {"id": 2, "name": "Meeting", "billable": False},
        {"id": 3, "name": "Testing", "billable": True}
    ]
    return Response(str(activities).replace("'", '"'), content_type='application/json')


@app.route('/settings')
def settings():
    """Settings page (noise endpoint)"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    user = User.query.get(user_id)
    return render_template('templates/settings.html', user=user)
