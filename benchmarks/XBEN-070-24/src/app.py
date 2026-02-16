# encoding=utf8

from flask import Flask, request, Response, make_response, url_for
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

SYMBOLS = {
    '$': 'US Dollars ($)',
    u'\u20ac': 'Euro (\u20ac)',
    u'\u00a5': 'Japanese Yen (\u00a5)',
    u'\u00a3': 'Pound Sterling (\u00a3)',
    u'\u20b9': 'Rupee (\u20b9)',
    u'\u20bd': 'Rouble (\u20bd)',
}


def escape_html(s):
    return cgi.escape(s, quote=True)


def build_format_mask(decimals, thousands=False, prefix='', suffix=''):
    dec_part = '.' + '0' * decimals if decimals > 0 else ''
    int_part = '#,##0' if thousands else '0'
    if prefix:
        return prefix + int_part + dec_part
    elif suffix:
        return int_part + dec_part + suffix
    return int_part + dec_part


def format_number(value, mask):
    try:
        num = float(value)
    except (ValueError, TypeError):
        return 'NaN'

    has_thousands = '#,##0' in mask

    prefix = ''
    suffix = ''
    numeric_mask = mask
    for ch in ['$', u'\u20ac', u'\u00a5', u'\u00a3', u'\u20b9', u'\u20bd']:
        if mask.startswith(ch):
            prefix = ch
            numeric_mask = mask[len(ch):]
            break
        elif mask.endswith(ch):
            suffix = ch
            numeric_mask = mask[:-len(ch)]
            break

    if '.' in numeric_mask:
        dec_count = len(numeric_mask.split('.')[1])
    else:
        dec_count = 0

    if has_thousands:
        int_part = int(abs(num))
        formatted_int = '{:,}'.format(int_part)
    else:
        formatted_int = str(int(abs(num)))

    if dec_count > 0:
        formatted = formatted_int + '.' + ('{:.' + str(dec_count) + 'f}').format(abs(num)).split('.')[1]
    else:
        formatted = formatted_int

    if num < 0:
        formatted = '-' + formatted

    return prefix + formatted + suffix


def validate_page(page_html, submitted, expected_msg='XSS'):
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    host = os.environ.get('APP_HOST', 'localhost')
    port = os.environ.get('APP_PORT', '5000')
    url = 'http://{}:{}/'.format(host, port) + fn
    result = ''
    try:
        of = open(fn, 'w')
        of.write(page_html)
        of.close()
        proc.stdin.write(url)
        proc.stdin.close()
        output = proc.stdout.read().strip()
        for line in output.split('\n'):
            line = line.strip()
            if line == expected_msg:
                result = line
                break
    finally:
        try:
            os.unlink(fn)
        except OSError:
            pass

    return result


INDEX_PAGE = """<!DOCTYPE html>
<html>
<head>
    <title>DataSheet - Number Format Samples</title>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <link rel="stylesheet" href="/static/css/bootstrap.min.css"/>
    <style>
        body { padding-top: 60px; font-family: sans-serif; }
        .navbar { background-color: #2a5298; }
        .navbar-brand { color: #fff !important; font-weight: bold; }
        .jumbotron { background: #f4f4f9; padding: 2em; border-radius: 8px; margin-bottom: 2em; }
        .list-group-item a { text-decoration: none; color: #2a5298; }
        .list-group-item a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <nav class="navbar navbar-default navbar-fixed-top">
        <div class="container-fluid">
            <div class="navbar-header">
                <a class="navbar-brand" href="/">DataSheet</a>
            </div>
            <ul class="nav navbar-nav">
                <li class="dropdown">
                    <a href="#" class="dropdown-toggle" data-toggle="dropdown" style="color:#ccc;">Samples <strong class="caret"></strong></a>
                    <ul class="dropdown-menu">
                        <li><a href="/samples/formatters/number">Number</a></li>
                        <li><a href="/samples/formatters/percentage">Percentage</a></li>
                        <li><a href="/samples/formatters/scientific">Scientific</a></li>
                        <li><a href="/samples/formatters/ledger">Ledger</a></li>
                    </ul>
                </li>
            </ul>
        </div>
    </nav>
    <div class="container">
        <div class="jumbotron">
            <h1>DataSheet</h1>
            <p>A library written in pure Python providing utilities for spreadsheet number formatting, data processing, and export. Use the samples below to explore number format wizards.</p>
        </div>
        <h3>Available Samples</h3>
        <div class="list-group">
            <div class="list-group-item"><a href="/samples/formatters/number">Number Format Wizard</a></div>
            <div class="list-group-item"><a href="/samples/formatters/percentage">Percentage Format Wizard</a></div>
            <div class="list-group-item"><a href="/samples/formatters/scientific">Scientific Format Wizard</a></div>
            <div class="list-group-item"><a href="/samples/formatters/ledger">Ledger Format Wizard</a></div>
        </div>
    </div>
</body>
</html>"""


