# encoding=utf8

from flask import Flask, request, Response, make_response, url_for, redirect
import string
import subprocess
import os
import re
import sys
import json
import time

from phantomjs import Phantom

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flag_value = open('secret.txt').read().strip()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False

phantom = Phantom()

# Currency data used by the NumberFormat wizards
CURRENCIES = {
    'USD': {'symbol': '$', 'name': 'US Dollar', 'decimals': 2},
    'EUR': {'symbol': '\xe2\x82\xac', 'name': 'Euro', 'decimals': 2},
    'GBP': {'symbol': '\xc2\xa3', 'name': 'British Pound', 'decimals': 2},
    'JPY': {'symbol': '\xc2\xa5', 'name': 'Japanese Yen', 'decimals': 0},
    'CHF': {'symbol': 'CHF', 'name': 'Swiss Franc', 'decimals': 2},
    'CAD': {'symbol': 'C$', 'name': 'Canadian Dollar', 'decimals': 2},
    'AUD': {'symbol': 'A$', 'name': 'Australian Dollar', 'decimals': 2},
    'CNY': {'symbol': '\xc2\xa5', 'name': 'Chinese Yuan', 'decimals': 2},
    'INR': {'symbol': '\xe2\x82\xb9', 'name': 'Indian Rupee', 'decimals': 2},
    'BRL': {'symbol': 'R$', 'name': 'Brazilian Real', 'decimals': 2},
}

SAMPLE_VALUES = [1234.56, -1234.56, 0.5, 1000000, 42]


def format_number(value, currency_symbol, decimals, thousands, position, spacing):
    """Format a number with the given currency settings."""
    space = ' ' if spacing else ''
    if thousands:
        if decimals > 0:
            num_str = '{:,.{prec}f}'.format(abs(value), prec=decimals)
        else:
            num_str = '{:,.0f}'.format(abs(value))
    else:
        if decimals > 0:
            num_str = '{:.{prec}f}'.format(abs(value), prec=decimals)
        else:
            num_str = '{:.0f}'.format(abs(value))

    sign = '-' if value < 0 else ''

    if position:
        return '{}{}{}{}'.format(sign, currency_symbol, space, num_str)
    else:
        return '{}{}{}{}'.format(sign, num_str, space, currency_symbol)


def generate_mask(currency_symbol, decimals, thousands, position, spacing):
    """Generate a format mask string."""
    space = ' ' if spacing else ''
    dec_part = '.' + '0' * decimals if decimals > 0 else ''
    if thousands:
        num_mask = '#,##0' + dec_part
    else:
        num_mask = '0' + dec_part

    if position:
        return '{}{}{}'.format(currency_symbol, space, num_mask)
    else:
        return '{}{}{}'.format(num_mask, space, currency_symbol)


def verify_xss_in_page(html_content):
    """Render a page through the headless browser and check for JS execution."""
    proc = subprocess.Popen(
        ["timeout", "5", "phantomjs", "check.js"],
        stdout=subprocess.PIPE, stdin=subprocess.PIPE
    )
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    host = os.environ.get('APP_HOST', 'localhost')
    port = os.environ.get('APP_PORT', '5000')
    url = 'http://{}:{}/{}'.format(host, port, fn)
    result = ''
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


# ---- Page Templates ----

