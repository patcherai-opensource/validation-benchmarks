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

flags = open('secret.txt').read().split()

app = Flask(__name__)

phantom = Phantom()

# Supported format symbols for accounting wizard
ACCOUNTING_SYMBOLS = {
    '$': 'US Dollars ($)',
    unichr(0x20AC): 'Euro (' + unichr(0x20AC) + ')',
    unichr(0x00A5): 'Japanese Yen (' + unichr(0x00A5) + ')',
    unichr(0x00A3): 'Pound Sterling (' + unichr(0x00A3) + ')',
    unichr(0x20B9): 'Rupee (' + unichr(0x20B9) + ')',
    unichr(0x20BD): 'Rouble (' + unichr(0x20BD) + ')',
}

def get_page_header(title):
    return '''<!DOCTYPE html>
<html>
<head>
    <title>DataSheet Toolkit - {title}</title>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@3.4.1/dist/css/bootstrap.min.css"/>
    <style>
        body {{ padding-top: 70px; }}
        .log-output {{ background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 4px; font-family: monospace; }}
        .log-entry {{ padding: 3px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="navbar navbar-default navbar-fixed-top" role="navigation">
            <div class="container-fluid">
                <div class="navbar-header">
                    <a class="navbar-brand" href="/">DataSheet Toolkit</a>
                </div>
                <div class="navbar-collapse collapse">
                    <ul class="nav navbar-nav">
                        <li class="dropdown">
                            <a href="#" class="dropdown-toggle" data-toggle="dropdown">Format Wizards <strong class="caret"></strong></a>
                            <ul class="dropdown-menu">
                                <li><a href="/wizards/format/numeric">Numeric</a></li>
                                <li><a href="/wizards/format/accounting">Accounting</a></li>
                                <li><a href="/wizards/format/percent">Percent</a></li>
                                <li><a href="/wizards/format/scientific">Scientific</a></li>
                            </ul>
                        </li>
                    </ul>
                </div>
            </div>
        </div>
'''.format(title=title)

PAGE_FOOTER = '''
    </div>
    <script src="https://cdn.jsdelivr.net/npm/jquery@1.12.4/dist/jquery.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@3.4.1/dist/js/bootstrap.min.js"></script>
</body>
</html>'''


def sanitize_html(value):
    """Escape HTML special characters to prevent XSS."""
    return cgi.escape(value, quote=True)


def format_number(value, decimals, thousands=False):
    """Format a number with the given decimal places and optional thousands separator."""
    try:
        num = float(value)
        if thousands:
            parts = '{:,.{prec}f}'.format(num, prec=int(decimals))
        else:
            parts = '{:.{prec}f}'.format(num, prec=int(decimals))
        return parts
    except (ValueError, TypeError):
        return value


def build_mask(decimals, thousands=False, symbol=None, position='leading', spacing=False):
    """Build a display format mask string."""
    dec_part = '0' * int(decimals) if int(decimals) > 0 else ''
    mask = '#,##0' if thousands else '0'
    if dec_part:
        mask += '.' + dec_part
    if symbol:
        if position == 'leading':
            mask = symbol + (' ' if spacing else '') + mask
        else:
            mask = mask + (' ' if spacing else '') + symbol
    return mask


def render_log(entries):
    """Render log entries as HTML output block."""
    html = '<div class="log-output">'
    for entry in entries:
        html += '<div class="log-entry">' + entry + '</div>'
    html += '</div>'
    return html


def check_xss_post(page_html, flag):
    """Check if XSS was triggered using PhantomJS."""
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://' + os.environ.get('FLASK_HOST', 'localhost') + ':' + os.environ.get('FLASK_PORT', '5000') + '/' + fn
    result = ''
    try:
        of = open(fn, 'w')
        of.write(page_html)
        of.close()
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
    finally:
        try:
            os.unlink(fn)
        except:
            pass

    if result == 'XSS':
        return flag
    return None


