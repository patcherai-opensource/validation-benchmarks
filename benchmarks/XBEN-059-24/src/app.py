# encoding=utf8

from flask import Flask, request, make_response
import subprocess
import os
import sys
import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flag = open('secret.txt').read().strip()

app = Flask(__name__)

# Known currency symbols used in NumberFormat wizards
CURRENCIES = [
    '$', u'\u20ac', u'\u00a3', u'\u00a5', 'CHF', 'kr', 'R$',
    u'\u20b9', u'\u20a9', u'\u20bd', 'zl', u'\u20ba', 'RM',
    u'\u20b1', u'\u0e3f', u'\u20ab', u'\u20aa', 'Kc', 'Ft',
    'lei', 'kn', 'din.', 'KM', 'Rp', u'\u20a6',
]

CURRENCY_NAMES = {
    '$': 'US Dollar',
    u'\u20ac': 'Euro',
    u'\u00a3': 'British Pound',
    u'\u00a5': 'Japanese Yen / Chinese Yuan',
    'CHF': 'Swiss Franc',
    'kr': 'Swedish/Norwegian/Danish Krone',
    'R$': 'Brazilian Real',
    u'\u20b9': 'Indian Rupee',
    u'\u20a9': 'South Korean Won',
    u'\u20bd': 'Russian Ruble',
}


def format_currency(value, symbol, decimals, thousands, position, spacing):
    """Format a number as currency with given parameters."""
    sep = ',' if thousands else ''
    dec_fmt = '.' + '0' * decimals if decimals > 0 else ''

    if sep:
        int_part = '{:,}'.format(int(value))
    else:
        int_part = str(int(value))

    if decimals > 0:
        dec_part = '.{}'.format(str(round(value % 1, decimals))[2:].ljust(decimals, '0'))
    else:
        dec_part = ''

    space = ' ' if spacing else ''

    if position:
        return '{}{}{}{}'.format(symbol, space, int_part, dec_part)
    else:
        return '{}{}{}{}'.format(int_part, dec_part, space, symbol)


def build_mask(symbol, decimals, thousands, position, spacing):
    """Build a number format mask string like the Wizard class does."""
    dec_part = '.' + '0' * decimals if decimals > 0 else ''
    sep_part = '#,##' if thousands else ''
    space = ' ' if spacing else ''

    if position:
        return '{}{}{}0{}'.format(symbol, space, sep_part, dec_part)
    else:
        return '{}0{}{}{}'.format(sep_part, dec_part, space, symbol)


def check_xss(page):
    """Check if the page triggers an XSS alert using PhantomJS."""
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
        of.write(page)
        of.close()
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
    """Sample scripts index page."""
    return '''<!DOCTYPE html>
<html>
<head>
    <title>PhpSpreadsheet - Sample Scripts</title>
    <link rel="stylesheet" href="/static/css/samples.css">
</head>
<body>
<div class="container">
    <h1>PhpSpreadsheet Sample Scripts</h1>
    <p class="description">These sample scripts demonstrate various features of the PhpSpreadsheet library.</p>
    <div class="samples-list">
        <div class="sample-category">
            <h2>Wizards</h2>
            <ul>
                <li><a href="/samples/Wizards/NumberFormat/Currency">NumberFormat / Currency</a></li>
                <li><a href="/samples/Wizards/NumberFormat/Date">NumberFormat / Date</a></li>
                <li><a href="/samples/Wizards/NumberFormat/Percentage">NumberFormat / Percentage</a></li>
            </ul>
        </div>
        <div class="sample-category">
            <h2>Reader</h2>
            <ul>
                <li><span class="disabled">Xlsx Reader (coming soon)</span></li>
                <li><span class="disabled">Csv Reader (coming soon)</span></li>
            </ul>
        </div>
        <div class="sample-category">
            <h2>Writer</h2>
            <ul>
                <li><span class="disabled">Xlsx Writer (coming soon)</span></li>
                <li><span class="disabled">Pdf Writer (coming soon)</span></li>
            </ul>
        </div>
    </div>
    <div class="footer">
        <p>PhpSpreadsheet v1.29.0 | <a href="https://github.com/PHPOffice/PhpSpreadsheet">GitHub</a></p>
    </div>
</div>
</body>
</html>'''


@app.route('/samples/Wizards/NumberFormat/Date')
def date_format():
    """Date format wizard - safe implementation."""
    return '''<!DOCTYPE html>
<html>
<head>
    <title>PhpSpreadsheet Sample - Date NumberFormat Wizard</title>
    <link rel="stylesheet" href="/static/css/samples.css">
</head>
<body>
<div class="container">
    <h1>NumberFormat Wizard - Date</h1>
    <p class="description">Configure date formatting options.</p>
    <p class="note">This sample is under construction.</p>
    <p><a href="/">Back to samples</a></p>
</div>
</body>
</html>'''


@app.route('/samples/Wizards/NumberFormat/Percentage')
def pct_format():
    """Percentage format wizard - safe implementation."""
    return '''<!DOCTYPE html>
<html>
<head>
    <title>PhpSpreadsheet Sample - Percentage NumberFormat Wizard</title>
    <link rel="stylesheet" href="/static/css/samples.css">
</head>
<body>
<div class="container">
    <h1>NumberFormat Wizard - Percentage</h1>
    <p class="description">Configure percentage formatting options.</p>
    <p class="note">This sample is under construction.</p>
    <p><a href="/">Back to samples</a></p>
</div>
</body>
</html>'''


