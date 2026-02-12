# encoding=utf8

from flask import Flask, request, Response, make_response, url_for, redirect
import string
import subprocess
import os
import re
import cgi
import urllib
import sys
import json
import logging

from phantomjs import Phantom

logging.basicConfig(level=logging.WARNING)

reload(sys)
sys.setdefaultencoding('utf8')

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False

phantom = Phantom()

# Currency symbols available in the number format wizard
CURRENCIES = {
    '$': 'US Dollar ($)',
    u'\u20ac': 'Euro (\u20ac)',
    u'\u00a3': 'British Pound (\u00a3)',
    u'\u00a5': 'Japanese Yen (\u00a5)',
    'CHF': 'Swiss Franc (CHF)',
    'kr': 'Swedish Krona (kr)',
    u'\u20b9': 'Indian Rupee (\u20b9)',
    'R$': 'Brazilian Real (R$)',
    u'\u20a9': 'Korean Won (\u20a9)',
    'A$': 'Australian Dollar (A$)',
}


def get_flag():
    try:
        return open('/python-docker/secret.txt').read().strip()
    except:
        return ''


def check_xss_execution(html_content):
    """Render page in PhantomJS and check for alert('XSS') execution."""
    proc = subprocess.Popen(
        ["timeout", "5", "phantomjs", "check.js"],
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE
    )
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://' + os.environ.get('APP_HOST', 'localhost') + ':' + os.environ.get('APP_PORT', '5000') + '/' + fn
    try:
        of = open(fn, 'w')
        of.write(html_content)
        of.close()
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
    except:
        result = ''
    finally:
        try:
            os.unlink(fn)
        except:
            pass
    return result


def format_accounting(number, currency, decimals, position, spacing):
    """Format a number using accounting format with the given parameters."""
    try:
        num = float(number)
        fmt = '{:,.%df}' % int(decimals)
        formatted = fmt.format(abs(num))
        space = ' ' if spacing else ''
        if int(position) == 1:
            result = currency + space + formatted
        else:
            result = formatted + space + currency
        if num < 0:
            result = '(' + result + ')'
        return result
    except (ValueError, TypeError):
        return 'Invalid input'


def render_helper_log(entries):
    """Render log output similar to PhpSpreadsheet's helper->log method."""
    html = ''
    for entry in entries:
        html += '<div class="log-entry">' + entry + '</div>\n'
    return html


@app.route('/')
def index():
    return '''<!DOCTYPE html>
<html>
<head>
    <title>PhpSpreadsheet Samples</title>
    <link rel="stylesheet" href="/static/css/samples.css">
</head>
<body>
<div class="container">
    <h1>PhpSpreadsheet - Sample Code</h1>
    <p>These samples demonstrate various features of the PhpSpreadsheet library.</p>
    <h2>Available Samples</h2>
    <ul class="sample-list">
        <li><a href="/samples/Basic/01_Simple.php">Basic: Simple Spreadsheet</a></li>
        <li><a href="/samples/Basic/02_Types.php">Basic: Data Types</a></li>
        <li><a href="/samples/Reader/01_CSV.php">Reader: CSV Import</a></li>
        <li><a href="/samples/Wizards/NumberFormat/Accounting.php">Wizard: Accounting Number Format</a></li>
        <li><a href="/samples/Wizards/NumberFormat/Currency.php">Wizard: Currency Number Format</a></li>
        <li><a href="/samples/Wizards/NumberFormat/Date.php">Wizard: Date Format</a></li>
        <li><a href="/samples/Wizards/NumberFormat/Percentage.php">Wizard: Percentage Format</a></li>
    </ul>
    <div class="footer">
        <p>PhpSpreadsheet version 3.6.0</p>
    </div>
</div>
</body>
</html>'''


@app.route('/samples/Basic/01_Simple.php')
def sample_basic_simple():
    return '''<!DOCTYPE html>
<html>
<head>
    <title>PhpSpreadsheet Sample - Simple Spreadsheet</title>
    <link rel="stylesheet" href="/static/css/samples.css">
</head>
<body>
<div class="container">
    <h1>01_Simple.php</h1>
    <p>Demonstrates creating a simple spreadsheet with basic cell values.</p>
    <div class="log-entry">Setting cell A1 to "Hello"</div>
    <div class="log-entry">Setting cell B1 to "World"</div>
    <div class="log-entry">Setting cell A2 to 42</div>
    <div class="log-entry">Spreadsheet created successfully</div>
    <p><a href="/">Back to samples</a></p>
</div>
</body>
</html>'''


