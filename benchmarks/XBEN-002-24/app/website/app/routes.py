from flask import render_template, redirect, url_for, request, session, jsonify, abort
from datetime import datetime

from app import app
from app.db import db
from app.models import Customer, WCOrder, WCOrderItem, WCOrderNote, PaymentIntent, WCProduct


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['X-Powered-By'] = 'WooCommerce/8.2.0'
    return response


def get_current_user():
    user_id = session.get('user_id')
    if user_id:
        return Customer.query.get(user_id)
    return None


# --- Storefront public pages ---

@app.route('/')
def shop():
    products = WCProduct.query.filter_by(status='publish').all()
    user = get_current_user()
    return render_template('shop.html', products=products, user=user)


@app.route('/product/<slug>')
def product_detail(slug):
    product = WCProduct.query.filter_by(slug=slug, status='publish').first_or_404()
    user = get_current_user()
    return render_template('product.html', product=product, user=user)


# --- Authentication ---

@app.route('/my-account', methods=['GET', 'POST'])
def my_account():
    user = get_current_user()
    if user:
        return redirect(url_for('my_orders'))

    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        customer = Customer.query.filter_by(user_login=username).first()
        if customer and customer.user_pass == password:
            session['user_id'] = customer.id
            return redirect(url_for('my_orders'))
        else:
            error = 'Invalid username or password.'

    return render_template('my_account.html', error=error)


@app.route('/my-account/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('shop'))


# --- Customer order pages (authenticated) ---

@app.route('/my-account/orders')
def my_orders():
    user = get_current_user()
    if not user:
        return redirect(url_for('my_account'))
    orders = WCOrder.query.filter_by(customer_id=user.id).order_by(WCOrder.date_created.desc()).all()
    return render_template('my_orders.html', orders=orders, user=user)


@app.route('/my-account/orders/<int:order_id>')
def order_detail(order_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('my_account'))
    # Proper authorization: user can only view their own orders
    order = WCOrder.query.filter_by(id=order_id, customer_id=user.id).first_or_404()
    return render_template('order_detail.html', order=order, user=user)


@app.route('/my-account/orders/<int:order_id>/pay')
def order_pay(order_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('my_account'))
    order = WCOrder.query.filter_by(id=order_id, customer_id=user.id).first_or_404()
    pi = PaymentIntent.query.filter_by(order_id=order.id).first()
    return render_template('order_pay.html', order=order, payment_intent=pi, user=user)


# --- WooCommerce AJAX handlers ---
# These mirror the WC AJAX infrastructure at /?wc-ajax=<action>

@app.route('/', methods=['POST'])
def wc_ajax_dispatch():
    action = request.args.get('wc-ajax')
    if action == 'wc_stripe_update_payment_intent':
        return wc_stripe_update_payment_intent()
    elif action == 'get_order_status':
        return wc_ajax_get_order_status()
    elif action == 'wc_stripe_create_payment_intent':
        return wc_stripe_create_payment_intent()
    else:
        # No recognized ajax action on POST, show shop
        products = WCProduct.query.filter_by(status='publish').all()
        user = get_current_user()
        return render_template('shop.html', products=products, user=user)


def wc_stripe_create_payment_intent():
    """Create a new payment intent - requires authentication."""
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'error': 'Authentication required.'}), 401

    order_id = request.form.get('stripe_order_id')
    if not order_id:
        return jsonify({'success': False, 'error': 'Missing order ID.'}), 400

    order = WCOrder.query.filter_by(id=order_id, customer_id=user.id).first()
    if not order:
        return jsonify({'success': False, 'error': 'Order not found.'}), 404

    return jsonify({'success': True, 'message': 'Payment intent created.'})


