# encoding=utf8

from flask import Flask, request, jsonify
import subprocess
import os
import sys
import cgi
import time

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False

# In-memory ticket storage (simulates database)
tickets = []
ticket_counter = [0]

# Load flag from secret file
def get_flag():
    try:
        return open('secret.txt').read().strip()
    except:
        return "FLAG{test}"

# Staff credentials (simulates authentication)
STAFF_USER = "admin"
STAFF_PASS = "support2024"

# HTML Templates
INDEX_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Support Helpdesk</title>
    <link rel="stylesheet" href="/static/css/helpdesk.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>Support Helpdesk</h1>
            <nav>
                <a href="/">Home</a>
                <a href="/tickets/new">Submit Ticket</a>
                <a href="/staff/login">Staff Login</a>
            </nav>
        </header>
        <main>
            <h2>Welcome to our Support System</h2>
            <p>Need help? Submit a support ticket and our team will get back to you.</p>
            <div class="actions">
                <a href="/tickets/new" class="btn">Submit New Ticket</a>
            </div>
        </main>
        <footer>
            <p>&copy; 2024 Support Helpdesk System</p>
        </footer>
    </div>
</body>
</html>
"""

NEW_TICKET_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Submit Ticket - Support Helpdesk</title>
    <link rel="stylesheet" href="/static/css/helpdesk.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>Support Helpdesk</h1>
            <nav>
                <a href="/">Home</a>
                <a href="/tickets/new">Submit Ticket</a>
                <a href="/staff/login">Staff Login</a>
            </nav>
        </header>
        <main>
            <h2>Submit a Support Ticket</h2>
            {message}
            <form method="POST" action="/tickets/new">
                <div class="form-group">
                    <label for="title">Title:</label>
                    <input type="text" id="title" name="title" required maxlength="500" placeholder="Brief description of your issue">
                </div>
                <div class="form-group">
                    <label for="description">Description:</label>
                    <textarea id="description" name="description" rows="6" required placeholder="Please describe your issue in detail"></textarea>
                </div>
                <div class="form-group">
                    <label for="email">Email:</label>
                    <input type="email" id="email" name="email" required placeholder="your@email.com">
                </div>
                <div class="form-group">
                    <label for="priority">Priority:</label>
                    <select id="priority" name="priority">
                        <option value="low">Low</option>
                        <option value="medium" selected>Medium</option>
                        <option value="high">High</option>
                    </select>
                </div>
                <button type="submit" class="btn">Submit Ticket</button>
            </form>
        </main>
        <footer>
            <p>&copy; 2024 Support Helpdesk System</p>
        </footer>
    </div>
</body>
</html>
"""

STAFF_LOGIN_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Staff Login - Support Helpdesk</title>
    <link rel="stylesheet" href="/static/css/helpdesk.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>Support Helpdesk</h1>
            <nav>
                <a href="/">Home</a>
                <a href="/tickets/new">Submit Ticket</a>
                <a href="/staff/login">Staff Login</a>
            </nav>
        </header>
        <main>
            <h2>Staff Login</h2>
            {message}
            <form method="POST" action="/staff/login">
                <div class="form-group">
                    <label for="username">Username:</label>
                    <input type="text" id="username" name="username" required>
                </div>
                <div class="form-group">
                    <label for="password">Password:</label>
                    <input type="password" id="password" name="password" required>
                </div>
                <button type="submit" class="btn">Login</button>
            </form>
        </main>
        <footer>
            <p>&copy; 2024 Support Helpdesk System</p>
        </footer>
    </div>
