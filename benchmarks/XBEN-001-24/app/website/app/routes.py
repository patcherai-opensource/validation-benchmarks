from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response, jsonify

from app import app
from app.db import db
from app.models import User, Order, PaymentIntent


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['X-Powered-By'] = 'WooCommerce/8.5.2'
    return response


# Home page - store front
@app.route('/')
def home():
    return render_template('shop.html')


# Route for login page
@app.route('/my-account', methods=['GET', 'POST'])
def login():
    error = request.args.get('error')
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('my_account_orders'))
        else:
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html', error=error)


# Route for logout
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))


# Route for my account orders
@app.route('/my-account/orders')
def my_account_orders():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        return render_template('orders.html', user=user, orders=user.orders)
    else:
        return redirect(url_for('login'))


# Route for order details
@app.route('/my-account/view-order/<int:order_id>')
def view_order(order_id):
    user_id = session.get('user_id')
    if user_id:
        # Properly check if the order belongs to the user
        order = Order.query.filter_by(id=order_id, user_id=user_id).first()
        if order:
            return render_template('order_details.html', order=order)
        else:
            return render_template('error.html', message='Order not found'), 404
    else:
        return redirect(url_for('login'))


# AJAX endpoint for updating payment intent
# VULNERABILITY: This endpoint does not verify that the current user owns the order
# or that the payment intent belongs to them. Any user (even unauthenticated) can
# modify payment intents for any order by providing arbitrary order_id values.
@app.route('/', methods=['POST'])
def wc_ajax_handler():
    action = request.args.get('wc-ajax')
    
    if action == 'wc_stripe_update_payment_intent':
        # Get parameters from request
        stripe_order_id = request.form.get('stripe_order_id')
        wc_payment_intent_id = request.form.get('wc_payment_intent_id')
        new_status = request.form.get('payment_status', 'processing')
        
        if not stripe_order_id:
            return jsonify({
                'success': False,
                'error': 'Missing stripe_order_id parameter'
            }), 400
        
        # IDOR VULNERABILITY: No authentication check!
        # No verification that the user owns this order or is even logged in!
        # The order is retrieved directly using the user-supplied stripe_order_id
        order = Order.query.get(stripe_order_id)
        
        if not order:
            return jsonify({
                'success': False,
                'error': 'Order not found'
            }), 404
        
        # Update payment intent if provided
        if wc_payment_intent_id:
            payment_intent = PaymentIntent.query.filter_by(intent_id=wc_payment_intent_id).first()
            if payment_intent:
                payment_intent.status = new_status
        
        # Update order status based on payment status
        old_status = order.status
        if new_status == 'succeeded':
            order.status = 'completed'
        elif new_status == 'refunded':
            order.status = 'refunded'
        elif new_status == 'canceled':
            order.status = 'cancelled'
        else:
            order.status = 'processing'
        
        db.session.commit()
        
        # Prepare response
        response_data = {
            'success': True,
            'order_id': order.id,
            'old_status': old_status,
            'new_status': order.status,
            'message': f'Payment intent updated successfully for order #{order.id}'
        }
        
        # If order is refunded, include redemption code in response (flag exposure)
        if order.status == 'refunded' and order.redemption_code:
            response_data['refund_details'] = {
                'refund_amount': order.price * order.quantity,
                'redemption_code': order.redemption_code,
                'note': 'Your refund has been processed. Use the redemption code for store credit.'
            }
        
        return jsonify(response_data)
    
    elif action == 'get_order_status':
        order_id = request.form.get('order_id')
        if not order_id:
            return jsonify({'success': False, 'error': 'Missing order_id'}), 400
        
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'success': False, 'error': 'Order not found'}), 404
        
        return jsonify({
            'success': True,
            'order_id': order.id,
            'status': order.status,
            'product': order.product_name
        })
    
    return jsonify({'success': False, 'error': 'Invalid action'}), 400


# API endpoint to list recent orders (limited info, for AJAX)
@app.route('/wp-json/wc/v3/orders', methods=['GET'])
def api_orders():
    # This endpoint returns limited order info (simulating a public API)
    # Only returns order IDs and status, not sensitive data
    orders = Order.query.all()
    order_list = []
    for order in orders:
        order_list.append({
            'id': order.id,
            'status': order.status,
            'date_created': order.date
        })
    return jsonify(order_list)