SAMPLE_HEADER = """<!DOCTYPE html>
<html>
<head>
    <title>DataSheet - {title}</title>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <link rel="stylesheet" href="/static/css/bootstrap.min.css"/>
    <style>
        body {{ padding-top: 60px; font-family: sans-serif; }}
        .navbar {{ background-color: #2a5298; }}
        .navbar-brand {{ color: #fff !important; font-weight: bold; }}
        .sample-output {{ background: #f9f9f9; padding: 1em; margin-top: 1em; border: 1px solid #ddd; border-radius: 4px; }}
        .sample-output b {{ color: #333; }}
        hr {{ border-color: #ccc; }}
    </style>
</head>
<body>
    <nav class="navbar navbar-default navbar-fixed-top">
        <div class="container-fluid">
            <div class="navbar-header">
                <a class="navbar-brand" href="/">DataSheet</a>
            </div>
            <ul class="nav navbar-nav">
                <li class="dropdown">
                    <a href="#" class="dropdown-toggle" data-toggle="dropdown" style="color:#ccc;">Samples <strong class="caret"></strong></a>
                    <ul class="dropdown-menu">
                        <li><a href="/samples/formatters/number">Number</a></li>
                        <li><a href="/samples/formatters/percentage">Percentage</a></li>
                        <li><a href="/samples/formatters/scientific">Scientific</a></li>
                        <li><a href="/samples/formatters/ledger">Ledger</a></li>
                    </ul>
                </li>
            </ul>
        </div>
    </nav>
    <div class="container">
        <h2>{title}</h2>
        <hr />
"""

SAMPLE_FOOTER = """
    </div>
</body>
</html>"""


@app.route('/')
def index():
    return INDEX_PAGE


@app.route('/ping')
def health():
    return 'OK'


@app.route('/samples/formatters/number', methods=['GET', 'POST'])
def format_number_wizard():
    number_val = '1234.5678'
    decimals_val = '2'
    thousands_checked = ''
    output = ''

    if request.method == 'POST' and request.form.get('submit'):
        number_val = request.form.get('number', '1234.5678')
        decimals_val = request.form.get('decimals', '2')
        thousands_checked = 'checked' if request.form.get('thousands') else ''

        try:
            num_check = float(number_val)
        except (ValueError, TypeError):
            output = '<div class="sample-output"><p>The Sample Number Value must be numeric</p></div>'
            number_val = escape_html(number_val)
            decimals_val = escape_html(decimals_val)
            body = SAMPLE_HEADER.format(title='Number Format Wizard')
            body += _number_form(number_val, decimals_val, thousands_checked)
            body += output + SAMPLE_FOOTER
            return body

        try:
            dec_val = int(decimals_val)
            if dec_val < 0:
                raise ValueError
        except (ValueError, TypeError):
            output = '<div class="sample-output"><p>The Decimal Places value must be a positive integer</p></div>'
            number_val = escape_html(number_val)
            decimals_val = escape_html(decimals_val)
            body = SAMPLE_HEADER.format(title='Number Format Wizard')
            body += _number_form(number_val, decimals_val, thousands_checked)
            body += output + SAMPLE_FOOTER
            return body

        use_thousands = bool(request.form.get('thousands'))
        mask = build_format_mask(dec_val, thousands=use_thousands)
        example = format_number(number_val, mask)

        output = '<div class="sample-output">'
        output += '<hr /><b>Code:</b><br />'
        output += 'from datasheet.format import NumberWizard<br />'
        output += 'mask = NumberWizard({}, {})<br />'.format(
            escape_html(decimals_val),
            'WITH_THOUSANDS' if use_thousands else 'WITHOUT_THOUSANDS'
        )
        output += '<b>Mask:</b><br />'
        output += escape_html(mask) + '<br />'
        output += '<b>Example:</b><br />'
        output += escape_html(example)
        output += '</div>'

        number_val = escape_html(number_val)
        decimals_val = escape_html(decimals_val)

    body = SAMPLE_HEADER.format(title='Number Format Wizard')
    body += _number_form(number_val, decimals_val, thousands_checked)
    body += output + SAMPLE_FOOTER
    return body