</body>
</html>
"""

# Ticket list page with vulnerable JavaScript (mimics django-helpdesk DataTables rendering)
TICKET_LIST_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Ticket List - Support Helpdesk</title>
    <link rel="stylesheet" href="/static/css/helpdesk.css">
    <style>
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #4a90d9; color: white; }}
        tr:hover {{ background-color: #f5f5f5; }}
        .tickettitle a {{ color: #4a90d9; text-decoration: none; }}
        .tickettitle a:hover {{ text-decoration: underline; }}
        .priority-high {{ color: #d9534f; font-weight: bold; }}
        .priority-medium {{ color: #f0ad4e; }}
        .priority-low {{ color: #5cb85c; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Support Helpdesk</h1>
            <nav>
                <a href="/">Home</a>
                <a href="/tickets/new">Submit Ticket</a>
                <a href="/staff/tickets">Ticket List</a>
                <a href="/staff/logout">Logout</a>
            </nav>
        </header>
        <main>
            <h2>Ticket List</h2>
            <p>Manage and review submitted support tickets.</p>
            <table id="ticketTable">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Title</th>
                        <th>Submitter</th>
                        <th>Priority</th>
                        <th>Status</th>
                        <th>Created</th>
                    </tr>
                </thead>
                <tbody id="ticketTableBody">
                </tbody>
            </table>
        </main>
        <footer>
            <p>&copy; 2024 Support Helpdesk System</p>
        </footer>
    </div>
    
    <script>
        function get_url(row) {{
            return '/staff/tickets/' + row.id;
        }}
        
        function loadTickets() {{
            var xhr = new XMLHttpRequest();
            xhr.open('GET', '/api/tickets', true);
            xhr.onreadystatechange = function() {{
                if (xhr.readyState === 4 && xhr.status === 200) {{
                    var response = JSON.parse(xhr.responseText);
                    var tbody = document.getElementById('ticketTableBody');
                    tbody.innerHTML = '';
                    
                    response.data.forEach(function(row) {{
                        var tr = document.createElement('tr');
                        
                        var data = '<div class="tickettitle"><a href="' + get_url(row) + '" >' +
                            row.id + '. ' +
                            row.title + '</a></div>';
                        
                        tr.innerHTML = 
                            '<td>' + row.id + '</td>' +
                            '<td>' + data + '</td>' +
                            '<td>' + row.email + '</td>' +
                            '<td class="priority-' + row.priority + '">' + row.priority + '</td>' +
                            '<td>' + row.status + '</td>' +
                            '<td>' + row.created + '</td>';
                        
                        tbody.appendChild(tr);
                    }});
                }}
            }};
            xhr.send();
        }}
        
        document.addEventListener('DOMContentLoaded', loadTickets);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return INDEX_PAGE

@app.route('/tickets/new', methods=['GET', 'POST'])
def new_ticket():
    message = ""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        email = request.form.get('email', '').strip()
        priority = request.form.get('priority', 'medium')
        
        if title and description and email:
            ticket_counter[0] += 1
            ticket = {
                'id': ticket_counter[0],
                'title': title,
                'description': description,
                'email': email,
                'priority': priority,
                'status': 'open',
                'created': time.strftime('%Y-%m-%d')
            }
            tickets.append(ticket)
            message = '<div class="success">Ticket #{} submitted successfully! Our staff will review it shortly.</div>'.format(ticket_counter[0])
        else:
            message = '<div class="error">Please fill in all required fields.</div>'
    
    return NEW_TICKET_PAGE.format(message=message)

@app.route('/staff/login', methods=['GET', 'POST'])
def staff_login():
    message = ""
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        if username == STAFF_USER and password == STAFF_PASS:
            response = app.make_response('<script>window.location.href="/staff/tickets";</script>')
            response.set_cookie('staff_session', 'authenticated', httponly=True)
            return response
        else:
            message = '<div class="error">Invalid credentials. Please try again.</div>'
    
    return STAFF_LOGIN_PAGE.format(message=message)

@app.route('/staff/logout')
def staff_logout():
    response = app.make_response('<script>window.location.href="/";</script>')
    response.set_cookie('staff_session', '', expires=0)
    return response

def is_staff_authenticated():
    return request.cookies.get('staff_session') == 'authenticated'

@app.route('/staff/tickets')
def ticket_list():
    if not is_staff_authenticated():
        return '<script>window.location.href="/staff/login";</script>'
    return TICKET_LIST_PAGE

@app.route('/api/tickets')
def api_tickets():
    return jsonify({
        'data': tickets,
        'recordsTotal': len(tickets),
        'recordsFiltered': len(tickets)
    })

@app.route('/staff/tickets/<int:ticket_id>')
def view_ticket(ticket_id):
    if not is_staff_authenticated():
        return '<script>window.location.href="/staff/login";</script>'
    
    ticket = None
    for t in tickets:
        if t['id'] == ticket_id:
            ticket = t
            break
    
    if not ticket:
        return "Ticket not found", 404
    
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Ticket #{id} - Support Helpdesk</title>
        <link rel="stylesheet" href="/static/css/helpdesk.css">
    </head>
    <body>
        <div class="container">
            <header>
                <h1>Support Helpdesk</h1>
                <nav>
                    <a href="/">Home</a>
                    <a href="/tickets/new">Submit Ticket</a>
                    <a href="/staff/tickets">Ticket List</a>
                    <a href="/staff/logout">Logout</a>
                </nav>
            </header>
            <main>
                <h2>Ticket #{id}</h2>
                <div class="ticket-details">
                    <p><strong>Title:</strong> {title}</p>
                    <p><strong>Status:</strong> {status}</p>
                    <p><strong>Priority:</strong> {priority}</p>
                    <p><strong>Submitter:</strong> {email}</p>
                    <p><strong>Description:</strong></p>
                    <div class="description">{description}</div>
                </div>
                <a href="/staff/tickets" class="btn">Back to List</a>
            </main>
        </div>
    </body>
    </html>
    """.format(
        id=ticket['id'],
        title=cgi.escape(ticket['title']),
        status=cgi.escape(ticket['status']),
        priority=cgi.escape(ticket['priority']),
        email=cgi.escape(ticket['email']),
        description=cgi.escape(ticket['description'])
    )

@app.route('/report', methods=['POST'])
def report_ticket():
    """
    This endpoint simulates reporting a ticket to staff for review.
    A staff bot will view the ticket list page.
    """
    proc = subprocess.Popen(["timeout", "10", "phantomjs", "check.js"], 
                           stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    
    host = os.environ.get('APP_HOST', 'localhost')
    port = os.environ.get('APP_PORT', '5000')
    
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    
    auth_page = """
    <!DOCTYPE html>
    <html>
    <head>
        <script>
            document.cookie = "staff_session=authenticated";
            window.location.href = "http://{host}:{port}/staff/tickets";
        </script>
    </head>
    <body>Redirecting...</body>
    </html>
    """.format(host=host, port=port)
    
    url = 'http://{}:{}/'.format(host, port) + fn
    
    try:
        of = open(fn, 'w')
        of.write(auth_page)
        of.close()
        
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
        
    finally:
        try:
            os.unlink(fn)
        except:
            pass
    
    if result == 'XSS':
        flag = get_flag()
        return jsonify({
            'status': 'success',
            'message': 'Staff review completed. Flag: ' + flag
        })
    elif result:
        return jsonify({
            'status': 'info',
            'message': 'Alert detected: ' + cgi.escape(result)
        })
    else:
        return jsonify({
            'status': 'completed',
            'message': 'Staff has reviewed the tickets.'
        })

@app.errorhandler(404)
def not_found(e):
    return "Not Found", 404

@app.errorhandler(500)
def server_error(e):
    return "Internal Server Error", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
