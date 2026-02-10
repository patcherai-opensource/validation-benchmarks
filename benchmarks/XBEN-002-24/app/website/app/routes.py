from flask import Flask, render_template, redirect, url_for, request, session, Response, jsonify

from app import app
from app.db import db
from app.models import User, VirtualServer


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.errorhandler(404)
def not_found(e):
    return Response('Not Found', status=404)


@app.errorhandler(500)
def internal_error(e):
    return Response('Internal Server Error', status=500)


@app.route('/', methods=['GET', 'POST'])
def login():
    error = request.args.get('error')
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html', error=error)


@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))


@app.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    user = User.query.filter(User.id == user_id).first()
    if not user:
        return redirect(url_for('login'))
    
    return render_template('dashboard.html', user=user)


@app.route('/servers')
def servers():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    user = User.query.filter(User.id == user_id).first()
    if not user:
        return redirect(url_for('login'))
    
    user_servers = VirtualServer.query.filter(VirtualServer.owner == user).all()
    return render_template('servers.html', servers=user_servers)


@app.route('/server/<int:vserverid>')
def server_details(vserverid):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    user = User.query.filter(User.id == user_id).first()
    if not user:
        return redirect(url_for('login'))
    
    server = VirtualServer.query.filter(VirtualServer.id == vserverid, VirtualServer.owner == user).first()
    if not server:
        return Response('Server not found or access denied', status=404)
    
    return render_template('server_details.html', server=server)


@app.route('/server/<int:vserverid>/change-hostname', methods=['GET', 'POST'])
def change_hostname(vserverid):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    user = User.query.filter(User.id == user_id).first()
    if not user:
        return redirect(url_for('login'))
    
    server = VirtualServer.query.filter(VirtualServer.id == vserverid).first()
    if not server:
        return Response('Server not found', status=404)
    
    if request.method == 'POST':
        new_hostname = request.form.get('newhostname', '')
        if new_hostname:
            server.hostname = new_hostname
            db.session.commit()
            return redirect(url_for('servers') + '?msg=Hostname+updated+successfully')
        return render_template('change_hostname.html', server=server, error='Hostname cannot be empty')
    
    return render_template('change_hostname.html', server=server)


@app.route('/server/<int:vserverid>/change-root-password', methods=['GET', 'POST'])
def change_root_password(vserverid):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    user = User.query.filter(User.id == user_id).first()
    if not user:
        return redirect(url_for('login'))
    
    server = VirtualServer.query.filter(VirtualServer.id == vserverid).first()
    if not server:
        return Response('Server not found', status=404)
    
    if request.method == 'POST':
        new_password = request.form.get('newrootpassword', '')
        if new_password and len(new_password) >= 8:
            server.root_password = new_password
            db.session.commit()
            return redirect(url_for('servers') + '?msg=Root+password+updated+successfully')
        return render_template('change_root_password.html', server=server, error='Password must be at least 8 characters')
    
    return render_template('change_root_password.html', server=server)


@app.route('/server/<int:vserverid>/change-vnc-password', methods=['GET', 'POST'])
def change_vnc_password(vserverid):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    user = User.query.filter(User.id == user_id).first()
    if not user:
        return redirect(url_for('login'))
    
    server = VirtualServer.query.filter(VirtualServer.id == vserverid).first()
    if not server:
        return Response('Server not found', status=404)
    
    if request.method == 'POST':
        new_password = request.form.get('newvncpassword', '')
        if new_password and len(new_password) >= 6:
            server.vnc_password = new_password
            db.session.commit()
            return redirect(url_for('servers') + '?msg=VNC+password+updated+successfully')
        return render_template('change_vnc_password.html', server=server, error='Password must be at least 6 characters')
    
    return render_template('change_vnc_password.html', server=server)


@app.route('/server/<int:vserverid>/console', methods=['GET', 'POST'])
def server_console(vserverid):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    user = User.query.filter(User.id == user_id).first()
    if not user:
        return redirect(url_for('login'))
    
    server = VirtualServer.query.filter(VirtualServer.id == vserverid).first()
    if not server:
        return Response('Server not found', status=404)
    
    if request.method == 'POST':
        password = request.form.get('password', '')
        if password == server.root_password:
            return render_template('console.html', server=server, authenticated=True)
        return render_template('console.html', server=server, authenticated=False, error='Invalid password')
    
    return render_template('console.html', server=server, authenticated=False)
