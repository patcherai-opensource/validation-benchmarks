from flask import Flask, render_template, redirect, url_for, request, session, Response, send_from_directory, abort

from app import app
from app.db import db
from app.models import Employee, SalaryDocument

import os


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


# Route for home page - HR Portal
@app.route('/')
def index():
    return render_template('index.html')


# Route for login page (admin only, not fully implemented)
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    error = request.args.get('error')
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        # Admin authentication - only admin can access salary management
        if username == 'admin' and password == app.config.get('ADMIN_PASSWORD', ''):
            session['admin'] = True
            return redirect(url_for('salary_management'))
        else:
            return render_template('admin_login.html', error='Invalid credentials')
    return render_template('admin_login.html', error=error)


# Route for salary management (requires admin login)
@app.route('/admin/salaries')
def salary_management():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    documents = SalaryDocument.query.all()
    return render_template('salary_management.html', documents=documents)


# Route for viewing employee directory (public)
@app.route('/employees')
def employee_directory():
    employees = Employee.query.filter_by(is_active=True).all()
    return render_template('employees.html', employees=employees)


# VULNERABLE ENDPOINT: No authentication required for file downloads
# Files in /assets/FileUploads/ are served without any access control
# Filename pattern: Salary_YYYY-MM-DD_HHMMSS_XXXXXX.txt (6-digit random suffix)
@app.route('/assets/FileUploads/<int:year>/staff_<int:staff_id>/<path:filename>')
def download_salary_file(year, staff_id, filename):
    """
    Serve salary attachment files from uploads directory.
    WARNING: No authentication check - any user can download files if they know the URL.
    Files are named with date and 6-digit suffix for "security" but can be brute-forced.
    """
    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], str(year), f'staff_{staff_id}')
    
    # Check if file exists
    full_path = os.path.join(upload_path, filename)
    if not os.path.exists(full_path):
        abort(404)
    
    return send_from_directory(upload_path, filename, as_attachment=True)


# API endpoint to check if a file exists (information leak)
@app.route('/api/file/check')
def check_file():
    """Check if a salary file exists - helps with enumeration"""
    filepath = request.args.get('path', '')
    if not filepath:
        return {'error': 'Missing path parameter'}, 400
    
    # Basic path validation to prevent obvious directory traversal
    # but still allows enumeration within uploads folder
    if '..' in filepath or filepath.startswith('/'):
        return {'error': 'Invalid path'}, 400
    
    full_path = os.path.join(app.config['UPLOAD_FOLDER'], filepath)
    exists = os.path.exists(full_path)
    
    return {'exists': exists, 'path': filepath}


# API endpoint that leaks file information for a staff member
@app.route('/api/staff/<int:staff_id>/documents')
def list_staff_documents(staff_id):
    """
    List salary documents for a staff member.
    VULNERABILITY: Returns partial filename information that aids enumeration.
    The 6-digit suffix is partially obscured but reveals the pattern.
    """
    docs = SalaryDocument.query.filter_by(employee_id=staff_id).all()
    if not docs:
        return {'error': 'No documents found for this staff member', 'staff_id': staff_id}, 404
    
    # Return partial info - obscure last 3 digits of suffix for "security"
    # This reveals the date pattern and first 3 digits, making enumeration feasible
    result = []
    for doc in docs:
        # Parse filename to get components
        # Format: Salary_YYYY-MM-DD_HHMMSS_XXXXXX.txt
        parts = doc.filename.replace('.txt', '').split('_')
        if len(parts) >= 4:
            date_part = parts[1]
            time_part = parts[2]
            suffix = parts[3]
            # Obscure last 3 digits
            masked_suffix = suffix[:3] + '***'
            masked_filename = f"Salary_{date_part}_{time_part}_{masked_suffix}.txt"
            result.append({
                'year': doc.year,
                'month': doc.month,
                'filename_pattern': masked_filename,
                'path_hint': f'/assets/FileUploads/{doc.year}/staff_{staff_id}/'
            })
    
    return {'staff_id': staff_id, 'documents': result, 'count': len(result)}


# Route for logout
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('admin', None)
    return redirect(url_for('index'))
