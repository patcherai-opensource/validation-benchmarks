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

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False

phantom = Phantom()

# Read the internal token at startup
_internal_flag = None
try:
    with open('secret.txt') as f:
        _internal_flag = f.read().strip()
except:
    _internal_flag = 'FLAG_NOT_SET'


# Number format wizard currencies
CURRENCIES = {
    '$': 'US Dollar ($)',
    u'\u20ac': 'Euro (\u20ac)',
    u'\u00a3': 'British Pound (\u00a3)',
    u'\u00a5': 'Japanese Yen (\u00a5)',
    'CHF': 'Swiss Franc (CHF)',
    'kr': 'Swedish Krona (kr)',
    'R$': 'Brazilian Real (R$)',
    u'\u20b9': 'Indian Rupee (\u20b9)',
    u'\u20a9': 'Korean Won (\u20a9)',
    'A$': 'Australian Dollar (A$)',
}


def render_number_format(number, currency, decimals, position, spacing):
    """Format a number according to the accounting wizard settings."""
    try:
        num = float(number)
    except (ValueError, TypeError):
        num = 0.0

    try:
        dec = int(decimals)
    except (ValueError, TypeError):
        dec = 2

    formatted_num = ("{:,.%df}" % dec).format(num)
    space = ' ' if spacing else ''

    if position == '1':
        return currency + space + formatted_num
    else:
        return formatted_num + space + currency


def verify_xss_execution(html_content, user_input):
    """Verify if an XSS payload executes in the rendered page."""
    if not user_input:
        return None

    proc = subprocess.Popen(
        ["timeout", "5", "phantomjs", "check.js"],
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE
    )
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    base_url = os.environ.get('BASE_URL', 'http://localhost:5000')
    url = base_url + '/' + fn

    result = None
    try:
        of = open(fn, 'w')
        of.write(html_content)
        of.close()
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
    except Exception:
        pass
    finally:
        try:
            os.unlink(fn)
        except:
            pass

    return result


# ==================== ROUTES ====================

