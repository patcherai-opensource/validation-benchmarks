# encoding=utf8

from flask import Flask, request, Response, make_response, url_for, redirect
import string
import subprocess
import os
import re
import cgi
import urllib
import sys

from phantomjs import Phantom

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flag = open('secret.txt').read().strip()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False

phantom = Phantom()

# Supported currencies for the number format wizard
CURRENCIES = {
    'USD': {'symbol': '$', 'name': 'US Dollar'},
    'EUR': {'symbol': u'\u20ac', 'name': 'Euro'},
    'GBP': {'symbol': u'\u00a3', 'name': 'British Pound'},
    'JPY': {'symbol': u'\u00a5', 'name': 'Japanese Yen'},
    'CNY': {'symbol': u'\u00a5', 'name': 'Chinese Yuan'},
    'INR': {'symbol': u'\u20b9', 'name': 'Indian Rupee'},
    'BRL': {'symbol': 'R$', 'name': 'Brazilian Real'},
    'CAD': {'symbol': 'C$', 'name': 'Canadian Dollar'},
    'AUD': {'symbol': 'A$', 'name': 'Australian Dollar'},
    'CHF': {'symbol': 'CHF', 'name': 'Swiss Franc'},
}


def generate_format_mask(currency, decimals, thousands, position, spacing):
    """Generate a number format mask similar to PhpSpreadsheet Wizard."""
    sep = ',' if thousands else ''
    dec = '.' + '0' * decimals if decimals > 0 else ''
    
    if position:
        if spacing:
            mask = '{} #{}0{}'.format(currency, sep, dec)
        else:
            mask = '{}#{}0{}'.format(currency, sep, dec)
    else:
        if spacing:
            mask = '#{}0{} {}'.format(sep, dec, currency)
        else:
            mask = '#{}0{}{}'.format(sep, dec, currency)
    return mask


def format_number(value, mask, currency, decimals, thousands):
    """Format a number using the generated mask."""
    try:
        num = float(value)
    except (ValueError, TypeError):
        num = 1234.56
    
    if thousands:
        int_part = int(abs(num))
        formatted_int = '{:,}'.format(int_part)
    else:
        formatted_int = str(int(abs(num)))
    
    if decimals > 0:
        dec_part = ('{:.' + str(decimals) + 'f}').format(abs(num) % 1)[1:]
    else:
        dec_part = ''
    
    sign = '-' if num < 0 else ''
    return sign + formatted_int + dec_part


@app.route('/')
def index():
    return '''<!DOCTYPE html>
<html>
<head>
    <title>PhpSpreadsheet - Samples</title>
    <link rel="stylesheet" href="/static/css/samples.css">
</head>
<body>
    <div class="container">
        <h1>PhpSpreadsheet Samples</h1>
        <p class="description">Browse the sample scripts to learn how to use PhpSpreadsheet.</p>
        <div class="samples-list">
            <div class="sample-group">
                <h2>Wizards</h2>
                <ul>
                    <li>
                        <h3>NumberFormat</h3>
                        <ul>
                            <li><a href="/samples/Wizards/NumberFormat/Currency">Currency Format Wizard</a></li>
                        </ul>
                    </li>
                </ul>
            </div>
            <div class="sample-group">
                <h2>Basic</h2>
                <ul>
                    <li><a href="/samples/Basic/HelloWorld">Hello World</a></li>
                    <li><a href="/samples/Basic/CellStyles">Cell Styles</a></li>
                </ul>
            </div>
            <div class="sample-group">
                <h2>Reader</h2>
                <ul>
                    <li><a href="/samples/Reader/Xlsx">Read XLSX</a></li>
                    <li><a href="/samples/Reader/Csv">Read CSV</a></li>
                </ul>
            </div>
        </div>
    </div>
</body>
</html>'''


@app.route('/samples/Basic/HelloWorld')
def hello_world():
    return '''<!DOCTYPE html>
<html>
<head>
    <title>PhpSpreadsheet - Hello World</title>
    <link rel="stylesheet" href="/static/css/samples.css">
</head>
<body>
    <div class="container">
        <h1>Hello World</h1>
        <p>This sample demonstrates basic spreadsheet creation.</p>
        <div class="log-output">
            <h2>Execution Log</h2>
            <div class="log-entry">Creating new Spreadsheet object</div>
            <div class="log-entry">Setting cell A1 to "Hello World"</div>
            <div class="log-entry">Writing output to HelloWorld.xlsx</div>
            <div class="log-entry success">Done. File written successfully.</div>
        </div>
        <p><a href="/">Back to samples</a></p>
    </div>
</body>
</html>'''


@app.route('/samples/Basic/CellStyles')
def cell_styles():
    return '''<!DOCTYPE html>
<html>
<head>
    <title>PhpSpreadsheet - Cell Styles</title>
    <link rel="stylesheet" href="/static/css/samples.css">
</head>
<body>
    <div class="container">
        <h1>Cell Styles</h1>
        <p>This sample demonstrates cell formatting and styles.</p>
        <div class="log-output">
            <h2>Execution Log</h2>
            <div class="log-entry">Creating new Spreadsheet object</div>
            <div class="log-entry">Applying bold font to A1</div>
            <div class="log-entry">Setting background color on B2</div>
            <div class="log-entry">Applying border styles to range A1:D4</div>
            <div class="log-entry success">Done. File written successfully.</div>
        </div>
        <p><a href="/">Back to samples</a></p>
    </div>
</body>
</html>'''


