from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response, jsonify
from sqlalchemy import or_

from app import app
from app.db import db
from app.models import User, Organization, Event


@app.after_request
def add_header(request):
    request.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    request.headers['Pragma'] = 'no-cache'
    request.headers['Expires'] = '0'
    request.headers['Cache-Control'] = 'public, max-age=0'
    return request



# Route for login page
@app.route('/', methods=['GET', 'POST'])
def login():
    error = request.args.get('error')
    if request.method == 'POST':
        username = request.form['username']
        # Check if username exists
        user = User.query.filter_by(username=username).first()
        if user:
            if not user.enabled:
                return render_template('login.html', error='Account disabled. Contact administrator.')
            # Redirect to password page if username exists
            return redirect(url_for('password', username=username))
        else:
            # Render login page with error message if username doesn't exist
            return render_template('login.html', error='User not found')
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
        return redirect(url_for('login', error='User not found'))

    if request.method == 'POST':
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            # User provided a valid username/password pair.
            session['user_id'] = user.id

            # If login successful, redirect to home page
            return redirect(url_for('dashboard', username=username))
        else:
            # Render login page with error message if password is incorrect
            return redirect(url_for('login', error='Incorrect password'))
    # Render password page for GET request
    return render_template('password.html', first_name=user.first_name, username=username, user_id=user.id)


# Route for dashboard page
@app.route('/dashboard')
def dashboard():
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        return render_template('dashboard.html', user=user)
    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))


# Route for events page (user's organization events)
@app.route('/admin/api/events')
def events():
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        # Only show active events from user's organization
        org_events = Event.query.filter(Event.organization == user.organization).filter(Event.enabled == True).all()
        return render_template('events.html', events=org_events)
    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))


# Route for event configuration - VULNERABLE TO IDOR
@app.route('/admin/api/events/<int:event_id>/config')
def event_config(event_id):
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        # VULNERABILITY: Event is retrieved by ID without checking if it belongs to user's organization
        # This allows cross-tenant access to event configurations
        event = Event.query.filter(Event.id == event_id).filter(or_(Event.creator == user, Event.manager == user)).first()
        if event:
            return render_template('config.html', event=event)
        else:
            return Response('Event not found or you do not have access to view its configuration.', status=403)
    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))


# Route for disabled events page
@app.route('/admin/api/events/disabled')
def events_disabled():
    db.session.expire_all()
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        disabled_events = Event.query.filter(Event.manager == user).all()
        return render_template('events_disabled.html', events=disabled_events)
    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))


# Route for enabling/disabling an event - VULNERABLE TO IDOR
@app.route('/admin/api/events/<int:event_id>/enable/<enable>')
def event_enable(event_id, enable):
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()

        # VULNERABILITY: The event is retrieved from the DB by using the event_id supplied
        # by the user. There is no authorization check to verify if the user belongs to
        # the same organization as the event. This lack of authorization checks 
        # creates an IDOR vulnerability that allows attackers to enable/disable events
        # from OTHER organizations (cross-tenant access).
        event = Event.query.filter(Event.id == event_id).first_or_404()
        
        if enable.lower() == 'true':
            event.enabled = True
            event.manager = None
        else:
            event.enabled = False
            event.manager = user  # Set current user as manager when disabling
        
        db.session.commit()
        
        org_events = Event.query.filter(Event.organization == user.organization).filter(Event.enabled == True).all()
        return render_template('events.html', events=org_events)
    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))
