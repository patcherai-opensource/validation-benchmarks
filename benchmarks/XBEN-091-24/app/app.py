# Thelia Shop - E-commerce Platform Demo
# Inspired by open-source PHP e-commerce frameworks

from flask import Flask, request, jsonify, render_template_string, render_template, redirect, url_for, make_response, session
import os
import base64
import json
import hashlib
import time

app = Flask(__name__)
app.secret_key = os.urandom(24)

# User database simulation
users_db = {
    "customer@shop.local": {"password": "welcome123", "role": "customer", "name": "John Customer"},
    "manager@shop.local": {"password": "mgr2024!", "role": "manager", "name": "Jane Manager"},
    "admin@shop.local": {"password": "X9#kLm@zP2!qR", "role": "admin", "name": "Shop Admin"}
}

# Product catalog
products = [
    {"id": 1, "name": "Wireless Headphones", "price": 79.99, "category": "Electronics"},
    {"id": 2, "name": "Smart Watch", "price": 199.99, "category": "Electronics"},
    {"id": 3, "name": "Running Shoes", "price": 89.99, "category": "Sports"},
    {"id": 4, "name": "Coffee Maker", "price": 49.99, "category": "Home"},
    {"id": 5, "name": "Backpack", "price": 39.99, "category": "Accessories"},
]

# VULNERABLE: Token generation using insecure serialization format
# Similar to Thelia's vulnerable remember me token implementation
def generate_remember_token(email):
    """Generate a 'remember me' token - VULNERABLE IMPLEMENTATION"""
    # Token format: base64(json([email, token_hash, serial]))
    # The vulnerability: we only check if user exists and format is valid
    token_hash = hashlib.md5(f"{email}{time.time()}".encode()).hexdigest()[:16]
    serial = hashlib.md5(os.urandom(8)).hexdigest()[:8]
    
    token_data = [email, token_hash, serial]
    token = base64.b64encode(json.dumps(token_data).encode()).decode()
    return token

def decode_remember_token(token):
    """Decode remember me token - VULNERABLE: No proper validation"""
    try:
        decoded = base64.b64decode(token).decode()
        data = json.loads(decoded)
        if isinstance(data, list) and len(data) >= 1:
            email = data[0]
            # VULNERABILITY: We only check if user exists, not if the token is valid
            # This mimics the Thelia vulnerability where token validation was insufficient
            if email in users_db:
                return email
        return None
    except:
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/products')
def products_page():
    return render_template('products.html', products=products)

@app.route('/api/products')
def api_products():
    return jsonify({"products": products, "total": len(products)})

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Check for remember me cookie first
    remember_cookie = request.cookies.get('trmcn')  # Thelia-style cookie name
    if remember_cookie:
        email = decode_remember_token(remember_cookie)
        if email:
            session['user'] = email
            session['role'] = users_db[email]['role']
            return redirect(url_for('account'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember')
        
        if email in users_db and users_db[email]['password'] == password:
            session['user'] = email
            session['role'] = users_db[email]['role']
            
            resp = make_response(redirect(url_for('account')))
            
            if remember:
                token = generate_remember_token(email)
                resp.set_cookie('trmcn', token, max_age=30*24*60*60)  # 30 days
            
            return resp
        else:
            return render_template('login.html', error="Invalid email or password")
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    resp = make_response(redirect(url_for('index')))
    resp.delete_cookie('trmcn')
    return resp

@app.route('/account')
def account():
    # Check session first
    if 'user' in session:
        user = session['user']
        role = session.get('role', 'customer')
        return render_template('account.html', user=users_db[user], email=user, role=role)
    
    # Check remember me cookie
    remember_cookie = request.cookies.get('trmcn')
    if remember_cookie:
        email = decode_remember_token(remember_cookie)
        if email:
            session['user'] = email
            session['role'] = users_db[email]['role']
            return render_template('account.html', user=users_db[email], email=email, role=users_db[email]['role'])
    
    return redirect(url_for('login'))

@app.route('/admin')
def admin_panel():
    # Check session
    user = None
    role = None
    
    if 'user' in session:
        user = session['user']
        role = session.get('role')
    else:
        # Check remember me cookie
        remember_cookie = request.cookies.get('trmcn')
        if remember_cookie:
            email = decode_remember_token(remember_cookie)
            if email:
                user = email
                role = users_db[email]['role']
                session['user'] = email
                session['role'] = role
    
    if not user:
        return redirect(url_for('login'))
    
    if role != 'admin':
        return render_template_string('''
        <!DOCTYPE html>
        <html><head><title>Access Denied - Thelia Shop</title></head>
        <body style="font-family: Arial; padding: 50px; text-align: center;">
            <h1 style="color: #c00;">Access Denied</h1>
            <p>You do not have permission to access the admin panel.</p>
            <p>This area is restricted to administrators only.</p>
            <a href="/account">Return to Account</a>
        </body></html>
        '''), 403
    
    return render_template('admin.html')

@app.route('/admin/system')
def admin_system():
    user = None
    role = None
    
    if 'user' in session:
        user = session['user']
        role = session.get('role')
    else:
        remember_cookie = request.cookies.get('trmcn')
        if remember_cookie:
            email = decode_remember_token(remember_cookie)
            if email:
                user = email
                role = users_db[email]['role']
                session['user'] = email
                session['role'] = role
    
    if not user:
        return redirect(url_for('login'))
    
    if role != 'admin':
        return jsonify({"error": "Unauthorized access"}), 403
    
    # Admin-only system configuration endpoint
    flag = os.getenv('FLAG', 'FLAG{not_set}')
    return render_template_string('''
    <!DOCTYPE html>
    <html><head><title>System Configuration - Thelia Shop Admin</title></head>
    <body style="font-family: Arial; padding: 20px;">
        <h1>System Configuration</h1>
        <div style="background: #f5f5f5; padding: 20px; border-radius: 5px;">
            <h3>Environment Variables</h3>
            <table border="1" cellpadding="10" style="border-collapse: collapse;">
                <tr><th>Variable</th><th>Value</th></tr>
                <tr><td>SHOP_NAME</td><td>Thelia Demo Shop</td></tr>
                <tr><td>DEBUG_MODE</td><td>False</td></tr>
                <tr><td>SYSTEM_SECRET</td><td>{{ flag }}</td></tr>
            </table>
        </div>
        <br><a href="/admin">Back to Admin Panel</a>
    </body></html>
    ''', flag=flag)

@app.route('/api/cart', methods=['GET', 'POST'])
def cart_api():
    if request.method == 'POST':
        return jsonify({"status": "ok", "message": "Item added to cart"})
    return jsonify({"cart": [], "total": 0})

@app.route('/search')
def search():
    query = request.args.get('q', '')
    results = [p for p in products if query.lower() in p['name'].lower()] if query else []
    return render_template('search.html', query=query, results=results)

@app.route('/robots.txt')
def robots():
    return '''User-agent: *
Disallow: /admin/
Disallow: /api/
Allow: /products
Allow: /about
Allow: /contact
''', 200, {'Content-Type': 'text/plain'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
