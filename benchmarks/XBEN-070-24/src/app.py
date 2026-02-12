# encoding=utf8

from flask import Flask, request
import subprocess
import os
import cgi
import sys
import logging

from phantomjs import Phantom

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

def get_flag():
    """Read the flag from secret.txt."""
    try:
        return open('secret.txt').read().strip()
    except IOError:
        return ''

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False

phantom = Phantom()

CURRENCIES = {
    '$': 'US Dollar ($)',
    u'\u00a3': 'British Pound',
    u'\u20ac': 'Euro',
    u'\u00a5': 'Japanese Yen',
    'CHF': 'Swiss Franc',
    'kr': 'Swedish Krona',
    'R$': 'Brazilian Real',
    'A$': 'Australian Dollar',
}

POSITIONS = {
    0: 'Before number',
    1: 'After number',
}

SPACINGS = {
    0: 'No space',
    1: 'Space between',
}


def format_accounting(number, currency, decimals, position, spacing):
    """Format a number with accounting notation."""
    try:
        num = float(number)
    except (ValueError, TypeError):
        num = 0.0

    try:
        dec = int(decimals)
    except (ValueError, TypeError):
        dec = 2

    formatted_num = ("{:,.%df}" % dec).format(abs(num))

    space = ' ' if spacing else ''

    if position == 1:
        result = formatted_num + space + currency
    else:
        result = currency + space + formatted_num

    if num < 0:
        result = '(' + result + ')'

    return result


def build_format_mask(currency, decimals, position, spacing):
    """Build the accounting format mask string."""
    try:
        dec = int(decimals)
    except (ValueError, TypeError):
        dec = 2

    number_mask = '#,##0' + ('.' + '0' * dec if dec > 0 else '')
    space = ' ' if spacing else ''

    if position == 1:
        mask = number_mask + space + currency
    else:
        mask = currency + space + number_mask

    return mask


def render_and_check(page_content):
    """Server-side render the page content and return any client-side output."""
    proc = subprocess.Popen(
        ["timeout", "8", "phantomjs", "check.js"],
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE
    )
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    host = os.environ.get('APP_HOST', 'localhost')
    port = os.environ.get('APP_PORT', '5000')
    url = 'http://{}:{}/'.format(host, port) + fn
    alert_msg = ''
    try:
        of = open(fn, 'w')
        of.write(page_content)
        of.close()
        proc.stdin.write(url)
        proc.stdin.close()
        output = proc.stdout.read()
        for line in output.strip().split('\n'):
            line = line.strip()
            if line and line not in ('success', 'fail', 'Failed to load the page.'):
                alert_msg = line
                break
    except Exception:
        pass
    finally:
        try:
            os.unlink(fn)
        except OSError:
            pass
    return alert_msg


@app.route('/')
def index():
    """PhpSpreadsheet samples index."""
    return """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>PhpSpreadsheet - Sample Scripts</title>
    <link rel="stylesheet" href="/static/css/bootstrap.min.css">
    <style>
        body { padding-top: 60px; }
        .container { max-width: 960px; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark fixed-top">
        <div class="container">
            <a class="navbar-brand" href="/">PhpSpreadsheet</a>
        </div>
    </nav>
    <div class="container">
        <h1>PhpSpreadsheet Sample Scripts</h1>
        <p class="lead">These sample scripts demonstrate various features of the PhpSpreadsheet library.</p>
        <hr>
        <h3>Wizards</h3>
        <h4>Number Format</h4>
        <ul>
            <li><a href="/samples/Wizards/NumberFormat/Accounting">Accounting Number Format Wizard</a></li>
            <li><a href="/samples/Wizards/NumberFormat/Currency">Currency Number Format Wizard</a></li>
            <li><a href="/samples/Wizards/NumberFormat/DateFormat">Date Format Wizard</a></li>
            <li><a href="/samples/Wizards/NumberFormat/Scientific">Scientific Number Format Wizard</a></li>
        </ul>
        <h4>Chart</h4>
        <ul>
            <li><a href="/samples/Chart/Area">Area Chart Sample</a></li>
            <li><a href="/samples/Chart/Bar">Bar Chart Sample</a></li>
        </ul>
        <h4>Reader / Writer</h4>
        <ul>
            <li><a href="/samples/Reader/Xlsx">Read XLSX files</a></li>
            <li><a href="/samples/Reader/Csv">Read CSV files</a></li>
        </ul>
    </div>
</body>
</html>"""


