# encoding=utf8

from flask import Flask, request, Response, make_response
import subprocess
import os
import re
import cgi
import sys

from phantomjs import Phantom

import logging

logging.basicConfig(level=logging.WARNING)

reload(sys)
sys.setdefaultencoding('utf8')

flag_data = open('secret.txt').read().strip()

app = Flask(__name__)

phantom = Phantom()

SYMBOLS = {
    '$': 'US Dollars ($)',
    u'\u20ac': 'Euro (\u20ac)',
    u'\u00a5': 'Japanese Yen (\u00a5)',
    u'\u00a3': 'Pound Sterling (\u00a3)',
    u'\u20b9': 'Rupee (\u20b9)',
    u'\u20bd': 'Rouble (\u20bd)',
}

ALLOWED_SYMBOLS = SYMBOLS.keys()


def escape_html(s):
    """Escape HTML entities in user input."""
    return cgi.escape(s, quote=True)


def build_format_mask(symbol, decimals, thousands, position, spacing):
    """Build a number format mask string similar to spreadsheet format codes."""
    dec_part = '0.' + '0' * decimals if decimals > 0 else '0'
    if thousands:
        int_part = '#,##0'
    else:
        int_part = '0'
    num_part = int_part + ('.' + '0' * decimals if decimals > 0 else '')

    space = ' ' if spacing else ''

    if position:
        mask = symbol + space + num_part
    else:
        mask = num_part + space + symbol

    return mask


def format_number(value, mask, symbol, decimals, thousands, position, spacing):
    """Format a number according to the mask pattern."""
    try:
        num = float(value)
    except (ValueError, TypeError):
        return 'N/A'

    if thousands:
        formatted = '{:,.{prec}f}'.format(num, prec=decimals)
    else:
        formatted = '{:.{prec}f}'.format(num, prec=decimals)

    space = ' ' if spacing else ''

    if position:
        return symbol + space + formatted
    else:
        return formatted + space + symbol