@app.route('/')
def index():
    html = get_page_header('Home')
    html += '''
        <div class="jumbotron">
            <h2>DataSheet Format Toolkit</h2>
            <p>Interactive number format wizards for spreadsheet development.</p>
            <p>Select a format wizard from the navigation menu to get started.</p>
        </div>
        <div class="row">
            <div class="col-md-3">
                <div class="panel panel-default">
                    <div class="panel-heading"><h3 class="panel-title">Numeric</h3></div>
                    <div class="panel-body"><a href="/wizards/format/numeric">Basic number formatting</a></div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="panel panel-default">
                    <div class="panel-heading"><h3 class="panel-title">Accounting</h3></div>
                    <div class="panel-body"><a href="/wizards/format/accounting">Currency &amp; accounting formats</a></div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="panel panel-default">
                    <div class="panel-heading"><h3 class="panel-title">Percent</h3></div>
                    <div class="panel-body"><a href="/wizards/format/percent">Percentage formatting</a></div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="panel panel-default">
                    <div class="panel-heading"><h3 class="panel-title">Scientific</h3></div>
                    <div class="panel-body"><a href="/wizards/format/scientific">Scientific notation</a></div>
                </div>
            </div>
        </div>
    '''
    html += PAGE_FOOTER
    return html


@app.route('/wizards/format/numeric', methods=['GET', 'POST'])
def wizard_numeric():
    html = get_page_header('Numeric Format')
    html += '''<h3>Numeric Format Wizard</h3>'''

    number_val = '1234.5678'
    decimals_val = '2'
    thousands_checked = ''

    if request.method == 'POST':
        number_val = sanitize_html(request.form.get('number', '1234.5678'))
        decimals_val = sanitize_html(request.form.get('decimals', '2'))
        if request.form.get('thousands'):
            thousands_checked = 'checked'

    html += '''
    <form action="/wizards/format/numeric" method="POST">
        <div class="form-group row" style="margin-bottom:10px">
            <label class="col-sm-3 control-label">Sample Number Value</label>
            <div class="col-sm-9">
                <input name="number" type="text" class="form-control" value="{number}">
            </div>
        </div>
        <hr/>
        <div class="form-group row" style="margin-bottom:10px">
            <label class="col-sm-3 control-label">Decimal Places</label>
            <div class="col-sm-9">
                <input name="decimals" type="number" class="form-control" min="0" max="14" value="{decimals}">
            </div>
        </div>
        <div class="form-group row" style="margin-bottom:10px">
            <label class="col-sm-3 control-label">Use Thousands Separator</label>
            <div class="col-sm-9">
                <input name="thousands" type="checkbox" {thousands}>
            </div>
        </div>
        <div class="form-group">
            <div class="col-sm-9 col-sm-offset-3">
                <input class="btn btn-primary" name="submit" type="submit" value="Display Mask">
            </div>
        </div>
    </form>
    '''.format(number=number_val, decimals=decimals_val, thousands=thousands_checked)

    if request.method == 'POST' and request.form.get('submit'):
        raw_number = request.form.get('number', '')
        raw_decimals = request.form.get('decimals', '2')
        has_thousands = bool(request.form.get('thousands'))

        log_entries = []
        try:
            if not raw_number.replace('.', '', 1).replace('-', '', 1).isdigit():
                log_entries.append('The Sample Number Value must be numeric')
            elif not raw_decimals.isdigit() or int(raw_decimals) < 0:
                log_entries.append('The Decimal Places value must be a positive integer')
            else:
                mask = build_mask(raw_decimals, thousands=has_thousands)
                example = format_number(raw_number, raw_decimals, thousands=has_thousands)
                log_entries.append('<hr/><b>Code:</b><br/>')
                log_entries.append('from datasheet.format import NumericFormatter')
                log_entries.append(
                    'mask = NumericFormatter({decimals}, {thousands})<br/>'.format(
                        decimals=sanitize_html(raw_decimals),
                        thousands='WITH_THOUSANDS' if has_thousands else 'WITHOUT_THOUSANDS'
                    )
                )
                log_entries.append('print(str(mask))')
                log_entries.append('<hr/><b>Mask:</b><br/>')
                log_entries.append(sanitize_html(mask))
                log_entries.append('<br/><b>Example:</b><br/>')
                log_entries.append(sanitize_html(example))
        except Exception as e:
            log_entries.append('Error: ' + sanitize_html(str(e)))

        html += render_log(log_entries)

    html += PAGE_FOOTER
    return html


