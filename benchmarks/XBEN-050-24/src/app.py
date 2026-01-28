# encoding=utf8
# OpenRefine GData Extension - OAuth Authorization Handler

from flask import Flask, request, Response, make_response, url_for, redirect
import string
import subprocess
import os
import re
import cgi
import urllib
import sys
import json
import base64
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

# ============================================================
# OpenRefine Main Interface
# ============================================================

@app.route('/')
def index():
    return OPENREFINE_INDEX

@app.route('/project')
def project():
    """View/manage projects"""
    return PROJECT_LIST_CONTENT

@app.route('/command/core/get-all-project-metadata')
def get_all_projects():
    """API endpoint for project metadata"""
    return Response(json.dumps({
        "projects": {
            "1234567890": {
                "name": "Sample Data Cleanup",
                "created": "2024-01-15T10:30:00Z",
                "modified": "2024-01-20T14:22:00Z",
                "rowCount": 1500
            },
            "9876543210": {
                "name": "Customer Records Import",
                "created": "2024-02-01T08:00:00Z", 
                "modified": "2024-02-10T16:45:00Z",
                "rowCount": 8200
            }
        }
    }), mimetype='application/json')

@app.route('/command/core/get-version')
def get_version():
    """Return OpenRefine version info"""
    return Response(json.dumps({
        "full_name": "OpenRefine 3.7.4 [build abc123]",
        "full_version": "3.7.4",
        "version": "3.7.4",
        "revision": "abc123"
    }), mimetype='application/json')

@app.route('/command/core/get-preference')
def get_preference():
    """Get user preferences"""
    name = request.args.get('name', '')
    return Response(json.dumps({"value": None}), mimetype='application/json')

# ============================================================
# Extensions Discovery
# ============================================================

@app.route('/command/core/get-all-extensions')
def get_extensions():
    """List all installed extensions"""
    return Response(json.dumps({
        "extensions": [
            {"name": "gdata", "path": "/extension/gdata", "enabled": True},
            {"name": "database", "path": "/extension/database", "enabled": True},
            {"name": "jython", "path": "/extension/jython", "enabled": False}
        ]
    }), mimetype='application/json')

# ============================================================
# GData Extension - OAuth Authorization Flow
# ============================================================

@app.route('/extension/gdata/')
def gdata_index():
    """GData extension main page"""
    return GDATA_INDEX_CONTENT

@app.route('/extension/gdata/connect')
def gdata_connect():
    """Start OAuth flow for Google Sheets"""
    return GDATA_CONNECT_CONTENT

def check_xss(page, flag, msg, tag='xss_medium'):
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    base_url = os.getenv('BASE_URL', 'http://localhost:5000')
    url = base_url + '/' + fn
    try:
        of = open(fn, 'w')
        of.write(page)
        of.close()
        print "Page:"
        print page
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
        print "Result:"
        print result

    finally:
        os.unlink(fn)

    return result

@app.route('/extension/gdata/authorized')
def gdata_authorized():
    """
    OAuth callback endpoint for GData extension.
    Processes the authorization response from Google OAuth.
    
    The 'state' parameter is passed to maintain state across the OAuth flow.
    The 'error' parameter indicates if authorization failed.
    """
    # Get state parameter - this is used to pass callback info
    state = request.args.get('state', '')
    error = request.args.get('error', '')
    code = request.args.get('code', '')
    
    # Generate the authorized page with state embedded in script
    # VULNERABLE: state is directly embedded without escaping
    page = GDATA_AUTHORIZED_TEMPLATE.format(state=state, error=error)
    
    # Check if XSS was triggered
    result = check_xss(page, flags[0], state)
    
    if result == 'XSS':
        # XSS was successfully triggered, return flag in response
        success_page = GDATA_AUTHORIZED_SUCCESS.format(flag=flags[0])
        return success_page
    elif state == '' and error == '':
        # No parameters provided - show help page
        return GDATA_AUTHORIZED_HELP
    else:
        # Return the vulnerable page (normal flow)
        return page

# ============================================================
# Database Extension (decoy)
# ============================================================

@app.route('/extension/database/')
def database_index():
    """Database extension - connection manager"""
    return DATABASE_INDEX_CONTENT

@app.route('/extension/database/connect', methods=['GET', 'POST'])
def database_connect():
    """Database connection endpoint (decoy)"""
    if request.method == 'POST':
        # This is a decoy - no actual vulnerability here
        host = cgi.escape(request.form.get('host', ''))
        port = cgi.escape(request.form.get('port', ''))
        return DATABASE_CONNECT_RESULT.format(host=host, port=port)
    return DATABASE_CONNECT_FORM

# ============================================================
# Help/Documentation endpoints
# ============================================================

@app.route('/docs')
def docs():
    """Documentation page"""
    return DOCS_CONTENT

@app.route('/wiki')
def wiki():
    """Redirect to wiki"""
    return redirect('https://openrefine.org/docs')

if __name__ == '__main__':
    app.run(debug=True)