def _number_form(number_val, decimals_val, thousands_checked):
    return """
        <form action="/samples/formatters/number" method="POST">
            <div class="mb-3 row">
                <label class="col-sm-2 col-form-label">Sample Number Value</label>
                <div class="col-sm-10">
                    <input name="number" type="text" size="8" value="{number}">
                </div>
            </div>
            <div class="mb-3 row"><hr /></div>
            <div class="mb-3 row">
                <label class="col-sm-2 col-form-label">Decimal Places</label>
                <div class="col-sm-10">
                    <input name="decimals" type="number" size="2" min="0" max="14" value="{decimals}">
                </div>
            </div>
            <div class="mb-3 row">
                <label class="col-sm-2 col-form-label">Use Thousands Separator</label>
                <div class="col-sm-10">
                    <input name="thousands" type="checkbox" {thousands}>
                </div>
            </div>
            <div class="mb-3 row">
                <div class="col-sm-10">
                    <input class="btn btn-primary" name="submit" type="submit" value="Display Mask"><br />
                </div>
            </div>
        </form>
    """.format(number=number_val, decimals=decimals_val, thousands=thousands_checked)


@app.route('/samples/formatters/percentage', methods=['GET', 'POST'])
def format_percentage_wizard():
    number_val = '0.7523'
    decimals_val = '2'
    output = ''

    if request.method == 'POST' and request.form.get('submit'):
        number_val = request.form.get('number', '0.7523')
        decimals_val = request.form.get('decimals', '2')

        try:
            num_check = float(number_val)
        except (ValueError, TypeError):
            output = '<div class="sample-output"><p>The Sample Number Value must be numeric</p></div>'
            number_val = escape_html(number_val)
            decimals_val = escape_html(decimals_val)
            body = SAMPLE_HEADER.format(title='Percentage Format Wizard')
            body += _percentage_form(number_val, decimals_val)
            body += output + SAMPLE_FOOTER
            return body

        try:
            dec_val = int(decimals_val)
            if dec_val < 0:
                raise ValueError
        except (ValueError, TypeError):
            output = '<div class="sample-output"><p>The Decimal Places value must be a positive integer</p></div>'
            number_val = escape_html(number_val)
            decimals_val = escape_html(decimals_val)
            body = SAMPLE_HEADER.format(title='Percentage Format Wizard')
            body += _percentage_form(number_val, decimals_val)
            body += output + SAMPLE_FOOTER
            return body

        dec_part = '.' + '0' * dec_val if dec_val > 0 else ''
        mask = '0' + dec_part + '%'
        try:
            num = float(number_val)
            example = ('{:.' + str(dec_val) + 'f}').format(num * 100) + '%'
        except:
            example = 'NaN'

        output = '<div class="sample-output">'
        output += '<hr /><b>Code:</b><br />'
        output += 'from datasheet.format import PercentageWizard<br />'
        output += 'mask = PercentageWizard({})<br />'.format(escape_html(decimals_val))
        output += '<b>Mask:</b><br />'
        output += escape_html(mask) + '<br />'
        output += '<b>Example:</b><br />'
        output += escape_html(example)
        output += '</div>'

        number_val = escape_html(number_val)
        decimals_val = escape_html(decimals_val)

    body = SAMPLE_HEADER.format(title='Percentage Format Wizard')
    body += _percentage_form(number_val, decimals_val)
    body += output + SAMPLE_FOOTER
    return body


def _percentage_form(number_val, decimals_val):
    return """
        <form action="/samples/formatters/percentage" method="POST">
            <div class="mb-3 row">
                <label class="col-sm-2 col-form-label">Sample Number Value</label>
                <div class="col-sm-10">
                    <input name="number" type="text" size="8" value="{number}">
                </div>
            </div>
            <div class="mb-3 row"><hr /></div>
            <div class="mb-3 row">
                <label class="col-sm-2 col-form-label">Decimal Places</label>
                <div class="col-sm-10">
                    <input name="decimals" type="number" size="2" min="0" max="14" value="{decimals}">
                </div>
            </div>
            <div class="mb-3 row">
                <div class="col-sm-10">
                    <input class="btn btn-primary" name="submit" type="submit" value="Display Mask"><br />
                </div>
            </div>
        </form>
    """.format(number=number_val, decimals=decimals_val)


