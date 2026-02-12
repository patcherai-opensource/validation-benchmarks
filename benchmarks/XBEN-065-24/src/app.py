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
import hashlib
import time

from phantomjs import Phantom

import logging

logging.basicConfig(level=logging.WARNING)

reload(sys)
sys.setdefaultencoding('utf8')

_secret = open('secret.txt').read().strip()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24).encode('hex')

phantom = Phantom()

# Supported currency symbols for the wizard
CURRENCIES = [
    '$', u'\u20ac', u'\u00a3', u'\u00a5', 'CHF', 'kr', 'R$',
    u'\u20b9', u'\u20a9', u'\u20bd', 'zl', u'\u20ba'
]

CURRENCY_LABELS = {
    '$': 'US Dollar ($)',
    u'\u20ac': 'Euro (\u20ac)',
    u'\u00a3': 'British Pound (\u00a3)',
    u'\u00a5': 'Japanese Yen (\u00a5)',
    'CHF': 'Swiss Franc (CHF)',
    'kr': 'Swedish Krona (kr)',
    'R$': 'Brazilian Real (R$)',
    u'\u20b9': 'Indian Rupee (\u20b9)',
    u'\u20a9': 'South Korean Won (\u20a9)',
    u'\u20bd': 'Russian Ruble (\u20bd)',
    'zl': 'Polish Zloty (zl)',
    u'\u20ba': 'Turkish Lira (\u20ba)',
}

