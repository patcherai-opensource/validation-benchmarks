from flask import Flask, render_template, redirect, url_for, request, session, Response, jsonify
import os
import json

from app import app
from app.db import db
from app.models import User

# Configuration for the file server
# Root directory for file operations - simulates a notebook server workspace
ROOT_DIR = '/workspace'
# Security setting: whether to allow access to hidden files (starting with .)
# This is set to False for security, but there's a bug in the implementation
ALLOW_HIDDEN = False


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Server'] = 'PyNotebook/2.4.1'
    return response


def is_hidden(path, root_dir):
    """Check if a path points to a hidden file or directory.
    
    A file is considered hidden if:
    - Its name starts with '.'
    - Any component of the path starts with '.'
    """
    # Get the relative path from root
    rel_path = os.path.relpath(path, root_dir)
    parts = rel_path.split(os.sep)
    
    for part in parts:
        if part.startswith('.'):
            return True
    return False


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
            session['username'] = user.username
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/home')
def home():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        return render_template('home.html', user=user)
    else:
        return redirect(url_for('login'))


@app.route('/files')
def files():
    """File browser page"""
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        return render_template('files.html', user=user)
    else:
        return redirect(url_for('login'))


@app.route('/settings')
def settings():
    """Settings page"""
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        return render_template('settings.html', user=user)
    else:
        return redirect(url_for('login'))


@app.route('/api/contents', defaults={'path': ''})
@app.route('/api/contents/<path:path>')
def api_contents_get(path):
    """
    REST API endpoint to get file/directory contents.
    Mimics Jupyter Server's Contents API.
    
    GET /api/contents/<path> - Get file or directory info
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized', 'message': 'Authentication required'}), 401
    
    # Construct the full path
    if path:
        full_path = os.path.join(ROOT_DIR, path)
    else:
        full_path = ROOT_DIR
    
    # Normalize the path to prevent directory traversal attacks
    full_path = os.path.normpath(full_path)
    
    # Check if path is within root directory (basic security)
    if not full_path.startswith(ROOT_DIR):
        return jsonify({'error': 'Forbidden', 'message': 'Access denied'}), 403
    
    # Check if path exists
    if not os.path.exists(full_path):
        return jsonify({'error': 'Not Found', 'message': f'No such file or directory: {path}'}), 404
    
    # VULNERABLE CODE: Hidden file check is only applied to directory listings,
    # not to direct file access. This allows reading hidden files directly.
    # The check below should also be applied when accessing individual files.
    
    if os.path.isdir(full_path):
        # Return directory listing
        items = []
        try:
            for item in os.listdir(full_path):
                item_path = os.path.join(full_path, item)
                # Filter out hidden files in directory listing (but not in direct access!)
                if not ALLOW_HIDDEN and item.startswith('.'):
                    continue
                
                item_info = {
                    'name': item,
                    'path': os.path.join(path, item) if path else item,
                    'type': 'directory' if os.path.isdir(item_path) else 'file',
                    'size': os.path.getsize(item_path) if os.path.isfile(item_path) else None,
                    'writable': os.access(item_path, os.W_OK)
                }
                items.append(item_info)
        except PermissionError:
            return jsonify({'error': 'Forbidden', 'message': 'Permission denied'}), 403
        
        return jsonify({
            'name': os.path.basename(full_path) or 'workspace',
            'path': path,
            'type': 'directory',
            'content': items,
            'writable': os.access(full_path, os.W_OK)
        })
    else:
        # Return file contents
        # BUG: No hidden file check here! This is the vulnerability.
        # An attacker can directly access /api/contents/.secrets/token
        # even though hidden files don't appear in directory listings.
        try:
            with open(full_path, 'r') as f:
                content = f.read()
            return jsonify({
                'name': os.path.basename(full_path),
                'path': path,
                'type': 'file',
                'content': content,
                'format': 'text',
                'writable': os.access(full_path, os.W_OK)
            })
        except PermissionError:
            return jsonify({'error': 'Forbidden', 'message': 'Permission denied'}), 403
        except UnicodeDecodeError:
            return jsonify({'error': 'Bad Request', 'message': 'File is not text readable'}), 400


@app.route('/api/contents/<path:path>', methods=['PUT'])
def api_contents_put(path):
    """
    REST API endpoint to create/update file contents.
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized', 'message': 'Authentication required'}), 401
    
    full_path = os.path.join(ROOT_DIR, path)
    full_path = os.path.normpath(full_path)
    
    if not full_path.startswith(ROOT_DIR):
        return jsonify({'error': 'Forbidden', 'message': 'Access denied'}), 403
    
    # Check for hidden files (but the check is inconsistent with GET)
    if not ALLOW_HIDDEN:
        rel_path = os.path.relpath(full_path, ROOT_DIR)
        if rel_path.startswith('.'):
            return jsonify({'error': 'Forbidden', 'message': 'Cannot write to hidden files'}), 403
    
    try:
        data = request.get_json()
        if not data or 'content' not in data:
            return jsonify({'error': 'Bad Request', 'message': 'Missing content'}), 400
        
        # Ensure parent directory exists
        parent_dir = os.path.dirname(full_path)
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)
        
        with open(full_path, 'w') as f:
            f.write(data['content'])
        
        return jsonify({
            'name': os.path.basename(full_path),
            'path': path,
            'type': 'file',
            'writable': True
        }), 201
    except PermissionError:
        return jsonify({'error': 'Forbidden', 'message': 'Permission denied'}), 403


@app.route('/api/contents/<path:path>', methods=['DELETE'])
def api_contents_delete(path):
    """
    REST API endpoint to delete a file.
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized', 'message': 'Authentication required'}), 401
    
    full_path = os.path.join(ROOT_DIR, path)
    full_path = os.path.normpath(full_path)
    
    if not full_path.startswith(ROOT_DIR):
        return jsonify({'error': 'Forbidden', 'message': 'Access denied'}), 403
    
    # Hidden file check for delete
    if not ALLOW_HIDDEN and is_hidden(full_path, ROOT_DIR):
        return jsonify({'error': 'Forbidden', 'message': 'Cannot delete hidden files'}), 403
    
    if not os.path.exists(full_path):
        return jsonify({'error': 'Not Found', 'message': 'File not found'}), 404
    
    try:
        if os.path.isdir(full_path):
            import shutil
            shutil.rmtree(full_path)
        else:
            os.remove(full_path)
        return '', 204
    except PermissionError:
        return jsonify({'error': 'Forbidden', 'message': 'Permission denied'}), 403


@app.route('/api/config')
def api_config():
    """Return server configuration (for debugging)"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    return jsonify({
        'version': '2.4.1',
        'root_dir': ROOT_DIR,
        'allow_hidden': ALLOW_HIDDEN,
        'features': ['contents', 'kernels', 'terminals'],
        'note': 'Hidden files (starting with .) are not accessible when allow_hidden is False'
    })


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if request.method == 'POST':
            user.name = request.form['name']
            user.lastname = request.form['lastname']
            user.email = request.form['email']
            db.session.commit()
            return redirect(url_for('home'))
        else:
            return render_template('profile.html', user=user)
    else:
        return redirect(url_for('login'))