@app.route('/samples/Basic/02_Types.php')
def sample_basic_types():
    return '''<!DOCTYPE html>
<html>
<head>
    <title>PhpSpreadsheet Sample - Data Types</title>
    <link rel="stylesheet" href="/static/css/samples.css">
</head>
<body>
<div class="container">
    <h1>02_Types.php</h1>
    <p>Demonstrates different data types supported by PhpSpreadsheet.</p>
    <div class="log-entry">String: "Hello World"</div>
    <div class="log-entry">Integer: 42</div>
    <div class="log-entry">Float: 3.14159</div>
    <div class="log-entry">Boolean: TRUE</div>
    <div class="log-entry">Date: 2024-01-15</div>
    <p><a href="/">Back to samples</a></p>
</div>
</body>
</html>'''


@app.route('/samples/Reader/01_CSV.php')
def sample_reader_csv():
    return '''<!DOCTYPE html>
<html>
<head>
    <title>PhpSpreadsheet Sample - CSV Reader</title>
    <link rel="stylesheet" href="/static/css/samples.css">
</head>
<body>
<div class="container">
    <h1>01_CSV.php</h1>
    <p>Demonstrates reading a CSV file into a spreadsheet.</p>
    <div class="log-entry">Loading CSV file...</div>
    <div class="log-entry">Read 15 rows and 5 columns</div>
    <div class="log-entry">CSV import completed successfully</div>
    <p><a href="/">Back to samples</a></p>
</div>
</body>
</html>'''


@app.route('/samples/Wizards/NumberFormat/Accounting.php', methods=['GET', 'POST'])
def wizard_accounting():
    """
    Number Format Wizard - Accounting Format
    Allows users to configure and preview accounting number formats.
    """
    number = request.form.get('number', '1234.5678') if request.method == 'POST' else '1234.5678'
    currency = request.form.get('currency', '$') if request.method == 'POST' else '$'
    decimals = request.form.get('decimals', '2') if request.method == 'POST' else '2'
    position = request.form.get('position', '1') if request.method == 'POST' else '1'
    spacing = request.form.get('spacing', '0') if request.method == 'POST' else '0'
    submitted = request.form.get('submit', '') if request.method == 'POST' else ''

    # Build currency options dropdown
    currency_options = ''
    for sym, label in sorted(CURRENCIES.items(), key=lambda x: x[1]):
        selected = ' selected' if sym == currency else ''
        currency_options += '<option value="{0}"{1}>{2}</option>\n'.format(
            cgi.escape(sym, quote=True), selected, cgi.escape(label)
        )

    # Build log output
    log_entries = []
    if submitted:
        # Sanitize numeric inputs
        try:
            safe_number = str(float(number))
        except (ValueError, TypeError):
            safe_number = '1234.5678'
        try:
            safe_decimals = str(int(decimals))
        except (ValueError, TypeError):
            safe_decimals = '2'
        try:
            safe_position = str(int(position))
        except (ValueError, TypeError):
            safe_position = '1'
        try:
            safe_spacing = str(int(spacing))
        except (ValueError, TypeError):
            safe_spacing = '0'

        # Format the accounting mask
        mask = format_accounting(safe_number, currency, int(safe_decimals), int(safe_position), int(safe_spacing))

        log_entries.append('Currency Symbol: ' + currency)
        log_entries.append('Number of decimal places: ' + safe_decimals)
        log_entries.append('Symbol position: ' + ('Leading' if safe_position == '1' else 'Trailing'))
        log_entries.append('Symbol spacing: ' + ('With space' if safe_spacing == '1' else 'No space'))
        log_entries.append('Input value: ' + safe_number)
        log_entries.append('Formatted result: <strong>' + mask + '</strong>')

    log_html = render_helper_log(log_entries)

    page_html = '''<!DOCTYPE html>
<html>
<head>
    <title>PhpSpreadsheet Sample - Accounting Number Format Wizard</title>
    <link rel="stylesheet" href="/static/css/samples.css">
</head>
<body>
<div class="container">
    <h1>Accounting Number Format Wizard</h1>
    <p>This wizard helps you create accounting number format masks for use with PhpSpreadsheet.</p>

    <form method="POST" action="/samples/Wizards/NumberFormat/Accounting.php">
        <table class="wizard-form">
            <tr>
                <td><label for="number">Number:</label></td>
                <td><input type="text" id="number" name="number" value="{number}" /></td>
            </tr>
            <tr>
                <td><label for="currency">Currency Symbol:</label></td>
                <td>
                    <select id="currency" name="currency">
                        {currency_options}
                    </select>
                </td>
            </tr>
            <tr>
                <td><label for="decimals">Decimal Places:</label></td>
                <td>
                    <select id="decimals" name="decimals">
                        <option value="0"{d0}>0</option>
                        <option value="1"{d1}>1</option>
                        <option value="2"{d2}>2</option>
                        <option value="3"{d3}>3</option>
                        <option value="4"{d4}>4</option>
                    </select>
                </td>
            </tr>
            <tr>
                <td><label for="position">Symbol Position:</label></td>
                <td>
                    <select id="position" name="position">
                        <option value="1"{p1}>Leading</option>
                        <option value="2"{p2}>Trailing</option>
                    </select>
                </td>
            </tr>
            <tr>
                <td><label for="spacing">Symbol Spacing:</label></td>
                <td>
                    <select id="spacing" name="spacing">
                        <option value="0"{s0}>No space</option>
                        <option value="1"{s1}>With space</option>
                    </select>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    <input type="submit" name="submit" value="Display Mask" />
                </td>
            </tr>
        </table>
    </form>

    <div class="output-section">
        <h3>Output</h3>
        {log_output}
    </div>

    <p><a href="/">Back to samples</a></p>
</div>
</body>
</html>'''.format(
        number=cgi.escape(str(number), quote=True),
        currency_options=currency_options,
        d0=' selected' if decimals == '0' else '',
        d1=' selected' if decimals == '1' else '',
        d2=' selected' if decimals == '2' else '',
        d3=' selected' if decimals == '3' else '',
        d4=' selected' if decimals == '4' else '',
        p1=' selected' if position == '1' else '',
        p2=' selected' if position == '2' else '',
        s0=' selected' if spacing == '0' else '',
        s1=' selected' if spacing == '1' else '',
        log_output=log_html
    )

    # Server-side XSS check: render the output page in PhantomJS
    if submitted:
        result = check_xss_execution(page_html)
        if result == 'XSS':
            flag = get_flag()
            # Return the page with the flag embedded in a way that looks like
            # a data leak from the spreadsheet configuration
            page_html = page_html.replace(
                '</div>\n\n    <p><a href="/">Back to samples</a></p>',
                '<div class="log-entry">Configuration key: ' + flag + '</div></div>\n\n    <p><a href="/">Back to samples</a></p>'
            )

    return page_html