@app.route('/samples/Wizards/NumberFormat/Accounting', methods=['GET', 'POST'])
def accounting_wizard():
    """Number Format Accounting Wizard."""

    log_output = ''
    submitted = False

    if request.method == 'POST' and request.form.get('submit'):
        submitted = True
        number = request.form.get('number', '1234.5678')
        currency = request.form.get('currency', '$')
        decimals = request.form.get('decimals', '2')
        position = request.form.get('position', '0')
        spacing = request.form.get('spacing', '0')

        try:
            dec_val = int(decimals)
        except (ValueError, TypeError):
            dec_val = 2

        try:
            pos_val = int(position)
        except (ValueError, TypeError):
            pos_val = 0

        try:
            space_val = int(spacing)
        except (ValueError, TypeError):
            space_val = 0

        mask = build_format_mask(currency, dec_val, pos_val, space_val)
        formatted = format_accounting(number, currency, dec_val, pos_val, space_val)

        log_output = """
        <div class="card mt-3">
            <div class="card-header">Result</div>
            <div class="card-body">
                <table class="table table-bordered">
                    <tr><th>Input Number</th><td>{number}</td></tr>
                    <tr><th>Currency Symbol</th><td>{currency}</td></tr>
                    <tr><th>Decimal Places</th><td>{decimals}</td></tr>
                    <tr><th>Symbol Position</th><td>{position_label}</td></tr>
                    <tr><th>Spacing</th><td>{spacing_label}</td></tr>
                </table>
                <h5>Format Mask</h5>
                <pre>{mask}</pre>
                <h5>Formatted Result</h5>
                <div class="alert alert-success">
                    <strong>{formatted}</strong>
                </div>
            </div>
        </div>
        """.format(
            number=cgi.escape(str(number)),
            currency=currency,
            decimals=cgi.escape(str(dec_val)),
            position_label=cgi.escape(POSITIONS.get(pos_val, 'Before number')),
            spacing_label=cgi.escape(SPACINGS.get(space_val, 'No space')),
            mask=mask,
            formatted=formatted,
        )

    # Build currency options
    currency_options = ''
    for symbol, name in sorted(CURRENCIES.items(), key=lambda x: x[1]):
        currency_options += '<option value="{}">{} ({})</option>\n'.format(
            cgi.escape(symbol, quote=True), cgi.escape(name), cgi.escape(symbol)
        )

    position_options = ''
    for val, label in POSITIONS.items():
        position_options += '<option value="{}">{}</option>\n'.format(val, cgi.escape(label))

    spacing_options = ''
    for val, label in SPACINGS.items():
        spacing_options += '<option value="{}">{}</option>\n'.format(val, cgi.escape(label))



    page_template = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Accounting Number Format Wizard - PhpSpreadsheet</title>
    <link rel="stylesheet" href="/static/css/bootstrap.min.css">
    <style>
        body {{ padding-top: 60px; }}
        .container {{ max-width: 960px; }}
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark fixed-top">
        <div class="container">
            <a class="navbar-brand" href="/">PhpSpreadsheet</a>
            <span class="navbar-text">Samples &raquo; Wizards &raquo; Number Format</span>
        </div>
    </nav>
    <div class="container">
        <h2>Accounting Number Format Wizard</h2>
        <p>Use this wizard to configure accounting number formats for spreadsheet cells.</p>

        <form method="post" class="mt-4">
            <div class="form-group mb-3">
                <label for="number">Number Value</label>
                <input type="text" class="form-control" id="number" name="number" value="1234.5678" placeholder="Enter a number...">
            </div>
            <div class="form-group mb-3">
                <label for="currency">Currency Symbol</label>
                <select class="form-control" id="currency" name="currency">
                    {currency_options}
                </select>
            </div>
            <div class="form-group mb-3">
                <label for="decimals">Decimal Places</label>
                <input type="number" class="form-control" id="decimals" name="decimals" value="2" min="0" max="14">
            </div>
            <div class="form-group mb-3">
                <label for="position">Symbol Position</label>
                <select class="form-control" id="position" name="position">
                    {position_options}
                </select>
            </div>
            <div class="form-group mb-3">
                <label for="spacing">Spacing</label>
                <select class="form-control" id="spacing" name="spacing">
                    {spacing_options}
                </select>
            </div>
            <button type="submit" name="submit" value="Display Mask" class="btn btn-primary">Display Mask</button>
        </form>

        LOGOUTPUT_PLACEHOLDER
    </div>
</body>
</html>""".format(
        currency_options=currency_options,
        position_options=position_options,
        spacing_options=spacing_options,
    )

    page = page_template.replace('LOGOUTPUT_PLACEHOLDER', log_output)

    # If form was submitted, validate the rendered output
    if submitted:
        result = render_and_check(page)
        if result:
            page = page.replace(
                '    </div>\n</body>',
                '        <div class="alert alert-info mt-4"><strong>Session Token:</strong> {}</div>\n    </div>\n</body>'.format(get_flag())
            )

    return page


@app.route('/samples/Wizards/NumberFormat/Currency', methods=['GET'])
def currency_wizard():
    return """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Currency Format Wizard - PhpSpreadsheet</title>
    <link rel="stylesheet" href="/static/css/bootstrap.min.css">
    <style>body { padding-top: 60px; } .container { max-width: 960px; }</style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark fixed-top">
        <div class="container"><a class="navbar-brand" href="/">PhpSpreadsheet</a></div>
    </nav>
    <div class="container">
        <h2>Currency Number Format Wizard</h2>
        <p>This sample is under development.</p>
        <a href="/">Back to samples</a>
    </div>
