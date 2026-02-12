# encoding=utf8

from flask import Flask, request, make_response, redirect, render_template_string
import subprocess
import os
import re
import sys
import time
import logging
import cgi

logging.basicConfig(level=logging.WARNING)

reload(sys)
sys.setdefaultencoding('utf8')

flag = open('secret.txt').read().strip()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False

# In-memory store for product reviews (simulates database)
product_reviews = {}
review_counter = [0]

# Enumerated list of known dangerous event attributes
# This mirrors PrestaShop's Validate::isCleanHtml approach prior to the fix:
# only specific known event names are matched, not a generic on* pattern
BLOCKED_EVENT_ATTRS = [
    'onabort', 'onactivate', 'onafterprint', 'onafterupdate',
    'onbeforeactivate', 'onbeforecopy', 'onbeforecut', 'onbeforedeactivate',
    'onbeforeeditfocus', 'onbeforepaste', 'onbeforeprint', 'onbeforeunload',
    'onbeforeupdate', 'onblur', 'onbounce', 'oncellchange', 'onchange',
    'onclick', 'oncontextmenu', 'oncontrolselect', 'oncopy', 'oncut',
    'ondataavailable', 'ondatasetchanged', 'ondatasetcomplete',
    'ondblclick', 'ondeactivate', 'ondrag', 'ondragend', 'ondragenter',
    'ondragleave', 'ondragover', 'ondragstart', 'ondrop',
    'onerror', 'onerrorupdate',
    'onfilterchange', 'onfinish', 'onfocus',
    'onhashchange', 'onhelp', 'oninput', 'onkeydown', 'onkeypress',
    'onkeyup', 'onlayoutcomplete', 'onload', 'onlosecapture',
    'onmessage', 'onmousedown', 'onmouseenter', 'onmouseleave',
    'onmousemove', 'onmouseout', 'onmouseover', 'onmouseup', 'onmousewheel',
    'onmove', 'onmoveend', 'onmovestart',
    'onoffline', 'ononline', 'onpageshow', 'onpagehide',
    'onpaste', 'onpopstate', 'onprogress',
    'onpropertychange', 'onreadystatechange', 'onreset', 'onresize',
    'onresizeend', 'onresizestart', 'onrowenter', 'onrowexit',
    'onrowsdelete', 'onrowsinserted', 'onscroll', 'onselect',
    'onselectionchange', 'onselectstart', 'onstart', 'onstop',
    'onstorage', 'onsubmit',
    'ontimeupdate', 'onunload'
]


def is_clean_html(html_content):
    """
    Validates that HTML content does not contain dangerous elements.
    Mirrors PrestaShop's Validate::isCleanHtml methodology.
    """
    if not html_content:
        return True

    # Block <script> tags
    if re.search(r'<\s*script', html_content, re.IGNORECASE):
        return False

    # Block javascript: protocol in attributes
    if re.search(r'javascript\s*:', html_content, re.IGNORECASE):
        return False

    # Block known dangerous event attributes (enumerated list)
    for attr in BLOCKED_EVENT_ATTRS:
        pattern = r'\b' + re.escape(attr) + r'\s*='
        if re.search(pattern, html_content, re.IGNORECASE):
            return False

    # Block <iframe>, <object>, <embed>, <applet>, <form>
    if re.search(r'<\s*(iframe|object|embed|applet|form)\b', html_content, re.IGNORECASE):
        return False

    # Block data: URIs in src/href
    if re.search(r'(src|href)\s*=\s*["\']?\s*data:', html_content, re.IGNORECASE):
        return False

    return True


def render_xss_check(html_content):
    """Verify rendered content using headless browser."""
    proc = subprocess.Popen(
        ["timeout", "5", "phantomjs", "check.js"],
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE
    )
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://localhost:5000/' + fn
    result = ''
    try:
        of = open(fn, 'w')
        of.write(html_content)
        of.close()
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
    finally:
        try:
            os.unlink(fn)
        except:
            pass
    return result