@app.route('/samples/Reader/Xlsx')
def reader_xlsx():
    return '''<!DOCTYPE html>
<html>
<head>
    <title>PhpSpreadsheet - Read XLSX</title>
    <link rel="stylesheet" href="/static/css/samples.css">
</head>
<body>
    <div class="container">
        <h1>Read XLSX</h1>
        <p>This sample demonstrates reading an XLSX file.</p>
        <div class="log-output">
            <h2>Execution Log</h2>
            <div class="log-entry">Loading file: sample.xlsx</div>
            <div class="log-entry">Reading worksheet: Sheet1</div>
            <div class="log-entry">Found 15 rows of data</div>
            <div class="log-entry success">Done.</div>
        </div>
        <p><a href="/">Back to samples</a></p>
    </div>
</body>
</html>'''


@app.route('/samples/Reader/Csv')
def reader_csv():
    return '''<!DOCTYPE html>
<html>
<head>
    <title>PhpSpreadsheet - Read CSV</title>
    <link rel="stylesheet" href="/static/css/samples.css">
</head>
<body>
    <div class="container">
        <h1>Read CSV</h1>
        <p>This sample demonstrates reading a CSV file.</p>
        <div class="log-output">
            <h2>Execution Log</h2>
            <div class="log-entry">Loading file: sample.csv</div>
            <div class="log-entry">Delimiter detected: comma</div>
            <div class="log-entry">Found 42 rows of data</div>
            <div class="log-entry success">Done.</div>
        </div>
        <p><a href="/">Back to samples</a></p>
    </div>
</body>
</html>'''


def check_xss_page(html_content):
    """Use PhantomJS to check if XSS alert was triggered."""
    proc = subprocess.Popen(
        ["timeout", "5", "phantomjs", "check.js"],
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE
    )
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    host = os.environ.get('APP_HOST', 'localhost')
    port = os.environ.get('APP_PORT', '5000')
    url = 'http://{}:{}/{}'.format(host, port, fn)
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