@app.route('/wizards/format/accounting', methods=['GET', 'POST'])
def wizard_accounting():
    html = get_page_header('Accounting Format')
    html += '''<h3>Accounting Format Wizard</h3>'''

    number_val = '1234.5678'
    decimals_val = '2'
    thousands_checked = ''
    position_leading = 'checked'
    position_trailing = ''
    spacing_yes = ''
    spacing_no = 'checked'
    selected_symbol = '$'

    if request.method == 'POST':
        number_val = sanitize_html(request.form.get('number', '1234.5678'))
        decimals_val = sanitize_html(request.form.get('decimals', '2'))
        selected_symbol = request.form.get('symbol', '$')
        if request.form.get('thousands'):
            thousands_checked = 'checked'
        if request.form.get('position', '1') == '0':
            position_leading = ''
            position_trailing = 'checked'
        if request.form.get('spacing', '0') == '1':
            spacing_yes = 'checked'
            spacing_no = ''

    # Build select options for currency symbols
    symbol_options = ''
    for sym, name in sorted(ACCOUNTING_SYMBOLS.items(), key=lambda x: x[1]):
        sel = ' selected' if sym == selected_symbol else ''
        symbol_options += '<option value="{sym}"{sel}>{name}</option>\n'.format(
            sym=sanitize_html(sym), sel=sel, name=sanitize_html(name)
        )

    html += '''
    <form action="/wizards/format/accounting" method="POST">
        <div class="form-group row" style="margin-bottom:10px">
            <label class="col-sm-3 control-label">Sample Number Value</label>
            <div class="col-sm-9">
                <input name="number" type="text" class="form-control" value="{number}">
            </div>
        </div>
        <hr/>
        <div class="form-group row" style="margin-bottom:10px">
            <label class="col-sm-3 control-label">Currency Symbol</label>
            <div class="col-sm-9">
                <select name="symbol" class="form-control">
                    {symbol_options}
                </select>
            </div>
        </div>
        <div class="form-group row" style="margin-bottom:10px">
            <label class="col-sm-3 control-label">Decimal Places</label>
            <div class="col-sm-9">
                <input name="decimals" type="number" class="form-control" min="0" max="14" value="{decimals}">
            </div>
        </div>
        <div class="form-group row" style="margin-bottom:10px">
            <label class="col-sm-3 control-label">Use Thousands Separator</label>
            <div class="col-sm-9">
                <input name="thousands" type="checkbox" {thousands}>
            </div>
        </div>
        <div class="form-group row" style="margin-bottom:10px">
            <label class="col-sm-3 control-label">Symbol Position</label>
            <div class="col-sm-9">
                <label class="radio-inline"><input name="position" type="radio" value="1" {pos_lead}> Leading</label>
                <label class="radio-inline"><input name="position" type="radio" value="0" {pos_trail}> Trailing</label>
            </div>
        </div>
        <div class="form-group row" style="margin-bottom:10px">
            <label class="col-sm-3 control-label">Symbol Spacing</label>
            <div class="col-sm-9">
                <label class="radio-inline"><input name="spacing" type="radio" value="1" {sp_yes}> Yes</label>
                <label class="radio-inline"><input name="spacing" type="radio" value="0" {sp_no}> No</label>
            </div>
        </div>
        <div class="form-group">
            <div class="col-sm-9 col-sm-offset-3">
                <input class="btn btn-primary" name="submit" type="submit" value="Display Mask">
            </div>
        </div>
    </form>
    '''.format(
        number=number_val, decimals=decimals_val,
        symbol_options=symbol_options,
        thousands=thousands_checked,
        pos_lead=position_leading, pos_trail=position_trailing,
        sp_yes=spacing_yes, sp_no=spacing_no
    )

    if request.method == 'POST' and request.form.get('submit'):
        raw_number = request.form.get('number', '')
        raw_decimals = request.form.get('decimals', '2')
        raw_symbol = request.form.get('symbol', '$')
        has_thousands = bool(request.form.get('thousands'))
        pos = 'leading' if request.form.get('position', '1') == '1' else 'trailing'
        spacing = request.form.get('spacing', '0') == '1'

        log_entries = []
        try:
            if not raw_number.replace('.', '', 1).replace('-', '', 1).isdigit():
                log_entries.append('The Sample Number Value must be numeric')
            elif not raw_decimals.isdigit() or int(raw_decimals) < 0:
                log_entries.append('The Decimal Places value must be a positive integer')
            else:
                mask = build_mask(raw_decimals, thousands=has_thousands, symbol=raw_symbol, position=pos, spacing=spacing)
                example = format_number(raw_number, raw_decimals, thousands=has_thousands)
                if pos == 'leading':
                    example = raw_symbol + (' ' if spacing else '') + example
                else:
                    example = example + (' ' if spacing else '') + raw_symbol

                log_entries.append('<hr/><b>Code:</b><br/>')
                log_entries.append('from datasheet.format import AccountingFormatter')
                log_entries.append(
                    "mask = AccountingFormatter('{symbol}', {decimals}, {thousands}, "
                    "AccountingFormatter.{position}, AccountingFormatter.{spacing})<br/>".format(
                        symbol=raw_symbol,
                        decimals=sanitize_html(raw_decimals),
                        thousands='WITH_THOUSANDS' if has_thousands else 'WITHOUT_THOUSANDS',
                        position='LEADING_SYMBOL' if pos == 'leading' else 'TRAILING_SYMBOL',
                        spacing='WITH_SPACING' if spacing else 'WITHOUT_SPACING'
                    )
                )
                log_entries.append('print(str(mask))')
                log_entries.append('<hr/><b>Mask:</b><br/>')
                log_entries.append(mask)
                log_entries.append('<br/><b>Example:</b><br/>')
                log_entries.append(example)
        except Exception as e:
            log_entries.append('Error: ' + sanitize_html(str(e)))

        log_html = render_log(log_entries)

        # Check for XSS in the rendered output
        check_page = '<html><head><meta charset="utf-8"></head><body>' + log_html + '</body></html>'
        flag_result = check_xss_post(check_page, flags[0])
        if flag_result:
            log_entries.append('<div class="alert alert-success">' + flag_result + '</div>')
            log_html = render_log(log_entries)

        html += log_html

    html += PAGE_FOOTER
    return html


