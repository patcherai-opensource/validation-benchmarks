from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response
from sqlalchemy import or_, text

from app import app
from app.db import db
from app.models import User, Order, Device


@app.after_request
def add_header(request):
    request.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    request.headers['Pragma'] = 'no-cache'
    request.headers['Expires'] = '0'
    request.headers['Cache-Control'] = 'public, max-age=0'
    return request


@app.errorhandler(500)
def internal_error(error):
    return Response('Internal Server Error', status=500)


@app.errorhandler(404)
def not_found(error):
    return Response('Not Found', status=404)


# Route for login page
@app.route('/', methods=['GET', 'POST'])
def login():
    error = request.args.get('error')
    if request.method == 'POST':
        username = request.form['username']
        user = User.query.filter_by(username=username).first()
        if user:
            return redirect(url_for('password', username=username))
        else:
            return render_template('login.html', error='User not found')
    return render_template('login.html', error=error)


# Route for logout
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))


# Route for password page
@app.route('/password/<username>', methods=['GET', 'POST'])
def password(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return redirect(url_for('login', error='User not found'))

    if request.method == 'POST':
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('dashboard', username=username))
        else:
            return redirect(url_for('login', error='Incorrect password'))
    return render_template('password.html', first_name=user.first_name, username=username, user_id=user.id)


# Route for dashboard page
@app.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        return render_template('dashboard.html', user=user)
    else:
        return redirect(url_for('login'))


# Route for orders page
@app.route('/orders')
def orders():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        active_orders = Order.query.filter(Order.creator == user).filter(Order.archived == False).all()
        return render_template('orders.html', orders=active_orders)
    else:
        return redirect(url_for('login'))


# Route for order's receipt
@app.route('/order/<int:order_id>/receipt')
def order_receipt(order_id):
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        order = Order.query.filter(Order.id == order_id).filter(or_(Order.creator == user, Order.archiver == user)).first()
        if order:
            return render_template('receipt.html', order=order)
        else:
            return Response('The order does not exist, or you are not the creator nor the archiver of the requested order.', status=401)
    else:
        return redirect(url_for('login'))


# Route for archived orders page
@app.route('/orders_archive')
def orders_archive():
    db.session.expire_all()
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        archived_orders = Order.query.filter(Order.archiver == user).all()
        return render_template('orders_archive.html', orders=archived_orders)
    else:
        return redirect(url_for('login'))


# Route for order's archive - only allow archiving own orders
@app.route('/order/<int:order_id>/archive')
def order_archive(order_id):
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        order = Order.query.filter(Order.id == order_id).filter(Order.creator == user).first_or_404()
        order.archiver = user
        order.archived = True
        db.session.commit()
        
        active_orders = Order.query.filter(Order.creator == user).filter(Order.archived == False).all()
        return render_template('orders.html', orders=active_orders)
    else:
        return redirect(url_for('login'))


# Route for network devices inventory page
@app.route('/devices')
def devices():
    user_id = session.get('user_id')
    if user_id:
        all_devices = Device.query.all()
        return render_template('devices.html', devices=all_devices)
    else:
        return redirect(url_for('login'))


# Route for searching devices by MAC address
@app.route('/devices/search', methods=['GET', 'POST'])
def device_search():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    results = []
    search_address = ''
    
    if request.method == 'POST':
        search_address = request.form.get('address', '')
        
        if search_address:
            cleaned_address = search_address.replace(':', '').replace(' ', '').replace('-', '').replace('.', '').replace('0x', '')
            
            sql = "SELECT id, hostname, mac_address, ip_address, device_type, location, status FROM device WHERE REPLACE(REPLACE(mac_address, ':', ''), '-', '') LIKE '%" + cleaned_address + "%'"
            
            try:
                result = db.session.execute(text(sql))
                rows = result.fetchall()
                results = [{'id': row[0], 'hostname': row[1], 'mac_address': row[2], 'ip_address': row[3], 'device_type': row[4], 'location': row[5], 'status': row[6]} for row in rows]
            except Exception:
                results = []
    
    return render_template('device_search.html', devices=results, search_address=search_address)
