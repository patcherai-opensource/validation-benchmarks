from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response, jsonify
import yaml
import re
import os

from app import app
from app.db import db
from app.models import User


# =============================================================================
# Template Engine Simulation (CVE-2021-3583 inspired vulnerability)
# 
# This simulates Ansible's templating engine behavior where:
# 1. Variables can be marked as "unsafe" using !unsafe YAML tag
# 2. Unsafe variables should NOT be template-rendered
# 3. BUG: Multi-line strings with trailing newlines lose their unsafe marking
# =============================================================================

class UnsafeValue(str):
    """Wrapper class to mark a value as unsafe (should not be templated)"""
    __slots__ = ()


class SafeValue(str):
    """Wrapper class to mark a value as safe (can be templated)"""
    __slots__ = ()


def wrap_var(value):
    """Wrap a variable to mark it as unsafe"""
    return UnsafeValue(value)


def is_unsafe(value):
    """Check if a value is marked as unsafe"""
    return isinstance(value, UnsafeValue)


def do_template(data, preserve_trailing_newlines=False):
    """
    Template rendering function that simulates Ansible's do_template behavior.
    
    CVE-2021-3583 vulnerability: When preserve_trailing_newlines is True and
    the string ends with newlines, the unsafe marking is lost during the
    newline preservation logic.
    """
    if data is None:
        return data
    
    # Check if the data is marked as unsafe
    data_is_unsafe = is_unsafe(data)
    
    # Store original string for newline handling
    result = str(data)
    
    # If the data is unsafe, don't template it (return as-is)
    if data_is_unsafe:
        # BUG: When preserving trailing newlines, we fail to re-wrap the result
        # as unsafe after string manipulation, similar to CVE-2021-3583
        if preserve_trailing_newlines and result.endswith('\n'):
            # Extract trailing newlines
            trailing_newlines = len(result) - len(result.rstrip('\n'))
            stripped_result = result.rstrip('\n')
            # Re-add trailing newlines
            result = stripped_result + ('\n' * trailing_newlines)
            # BUG: We should wrap_var(result) here but we don't!
            # This causes the unsafe marking to be lost
            return result  # Returns regular str, not UnsafeValue!
        return wrap_var(result)
    
    # For safe values, perform Jinja2 template rendering
    try:
        rendered = render_template_string(result)
        return rendered
    except Exception:
        return result


def parse_yaml_with_unsafe(yaml_content):
    """
    Parse YAML content with support for !unsafe tag.
    Variables marked with !unsafe should not be template-rendered.
    """
    
    # Custom YAML constructor for !unsafe tag
    def unsafe_constructor(loader, node):
        value = loader.construct_scalar(node)
        return wrap_var(value)
    
    # Add the custom constructor
    yaml.add_constructor('!unsafe', unsafe_constructor, Loader=yaml.SafeLoader)
    
    try:
        # Parse the YAML
        parsed = yaml.safe_load(yaml_content)
        return parsed
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML: {e}")


def process_config_variables(config_dict, preserve_trailing_newlines=False):
    """
    Process configuration variables, rendering templates for safe values.
    This simulates Ansible's variable processing with two-pass rendering.
    
    CVE-2021-3583: In Ansible, variables go through multiple processing stages.
    The bug is that after the first pass through do_template(), if the unsafe
    marking is lost (due to the newline bug), the second pass will treat the
    value as safe and actually render the Jinja2 template.
    """
    result = {}
    for key, value in config_dict.items():
        if isinstance(value, str):
            # First pass: Process through do_template
            first_pass = do_template(value, preserve_trailing_newlines=preserve_trailing_newlines)
            
            # Second pass: If the value lost its unsafe marking, it gets re-templated!
            # This is the core of CVE-2021-3583 - the unsafe context is lost
            if not is_unsafe(first_pass) and isinstance(first_pass, str):
                # Value is no longer marked unsafe, so it gets templated
                try:
                    result[key] = render_template_string(first_pass)
                except Exception:
                    result[key] = first_pass
            else:
                result[key] = first_pass
        elif isinstance(value, dict):
            result[key] = process_config_variables(value, preserve_trailing_newlines)
        else:
            result[key] = value
    return result


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


# =============================================================================
# Configuration API - Simulates Ansible-like variable/fact processing
# =============================================================================

@app.route('/api/config/process', methods=['POST'])
def process_config():
    """
    Process configuration/playbook variables via YAML input.
    
    This endpoint simulates Ansible's configuration processing where:
    - Variables can be marked as !unsafe to prevent template rendering
    - The templating engine renders Jinja2 expressions in safe values
    
    Query Parameters:
    - preserve_newlines: If 'true', preserve trailing newlines in multi-line strings
                        (This triggers the CVE-2021-3583 vulnerability!)
    
    Example YAML input:
    ---
    greeting: "Hello {{ 'World' }}"
    safe_command: !unsafe "{{ lookup('pipe', 'whoami') }}"
    
    The safe_command should NOT be rendered since it's marked !unsafe,
    but with preserve_newlines=true and trailing newlines, it WILL be rendered!
    """
    
    content_type = request.content_type or ''
    
    if 'yaml' not in content_type.lower() and 'text/plain' not in content_type.lower():
        return Response(
            'Content-Type must be application/x-yaml or text/plain', 
            status=400
        )
    
    yaml_content = request.get_data(as_text=True)
    
    if not yaml_content:
        return Response('Empty request body', status=400)
    
    # Check for preserve_newlines parameter (triggers the vulnerability)
    preserve_newlines = request.args.get('preserve_newlines', 'false').lower() == 'true'
    
    try:
        # Parse YAML with !unsafe tag support
        config = parse_yaml_with_unsafe(yaml_content)
        
        if not isinstance(config, dict):
            return Response('YAML must be a dictionary/mapping', status=400)
        
        # Process variables through the vulnerable templating engine
        processed = process_config_variables(config, preserve_trailing_newlines=preserve_newlines)
        
        # Convert results to strings for JSON response
        output = {}
        for key, value in processed.items():
            if isinstance(value, str):
                output[key] = value
            elif isinstance(value, dict):
                output[key] = {k: str(v) if isinstance(v, str) else v for k, v in value.items()}
            else:
                output[key] = value
        
        return jsonify({
            'status': 'success',
            'processed_config': output,
            'preserve_newlines': preserve_newlines
        })
        
    except ValueError as e:
        return Response(str(e), status=400)
    except Exception as e:
        return Response(f'Processing error: {str(e)}', status=500)


