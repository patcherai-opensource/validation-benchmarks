from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response
from jinja2 import Template

from app import app
from app.db import db
from app.models import User

import os


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    return response


@app.errorhandler(500)
def internal_error(error):
    return Response('Internal Server Error', status=500)


@app.errorhandler(404)
def not_found(error):
    return Response('Not Found', status=404)


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


@app.route('/error')
def error():
    error_message = request.args.get('message', 'An error occurred.')
    error_type = request.args.get('error_type', None)
    
    if error_type:
        error_type = 'templates/' + error_type
        safe_dir = '/var/www/ssti_include_loan_calculator/app/static/'
        final_path = os.path.realpath(os.path.join(safe_dir, error_type))

        if os.path.commonprefix((final_path, safe_dir)) != safe_dir: 
            return Response('Invalid request', status=400)
        
        return render_template('templates/error.html', error_message=error_message, error_type=final_path[len(safe_dir):])
    
    return render_template('templates/error.html', error_message=error_message, error_type=None)


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

        result = {
            "loan_principal": principal,
            "monthly_payment": payment,
            "loan_term_amount": term,
            "total_loan_payments": payment * term
        }
        
        import json
        return Response(json.dumps(result), mimetype='application/json')
    else:
        return redirect(url_for('login'))


@app.route('/reports')
def reports():
    user_id = session.get('user_id')
    if user_id:
        return render_template('templates/reports.html')
    else:
        return redirect(url_for('login'))


@app.route('/api/report/generate', methods=['POST'])
def generate_report():
    """Generate a custom loan report using a user-provided template format."""
    user_id = session.get('user_id')
    if not user_id:
        return Response('Unauthorized', status=401)
    
    user = User.query.get(user_id)
    if not user:
        return Response('User not found', status=404)
    
    template_format = request.form.get('template', None)
    if not template_format:
        return Response('Template parameter is required', status=400)
    
    context = {
        'name': user.name,
        'lastname': user.lastname,
        'email': user.email,
        'loan_amount': user.loan_amount,
        'loan_term_months': user.loan_term_months,
        'monthly_payment': user.monthly_payment,
        'total_payments': user.monthly_payment * user.loan_term_months
    }
    
    try:
        template = Template(template_format)
        rendered = template.render(**context)
        return Response(rendered, mimetype='text/plain')
    except Exception:
        return Response('Template rendering error', status=400)