# ==================== Routes ====================

@app.route('/')
def index():
    categories = [
        {'id': 1, 'name': 'Electronics', 'count': 24},
        {'id': 2, 'name': 'Clothing', 'count': 56},
        {'id': 3, 'name': 'Home & Garden', 'count': 31},
        {'id': 4, 'name': 'Sports', 'count': 18},
    ]
    products = [
        {'id': 101, 'name': 'Wireless Headphones', 'price': '49.99', 'category': 'Electronics'},
        {'id': 102, 'name': 'Cotton T-Shirt', 'price': '19.99', 'category': 'Clothing'},
        {'id': 103, 'name': 'Garden Tool Set', 'price': '34.99', 'category': 'Home & Garden'},
        {'id': 104, 'name': 'Yoga Mat', 'price': '24.99', 'category': 'Sports'},
        {'id': 105, 'name': 'Bluetooth Speaker', 'price': '39.99', 'category': 'Electronics'},
        {'id': 106, 'name': 'Running Shoes', 'price': '79.99', 'category': 'Sports'},
    ]
    return render_template_string(STORE_INDEX, categories=categories, products=products)


@app.route('/product/<int:product_id>')
def product_detail(product_id):
    products_db = {
        101: {'id': 101, 'name': 'Wireless Headphones', 'price': '49.99', 'category': 'Electronics', 'description': 'Premium wireless headphones with noise cancellation and 30-hour battery life.', 'sku': 'WH-NC300', 'stock': 45},
        102: {'id': 102, 'name': 'Cotton T-Shirt', 'price': '19.99', 'category': 'Clothing', 'description': '100% organic cotton t-shirt. Available in multiple colors.', 'sku': 'CT-ORG100', 'stock': 120},
        103: {'id': 103, 'name': 'Garden Tool Set', 'price': '34.99', 'category': 'Home & Garden', 'description': '5-piece stainless steel garden tool set with ergonomic handles.', 'sku': 'GT-SS500', 'stock': 33},
        104: {'id': 104, 'name': 'Yoga Mat', 'price': '24.99', 'category': 'Sports', 'description': 'Non-slip yoga mat, 6mm thick, eco-friendly materials.', 'sku': 'YM-ECO6', 'stock': 78},
        105: {'id': 105, 'name': 'Bluetooth Speaker', 'price': '39.99', 'category': 'Electronics', 'description': 'Portable waterproof Bluetooth speaker with 12-hour playtime.', 'sku': 'BS-WP120', 'stock': 62},
        106: {'id': 106, 'name': 'Running Shoes', 'price': '79.99', 'category': 'Sports', 'description': 'Lightweight running shoes with responsive cushioning.', 'sku': 'RS-LW200', 'stock': 29},
    }

    product = products_db.get(product_id)
    if not product:
        return render_template_string(ERROR_404), 404

    reviews = product_reviews.get(product_id, [])
    return render_template_string(PRODUCT_PAGE, product=product, reviews=reviews)


@app.route('/product/<int:product_id>/review', methods=['POST'])
def submit_review(product_id):
    author = request.form.get('author', 'Anonymous')
    content = request.form.get('content', '')
    rating = request.form.get('rating', '5')

    if not content.strip():
        return redirect('/product/%d?error=empty' % product_id)

    # Validate content using isCleanHtml approach
    if not is_clean_html(content) or not is_clean_html(author):
        return redirect('/product/%d?error=invalid_html' % product_id)

    # Validate rating
    try:
        rating_val = int(rating)
        if rating_val < 1 or rating_val > 5:
            rating_val = 5
    except:
        rating_val = 5

    # Sanitize author more strictly - plain text only
    author = re.sub(r'<[^>]*>', '', author)

    review_counter[0] += 1
    review = {
        'id': review_counter[0],
        'author': author,
        'content': content,
        'rating': rating_val,
        'date': time.strftime('%Y-%m-%d %H:%M'),
    }

    if product_id not in product_reviews:
        product_reviews[product_id] = []
    product_reviews[product_id].append(review)

    return redirect('/product/%d?success=1' % product_id)