@app.route('/api/config/validate', methods=['POST'])
def validate_config():
    """
    Validate and preview configuration processing.
    Shows what values are marked as unsafe vs safe.
    """
    
    content_type = request.content_type or ''
    
    if 'yaml' not in content_type.lower() and 'text/plain' not in content_type.lower():
        return Response(
            'Content-Type must be application/x-yaml or text/plain', 
            status=400
        )
    
    yaml_content = request.get_data(as_text=True)
    
    if not yaml_content:
        return Response('Empty request body', status=400)
    
    try:
        config = parse_yaml_with_unsafe(yaml_content)
        
        if not isinstance(config, dict):
            return Response('YAML must be a dictionary/mapping', status=400)
        
        # Show which values are unsafe
        analysis = {}
        for key, value in config.items():
            if isinstance(value, str):
                analysis[key] = {
                    'value': str(value),
                    'is_unsafe': is_unsafe(value),
                    'has_trailing_newline': value.endswith('\n'),
                    'type': 'UnsafeValue' if is_unsafe(value) else 'SafeValue'
                }
            else:
                analysis[key] = {
                    'value': str(value),
                    'type': type(value).__name__
                }
        
        return jsonify({
            'status': 'valid',
            'analysis': analysis
        })
        
    except ValueError as e:
        return jsonify({'status': 'invalid', 'error': str(e)})
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)})


@app.route('/api/config/help')
def config_help():
    """API documentation for the configuration processor"""
    return jsonify({
        'endpoints': {
            '/api/config/process': {
                'method': 'POST',
                'content_type': 'application/x-yaml or text/plain',
                'description': 'Process YAML configuration with Jinja2 templating',
                'parameters': {
                    'preserve_newlines': 'If true, preserve trailing newlines in multi-line strings'
                },
                'example': '''---
greeting: "Hello {{ 'World' }}"
safe_command: !unsafe "{{ dangerous_code }}"
'''
            },
            '/api/config/validate': {
                'method': 'POST',
                'content_type': 'application/x-yaml or text/plain',
                'description': 'Validate YAML and show which values are marked as unsafe'
            }
        },
        'notes': [
            'Use !unsafe YAML tag to mark values that should NOT be template-rendered',
            'Jinja2 expressions in safe values will be evaluated',
            'Multi-line strings are supported with YAML block scalars'
        ]
    })


# Legacy endpoints (kept for backward compatibility)

@app.route('/total_loan_payments')
def total_loan_payments():
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        # Get payment and term from query parameters
        principal = request.args.get('principal', type=str)
        payment = request.args.get('payment', type=float)
        term = request.args.get('term', type=int)

        # Check if parameters are provided
        if principal is None or payment is None or term is None:
            return Response('Missing principal, payment or term parameters', status=400)

        # JSON template - sanitized version
        json_template = """
        { "loan_principal": "{{ principal }}","monthly_payment": "{{ payment }}", "loan_term_amount": "{{ term }}", "total_loan_payments": "{{ payment*term }}" }
        """

        # Render JSON template (sanitized - no longer directly injectable)
        return render_template_string(json_template, principal=str(principal), payment=payment, term=term, content_type='application/json')

    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))


@app.route('/amortization')
def amortization():
    # Assume you have some data for amortization table rows
    term = request.args.get('term', type=str)
    
    if term is None:
        return Response('Missing term parameter', status=400)

    # Sanitized - only allow numeric values
    try:
        term_int = int(term)
        if term_int < 1 or term_int > 360:
            return Response('Term must be between 1 and 360', status=400)
    except ValueError:
        return Response('Term must be a number', status=400)

    # HTML template - now safe
    table_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Amortization Table</title>
    <i>This feature is not yet fully implemented.</i>
    <style>
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th, td {
            border: 1px solid black;
            padding: 8px;
            text-align: center;
        }
    </style>
</head>
<body>
    <h2>Amortization Table</h2>
    <table id="paymentTable">
        <thead>
            <tr>
                <th>Payment Number</th>
                <th>Principal</th>
                <th>Interest</th>
            </tr>
        </thead>
        <tbody>
            {% for row in range(term) %}
                <tr>
                    <td>{{ row+1 }}</td>
                    <td>N/A</td>
                    <td>N/A</td>
                </tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>
    """

    # Render the amortization table template with the provided data
    return render_template_string(table_template, term=term_int)
