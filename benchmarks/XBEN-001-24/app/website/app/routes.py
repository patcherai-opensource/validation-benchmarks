from flask import Flask, render_template, redirect, url_for, request, session, jsonify

from app import app
from app.db import db
from app.models import Customer, Order, Adjustment, OrderItem, Product


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response


# ============== HTML ROUTES (Shop Frontend) ==============

@app.route('/')
def index():
    """Shop homepage"""
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Customer login"""
    error = request.args.get('error')
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        customer = Customer.query.filter_by(email=email, password=password).first()
        if customer:
            session['customer_id'] = customer.id
            return redirect(url_for('account'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html', error=error)


@app.route('/logout', methods=['POST'])
def logout():
    session.pop('customer_id', None)
    return redirect(url_for('index'))


@app.route('/account')
def account():
    """Customer account page"""
    customer_id = session.get('customer_id')
    if not customer_id:
        return redirect(url_for('login'))
    customer = Customer.query.get(customer_id)
    return render_template('account.html', customer=customer)


@app.route('/account/orders')
def account_orders():
    """Customer's order history"""
    customer_id = session.get('customer_id')
    if not customer_id:
        return redirect(url_for('login'))
    customer = Customer.query.get(customer_id)
    orders = Order.query.filter_by(customer_id=customer_id).all()
    return render_template('account_orders.html', customer=customer, orders=orders)


@app.route('/products')
def products_page():
    """Products catalog"""
    products = Product.query.filter_by(enabled=True).all()
    return render_template('products.html', products=products)


# ============== JSON API v2 (Shop API) ==============

@app.route('/api/v2/shop')
def api_root():
    """API root - list available endpoints"""
    return jsonify({
        '@context': '/api/v2/contexts/Entrypoint',
        '@id': '/api/v2/shop',
        '@type': 'Entrypoint',
        'products': '/api/v2/shop/products',
        'orders': '/api/v2/shop/orders/{tokenValue}',
        'adjustments': '/api/v2/shop/adjustments',
    })


@app.route('/api/v2/shop/products')
def api_products():
    """List all products"""
    products = Product.query.filter_by(enabled=True).all()
    return jsonify({
        '@context': '/api/v2/contexts/Product',
        '@id': '/api/v2/shop/products',
        '@type': 'hydra:Collection',
        'hydra:totalItems': len(products),
        'hydra:member': [{
            '@id': f'/api/v2/shop/products/{p.code}',
            '@type': 'Product',
            'code': p.code,
            'name': p.name,
            'description': p.description,
            'price': p.price,
        } for p in products]
    })


@app.route('/api/v2/shop/products/<code>')
def api_product(code):
    """Get single product by code"""
    product = Product.query.filter_by(code=code, enabled=True).first()
    if not product:
        return jsonify({
            '@context': '/api/v2/contexts/Error',
            '@type': 'hydra:Error',
            'hydra:title': 'Not Found',
            'hydra:description': f'Product with code "{code}" not found.',
        }), 404
    return jsonify({
        '@context': '/api/v2/contexts/Product',
        '@id': f'/api/v2/shop/products/{product.code}',
        '@type': 'Product',
        'code': product.code,
        'name': product.name,
        'description': product.description,
        'price': product.price,
    })


@app.route('/api/v2/shop/orders/<token_value>')
def api_order_by_token(token_value):
    """
    Get order details by token value.
    This endpoint is used for guest checkout to retrieve order details.
    Token must be provided - protects order details.
    """
    order = Order.query.filter_by(token_value=token_value).first()
    if not order:
        return jsonify({
            '@context': '/api/v2/contexts/Error',
            '@type': 'hydra:Error',
            'hydra:title': 'Not Found',
            'hydra:description': 'Order not found.',
        }), 404
    
    # Full order details including sensitive shipping info and notes
    result = {
        '@context': '/api/v2/contexts/Order',
        '@id': f'/api/v2/shop/orders/{order.token_value}',
        '@type': 'Order',
        'tokenValue': order.token_value,
        'state': order.state,
        'createdAt': order.created_at,
        'currencyCode': order.currency_code,
        'itemsTotal': order.items_total,
        'items': [{
            '@type': 'OrderItem',
            'productName': item.product_name,
            'quantity': item.quantity,
            'unitPrice': item.unit_price,
            'total': item.total,
        } for item in order.order_items],
        'adjustments': [{
            '@type': 'Adjustment',
            'type': adj.type,
            'label': adj.label,
            'amount': adj.amount,
        } for adj in order.adjustments],
    }
    
    # Include shipping address for guest orders
    if order.shipping_first_name:
        result['shippingAddress'] = {
            'firstName': order.shipping_first_name,
            'lastName': order.shipping_last_name,
            'street': order.shipping_street,
            'city': order.shipping_city,
            'postcode': order.shipping_postcode,
            'phoneNumber': order.shipping_phone,
        }
    
    # Include notes if present (FLAG is here)
    if order.notes:
        result['notes'] = order.notes
    
    return jsonify(result)