@app.route('/product/<int:product_id>/reviews')
def view_reviews(product_id):
    """Render all reviews for a product."""
    reviews = product_reviews.get(product_id, [])

    products_db = {
        101: 'Wireless Headphones', 102: 'Cotton T-Shirt',
        103: 'Garden Tool Set', 104: 'Yoga Mat',
        105: 'Bluetooth Speaker', 106: 'Running Shoes',
    }
    product_name = products_db.get(product_id, 'Unknown Product')

    # Build the page with reviews rendered
    reviews_html = ''
    for r in reviews:
        stars = '&#9733;' * r['rating'] + '&#9734;' * (5 - r['rating'])
        reviews_html += '<div class="review-item">'
        reviews_html += '<div class="review-header">'
        reviews_html += '<span class="review-author">%s</span>' % cgi.escape(r['author'])
        reviews_html += '<span class="review-rating">%s</span>' % stars
        reviews_html += '<span class="review-date">%s</span>' % r['date']
        reviews_html += '</div>'
        reviews_html += '<div class="review-content">%s</div>' % r['content']
        reviews_html += '</div>'

    page_html = REVIEWS_PAGE.replace('{{PRODUCT_NAME}}', cgi.escape(product_name))
    page_html = page_html.replace('{{PRODUCT_ID}}', str(product_id))
    page_html = page_html.replace('{{REVIEWS_HTML}}', reviews_html)

    # Content verification check
    result = render_xss_check(page_html)

    if result == 'XSS':
        page_html = page_html.replace('</body>', '<div class="alert-success">Content verification token: %s</div></body>' % flag)

    return page_html


@app.route('/categories')
def categories():
    return render_template_string(CATEGORIES_PAGE)


@app.route('/about')
def about():
    return render_template_string(ABOUT_PAGE)


@app.route('/search')
def search():
    q = request.args.get('q', '')
    return render_template_string(SEARCH_PAGE, query=q, results=[])


# ==================== Templates ====================

