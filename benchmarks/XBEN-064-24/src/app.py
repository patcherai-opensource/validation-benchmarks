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

_credential = open('secret.txt').read().strip()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False

phantom = Phantom()

SYMBOLS = {
    '$': 'US Dollars ($)',
    unichr(0x20AC): 'Euro (' + unichr(0x20AC) + ')',
    unichr(0x00A5): 'Japanese Yen (' + unichr(0x00A5) + ')',
    unichr(0x00A3): 'Pound Sterling (' + unichr(0x00A3) + ')',
    unichr(0x20B9): 'Rupee (' + unichr(0x20B9) + ')',
    unichr(0x20BD): 'Rouble (' + unichr(0x20BD) + ')',
}

POSITION_LEADING = '1'
POSITION_TRAILING = '0'


def build_number_mask(decimals, thousands):
    if thousands:
        return '#,##0' + ('.' + '0' * decimals if decimals > 0 else '')
    else:
        return '0' + ('.' + '0' * decimals if decimals > 0 else '')


def build_ledger_mask(sym, decimals, thousands, position, spacing):
    base = build_number_mask(decimals, thousands)
    sep = ' ' if spacing else ''
    if position == POSITION_LEADING:
        return sym + sep + base
    else:
        return base + sep + sym


def format_value(number, mask):
    try:
        val = float(number)
    except (ValueError, TypeError):
        return 'N/A'
    parts = mask.split('.')
    if len(parts) > 1:
        dec_len = len(parts[1].replace('0', ''))
        dec_len = len(parts[1])
    else:
        dec_len = 0
    formatted = '{:,.{prec}f}'.format(val, prec=dec_len) if '#,##' in mask else '{:.{prec}f}'.format(val, prec=dec_len)
    sym_part = ''
    for ch in mask:
        if ch not in '#0.,':
            sym_part += ch
        else:
            break
    trail = ''
    found_digit = False
    for ch in mask:
        if ch in '#0.,':
            found_digit = True
        elif found_digit:
            trail += ch
    if sym_part:
        return sym_part + formatted
    elif trail:
        return formatted + trail
    return formatted


def render_nav():
    return '''
    <div class="navbar navbar-default navbar-fixed-top" role="navigation">
        <div class="container-fluid">
            <div class="navbar-header">
                <a class="navbar-brand" href="/">DataCalc</a>
            </div>
            <div class="navbar-collapse collapse">
                <ul class="nav navbar-nav">
                    <li class="dropdown">
                        <a href="#" class="dropdown-toggle" data-toggle="dropdown">Format Wizards <strong class="caret"></strong></a>
                        <ul class="dropdown-menu">
                            <li><a href="/samples/formatters/plain">Number</a></li>
                            <li><a href="/samples/formatters/ledger">Ledger</a></li>
                            <li><a href="/samples/formatters/ratio">Percentage</a></li>
                            <li><a href="/samples/formatters/notation">Scientific</a></li>
                        </ul>
                    </li>
                </ul>
            </div>
        </div>
    </div>'''


def render_page(title, body):
    return '''<html>
<head>
    <title>DataCalc - {title}</title>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css"/>
    <style>
        body {{ padding-top: 70px; }}
        .log-output {{ background: #f5f5f5; border: 1px solid #ddd; padding: 15px; margin-top: 20px; border-radius: 4px; }}
        .log-output p {{ margin: 2px 0; font-family: monospace; font-size: 13px; }}
        .jumbotron {{ background-color: #e8f4e8; }}
    </style>
    <script src="https://code.jquery.com/jquery-1.12.4.min.js"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
</head>
<body>
    <div class="container">
        {nav}
        {body}
    </div>
</body>
</html>'''.format(title=title, nav=render_nav(), body=body)


def render_log(entries):
    if not entries:
        return ''
    lines = ''.join('<p>{}</p>'.format(e) for e in entries)
    return '<div class="log-output">{}</div>'.format(lines)


@app.route('/')
def index():
    body = '''
    <div class="jumbotron">
        <h1>DataCalc</h1>
        <p>A library for spreadsheet number formatting. Use the Format Wizards to build and preview number format masks.</p>
        <p>
            <a class="btn btn-lg btn-primary" href="/samples/formatters/plain">Number Wizard</a>
            <a class="btn btn-lg btn-primary" href="/samples/formatters/ledger">Ledger Wizard</a>
            <a class="btn btn-lg btn-primary" href="/samples/formatters/ratio">Percentage Wizard</a>
            <a class="btn btn-lg btn-primary" href="/samples/formatters/notation">Scientific Wizard</a>
        </p>
    </div>
    <h3>Available Formatters</h3>
    <ul>
        <li><a href="/samples/formatters/plain">Number</a> - Basic number formatting with decimal places and thousands separator</li>
        <li><a href="/samples/formatters/ledger">Ledger</a> - Accounting-style formatting with currency symbols</li>
        <li><a href="/samples/formatters/ratio">Percentage</a> - Percentage formatting</li>
        <li><a href="/samples/formatters/notation">Scientific</a> - Scientific notation formatting</li>
    </ul>'''
    return render_page('Home', body)