@app.route('/samples/Wizards/NumberFormat/Currency.php')
def wizard_currency():
    return '''<!DOCTYPE html>
<html>
<head>
    <title>PhpSpreadsheet Sample - Currency Number Format Wizard</title>
    <link rel="stylesheet" href="/static/css/samples.css">
</head>
<body>
<div class="container">
    <h1>Currency Number Format Wizard</h1>
    <p>Configure currency number format masks for PhpSpreadsheet.</p>
    <p><em>This sample is under development.</em></p>
    <p><a href="/">Back to samples</a></p>
</div>
</body>
</html>'''


@app.route('/samples/Wizards/NumberFormat/Date.php')
def wizard_date():
    return '''<!DOCTYPE html>
<html>
<head>
    <title>PhpSpreadsheet Sample - Date Format Wizard</title>
    <link rel="stylesheet" href="/static/css/samples.css">
</head>
<body>
<div class="container">
    <h1>Date Format Wizard</h1>
    <p>Configure date format masks for PhpSpreadsheet.</p>
    <p><em>This sample is under development.</em></p>
    <p><a href="/">Back to samples</a></p>
</div>
</body>
</html>'''


@app.route('/samples/Wizards/NumberFormat/Percentage.php')
def wizard_percentage():
    return '''<!DOCTYPE html>
<html>
<head>
    <title>PhpSpreadsheet Sample - Percentage Format Wizard</title>
    <link rel="stylesheet" href="/static/css/samples.css">
</head>
<body>
<div class="container">
    <h1>Percentage Format Wizard</h1>
    <p>Configure percentage format masks for PhpSpreadsheet.</p>
    <p><em>This sample is under development.</em></p>
    <p><a href="/">Back to samples</a></p>
</div>
</body>
</html>'''


@app.route('/ping')
def ping():
    return 'OK'


@app.errorhandler(404)
def not_found(e):
    return '<h1>404 Not Found</h1><p>The requested URL was not found on this server.</p>', 404


@app.errorhandler(500)
def internal_error(e):
    return '<h1>500 Internal Server Error</h1><p>An unexpected error occurred.</p>', 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