LAYOUT_HEADER = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{title} - PhpSpreadsheet Samples</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; background: #f8f9fa; color: #212529; }}
        .navbar {{ background: #343a40; padding: 0.75rem 1.5rem; color: #fff; }}
        .navbar a {{ color: #adb5bd; text-decoration: none; margin-right: 1rem; }}
        .navbar a:hover {{ color: #fff; }}
        .navbar .brand {{ font-weight: bold; color: #fff; font-size: 1.1rem; margin-right: 2rem; }}
        .container {{ max-width: 960px; margin: 2rem auto; padding: 0 1rem; }}
        .card {{ background: #fff; border: 1px solid #dee2e6; border-radius: 0.25rem; padding: 1.5rem; margin-bottom: 1.5rem; }}
        .card h2 {{ margin-bottom: 1rem; font-size: 1.25rem; }}
        h1 {{ margin-bottom: 1.5rem; }}
        table {{ width: 100%; border-collapse: collapse; margin: 1rem 0; }}
        table th, table td {{ text-align: left; padding: 0.5rem; border-bottom: 1px solid #dee2e6; }}
        table th {{ background: #e9ecef; }}
        label {{ display: block; margin-bottom: 0.25rem; font-weight: 600; }}
        input[type=text], input[type=number], select {{ width: 100%; padding: 0.375rem 0.75rem; border: 1px solid #ced4da; border-radius: 0.25rem; margin-bottom: 0.75rem; font-size: 1rem; }}
        input[type=checkbox] {{ margin-right: 0.5rem; }}
        .form-check {{ margin-bottom: 0.75rem; }}
        .btn {{ display: inline-block; padding: 0.5rem 1rem; background: #0d6efd; color: #fff; border: none; border-radius: 0.25rem; cursor: pointer; font-size: 1rem; text-decoration: none; }}
        .btn:hover {{ background: #0b5ed7; }}
        .btn-secondary {{ background: #6c757d; }}
        .btn-secondary:hover {{ background: #5c636a; }}
        .log-output {{ background: #f1f3f5; border: 1px solid #dee2e6; border-radius: 0.25rem; padding: 1rem; font-family: monospace; font-size: 0.875rem; white-space: pre-wrap; word-break: break-all; }}
        .breadcrumb {{ margin-bottom: 1rem; color: #6c757d; font-size: 0.9rem; }}
        .breadcrumb a {{ color: #0d6efd; text-decoration: none; }}
        .sample-list a {{ display: block; padding: 0.5rem 0; color: #0d6efd; text-decoration: none; border-bottom: 1px solid #f1f3f5; }}
        .sample-list a:hover {{ background: #f8f9fa; padding-left: 0.5rem; }}
        footer {{ text-align: center; padding: 2rem; color: #6c757d; font-size: 0.85rem; }}
    </style>
</head>
<body>
<div class="navbar">
    <a href="/" class="brand">PhpSpreadsheet</a>
    <a href="/samples">Samples</a>
    <a href="/samples/wizards">Wizards</a>
</div>
<div class="container">
"""

LAYOUT_FOOTER = """
</div>
<footer>PhpSpreadsheet Library &copy; 2024</footer>
</body>
</html>"""


@app.route('/')
def index():
    content = LAYOUT_HEADER.format(title="Home")
    content += """
    <h1>PhpSpreadsheet Sample Application</h1>
    <div class="card">
        <h2>Welcome</h2>
        <p>This is the sample application for the PhpSpreadsheet library. Use the navigation above to browse available samples and wizards.</p>
        <p style="margin-top:1rem;"><a class="btn" href="/samples">Browse Samples</a></p>
    </div>
    """
    content += LAYOUT_FOOTER
    return content


@app.route('/samples')
def samples_index():
    content = LAYOUT_HEADER.format(title="Samples")
    content += """
    <div class="breadcrumb"><a href="/">Home</a> / Samples</div>
    <h1>Available Samples</h1>
    <div class="card">
        <div class="sample-list">
            <a href="/samples/wizards">Wizards</a>
            <a href="/samples/reader">Reader Examples</a>
            <a href="/samples/writer">Writer Examples</a>
            <a href="/samples/calculations">Calculation Engine</a>
        </div>
    </div>
    """
    content += LAYOUT_FOOTER
    return content


@app.route('/samples/reader')
def samples_reader():
    content = LAYOUT_HEADER.format(title="Reader Examples")
    content += """
    <div class="breadcrumb"><a href="/">Home</a> / <a href="/samples">Samples</a> / Reader</div>
    <h1>Reader Examples</h1>
    <div class="card">
        <p>Reader examples demonstrate how to load spreadsheet files in various formats (XLSX, XLS, CSV, ODS).</p>
        <p style="margin-top:1rem; color:#6c757d;"><em>Sample files not included in this deployment.</em></p>
    </div>
    """
    content += LAYOUT_FOOTER
    return content


@app.route('/samples/writer')
def samples_writer():
    content = LAYOUT_HEADER.format(title="Writer Examples")
    content += """
    <div class="breadcrumb"><a href="/">Home</a> / <a href="/samples">Samples</a> / Writer</div>
    <h1>Writer Examples</h1>
    <div class="card">
        <p>Writer examples demonstrate how to create and save spreadsheet files in various formats.</p>
        <p style="margin-top:1rem; color:#6c757d;"><em>Sample files not included in this deployment.</em></p>
    </div>
    """
    content += LAYOUT_FOOTER
    return content


@app.route('/samples/calculations')
def samples_calculations():
    content = LAYOUT_HEADER.format(title="Calculation Engine")
    content += """
    <div class="breadcrumb"><a href="/">Home</a> / <a href="/samples">Samples</a> / Calculations</div>
    <h1>Calculation Engine</h1>
    <div class="card">
        <p>The calculation engine samples demonstrate formula parsing and evaluation capabilities.</p>
        <p style="margin-top:1rem; color:#6c757d;"><em>Sample files not included in this deployment.</em></p>
    </div>
    """
    content += LAYOUT_FOOTER
    return content


@app.route('/samples/wizards')
def wizards_index():
    content = LAYOUT_HEADER.format(title="Wizards")
    content += """
    <div class="breadcrumb"><a href="/">Home</a> / <a href="/samples">Samples</a> / Wizards</div>
    <h1>Number Format Wizards</h1>
    <div class="card">
        <p>These interactive wizards demonstrate the NumberFormat helper classes that simplify creating format masks for spreadsheet cells.</p>
        <div class="sample-list" style="margin-top:1rem;">
            <a href="/samples/wizards/number-format/currency">Currency Format Wizard</a>
            <a href="/samples/wizards/number-format/percentage">Percentage Format Wizard</a>
            <a href="/samples/wizards/number-format/accounting">Accounting Format Wizard</a>
            <a href="/samples/wizards/number-format/date-time">Date/Time Format Wizard</a>
        </div>
    </div>
    """
    content += LAYOUT_FOOTER
    return content


@app.route('/samples/wizards/number-format/percentage')
def wizard_percentage():
    content = LAYOUT_HEADER.format(title="Percentage Format")
    content += """
    <div class="breadcrumb"><a href="/">Home</a> / <a href="/samples">Samples</a> / <a href="/samples/wizards">Wizards</a> / Percentage</div>
    <h1>Percentage Number Format Wizard</h1>
    <div class="card">
        <p>The Percentage wizard helps create format masks for displaying values as percentages.</p>
        <p style="margin-top:1rem; color:#6c757d;"><em>Interactive demo coming soon.</em></p>
    </div>
    """
    content += LAYOUT_FOOTER
    return content


@app.route('/samples/wizards/number-format/accounting')
def wizard_accounting():
    content = LAYOUT_HEADER.format(title="Accounting Format")
    content += """
    <div class="breadcrumb"><a href="/">Home</a> / <a href="/samples">Samples</a> / <a href="/samples/wizards">Wizards</a> / Accounting</div>
    <h1>Accounting Number Format Wizard</h1>
    <div class="card">
        <p>The Accounting wizard helps create format masks for displaying values in accounting format with aligned currency symbols.</p>
        <p style="margin-top:1rem; color:#6c757d;"><em>Interactive demo coming soon.</em></p>
    </div>
    """
    content += LAYOUT_FOOTER
    return content


@app.route('/samples/wizards/number-format/date-time')
def wizard_datetime():
    content = LAYOUT_HEADER.format(title="Date/Time Format")
    content += """
    <div class="breadcrumb"><a href="/">Home</a> / <a href="/samples">Samples</a> / <a href="/samples/wizards">Wizards</a> / Date/Time</div>
    <h1>Date/Time Number Format Wizard</h1>
    <div class="card">
        <p>The Date/Time wizard helps create format masks for displaying date and time values.</p>
        <p style="margin-top:1rem; color:#6c757d;"><em>Interactive demo coming soon.</em></p>
    </div>
    """
    content += LAYOUT_FOOTER
    return content


@app.route('/samples/wizards/number-format/currency', methods=['GET', 'POST'])
def wizard_currency():
    """Currency Number Format Wizard - demonstrates the Currency format mask wizard."""

    # Build the available currencies dropdown options
    currency_options = ''
    for code, info in sorted(CURRENCIES.items()):
        currency_options += '<option value="' + code + '">' + code + ' - ' + info['name'] + ' (' + info['symbol'] + ')</option>\n'

    if request.method == 'GET':
        content = LAYOUT_HEADER.format(title="Currency Format")
        content += """
        <div class="breadcrumb"><a href="/">Home</a> / <a href="/samples">Samples</a> / <a href="/samples/wizards">Wizards</a> / Currency</div>
        <h1>Currency Number Format Wizard</h1>
        <div class="card">
            <h2>Configure Currency Format</h2>
            <form method="post" action="/samples/wizards/number-format/currency">
                <label for="currency">Currency Symbol</label>
                <input type="text" id="currency" name="currency" value="$" placeholder="Enter currency symbol...">

                <label for="decimals">Decimal Places</label>
                <input type="number" id="decimals" name="decimals" value="2" min="0" max="6">

                <div class="form-check">
                    <input type="checkbox" id="thousands" name="thousands" checked>
                    <label for="thousands" style="display:inline;">Use thousands separator</label>
                </div>

                <label for="position">Symbol Position</label>
                <select id="position" name="position">
                    <option value="1" selected>Before number (prefix)</option>
                    <option value="0">After number (suffix)</option>
                </select>

                <div class="form-check">
                    <input type="checkbox" id="spacing" name="spacing" checked>
                    <label for="spacing" style="display:inline;">Space between symbol and number</label>
                </div>

                <button type="submit" class="btn">Generate Format</button>
            </form>
        </div>
        """
        content += LAYOUT_FOOTER
        return content

    # POST: Process the form submission
    currency = request.form.get('currency', '$')
    try:
        decimals = int(request.form.get('decimals', '2'))
    except (ValueError, TypeError):
        decimals = 2
    thousands = 'thousands' in request.form
    try:
        position = bool(int(request.form.get('position', '1')))
    except (ValueError, TypeError):
        position = True
    spacing = 'spacing' in request.form

    # Clamp decimals to valid range
    if decimals < 0:
        decimals = 0
    elif decimals > 6:
        decimals = 6

    # Generate the format mask
    mask = generate_mask(currency, decimals, thousands, position, spacing)

    # Format sample values
    formatted_rows = ''
    for val in SAMPLE_VALUES:
        formatted = format_number(val, currency, decimals, thousands, position, spacing)
        formatted_rows += '<tr><td>' + str(val) + '</td><td>' + formatted + '</td></tr>\n'

    # Build the code example that was "executed"
    code_example = '$wizard = new NumberFormat\\Wizard\\Currency("' + currency + '", ' + str(decimals) + ', '
    code_example += ('true' if thousands else 'false') + ', '
    code_example += ('Wizard::LEADING_SYMBOL' if position else 'Wizard::TRAILING_SYMBOL') + ', '
    code_example += ('true' if spacing else 'false') + ');\n'
    code_example += '$mask = $wizard->format();'

    # Build the result page - the currency value is reflected in the log output
    # mirroring how $helper->log() works in the PHP samples
    content = LAYOUT_HEADER.format(title="Currency Format Result")

    result_html = '<div class="breadcrumb"><a href="/">Home</a> / <a href="/samples">Samples</a> / <a href="/samples/wizards">Wizards</a> / Currency</div>\n'
    result_html += '<h1>Currency Number Format Wizard</h1>\n'
    result_html += '<div class="card">\n'
    result_html += '<h2>Execution Log</h2>\n'
    result_html += '<div class="log-output">Currency Wizard for: ' + currency + '\n\n'
    result_html += 'Code executed:\n' + code_example + '\n\n'
    result_html += 'Result mask: ' + mask + '</div>\n'
    result_html += '</div>\n'
    result_html += '<div class="card">\n'
    result_html += '<h2>Sample Output using mask: ' + mask + '</h2>\n'
    result_html += '<table>\n<thead><tr><th>Raw Value</th><th>Formatted (' + currency + ')</th></tr></thead>\n'
    result_html += '<tbody>' + formatted_rows + '</tbody>\n</table>\n</div>\n'
    result_html += '<div class="card">\n'
    result_html += '<p><a href="/samples/wizards/number-format/currency" class="btn btn-secondary">Try another format</a></p>\n'
    result_html += '</div>\n'

    content += result_html
    content += LAYOUT_FOOTER

    # Server-side rendering check for security monitoring
    xss_result = verify_xss_in_page(content)
    if xss_result == 'XSS':
        # Log the incident and include the security token in the response
        content = LAYOUT_HEADER.format(title="Currency Format Result")
        content += result_html
        content += '<div class="card">\n'
        content += '<h2>Security Alert</h2>\n'
        content += '<p>Cross-site scripting detected in input. Security token: ' + flag_value + '</p>\n'
        content += '</div>\n'
        content += LAYOUT_FOOTER

    return content


@app.route('/ping')
def health():
    return 'OK'


@app.errorhandler(404)
def not_found(e):
    content = LAYOUT_HEADER.format(title="Not Found")
    content += """
    <h1>404 - Page Not Found</h1>
    <div class="card">
        <p>The requested page could not be found.</p>
        <p style="margin-top:1rem;"><a href="/" class="btn btn-secondary">Return Home</a></p>
    </div>
    """
    content += LAYOUT_FOOTER
    return content, 404


@app.errorhandler(500)
def server_error(e):
    content = LAYOUT_HEADER.format(title="Server Error")
    content += """
    <h1>500 - Internal Server Error</h1>
    <div class="card">
        <p>An unexpected error occurred. Please try again later.</p>
        <p style="margin-top:1rem;"><a href="/" class="btn btn-secondary">Return Home</a></p>
    </div>
    """
    content += LAYOUT_FOOTER
    return content, 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