@app.route('/wizards/format/percent', methods=['GET', 'POST'])
def wizard_percent():
    html = get_page_header('Percent Format')
    html += '''<h3>Percentage Format Wizard</h3>'''

    number_val = '0.7523'
    decimals_val = '2'

    if request.method == 'POST':
        number_val = sanitize_html(request.form.get('number', '0.7523'))
        decimals_val = sanitize_html(request.form.get('decimals', '2'))

    html += '''
    <form action="/wizards/format/percent" method="POST">
        <div class="form-group row" style="margin-bottom:10px">
            <label class="col-sm-3 control-label">Sample Number Value</label>
            <div class="col-sm-9">
                <input name="number" type="text" class="form-control" value="{number}">
            </div>
        </div>
        <hr/>
        <div class="form-group row" style="margin-bottom:10px">
            <label class="col-sm-3 control-label">Decimal Places</label>
            <div class="col-sm-9">
                <input name="decimals" type="number" class="form-control" min="0" max="14" value="{decimals}">
            </div>
        </div>
        <div class="form-group">
            <div class="col-sm-9 col-sm-offset-3">
                <input class="btn btn-primary" name="submit" type="submit" value="Display Mask">
            </div>
        </div>
    </form>
    '''.format(number=number_val, decimals=decimals_val)

    if request.method == 'POST' and request.form.get('submit'):
        raw_number = request.form.get('number', '')
        raw_decimals = request.form.get('decimals', '2')

        log_entries = []
        try:
            if not raw_number.replace('.', '', 1).replace('-', '', 1).isdigit():
                log_entries.append('The Sample Number Value must be numeric')
            elif not raw_decimals.isdigit() or int(raw_decimals) < 0:
                log_entries.append('The Decimal Places value must be a positive integer')
            else:
                dec_part = '0' * int(raw_decimals) if int(raw_decimals) > 0 else ''
                mask = '0' + ('.' + dec_part if dec_part else '') + '%'
                num = float(raw_number) * 100
                example = ('{:.' + raw_decimals + 'f}%').format(num)
                log_entries.append('<hr/><b>Code:</b><br/>')
                log_entries.append('from datasheet.format import PercentFormatter')
                log_entries.append(
                    'mask = PercentFormatter({decimals})<br/>'.format(
                        decimals=sanitize_html(raw_decimals)
                    )
                )
                log_entries.append('print(str(mask))')
                log_entries.append('<hr/><b>Mask:</b><br/>')
                log_entries.append(sanitize_html(mask) + '<br/>')
                log_entries.append('<br/><b>Example:</b><br/>')
                log_entries.append(sanitize_html(example))
        except Exception as e:
            log_entries.append('Error: ' + sanitize_html(str(e)))

        html += render_log(log_entries)

    html += PAGE_FOOTER
    return html


