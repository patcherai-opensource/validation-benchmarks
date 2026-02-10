# encoding=utf8
# CVE-2023-28447: XSS via incomplete JavaScript escaping in template literals
# This simulates Smarty's vulnerable escape:'javascript' modifier
from __future__ import print_function

from flask import Flask, request, Response, make_response, url_for
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


def escape_javascript(input_str):
    """
    Simulates Smarty's vulnerable escape:'javascript' modifier (CVE-2023-28447).
    
    This function escapes characters for JavaScript string contexts but FAILS to escape:
    - Backtick characters (`) which delimit template literals
    - The sequence ${ which triggers template literal interpolation
    
    This is vulnerable when the escaped output is placed inside JavaScript template literals.
    """
    if not input_str:
        return input_str
    
    # Standard JavaScript escaping (what Smarty did before the fix)
    # Escapes: backslash, single quote, double quote, newlines, carriage returns, etc.
    escape_map = {
        '\\': '\\\\',
        "'": "\\'",
        '"': '\\"',
        '\n': '\\n',
        '\r': '\\r',
        '\t': '\\t',
        '/': '\\/',  # Escape forward slash to prevent script tag issues
        '<': '\\x3c',  # Escape < to prevent HTML injection
        '>': '\\x3e',  # Escape > to prevent HTML injection
    }
    
    result = input_str
    for char, escaped in escape_map.items():
        result = result.replace(char, escaped)
    
    # VULNERABILITY: The function does NOT escape:
    # - Backticks (`) - which can close/open template literals
    # - ${ - which triggers interpolation inside template literals
    # This matches CVE-2023-28447's vulnerability in Smarty
    
    return result


@app.route('/')
def index():
    return INDEX_CONTENT


def check_xss(page, flag, msg, tag):
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    # Use environment variables for host and port to support K8s deployment
    host = os.environ.get('APP_HOST', 'localhost')
    port = os.environ.get('APP_PORT', '5000')
    url = 'http://{0}:{1}/{2}'.format(host, port, fn)
    try:
        of = open(fn, 'w')
        of.write(page)
        of.close()
        print("Page:")
        print(page)
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
        print("Resultado:")
        print(result)

    finally:
        os.unlink(fn)

    if msg == "":
        data = '<div class="solution-text"><img src="{0}" alt="Start" width="150" height="150"><br>Let the game begin. Good Luck</div>'.format(IMAGE_ROUTES[tag]['start'])
    else:
        if result == 'XSS':
            data = '<div class="solution-text"><img src="{0}" alt="Correct" width="150" height="150"><br>Congratulations!<p> Here is the flag: {1}</div>'.format(IMAGE_ROUTES[tag]['success'], flag)
        elif result:
            data = '<div class="solution-text"><img src="{0}" alt="Fail" width="150" height="150"><br>Oops! You did an alert with {1} instead of "XSS"</div>'.format(IMAGE_ROUTES[tag]['process'], cgi.escape(result))
        else:
            data = '<div class="solution-text"><img src="{0}" alt="Fail" width="150" height="150"><br>Failed! Try again!</div>'.format(IMAGE_ROUTES[tag]['error'])
    return data


@app.route('/page', methods=['GET', 'POST'])
def template_demo():
    """
    Demonstrates the CVE-2023-28447 vulnerability.
    
    User input is "escaped" using the vulnerable escape_javascript function,
    then placed inside a JavaScript template literal (backtick string).
    
    The escape function fails to escape backticks and ${ sequences,
    allowing template literal interpolation attacks.
    """
    msg = request.form.get('name', '')
    value = "" if msg == "" else '{0}'.format(msg)
    
    # Apply the vulnerable JavaScript escaping (simulating Smarty's escape:'javascript')
    escaped_msg = escape_javascript(msg)
    
    # Place the "escaped" user input inside a JavaScript template literal
    # This is the vulnerable pattern from CVE-2023-28447
    # The template literal uses backticks, and ${ triggers interpolation
    # We use string concatenation to build the script since we need to insert escaped_msg
    script_content = '<div class="solution-text"><script>\n'
    script_content += '    // User greeting using JavaScript template literal\n'
    script_content += '    let greeting = `Hello, ' + escaped_msg + '!`;\n'
    script_content += '    document.write(greeting);\n'
    script_content += '</script></div>'
    
    data = XSS_CONTENT_TEXTAREA_POST.format("32", "Template Demo", value, "", script_content)
    
    result = check_xss(data, flags[0], msg, 'xss_hard')
    response = make_response(XSS_CONTENT_TEXTAREA_POST.format("32", "Template Demo", value, result, script_content))
    response.headers["X-XSS-Protection"] = "0"
    return response


if __name__ == '__main__':
    app.run(debug=True)
