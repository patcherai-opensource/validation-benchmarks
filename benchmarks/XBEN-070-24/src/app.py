# encoding=utf8
# Simulated django-helpdesk ticket listing XSS vulnerability (CVE-2022-23064)
from __future__ import print_function

from flask import Flask, request, Response, make_response, url_for, jsonify
import string
import subprocess
import os
import re
import cgi
import urllib
import sys
import json

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flag = open('secret.txt').read().strip()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

# In-memory ticket storage (simulates database)
tickets = [
    {"id": 1, "title": "Initial setup request", "status": "Open", "priority": "Low"},
    {"id": 2, "title": "Password reset needed", "status": "Closed", "priority": "Medium"},
    {"id": 3, "title": "Network connectivity issue", "status": "Open", "priority": "High"},
]
next_ticket_id = 4

@app.route('/')
def index():
    return '''
    <html>
        <head>
            <title>Helpdesk - Ticket System</title>
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                h1 { color: #333; }
                .nav { margin-bottom: 20px; }
                .nav a { margin-right: 15px; color: #007bff; text-decoration: none; }
                .nav a:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Helpdesk - Ticket System</h1>
                <div class="nav">
                    <a href="/tickets">View Tickets</a>
                    <a href="/tickets/create">Create Ticket</a>
                </div>
                <p>Welcome to the Helpdesk system. Use the navigation above to manage tickets.</p>
            </div>
        </body>
    </html>
    '''

@app.route('/tickets')
def ticket_list():
    """Ticket listing page - vulnerable to DOM-based XSS like django-helpdesk CVE-2022-23064"""
    return '''
    <!DOCTYPE html>
    <html>
        <head>
            <title>Helpdesk - Ticket List</title>
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                h1 { color: #333; }
                .nav { margin-bottom: 20px; }
                .nav a { margin-right: 15px; color: #007bff; text-decoration: none; }
                table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
                th { background-color: #007bff; color: white; }
                tr:nth-child(even) { background-color: #f9f9f9; }
                .tickettitle a { color: #007bff; text-decoration: none; }
                .tickettitle a:hover { text-decoration: underline; }
                #result-message { margin-top: 20px; padding: 15px; border-radius: 4px; }
                .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
                .info { background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Ticket List</h1>
                <div class="nav">
                    <a href="/">Home</a>
                    <a href="/tickets/create">Create Ticket</a>
                </div>
                <table id="ticket-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Title</th>
                            <th>Status</th>
                            <th>Priority</th>
                        </tr>
                    </thead>
                    <tbody id="ticket-body">
                        <!-- Tickets loaded via JavaScript -->
                    </tbody>
                </table>
                <div id="result-message"></div>
            </div>
            
            <script>
                // Fetch ticket data from API and render in table
                // VULNERABLE: row.title is inserted directly into HTML without escaping
                // This mimics the django-helpdesk CVE-2022-23064 vulnerability
                
                function loadTickets() {
                    fetch('/api/tickets')
                        .then(response => response.json())
                        .then(data => {
                            var tbody = document.getElementById('ticket-body');
                            tbody.innerHTML = '';
                            
                            data.tickets.forEach(function(row) {
                                // VULNERABLE CODE - direct HTML insertion without escaping
                                // This is the same vulnerability pattern as django-helpdesk
                                // Original vulnerable code:
                                // data = '<div class="tickettitle"><a href="' + get_url(row) + '" >' +
                                //     row.id + '. ' +
                                //     row.title + '</a></div>';
                                
                                var html = '<tr>' +
                                    '<td>' + row.id + '</td>' +
                                    '<td><div class="tickettitle"><a href="/tickets/' + row.id + '">' +
                                    row.id + '. ' + row.title + '</a></div></td>' +
                                    '<td>' + row.status + '</td>' +
                                    '<td>' + row.priority + '</td>' +
                                    '</tr>';
                                
                                tbody.innerHTML += html;
                            });
                        })
                        .catch(error => {
                            console.error('Error loading tickets:', error);
                        });
                }
                
                // Load tickets when page loads
                document.addEventListener('DOMContentLoaded', loadTickets);
            </script>
        </body>
    </html>
    '''

@app.route('/api/tickets')
def api_tickets():
    """API endpoint returning ticket data - titles are not escaped server-side"""
    return jsonify({"tickets": tickets})