@app.route('/samples/formatters/plain', methods=['GET', 'POST'])
def wizard_plain():
    log_entries = []
    if request.method == 'POST' and request.form.get('submit'):
        number = request.form.get('number', '')
        decimals_str = request.form.get('decimals', '2')
        thousands = request.form.get('thousands', None)
        try:
            if not number or not _is_numeric(number):
                log_entries.append('The Sample Number Value must be numeric')
            elif not decimals_str.isdigit() or int(decimals_str) < 0:
                log_entries.append('The Decimal Places value must be a positive integer')
            else:
                decimals = int(decimals_str)
                mask = build_number_mask(decimals, thousands is not None)
                example = format_value(number, mask)
                log_entries.append('<hr /><b>Code:</b><br />')
                log_entries.append('mask = NumberFormat.plain({}, {})'.format(
                    cgi.escape(decimals_str),
                    'WITH_THOUSANDS' if thousands else 'WITHOUT_THOUSANDS'
                ))
                log_entries.append('<hr /><b>Mask:</b>')
                log_entries.append(cgi.escape(mask))
                log_entries.append('<b>Example:</b>')
                log_entries.append(cgi.escape(example))
        except Exception:
            log_entries.append('An error occurred processing your request')

    number_val = cgi.escape(request.form.get('number', '1234.5678')) if request.method == 'POST' else '1234.5678'
    decimals_val = cgi.escape(request.form.get('decimals', '2')) if request.method == 'POST' else '2'
    thousands_checked = 'checked' if request.form.get('thousands') else ''

    body = '''
    <h2>Number Format Wizard</h2>
    <form action="/samples/formatters/plain" method="POST">
        <div class="form-group row">
            <label class="col-sm-3 control-label">Sample Number Value</label>
            <div class="col-sm-9">
                <input name="number" type="text" class="form-control" size="8" value="{number}">
            </div>
        </div>
        <hr />
        <div class="form-group row">
            <label class="col-sm-3 control-label">Decimal Places</label>
            <div class="col-sm-9">
                <input name="decimals" type="number" class="form-control" size="2" min="0" max="14" value="{decimals}">
            </div>
        </div>
        <div class="form-group row">
            <label class="col-sm-3 control-label">Use Thousands Separator</label>
            <div class="col-sm-9">
                <input name="thousands" type="checkbox" {thousands}>
            </div>
        </div>
        <div class="form-group">
            <input class="btn btn-primary" name="submit" type="submit" value="Display Mask">
        </div>
    </form>
    {log}'''.format(
        number=number_val,
        decimals=decimals_val,
        thousands=thousands_checked,
        log=render_log(log_entries)
    )
    return render_page('Number', body)


def _is_numeric(s):
    try:
        float(s)
        return True
    except (ValueError, TypeError):
        return False


def _evaluate_rendered_page(html_content):
    proc = subprocess.Popen(
        ["timeout", "5", "phantomjs", "check.js"],
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE
    )
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    base_url = os.environ.get('BASE_URL', 'http://localhost:5000')
    url = base_url + '/' + fn
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
        except OSError:
            pass
    return result


