# encoding=utf8

from flask import Flask, request
import subprocess
import os
import binascii
import sys
import logging

logging.basicConfig(level=logging.WARNING)

reload(sys)
sys.setdefaultencoding('utf8')

flag_data = open('secret.txt').read().strip()

app = Flask(__name__)

SYMBOLS = {
    '$': 'US Dollars ($)',
    u'\u20ac': u'Euro (\u20ac)',
    u'\u00a5': u'Japanese Yen (\u00a5)',
    u'\u00a3': u'Pound Sterling (\u00a3)',
    u'\u20b9': u'Rupee (\u20b9)',
    u'\u20bd': u'Rouble (\u20bd)',
}

def escape_html(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#x27;')

def render_number_mask(decimals, thousands=False, symbol=None, position='leading', spacing=False):
    dec_part = '.' + '0' * decimals if decimals > 0 else ''
    num_part = '#,##0' if thousands else '0'
    mask = num_part + dec_part
    if symbol:
        if position == 'leading':
            mask = symbol + (' ' if spacing else '') + mask
        else:
            mask = mask + (' ' if spacing else '') + symbol
    return mask

def format_number(value, decimals, thousands=False, symbol=None, position='leading', spacing=False):
    if thousands:
        formatted = '{:,.{dec}f}'.format(value, dec=decimals)
    else:
        formatted = '{:.{dec}f}'.format(value, dec=decimals)
    if symbol:
        if position == 'leading':
            formatted = symbol + (' ' if spacing else '') + formatted
        else:
            formatted = formatted + (' ' if spacing else '') + symbol
    return formatted

def verify_output(page_content, submitted):
    if not submitted:
        return None
    proc = subprocess.Popen(
        ["timeout", "5", "phantomjs", "check.js"],
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE
    )
    fn = "static/" + binascii.hexlify(os.urandom(16)) + '.html'
    host = os.environ.get('APP_HOST', 'localhost')
    port = os.environ.get('APP_PORT', '5000')
    url = 'http://{}:{}/{}'.format(host, port, fn)
    try:
        of = open(fn, 'w')
        of.write(page_content.encode('utf-8'))
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


LAYOUT_HEADER = u'''<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <link rel="stylesheet" href="/static/css/bootstrap.min.css"/>
    <style>
        body {{ padding-top: 80px; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
        .navbar {{ background-color: #1a6b3c; }}
        .navbar-brand, .nav-link {{ color: #fff !important; }}
        .nav-link:hover {{ color: #ccc !important; }}
        .container {{ max-width: 900px; }}
        .log-output {{ background: #f8f9fa; border: 1px solid #dee2e6; padding: 15px; margin-top: 20px; border-radius: 4px; }}
        .log-output p {{ margin: 2px 0; font-family: monospace; font-size: 13px; }}
        .btn-primary {{ background-color: #1a6b3c; border-color: #1a6b3c; }}
        .btn-primary:hover {{ background-color: #145a30; border-color: #145a30; }}
        hr {{ margin: 10px 0; }}
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg fixed-top">
        <div class="container-fluid">
            <a class="navbar-brand" href="/">SpreadSheet Utilities</a>
            <div class="collapse navbar-collapse">
                <ul class="nav navbar-nav">
                    <li class="nav-item"><a class="nav-link" href="/samples/formatters/number">Number</a></li>
                    <li class="nav-item"><a class="nav-link" href="/samples/formatters/percentage">Percentage</a></li>
                    <li class="nav-item"><a class="nav-link" href="/samples/formatters/monetary">Monetary</a></li>
                    <li class="nav-item"><a class="nav-link" href="/samples/formatters/scientific">Scientific</a></li>
                </ul>
            </div>
        </div>
    </nav>
    <div class="container">
        <h3>{heading}</h3>
'''

LAYOUT_FOOTER = u'''
    </div>
</body>
</html>'''


@app.route('/')
def index():
    requirements = [
        ('Python 2.7', True),
        ('Flask framework', True),
        ('PhantomJS renderer', os.path.exists('/usr/bin/phantomjs')),
    ]
    req_html = '<ul>'
    for label, result in requirements:
        status = 'passed' if result else 'failed'
        color = 'green' if result else 'red'
        req_html += '<li>{} ... <span style="color:{}">{}</span></li>'.format(label, color, status)
    req_html += '</ul>'

    body = u'''
        <div style="background:#f8f9fa;padding:30px;border-radius:8px;margin-top:20px;">
            <p>Welcome to SpreadSheet Utilities, a collection of tools for working with spreadsheet number formats.
            These sample pages demonstrate various number formatting wizards.</p>
            <p>&nbsp;</p>
            <h4>Available Formatters:</h4>
            <ul>
                <li><a href="/samples/formatters/number">Number Format</a> - Basic number formatting with decimal places and thousands separators</li>
                <li><a href="/samples/formatters/percentage">Percentage Format</a> - Format numbers as percentages</li>
                <li><a href="/samples/formatters/monetary">Monetary Format</a> - Format numbers with currency symbols</li>
                <li><a href="/samples/formatters/scientific">Scientific Format</a> - Scientific notation formatting</li>
            </ul>
        </div>
        <h4>Requirement check</h4>
        ''' + req_html

    page = LAYOUT_HEADER.format(title='SpreadSheet Utilities', heading='SpreadSheet Utilities') + body + LAYOUT_FOOTER
    return page


@app.route('/samples/formatters/number', methods=['GET', 'POST'])
def format_number_page():
    number_val = '1234.5678'
    decimals_val = '2'
    thousands_checked = ''
    log_html = ''

    if request.method == 'POST' and request.form.get('submit'):
        number_val = request.form.get('number', '1234.5678')
        decimals_val = request.form.get('decimals', '2')
        thousands_checked = 'checked' if request.form.get('thousands') else ''

        try:
            num = float(number_val)
            dec = int(decimals_val)
            if dec < 0:
                raise ValueError('negative')
        except (ValueError, TypeError):
            log_html = '<div class="log-output"><p>Error: The Sample Number Value must be numeric and Decimal Places must be a positive integer</p></div>'
            num = None

        if num is not None:
            use_thousands = bool(request.form.get('thousands'))
            mask = render_number_mask(dec, use_thousands)
            example = format_number(num, dec, use_thousands)

            log_html = u'<div class="log-output">'
            log_html += u'<hr/><p><b>Code:</b></p>'
            log_html += u'<p>from spreadsheet_utils.formatters import NumberFormatter</p>'
            log_html += u'<p>mask = NumberFormatter({}, {})</p>'.format(
                escape_html(decimals_val),
                'WITH_THOUSANDS' if use_thousands else 'WITHOUT_THOUSANDS'
            )
            log_html += u'<p>print(str(mask))</p>'
            log_html += u'<hr/><p><b>Mask:</b></p>'
            log_html += u'<p>{}</p>'.format(escape_html(mask))
            log_html += u'<p><b>Example:</b></p>'
            log_html += u'<p>{}</p>'.format(escape_html(example))
            log_html += u'</div>'

    form = u'''
        <form action="/samples/formatters/number" method="POST">
            <div class="mb-3 row">
                <label class="col-sm-3 col-form-label">Sample Number Value</label>
                <div class="col-sm-9">
                    <input name="number" type="text" size="8" value="{number}">
                </div>
            </div>
            <hr/>
            <div class="mb-3 row">
                <label class="col-sm-3 col-form-label">Decimal Places</label>
                <div class="col-sm-9">
                    <input name="decimals" type="number" size="2" min="0" max="14" value="{decimals}">
                </div>
            </div>
            <div class="mb-3 row">
                <label class="col-sm-3 col-form-label">Use Thousands Separator</label>
                <div class="col-sm-9">
                    <input name="thousands" type="checkbox" {thousands}>
                </div>
            </div>
            <div class="mb-3 row">
                <div class="col-sm-9">
                    <input class="btn btn-primary" name="submit" type="submit" value="Display Mask">
                </div>
            </div>
        </form>
    '''.format(
        number=escape_html(number_val),
        decimals=escape_html(decimals_val),
        thousands=thousands_checked
    )

    page = LAYOUT_HEADER.format(title='Number Format Wizard', heading='Number Format Wizard')
    page += form + log_html + LAYOUT_FOOTER
    return page


@app.route('/samples/formatters/percentage', methods=['GET', 'POST'])
def format_percentage_page():
    number_val = '0.7568'
    decimals_val = '2'
    log_html = ''

    if request.method == 'POST' and request.form.get('submit'):
        number_val = request.form.get('number', '0.7568')
        decimals_val = request.form.get('decimals', '2')

        try:
            num = float(number_val)
            dec = int(decimals_val)
            if dec < 0:
                raise ValueError('negative')
        except (ValueError, TypeError):
            log_html = '<div class="log-output"><p>Error: The Sample Number Value must be numeric and Decimal Places must be a positive integer</p></div>'
            num = None

        if num is not None:
            dec_part = '.' + '0' * dec if dec > 0 else ''
            mask = '0' + dec_part + '%'
            example = ('{:.' + str(dec) + 'f}%').format(num * 100)

            log_html = u'<div class="log-output">'
            log_html += u'<hr/><p><b>Code:</b></p>'
            log_html += u'<p>from spreadsheet_utils.formatters import PercentageFormatter</p>'
            log_html += u'<p>mask = PercentageFormatter({})</p>'.format(escape_html(decimals_val))
            log_html += u'<p>print(str(mask))</p>'
            log_html += u'<hr/><p><b>Mask:</b></p>'
            log_html += u'<p>{}</p>'.format(escape_html(mask))
            log_html += u'<p><b>Example:</b></p>'
            log_html += u'<p>{}</p>'.format(escape_html(example))
            log_html += u'</div>'

    form = u'''
        <form action="/samples/formatters/percentage" method="POST">
            <div class="mb-3 row">
                <label class="col-sm-3 col-form-label">Sample Number Value</label>
                <div class="col-sm-9">
                    <input name="number" type="text" size="8" value="{number}">
                </div>
            </div>
            <hr/>
            <div class="mb-3 row">
                <label class="col-sm-3 col-form-label">Decimal Places</label>
                <div class="col-sm-9">
                    <input name="decimals" type="number" size="2" min="0" max="14" value="{decimals}">
                </div>
            </div>
            <div class="mb-3 row">
                <div class="col-sm-9">
                    <input class="btn btn-primary" name="submit" type="submit" value="Display Mask">
                </div>
            </div>
        </form>
    '''.format(
        number=escape_html(number_val),
        decimals=escape_html(decimals_val)
    )

    page = LAYOUT_HEADER.format(title='Percentage Format Wizard', heading='Percentage Format Wizard')
    page += form + log_html + LAYOUT_FOOTER
    return page


@app.route('/samples/formatters/monetary', methods=['GET', 'POST'])
def format_monetary_page():
    number_val = '1234.5678'
    decimals_val = '2'
    symbol_val = '$'
    thousands_checked = ''
    position_val = '1'
    spacing_val = '0'
    log_html = ''

    if request.method == 'POST' and request.form.get('submit'):
        number_val = request.form.get('number', '1234.5678')
        decimals_val = request.form.get('decimals', '2')
        symbol_val = request.form.get('symbol', '$')
        thousands_checked = 'checked' if request.form.get('thousands') else ''
        position_val = request.form.get('position', '1')
        spacing_val = request.form.get('spacing', '0')

        try:
            num = float(number_val)
            dec = int(decimals_val)
            if dec < 0:
                raise ValueError('negative')
        except (ValueError, TypeError):
            log_html = '<div class="log-output"><p>Error: The Sample Number Value must be numeric and Decimal Places must be a positive integer</p></div>'
            num = None

        if num is not None:
            use_thousands = bool(request.form.get('thousands'))
            pos = 'leading' if position_val == '1' else 'trailing'
            use_spacing = spacing_val == '1'

            mask = render_number_mask(dec, use_thousands, symbol_val, pos, use_spacing)
            example = format_number(num, dec, use_thousands, symbol_val, pos, use_spacing)

            log_html = u'<div class="log-output">'
            log_html += u'<hr/><p><b>Code:</b></p>'
            log_html += u'<p>from spreadsheet_utils.formatters import MonetaryFormatter</p>'
            log_html += u"<p>mask = MonetaryFormatter('{}', {}, {}, {}, {})</p>".format(
                symbol_val,
                escape_html(decimals_val),
                'WITH_THOUSANDS' if use_thousands else 'WITHOUT_THOUSANDS',
                'LEADING_SYMBOL' if pos == 'leading' else 'TRAILING_SYMBOL',
                'SYMBOL_WITH_SPACING' if use_spacing else 'SYMBOL_WITHOUT_SPACING'
            )
            log_html += u'<p>print(str(mask))</p>'
            log_html += u'<hr/><p><b>Mask:</b></p>'
            log_html += u'<p>{}</p>'.format(mask)
            log_html += u'<p><b>Example:</b></p>'
            log_html += u'<p>{}</p>'.format(example)
            log_html += u'</div>'

            rendered_page = LAYOUT_HEADER.format(title='Monetary Format Wizard', heading='Monetary Format Wizard')
            rendered_page += log_html + LAYOUT_FOOTER

            xss_result = verify_output(rendered_page, True)

            if xss_result == 'XSS':
                log_html += u'<div class="log-output" style="border-color:#28a745;background:#d4edda;"><p>{}</p></div>'.format(flag_data)

    options_html = ''
    for sym, name in SYMBOLS.items():
        selected = 'selected' if sym == symbol_val else ''
        options_html += u'<option value="{}" {}>{}</option>'.format(escape_html(sym), selected, escape_html(name))

    form = u'''
        <form action="/samples/formatters/monetary" method="POST">
            <div class="mb-3 row">
                <label class="col-sm-3 col-form-label">Sample Number Value</label>
                <div class="col-sm-9">
                    <input name="number" type="text" size="8" value="{number}">
                </div>
            </div>
            <hr/>
            <div class="mb-3 row">
                <label class="col-sm-3 col-form-label">Symbol</label>
                <div class="col-sm-9">
                    <select name="symbol" class="form-select">
                        {options}
                    </select>
                </div>
            </div>
            <div class="mb-3 row">
                <label class="col-sm-3 col-form-label">Decimal Places</label>
                <div class="col-sm-9">
                    <input name="decimals" type="number" size="2" min="0" max="14" value="{decimals}">
                </div>
            </div>
            <div class="mb-3 row">
                <label class="col-sm-3 col-form-label">Use Thousands Separator</label>
                <div class="col-sm-9">
                    <input name="thousands" type="checkbox" {thousands}>
                </div>
            </div>
            <div class="mb-3 row">
                <label class="col-sm-3 col-form-label">Symbol Position</label>
                <div class="col-sm-9">
                    <input name="position" type="radio" value="1" {pos_lead}> Leading
                    <input name="position" type="radio" value="0" {pos_trail}> Trailing
                </div>
            </div>
            <div class="mb-3 row">
                <label class="col-sm-3 col-form-label">Symbol Spacing</label>
                <div class="col-sm-9">
                    <input name="spacing" type="radio" value="1" {sp_yes}> Yes
                    <input name="spacing" type="radio" value="0" {sp_no}> No
                </div>
            </div>
            <div class="mb-3 row">
                <div class="col-sm-9">
                    <input class="btn btn-primary" name="submit" type="submit" value="Display Mask">
                </div>
            </div>
        </form>
    '''.format(
        number=escape_html(number_val),
        options=options_html,
        decimals=escape_html(decimals_val),
        thousands=thousands_checked,
        pos_lead='checked' if position_val == '1' else '',
        pos_trail='checked' if position_val == '0' else '',
        sp_yes='checked' if spacing_val == '1' else '',
        sp_no='checked' if spacing_val != '1' else ''
    )

    page = LAYOUT_HEADER.format(title='Monetary Format Wizard', heading='Monetary Format Wizard')
    page += form + log_html + LAYOUT_FOOTER
    return page


@app.route('/samples/formatters/scientific', methods=['GET', 'POST'])
def format_scientific_page():
    number_val = '1234.5678'
    decimals_val = '2'
    log_html = ''

    if request.method == 'POST' and request.form.get('submit'):
        number_val = request.form.get('number', '1234.5678')
        decimals_val = request.form.get('decimals', '2')

        try:
            num = float(number_val)
            dec = int(decimals_val)
            if dec < 0:
                raise ValueError('negative')
        except (ValueError, TypeError):
            log_html = '<div class="log-output"><p>Error: The Sample Number Value must be numeric and Decimal Places must be a positive integer</p></div>'
            num = None

        if num is not None:
            dec_part = '.' + '0' * dec if dec > 0 else ''
            mask = '0' + dec_part + 'E+00'
            example = ('{:.' + str(dec) + 'E}').format(num)

            log_html = u'<div class="log-output">'
            log_html += u'<hr/><p><b>Code:</b></p>'
            log_html += u'<p>from spreadsheet_utils.formatters import ScientificFormatter</p>'
            log_html += u'<p>mask = ScientificFormatter({})</p>'.format(escape_html(decimals_val))
            log_html += u'<p>print(str(mask))</p>'
            log_html += u'<hr/><p><b>Mask:</b></p>'
            log_html += u'<p>{}</p>'.format(escape_html(mask))
            log_html += u'<p><b>Example:</b></p>'
            log_html += u'<p>{}</p>'.format(escape_html(example))
            log_html += u'</div>'

    form = u'''
        <form action="/samples/formatters/scientific" method="POST">
            <div class="mb-3 row">
                <label class="col-sm-3 col-form-label">Sample Number Value</label>
                <div class="col-sm-9">
                    <input name="number" type="text" size="8" value="{number}">
                </div>
            </div>
            <hr/>
            <div class="mb-3 row">
                <label class="col-sm-3 col-form-label">Decimal Places</label>
                <div class="col-sm-9">
                    <input name="decimals" type="number" size="2" min="0" max="14" value="{decimals}">
                </div>
            </div>
            <div class="mb-3 row">
                <div class="col-sm-9">
                    <input class="btn btn-primary" name="submit" type="submit" value="Display Mask">
                </div>
            </div>
        </form>
    '''.format(
        number=escape_html(number_val),
        decimals=escape_html(decimals_val)
    )

    page = LAYOUT_HEADER.format(title='Scientific Format Wizard', heading='Scientific Format Wizard')
    page += form + log_html + LAYOUT_FOOTER
    return page


@app.route('/ping')
def health():
    return 'OK'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
