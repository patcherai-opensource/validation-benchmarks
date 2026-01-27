from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response, jsonify

from app import app
from app.db import db
from app.models import User, Translation
from sqlalchemy import text

import os
import json

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response



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
            session['user_role'] = user.role
            # If login successful, redirect to home page
            return redirect(url_for('home'))
        else:
            # If login fails, redirect back to login page with an error message
            return render_template('templates/login.html', error='Invalid username or password')
    return render_template('templates/login.html')


@app.route('/logout')
def logout():
    # Clear user ID from session
    session.pop('user_id', None)
    session.pop('user_role', None)
    return redirect(url_for('login'))


@app.route('/home')
def home():
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        translation_count = Translation.query.count()
        return render_template('templates/home.html', user=user, translation_count=translation_count)
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
            db.session.commit()
            return redirect(url_for('home'))  # Redirect to home page after profile update
        else:
            # Render profile template with user's information for GET request
            return render_template('templates/profile.html', user=user)
    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))


@app.route('/update_profile', methods=['GET', 'POST'])
def update_profile():
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if request.method == 'POST':
            # Update user's profile with new values
            user.name = request.form['name']
            user.lastname = request.form['lastname']
            user.email = request.form['email']

            # Check if the post request has the file part
            if 'image_profile' in request.files:
                image_profile = request.files['image_profile']
                # If the user does not select a file, the browser submits an empty file without a filename
                if image_profile.filename != '':

                    safe_dir = '/var/www/translation_cms/app/static/images/'
                    final_path = os.path.realpath(os.path.join(safe_dir, image_profile.filename))

                    if os.path.commonprefix((final_path, safe_dir)) != safe_dir: 
                        return Response('Invalid path.', status=400)

                    image_profile.save(final_path)
                    user.image_profile_filename = image_profile.filename

            db.session.commit()
        return render_template('templates/profile.html', user=user)

    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))


@app.route('/translations')
def translations():
    """List all translations"""
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        translations = Translation.query.all()
        return render_template('templates/translations.html', user=user, translations=translations)
    else:
        return redirect(url_for('login'))


@app.route('/admin/translation/export')
def export_translations():
    """
    Export translations with optional filtering.
    Accepts a 'filter' GET parameter containing a JSON array of filter objects.
    Each filter object can have: property, value, type, operator
    
    Example: /admin/translation/export?filter=[{"property":"language","value":"en","type":"string"}]
    """
    user_id = session.get('user_id')
    user_role = session.get('user_role')
    
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    if user_role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    # Get filter parameter
    filter_json = request.args.get('filter', None)
    
    # Base query
    base_query = "SELECT id, `key`, language, value, domain FROM translation WHERE 1=1"
    condition_parts = []
    
    if filter_json:
        try:
            filters = json.loads(filter_json)
            
            for f in filters:
                # Get filter properties
                field_name = f.get('property', '')
                filter_value = f.get('value', '')
                filter_type = f.get('type', 'string')
                operator = f.get('operator', 'like')
                
                # Determine SQL operator
                if operator == 'like':
                    sql_operator = 'LIKE'
                    filter_value = f'%{filter_value}%'
                elif operator == 'eq':
                    sql_operator = '='
                elif operator == 'gt':
                    sql_operator = '>'
                elif operator == 'lt':
                    sql_operator = '<'
                else:
                    sql_operator = 'LIKE'
                    filter_value = f'%{filter_value}%'
                
                # VULNERABLE: field_name is directly interpolated into SQL without validation
                # This mimics CVE-2023-30849 where the 'property' field is used unsanitized
                condition = f"{field_name} {sql_operator} '{filter_value}'"
                condition_parts.append(condition)
                
        except json.JSONDecodeError as e:
            return jsonify({'error': f'Invalid JSON in filter parameter: {str(e)}'}), 400
        except Exception as e:
            return jsonify({'error': f'Filter processing error: {str(e)}'}), 400
    
    # Build final query
    if condition_parts:
        full_query = base_query + " AND " + " AND ".join(condition_parts)
    else:
        full_query = base_query
    
    try:
        # Execute raw SQL query (vulnerable to injection)
        result = db.session.execute(text(full_query))
        rows = result.fetchall()
        
        # Format results
        export_data = []
        for row in rows:
            export_data.append({
                'id': row[0],
                'key': row[1],
                'language': row[2],
                'value': row[3],
                'domain': row[4]
            })
        
        return jsonify({
            'success': True,
            'count': len(export_data),
            'data': export_data
        })
        
    except Exception as e:
        # Return SQL error for debugging - this helps attackers identify injection points
        error_msg = str(e)
        return jsonify({
            'success': False,
            'error': f'Database error: {error_msg}'
        }), 500


@app.route('/admin/translation/add', methods=['POST'])
def add_translation():
    """Add a new translation"""
    user_id = session.get('user_id')
    user_role = session.get('user_role')
    
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    if user_role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'JSON body required'}), 400
    
    key = data.get('key')
    language = data.get('language')
    value = data.get('value')
    domain = data.get('domain', 'messages')
    
    if not key or not language or not value:
        return jsonify({'error': 'key, language, and value are required'}), 400
    
    translation = Translation(key=key, language=language, value=value, domain=domain)
    db.session.add(translation)
    db.session.commit()
    
    return jsonify({'success': True, 'id': translation.id})


@app.route('/error')
def error():
    error_message = request.args.get('message', 'An error occurred.')
    return render_template('templates/error.html', error_message=error_message)