LAYOUT_HEAD = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="stylesheet" href="/static/css/bootstrap.min.css">
    <style>
        body {{ padding-top: 70px; }}
        .navbar-brand {{ font-weight: bold; }}
        .result-section {{ margin-top: 20px; padding: 15px; background-color: #f5f5f5; border-radius: 4px; }}
        .result-section b {{ color: #333; }}
        .log-entry {{ margin-bottom: 5px; }}
    </style>
</head>
<body>
    <div class="container">
        <nav class="navbar navbar-default navbar-fixed-top" role="navigation">
            <div class="container-fluid">
                <div class="navbar-header">
                    <a class="navbar-brand" href="/">SpreadsheetForge</a>
                </div>
                <div class="navbar-collapse collapse">
                    <ul class="nav navbar-nav">
                        <li class="dropdown">
                            <a href="#" class="dropdown-toggle" data-toggle="dropdown">Format Wizards <strong class="caret"></strong></a>
                            <ul class="dropdown-menu">
                                <li><a href="/tools/format/numeric">Numeric</a></li>
                                <li><a href="/tools/format/percent">Percentage</a></li>
                                <li><a href="/tools/format/ledger">Ledger</a></li>
                                <li><a href="/tools/format/scientific">Scientific</a></li>
                            </ul>
                        </li>
                    </ul>
                </div>
            </div>
        </nav>
"""

LAYOUT_FOOT = """
    </div>
</body>
</html>"""


@app.route('/')
def index():
    content = LAYOUT_HEAD.format(title='SpreadsheetForge')
    content += """
        <div class="jumbotron">
            <h1>SpreadsheetForge</h1>
            <p>A library providing tools for spreadsheet number formatting. Use the Format Wizards to generate format masks for your spreadsheet data.</p>
        </div>
        <h3>Available Wizards</h3>
        <ul>
            <li><a href="/tools/format/numeric">Numeric Format</a> - Basic number formatting with decimal and thousands separator options</li>
            <li><a href="/tools/format/percent">Percentage Format</a> - Format numbers as percentages</li>
            <li><a href="/tools/format/ledger">Ledger Format</a> - Accounting/financial number formatting with currency symbols</li>
            <li><a href="/tools/format/scientific">Scientific Format</a> - Scientific notation formatting</li>
        </ul>
    """
    content += LAYOUT_FOOT
    return content


@app.route('/tools/format/numeric', methods=['GET', 'POST'])
def format_numeric():
    page_title = 'Numeric Format Wizard'
    content = LAYOUT_HEAD.format(title=page_title)
    content += '<h1>Numeric Format</h1>'

    number_val = '1234.5678'
    decimals_val = '2'
    thousands_checked = ''

    if request.method == 'POST':
        number_val = escape_html(request.form.get('number', '1234.5678'))
        decimals_val = escape_html(request.form.get('decimals', '2'))
        if request.form.get('thousands'):
            thousands_checked = 'checked'

    content += """
    <form action="/tools/format/numeric" method="POST">
        <div class="form-group row">
            <label class="col-sm-2 control-label">Sample Number Value</label>
            <div class="col-sm-10">
                <input name="number" type="text" size="8" value="{number}">
            </div>
        </div>
        <hr />
        <div class="form-group row">
            <label class="col-sm-2 control-label">Decimal Places</label>
            <div class="col-sm-10">
                <input name="decimals" type="number" size="2" min="0" max="14" value="{decimals}">
            </div>
        </div>
        <div class="form-group row">
            <label class="col-sm-2 control-label">Use Thousands Separator</label>
            <div class="col-sm-10">
                <input name="thousands" type="checkbox" {thousands}>
            </div>
        </div>
        <div class="form-group row">
            <div class="col-sm-10">
                <input class="btn btn-primary" name="submit" type="submit" value="Display Mask">
            </div>
        </div>
    </form>
    """.format(number=number_val, decimals=decimals_val, thousands=thousands_checked)

    if request.method == 'POST' and request.form.get('submit'):
        num_str = request.form.get('number', '')
        dec_str = request.form.get('decimals', '2')

        try:
            num = float(num_str)
        except (ValueError, TypeError):
            content += '<div class="result-section"><span class="log-entry">The Sample Number Value must be numeric</span></div>'
            content += LAYOUT_FOOT
            return content

        try:
            dec = int(dec_str)
            if dec < 0:
                raise ValueError
        except (ValueError, TypeError):
            content += '<div class="result-section"><span class="log-entry">The Decimal Places value must be positive integer</span></div>'
            content += LAYOUT_FOOT
            return content

        use_thousands = bool(request.form.get('thousands'))
        mask = build_format_mask('', dec, use_thousands, False, False).strip()
        if use_thousands:
            example = '{:,.{prec}f}'.format(num, prec=dec)
        else:
            example = '{:.{prec}f}'.format(num, prec=dec)

        content += '<div class="result-section">'
        content += '<b>Code:</b><br />'
        content += '<span class="log-entry">FormatWizard.Numeric({dec}, {th})</span><br />'.format(
            dec=escape_html(dec_str),
            th='WITH_THOUSANDS_SEPARATOR' if use_thousands else 'WITHOUT_THOUSANDS_SEPARATOR'
        )
        content += '<hr /><b>Mask:</b><br />'
        content += '<span class="log-entry">{}</span><br />'.format(escape_html(mask))
        content += '<br /><b>Example:</b><br />'
        content += '<span class="log-entry">{}</span>'.format(escape_html(example))
        content += '</div>'

    content += LAYOUT_FOOT
    return content


@app.route('/tools/format/percent', methods=['GET', 'POST'])
def format_percent():
    page_title = 'Percentage Format Wizard'
    content = LAYOUT_HEAD.format(title=page_title)
    content += '<h1>Percentage Format</h1>'

    number_val = '0.7523'
    decimals_val = '2'

    if request.method == 'POST':
        number_val = escape_html(request.form.get('number', '0.7523'))
        decimals_val = escape_html(request.form.get('decimals', '2'))

    content += """
    <form action="/tools/format/percent" method="POST">
        <div class="form-group row">
            <label class="col-sm-2 control-label">Sample Number Value</label>
            <div class="col-sm-10">
                <input name="number" type="text" size="8" value="{number}">
            </div>
        </div>
        <hr />
        <div class="form-group row">
            <label class="col-sm-2 control-label">Decimal Places</label>
            <div class="col-sm-10">
                <input name="decimals" type="number" size="2" min="0" max="14" value="{decimals}">
            </div>
        </div>
        <div class="form-group row">
            <div class="col-sm-10">
                <input class="btn btn-primary" name="submit" type="submit" value="Display Mask">
            </div>
        </div>
    </form>
    """.format(number=number_val, decimals=decimals_val)

    if request.method == 'POST' and request.form.get('submit'):
        num_str = request.form.get('number', '')
        dec_str = request.form.get('decimals', '2')

        try:
            num = float(num_str)
        except (ValueError, TypeError):
            content += '<div class="result-section"><span class="log-entry">The Sample Number Value must be numeric</span></div>'
            content += LAYOUT_FOOT
            return content

        try:
            dec = int(dec_str)
            if dec < 0:
                raise ValueError
        except (ValueError, TypeError):
            content += '<div class="result-section"><span class="log-entry">The Decimal Places value must be positive integer</span></div>'
            content += LAYOUT_FOOT
            return content

        mask = '0.' + '0' * dec + '%' if dec > 0 else '0%'
        example = '{:.{prec}f}%'.format(num * 100, prec=dec)

        content += '<div class="result-section">'
        content += '<b>Code:</b><br />'
        content += '<span class="log-entry">FormatWizard.Percentage({})</span><br />'.format(escape_html(dec_str))
        content += '<hr /><b>Mask:</b><br />'
        content += '<span class="log-entry">{}</span><br />'.format(escape_html(mask))
        content += '<br /><b>Example:</b><br />'
        content += '<span class="log-entry">{}</span>'.format(escape_html(example))
        content += '</div>'

    content += LAYOUT_FOOT
    return content


@app.route('/tools/format/scientific', methods=['GET', 'POST'])
def format_scientific():
    page_title = 'Scientific Format Wizard'
    content = LAYOUT_HEAD.format(title=page_title)
    content += '<h1>Scientific Format</h1>'

    number_val = '1234.5678'
    decimals_val = '2'

    if request.method == 'POST':
        number_val = escape_html(request.form.get('number', '1234.5678'))
        decimals_val = escape_html(request.form.get('decimals', '2'))

    content += """
    <form action="/tools/format/scientific" method="POST">
        <div class="form-group row">
            <label class="col-sm-2 control-label">Sample Number Value</label>
            <div class="col-sm-10">
                <input name="number" type="text" size="8" value="{number}">
            </div>
        </div>
        <hr />
        <div class="form-group row">
            <label class="col-sm-2 control-label">Decimal Places</label>
            <div class="col-sm-10">
                <input name="decimals" type="number" size="2" min="0" max="14" value="{decimals}">
            </div>
        </div>
        <div class="form-group row">
            <div class="col-sm-10">
                <input class="btn btn-primary" name="submit" type="submit" value="Display Mask">
            </div>
        </div>
    </form>
    """.format(number=number_val, decimals=decimals_val)

    if request.method == 'POST' and request.form.get('submit'):
        num_str = request.form.get('number', '')
        dec_str = request.form.get('decimals', '2')

        try:
            num = float(num_str)
        except (ValueError, TypeError):
            content += '<div class="result-section"><span class="log-entry">The Sample Number Value must be numeric</span></div>'
            content += LAYOUT_FOOT
            return content

        try:
            dec = int(dec_str)
            if dec < 0:
                raise ValueError
        except (ValueError, TypeError):
            content += '<div class="result-section"><span class="log-entry">The Decimal Places value must be positive integer</span></div>'
            content += LAYOUT_FOOT
            return content

        mask = '0.' + '0' * dec + 'E+00' if dec > 0 else '0E+00'
        example = ('{:.{prec}E}'.format(num, prec=dec))

        content += '<div class="result-section">'
        content += '<b>Code:</b><br />'
        content += '<span class="log-entry">FormatWizard.Scientific({})</span><br />'.format(escape_html(dec_str))
        content += '<hr /><b>Mask:</b><br />'
        content += '<span class="log-entry">{}</span><br />'.format(escape_html(mask))
        content += '<br /><b>Example:</b><br />'
        content += '<span class="log-entry">{}</span>'.format(escape_html(example))
        content += '</div>'

    content += LAYOUT_FOOT
    return content


def verify_xss(html_page):
    """Verify XSS execution using headless browser."""
    proc = subprocess.Popen(
        ["timeout", "5", "phantomjs", "check.js"],
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE
    )
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://' + os.environ.get('APP_HOST', 'localhost') + ':' + os.environ.get('APP_PORT', '5000') + '/' + fn
    try:
        of = open(fn, 'w')
        of.write(html_page)
        of.close()
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
    except Exception:
        result = ''
    finally:
        try:
            os.unlink(fn)
        except OSError:
            pass

    return result


@app.route('/tools/format/ledger', methods=['GET', 'POST'])
def format_ledger():
    page_title = 'Ledger Format Wizard'
    content = LAYOUT_HEAD.format(title=page_title)
    content += '<h1>Ledger Format</h1>'

    number_val = '1234.5678'
    decimals_val = '2'
    symbol_val = '$'
    position_val = '1'
    spacing_val = '0'
    thousands_checked = ''

    if request.method == 'POST':
        number_val = escape_html(request.form.get('number', '1234.5678'))
        decimals_val = escape_html(request.form.get('decimals', '2'))
        symbol_val = request.form.get('symbol', '$')
        position_val = request.form.get('position', '1')
        spacing_val = request.form.get('spacing', '0')
        if request.form.get('thousands'):
            thousands_checked = 'checked'

    symbol_options = ''
    for sym, name in SYMBOLS.items():
        selected = 'selected' if symbol_val == sym else ''
        symbol_options += '<option value="{}" {}>{}</option>\n'.format(
            escape_html(sym), selected, escape_html(name)
        )

    content += """
    <form action="/tools/format/ledger" method="POST">
        <div class="form-group row">
            <label class="col-sm-2 control-label">Sample Number Value</label>
            <div class="col-sm-10">
                <input name="number" type="text" size="8" value="{number}">
            </div>
        </div>
        <hr />
        <div class="form-group row">
            <label class="col-sm-2 control-label">Symbol</label>
            <div class="col-sm-10">
                <select name="symbol" class="form-control">
                    {symbol_options}
                </select>
            </div>
        </div>
        <div class="form-group row">
            <label class="col-sm-2 control-label">Decimal Places</label>
            <div class="col-sm-10">
                <input name="decimals" type="number" size="2" min="0" max="14" value="{decimals}">
            </div>
        </div>
        <div class="form-group row">
            <label class="col-sm-2 control-label">Use Thousands Separator</label>
            <div class="col-sm-10">
                <input name="thousands" type="checkbox" {thousands}>
            </div>
        </div>
        <div class="form-group row">
            <label class="col-sm-2 control-label">Symbol Position</label>
            <div class="col-sm-10">
                <input name="position" type="radio" value="1" {pos_leading}> Leading
                <input name="position" type="radio" value="0" {pos_trailing}> Trailing
            </div>
        </div>
        <div class="form-group row">
            <label class="col-sm-2 control-label">Symbol Spacing</label>
            <div class="col-sm-10">
                <input name="spacing" type="radio" value="1" {sp_yes}> Yes
                <input name="spacing" type="radio" value="0" {sp_no}> No
            </div>
        </div>
        <div class="form-group row">
            <div class="col-sm-10">
                <input class="btn btn-primary" name="submit" type="submit" value="Display Mask">
            </div>
        </div>
    </form>
    """.format(
        number=number_val,
        symbol_options=symbol_options,
        decimals=decimals_val,
        thousands=thousands_checked,
        pos_leading='checked' if position_val == '1' else '',
        pos_trailing='checked' if position_val == '0' else '',
        sp_yes='checked' if spacing_val == '1' else '',
        sp_no='checked' if spacing_val != '1' else ''
    )

    if request.method == 'POST' and request.form.get('submit'):
        num_str = request.form.get('number', '')
        dec_str = request.form.get('decimals', '2')
        sym = request.form.get('symbol', '$')
        pos = request.form.get('position', '1')
        sp = request.form.get('spacing', '0')

        try:
            num = float(num_str)
        except (ValueError, TypeError):
            content += '<div class="result-section"><span class="log-entry">The Sample Number Value must be numeric</span></div>'
            content += LAYOUT_FOOT
            return content

        try:
            dec = int(dec_str)
            if dec < 0:
                raise ValueError
        except (ValueError, TypeError):
            content += '<div class="result-section"><span class="log-entry">The Decimal Places value must be positive integer</span></div>'
            content += LAYOUT_FOOT
            return content

        try:
            is_leading = bool(int(pos))
        except (ValueError, TypeError):
            is_leading = True
        try:
            use_spacing = bool(int(sp))
        except (ValueError, TypeError):
            use_spacing = False
        use_thousands = bool(request.form.get('thousands'))

        mask = build_format_mask(sym, dec, use_thousands, is_leading, use_spacing)
        example = format_number(num, mask, sym, dec, use_thousands, is_leading, use_spacing)

        log_output = '<div class="result-section">'
        log_output += '<b>Code:</b><br />'
        log_output += "<span class=\"log-entry\">FormatWizard.Ledger('{sym}', {dec}, {th}, {pos}, {sp})</span><br />".format(
            sym=sym,
            dec=escape_html(dec_str),
            th='WITH_THOUSANDS_SEPARATOR' if use_thousands else 'WITHOUT_THOUSANDS_SEPARATOR',
            pos='LEADING_SYMBOL' if is_leading else 'TRAILING_SYMBOL',
            sp='SYMBOL_WITH_SPACING' if use_spacing else 'SYMBOL_WITHOUT_SPACING'
        )
        log_output += '<hr /><b>Mask:</b><br />'
        log_output += '<span class="log-entry">{}</span><br />'.format(mask)
        log_output += '<br /><b>Example:</b><br />'
        log_output += '<span class="log-entry">{}</span>'.format(example)
        log_output += '</div>'

        content += log_output

        full_page = content + LAYOUT_FOOT
        xss_result = verify_xss(full_page)

        if xss_result == 'XSS':
            content += '<div class="result-section"><b>Format validation token:</b> {}</div>'.format(flag_data)

    content += LAYOUT_FOOT
    return content


@app.errorhandler(404)
def page_not_found(e):
    return LAYOUT_HEAD.format(title='Not Found') + '<h1>404 - Page Not Found</h1><p>The requested resource could not be found.</p>' + LAYOUT_FOOT, 404


@app.errorhandler(500)
def internal_error(e):
    return LAYOUT_HEAD.format(title='Error') + '<h1>500 - Internal Server Error</h1><p>An unexpected error occurred.</p>' + LAYOUT_FOOT, 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