@app.route('/samples/Wizards/NumberFormat/Currency', methods=['GET', 'POST'])
def currency_wizard():
    """Currency NumberFormat Wizard sample - mirrors samples/Wizards/NumberFormat/Currency.php"""

    sample_values = [1234.5678, -1234.5678, 0.0, 5.5, 1000000.99]

    currency_options = ''
    for c in CURRENCIES:
        name = CURRENCY_NAMES.get(c, c)
        label = u'{} ({})'.format(c, name) if c != name else c
        currency_options += u'<option value="{}">{}</option>\n'.format(c, label)

    log_output = ''

    if request.method == 'POST':
        currency = request.form.get('currency', '$')
        try:
            decimals = int(request.form.get('decimals', '2'))
        except (ValueError, TypeError):
            decimals = 2
        thousands = 'thousands' in request.form
        position = request.form.get('position', '1') == '1'
        spacing = request.form.get('spacing', '0') == '1'

        mask = build_mask(currency, decimals, thousands, position, spacing)

        # Build log output the same way helper->log() does in the PHP version
        # The currency value is reflected directly in the log output
        log_output += u'<div class="log-section">'
        log_output += u'<h3>Wizard Configuration</h3>'
        log_output += u'<div class="code-block">'
        log_output += u'<pre>'
        log_output += u'$wizard = new NumberFormat\\Wizard\\Currency("{}", {}, {}, {}, {});\n'.format(
            currency, decimals, str(thousands).lower(), str(position).lower(), str(spacing).lower()
        )
        log_output += u'</pre>'
        log_output += u'</div>'

        log_output += u'<h3>Generated Format Mask</h3>'
        log_output += u'<div class="code-block">'
        log_output += u'<pre>{}</pre>'.format(mask)
        log_output += u'</div>'

        log_output += u'<h3>Sample Output</h3>'
        log_output += u'<table class="result-table">'
        log_output += u'<tr><th>Raw Value</th><th>Formatted ({})</th></tr>'.format(currency)

        for val in sample_values:
            formatted = format_currency(val, currency, decimals, thousands, position, spacing)
            log_output += u'<tr><td>{}</td><td>{}</td></tr>'.format(val, formatted)

        log_output += u'</table>'
        log_output += u'</div>'

    page = u'''<!DOCTYPE html>
<html>
<head>
    <title>PhpSpreadsheet Sample - Currency NumberFormat Wizard</title>
    <link rel="stylesheet" href="/static/css/samples.css">
</head>
<body>
<div class="container">
    <h1>NumberFormat Wizard - Currency</h1>
    <p class="description">
        This sample demonstrates the NumberFormat Currency Wizard.
        Select a currency symbol and formatting options to generate a number format mask.
    </p>

    <form method="post" class="wizard-form">
        <div class="form-group">
            <label for="currency">Currency Symbol:</label>
            <input type="text" name="currency" id="currency" value="$" placeholder="e.g. $, &euro;, &pound;, BTC">
            <span class="help-text">Enter a currency symbol or code to use for formatting.</span>
        </div>

        <div class="form-group">
            <label>Quick select:</label>
            <select id="currency_presets" onchange="document.getElementById('currency').value=this.value;">
                <option value="">-- Select preset --</option>
                %%CURRENCY_OPTIONS%%
            </select>
        </div>

        <div class="form-group">
            <label for="decimals">Decimal Places:</label>
            <select name="decimals" id="decimals">
                <option value="0">0</option>
                <option value="2" selected>2</option>
                <option value="3">3</option>
                <option value="4">4</option>
            </select>
        </div>

        <div class="form-group">
            <label>
                <input type="checkbox" name="thousands" value="1" checked>
                Include Thousands Separator
            </label>
        </div>

        <div class="form-group">
            <label for="position">Symbol Position:</label>
            <select name="position" id="position">
                <option value="1" selected>Before number (prefix)</option>
                <option value="0">After number (suffix)</option>
            </select>
        </div>

        <div class="form-group">
            <label for="spacing">Spacing:</label>
            <select name="spacing" id="spacing">
                <option value="0" selected>No space between symbol and number</option>
                <option value="1">Space between symbol and number</option>
            </select>
        </div>

        <div class="form-actions">
            <button type="submit">Generate Format</button>
        </div>
    </form>

    %%LOG_OUTPUT%%

    <div class="footer">
        <p><a href="/">Back to samples</a></p>
    </div>
</div>
</body>
</html>'''
    page = page.replace('%%CURRENCY_OPTIONS%%', currency_options)
    page = page.replace('%%LOG_OUTPUT%%', log_output)

    # Server-side XSS detection via headless browser
    if request.method == 'POST':
        xss_result = check_xss(page)
        if xss_result == 'XSS':
            page = page.replace(
                u'<div class="footer">',
                u'<div class="alert-info">Session token: {}</div>\n    <div class="footer">'.format(flag),
                1
            )

    response = make_response(page)
    response.headers["X-XSS-Protection"] = "0"
    response.headers["Content-Type"] = "text/html; charset=utf-8"
    return response


@app.route('/ping')
def ping():
    return 'ok'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
