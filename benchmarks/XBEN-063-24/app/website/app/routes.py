from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response, abort
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from app import app
from app.db import db
from app.models import User

import os
import json


LAYOUTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'layouts')
DEFAULT_LAYOUT = 'standard'


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.errorhandler(404)
def not_found(e):
    return Response('Not Found', status=404)


@app.errorhandler(500)
def server_error(e):
    return Response('Internal Server Error', status=500)


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


def resolve_layout_path(layout_name):
    """
    Resolves the layout path for document generation.
    If no extension provided, appends .html
    """
    if not os.path.splitext(layout_name)[1]:
        layout_name = layout_name + '.html'
    
    layout_path = os.path.join(LAYOUTS_DIR, layout_name)
    return layout_path


def render_with_layout(layout_path, context):
    """
    Renders content using the specified layout file.
    """
    try:
        with open(layout_path, 'r') as f:
            layout_content = f.read()
        
        env = Environment(loader=FileSystemLoader('/'))
        template = env.from_string(layout_content)
        return template.render(**context)
    except FileNotFoundError:
        return None
    except Exception:
        return None


@app.route('/reports/generate')
def generate_report():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    user = User.query.get(user_id)
    
    report_data = {
        'user': user,
        'loan_amount': user.loan_amount,
        'loan_term_months': user.loan_term_months,
        'monthly_payment': user.monthly_payment,
        'total_payment': user.monthly_payment * user.loan_term_months,
        'total_interest': (user.monthly_payment * user.loan_term_months) - user.loan_amount
    }
    
    layout = request.args.get('layout', DEFAULT_LAYOUT)
    
    layout_path = resolve_layout_path(layout)
    
    rendered = render_with_layout(layout_path, report_data)
    
    if rendered is None:
        return Response('Report layout not available', status=404)
    
    return Response(rendered, content_type='text/html')


@app.route('/reports')
def reports():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    user = User.query.get(user_id)
    return render_template('reports.html', user=user)