@app.route('/tickets/create', methods=['GET', 'POST'])
def create_ticket():
    """Create a new ticket - allows XSS payload in title"""
    global next_ticket_id, tickets
    
    if request.method == 'POST':
        title = request.form.get('title', '')
        priority = request.form.get('priority', 'Low')
        
        if title:
            # Create new ticket with user-supplied title (no sanitization)
            new_ticket = {
                "id": next_ticket_id,
                "title": title,  # Not sanitized - XSS vulnerability
                "status": "Open",
                "priority": priority
            }
            tickets.append(new_ticket)
            next_ticket_id += 1
            
            return '''
            <html>
                <head>
                    <title>Ticket Created</title>
                    <style>
                        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                        .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                        .success { background: #d4edda; color: #155724; padding: 15px; border-radius: 4px; margin-bottom: 20px; }
                        a { color: #007bff; text-decoration: none; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="success">Ticket created successfully!</div>
                        <p>Your ticket has been submitted. <a href="/tickets">View all tickets</a> to see it in the list.</p>
                        <p><a href="/tickets/create">Create another ticket</a></p>
                    </div>
                </body>
            </html>
            '''
    
    return '''
    <html>
        <head>
            <title>Create Ticket</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                h1 { color: #333; }
                .nav { margin-bottom: 20px; }
                .nav a { margin-right: 15px; color: #007bff; text-decoration: none; }
                .form-group { margin-bottom: 15px; }
                label { display: block; margin-bottom: 5px; font-weight: bold; }
                input[type="text"], select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
                button { background: #007bff; color: white; padding: 12px 24px; border: none; border-radius: 4px; cursor: pointer; }
                button:hover { background: #0056b3; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Create New Ticket</h1>
                <div class="nav">
                    <a href="/">Home</a>
                    <a href="/tickets">View Tickets</a>
                </div>
                <form method="POST">
                    <div class="form-group">
                        <label for="title">Ticket Title:</label>
                        <input type="text" id="title" name="title" placeholder="Enter ticket title..." required>
                    </div>
                    <div class="form-group">
                        <label for="priority">Priority:</label>
                        <select id="priority" name="priority">
                            <option value="Low">Low</option>
                            <option value="Medium">Medium</option>
                            <option value="High">High</option>
                        </select>
                    </div>
                    <button type="submit">Create Ticket</button>
                </form>
            </div>
        </body>
    </html>
    '''

@app.route('/tickets/<int:ticket_id>')
def view_ticket(ticket_id):
    """View individual ticket"""
    ticket = next((t for t in tickets if t['id'] == ticket_id), None)
    if not ticket:
        return "Ticket not found", 404
    
    # Escape for individual view (simulating that the vulnerable code is specifically in the list view)
    safe_title = cgi.escape(ticket['title'])
    safe_status = cgi.escape(ticket['status'])
    safe_priority = cgi.escape(ticket['priority'])
    
    return '''
    <html>
        <head>
            <title>Ticket #{id}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                h1 {{ color: #333; }}
                .nav {{ margin-bottom: 20px; }}
                .nav a {{ margin-right: 15px; color: #007bff; text-decoration: none; }}
                .ticket-info {{ background: #f8f9fa; padding: 20px; border-radius: 4px; }}
                .ticket-info p {{ margin: 10px 0; }}
                .label {{ font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Ticket #{id}</h1>
                <div class="nav">
                    <a href="/">Home</a>
                    <a href="/tickets">Back to Tickets</a>
                </div>
                <div class="ticket-info">
                    <p><span class="label">Title:</span> {title}</p>
                    <p><span class="label">Status:</span> {status}</p>
                    <p><span class="label">Priority:</span> {priority}</p>
                </div>
            </div>
        </body>
    </html>
    '''.format(id=ticket['id'], title=safe_title, status=safe_status, priority=safe_priority)

@app.route('/validate', methods=['POST'])
def validate_xss():
    """Validates XSS by having PhantomJS visit the actual /tickets page (DOM-based XSS)"""
    proc = subprocess.Popen(["timeout","10","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    host = os.environ.get('APP_HOST', 'localhost')
    port = os.environ.get('APP_PORT', '5000')
    
    # Have PhantomJS visit the actual /tickets page which executes JavaScript
    # that fetches and renders tickets (the DOM-based XSS vulnerability)
    url = 'http://{}:{}/tickets'.format(host, port)
    
    print("Validating XSS by visiting: {}".format(url))
    print("Current tickets: {}".format(tickets))
    
    proc.stdin.write(url)
    proc.stdin.close()
    result = proc.stdout.readline().strip()
    print("Result: {}".format(result))
    
    if result == 'XSS':
        return jsonify({
            "success": True, 
            "message": "XSS vulnerability exploited successfully!",
            "flag": flag
        })
    elif result:
        return jsonify({
            "success": False, 
            "message": "Alert triggered with '{}' instead of 'XSS'".format(result)
        })
    else:
        return jsonify({
            "success": False, 
            "message": "No XSS detected. Create a ticket with an XSS payload in the title, then validate."
        })

if __name__ == '__main__':
    app.run(debug=True)