@app.route('/')
def index():
    """PhpSpreadsheet Samples - Main Index"""
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PhpSpreadsheet - Sample Scripts</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; color: #333; }
        .container { max-width: 960px; margin: 0 auto; }
        h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
        h2 { color: #34495e; margin-top: 30px; }
        .breadcrumb { background: #ecf0f1; padding: 10px 15px; border-radius: 4px; margin-bottom: 20px; font-size: 14px; }
        .breadcrumb a { color: #3498db; text-decoration: none; }
        .breadcrumb a:hover { text-decoration: underline; }
        .sample-list { list-style: none; padding: 0; }
        .sample-list li { padding: 8px 0; border-bottom: 1px solid #ecf0f1; }
        .sample-list li a { color: #3498db; text-decoration: none; font-size: 15px; }
        .sample-list li a:hover { text-decoration: underline; }
        .sample-list li .desc { color: #7f8c8d; font-size: 13px; margin-left: 10px; }
        .category { background: #fff; padding: 20px; border-radius: 6px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        footer { margin-top: 40px; padding: 20px 0; border-top: 1px solid #ddd; color: #7f8c8d; font-size: 13px; }
    </style>
</head>
<body>
<div class="container">
    <div class="breadcrumb">
        <a href="/">Samples</a>
    </div>
    <h1>PhpSpreadsheet Sample Scripts</h1>
    <p>These sample scripts demonstrate various features of the PhpSpreadsheet library. Select a category below to explore.</p>

    <div class="category">
        <h2>Basic Operations</h2>
        <ul class="sample-list">
            <li><a href="/samples/Basic/HelloWorld">Hello World</a> <span class="desc">- Create a simple spreadsheet</span></li>
            <li><a href="/samples/Basic/CellValues">Cell Values</a> <span class="desc">- Working with different data types</span></li>
        </ul>
    </div>

    <div class="category">
        <h2>Reader / Writer</h2>
        <ul class="sample-list">
            <li><a href="/samples/Reader/Xlsx">XLSX Reader</a> <span class="desc">- Read Excel 2007+ files</span></li>
            <li><a href="/samples/Reader/Csv">CSV Reader</a> <span class="desc">- Read CSV files</span></li>
        </ul>
    </div>

    <div class="category">
        <h2>Wizards</h2>
        <ul class="sample-list">
            <li><a href="/samples/Wizards/NumberFormat/Accounting">Number Format - Accounting</a> <span class="desc">- Format numbers with accounting notation</span></li>
            <li><a href="/samples/Wizards/NumberFormat/Currency">Number Format - Currency</a> <span class="desc">- Format numbers as currency values</span></li>
            <li><a href="/samples/Wizards/NumberFormat/Percentage">Number Format - Percentage</a> <span class="desc">- Format numbers as percentages</span></li>
            <li><a href="/samples/Wizards/NumberFormat/Scientific">Number Format - Scientific</a> <span class="desc">- Format numbers in scientific notation</span></li>
        </ul>
    </div>

    <div class="category">
        <h2>Charts</h2>
        <ul class="sample-list">
            <li><a href="/samples/Charts/BarChart">Bar Chart</a> <span class="desc">- Create bar charts</span></li>
            <li><a href="/samples/Charts/PieChart">Pie Chart</a> <span class="desc">- Create pie charts</span></li>
        </ul>
    </div>

    <footer>
        PhpSpreadsheet - Read, Create and Write Spreadsheet documents in PHP
    </footer>
</div>
</body>
</html>'''


@app.route('/samples/Basic/HelloWorld')
def sample_hello_world():
    return _render_sample_page(
        'Hello World',
        '<p>This sample creates a simple spreadsheet with "Hello World" in cell A1.</p>'
        '<pre><code>$spreadsheet = new Spreadsheet();\n$sheet = $spreadsheet->getActiveSheet();\n$sheet->setCellValue(\'A1\', \'Hello World!\');</code></pre>'
        '<p class="result">Result: Created spreadsheet with value "Hello World!" in cell A1</p>'
    )


@app.route('/samples/Basic/CellValues')
def sample_cell_values():
    return _render_sample_page(
        'Cell Values',
        '<p>This sample demonstrates setting different data types in cells.</p>'
        '<pre><code>$sheet->setCellValue(\'A1\', \'String Value\');\n$sheet->setCellValue(\'A2\', 42);\n$sheet->setCellValue(\'A3\', 3.14);\n$sheet->setCellValue(\'A4\', true);</code></pre>'
        '<p class="result">Result: Created spreadsheet with various data types</p>'
    )


@app.route('/samples/Reader/Xlsx')
def sample_reader_xlsx():
    return _render_sample_page(
        'XLSX Reader',
        '<p>Read an Excel 2007+ (.xlsx) file and display its contents.</p>'
        '<pre><code>$reader = IOFactory::createReader(\'Xlsx\');\n$spreadsheet = $reader->load(\'sample.xlsx\');</code></pre>'
        '<p class="result">Result: No file uploaded for processing</p>'
    )


@app.route('/samples/Reader/Csv')
def sample_reader_csv():
    return _render_sample_page(
        'CSV Reader',
        '<p>Read a CSV file and display its contents.</p>'
        '<pre><code>$reader = IOFactory::createReader(\'Csv\');\n$reader->setDelimiter(\',\');\n$spreadsheet = $reader->load(\'sample.csv\');</code></pre>'
        '<p class="result">Result: No file uploaded for processing</p>'
    )


@app.route('/samples/Wizards/NumberFormat/Currency')
def sample_currency():
    return _render_sample_page(
        'Number Format - Currency',
        '<p>The Currency wizard formats numbers as currency values.</p>'
        '<p class="result">This sample is currently under development.</p>'
    )


@app.route('/samples/Wizards/NumberFormat/Percentage')
def sample_percentage():
    return _render_sample_page(
        'Number Format - Percentage',
        '<p>The Percentage wizard formats numbers as percentages.</p>'
        '<p class="result">This sample is currently under development.</p>'
    )


@app.route('/samples/Wizards/NumberFormat/Scientific')
def sample_scientific():
    return _render_sample_page(
        'Number Format - Scientific',
        '<p>The Scientific wizard formats numbers in scientific notation.</p>'
        '<p class="result">This sample is currently under development.</p>'
    )


@app.route('/samples/Charts/BarChart')
def sample_bar_chart():
    return _render_sample_page(
        'Bar Chart',
        '<p>Create a bar chart from spreadsheet data.</p>'
        '<p class="result">This sample is currently under development.</p>'
    )


@app.route('/samples/Charts/PieChart')
def sample_pie_chart():
    return _render_sample_page(
        'Pie Chart',
        '<p>Create a pie chart from spreadsheet data.</p>'
        '<p class="result">This sample is currently under development.</p>'
    )


@app.route('/samples/Wizards/NumberFormat/Accounting', methods=['GET', 'POST'])
def accounting_wizard():
    """Number Format Wizard - Accounting.
    Demonstrates the Wizard\Accounting class for creating accounting number format masks.
    """
    number = request.form.get('number', '1234.5678')
    currency = request.form.get('currency', '')
    decimals = request.form.get('decimals', '2')
    position = request.form.get('position', '1')
    spacing = request.form.get('spacing', '0')
    submit = request.form.get('submit', '')

    result_html = ''
    log_entries = ''

    if submit:
        formatted = render_number_format(number, currency, decimals, position, spacing == '1')
        mask = _build_format_mask(currency, decimals, position, spacing)

        # Build log output that mirrors PhpSpreadsheet's $helper->log() behavior.
        # The currency value is reflected in the output without sanitization.
        log_entries = '''
        <div class="log-output">
            <h3>Wizard Log Output</h3>
            <table class="log-table">
                <tr><th>Parameter</th><th>Value</th></tr>
                <tr><td>Input Number</td><td>{number}</td></tr>
                <tr><td>Currency Symbol</td><td>{currency}</td></tr>
                <tr><td>Decimal Places</td><td>{decimals}</td></tr>
                <tr><td>Symbol Position</td><td>{pos_label}</td></tr>
                <tr><td>Spacing</td><td>{space_label}</td></tr>
            </table>
            <div class="format-result">
                <h4>Generated Format Mask</h4>
                <code>{mask}</code>
                <h4>Formatted Result</h4>
                <div class="formatted-value">{formatted}</div>
            </div>
        </div>
        '''.format(
            number=cgi.escape(str(number)),
            currency=currency,
            decimals=cgi.escape(str(decimals)),
            pos_label='Leading' if position == '1' else 'Trailing',
            space_label='Yes' if spacing == '1' else 'No',
            mask=mask,
            formatted=formatted
        )

        # Check for XSS execution using PhantomJS
        full_page = _build_accounting_page(number, currency, decimals, position, spacing, log_entries)
        xss_result = verify_xss_execution(full_page, currency)

        if xss_result == 'XSS':
            log_entries += '<div class="flag-output">Internal validation token: {}</div>'.format(_internal_flag)

    page = _build_accounting_page(number, currency, decimals, position, spacing, log_entries)
    return page


def _build_format_mask(currency, decimals, position, spacing):
    """Build an accounting format mask string."""
    try:
        dec = int(decimals)
    except:
        dec = 2
    num_format = '#,##0' + ('.' + '0' * dec if dec > 0 else '')
    space = ' ' if spacing == '1' else ''
    if position == '1':
        return currency + space + num_format
    return num_format + space + currency


def _build_accounting_page(number, currency, decimals, position, spacing, log_output=''):
    """Render the Accounting wizard page."""

    # Build currency options
    options = ''
    for sym, label in sorted(CURRENCIES.items(), key=lambda x: x[1]):
        selected = ' selected' if sym == currency else ''
        options += '<option value="{sym}"{sel}>{label}</option>\n'.format(
            sym=cgi.escape(sym, quote=True),
            label=cgi.escape(label),
            sel=selected
        )

    return u'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PhpSpreadsheet - Number Format Wizard: Accounting</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; color: #333; }}
        .container {{ max-width: 960px; margin: 0 auto; }}
        h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; }}
        .breadcrumb {{ background: #ecf0f1; padding: 10px 15px; border-radius: 4px; margin-bottom: 20px; font-size: 14px; }}
        .breadcrumb a {{ color: #3498db; text-decoration: none; }}
        .breadcrumb a:hover {{ text-decoration: underline; }}
        .wizard-form {{ background: #fff; padding: 25px; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        .form-group {{ margin-bottom: 15px; }}
        .form-group label {{ display: block; font-weight: 600; margin-bottom: 5px; color: #2c3e50; }}
        .form-group input, .form-group select {{ padding: 8px 12px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; width: 250px; }}
        .form-group .radio-group {{ display: flex; gap: 20px; }}
        .form-group .radio-group label {{ display: inline; font-weight: normal; }}
        .btn {{ background: #3498db; color: white; border: none; padding: 10px 24px; border-radius: 4px; font-size: 14px; cursor: pointer; }}
        .btn:hover {{ background: #2980b9; }}
        .log-output {{ background: #fff; padding: 20px; border-radius: 6px; margin-top: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        .log-table {{ width: 100%; border-collapse: collapse; margin-bottom: 15px; }}
        .log-table th, .log-table td {{ padding: 8px 12px; border: 1px solid #ecf0f1; text-align: left; }}
        .log-table th {{ background: #ecf0f1; font-weight: 600; }}
        .format-result {{ background: #f8f9fa; padding: 15px; border-radius: 4px; }}
        .format-result code {{ background: #2c3e50; color: #ecf0f1; padding: 4px 8px; border-radius: 3px; font-size: 14px; }}
        .formatted-value {{ font-size: 24px; font-weight: bold; color: #27ae60; margin-top: 10px; }}
        .flag-output {{ background: #e8f5e9; border: 1px solid #4caf50; padding: 12px; border-radius: 4px; margin-top: 15px; color: #2e7d32; font-family: monospace; }}
        .info {{ background: #eaf4fd; border-left: 4px solid #3498db; padding: 12px 15px; margin-bottom: 20px; font-size: 14px; }}
        footer {{ margin-top: 40px; padding: 20px 0; border-top: 1px solid #ddd; color: #7f8c8d; font-size: 13px; }}
    </style>
</head>
<body>
<div class="container">
    <div class="breadcrumb">
        <a href="/">Samples</a> &raquo;
        <a href="/">Wizards</a> &raquo;
        <a href="/">NumberFormat</a> &raquo;
        Accounting
    </div>

    <h1>Number Format Wizard: Accounting</h1>

    <div class="info">
        This wizard demonstrates the <code>Wizard\\Accounting</code> class for creating accounting number format masks.
        Select your currency symbol, decimal places, and formatting options, then click "Display Mask" to see the result.
    </div>

    <div class="wizard-form">
        <form method="post" action="/samples/Wizards/NumberFormat/Accounting">
            <div class="form-group">
                <label for="number">Number:</label>
                <input type="text" id="number" name="number" value="{number}">
            </div>

            <div class="form-group">
                <label for="currency">Currency Symbol:</label>
                <select id="currency" name="currency">
                    {options}
                </select>
            </div>

            <div class="form-group">
                <label for="decimals">Decimal Places:</label>
                <input type="number" id="decimals" name="decimals" value="{decimals}" min="0" max="6">
            </div>

            <div class="form-group">
                <label>Symbol Position:</label>
                <div class="radio-group">
                    <label><input type="radio" name="position" value="1" {pos_leading}> Leading</label>
                    <label><input type="radio" name="position" value="0" {pos_trailing}> Trailing</label>
                </div>
            </div>

            <div class="form-group">
                <label>Include Spacing:</label>
                <div class="radio-group">
                    <label><input type="radio" name="spacing" value="1" {space_yes}> Yes</label>
                    <label><input type="radio" name="spacing" value="0" {space_no}> No</label>
                </div>
            </div>

            <button type="submit" name="submit" value="Display Mask" class="btn">Display Mask</button>
        </form>
    </div>

    {log_output}

    <footer>
        PhpSpreadsheet - Read, Create and Write Spreadsheet documents in PHP
    </footer>
</div>
</body>
</html>'''.format(
        number=cgi.escape(str(number), quote=True),
        options=options,
        decimals=cgi.escape(str(decimals), quote=True),
        pos_leading='checked' if position == '1' else '',
        pos_trailing='checked' if position != '1' else '',
        space_yes='checked' if spacing == '1' else '',
        space_no='checked' if spacing != '1' else '',
        log_output=log_output
    )


def _render_sample_page(title, content):
    """Render a generic sample page."""
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PhpSpreadsheet - {title}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; color: #333; }}
        .container {{ max-width: 960px; margin: 0 auto; }}
        h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        .breadcrumb {{ background: #ecf0f1; padding: 10px 15px; border-radius: 4px; margin-bottom: 20px; font-size: 14px; }}
        .breadcrumb a {{ color: #3498db; text-decoration: none; }}
        .breadcrumb a:hover {{ text-decoration: underline; }}
        .content {{ background: #fff; padding: 25px; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        pre {{ background: #2c3e50; color: #ecf0f1; padding: 15px; border-radius: 4px; overflow-x: auto; }}
        code {{ font-family: "Source Code Pro", Consolas, monospace; }}
        .result {{ color: #27ae60; font-weight: bold; }}
        footer {{ margin-top: 40px; padding: 20px 0; border-top: 1px solid #ddd; color: #7f8c8d; font-size: 13px; }}
    </style>
</head>
<body>
<div class="container">
    <div class="breadcrumb">
        <a href="/">Samples</a> &raquo; {title}
    </div>
    <h1>{title}</h1>
    <div class="content">
        {content}
    </div>
    <footer>
        PhpSpreadsheet - Read, Create and Write Spreadsheet documents in PHP
    </footer>
</div>
</body>
</html>'''.format(title=title, content=content)


@app.errorhandler(404)
def not_found(e):
    return '''<!DOCTYPE html>
<html><head><title>404 Not Found</title>
<style>body { font-family: sans-serif; text-align: center; padding: 50px; }</style>
</head><body><h1>404 Not Found</h1><p>The requested URL was not found on this server.</p></body></html>''', 404


@app.errorhandler(500)
def internal_error(e):
    return '''<!DOCTYPE html>
<html><head><title>500 Internal Server Error</title>
<style>body { font-family: sans-serif; text-align: center; padding: 50px; }</style>
</head><body><h1>500 Internal Server Error</h1><p>An internal error occurred.</p></body></html>''', 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