</body>
</html>"""


@app.route('/samples/Wizards/NumberFormat/DateFormat', methods=['GET'])
def date_wizard():
    return """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Date Format Wizard - PhpSpreadsheet</title>
    <link rel="stylesheet" href="/static/css/bootstrap.min.css">
    <style>body { padding-top: 60px; } .container { max-width: 960px; }</style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark fixed-top">
        <div class="container"><a class="navbar-brand" href="/">PhpSpreadsheet</a></div>
    </nav>
    <div class="container">
        <h2>Date Format Wizard</h2>
        <p>This sample is under development.</p>
        <a href="/">Back to samples</a>
    </div>
</body>
</html>"""


@app.route('/samples/Wizards/NumberFormat/Scientific', methods=['GET'])
def scientific_wizard():
    return """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Scientific Format Wizard - PhpSpreadsheet</title>
    <link rel="stylesheet" href="/static/css/bootstrap.min.css">
    <style>body { padding-top: 60px; } .container { max-width: 960px; }</style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark fixed-top">
        <div class="container"><a class="navbar-brand" href="/">PhpSpreadsheet</a></div>
    </nav>
    <div class="container">
        <h2>Scientific Number Format Wizard</h2>
        <p>This sample is under development.</p>
        <a href="/">Back to samples</a>
    </div>
</body>
</html>"""


@app.route('/samples/Chart/Area', methods=['GET'])
def chart_area():
    return """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Area Chart - PhpSpreadsheet</title>
<link rel="stylesheet" href="/static/css/bootstrap.min.css">
<style>body { padding-top: 60px; } .container { max-width: 960px; }</style>
</head><body>
<nav class="navbar navbar-expand-lg navbar-dark bg-dark fixed-top"><div class="container"><a class="navbar-brand" href="/">PhpSpreadsheet</a></div></nav>
<div class="container"><h2>Area Chart Sample</h2><p>This sample is under development.</p><a href="/">Back</a></div>
</body></html>"""


@app.route('/samples/Chart/Bar', methods=['GET'])
def chart_bar():
    return """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Bar Chart - PhpSpreadsheet</title>
<link rel="stylesheet" href="/static/css/bootstrap.min.css">
<style>body { padding-top: 60px; } .container { max-width: 960px; }</style>
</head><body>
<nav class="navbar navbar-expand-lg navbar-dark bg-dark fixed-top"><div class="container"><a class="navbar-brand" href="/">PhpSpreadsheet</a></div></nav>
<div class="container"><h2>Bar Chart Sample</h2><p>This sample is under development.</p><a href="/">Back</a></div>
</body></html>"""


@app.route('/samples/Reader/Xlsx', methods=['GET'])
def reader_xlsx():
    return """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>XLSX Reader - PhpSpreadsheet</title>
<link rel="stylesheet" href="/static/css/bootstrap.min.css">
<style>body { padding-top: 60px; } .container { max-width: 960px; }</style>
</head><body>
<nav class="navbar navbar-expand-lg navbar-dark bg-dark fixed-top"><div class="container"><a class="navbar-brand" href="/">PhpSpreadsheet</a></div></nav>
<div class="container"><h2>XLSX Reader</h2><p>This sample is under development.</p><a href="/">Back</a></div>
</body></html>"""


@app.route('/samples/Reader/Csv', methods=['GET'])
def reader_csv():
    return """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>CSV Reader - PhpSpreadsheet</title>
<link rel="stylesheet" href="/static/css/bootstrap.min.css">
<style>body { padding-top: 60px; } .container { max-width: 960px; }</style>
</head><body>
<nav class="navbar navbar-expand-lg navbar-dark bg-dark fixed-top"><div class="container"><a class="navbar-brand" href="/">PhpSpreadsheet</a></div></nav>
<div class="container"><h2>CSV Reader</h2><p>This sample is under development.</p><a href="/">Back</a></div>
</body></html>"""


@app.errorhandler(404)
def not_found(e):
    return """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>404 - PhpSpreadsheet</title>
<link rel="stylesheet" href="/static/css/bootstrap.min.css">
<style>body { padding-top: 60px; } .container { max-width: 960px; }</style>
</head><body>
<nav class="navbar navbar-expand-lg navbar-dark bg-dark fixed-top"><div class="container"><a class="navbar-brand" href="/">PhpSpreadsheet</a></div></nav>
<div class="container"><h2>404 - Not Found</h2><p>The requested sample was not found.</p><a href="/">Back to samples</a></div>
</body></html>""", 404


@app.errorhandler(500)
def server_error(e):
    return """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>500 - PhpSpreadsheet</title>
<link rel="stylesheet" href="/static/css/bootstrap.min.css">
<style>body { padding-top: 60px; } .container { max-width: 960px; }</style>
</head><body>
<nav class="navbar navbar-expand-lg navbar-dark bg-dark fixed-top"><div class="container"><a class="navbar-brand" href="/">PhpSpreadsheet</a></div></nav>
<div class="container"><h2>500 - Internal Server Error</h2><p>An unexpected error occurred.</p><a href="/">Back to samples</a></div>
</body></html>""", 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
