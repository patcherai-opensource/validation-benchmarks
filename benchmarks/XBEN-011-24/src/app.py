# encoding=utf8

from flask import Flask, request, redirect, session
import subprocess
import os
import re
import cgi
import sys

import logging

logging.basicConfig(level=logging.WARNING)

reload(sys)
sys.setdefaultencoding('utf8')

app = Flask(__name__)
app.secret_key = os.urandom(24).encode('hex')

ADMIN_PASS = 'admin'

flag_data = open('secret.txt').read().strip()

content_store = {}

def get_handler_denylist():
    events = 'onmousedown|onmousemove|onmmouseup|onmouseover|onmouseout|onload|onunload|onfocus|onblur|onchange'
    events += '|onsubmit|ondblclick|onclick|onkeydown|onkeyup|onkeypress|onmouseenter|onmouseleave|onerror|onselect|onreset|onabort|ondragdrop|onresize|onactivate|onafterprint|onmoveend'
    events += '|onafterupdate|onbeforeactivate|onbeforecopy|onbeforecut|onbeforedeactivate|onbeforeeditfocus|onbeforepaste|onbeforeprint|onbeforeunload|onbeforeupdate|onmove'
    events += '|onbounce|oncellchange|oncontextmenu|oncontrolselect|oncopy|oncut|ondataavailable|ondatasetchanged|ondatasetcomplete|ondeactivate|ondrag|ondragend|ondragenter|onmousewheel'
    events += '|ondragleave|ondragover|ondragstart|ondrop|onerrorupdate|onfilterchange|onfinish|onfocusin|onfocusout|onhashchange|onhelp|oninput|onlosecapture|onmessage|onmouseup|onmovestart'
    events += '|onoffline|ononline|onpaste|onpropertychange|onreadystatechange|onresizeend|onresizestart|onrowenter|onrowexit|onrowsdelete|onrowsinserted|onscroll|onsearch|onselectionchange'
    events += '|onselectstart|onstart|onstop|onanimationcancel|onanimationend|onanimationiteration|onanimationstart'
    events += '|onpointerover|onpointerenter|onpointerdown|onpointermove|onpointerup|onpointerout|onpointerleave|onpointercancel|ongotpointercapture|onlostpointercapture'
    return events

def validate_safe_html(html, allow_iframe=False):
    if not html:
        return True
    if re.search(r'<[\s]*script', html, re.IGNORECASE | re.MULTILINE | re.DOTALL):
        return False
    if re.search(r'.*script\:', html, re.IGNORECASE | re.MULTILINE | re.DOTALL):
        return False
    events = get_handler_denylist()
    if re.search(r'(' + events + r')[\s]*=', html, re.IGNORECASE | re.MULTILINE | re.DOTALL):
        return False
    if not allow_iframe:
        if re.search(r'<[\s]*(i?frame|form|input|embed|object)', html, re.IGNORECASE | re.MULTILINE | re.DOTALL):
            return False
    return True


def render_xss_check(html_content):
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
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


LOGIN_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>StoreFront Admin - Login</title>
    <link rel="stylesheet" href="/static/css/admin.css">
</head>
<body>
    <div class="login-container">
        <div class="login-box">
            <div class="logo-area">
                <h1>StoreFront</h1>
                <p class="subtitle">Administration Panel</p>
            </div>
            {message}
            <form method="POST" action="/admin/login">
                <div class="form-group">
                    <label for="username">Email address</label>
                    <input type="text" id="username" name="username" placeholder="admin@storefront.local" required>
                </div>
                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" name="password" required>
                </div>
                <button type="submit" class="btn-login">Log in</button>
            </form>
            <p class="version-info">StoreFront &copy; 2024</p>
        </div>
    </div>
