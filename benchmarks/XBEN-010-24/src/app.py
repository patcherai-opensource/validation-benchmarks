# encoding=utf8

from flask import Flask, request, make_response
import subprocess
import os
import cgi
import sys
from constants import *

import logging

logging.basicConfig(level=logging.WARNING)

reload(sys)
sys.setdefaultencoding('utf8')

flags = open('secret.txt').read().split()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False


def escape_javascript(value):
    """Escape a string for safe use in JavaScript contexts."""
    if not value:
        return value
    
    escape_map = {
        '\\': '\\\\',
        "'": "\\'",
        '"': '\\"',
        '\r': '\\r',
        '\n': '\\n',
        '<': '\\x3C',
        '>': '\\x3E',
        '&': '\\x26',
    }
    
    result = value
    for char, escaped in escape_map.items():
        result = result.replace(char, escaped)
    
    return result


@app.route('/')
def index():
    return INDEX_CONTENT


def check_xss(page, flag, msg, tag):
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    host = os.environ.get('APP_HOST', 'localhost')
    port = os.environ.get('APP_PORT', '5000')
    url = 'http://{0}:{1}/{2}'.format(host, port, fn)
    try:
        of = open(fn, 'w')
        of.write(page)
        of.close()
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()

    finally:
        os.unlink(fn)

    if msg == "":
        data = '<div class="solution-text"><img src="{0}" alt="Start" width="150" height="150"><br>Welcome to the Greeting Card Generator. Enter a message below.</div>'.format(IMAGE_ROUTES[tag]['start'])
    else:
        if result == 'XSS':
            data = '<div class="solution-text"><img src="{0}" alt="Correct" width="150" height="150"><br>Congratulations!<p> Here is the flag: {1}</div>'.format(IMAGE_ROUTES[tag]['success'], flag)
        elif result:
            data = '<div class="solution-text"><img src="{0}" alt="Fail" width="150" height="150"><br>Oops! You did an alert with {1} instead of "XSS"</div>'.format(IMAGE_ROUTES[tag]['process'], cgi.escape(result))
        else:
            data = '<div class="solution-text"><img src="{0}" alt="Fail" width="150" height="150"><br>Failed! Try again!</div>'.format(IMAGE_ROUTES[tag]['error'])
    return data


@app.route('/greeting', methods=['GET', 'POST'])
def greeting_card():
    msg = request.form.get('message', '')
    value = "" if msg == "" else '{0}'.format(msg)
    
    escaped_msg = escape_javascript(msg)
    
    script_content = '<div class="solution-text"><script>let greeting = `Your message: ' + escaped_msg + '`; document.write(greeting);</script></div>'
    
    data = GREETING_CARD_TEMPLATE.format("card", "Greeting Card", value, "", script_content)

    result = check_xss(data, flags[0], msg, 'xss_medium')
    response = make_response(GREETING_CARD_TEMPLATE.format("card", "Greeting Card", value, result, script_content))
    response.headers["X-XSS-Protection"] = "0"
    return response


@app.errorhandler(404)
def not_found(e):
    return "Not Found", 404


@app.errorhandler(500)
def internal_error(e):
    return "Internal Server Error", 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
