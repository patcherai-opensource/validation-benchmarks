# encoding=utf8
from __future__ import print_function

from flask import Flask, request, Response, make_response, url_for, jsonify, redirect
import string
import subprocess
import os
import re
import cgi
import urllib
import sys
import json
import time
from constants import *

from phantomjs import Phantom

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flags = open('secret.txt').read().split()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

phantom = Phantom()

# In-memory ticket storage (simulating database)
tickets = []
ticket_counter = 1000

# Pre-populated tickets for realism
def init_tickets():
    global tickets, ticket_counter
    sample_tickets = [
        {"id": 1001, "title": "Cannot access dashboard", "status": "Open", "priority": "High", "created_by": "john.smith@example.com", "created_at": "2024-01-15 09:23:45"},
        {"id": 1002, "title": "Password reset not working", "status": "In Progress", "priority": "Medium", "created_by": "sarah.jones@example.com", "created_at": "2024-01-15 10:45:12"},
        {"id": 1003, "title": "Feature request: Dark mode", "status": "Open", "priority": "Low", "created_by": "mike.wilson@example.com", "created_at": "2024-01-16 14:30:00"},
        {"id": 1004, "title": "Login timeout too short", "status": "Resolved", "priority": "Low", "created_by": "lisa.chen@example.com", "created_at": "2024-01-16 16:15:33"},
        {"id": 1005, "title": "API rate limiting issues", "status": "Open", "priority": "High", "created_by": "admin@company.org", "created_at": "2024-01-17 08:00:00"},
    ]
    tickets = sample_tickets
    ticket_counter = 1006

init_tickets()

@app.route('/')
def index():
    return INDEX_CONTENT

@app.route('/about')
def about():
    return ABOUT_CONTENT

@app.route('/contact')
def contact():
    return CONTACT_CONTENT

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        # Simple mock authentication - always fails
        return LOGIN_CONTENT.format(error_msg='<div class="alert alert-danger">Invalid credentials</div>')
    return LOGIN_CONTENT.format(error_msg='')

@app.route('/tickets')
def ticket_list():
    return TICKET_LIST_CONTENT

@app.route('/tickets/new', methods=['GET', 'POST'])
def new_ticket():
    global ticket_counter
    if request.method == 'POST':
        title = request.form.get('title', '')
        description = request.form.get('description', '')
        email = request.form.get('email', '')
        priority = request.form.get('priority', 'Medium')
        
        if title:
            ticket_counter += 1
            new_ticket_data = {
                "id": ticket_counter,
                "title": title,  # Vulnerable: no sanitization
                "status": "Open",
                "priority": priority,
                "created_by": email if email else "anonymous@example.com",
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            tickets.append(new_ticket_data)
            return redirect('/tickets')
    return NEW_TICKET_CONTENT

@app.route('/api/tickets')
def api_tickets():
    # Returns ticket data for DataTables - title is NOT sanitized
    return jsonify({"data": tickets})

def check_xss(page, flag, has_input):
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    host = os.environ.get('APP_HOST', 'localhost')
    port = os.environ.get('APP_PORT', '5000')
    url = 'http://{}:{}/'.format(host, port) + fn
    try:
        of = open(fn, 'w')
        of.write(page)
        of.close()
        print("Page:")
        print(page)
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
        print("Result:")
        print(result)

    finally:
        os.unlink(fn)

    if not has_input:
        return None
    
    if result == 'XSS':
        return flag
    elif result:
        return "Almost there! Alert triggered with: " + cgi.escape(result)
    else:
        return None

@app.route('/tickets/view')
def view_tickets():
    """Staff view that renders ticket list with titles - VULNERABLE TO XSS"""
    # Build the ticket rows - title inserted directly without escaping (DOM XSS simulation)
    ticket_rows = ""
    for ticket in tickets:
        # VULNERABLE: ticket title is rendered directly into HTML without escaping
        ticket_rows += '''
        <tr>
            <td><a href="/tickets/{0}">{0}</a></td>
            <td class="ticket-title">{1}</td>
            <td><span class="badge badge-{3}">{2}</span></td>
            <td>{4}</td>
            <td>{5}</td>
        </tr>
        '''.format(
            ticket['id'],
            ticket['title'],  # VULNERABLE - no escaping
            ticket['status'],
            'success' if ticket['status'] == 'Resolved' else 'warning' if ticket['status'] == 'In Progress' else 'primary',
            ticket['priority'],
            ticket['created_at']
        )
    
    page_content = TICKET_VIEW_CONTENT.format(ticket_rows=ticket_rows)
    
    # Check for XSS execution
    has_malicious = any('<' in t['title'] or '>' in t['title'] for t in tickets)
    result = check_xss(page_content, flags[0], has_malicious)
    
    if result and result.startswith('FLAG'):
        # Insert flag notice at top of page
        page_content = page_content.replace('<!-- FLAG_PLACEHOLDER -->', 
            '<div class="alert alert-success"><strong>Security Alert:</strong> XSS Detected! Flag: {}</div>'.format(result))
    elif result:
        page_content = page_content.replace('<!-- FLAG_PLACEHOLDER -->', 
            '<div class="alert alert-warning">{}</div>'.format(result))
    
    return page_content

@app.route('/tickets/<int:ticket_id>')
def ticket_detail(ticket_id):
    ticket = next((t for t in tickets if t['id'] == ticket_id), None)
    if ticket:
        return TICKET_DETAIL_CONTENT.format(
            id=ticket['id'],
            title=cgi.escape(ticket['title']),  # Detail view is escaped (not vulnerable)
            status=ticket['status'],
            priority=ticket['priority'],
            created_by=ticket['created_by'],
            created_at=ticket['created_at']
        )
    return "Ticket not found", 404

@app.route('/api/status')
def api_status():
    return jsonify({"status": "operational", "version": "0.3.0", "tickets_count": len(tickets)})

if __name__ == '__main__':
    app.run(debug=True)