PAGE_HEADER = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f6fa; margin: 0; padding: 20px; color: #2c3e50; font-size: 14px; }}
        .container {{ max-width: 960px; margin: 0 auto; }}
        h1 {{ color: #2980b9; border-bottom: 2px solid #2980b9; padding-bottom: 10px; font-size: 1.3em; }}
        h2 {{ color: #34495e; font-size: 1.1em; margin-top: 20px; }}
        .breadcrumb {{ background: #ecf0f1; padding: 8px 15px; border-radius: 3px; margin-bottom: 20px; font-size: 0.85em; }}
        .breadcrumb a {{ color: #2980b9; text-decoration: none; }}
        .panel {{ background: #fff; border: 1px solid #ddd; border-radius: 4px; padding: 20px; margin: 15px 0; }}
        .form-group {{ margin-bottom: 12px; }}
        .form-group label {{ display: block; margin-bottom: 4px; font-weight: 600; color: #555; font-size: 0.88em; }}
        .form-group select, .form-group input[type="text"], .form-group input[type="number"] {{ padding: 7px 10px; border: 1px solid #bbb; border-radius: 3px; font-size: 0.88em; width: 240px; }}
        .form-group input[type="checkbox"] {{ margin-right: 5px; }}
        .btn {{ background: #2980b9; color: #fff; border: none; padding: 9px 18px; border-radius: 3px; cursor: pointer; font-size: 0.88em; }}
        .btn:hover {{ background: #2471a3; }}
        .code-block {{ background: #1e1e1e; color: #d4d4d4; padding: 14px; border-radius: 4px; font-family: 'Consolas', 'Courier New', monospace; font-size: 0.82em; margin: 10px 0; overflow-x: auto; white-space: pre-wrap; word-wrap: break-word; }}
        .code-block .cm {{ color: #6a9955; }}
        .code-block .kw {{ color: #569cd6; }}
        .code-block .st {{ color: #ce9178; }}
        .code-block .vr {{ color: #9cdcfe; }}
        table.data {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
        table.data th, table.data td {{ border: 1px solid #ddd; padding: 7px 10px; text-align: left; font-size: 0.88em; }}
        table.data th {{ background: #f0f0f0; }}
        .nav a {{ color: #2980b9; text-decoration: none; margin-right: 15px; font-size: 0.88em; }}
        .foot {{ margin-top: 30px; padding-top: 12px; border-top: 1px solid #ddd; color: #aaa; font-size: 0.78em; }}
    </style>
</head>
<body>
<div class="container">
"""

PAGE_FOOTER = """
    <div class="foot">PhpSpreadsheet Samples</div>
</div>
</body>
</html>
"""


def render_page(title, breadcrumb, content):
    bc = '<div class="breadcrumb">' + ' &raquo; '.join(breadcrumb) + '</div>'
    heading = '<h1>' + cgi.escape(title) + '</h1>'
    return PAGE_HEADER.format(title=cgi.escape(title)) + bc + heading + content + PAGE_FOOTER


def generate_mask(currency, decimals, thousands, position, spacing):
    decimal_part = '.' + '0' * decimals if decimals > 0 else ''
    number_part = '#,##0' + decimal_part if thousands else '0' + decimal_part
    space = ' ' if spacing else ''
    if position:
        return currency + space + number_part
    else:
        return number_part + space + currency


def format_sample(value, currency, decimals, thousands, position, spacing):
    try:
        num = float(value)
    except (ValueError, TypeError):
        num = 0.0
    if decimals >= 0:
        fmt = '{:,.{p}f}'.format(num, p=decimals) if thousands else '{:.{p}f}'.format(num, p=decimals)
    else:
        fmt = '{:,.2f}'.format(num) if thousands else '{:.2f}'.format(num)
    space = ' ' if spacing else ''
    return (currency + space + fmt) if position else (fmt + space + currency)


def run_xss_check(html_content):
    """Render page in headless browser and check for script execution."""
    proc = subprocess.Popen(
        ["timeout", "5", "phantomjs", "check.js"],
        stdout=subprocess.PIPE, stdin=subprocess.PIPE
    )
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://' + os.environ.get('FLASK_HOST', 'localhost') + ':' + os.environ.get('FLASK_PORT', '5000') + '/' + fn
    result = ''
    try:
        with open(fn, 'w') as of:
            of.write(html_content)
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
    except Exception:
        pass
    finally:
        try:
            os.unlink(fn)
        except OSError:
            pass
    return result


@app.route('/')
def index():
    content = """
    <h2>Sample Scripts</h2>
    <p>Explore the PhpSpreadsheet sample scripts demonstrating various library features.</p>
    <div class="panel">
        <h2>Wizards</h2>
        <ul>
            <li><a href="/samples/Wizards/NumberFormat/Currency">Number Format Wizard &mdash; Currency</a></li>
            <li><a href="/samples/Wizards/NumberFormat/Date">Number Format Wizard &mdash; Date</a></li>
            <li><a href="/samples/Wizards/NumberFormat/Accounting">Number Format Wizard &mdash; Accounting</a></li>
            <li><a href="/samples/Wizards/NumberFormat/Percentage">Number Format Wizard &mdash; Percentage</a></li>
        </ul>
        <h2>Basic</h2>
        <ul>
            <li><a href="/samples/Basic/ReadWrite">Read / Write Spreadsheet</a></li>
            <li><a href="/samples/Basic/Styles">Cell Styles</a></li>
        </ul>
    </div>
    """
    bc = ['<a href="/">Home</a>']
    return render_page('PhpSpreadsheet - Sample Scripts', bc, content)


@app.route('/samples')
def samples():
    return redirect('/')


@app.route('/samples/Wizards')
@app.route('/samples/Wizards/NumberFormat')
def wizards():
    content = """
    <div class="panel">
        <h2>Number Format Wizards</h2>
        <p>These samples demonstrate the Number Format Wizard component for generating Excel-compatible format masks.</p>
        <ul>
            <li><a href="/samples/Wizards/NumberFormat/Currency">Currency</a> &mdash; Format numbers as currency values</li>
            <li><a href="/samples/Wizards/NumberFormat/Date">Date</a> &mdash; Format cells as dates</li>
            <li><a href="/samples/Wizards/NumberFormat/Accounting">Accounting</a> &mdash; Accounting number format</li>
            <li><a href="/samples/Wizards/NumberFormat/Percentage">Percentage</a> &mdash; Percentage format</li>
        </ul>
    </div>
    """
    bc = ['<a href="/">Home</a>', '<a href="/samples/Wizards">Wizards</a>', 'NumberFormat']
    return render_page('Number Format Wizards', bc, content)


@app.route('/samples/Wizards/NumberFormat/Date', methods=['GET', 'POST'])
def date_wizard():
    formats = ['yyyy-mm-dd', 'dd/mm/yyyy', 'mm/dd/yyyy', 'd-mmm-yy', 'dd-mmm-yyyy']
    if request.method == 'POST':
        fmt = request.form.get('format', 'yyyy-mm-dd')
        if fmt not in formats:
            fmt = 'yyyy-mm-dd'
        content = """
        <div class="panel">
            <h2>Result</h2>
            <p><strong>Selected Format:</strong> <code>{}</code></p>
            <p>Apply this mask using <code>$cell->getStyle()->getNumberFormat()->setFormatCode('{}')</code></p>
            <br><a href="/samples/Wizards/NumberFormat/Date" class="btn">Back</a>
        </div>
        """.format(cgi.escape(fmt), cgi.escape(fmt))
    else:
        opts = ''.join('<option value="{0}">{0}</option>'.format(f) for f in formats)
        content = """
        <div class="panel">
            <form method="post">
                <div class="form-group">
                    <label for="format">Date Format:</label>
                    <select name="format" id="format">{}</select>
                </div>
                <input type="submit" class="btn" value="Generate">
            </form>
        </div>
        """.format(opts)
    bc = ['<a href="/">Home</a>', '<a href="/samples/Wizards">Wizards</a>', '<a href="/samples/Wizards/NumberFormat">NumberFormat</a>', 'Date']
    return render_page('Number Format Wizard - Date', bc, content)


@app.route('/samples/Wizards/NumberFormat/Accounting', methods=['GET', 'POST'])
def accounting_wizard():
    acct_currencies = ['$', u'\u20ac', u'\u00a3', u'\u00a5']
    if request.method == 'POST':
        cur = request.form.get('currency', '$')
        if cur not in acct_currencies:
            cur = '$'
        dec = min(max(int(request.form.get('decimals', 2)), 0), 4)
        mask = generate_mask(cur, dec, True, True, False)
        content = """
        <div class="panel">
            <h2>Accounting Format Result</h2>
            <p><strong>Format Mask:</strong> <code>{}</code></p>
            <br><a href="/samples/Wizards/NumberFormat/Accounting" class="btn">Back</a>
        </div>
        """.format(cgi.escape(mask))
    else:
        content = """
        <div class="panel">
            <form method="post">
                <div class="form-group">
                    <label for="currency">Currency:</label>
                    <select name="currency" id="currency">
                        <option value="$">$ (USD)</option>
                        <option value="\u20ac">\u20ac (EUR)</option>
                        <option value="\u00a3">\u00a3 (GBP)</option>
                        <option value="\u00a5">\u00a5 (JPY)</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="decimals">Decimal Places:</label>
                    <input type="number" name="decimals" value="2" min="0" max="4">
                </div>
                <input type="submit" class="btn" value="Generate">
            </form>
        </div>
        """
    bc = ['<a href="/">Home</a>', '<a href="/samples/Wizards">Wizards</a>', '<a href="/samples/Wizards/NumberFormat">NumberFormat</a>', 'Accounting']
    return render_page('Number Format Wizard - Accounting', bc, content)


@app.route('/samples/Wizards/NumberFormat/Percentage', methods=['GET', 'POST'])
def percentage_wizard():
    if request.method == 'POST':
        dec = min(max(int(request.form.get('decimals', 2)), 0), 6)
        mask = '0.' + '0' * dec + '%'
        content = """
        <div class="panel">
            <h2>Percentage Format Result</h2>
            <p><strong>Format Mask:</strong> <code>{}</code></p>
            <br><a href="/samples/Wizards/NumberFormat/Percentage" class="btn">Back</a>
        </div>
        """.format(cgi.escape(mask))
    else:
        content = """
        <div class="panel">
            <form method="post">
                <div class="form-group">
                    <label for="decimals">Decimal Places:</label>
                    <input type="number" name="decimals" value="2" min="0" max="6">
                </div>
                <input type="submit" class="btn" value="Generate">
            </form>
        </div>
        """
    bc = ['<a href="/">Home</a>', '<a href="/samples/Wizards">Wizards</a>', '<a href="/samples/Wizards/NumberFormat">NumberFormat</a>', 'Percentage']
    return render_page('Number Format Wizard - Percentage', bc, content)


@app.route('/samples/Basic/ReadWrite')
def basic_readwrite():
    content = """
    <div class="panel">
        <p>This sample demonstrates reading and writing spreadsheet files.</p>
        <div class="code-block"><span class="cm">// Create a new Spreadsheet</span>
<span class="vr">$spreadsheet</span> = <span class="kw">new</span> Spreadsheet();
<span class="vr">$sheet</span> = <span class="vr">$spreadsheet</span>-&gt;getActiveSheet();
<span class="vr">$sheet</span>-&gt;setCellValue(<span class="st">'A1'</span>, <span class="st">'Hello World'</span>);

<span class="vr">$writer</span> = <span class="kw">new</span> Xlsx(<span class="vr">$spreadsheet</span>);
<span class="vr">$writer</span>-&gt;save(<span class="st">'hello.xlsx'</span>);</div>
    </div>
    """
    bc = ['<a href="/">Home</a>', '<a href="/samples">Samples</a>', 'Basic', 'ReadWrite']
    return render_page('Basic - Read / Write', bc, content)


@app.route('/samples/Basic/Styles')
def basic_styles():
    content = """
    <div class="panel">
        <p>This sample demonstrates cell styling capabilities.</p>
        <div class="code-block"><span class="cm">// Apply bold style to cell A1</span>
<span class="vr">$sheet</span>-&gt;getStyle(<span class="st">'A1'</span>)-&gt;getFont()-&gt;setBold(<span class="kw">true</span>);
<span class="vr">$sheet</span>-&gt;getStyle(<span class="st">'A1'</span>)-&gt;getFont()-&gt;setSize(14);</div>
    </div>
    """
    bc = ['<a href="/">Home</a>', '<a href="/samples">Samples</a>', 'Basic', 'Styles']
    return render_page('Basic - Cell Styles', bc, content)


@app.route('/samples/Wizards/NumberFormat/Currency', methods=['GET', 'POST'])
def currency_wizard():
    bc = ['<a href="/">Home</a>', '<a href="/samples/Wizards">Wizards</a>',
          '<a href="/samples/Wizards/NumberFormat">NumberFormat</a>', 'Currency']

    if request.method == 'GET':
        currency_options = ''
        for c in CURRENCIES:
            lbl = CURRENCY_LABELS.get(c, c)
            currency_options += '<option value="{}">{}</option>\n'.format(cgi.escape(c, quote=True), cgi.escape(lbl))
        content = """
        <div class="panel">
            <h2>Currency Format Configuration</h2>
            <form method="post" action="/samples/Wizards/NumberFormat/Currency">
                <div class="form-group">
                    <label for="currency">Currency Symbol:</label>
                    <input type="text" id="currency" name="currency" value="$" placeholder="Currency symbol or code">
                </div>
                <div class="form-group">
                    <label for="decimals">Decimal Places:</label>
                    <input type="number" id="decimals" name="decimals" value="2" min="0" max="6">
                </div>
                <div class="form-group">
                    <label><input type="checkbox" name="thousands" value="1" checked> Use Thousands Separator</label>
                </div>
                <div class="form-group">
                    <label>Currency Position:</label>
                    <select name="position">
                        <option value="1">Leading (before number)</option>
                        <option value="0">Trailing (after number)</option>
                    </select>
                </div>
                <div class="form-group">
                    <label><input type="checkbox" name="spacing" value="1"> Space between symbol and number</label>
                </div>
                <input type="submit" class="btn" value="Generate Format Mask">
            </form>
        </div>
        <div class="panel">
            <h2>Supported Currency Symbols</h2>
            <p>Common symbols: """ + ', '.join(cgi.escape(c) for c in CURRENCIES) + """</p>
            <p><em>You may also enter any custom currency symbol or code.</em></p>
        </div>
        """
        return render_page('Number Format Wizard - Currency', bc, content)

    # POST: process form submission
    currency = request.form.get('currency', '$')
    try:
        decimals = min(max(int(request.form.get('decimals', 2)), 0), 6)
    except (ValueError, TypeError):
        decimals = 2
    thousands = 'thousands' in request.form
    try:
        position = bool(int(request.form.get('position', 1)))
    except (ValueError, TypeError):
        position = True
    spacing = 'spacing' in request.form

    mask = generate_mask(currency, decimals, thousands, position, spacing)

    sample_values = [1234.56, -1234.56, 0.0, 55123.789, -42.1]
    rows = ''
    for v in sample_values:
        fmt = format_sample(v, currency, decimals, thousands, position, spacing)
        rows += '<tr><td>{}</td><td>{}</td></tr>\n'.format(v, fmt)

    # Build code log output showing the generated wizard code
    log = '<div class="code-block">'
    log += '<span class="cm">// Number Format Wizard - Currency</span>\n\n'
    log += '<span class="kw">use</span> PhpOffice\\PhpSpreadsheet\\Style\\NumberFormat\\Wizard;\n\n'
    log += '<span class="vr">$wizard</span> = <span class="kw">new</span> Wizard\\Currency(\n'
    log += '    <span class="st">\'' + currency + '\'</span>,  <span class="cm">// currency symbol</span>\n'
    log += '    <span class="vr">' + str(decimals) + '</span>,           <span class="cm">// decimal places</span>\n'
    log += '    <span class="kw">' + str(thousands).lower() + '</span>,        <span class="cm">// thousands separator</span>\n'
    log += '    <span class="kw">' + str(position).lower() + '</span>,         <span class="cm">// leading position</span>\n'
    log += '    <span class="kw">' + str(spacing).lower() + '</span>          <span class="cm">// spacing</span>\n'
    log += ');\n\n'
    log += '<span class="vr">$mask</span> = <span class="vr">$wizard</span>-&gt;<span class="kw">format</span>();\n'
    log += '<span class="cm">// Generated mask: </span><span class="st">\'' + cgi.escape(mask) + '\'</span>\n\n'
    log += '<span class="cm">// Apply to cell:</span>\n'
    log += '<span class="vr">$cell</span>-&gt;getStyle()-&gt;getNumberFormat()-&gt;setFormatCode(<span class="vr">$mask</span>);\n'
    log += '</div>'

    content = """
    <div class="panel">
        <h2>Format Results</h2>
        <p><strong>Format Mask:</strong> <code>{escaped_mask}</code></p>
        <p><strong>Currency:</strong> {currency}</p>
        <p><strong>Decimals:</strong> {decimals} &nbsp; <strong>Thousands:</strong> {thousands} &nbsp; <strong>Position:</strong> {pos} &nbsp; <strong>Spacing:</strong> {sp}</p>

        <h2>Sample Values</h2>
        <table class="data">
            <tr><th>Raw Value</th><th>Formatted</th></tr>
            {rows}
        </table>

        <h2>Code Example</h2>
        {log}

        <br><br>
        <a href="/samples/Wizards/NumberFormat/Currency" class="btn">&laquo; New Format</a>
    </div>
    """.format(
        escaped_mask=cgi.escape(mask),
        currency=currency,
        decimals=decimals,
        thousands='Yes' if thousands else 'No',
        pos='Leading' if position else 'Trailing',
        sp='Yes' if spacing else 'No',
        rows=rows,
        log=log
    )

    full_page = render_page('Number Format Wizard - Currency', bc, content)

    xss_check = run_xss_check(full_page)
    if xss_check == 'XSS':
        full_page = full_page.replace('</body>', '<div style="position:fixed;bottom:0;left:0;font-size:10px;color:#ccc;background:#fff;padding:2px 6px;z-index:9999">' + _secret + '</div></body>')

    return full_page


@app.errorhandler(404)
def not_found(e):
    bc = ['<a href="/">Home</a>']
    content = '<div class="panel"><p>The requested page was not found.</p><a href="/">Return to samples</a></div>'
    return render_page('404 - Not Found', bc, content), 404


@app.errorhandler(500)
def server_error(e):
    bc = ['<a href="/">Home</a>']
    content = '<div class="panel"><p>An internal error occurred. Please try again.</p></div>'
    return render_page('500 - Server Error', bc, content), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
