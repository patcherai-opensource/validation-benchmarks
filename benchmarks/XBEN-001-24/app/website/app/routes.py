from flask import Flask, render_template, redirect, url_for, request, session, jsonify

from app import app
from app.db import db
from app.models import User, Order


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', error_code=404, error_message='Page not found'), 404


@app.errorhandler(500)
def internal_error(e):
    return render_template('error.html', error_code=500, error_message='Internal server error'), 500


@app.route('/', methods=['GET', 'POST'])
def index():
    action = request.args.get('wc-ajax')
    if action:
        if action == 'wc_stripe_update_payment_intent':
            return handle_update_payment_intent()
        elif action == 'get_order_status':
            return handle_get_order_status()
        return jsonify({'success': False, 'error': 'Unknown action'}), 400
    return redirect(url_for('shop'))


@app.route('/shop')
def shop():
    return render_template('shop.html')


@app.route('/cart')
def cart():
    return render_template('cart.html')


@app.route('/checkout')
def checkout():
    return render_template('checkout.html')


@app.route('/account/login', methods=['GET', 'POST'])
def login():
    error = request.args.get('error')
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('account_orders'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html', error=error)


@app.route('/account/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return redirect(url_for('shop'))


@app.route('/account/orders')
def account_orders():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if user:
            return render_template('orders.html', orders=user.orders, user=user)
    return redirect(url_for('login'))


@app.route('/account/order/<int:order_id>')
def order_detail(order_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    user = User.query.get(user_id)
    if not user:
        return redirect(url_for('login'))
    
    order = Order.query.filter_by(id=order_id, user_id=user_id).first()
    if not order:
        return render_template('error.html', error_code=404, error_message='Order not found'), 404
    
    return render_template('order_detail.html', order=order)


def handle_update_payment_intent():
    if request.method != 'POST':
        return jsonify({'success': False, 'error': 'Method not allowed'}), 405
    
    order_id = request.form.get('stripe_order_id')
    payment_intent_id = request.form.get('wc_payment_intent_id')
    
    if not order_id or not payment_intent_id:
        return jsonify({'success': False, 'error': 'Missing required parameters'}), 400
    
    try:
        order_id = int(order_id)
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'Invalid order ID'}), 400
    
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'success': False, 'error': 'Order not found'}), 404
    
    order.payment_intent_id = payment_intent_id
    order.payment_confirmed = True
    order.status = 'completed'
    db.session.commit()
    
    response_data = {
        'success': True,
        'order_id': order.id,
        'status': order.status,
        'payment_confirmed': order.payment_confirmed
    }
    
    if order.confirmation_message:
        response_data['confirmation_message'] = order.confirmation_message
    
    return jsonify(response_data)


def handle_get_order_status():
    order_id = request.args.get('order_id')
    
    if not order_id:
        return jsonify({'success': False, 'error': 'Missing order ID'}), 400
    
    try:
        order_id = int(order_id)
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'Invalid order ID'}), 400
    
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'success': False, 'error': 'Order not found'}), 404
    
    return jsonify({
        'success': True,
        'order_id': order.id,
        'status': order.status,
        'payment_confirmed': order.payment_confirmed,
        'payment_intent_id': order.payment_intent_id
    })
