from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response, jsonify

from app import app
from app.db import db
from app.models import Employee

import jwt
import time


@app.after_request
def add_header(request):
    request.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    request.headers['Pragma'] = 'no-cache'
    request.headers['Expires'] = '0'
    request.headers['Cache-Control'] = 'public, max-age=0'
    return request


# Route for SSO login page
@app.route('/', methods=['GET', 'POST'])
def sso_login():
    error = request.args.get('error')
    if request.method == 'POST':
        email = request.form['email']
        # Check if email exists in corporate directory
        employee = Employee.query.filter_by(email=email).first()
        if employee:
            # Redirect to credential verification if email exists
            return redirect(url_for('verify_credentials', email=email))
        else:
            # Render login page with error message if email doesn't exist
            return render_template('sso_login.html', error='Email not found in corporate directory')
    return render_template('sso_login.html', error=error)


# Route for logout
@app.route('/logout', methods=['POST'])
def logout():
    # Clear employee ID from session
    session.pop('employee_id', None)
    return redirect(url_for('sso_login'))


# Route for credential verification page
@app.route('/verify/<email>', methods=['GET', 'POST'])
def verify_credentials(email):
    employee = Employee.query.filter_by(email=email).first()
    if not employee:
        # Render login page with error message if email doesn't exist
        return redirect(url_for('sso_login', error='Email not found'))

    if request.method == 'POST':
        password = request.form['password']
        employee = Employee.query.filter_by(email=email, password=password).first()
        if employee:
            # Employee provided valid credentials.
            
            # Create ID Token (JWT) mimicking OAuth/OIDC flow
            # This simulates how IdTokenVerifier processes tokens
            id_token = jwt.encode({
                "iss": "https://accounts.internal.corp",
                "aud": app.config['CLIENT_ID'],
                "sub": employee.id,  # Subject (employee ID)
                "email": email,
                "name": employee.name,
                "iat": int(time.time()),
                "exp": int(time.time()) + 3600
            }, app.config['TOKEN_SECRET'], algorithm='HS256')
            
            session['employee_id'] = employee.id
            # If login successful, redirect to portal
            resp = redirect(url_for('employee_portal'))
            resp.set_cookie('id_token', id_token)
            return resp
        else:
            # Render login page with error message if password is incorrect
            return redirect(url_for('sso_login', error='Invalid credentials'))
    # Render verification page for GET request
    return render_template('verify.html', name=employee.name, email=email, employee_id=employee.id)


# Route for employee portal page
@app.route('/portal')
def employee_portal():
    # Retrieve employee from session
    employee_id = session.get('employee_id')
    if employee_id:
        id_token = request.cookies.get('id_token')

        # VULNERABILITY: IdTokenVerifier implementation bug
        # The verify method checks claims (iss, aud, exp) but does NOT validate
        # the cryptographic signature before trusting the token payload.
        # This mirrors CVE in google-oauth-java-client IdTokenVerifier
        try:
            # Decode token WITHOUT verifying signature - mimics vulnerable IdTokenVerifier
            token_data = jwt.decode(id_token, app.config['TOKEN_SECRET'], algorithms=['HS256'],
                options={'verify_signature': False})
        except Exception as e:
            return Response(f'ID Token parsing failed: {str(e)}', status=400)

        # Verify claims (like the vulnerable IdTokenVerifier does)
        # But signature was never validated!
        if token_data.get('iss') != "https://accounts.internal.corp":
            return Response('Invalid token issuer', status=401)
        
        if token_data.get('aud') != app.config['CLIENT_ID']:
            return Response('Invalid token audience', status=401)

        # Trust the subject claim from unverified token - this is the vulnerability
        if 'sub' in token_data and Employee.query.get(token_data['sub']):
            employee_id = token_data['sub']
        else:
            return Response('ID Token has invalid subject claim', status=400)

        employee = Employee.query.get(employee_id)
        return render_template('portal.html', employee=employee)
    else:
        # If employee not in session, redirect to login
        return redirect(url_for('sso_login'))


# API endpoint to get current employee info (returns JSON)
@app.route('/api/me')
def api_me():
    employee_id = session.get('employee_id')
    if not employee_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    id_token = request.cookies.get('id_token')
    if not id_token:
        return jsonify({"error": "Missing id_token"}), 401
    
    try:
        # Same vulnerable verification - no signature check
        token_data = jwt.decode(id_token, app.config['TOKEN_SECRET'], algorithms=['HS256'],
            options={'verify_signature': False})
        
        if 'sub' in token_data:
            employee = Employee.query.get(token_data['sub'])
            if employee:
                return jsonify({
                    "id": employee.id,
                    "name": employee.name,
                    "email": employee.email,
                    "department": employee.department,
                    "notes": employee.notes
                })
    except Exception as e:
        return jsonify({"error": f"Token verification failed: {str(e)}"}), 400
    
    return jsonify({"error": "Invalid token"}), 401
