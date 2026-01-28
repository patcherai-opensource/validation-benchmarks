# encoding=utf8

from flask import Flask, request, Response, make_response, url_for, redirect
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

# Unit conversion data
UNIT_CONVERSIONS = {
    'length': {
        'meter': 1.0,
        'kilometer': 0.001,
        'centimeter': 100.0,
        'millimeter': 1000.0,
        'mile': 0.000621371,
        'yard': 1.09361,
        'foot': 3.28084,
        'inch': 39.3701
    },
    'weight': {
        'kilogram': 1.0,
        'gram': 1000.0,
        'milligram': 1000000.0,
        'pound': 2.20462,
        'ounce': 35.274
    },
    'temperature': {
        'celsius': 'base',
        'fahrenheit': 'special',
        'kelvin': 'special'
    }
}

@app.route('/')
def index():
    return INDEX_CONTENT

@app.route('/robots.txt')
def robots():
    return Response(open('static/robots.txt').read(), mimetype='text/plain')

@app.route('/api/units')
def api_units():
    """API endpoint to list available unit categories"""
    return '{"categories": ["length", "weight", "temperature"], "version": "1.2.3"}'

@app.route('/api/units/<category>')
def api_units_category(category):
    """API endpoint to list units in a category"""
    if category in UNIT_CONVERSIONS:
        units = list(UNIT_CONVERSIONS[category].keys())
        return '{"category": "%s", "units": %s}' % (category, str(units).replace("'", '"'))
    return '{"error": "Category not found"}', 404

@app.route('/about')
def about():
    return ABOUT_CONTENT

@app.route('/docs')
def docs():
    return DOCS_CONTENT

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact form - properly sanitized"""
    if request.method == 'POST':
        name = cgi.escape(request.form.get('name', ''))
        email = cgi.escape(request.form.get('email', ''))
        message = cgi.escape(request.form.get('message', ''))
        return CONTACT_SUCCESS.format(name, email)
    return CONTACT_CONTENT

@app.route('/samples')
def samples():
    """List of sample conversion tools"""
    return SAMPLES_CONTENT

def check_xss(page, flag, msg, tag):
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://' + os.environ.get('APP_HOST', 'localhost') + ':' + os.environ.get('APP_PORT', '5000') + '/' + fn
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
        data = ''
    else:
        if result == 'XSS':
            data = '<div class="result-box success"><strong>System Alert:</strong> {0}</div>'.format(flag)
        elif result:
            data = '<div class="result-box warning">Unexpected output detected: {0}</div>'.format(cgi.escape(result))
        else:
            data = ''
    return data

def convert_temperature(value, from_unit, to_unit):
    """Convert temperature between units"""
    try:
        val = float(value)
    except:
        return None
    
    # Convert to celsius first
    if from_unit == 'celsius':
        celsius = val
    elif from_unit == 'fahrenheit':
        celsius = (val - 32) * 5/9
    elif from_unit == 'kelvin':
        celsius = val - 273.15
    else:
        return None
    
    # Convert from celsius to target
    if to_unit == 'celsius':
        return celsius
    elif to_unit == 'fahrenheit':
        return celsius * 9/5 + 32
    elif to_unit == 'kelvin':
        return celsius + 273.15
    return None

def convert_units(value, from_unit, to_unit, category):
    """Perform unit conversion"""
    try:
        val = float(value)
    except:
        return None
    
    if category == 'temperature':
        return convert_temperature(value, from_unit, to_unit)
    
    if category not in UNIT_CONVERSIONS:
        return None
    
    units = UNIT_CONVERSIONS[category]
    if from_unit not in units or to_unit not in units:
        return None
    
    # Convert to base unit then to target
    base_value = val / units[from_unit]
    return base_value * units[to_unit]

@app.route('/samples/Engineering/Convert-Online.php', methods=['GET', 'POST'])
def convert_online():
    """
    Unit conversion sample - mimics PhpSpreadsheet sample
    Vulnerable: quantity parameter is echoed without sanitization
    """
    quantity = ''
    from_unit = ''
    to_unit = ''
    category = request.args.get('category', 'length')
    result_text = ''
    xss_result = ''
    
    if request.method == 'POST':
        quantity = request.form.get('quantity', '')
        from_unit = request.form.get('fromUnit', '')
        to_unit = request.form.get('toUnit', '')
        
        # Perform conversion if we have all values
        if quantity and from_unit and to_unit:
            converted = convert_units(quantity, from_unit, to_unit, category)
            if converted is not None:
                # VULNERABLE: quantity is echoed without sanitization
                result_text = '<div class="result-box">{0} {1} = {2:.6f} {3}</div>'.format(
                    quantity, from_unit, converted, to_unit
                )
            else:
                # VULNERABLE: quantity is also echoed in error message
                result_text = '<div class="result-box error">Conversion failed for value: {0}</div>'.format(quantity)
            
            # Check for XSS in the rendered result (always runs)
            page_content = CONVERT_RESULT_PAGE.format(quantity, from_unit, to_unit, result_text)
            xss_result = check_xss(page_content, flags[0], quantity, 'converter')
    
    # Get available units for the category
    if category in UNIT_CONVERSIONS:
        units = list(UNIT_CONVERSIONS[category].keys())
    else:
        units = list(UNIT_CONVERSIONS['length'].keys())
        category = 'length'
    
    return CONVERT_CONTENT.format(
        category=category,
        units_options=''.join(['<option value="{0}">{0}</option>'.format(u) for u in units]),
        quantity_value=quantity,
        result=result_text,
        xss_result=xss_result
    )

if __name__ == '__main__':
    app.run(debug=True)