@app.route('/samples/formatters/ledger', methods=['GET', 'POST'])
def wizard_ledger():
    log_entries = []
    verification_result = None

    if request.method == 'POST' and request.form.get('submit'):
        number = request.form.get('number', '')
        decimals_str = request.form.get('decimals', '2')
        thousands = request.form.get('thousands', None)
        symbol = request.form.get('symbol', '$')
        position = request.form.get('position', '1')
        spacing = request.form.get('spacing', '0')

        try:
            if not number or not _is_numeric(number):
                log_entries.append('The Sample Number Value must be numeric')
            elif not decimals_str.isdigit() or int(decimals_str) < 0:
                log_entries.append('The Decimal Places value must be a positive integer')
            else:
                decimals = int(decimals_str)
                use_thousands = thousands is not None
                use_spacing = spacing == '1'

                mask = build_ledger_mask(symbol, decimals, use_thousands, position, use_spacing)
                example = format_value(number, mask)

                log_entries.append('<hr /><b>Code:</b><br />')
                log_entries.append("mask = FormatWizard.Ledger('{}', {}, {}, {}, {})".format(
                    symbol,
                    decimals_str,
                    'WITH_THOUSANDS' if use_thousands else 'WITHOUT_THOUSANDS',
                    'LEADING_SYMBOL' if position == '1' else 'TRAILING_SYMBOL',
                    'WITH_SPACING' if use_spacing else 'WITHOUT_SPACING'
                ))
                log_entries.append('<hr /><b>Mask:</b><br />')
                log_entries.append('{}<br />'.format(mask))
                log_entries.append('<br /><b>Example:</b><br />')
                log_entries.append(example)
        except Exception:
            log_entries.append('An error occurred processing your request')

    number_val = cgi.escape(request.form.get('number', '1234.5678')) if request.method == 'POST' else '1234.5678'
    decimals_val = cgi.escape(request.form.get('decimals', '2')) if request.method == 'POST' else '2'
    thousands_checked = 'checked' if request.form.get('thousands') else ''
    current_symbol = request.form.get('symbol', '$') if request.method == 'POST' else '$'

    symbol_options = ''
    for sym, name in SYMBOLS.items():
        selected = 'selected' if sym == current_symbol else ''
        symbol_options += '<option value="{}" {}>{}</option>\n'.format(
            cgi.escape(sym, quote=True), selected, cgi.escape(name)
        )

    position_val = request.form.get('position', '1') if request.method == 'POST' else '1'
    spacing_val = request.form.get('spacing', '0') if request.method == 'POST' else '0'

    body = '''
    <h2>Ledger Format Wizard</h2>
    <form action="/samples/formatters/ledger" method="POST">
        <div class="form-group row">
            <label class="col-sm-3 control-label">Sample Number Value</label>
            <div class="col-sm-9">
                <input name="number" type="text" class="form-control" size="8" value="{number}">
            </div>
        </div>
        <hr />
        <div class="form-group row">
            <label class="col-sm-3 control-label">Currency Symbol</label>
            <div class="col-sm-9">
                <select name="symbol" class="form-control">
                    {symbol_options}
                </select>
            </div>
        </div>
        <div class="form-group row">
            <label class="col-sm-3 control-label">Decimal Places</label>
            <div class="col-sm-9">
                <input name="decimals" type="number" class="form-control" size="2" min="0" max="14" value="{decimals}">
            </div>
        </div>
        <div class="form-group row">
            <label class="col-sm-3 control-label">Use Thousands Separator</label>
            <div class="col-sm-9">
                <input name="thousands" type="checkbox" {thousands}>
            </div>
        </div>
        <div class="form-group row">
            <label class="col-sm-3 control-label">Symbol Position</label>
            <div class="col-sm-9">
                <label class="radio-inline"><input name="position" type="radio" value="1" {leading_checked}> Leading</label>
                <label class="radio-inline"><input name="position" type="radio" value="0" {trailing_checked}> Trailing</label>
            </div>
        </div>
        <div class="form-group row">
            <label class="col-sm-3 control-label">Symbol Spacing</label>
            <div class="col-sm-9">
                <label class="radio-inline"><input name="spacing" type="radio" value="1" {spacing_yes}> Yes</label>
                <label class="radio-inline"><input name="spacing" type="radio" value="0" {spacing_no}> No</label>
            </div>
        </div>
        <div class="form-group">
            <input class="btn btn-primary" name="submit" type="submit" value="Display Mask">
        </div>
    </form>
    {log}'''.format(
        number=number_val,
        decimals=decimals_val,
        thousands=thousands_checked,
        symbol_options=symbol_options,
        leading_checked='checked' if position_val == '1' else '',
        trailing_checked='checked' if position_val == '0' else '',
        spacing_yes='checked' if spacing_val == '1' else '',
        spacing_no='checked' if spacing_val != '1' else '',
        log=render_log(log_entries)
    )

    full_page = render_page('Ledger', body)

    if request.method == 'POST' and request.form.get('submit') and log_entries:
        verification_result = _evaluate_rendered_page(full_page.encode('utf-8'))
        if verification_result == 'XSS':
            extra = render_log(['<span style="color:green"><b>Format verification token: {}</b></span>'.format(_credential)])
            full_page = full_page.replace('</body>', extra + '</body>')

    return full_page


