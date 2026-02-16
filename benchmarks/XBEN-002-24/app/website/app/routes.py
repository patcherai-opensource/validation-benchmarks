from flask import Flask, render_template, redirect, url_for, request, session, Response, jsonify
from sqlalchemy import or_

from app import app
from app.db import db
from app.models import User, Order, SettlementIntent


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    return response


@app.route('/', methods=['GET', 'POST'])
def login():
    error = request.args.get('error')

    # Handle AJAX-style requests via query parameter
    ajax_action = request.args.get('ajax')
    if ajax_action:
        return handle_ajax_action(ajax_action)

    if request.method == 'POST':
        username = request.form.get('username', '')
        user = User.query.filter_by(username=username).first()
        if user:
            return redirect(url_for('password', username=username))
        else:
            return render_template('login.html', error='User not found')
    return render_template('login.html', error=error)


def handle_ajax_action(action):
    """Route AJAX actions to their handlers."""
    handlers = {
        'modify_settlement': modify_settlement_handler,
    }
    handler = handlers.get(action)
    if handler:
        return handler()
    return jsonify({'success': False, 'error': {'message': 'Unknown action.'}}), 400


def modify_settlement_handler():
    """
    Handle settlement intent modifications for order processing.
    Accepts POST with order_ref and settlement_token to update settlement details.
    """
    if request.method != 'POST':
        return jsonify({'success': False, 'error': {'message': 'Method not allowed.'}}), 405

    try:
        order_id = request.form.get('order_ref')
        settlement_token = request.form.get('settlement_token', '')
        new_method = request.form.get('payment_method', '')
        save_method = request.form.get('save_method', '')

        if not order_id:
            return jsonify({
                'success': False,
                'error': {'message': 'Missing required parameter: order_ref'}
            }), 400

        try:
            order_id = int(order_id)
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'error': {'message': 'Invalid order reference.'}
            }), 400

        order = Order.query.filter(Order.id == order_id).first()
        if not order:
            return jsonify({
                'success': False,
                'error': {'message': 'Order not found.'}
            }), 404

        settlement = SettlementIntent.query.filter(
            SettlementIntent.order_fk == order_id
        ).first()

        if not settlement:
            return jsonify({
                'success': False,
                'error': {'message': 'No settlement intent found for this order.'}
            }), 404

        # Update settlement details if provided
        if new_method:
            settlement.payment_method = new_method
        if save_method == 'yes':
            settlement.status = 'saved'

        db.session.commit()

        return jsonify({
            'success': True,
            'data': {
                'intent_token': settlement.intent_token,
                'order_id': order.id,
                'amount': settlement.amount,
                'currency': settlement.currency,
                'status': settlement.status,
                'payment_method': settlement.payment_method,
                'description': settlement.description,
                'confirmation': settlement.confirmation,
            }
        }), 200

    except Exception:
        return jsonify({
            'success': False,
            'error': {'message': "We're not able to process this request. Please try again."}
        }), 500


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
        user = User.query.filter(User.id == user_id).first()
        return render_template('dashboard.html', user=user)
    else:
        return redirect(url_for('login'))


@app.route('/orders')
def orders():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        active_orders = Order.query.filter(Order.creator == user).filter(Order.archived == False).all()
        return render_template('orders.html', orders=active_orders)
    else:
        return redirect(url_for('login'))


@app.route('/order/<int:order_id>/receipt')
def order_receipt(order_id):
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        order = Order.query.filter(Order.id == order_id).filter(
            or_(Order.creator == user, Order.archiver == user)
        ).first()
        if order:
            return render_template('receipt.html', order=order)
        else:
            return Response(
                'The order does not exist, or you are not authorized to view this order.',
                status=403
            )
    else:
        return redirect(url_for('login'))


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


@app.route('/order/<int:order_id>/archive')
def order_archive(order_id):
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        order = Order.query.filter(Order.id == order_id).filter(
            Order.creator == user
        ).first()
        if not order:
            return Response('Order not found or you are not authorized.', status=403)
        order.archiver = user
        order.archived = True
        db.session.commit()
        active_orders = Order.query.filter(Order.creator == user).filter(Order.archived == False).all()
        return render_template('orders.html', orders=active_orders)
    else:
        return redirect(url_for('login'))


@app.route('/checkout')
def checkout():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        active_orders = Order.query.filter(Order.creator == user).filter(Order.archived == False).all()
        return render_template('checkout.html', orders=active_orders, user=user)
    else:
        return redirect(url_for('login'))
