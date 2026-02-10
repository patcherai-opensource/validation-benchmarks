from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response

from app import app
from app.db import db
from app.models import User

import json
import re
import yaml
import subprocess
import os


@app.after_request
def add_header(request):
    request.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    request.headers['Pragma'] = 'no-cache'
    request.headers['Expires'] = '0'
    request.headers['Cache-Control'] = 'public, max-age=0'
    return request


# Ansible-like template engine simulation
# This simulates CVE-2021-3583 where multi-line YAML strings lose their "unsafe" marker
class AnsibleTemplateEngine:
    """
    Simulates Ansible's templating engine with the vulnerability from CVE-2021-3583.
    The vulnerability occurs when multi-line strings with trailing newlines are not
    properly marked as 'unsafe', allowing template expressions to be re-evaluated.
    """
    
    def __init__(self):
        self.unsafe_vars = set()
    
    def mark_unsafe(self, var_name):
        """Mark a variable as unsafe (should not be template-rendered)"""
        self.unsafe_vars.add(var_name)
    
    def is_unsafe(self, var_name):
        """Check if a variable is marked unsafe"""
        return var_name in self.unsafe_vars
    
    def wrap_var(self, value, var_name):
        """Wrap variable with unsafe marker - this is where the bug exists"""
        # BUG: If value contains trailing newlines, we fail to preserve the unsafe marker
        # This simulates the CVE-2021-3583 vulnerability
        if isinstance(value, str) and value.endswith('\n'):
            # Vulnerability: lose the unsafe marker for multi-line strings
            return value
        return value
    
    def do_template(self, data, variables):
        """
        Process template data - simulates Ansible's do_template function.
        This is the vulnerable function where template injection can occur.
        """
        result = data
        
        # Process variables in the template
        for var_name, var_value in variables.items():
            placeholder = "{{ " + var_name + " }}"
            if placeholder in result:
                # Check if this variable should be treated as unsafe
                if self.is_unsafe(var_name):
                    processed_value = self.wrap_var(str(var_value), var_name)
                else:
                    processed_value = str(var_value)
                result = result.replace(placeholder, processed_value)
        
        # Second pass: evaluate any remaining template expressions
        # This is where the vulnerability manifests - expressions in user data get evaluated
        result = self._evaluate_expressions(result)
        
        return result
    
    def _evaluate_expressions(self, template_str):
        """
        Evaluate template expressions like {{ lookup('pipe', 'cmd') }}.
        This simulates Ansible's template expression evaluation.
        """
        # Find and process lookup expressions (Ansible-style)
        lookup_pattern = r"\{\{\s*lookup\s*\(\s*['\"]pipe['\"]\s*,\s*['\"]([^'\"]+)['\"]\s*\)\s*\}\}"
        
        def evaluate_lookup(match):
            command = match.group(1)
            try:
                # Execute the command - this is the RCE vulnerability
                result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
                return result.decode('utf-8').strip()
            except subprocess.CalledProcessError as e:
                return f"Error: {e.output.decode('utf-8')}"
            except Exception as e:
                return f"Error: {str(e)}"
        
        result = re.sub(lookup_pattern, evaluate_lookup, template_str)
        
        # Also support simple variable expressions that might contain executable content
        # Pattern for {{ variable }} style expressions
        expr_pattern = r"\{\{\s*([^}]+)\s*\}\}"
        
        def evaluate_expr(match):
            expr = match.group(1).strip()
            # If it looks like a lookup call, it was already processed
            if 'lookup' in expr:
                return match.group(0)
            # For other expressions, just return as-is (safe behavior)
            return match.group(0)
        
        return result


# Global template engine instance
ansible_engine = AnsibleTemplateEngine()


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


@app.route('/total_loan_payments')
def total_loan_payments():
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        # Get payment and term from query parameters
        principal = request.args.get('principal', type=str)
        if principal:
            principal = principal.strip()
        payment = request.args.get('payment', type=float)
        term = request.args.get('term', type=int)

        # Check if parameters are provided
        if principal is None or payment is None or term is None:
            return Response('Missing principal, payment or term parameters', status=400)

        # JSON response
        json_response = {
            "loan_principal": principal,
            "monthly_payment": payment,
            "loan_term_amount": term,
            "total_loan_payments": payment * term
        }

        return Response(json.dumps(json_response), mimetype='application/json')
    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))


