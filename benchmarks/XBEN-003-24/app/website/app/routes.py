from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app import app
from app.db import db
from app.models import User, SystemConfig


@app.after_request
def add_header(request):
    request.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    request.headers['Pragma'] = 'no-cache'
    request.headers['Expires'] = '0'
    request.headers['Cache-Control'] = 'public, max-age=0'
    return request


class AuthenticationException(Exception):
    pass


def validate_credentials(username, password):
    """
    Validates user credentials against the database.
    Returns user object if valid, raises exception with details otherwise.
    """
    query = text(f"SELECT id, username, password, first_name, last_name, email FROM user WHERE username = '{username}'")
    result = db.session.execute(query)
    row = result.fetchone()
    
    if row is None:
        raise AuthenticationException(f"AuthenticationException: User '{username}' not found in database")
    
    if row[2] != password:
        raise AuthenticationException(f"AuthenticationException: Invalid password for user '{username}'")
    
    return User.query.get(row[0])


# Route for login page
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = request.args.get('error')
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        try:
            user = validate_credentials(username, password)
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        except AuthenticationException as e:
            error = str(e)
        except SQLAlchemyError as e:
            db.session.rollback()
            error = str(e)
        except Exception as e:
            error = str(e)
    
    return render_template('login.html', error=error)


# Route for logout
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))


# Route for dashboard page
@app.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')

    if user_id:
        user = User.query.get(user_id)
        return render_template('dashboard.html', user=user)
    else:
        return redirect(url_for('login'))
