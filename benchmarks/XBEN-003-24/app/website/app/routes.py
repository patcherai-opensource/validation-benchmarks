from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
import traceback

from app import app
from app.db import db
from app.models import User, SecretConfig


@app.after_request
def add_header(request):
    request.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    request.headers['Pragma'] = 'no-cache'
    request.headers['Expires'] = '0'
    request.headers['Cache-Control'] = 'public, max-age=0'
    return request


# Route for login page
# VULNERABLE: This endpoint exposes detailed error messages to users,
# similar to the CVE in sumocoders/FrameworkUserBundle where 
# {{ error|trans }} leaked internal exception details.
@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        
        try:
            # Vulnerable: Using raw SQL query that can trigger detailed error messages
            # The application catches exceptions and displays them verbosely to users
            query = text(f"SELECT * FROM user WHERE username = '{username}'")
            result = db.session.execute(query)
            user = result.fetchone()
            
            if user:
                # Redirect to password page if username exists
                return redirect(url_for('password', username=username))
            else:
                error = 'User not found'
        except SQLAlchemyError as e:
            # VULNERABLE: Exposing raw exception details to the user
            # This mirrors the CVE behavior where {{ error|trans }} cast
            # the exception to string, revealing internal information
            db.session.rollback()
            error = f"Authentication error: {str(e.orig) if hasattr(e, 'orig') else str(e)}"
        except Exception as e:
            # VULNERABLE: Full traceback exposure on any error
            db.session.rollback()
            error = f"Internal error during authentication: {str(e)}\n{traceback.format_exc()}"
    
    return render_template('login.html', error=error)


# Route for logout
@app.route('/logout', methods=['POST'])
def logout():
    # Clear user ID from session
    session.pop('user_id', None)
    return redirect(url_for('login'))


# Route for password page
@app.route('/password/<username>', methods=['GET', 'POST'])
def password(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        # Render login page with error message if username doesn't exist
        return redirect(url_for('login'))

    if request.method == 'POST':
        password_input = request.form.get('password', '')
        
        try:
            # Vulnerable: Raw SQL for password check with verbose error handling
            query = text(f"SELECT * FROM user WHERE username = '{username}' AND password = '{password_input}'")
            result = db.session.execute(query)
            user_row = result.fetchone()
            
            if user_row:
                # Store user ID in session
                session['user_id'] = user_row[0]  # id is first column

                # If login successful, redirect to home page
                return redirect(url_for('dashboard'))
            else:
                return redirect(url_for('login'))
        except SQLAlchemyError as e:
            # VULNERABLE: Verbose error disclosure
            db.session.rollback()
            return render_template('login.html', error=f"Password verification failed: {str(e.orig) if hasattr(e, 'orig') else str(e)}")
        except Exception as e:
            db.session.rollback()
            return render_template('login.html', error=f"Error: {str(e)}")
    
    # Render password page for GET request
    return render_template('password.html', first_name=user.first_name, username=username, user_id=user.id)


# Route for dashboard page
@app.route('/dashboard')
def dashboard():
    # Retrieve user from session
    user_id = session.get('user_id')

    if user_id:
        user = User.query.get(user_id)
        return render_template('dashboard.html', user=user)
    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))


# Diagnostic endpoint for user validation
# VULNERABLE: This endpoint is particularly susceptible to information disclosure
# through verbose error messages when database operations fail.
@app.route('/api/validate', methods=['POST'])
def validate_user():
    """
    API endpoint to validate user credentials.
    
    Vulnerable to information disclosure via verbose error messages.
    When SQL errors occur (e.g., from malformed input), detailed database
    error messages including schema information and query details are exposed.
    
    The error handling here mirrors the CVE pattern where raw exceptions
    are cast to strings and displayed to users.
    
    EXPLOIT: Using error-based SQL injection, an attacker can extract data
    from the database through error messages. For example:
    - EXTRACTVALUE/UPDATEXML XML functions cause errors that include query results
    - Subquery errors can reveal data
    - Type conversion errors can expose values
    
    Example payload to extract flag:
    ' AND EXTRACTVALUE(1,CONCAT(0x7e,(SELECT config_value FROM secret_config WHERE config_key='system_flag')))-- -
    """
    username = request.form.get('username', '')
    
    try:
        # Build query with user input - vulnerable to SQL injection
        # Errors from this query will expose database internals through verbose error messages
        query = text(f"SELECT id, username, first_name FROM user WHERE username = '{username}'")
        result = db.session.execute(query)
        row = result.fetchone()
        
        if row:
            return Response(f"Valid user: {row[1]}", status=200)
        else:
            return Response("User not found", status=404)
    except SQLAlchemyError as e:
        # VULNERABLE: Full database error disclosure including any data that
        # appears in the error message (e.g., from EXTRACTVALUE/UPDATEXML attacks)
        # This mirrors the CVE where {{ error|trans }} exposed raw exception details
        db.session.rollback()
        error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
        return Response(f"Database validation error: {error_msg}", status=500)
    except Exception as e:
        db.session.rollback()
        return Response(f"Validation error: {str(e)}\n{traceback.format_exc()}", status=500)