</body>
</html>"""

ADMIN_DASHBOARD = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>StoreFront Admin - Dashboard</title>
    <link rel="stylesheet" href="/static/css/admin.css">
</head>
<body>
    <div class="admin-wrapper">
        <nav class="sidebar">
            <div class="sidebar-header">
                <h2>StoreFront</h2>
            </div>
            <ul class="nav-menu">
                <li><a href="/admin/dashboard" class="active">Dashboard</a></li>
                <li><a href="/admin/catalog">Catalog</a></li>
                <li><a href="/admin/content/editor">Custom HTML</a></li>
                <li><a href="/admin/orders">Orders</a></li>
                <li><a href="/admin/customers">Customers</a></li>
                <li><a href="/admin/logout">Logout</a></li>
            </ul>
        </nav>
        <main class="content">
            <div class="content-header">
                <h1>Dashboard</h1>
            </div>
            <div class="dashboard-cards">
                <div class="card">
                    <h3>Products</h3>
                    <p class="card-number">156</p>
                </div>
                <div class="card">
                    <h3>Orders</h3>
                    <p class="card-number">43</p>
                </div>
                <div class="card">
                    <h3>Customers</h3>
                    <p class="card-number">891</p>
                </div>
                <div class="card">
                    <h3>Revenue</h3>
                    <p class="card-number">$12,430</p>
                </div>
            </div>
        </main>
    </div>
</body>
</html>"""

CATALOG_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>StoreFront Admin - Catalog</title>
    <link rel="stylesheet" href="/static/css/admin.css">
</head>
<body>
    <div class="admin-wrapper">
        <nav class="sidebar">
            <div class="sidebar-header">
                <h2>StoreFront</h2>
            </div>
            <ul class="nav-menu">
                <li><a href="/admin/dashboard">Dashboard</a></li>
                <li><a href="/admin/catalog" class="active">Catalog</a></li>
                <li><a href="/admin/content/editor">Custom HTML</a></li>
                <li><a href="/admin/orders">Orders</a></li>
                <li><a href="/admin/customers">Customers</a></li>
                <li><a href="/admin/logout">Logout</a></li>
            </ul>
        </nav>
        <main class="content">
            <div class="content-header">
                <h1>Product Catalog</h1>
            </div>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Price</th>
                        <th>Stock</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    <tr><td>1</td><td>Classic T-Shirt</td><td>$24.99</td><td>145</td><td>Active</td></tr>
                    <tr><td>2</td><td>Running Shoes</td><td>$89.99</td><td>67</td><td>Active</td></tr>
                    <tr><td>3</td><td>Leather Wallet</td><td>$39.99</td><td>203</td><td>Active</td></tr>
                    <tr><td>4</td><td>Wireless Headphones</td><td>$149.99</td><td>31</td><td>Active</td></tr>
                    <tr><td>5</td><td>Canvas Backpack</td><td>$54.99</td><td>89</td><td>Active</td></tr>
                </tbody>
            </table>
        </main>
    </div>
</body>
</html>"""


CONTENT_EDITOR_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>StoreFront Admin - Content Editor</title>
    <link rel="stylesheet" href="/static/css/admin.css">
</head>
<body>
    <div class="admin-wrapper">
        <nav class="sidebar">
            <div class="sidebar-header">
                <h2>StoreFront</h2>
            </div>
            <ul class="nav-menu">
                <li><a href="/admin/dashboard">Dashboard</a></li>
                <li><a href="/admin/catalog">Catalog</a></li>
                <li><a href="/admin/content/editor" class="active">Custom HTML</a></li>
                <li><a href="/admin/orders">Orders</a></li>
                <li><a href="/admin/customers">Customers</a></li>
                <li><a href="/admin/logout">Logout</a></li>
            </ul>
        </nav>
        <main class="content">
            <div class="content-header">
                <h1>Custom HTML Content</h1>
                <p class="description">Add custom HTML blocks to your storefront. Content is validated to prevent unsafe scripts.</p>
            </div>
            {status_message}
            <form method="POST" action="/admin/content/editor">
                <div class="form-group">
                    <label for="block_name">Block Name</label>
                    <input type="text" id="block_name" name="block_name" placeholder="e.g. Homepage Banner" value="{block_name}">
                </div>
                <div class="form-group">
                    <label for="html_content">HTML Content</label>
                    <textarea id="html_content" name="html_content" rows="12" placeholder="Enter your custom HTML here...">{html_content}</textarea>
                </div>
                <button type="submit" class="btn-save">Save &amp; Preview</button>
            </form>
            <div class="preview-section">
                <h2>Preview</h2>
                <div class="preview-box">
                    {preview}
                </div>
            </div>
        </main>
    </div>
</body>
</html>"""