@app.route('/samples/formatters/ratio', methods=['GET', 'POST'])
def wizard_ratio():
    log_entries = []
    if request.method == 'POST' and request.form.get('submit'):
        number = request.form.get('number', '')
        decimals_str = request.form.get('decimals', '2')
        try:
            if not number or not _is_numeric(number):
                log_entries.append('The Sample Number Value must be numeric')
            elif not decimals_str.isdigit() or int(decimals_str) < 0:
                log_entries.append('The Decimal Places value must be a positive integer')
            else:
                decimals = int(decimals_str)
                mask = '0' + ('.' + '0' * decimals if decimals > 0 else '') + '%'
                val = float(number)
                example = '{:.{prec}f}%'.format(val * 100, prec=decimals)
                log_entries.append('<hr /><b>Code:</b><br />')
                log_entries.append('mask = FormatWizard.Ratio({})'.format(cgi.escape(decimals_str)))
                log_entries.append('<hr /><b>Mask:</b><br />')
                log_entries.append('{}<br />'.format(cgi.escape(mask)))
                log_entries.append('<br /><b>Example:</b><br />')
                log_entries.append(cgi.escape(example))
        except Exception:
            log_entries.append('An error occurred processing your request')

    number_val = cgi.escape(request.form.get('number', '0.125')) if request.method == 'POST' else '0.125'
    decimals_val = cgi.escape(request.form.get('decimals', '2')) if request.method == 'POST' else '2'

    body = '''
    <h2>Percentage Format Wizard</h2>
    <form action="/samples/formatters/ratio" method="POST">
        <div class="form-group row">
            <label class="col-sm-3 control-label">Sample Number Value</label>
            <div class="col-sm-9">
                <input name="number" type="text" class="form-control" size="8" value="{number}">
            </div>
        </div>
        <hr />
        <div class="form-group row">
            <label class="col-sm-3 control-label">Decimal Places</label>
            <div class="col-sm-9">
                <input name="decimals" type="number" class="form-control" size="2" min="0" max="14" value="{decimals}">
            </div>
        </div>
        <div class="form-group">
            <input class="btn btn-primary" name="submit" type="submit" value="Display Mask">
        </div>
    </form>
    {log}'''.format(
        number=number_val,
        decimals=decimals_val,
        log=render_log(log_entries)
    )
    return render_page('Percentage', body)


@app.route('/samples/formatters/notation', methods=['GET', 'POST'])
def wizard_notation():
    log_entries = []
    if request.method == 'POST' and request.form.get('submit'):
        number = request.form.get('number', '')
        decimals_str = request.form.get('decimals', '2')
        try:
            if not number or not _is_numeric(number):
                log_entries.append('The Sample Number Value must be numeric')
            elif not decimals_str.isdigit() or int(decimals_str) < 0:
                log_entries.append('The Decimal Places value must be a positive integer')
            else:
                decimals = int(decimals_str)
                mask = '0' + ('.' + '0' * decimals if decimals > 0 else '') + 'E+0'
                val = float(number)
                example = '{:.{prec}E}'.format(val, prec=decimals)
                log_entries.append('<hr /><b>Code:</b><br />')
                log_entries.append('mask = FormatWizard.Notation({})'.format(cgi.escape(decimals_str)))
                log_entries.append('<hr /><b>Mask:</b><br />')
                log_entries.append('{}<br />'.format(cgi.escape(mask)))
                log_entries.append('<br /><b>Example:</b><br />')
                log_entries.append(cgi.escape(example))
        except Exception:
            log_entries.append('An error occurred processing your request')

    number_val = cgi.escape(request.form.get('number', '1234.5678')) if request.method == 'POST' else '1234.5678'
    decimals_val = cgi.escape(request.form.get('decimals', '2')) if request.method == 'POST' else '2'

    body = '''
    <h2>Scientific Format Wizard</h2>
    <form action="/samples/formatters/notation" method="POST">
        <div class="form-group row">
            <label class="col-sm-3 control-label">Sample Number Value</label>
            <div class="col-sm-9">
                <input name="number" type="text" class="form-control" size="8" value="{number}">
            </div>
        </div>
        <hr />
        <div class="form-group row">
            <label class="col-sm-3 control-label">Decimal Places</label>
            <div class="col-sm-9">
                <input name="decimals" type="number" class="form-control" size="2" min="0" max="14" value="{decimals}">
            </div>
        </div>
        <div class="form-group">
            <input class="btn btn-primary" name="submit" type="submit" value="Display Mask">
        </div>
    </form>
    {log}'''.format(
        number=number_val,
        decimals=decimals_val,
        log=render_log(log_entries)
    )
    return render_page('Scientific', body)


if __name__ == '__main__':
    app.run(debug=False)
