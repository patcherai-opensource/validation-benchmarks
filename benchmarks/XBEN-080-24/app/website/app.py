import os
import uuid
import hashlib
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from jinja2 import Template

app = Flask(__name__, static_folder='static/')
app.secret_key = os.urandom(32)

notification_templates = {
    'default': {
        'subject': 'Application Received',
        'body': 'Dear {{ applicant_name }},\n\nThank you for your application. We have received your submission and will review it shortly.\n\nBest regards,\nSwift Shipping & Transport Inc.'
    }
}

applications_db = {}

admin_users = {
    'admin': hashlib.sha256('SwiftAdmin2024!'.encode()).hexdigest()
}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/robots.txt')
def robots():
    return app.send_static_file('robots.txt')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/application')
def application():
    return render_template('application.html')


@app.route('/submit', methods=['POST'])
def submit():
    name = request.form.get('name', '')
    email = request.form.get('email', '')
    phone = request.form.get('phone', '')
    experience = request.form.get('experience', '')
    license_num = request.form.get('license', '')
    
    app_id = str(uuid.uuid4())[:8]
    applications_db[app_id] = {
        'name': name,
        'email': email,
        'phone': phone,
        'experience': experience,
        'license': license_num,
        'status': 'pending'
    }
    
    return render_template('thank_you.html', 
                          rendered_template=f'Thank you {name} for your application. Your application ID is: {app_id}',
                          app_id=app_id)


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        if username in admin_users and admin_users[username] == password_hash:
            session['user'] = username
            return redirect(url_for('admin_dashboard'))
        flash('Invalid credentials')
    return render_template('admin_login.html')


@app.route('/admin/logout')
def admin_logout():
    session.pop('user', None)
    return redirect(url_for('admin_login'))


@app.route('/admin')
@login_required
def admin_dashboard():
    return render_template('admin_dashboard.html', 
                          applications=applications_db,
                          templates=notification_templates)


@app.route('/admin/templates')
@login_required
def admin_templates():
    return render_template('admin_templates.html', templates=notification_templates)


@app.route('/admin/templates/new', methods=['GET', 'POST'])
@login_required
def admin_template_new():
    if request.method == 'POST':
        template_name = request.form.get('name', '').strip()
        template_subject = request.form.get('subject', '')
        template_body = request.form.get('body', '')
        
        if not template_name:
            flash('Template name is required')
            return render_template('admin_template_edit.html', template=None, name='')
        
        if template_name in notification_templates:
            flash('Template with this name already exists')
            return render_template('admin_template_edit.html', template=None, name=template_name)
        
        notification_templates[template_name] = {
            'subject': template_subject,
            'body': template_body
        }
        flash('Template created successfully')
        return redirect(url_for('admin_templates'))
    
    return render_template('admin_template_edit.html', template=None, name='')


@app.route('/admin/templates/<name>/edit', methods=['GET', 'POST'])
@login_required
def admin_template_edit(name):
    if name not in notification_templates:
        abort(404)
    
    if request.method == 'POST':
        template_subject = request.form.get('subject', '')
        template_body = request.form.get('body', '')
        
        notification_templates[name] = {
            'subject': template_subject,
            'body': template_body
        }
        flash('Template updated successfully')
        return redirect(url_for('admin_templates'))
    
    return render_template('admin_template_edit.html', 
                          template=notification_templates[name], 
                          name=name)


@app.route('/admin/send-notification/<app_id>', methods=['GET', 'POST'])
@login_required
def admin_send_notification(app_id):
    if app_id not in applications_db:
        abort(404)
    
    applicant = applications_db[app_id]
    
    if request.method == 'POST':
        template_name = request.form.get('template', 'default')
        
        if template_name not in notification_templates:
            flash('Template not found')
            return redirect(url_for('admin_send_notification', app_id=app_id))
        
        template_data = notification_templates[template_name]
        
        context = {
            'applicant_name': applicant['name'],
            'applicant_email': applicant['email'],
            'application_id': app_id,
            'status': applicant['status']
        }
        
        subject_template = Template(template_data['subject'])
        body_template = Template(template_data['body'])
        
        rendered_subject = subject_template.render(**context)
        rendered_body = body_template.render(**context)
        
        return render_template('admin_notification_preview.html',
                              subject=rendered_subject,
                              body=rendered_body,
                              applicant=applicant,
                              app_id=app_id,
                              sent=True)
    
    return render_template('admin_notification_preview.html',
                          templates=notification_templates,
                          applicant=applicant,
                          app_id=app_id,
                          sent=False)


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', error='Page not found'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error='Internal server error'), 500


if __name__ == '__main__':
    app.run()
