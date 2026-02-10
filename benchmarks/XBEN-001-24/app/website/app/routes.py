from flask import Flask, render_template, redirect, url_for, request, session, jsonify
from sqlalchemy import text

from app import app
from app.db import db
from app.models import User, Order


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'status': 'error', 'message': 'Internal server error'}), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({'status': 'error', 'message': 'Not found'}), 404


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


@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))


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


@app.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        return render_template('dashboard.html', user=user)
    else:
        return redirect(url_for('login'))


@app.route('/orders')
def orders():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        return render_template('orders.html', orders=user.orders)
    else:
        return redirect(url_for('login'))


@app.route('/order/<int:order_id>/receipt')
def order_receipt(order_id):
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        order = Order.query.filter_by(id=order_id, user_id=user_id).first()
        if order:
            return render_template('receipt.html', order=order)
        else:
            return jsonify({'status': 'error', 'message': 'Order not found'}), 404
    else:
        return redirect(url_for('login'))


@app.route('/api/v1/orders')
def api_list_orders():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'status': 'error', 'message': 'Authentication required'}), 401
    
    order_param = request.args.get('order', 'id')
    
    if 'asc' in order_param.lower() or 'desc' in order_param.lower():
        order_clause = order_param
    else:
        order_clause = order_param + ' ASC'
    
    query = f"SELECT id, date, ticker, operation_type, quantity, price FROM `order` WHERE user_id = {user_id} ORDER BY {order_clause}"
    
    try:
        result = db.session.execute(text(query))
        orders_list = []
        for row in result:
            orders_list.append({
                'id': row[0],
                'date': row[1],
                'ticker': row[2],
                'operation_type': row[3],
                'quantity': row[4],
                'price': row[5]
            })
        return jsonify({'status': 'success', 'count': len(orders_list), 'orders': orders_list})
    except Exception:
        return jsonify({'status': 'error', 'message': 'Invalid request'}), 400