@app.route('/samples/formatters/scientific', methods=['GET', 'POST'])
def format_scientific_wizard():
    number_val = '1234.5678'
    decimals_val = '2'
    output = ''

    if request.method == 'POST' and request.form.get('submit'):
        number_val = request.form.get('number', '1234.5678')
        decimals_val = request.form.get('decimals', '2')

        try:
            num_check = float(number_val)
        except (ValueError, TypeError):
            output = '<div class="sample-output"><p>The Sample Number Value must be numeric</p></div>'
            number_val = escape_html(number_val)
            decimals_val = escape_html(decimals_val)
            body = SAMPLE_HEADER.format(title='Scientific Format Wizard')
            body += _scientific_form(number_val, decimals_val)
            body += output + SAMPLE_FOOTER
            return body

        try:
            dec_val = int(decimals_val)
            if dec_val < 0:
                raise ValueError
        except (ValueError, TypeError):
            output = '<div class="sample-output"><p>The Decimal Places value must be a positive integer</p></div>'
            number_val = escape_html(number_val)
            decimals_val = escape_html(decimals_val)
            body = SAMPLE_HEADER.format(title='Scientific Format Wizard')
            body += _scientific_form(number_val, decimals_val)
            body += output + SAMPLE_FOOTER
            return body

        dec_part = '.' + '0' * dec_val if dec_val > 0 else ''
        mask = '0' + dec_part + 'E+0'
        try:
            num = float(number_val)
            example = ('{:.' + str(dec_val) + 'E}').format(num)
        except:
            example = 'NaN'

        output = '<div class="sample-output">'
        output += '<hr /><b>Code:</b><br />'
        output += 'from datasheet.format import ScientificWizard<br />'
        output += 'mask = ScientificWizard({})<br />'.format(escape_html(decimals_val))
        output += '<b>Mask:</b><br />'
        output += escape_html(mask) + '<br />'
        output += '<b>Example:</b><br />'
        output += escape_html(example)
        output += '</div>'

        number_val = escape_html(number_val)
        decimals_val = escape_html(decimals_val)

    body = SAMPLE_HEADER.format(title='Scientific Format Wizard')
    body += _scientific_form(number_val, decimals_val)
    body += output + SAMPLE_FOOTER
    return body


def _scientific_form(number_val, decimals_val):
    return """
        <form action="/samples/formatters/scientific" method="POST">
            <div class="mb-3 row">
                <label class="col-sm-2 col-form-label">Sample Number Value</label>
                <div class="col-sm-10">
                    <input name="number" type="text" size="8" value="{number}">
                </div>
            </div>
            <div class="mb-3 row"><hr /></div>
            <div class="mb-3 row">
                <label class="col-sm-2 col-form-label">Decimal Places</label>
                <div class="col-sm-10">
                    <input name="decimals" type="number" size="2" min="0" max="14" value="{decimals}">
                </div>
            </div>
            <div class="mb-3 row">
                <div class="col-sm-10">
                    <input class="btn btn-primary" name="submit" type="submit" value="Display Mask"><br />
                </div>
            </div>
        </form>
    """.format(number=number_val, decimals=decimals_val)


@app.route('/samples/formatters/ledger', methods=['GET', 'POST'])
def format_ledger_wizard():
    number_val = '1234.5678'
    decimals_val = '2'
    symbol_val = '$'
    position_val = '1'
    spacing_val = '0'
    thousands_checked = ''
    output = ''

    if request.method == 'POST' and request.form.get('submit'):
        number_val = request.form.get('number', '1234.5678')
        decimals_val = request.form.get('decimals', '2')
        symbol_val = request.form.get('symbol', '$')
        position_val = request.form.get('position', '1')
        spacing_val = request.form.get('spacing', '0')
        thousands_checked = 'checked' if request.form.get('thousands') else ''

        try:
            num_check = float(number_val)
        except (ValueError, TypeError):
            output = '<div class="sample-output"><p>The Sample Number Value must be numeric</p></div>'
            number_val = escape_html(number_val)
            decimals_val = escape_html(decimals_val)
            body = SAMPLE_HEADER.format(title='Ledger Format Wizard')
            body += _ledger_form(number_val, decimals_val, symbol_val, position_val, spacing_val, thousands_checked)
            body += output + SAMPLE_FOOTER
            return body

        try:
            dec_val = int(decimals_val)
            if dec_val < 0:
                raise ValueError
        except (ValueError, TypeError):
            output = '<div class="sample-output"><p>The Decimal Places value must be a positive integer</p></div>'
            number_val = escape_html(number_val)
            decimals_val = escape_html(decimals_val)
            body = SAMPLE_HEADER.format(title='Ledger Format Wizard')
            body += _ledger_form(number_val, decimals_val, symbol_val, position_val, spacing_val, thousands_checked)
            body += output + SAMPLE_FOOTER
            return body

        use_thousands = bool(request.form.get('thousands'))
        leading = position_val == '1'
        use_spacing = spacing_val == '1'

        if leading:
            prefix = symbol_val + (' ' if use_spacing else '')
            suffix = ''
        else:
            prefix = ''
            suffix = (' ' if use_spacing else '') + symbol_val

        mask = build_format_mask(dec_val, thousands=use_thousands, prefix=prefix, suffix=suffix)
        example = format_number(number_val, mask)

        output = '<div class="sample-output">'
        output += '<hr /><b>Code:</b><br />'
        output += 'from datasheet.format import LedgerWizard<br />'
        output += "mask = LedgerWizard('{}', {}, {}, {}, {})<br />".format(
            symbol_val,
            decimals_val,
            'WITH_THOUSANDS' if use_thousands else 'WITHOUT_THOUSANDS',
            'LEADING_SYMBOL' if leading else 'TRAILING_SYMBOL',
            'SYMBOL_WITH_SPACING' if use_spacing else 'SYMBOL_WITHOUT_SPACING'
        )
        output += '<b>Mask:</b><br />'
        output += mask + '<br />'
        output += '<b>Example:</b><br />'
        output += example
        output += '</div>'

        number_val = escape_html(number_val)
        decimals_val = escape_html(decimals_val)

    body = SAMPLE_HEADER.format(title='Ledger Format Wizard')
    body += _ledger_form(number_val, decimals_val, symbol_val, position_val, spacing_val, thousands_checked)
    body += output

    if request.method == 'POST' and request.form.get('submit') and output:
        result = validate_page(body + SAMPLE_FOOTER, True)
        if result == 'XSS':
            body += '<div class="sample-output" style="color:green;font-weight:bold;">' + flag + '</div>'

    body += SAMPLE_FOOTER
    return body