@app.route('/samples/Wizards/NumberFormat/Currency', methods=['GET', 'POST'])
def currency_wizard():
    """
    Number Format Wizard - Currency

    This sample demonstrates the NumberFormat Wizard for Currency formatting.
    Select a currency and formatting options to see the generated format mask.
    """
    log_entries = []
    result_html = ''

    if request.method == 'POST':
        currency = request.form.get('currency', '')
        decimals_str = request.form.get('decimals', '2')
        thousands = 'thousands' in request.form
        position = request.form.get('position', '1')
        spacing = request.form.get('spacing', '0')

        try:
            decimals = int(decimals_str)
            if decimals < 0 or decimals > 6:
                decimals = 2
        except (ValueError, TypeError):
            decimals = 2

        try:
            pos_bool = bool(int(position))
        except (ValueError, TypeError):
            pos_bool = True

        try:
            space_bool = bool(int(spacing))
        except (ValueError, TypeError):
            space_bool = False

        mask = generate_format_mask(currency, decimals, thousands, pos_bool, space_bool)

        # Log the wizard execution - mirrors $helper->log() in the PHP version
        log_entries.append('Creating new Wizard\Currency for currency: {}'.format(currency))
        log_entries.append('Setting decimal places: {}'.format(decimals))
        log_entries.append('Thousands separator: {}'.format('enabled' if thousands else 'disabled'))
        log_entries.append('Currency position: {}'.format('before' if pos_bool else 'after'))
        log_entries.append('Spacing: {}'.format('with space' if space_bool else 'no space'))

        # Generate example formatted values
        examples = [1234.56, 9876543.21, 0.99, -500.00, 42.0]
        example_rows = ''
        for val in examples:
            formatted = format_number(val, mask, currency, decimals, thousands)
            if pos_bool:
                if space_bool:
                    display = '{} {}'.format(currency, formatted)
                else:
                    display = '{}{}'.format(currency, formatted)
            else:
                if space_bool:
                    display = '{} {}'.format(formatted, currency)
                else:
                    display = '{}{}'.format(formatted, currency)

            example_rows += '<tr><td>{}</td><td>{}</td></tr>\n'.format(val, display)

        log_entries.append('Generated format mask: {}'.format(mask))
        log_entries.append('Code: $wizard = new Wizard\\Currency(\'{}\', {}, {}, {}, {});'.format(
            currency, decimals, 'true' if thousands else 'false',
            'true' if pos_bool else 'false', 'true' if space_bool else 'false'
        ))

        # Build the full page for XSS checking
        log_html = ''
        for entry in log_entries:
            log_html += '<div class="log-entry">{}</div>\n'.format(entry)

        page_html = u'''<!DOCTYPE html>
<html>
<head>
    <title>PhpSpreadsheet - Currency Format Wizard</title>
    <link rel="stylesheet" href="/static/css/samples.css">
</head>
<body>
    <div class="container">
        <h1>Number Format Wizard - Currency</h1>
        <div class="log-output">
            <h2>Execution Log</h2>
            {}
            <div class="log-entry success">Format mask generated successfully.</div>
        </div>
        <div class="result-section">
            <h2>Result</h2>
            <p>Format Mask: <code>{}</code></p>
            <table class="result-table">
                <thead><tr><th>Value</th><th>Formatted ({})</th></tr></thead>
                <tbody>{}</tbody>
            </table>
        </div>
    </div>
</body>
</html>'''.format(log_html, mask, currency, example_rows)

        # Check for XSS execution
        xss_result = check_xss_page(page_html)

        if xss_result == 'XSS':
            result_html = '<div class="log-entry success">Flag: {}</div>'.format(flag)
        elif xss_result:
            result_html = '<div class="log-entry error">Alert detected: {} (expected "XSS")</div>'.format(cgi.escape(xss_result))

        # Build the response page
        log_output = ''
        for entry in log_entries:
            log_output += '<div class="log-entry">{}</div>\n'.format(entry)

        return u'''<!DOCTYPE html>
<html>
<head>
    <title>PhpSpreadsheet - Currency Format Wizard</title>
    <link rel="stylesheet" href="/static/css/samples.css">
</head>
<body>
    <div class="container">
        <h1>Number Format Wizard - Currency</h1>
        {}
        <div class="log-output">
            <h2>Execution Log</h2>
            {}
            <div class="log-entry success">Format mask generated successfully.</div>
        </div>
        <div class="result-section">
            <h2>Result</h2>
            <p>Format Mask: <code>{}</code></p>
            <table class="result-table">
                <thead><tr><th>Value</th><th>Formatted ({})</th></tr></thead>
                <tbody>{}</tbody>
            </table>
        </div>
        <p><a href="/samples/Wizards/NumberFormat/Currency">Try another format</a> | <a href="/">Back to samples</a></p>
    </div>
</body>
</html>'''.format(result_html, log_output, mask, currency, example_rows)

    # GET request - show the form
    currency_options = ''
    for code, info in sorted(CURRENCIES.items()):
        currency_options += '<option value="{}">{} ({})</option>\n'.format(
            cgi.escape(code, quote=True), cgi.escape(info['name']), cgi.escape(info['symbol'])
        )

    return '''<!DOCTYPE html>
<html>
<head>
    <title>PhpSpreadsheet - Currency Format Wizard</title>
    <link rel="stylesheet" href="/static/css/samples.css">
</head>
<body>
    <div class="container">
        <h1>Number Format Wizard - Currency</h1>
        <p>This sample demonstrates the NumberFormat Wizard for Currency formatting.
        Select a currency and formatting options, then click "Generate" to see the format mask and example output.</p>

        <form method="post" class="wizard-form">
            <div class="form-group">
                <label for="currency">Currency Symbol / Code:</label>
                <input type="text" id="currency" name="currency" value="$" 
                       placeholder="Enter currency symbol or code"
                       list="currency-list">
                <datalist id="currency-list">
                    ''' + currency_options + '''
                </datalist>
                <small>Type a custom currency symbol or select from the list</small>
            </div>

            <div class="form-group">
                <label for="decimals">Decimal Places:</label>
                <select id="decimals" name="decimals">
                    <option value="0">0</option>
                    <option value="1">1</option>
                    <option value="2" selected>2</option>
                    <option value="3">3</option>
                    <option value="4">4</option>
                </select>
            </div>

            <div class="form-group">
                <label>
                    <input type="checkbox" name="thousands" checked>
                    Use Thousands Separator
                </label>
            </div>

            <div class="form-group">
                <label>Currency Position:</label>
                <select name="position">
                    <option value="1" selected>Before number</option>
                    <option value="0">After number</option>
                </select>
            </div>

            <div class="form-group">
                <label>Spacing:</label>
                <select name="spacing">
                    <option value="0" selected>No space</option>
                    <option value="1">Space between symbol and number</option>
                </select>
            </div>

            <div class="form-group">
                <input type="submit" value="Generate Format" class="btn-generate">
            </div>
        </form>

        <p><a href="/">Back to samples</a></p>
    </div>
</body>
</html>'''


@app.errorhandler(404)
def page_not_found(e):
    return '''<!DOCTYPE html>
<html>
<head><title>404 - Not Found</title><link rel="stylesheet" href="/static/css/samples.css"></head>
<body>
<div class="container">
    <h1>404 - Page Not Found</h1>
    <p>The requested sample was not found.</p>
    <p><a href="/">Back to samples</a></p>
</div>
</body>
</html>''', 404


@app.errorhandler(500)
def internal_error(e):
    return '''<!DOCTYPE html>
<html>
<head><title>500 - Internal Server Error</title><link rel="stylesheet" href="/static/css/samples.css"></head>
<body>
<div class="container">
    <h1>500 - Internal Server Error</h1>
    <p>An unexpected error occurred.</p>
    <p><a href="/">Back to samples</a></p>
</div>
</body>
</html>''', 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
