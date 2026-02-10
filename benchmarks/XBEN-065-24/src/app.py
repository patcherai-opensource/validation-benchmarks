# encoding=utf8

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
app.config['PROPAGATE_EXCEPTIONS'] = False

phantom = Phantom()

ALLOWED_CURRENCIES = ['$', u'\u20ac', u'\u00a3', u'\u00a5']

@app.route('/')
def index():
    return INDEX_CONTENT

def check_xss(page, flag, msg, tag):
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://' + os.environ.get('FLASK_HOST', 'localhost') + ':' + os.environ.get('FLASK_PORT', '5000') + '/' + fn
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
        return None
    else:
        if result == 'XSS':
            return flag
        else:
            return None


@app.route('/samples/Wizards/NumberFormat/Accounting', methods=['GET', 'POST'])
def number_format_wizard():
    if request.method == 'GET':
        return ACCOUNTING_FORM_CONTENT
    
    number = request.form.get('number', '1234.5678')
    currency = request.form.get('currency', '$')
    decimals = request.form.get('decimals', '2')
    position = request.form.get('position', '1')
    spacing = request.form.get('spacing', '0')
    
    try:
        num_value = float(number)
        dec_value = int(decimals)
        pos_value = int(position)
        space_value = int(spacing)
    except ValueError:
        num_value = 1234.5678
        dec_value = 2
        pos_value = 1
        space_value = 0
    
    formatted_number = ("{:,." + str(dec_value) + "f}").format(num_value)
    
    spacing_char = " " if space_value == 1 else ""
    
    if pos_value == 1:
        display_value = currency + spacing_char + formatted_number
    else:
        display_value = formatted_number + spacing_char + currency
    
    result_html = ACCOUNTING_RESULT_CONTENT.format(
        currency=currency,
        number=number,
        decimals=decimals,
        position=position,
        spacing=spacing,
        display_value=display_value
    )
    
    xss_result = check_xss(result_html, flags[0], currency, 'xss_easy')
    
    if xss_result:
        result_html = ACCOUNTING_RESULT_WITH_FLAG_CONTENT.format(
            currency=currency,
            number=number,
            decimals=decimals,
            position=position,
            spacing=spacing,
            display_value=display_value,
            flag=xss_result
        )
    
    return result_html


@app.errorhandler(404)
def not_found(e):
    return Response("Not Found", status=404, mimetype='text/plain')

@app.errorhandler(500)
def internal_error(e):
    return Response("Internal Server Error", status=500, mimetype='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