@app.route('/api/template/render', methods=['POST'])
def render_playbook_template():
    """
    Ansible-like template rendering API endpoint.
    
    This simulates an Ansible controller's template rendering functionality.
    The vulnerability (CVE-2021-3583) occurs when user-supplied variables
    containing template expressions are processed without proper 'unsafe' marking,
    especially for multi-line strings with trailing newlines.
    
    Expected JSON input:
    {
        "template": "Hello {{ name }}!",
        "variables": {
            "name": "World"
        },
        "unsafe_vars": ["name"]  // Optional: variables that should be marked unsafe
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return Response(json.dumps({"error": "No JSON data provided"}), 
                          status=400, mimetype='application/json')
        
        template = data.get('template', '')
        variables = data.get('variables', {})
        unsafe_vars = data.get('unsafe_vars', [])
        
        if not template:
            return Response(json.dumps({"error": "Template is required"}),
                          status=400, mimetype='application/json')
        
        # Create a fresh template engine for this request
        engine = AnsibleTemplateEngine()
        
        # Mark specified variables as unsafe
        for var_name in unsafe_vars:
            engine.mark_unsafe(var_name)
        
        # Process the template - this is where the vulnerability lies
        # Variables with trailing newlines will lose their unsafe status
        result = engine.do_template(template, variables)
        
        return Response(json.dumps({
            "status": "success",
            "rendered": result
        }), mimetype='application/json')
        
    except Exception as e:
        return Response(json.dumps({"error": str(e)}),
                      status=500, mimetype='application/json')


@app.route('/api/playbook/preview', methods=['POST'])
def preview_playbook():
    """
    Preview endpoint for Ansible playbook configuration.
    
    Accepts YAML-formatted playbook data with variables and renders it.
    This endpoint is vulnerable to CVE-2021-3583 style template injection
    when user-supplied facts/variables contain template expressions.
    
    Expected input format (application/x-yaml or application/json):
    
    YAML format:
    ---
    name: Test Playbook
    vars:
      user_input: "{{ lookup('pipe', 'whoami') }}"
    tasks:
      - name: Display message
        debug:
          msg: "User: {{ user_input }}"
    
    JSON format:
    {
        "name": "Test Playbook",
        "vars": {
            "user_input": "{{ lookup('pipe', 'whoami') }}"
        },
        "tasks": [...]
    }
    """
    try:
        content_type = request.content_type or ''
        
        if 'yaml' in content_type or 'text/plain' in content_type:
            # Parse YAML input
            playbook_data = yaml.safe_load(request.data.decode('utf-8'))
        else:
            # Default to JSON
            playbook_data = request.get_json()
        
        if not playbook_data:
            return Response(json.dumps({"error": "No playbook data provided"}),
                          status=400, mimetype='application/json')
        
        playbook_name = playbook_data.get('name', 'Unnamed Playbook')
        vars_dict = playbook_data.get('vars', {})
        tasks = playbook_data.get('tasks', [])
        
        # Create template engine
        engine = AnsibleTemplateEngine()
        
        # Process variables - this is the vulnerable code path
        # Multi-line variables with trailing newlines won't be properly marked unsafe
        processed_vars = {}
        for var_name, var_value in vars_dict.items():
            if isinstance(var_value, str):
                # The vulnerability: if the value has trailing newlines,
                # the unsafe marker is lost and template expressions get evaluated
                processed_value = engine._evaluate_expressions(var_value)
                processed_vars[var_name] = processed_value
            else:
                processed_vars[var_name] = var_value
        
        # Process tasks with the variables
        processed_tasks = []
        for task in tasks:
            task_str = json.dumps(task)
            processed_task_str = engine.do_template(task_str, processed_vars)
            try:
                processed_task = json.loads(processed_task_str)
            except json.JSONDecodeError:
                processed_task = {"raw": processed_task_str}
            processed_tasks.append(processed_task)
        
        result = {
            "status": "preview",
            "playbook_name": playbook_name,
            "processed_vars": processed_vars,
            "tasks": processed_tasks
        }
        
        return Response(json.dumps(result, indent=2), mimetype='application/json')
        
    except yaml.YAMLError as e:
        return Response(json.dumps({"error": f"YAML parse error: {str(e)}"}),
                      status=400, mimetype='application/json')
    except Exception as e:
        return Response(json.dumps({"error": str(e)}),
                      status=500, mimetype='application/json')


@app.route('/api/inventory/validate', methods=['POST'])
def validate_inventory():
    """
    Validate and process Ansible inventory data.
    
    This endpoint processes inventory data containing host variables.
    Vulnerable to template injection via CVE-2021-3583 mechanism when
    host facts contain template expressions.
    
    Expected JSON input:
    {
        "hosts": {
            "webserver1": {
                "ansible_host": "192.168.1.10",
                "custom_fact": "{{ lookup('pipe', 'cat /flag') }}"
            }
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return Response(json.dumps({"error": "No inventory data provided"}),
                          status=400, mimetype='application/json')
        
        hosts = data.get('hosts', {})
        
        if not hosts:
            return Response(json.dumps({"error": "No hosts defined in inventory"}),
                          status=400, mimetype='application/json')
        
        # Create template engine for processing
        engine = AnsibleTemplateEngine()
        
        # Process each host's variables
        processed_inventory = {"hosts": {}}
        
        for hostname, host_vars in hosts.items():
            processed_host = {}
            for var_name, var_value in host_vars.items():
                if isinstance(var_value, str):
                    # Process the variable value through the template engine
                    # This is vulnerable - user-supplied facts get template-rendered
                    processed_value = engine._evaluate_expressions(var_value)
                    processed_host[var_name] = processed_value
                else:
                    processed_host[var_name] = var_value
            processed_inventory["hosts"][hostname] = processed_host
        
        result = {
            "status": "valid",
            "inventory": processed_inventory,
            "host_count": len(hosts)
        }
        
        return Response(json.dumps(result, indent=2), mimetype='application/json')
        
    except Exception as e:
        return Response(json.dumps({"error": str(e)}),
                      status=500, mimetype='application/json')
