# encoding=utf8
"""
Data Profiling Report Generator

This application simulates a data profiling tool similar to ydata-profiling.
Users can submit data samples which are then rendered into HTML reports.

VULNERABILITY: CVE-like issue where Jinja2 templates are configured WITHOUT
autoescape, allowing XSS when user-controlled data is rendered into reports.
"""

from flask import Flask, request, Response, make_response, url_for
import jinja2
import string
import subprocess
import os
import re
import cgi
import urllib
import sys
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

# VULNERABLE: Jinja2 environment without autoescape enabled
# This mirrors the vulnerability in ydata-profiling where templates.py
# initialized Environment without autoescape=jinja2.select_autoescape()
template_env = jinja2.Environment(
    loader=jinja2.BaseLoader(),
    autoescape=False  # VULNERABILITY: autoescape disabled
)

# Report template - similar to how ydata-profiling renders data in reports
REPORT_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Data Profile Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #333; }
        .data-table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        .data-table th, .data-table td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        .data-table th { background: #4CAF50; color: white; }
        .data-table tr:nth-child(even) { background: #f9f9f9; }
        .sample-section { margin: 20px 0; }
        .caption { font-style: italic; color: #666; margin-bottom: 10px; }
        .result-section { margin-top: 20px; padding: 15px; border-radius: 5px; }
        .success { background: #d4edda; border: 1px solid #c3e6cb; }
        .info { background: #d1ecf1; border: 1px solid #bee5eb; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Data Profile Report</h1>
        
        <div class="sample-section">
            <h2>Data Sample</h2>
            <p class="caption">{{ caption }}</p>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Column Name</th>
                        <th>Sample Value</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>{{ column_name }}</td>
                        <td>{{ sample_value }}</td>
                    </tr>
                </tbody>
            </table>
        </div>
        
        <div class="result-section info">
            {{ result_message }}
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return INDEX_CONTENT

def check_xss(page, flag, msg, tag):
    """Check if XSS was triggered using PhantomJS headless browser"""
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    base_url = os.getenv('BASE_URL', 'http://localhost:5000')
    url = base_url + '/' + fn
    try:
        of = open(fn, 'w')
        of.write(page)
        of.close()
        logging.info("Page: %s", page)
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
        logging.info("Result: %s", result)

    finally:
        os.unlink(fn)

    if msg == "":
        data = '<p>Enter data values to generate a profile report.</p>'
    else:
        if result == 'XSS':
            data = '<p class="success-msg"><strong>Congratulations!</strong> XSS detected in report. Flag: {0}</p>'.format(flag)
        elif result:
            data = '<p class="fail-msg">Alert triggered with "{0}" instead of "XSS"</p>'.format(cgi.escape(result))
        else:
            data = '<p class="fail-msg">No XSS detected. The data was rendered safely.</p>'
    return data


@app.route('/report')
def generate_report():
    """
    Generate a data profile report from user-supplied data.
    
    VULNERABILITY: User input is rendered through Jinja2 templates without
    autoescape enabled. This is identical to CVE in ydata-profiling where
    DataFrame values, column names, and captions could inject arbitrary HTML/JS.
    
    The vulnerability allows payloads like:
    - <img src=x onerror=alert('XSS')>
    - <script>alert('XSS')</script>
    - <svg onload=alert('XSS')>
    """
    # User-controlled inputs that flow into the template
    # These mirror how ydata-profiling accepts user data in DataFrames
    caption = request.args.get('caption', 'Sample data preview')
    column_name = request.args.get('column', 'value')
    sample_value = request.args.get('data', '')
    
    # VULNERABLE: Compile and render template without autoescape
    # This is the exact pattern from the CVE - Jinja2 Environment
    # initialized without autoescape=jinja2.select_autoescape()
    template = template_env.from_string(REPORT_TEMPLATE)
    
    # Render the report with user-controlled data
    # No escaping happens because autoescape=False
    rendered_html = template.render(
        caption=caption,
        column_name=column_name,
        sample_value=sample_value,
        result_message=""
    )
    
    # Check if XSS payload executed
    result_msg = check_xss(rendered_html, flags[0], sample_value, 'xss_medium')
    
    # Re-render with result message
    final_html = template.render(
        caption=caption,
        column_name=column_name,
        sample_value=sample_value,
        result_message=result_msg
    )
    
    return final_html


# Keep backward compatibility with old endpoint
@app.route('/page')
def xss22():
    """Legacy endpoint - redirects to new report generator"""
    return '''
    <html>
    <head><title>Redirecting...</title></head>
    <body>
        <p>This endpoint has been deprecated. Please use <a href="/report">/report</a> instead.</p>
        <p>Example: <code>/report?data=your_value&amp;column=column_name&amp;caption=your_caption</code></p>
    </body>
    </html>
    '''


if __name__ == '__main__':
    app.run(debug=True)