STORE_INDEX = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ShopDemo - Online Store</title>
    <link rel="shortcut icon" href="/static/assets/fav-icon.png">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color: #333; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 15px 0; }
        .header-inner { max-width: 1200px; margin: 0 auto; padding: 0 20px; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { font-size: 24px; }
        .header nav a { color: #ecf0f1; text-decoration: none; margin-left: 20px; font-size: 14px; }
        .header nav a:hover { color: #3498db; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .search-bar { margin: 20px 0; }
        .search-bar form { display: flex; }
        .search-bar input[type="text"] { flex: 1; padding: 10px 15px; border: 1px solid #ddd; border-radius: 4px 0 0 4px; font-size: 14px; }
        .search-bar button { padding: 10px 20px; background: #3498db; color: white; border: none; border-radius: 0 4px 4px 0; cursor: pointer; }
        .categories { display: flex; gap: 15px; margin: 20px 0; flex-wrap: wrap; }
        .category-card { background: white; border-radius: 8px; padding: 20px; flex: 1; min-width: 150px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .category-card h3 { font-size: 16px; margin-bottom: 5px; }
        .category-card span { color: #7f8c8d; font-size: 13px; }
        .products-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 20px; margin: 20px 0; }
        .product-card { background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1); transition: transform 0.2s; }
        .product-card:hover { transform: translateY(-2px); }
        .product-card .img-placeholder { height: 180px; background: #ecf0f1; display: flex; align-items: center; justify-content: center; color: #95a5a6; }
        .product-card .info { padding: 15px; }
        .product-card .info h3 { font-size: 16px; margin-bottom: 8px; }
        .product-card .info .price { color: #e74c3c; font-weight: bold; font-size: 18px; }
        .product-card .info .category { color: #7f8c8d; font-size: 12px; margin-top: 5px; }
        .product-card a { text-decoration: none; color: inherit; }
        .footer { background: #2c3e50; color: #ecf0f1; text-align: center; padding: 20px; margin-top: 40px; font-size: 13px; }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-inner">
            <h1>ShopDemo</h1>
            <nav>
                <a href="/">Home</a>
                <a href="/categories">Categories</a>
                <a href="/about">About</a>
            </nav>
        </div>
    </div>
    <div class="container">
        <div class="search-bar">
            <form action="/search" method="get">
                <input type="text" name="q" placeholder="Search products...">
                <button type="submit">Search</button>
            </form>
        </div>
        <h2>Categories</h2>
        <div class="categories">
            {% for cat in categories %}
            <div class="category-card">
                <h3>{{ cat.name }}</h3>
                <span>{{ cat.count }} products</span>
            </div>
            {% endfor %}
        </div>
        <h2>Featured Products</h2>
        <div class="products-grid">
            {% for p in products %}
            <div class="product-card">
                <a href="/product/{{ p.id }}">
                    <div class="img-placeholder">Product Image</div>
                    <div class="info">
                        <h3>{{ p.name }}</h3>
                        <div class="price">${{ p.price }}</div>
                        <div class="category">{{ p.category }}</div>
                    </div>
                </a>
            </div>
            {% endfor %}
        </div>
    </div>
    <div class="footer">
        <p>&copy; 2024 ShopDemo. All rights reserved.</p>
    </div>
</body>
</html>"""

PRODUCT_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ product.name }} - ShopDemo</title>
    <link rel="shortcut icon" href="/static/assets/fav-icon.png">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color: #333; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 15px 0; }
        .header-inner { max-width: 1200px; margin: 0 auto; padding: 0 20px; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { font-size: 24px; }
        .header nav a { color: #ecf0f1; text-decoration: none; margin-left: 20px; font-size: 14px; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .breadcrumb { margin-bottom: 20px; font-size: 13px; color: #7f8c8d; }
        .breadcrumb a { color: #3498db; text-decoration: none; }
        .product-detail { display: flex; gap: 30px; background: white; border-radius: 8px; padding: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .product-image { flex: 0 0 400px; height: 350px; background: #ecf0f1; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #95a5a6; }
        .product-info { flex: 1; }
        .product-info h2 { margin-bottom: 10px; font-size: 24px; }
        .product-info .price { color: #e74c3c; font-size: 28px; font-weight: bold; margin-bottom: 15px; }
        .product-info .description { color: #555; line-height: 1.6; margin-bottom: 20px; }
        .product-info .meta { font-size: 13px; color: #7f8c8d; }
        .product-info .meta span { margin-right: 20px; }
        .btn { display: inline-block; padding: 12px 25px; background: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; text-decoration: none; }
        .btn:hover { background: #2980b9; }
        .reviews-section { margin-top: 30px; background: white; border-radius: 8px; padding: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .reviews-section h3 { margin-bottom: 20px; font-size: 20px; }
        .review-form { margin-top: 20px; }
        .review-form label { display: block; margin-bottom: 5px; font-weight: 600; font-size: 14px; }
        .review-form input[type="text"], .review-form textarea, .review-form select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; margin-bottom: 15px; font-family: inherit; font-size: 14px; }
        .review-form textarea { min-height: 100px; resize: vertical; }
        .review-item { border-bottom: 1px solid #eee; padding: 15px 0; }
        .review-header { display: flex; gap: 15px; align-items: center; margin-bottom: 8px; }
        .review-author { font-weight: 600; }
        .review-rating { color: #f39c12; }
        .review-date { color: #95a5a6; font-size: 12px; }
        .review-content { color: #555; line-height: 1.5; }
        .alert { padding: 12px 15px; border-radius: 4px; margin-bottom: 15px; font-size: 14px; }
        .alert-error { background: #fee; border: 1px solid #fcc; color: #c33; }
        .alert-success { background: #efe; border: 1px solid #cfc; color: #363; }
        .footer { background: #2c3e50; color: #ecf0f1; text-align: center; padding: 20px; margin-top: 40px; font-size: 13px; }
        .help-text { font-size: 12px; color: #95a5a6; margin-top: -10px; margin-bottom: 15px; }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-inner">
            <h1>ShopDemo</h1>
            <nav>
                <a href="/">Home</a>
                <a href="/categories">Categories</a>
                <a href="/about">About</a>
            </nav>
        </div>
    </div>
    <div class="container">
        <div class="breadcrumb">
            <a href="/">Home</a> &raquo; <a href="/categories">{{ product.category }}</a> &raquo; {{ product.name }}
        </div>
        <div class="product-detail">
            <div class="product-image">Product Image</div>
            <div class="product-info">
                <h2>{{ product.name }}</h2>
                <div class="price">${{ product.price }}</div>
                <div class="description">{{ product.description }}</div>
                <div class="meta">
                    <span>SKU: {{ product.sku }}</span>
                    <span>Stock: {{ product.stock }} available</span>
                    <span>Category: {{ product.category }}</span>
                </div>
                <br>
                <a class="btn" href="#">Add to Cart</a>
            </div>
        </div>

        <div class="reviews-section">
            <h3>Customer Reviews ({{ reviews|length }})</h3>
            {% if request.args.get('error') == 'empty' %}
            <div class="alert alert-error">Review content cannot be empty.</div>
            {% elif request.args.get('error') == 'invalid_html' %}
            <div class="alert alert-error">Your review contains content that is not allowed. Please remove any scripts or dangerous HTML.</div>
            {% elif request.args.get('success') %}
            <div class="alert alert-success">Your review has been submitted. <a href="/product/{{ product.id }}/reviews">View all reviews</a></div>
            {% endif %}

            {% for review in reviews %}
            <div class="review-item">
                <div class="review-header">
                    <span class="review-author">{{ review.author }}</span>
                    <span class="review-rating">{{ '&#9733;' * review.rating }}{{ '&#9734;' * (5 - review.rating) }}</span>
                    <span class="review-date">{{ review.date }}</span>
                </div>
                <div class="review-content">{{ review.content }}</div>
            </div>
            {% endfor %}

            <a href="/product/{{ product.id }}/reviews" class="btn" style="margin-top:10px;background:#27ae60;">View All Reviews</a>

            <div class="review-form">
                <h4>Write a Review</h4>
                <form method="post" action="/product/{{ product.id }}/review">
                    <label for="author">Your Name</label>
                    <input type="text" id="author" name="author" placeholder="Your name" required>

                    <label for="rating">Rating</label>
                    <select id="rating" name="rating">
                        <option value="5">&#9733;&#9733;&#9733;&#9733;&#9733; (5)</option>
                        <option value="4">&#9733;&#9733;&#9733;&#9733;&#9734; (4)</option>
                        <option value="3">&#9733;&#9733;&#9733;&#9734;&#9734; (3)</option>
                        <option value="2">&#9733;&#9733;&#9734;&#9734;&#9734; (2)</option>
                        <option value="1">&#9733;&#9734;&#9734;&#9734;&#9734; (1)</option>
                    </select>

                    <label for="content">Review</label>
                    <textarea id="content" name="content" placeholder="Share your experience with this product..."></textarea>
                    <p class="help-text">Basic HTML formatting is allowed (bold, italic, links). Dangerous content will be rejected.</p>

                    <button type="submit" class="btn">Submit Review</button>
                </form>
            </div>
        </div>
    </div>
    <div class="footer">
        <p>&copy; 2024 ShopDemo. All rights reserved.</p>
    </div>
</body>
</html>"""

REVIEWS_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reviews - {{PRODUCT_NAME}} - ShopDemo</title>
    <link rel="shortcut icon" href="/static/assets/fav-icon.png">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color: #333; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 15px 0; }
        .header-inner { max-width: 1200px; margin: 0 auto; padding: 0 20px; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { font-size: 24px; }
        .header nav a { color: #ecf0f1; text-decoration: none; margin-left: 20px; font-size: 14px; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .breadcrumb { margin-bottom: 20px; font-size: 13px; color: #7f8c8d; }
        .breadcrumb a { color: #3498db; text-decoration: none; }
        .reviews-section { background: white; border-radius: 8px; padding: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .reviews-section h3 { margin-bottom: 20px; font-size: 20px; }
        .review-item { border-bottom: 1px solid #eee; padding: 15px 0; }
        .review-header { display: flex; gap: 15px; align-items: center; margin-bottom: 8px; }
        .review-author { font-weight: 600; }
        .review-rating { color: #f39c12; }
        .review-date { color: #95a5a6; font-size: 12px; }
        .review-content { color: #555; line-height: 1.5; }
        .btn { display: inline-block; padding: 12px 25px; background: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; text-decoration: none; }
        .empty-reviews { text-align: center; color: #95a5a6; padding: 40px; }
        .footer { background: #2c3e50; color: #ecf0f1; text-align: center; padding: 20px; margin-top: 40px; font-size: 13px; }
        .alert-success { background: #28a745; color: #fff; padding: 15px; margin: 15px 0; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-inner">
            <h1>ShopDemo</h1>
            <nav>
                <a href="/">Home</a>
                <a href="/categories">Categories</a>
                <a href="/about">About</a>
            </nav>
        </div>
    </div>
    <div class="container">
        <div class="breadcrumb">
            <a href="/">Home</a> &raquo; <a href="/product/{{PRODUCT_ID}}">{{PRODUCT_NAME}}</a> &raquo; Reviews
        </div>
        <div class="reviews-section">
            <h3>All Reviews for {{PRODUCT_NAME}}</h3>
            {{REVIEWS_HTML}}
            <br>
            <a href="/product/{{PRODUCT_ID}}" class="btn">Back to Product</a>
        </div>
    </div>
    <div class="footer">
        <p>&copy; 2024 ShopDemo. All rights reserved.</p>
    </div>
</body>
</html>"""

ERROR_404 = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Not Found - ShopDemo</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; text-align: center; padding: 80px 20px; background: #f5f5f5; }
        h1 { color: #e74c3c; margin-bottom: 10px; }
        p { color: #7f8c8d; }
        a { color: #3498db; }
    </style>
</head>
<body>
    <h1>404 - Page Not Found</h1>
    <p>The page you're looking for doesn't exist.</p>
    <p><a href="/">Return to Home</a></p>
</body>
</html>"""

CATEGORIES_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Categories - ShopDemo</title>
    <link rel="shortcut icon" href="/static/assets/fav-icon.png">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color: #333; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 15px 0; }
        .header-inner { max-width: 1200px; margin: 0 auto; padding: 0 20px; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { font-size: 24px; }
        .header nav a { color: #ecf0f1; text-decoration: none; margin-left: 20px; font-size: 14px; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .cat-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 20px; margin-top: 20px; }
        .cat-card { background: white; border-radius: 8px; padding: 30px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .cat-card h3 { margin-bottom: 8px; }
        .cat-card p { color: #7f8c8d; font-size: 14px; }
        .footer { background: #2c3e50; color: #ecf0f1; text-align: center; padding: 20px; margin-top: 40px; font-size: 13px; }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-inner">
            <h1>ShopDemo</h1>
            <nav>
                <a href="/">Home</a>
                <a href="/categories">Categories</a>
                <a href="/about">About</a>
            </nav>
        </div>
    </div>
    <div class="container">
        <h2>All Categories</h2>
        <div class="cat-grid">
            <div class="cat-card"><h3>Electronics</h3><p>24 products</p></div>
            <div class="cat-card"><h3>Clothing</h3><p>56 products</p></div>
            <div class="cat-card"><h3>Home &amp; Garden</h3><p>31 products</p></div>
            <div class="cat-card"><h3>Sports</h3><p>18 products</p></div>
            <div class="cat-card"><h3>Books</h3><p>42 products</p></div>
            <div class="cat-card"><h3>Toys</h3><p>15 products</p></div>
        </div>
    </div>
    <div class="footer">
        <p>&copy; 2024 ShopDemo. All rights reserved.</p>
    </div>
</body>
</html>"""

ABOUT_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>About - ShopDemo</title>
    <link rel="shortcut icon" href="/static/assets/fav-icon.png">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color: #333; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 15px 0; }
        .header-inner { max-width: 1200px; margin: 0 auto; padding: 0 20px; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { font-size: 24px; }
        .header nav a { color: #ecf0f1; text-decoration: none; margin-left: 20px; font-size: 14px; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .content { background: white; border-radius: 8px; padding: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); line-height: 1.6; }
        .content h2 { margin-bottom: 15px; }
        .content p { margin-bottom: 10px; color: #555; }
        .footer { background: #2c3e50; color: #ecf0f1; text-align: center; padding: 20px; margin-top: 40px; font-size: 13px; }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-inner">
            <h1>ShopDemo</h1>
            <nav>
                <a href="/">Home</a>
                <a href="/categories">Categories</a>
                <a href="/about">About</a>
            </nav>
        </div>
    </div>
    <div class="container">
        <div class="content">
            <h2>About ShopDemo</h2>
            <p>ShopDemo is an open-source e-commerce platform built for modern merchants. We provide a flexible, customizable solution for online retail.</p>
            <p>Our platform features product management, customer reviews, category browsing, and a powerful search engine to help customers find what they need.</p>
            <p>Built with Python and Flask. Version 1.7.8</p>
        </div>
    </div>
    <div class="footer">
        <p>&copy; 2024 ShopDemo. All rights reserved.</p>
    </div>
</body>
</html>"""

SEARCH_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Search - ShopDemo</title>
    <link rel="shortcut icon" href="/static/assets/fav-icon.png">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color: #333; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 15px 0; }
        .header-inner { max-width: 1200px; margin: 0 auto; padding: 0 20px; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { font-size: 24px; }
        .header nav a { color: #ecf0f1; text-decoration: none; margin-left: 20px; font-size: 14px; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .search-bar { margin: 20px 0; }
        .search-bar form { display: flex; }
        .search-bar input[type="text"] { flex: 1; padding: 10px 15px; border: 1px solid #ddd; border-radius: 4px 0 0 4px; font-size: 14px; }
        .search-bar button { padding: 10px 20px; background: #3498db; color: white; border: none; border-radius: 0 4px 4px 0; cursor: pointer; }
        .results { background: white; border-radius: 8px; padding: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .footer { background: #2c3e50; color: #ecf0f1; text-align: center; padding: 20px; margin-top: 40px; font-size: 13px; }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-inner">
            <h1>ShopDemo</h1>
            <nav>
                <a href="/">Home</a>
                <a href="/categories">Categories</a>
                <a href="/about">About</a>
            </nav>
        </div>
    </div>
    <div class="container">
        <div class="search-bar">
            <form action="/search" method="get">
                <input type="text" name="q" placeholder="Search products..." value="{{ query }}">
                <button type="submit">Search</button>
            </form>
        </div>
        <div class="results">
            <h3>Search Results for "{{ query }}"</h3>
            <p style="color: #7f8c8d; margin-top: 10px;">No products found matching your search.</p>
        </div>
    </div>
    <div class="footer">
        <p>&copy; 2024 ShopDemo. All rights reserved.</p>
    </div>
</body>
</html>"""


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