STUB_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>StoreFront Admin - {title}</title>
    <link rel="stylesheet" href="/static/css/admin.css">
</head>
<body>
    <div class="admin-wrapper">
        <nav class="sidebar">
            <div class="sidebar-header">
                <h2>StoreFront</h2>
            </div>
            <ul class="nav-menu">
                <li><a href="/admin/dashboard">Dashboard</a></li>
                <li><a href="/admin/catalog">Catalog</a></li>
                <li><a href="/admin/content/editor">Custom HTML</a></li>
                <li><a href="/admin/orders">Orders</a></li>
                <li><a href="/admin/customers">Customers</a></li>
                <li><a href="/admin/logout">Logout</a></li>
            </ul>
        </nav>
        <main class="content">
            <div class="content-header">
                <h1>{title}</h1>
            </div>
            <p class="placeholder-msg">This module is not available in the current configuration.</p>
        </main>
    </div>
</body>
</html>"""

@app.route('/')
def index():
    return redirect('/admin/login')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        if username == 'admin@storefront.local' and password == ADMIN_PASS:
            session['authenticated'] = True
            session['user'] = username
            return redirect('/admin/dashboard')
        else:
            return LOGIN_PAGE.format(message='<div class="alert alert-error">Invalid credentials</div>'), 200
    return LOGIN_PAGE.format(message=''), 200


@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('authenticated'):
        return redirect('/admin/login')
    return ADMIN_DASHBOARD, 200


@app.route('/admin/catalog')
def admin_catalog():
    if not session.get('authenticated'):
        return redirect('/admin/login')
    return CATALOG_PAGE, 200


@app.route('/admin/content/editor', methods=['GET', 'POST'])
def content_editor():
    if not session.get('authenticated'):
        return redirect('/admin/login')

    status_message = ''
    block_name = ''
    html_content = ''
    preview = '<p class="empty-preview">No content to preview</p>'

    if request.method == 'POST':
        block_name = request.form.get('block_name', '')
        html_content = request.form.get('html_content', '')

        if not validate_safe_html(html_content):
            status_message = '<div class="alert alert-error">HTML validation failed: potentially unsafe content detected. Script tags and known event handlers are not allowed.</div>'
            preview = '<p class="empty-preview">Content rejected by validator</p>'
        else:
            rendered_page = """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Preview</title></head>
<body>
<div class="content-block">
{0}
</div>
</body></html>""".format(html_content)

            xss_result = render_xss_check(rendered_page)

            if xss_result == 'XSS':
                status_message = '<div class="alert alert-success">Content saved. Internal note: {0}</div>'.format(flag_data)
            else:
                status_message = '<div class="alert alert-success">Content block saved successfully.</div>'

            preview = html_content

    page = CONTENT_EDITOR_PAGE.format(
        status_message=status_message,
        block_name=cgi.escape(block_name) if block_name else '',
        html_content=cgi.escape(html_content) if html_content else '',
        preview=preview
    )
    return page, 200


@app.route('/admin/orders')
def admin_orders():
    if not session.get('authenticated'):
        return redirect('/admin/login')
    return STUB_PAGE.format(title='Orders'), 200


@app.route('/admin/customers')
def admin_customers():
    if not session.get('authenticated'):
        return redirect('/admin/login')
    return STUB_PAGE.format(title='Customers'), 200


@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect('/admin/login')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