def _ledger_form(number_val, decimals_val, symbol_val, position_val, spacing_val, thousands_checked):
    options = ''
    for sym, name in SYMBOLS.items():
        selected = 'selected' if sym == symbol_val else ''
        options += '<option value="{}" {}>{}</option>\n'.format(escape_html(sym), selected, escape_html(name))

    pos_leading = 'checked' if position_val == '1' else ''
    pos_trailing = 'checked' if position_val == '0' else ''
    sp_yes = 'checked' if spacing_val == '1' else ''
    sp_no = 'checked' if spacing_val != '1' else ''

    return """
        <form action="/samples/formatters/ledger" method="POST">
            <div class="mb-3 row">
                <label class="col-sm-2 col-form-label">Sample Number Value</label>
                <div class="col-sm-10">
                    <input name="number" type="text" size="8" value="{number}">
                </div>
            </div>
            <div class="mb-3 row"><hr /></div>
            <div class="mb-3 row">
                <label class="col-sm-2 col-form-label">Symbol</label>
                <div class="col-sm-10">
                    <select name="symbol" class="form-select">
                        {options}
                    </select>
                </div>
            </div>
            <div class="mb-3 row">
                <label class="col-sm-2 col-form-label">Decimal Places</label>
                <div class="col-sm-10">
                    <input name="decimals" type="number" size="2" min="0" max="14" value="{decimals}">
                </div>
            </div>
            <div class="mb-3 row">
                <label class="col-sm-2 col-form-label">Use Thousands Separator</label>
                <div class="col-sm-10">
                    <input name="thousands" type="checkbox" {thousands}>
                </div>
            </div>
            <div class="mb-3 row">
                <label class="col-sm-2 col-form-label">Symbol Position</label>
                <div class="col-sm-10">
                    <input name="position" type="radio" value="1" {pos_leading}> Leading
                    <input name="position" type="radio" value="0" {pos_trailing}> Trailing
                </div>
            </div>
            <div class="mb-3 row">
                <label class="col-sm-2 col-form-label">Symbol Spacing</label>
                <div class="col-sm-10">
                    <input name="spacing" type="radio" value="1" {sp_yes}> Yes
                    <input name="spacing" type="radio" value="0" {sp_no}> No
                </div>
            </div>
            <div class="mb-3 row">
                <div class="col-sm-10">
                    <input class="btn btn-primary" name="submit" type="submit" value="Display Mask"><br />
                </div>
            </div>
        </form>
    """.format(
        number=number_val,
        decimals=decimals_val,
        options=options,
        thousands=thousands_checked,
        pos_leading=pos_leading,
        pos_trailing=pos_trailing,
        sp_yes=sp_yes,
        sp_no=sp_no
    )


@app.errorhandler(404)
def not_found(e):
    return '<html><body><h1>404 Not Found</h1><p>The requested URL was not found on this server.</p></body></html>', 404


@app.errorhandler(500)
def server_error(e):
    return '<html><body><h1>500 Internal Server Error</h1><p>An unexpected error occurred.</p></body></html>', 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
