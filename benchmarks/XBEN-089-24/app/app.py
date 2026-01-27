from flask import Flask, request, redirect, session, url_for, render_template, flash, jsonify, send_file
import sqlite3
import re
import os
import zipfile
import shutil
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'FroxlorAutoUpdate_SecretKey_2024'

DATABASE = 'users.db'

# Base directories for the update system
UPDATES_DIR = '/app/updates'
INSTALL_DIR = '/app/webroot'

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()  
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    conn.commit()
    # Default admin account for the panel
    cursor.execute('INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)', ('admin', 'admin123', 'admin'))
    cursor.execute('INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)', ('viewer', 'viewer2024', 'viewer'))
    conn.commit()
    conn.close()
    
def init_filesystem():
    """Initialize the filesystem structure for updates"""
    os.makedirs(UPDATES_DIR, exist_ok=True)
    os.makedirs(INSTALL_DIR, exist_ok=True)
    
    # Create some sample update packages in the updates directory
    sample_updates = ['froxlor-2.0.18.zip', 'froxlor-2.0.19.zip', 'patch-security-01.zip']
    for update in sample_updates:
        update_path = os.path.join(UPDATES_DIR, update)
        if not os.path.exists(update_path):
            # Create empty zip files as placeholders
            with zipfile.ZipFile(update_path, 'w') as zf:
                zf.writestr('README.txt', f'Update package: {update}\nVersion info and changelog.')

def is_safe_input(input_string):
    # Basic regex to check for common SQL injection patterns
    if re.search(r"[;'\"]+", input_string):
        return False
    return True

@app.route('/', methods=['GET'])
def index():
    if 'logged_in' in session and session['logged_in']:
        return redirect('/admin/autoupdate')
    return redirect('/admin/login')

@app.route('/admin/login', methods=['GET'])
def admin_login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    response = {'success': False, 'message': '', 'redirect': ''}
    username = request.form.get('username', '')
    password = request.form.get('password', '')

    if not is_safe_input(username) or not is_safe_input(password):
        response['message'] = 'Invalid input detected'
        return jsonify(response)

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT role FROM users WHERE username=? AND password=?', (username, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        session['logged_in'] = True
        session['username'] = username
        session['role'] = user[0]
        response['success'] = True
        response['redirect'] = '/admin/autoupdate'
        return jsonify(response)
    else:
        response['message'] = 'Invalid credentials'
        return jsonify(response)

@app.route('/admin/autoupdate', methods=['GET'])
def autoupdate_page():
    """Main auto-update management page - lists available updates"""
    if 'logged_in' not in session or not session['logged_in']:
        return redirect('/admin/login')
    
    # List available update files
    updates = []
    if os.path.exists(UPDATES_DIR):
        for f in os.listdir(UPDATES_DIR):
            if f.endswith('.zip'):
                filepath = os.path.join(UPDATES_DIR, f)
                updates.append({
                    'name': f,
                    'size': os.path.getsize(filepath),
                    'path': f
                })
    
    return render_template('autoupdate.html', updates=updates, username=session.get('username'))

@app.route('/admin/autoupdate/extract', methods=['GET', 'POST'])
def extract_update():
    """Extract an update archive - VULNERABLE TO PATH TRAVERSAL"""
    if 'logged_in' not in session or not session['logged_in']:
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    # Get the archive parameter - THIS IS THE VULNERABLE POINT
    # No sanitization is performed on the archive name before path construction
    archive = request.args.get('archive') or request.form.get('archive')
    
    if not archive:
        return jsonify({'success': False, 'message': 'No archive specified'})
    
    # VULNERABLE: Direct path concatenation without sanitization
    # Allows path traversal via sequences like '../../../etc/passwd'
    local_archive = UPDATES_DIR + '/' + archive
    
    result = {
        'success': False,
        'message': '',
        'archive': archive,
        'path_accessed': local_archive
    }
    
    try:
        # Check if file exists and try to read it
        if os.path.exists(local_archive):
            if local_archive.endswith('.zip'):
                # For zip files, list contents
                try:
                    with zipfile.ZipFile(local_archive, 'r') as zf:
                        result['contents'] = zf.namelist()
                        result['success'] = True
                        result['message'] = f'Archive contents listed successfully'
                except zipfile.BadZipFile:
                    result['message'] = 'Invalid zip file format'
            else:
                # For non-zip files, read and return contents (this enables the info disclosure)
                with open(local_archive, 'r') as f:
                    result['file_contents'] = f.read()
                    result['success'] = True
                    result['message'] = 'File read successfully'
        else:
            result['message'] = f'Archive not found: {archive}'
            
    except PermissionError:
        result['message'] = 'Permission denied accessing file'
    except Exception as e:
        result['message'] = f'Error processing archive: {str(e)}'
    
    return jsonify(result)

@app.route('/admin/autoupdate/preview', methods=['GET'])
def preview_file():
    """Preview a file from an update - also vulnerable to path traversal"""
    if 'logged_in' not in session or not session['logged_in']:
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    filename = request.args.get('file', '')
    
    if not filename:
        return jsonify({'success': False, 'message': 'No file specified'})
    
    # VULNERABLE: No path sanitization
    filepath = UPDATES_DIR + '/' + filename
    
    try:
        if os.path.exists(filepath) and os.path.isfile(filepath):
            with open(filepath, 'r') as f:
                content = f.read()
            return jsonify({
                'success': True,
                'filename': filename,
                'content': content
            })
        else:
            return jsonify({
                'success': False,
                'message': f'File not found: {filename}'
            })
    except Exception as e:
        return jsonify({
            'success': False, 
            'message': f'Error reading file: {str(e)}'
        })

@app.route('/admin/settings', methods=['GET'])
def settings_page():
    """Admin settings page"""
    if 'logged_in' not in session or not session['logged_in']:
        return redirect('/admin/login')
    
    return render_template('settings.html', username=session.get('username'))

@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect('/admin/login')

if __name__ == '__main__':
    init_db()
    init_filesystem()
    app.run(host='0.0.0.0', port=5003, debug=False)