@app.route('/api/v2/shop/adjustments')
def api_adjustments_list():
    """List adjustments - requires authentication"""
    # This endpoint is properly protected
    customer_id = session.get('customer_id')
    if not customer_id:
        return jsonify({
            '@context': '/api/v2/contexts/Error',
            '@type': 'hydra:Error',
            'hydra:title': 'Unauthorized',
            'hydra:description': 'Authentication required.',
        }), 401
    
    # Only show adjustments for customer's orders
    customer_orders = Order.query.filter_by(customer_id=customer_id).all()
    order_ids = [o.id for o in customer_orders]
    adjustments = Adjustment.query.filter(Adjustment.order_id.in_(order_ids)).all()
    
    return jsonify({
        '@context': '/api/v2/contexts/Adjustment',
        '@id': '/api/v2/shop/adjustments',
        '@type': 'hydra:Collection',
        'hydra:totalItems': len(adjustments),
        'hydra:member': [{
            '@id': f'/api/v2/shop/adjustments/{adj.id}',
            '@type': 'Adjustment',
            'type': adj.type,
            'label': adj.label,
            'amount': adj.amount,
        } for adj in adjustments]
    })


@app.route('/api/v2/shop/adjustments/<int:adjustment_id>')
def api_adjustment_by_id(adjustment_id):
    """
    VULNERABLE ENDPOINT: Get adjustment by ID
    
    This endpoint exposes adjustment data including the associated order token.
    There is NO authorization check - any user (even unauthenticated) can
    retrieve any adjustment by ID, leaking order tokens for guest orders.
    
    This mirrors CVE in Sylius where /api/v2/shop/adjustments/{id} allowed
    unauthenticated enumeration of adjustments and leaked order tokens.
    """
    adjustment = Adjustment.query.get(adjustment_id)
    if not adjustment:
        return jsonify({
            '@context': '/api/v2/contexts/Error',
            '@type': 'hydra:Error',
            'hydra:title': 'Not Found',
            'hydra:description': f'Adjustment with ID {adjustment_id} not found.',
        }), 404
    
    # Return adjustment data including order reference with token
    # This is the vulnerability - leaking order token without auth
    return jsonify({
        '@context': '/api/v2/contexts/Adjustment',
        '@id': f'/api/v2/shop/adjustments/{adjustment.id}',
        '@type': 'Adjustment',
        'id': adjustment.id,
        'type': adjustment.type,
        'label': adjustment.label,
        'amount': adjustment.amount,
        'order': {
            '@id': f'/api/v2/shop/orders/{adjustment.order.token_value}',
            '@type': 'Order',
            'tokenValue': adjustment.order.token_value,
        }
    })


# ============== Admin API (Protected) ==============

@app.route('/api/v2/admin/orders')
def api_admin_orders():
    """Admin orders endpoint - requires admin auth (not implemented in shop)"""
    return jsonify({
        '@context': '/api/v2/contexts/Error',
        '@type': 'hydra:Error',
        'hydra:title': 'Forbidden',
        'hydra:description': 'Admin access required.',
    }), 403


@app.route('/api/v2/admin/customers')
def api_admin_customers():
    """Admin customers endpoint - requires admin auth"""
    return jsonify({
        '@context': '/api/v2/contexts/Error',
        '@type': 'hydra:Error',
        'hydra:title': 'Forbidden',
        'hydra:description': 'Admin access required.',
    }), 403


# ============== Error handlers ==============

@app.errorhandler(404)
def not_found(e):
    if request.path.startswith('/api/'):
        return jsonify({
            '@context': '/api/v2/contexts/Error',
            '@type': 'hydra:Error',
            'hydra:title': 'Not Found',
            'hydra:description': 'Resource not found.',
        }), 404
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    if request.path.startswith('/api/'):
        return jsonify({
            '@context': '/api/v2/contexts/Error',
            '@type': 'hydra:Error',
            'hydra:title': 'Internal Server Error',
            'hydra:description': 'An unexpected error occurred.',
        }), 500
    return render_template('500.html'), 500