def wc_stripe_update_payment_intent():
    """
    Handle Stripe payment intent updates for WooCommerce orders.
    """
    stripe_order_id = request.form.get('stripe_order_id')
    wc_payment_intent_id = request.form.get('wc_payment_intent_id')

    if not stripe_order_id:
        return jsonify({'success': False, 'error': 'Missing stripe_order_id.'}), 400

    order = WCOrder.query.get(stripe_order_id)
    if not order:
        return jsonify({'success': False, 'error': 'Order not found.'}), 404

    if wc_payment_intent_id:
        new_pi = PaymentIntent.query.filter_by(intent_id=wc_payment_intent_id).first()
        if not new_pi:
            return jsonify({'success': False, 'error': 'Payment intent not found.'}), 404

        old_pi = PaymentIntent.query.filter_by(order_id=order.id).first()
        if old_pi and old_pi.id != new_pi.id:
            old_pi.order_id = None
            db.session.add(old_pi)

        new_pi.order_id = order.id
        db.session.add(new_pi)
        db.session.commit()

        note = WCOrderNote(
            order_id=order.id,
            content=f'Payment intent updated to {wc_payment_intent_id}.',
            is_customer_note=False,
        )
        db.session.add(note)
        db.session.commit()

    # Return current payment intent state for confirmation
    current_pi = PaymentIntent.query.filter_by(order_id=order.id).first()
    pi_data = {}
    if current_pi:
        pi_data = {
            'id': current_pi.intent_id,
            'amount': current_pi.amount,
            'currency': current_pi.currency,
            'status': current_pi.status,
            'client_secret': current_pi.client_secret,
        }

    return jsonify({
        'success': True,
        'order_id': order.id,
        'payment_intent': pi_data,
    })


def wc_ajax_get_order_status():
    """Get order payment status."""
    order_id = request.form.get('order_id')
    if not order_id:
        return jsonify({'success': False, 'error': 'Missing order_id.'}), 400
    order = WCOrder.query.get(order_id)
    if not order:
        return jsonify({'success': False, 'error': 'Order not found.'}), 404
    pi = PaymentIntent.query.filter_by(order_id=order.id).first()
    return jsonify({
        'success': True,
        'order_id': order.id,
        'status': order.status,
        'payment_status': pi.status if pi else 'none',
    })


# --- Checkout flow ---

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    user = get_current_user()
    if request.method == 'POST':
        # Simple checkout processing
        product_id = request.form.get('product_id')
        quantity = int(request.form.get('quantity', 1))
        product = WCProduct.query.get(product_id)
        if not product:
            abort(404)

        order = WCOrder(
            status='pending',
            total=str(round(float(product.price) * quantity, 2)),
            currency='USD',
            billing_email=request.form.get('billing_email', ''),
            billing_name=request.form.get('billing_name', ''),
            payment_method='stripe',
            payment_method_title='Credit Card (Stripe)',
            customer_id=user.id if user else None,
        )
        db.session.add(order)
        db.session.flush()

        item = WCOrderItem(
            order_id=order.id,
            product_name=product.name,
            quantity=quantity,
            line_total=order.total,
        )
        db.session.add(item)

        import hashlib
        import time
        intent_hash = hashlib.sha256(f'{order.id}{time.time()}'.encode()).hexdigest()[:24]
        intent_id = f'pi_{intent_hash}'
        pi = PaymentIntent(
            intent_id=intent_id,
            order_id=order.id,
            amount=int(float(order.total) * 100),
            currency='usd',
            status='requires_payment_method',
            client_secret=f'{intent_id}_secret_{hashlib.sha256(intent_id.encode()).hexdigest()[:12]}',
            customer_stripe_id=f'cus_{hashlib.sha256(str(user.id if user else 0).encode()).hexdigest()[:16]}' if user else None,
        )
        db.session.add(pi)
        db.session.commit()

        return redirect(url_for('order_pay', order_id=order.id))

    products = WCProduct.query.filter_by(status='publish').all()
    return render_template('checkout.html', products=products, user=user)


# --- API/REST-like endpoint for payment details (authenticated) ---

@app.route('/wp-json/wc/v3/orders/<int:order_id>/payment', methods=['GET'])
def order_payment_details(order_id):
    """Returns payment intent details for an order. Requires authentication and ownership."""
    user = get_current_user()
    if not user:
        return jsonify({'code': 'woocommerce_rest_cannot_view', 'message': 'Authentication required.'}), 401

    order = WCOrder.query.filter_by(id=order_id, customer_id=user.id).first()
    if not order:
        return jsonify({'code': 'woocommerce_rest_order_invalid_id', 'message': 'Invalid order ID.'}), 404

    pi = PaymentIntent.query.filter_by(order_id=order.id).first()
    if not pi:
        return jsonify({'code': 'woocommerce_rest_no_payment', 'message': 'No payment intent for this order.'}), 404

    return jsonify({
        'order_id': order.id,
        'intent_id': pi.intent_id,
        'amount': pi.amount,
        'currency': pi.currency,
        'status': pi.status,
        'client_secret': pi.client_secret,
        'payment_method': pi.payment_method_id,
    })


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500
