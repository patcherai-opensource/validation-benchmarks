from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response
from jinja2 import Environment, FileSystemLoader, select_autoescape
from werkzeug.utils import secure_filename

from app import app
from app.db import db
from app.models import User

import os

UPLOAD_FOLDER = '/var/www/ssti_include_loan_calculator/app/static/invoice_templates/'
ALLOWED_EXTENSIONS = {'html', 'jinja2'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

@app.errorhandler(404)
def page_not_found(e):
    return render_template('templates/404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('templates/500.html'), 500


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
            return render_template('templates/login.html', error='Invalid username or password')
    return render_template('templates/login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))


@app.route('/home')
def home():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        return render_template('templates/home.html', user=user)
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
            return render_template('templates/profile.html', user=user)
    else:
        return redirect(url_for('login'))


@app.route('/update_profile', methods=['GET', 'POST'])
def update_profile():
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

            if 'image_profile' in request.files:
                image_profile = request.files['image_profile']
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
        return redirect(url_for('login'))


@app.route('/loan_details')
def loan_details():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        return render_template('templates/loan_details.html', loan_amount=user.loan_amount, 
            loan_term_months=user.loan_term_months, monthly_payment=user.monthly_payment)
    else:
        return redirect(url_for('login'))


@app.route('/total_loan_payments')
def total_loan_payments():
    user_id = session.get('user_id')
    if user_id:
        principal = request.args.get('principal', type=float)
        payment = request.args.get('payment', type=float)
        term = request.args.get('term', type=int)

        if principal is None or payment is None or term is None:
            return Response('Missing principal, payment or term parameters', status=400)

        import json
        result = {
            "loan_principal": str(principal),
            "monthly_payment": str(payment),
            "loan_term_amount": str(term),
            "total_loan_payments": str(payment * term)
        }
        return Response(json.dumps(result), mimetype='application/json')
    else:
        return redirect(url_for('login'))


@app.route('/invoice_templates')
def invoice_templates():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        templates = []
        if os.path.exists(UPLOAD_FOLDER):
            templates = [f for f in os.listdir(UPLOAD_FOLDER) if allowed_file(f)]
        return render_template('templates/invoice_templates.html', user=user, templates=templates)
    else:
        return redirect(url_for('login'))


@app.route('/upload_invoice_template', methods=['POST'])
def upload_invoice_template():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    if 'template_file' not in request.files:
        return redirect(url_for('invoice_templates'))
    
    file = request.files['template_file']
    
    if file.filename == '':
        return redirect(url_for('invoice_templates'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        return redirect(url_for('invoice_templates'))
    
    return Response('Invalid file type. Only .html and .jinja2 files are allowed.', status=400)


@app.route('/generate_invoice')
def generate_invoice():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    user = User.query.get(user_id)
    template_name = request.args.get('template', 'default_invoice.html')
    
    template_path = os.path.join(UPLOAD_FOLDER, template_name)
    
    if not os.path.exists(template_path):
        return Response('Template not found.', status=404)
    
    safe_dir = os.path.realpath(UPLOAD_FOLDER)
    final_path = os.path.realpath(template_path)
    
    if not final_path.startswith(safe_dir):
        return Response('Invalid template path.', status=400)
    
    with open(template_path, 'r') as f:
        template_content = f.read()
    
    env = Environment(
        loader=FileSystemLoader(UPLOAD_FOLDER),
        autoescape=select_autoescape(['html', 'xml'])
    )
    
    template = env.from_string(template_content)
    
    invoice_data = {
        'user': user,
        'loan_amount': user.loan_amount,
        'loan_term_months': user.loan_term_months,
        'monthly_payment': user.monthly_payment,
        'total_payment': user.monthly_payment * user.loan_term_months,
        'invoice_number': f'INV-{user.id:05d}',
    }
    
    rendered = template.render(**invoice_data)
    
    return Response(rendered, mimetype='text/html')
