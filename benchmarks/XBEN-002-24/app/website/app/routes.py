from flask import Flask, render_template, render_template_string, redirect, url_for, request, session, Response, jsonify

from app import app
from app.db import db
from app.models import User, Order


@app.after_request
def add_header(request):
    request.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    request.headers['Pragma'] = 'no-cache'
    request.headers['Expires'] = '0'
    request.headers['Cache-Control'] = 'public, max-age=0'
    return request


# Homepage - redirect to login or dashboard
@app.route('/')
def index():
    user_id = session.get('user_id')
    if user_id:
        return redirect(url_for('my_orders'))
    return redirect(url_for('login'))


# Route for login page
@app.route('/account/login', methods=['GET', 'POST'])
def login():
    error = request.args.get('error')
    if request.method == 'POST':
        username = request.form['username']
        # Check if username exists
        user = User.query.filter_by(username=username).first()
        if user:
            # Redirect to password page if username exists
            return redirect(url_for('password', username=username))
        else:
            # Render login page with error message if username doesn't exist
            return render_template('login.html', error='Account not found')
    return render_template('login.html', error=error)


# Route for logout
@app.route('/account/logout', methods=['POST'])
def logout():
    # Clear user ID from session
    session.pop('user_id', None)
    return redirect(url_for('login'))


# Route for password page
@app.route('/account/password/<username>', methods=['GET', 'POST'])
def password(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        # Render login page with error message if username doesn't exist
        return redirect(url_for('login', error='Account not found'))

    if request.method == 'POST':
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            # User provided a valid username/password pair.
            session['user_id'] = user.id

            # If login successful, redirect to orders page
            return redirect(url_for('my_orders'))
        else:
            # Render login page with error message if password is incorrect
            return redirect(url_for('login', error='Incorrect password'))
    # Render password page for GET request
    return render_template('password.html', first_name=user.first_name, username=username, user_id=user.id)


# Route for my orders page
@app.route('/my-orders')
def my_orders():
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        user_orders = Order.query.filter(Order.creator == user).all()
        return render_template('orders.html', orders=user_orders, user=user)
    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))


# Route for viewing order confirmation (requires confirmed status)
@app.route('/order/<int:order_id>/confirmation')
def order_confirmation(order_id):
    # Retrieve user from session
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        # Check that user owns this order
        order = Order.query.filter(Order.id == order_id).filter(Order.creator == user).first()
        if order:
            if order.status == 'confirmed':
                return render_template('confirmation.html', order=order)
            else:
                return Response('Payment not yet confirmed for this order. Status: ' + order.status, status=400)
        else:
            return Response('Order not found or you do not have permission to view this order.', status=403)
    else:
        # If user not in session, redirect to login
        return redirect(url_for('login'))


# AJAX endpoint for updating payment intent status
# This endpoint simulates the WooCommerce Stripe payment gateway AJAX handler
# VULNERABILITY: No authentication required, no ownership verification
# An attacker can update any order's status by guessing/enumerating order IDs
@app.route('/', methods=['POST'])
def wc_ajax_handler():
    # Check if this is a wc-ajax request (simulating WooCommerce AJAX pattern)
    wc_ajax = request.args.get('wc-ajax')
    
    if wc_ajax == 'update_order_status':
        # Get order_id and payment_intent from POST data
        # VULNERABILITY: No authentication check - any request can update orders
        # VULNERABILITY: No ownership verification - can update ANY order by ID
        order_id = request.form.get('order_id')
        payment_intent = request.form.get('payment_intent_id')
        new_status = request.form.get('status', 'confirmed')
        customer_id = request.form.get('customer_id')
        
        if not order_id:
            return jsonify({'success': False, 'error': 'Missing order_id parameter'}), 400
        
        # Find the order by ID without any authorization check
        order = Order.query.filter(Order.id == order_id).first()
        
        if not order:
            return jsonify({'success': False, 'error': 'Order not found'}), 404
        
        # Update the order status without verifying ownership
        if payment_intent:
            order.payment_intent = payment_intent
        order.status = new_status
        
        # VULNERABILITY: Can reassign order to different customer
        if customer_id:
            order.creator_fk = customer_id
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Order status updated',
            'order_id': order.id,
            'new_status': order.status
        })
    
    # Unknown wc-ajax action
    return jsonify({'success': False, 'error': 'Unknown action'}), 400


# API endpoint to get order details (for AJAX calls)
@app.route('/api/order/<int:order_id>')
def api_order_details(order_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    user = User.query.filter(User.id == user_id).first()
    order = Order.query.filter(Order.id == order_id).filter(Order.creator == user).first()
    
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    return jsonify({
        'id': order.id,
        'date': order.date,
        'product_name': order.product_name,
        'status': order.status,
        'quantity': order.quantity,
        'price': order.price,
        'payment_intent': order.payment_intent
    })