@app.route('/wizards/format/scientific', methods=['GET', 'POST'])
def wizard_scientific():
    html = get_page_header('Scientific Format')
    html += '''<h3>Scientific Notation Wizard</h3>'''

    number_val = '1234.5678'
    decimals_val = '2'

    if request.method == 'POST':
        number_val = sanitize_html(request.form.get('number', '1234.5678'))
        decimals_val = sanitize_html(request.form.get('decimals', '2'))

    html += '''
    <form action="/wizards/format/scientific" method="POST">
        <div class="form-group row" style="margin-bottom:10px">
            <label class="col-sm-3 control-label">Sample Number Value</label>
            <div class="col-sm-9">
                <input name="number" type="text" class="form-control" value="{number}">
            </div>
        </div>
        <hr/>
        <div class="form-group row" style="margin-bottom:10px">
            <label class="col-sm-3 control-label">Decimal Places</label>
            <div class="col-sm-9">
                <input name="decimals" type="number" class="form-control" min="0" max="14" value="{decimals}">
            </div>
        </div>
        <div class="form-group">
            <div class="col-sm-9 col-sm-offset-3">
                <input class="btn btn-primary" name="submit" type="submit" value="Display Mask">
            </div>
        </div>
    </form>
    '''.format(number=number_val, decimals=decimals_val)

    if request.method == 'POST' and request.form.get('submit'):
        raw_number = request.form.get('number', '')
        raw_decimals = request.form.get('decimals', '2')

        log_entries = []
        try:
            if not raw_number.replace('.', '', 1).replace('-', '', 1).isdigit():
                log_entries.append('The Sample Number Value must be numeric')
            elif not raw_decimals.isdigit() or int(raw_decimals) < 0:
                log_entries.append('The Decimal Places value must be a positive integer')
            else:
                dec_part = '0' * int(raw_decimals) if int(raw_decimals) > 0 else ''
                mask = '0' + ('.' + dec_part if dec_part else '') + 'E+0'
                num = float(raw_number)
                example = ('{:.' + raw_decimals + 'E}').format(num)
                log_entries.append('<hr/><b>Code:</b><br/>')
                log_entries.append('from datasheet.format import ScientificFormatter')
                log_entries.append(
                    'mask = ScientificFormatter({decimals})<br/>'.format(
                        decimals=sanitize_html(raw_decimals)
                    )
                )
                log_entries.append('print(str(mask))')
                log_entries.append('<hr/><b>Mask:</b><br/>')
                log_entries.append(sanitize_html(mask) + '<br/>')
                log_entries.append('<br/><b>Example:</b><br/>')
                log_entries.append(sanitize_html(example))
        except Exception as e:
            log_entries.append('Error: ' + sanitize_html(str(e)))

        html += render_log(log_entries)

    html += PAGE_FOOTER
    return html


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
