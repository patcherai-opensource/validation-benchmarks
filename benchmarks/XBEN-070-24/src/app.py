# encoding=utf8

from flask import Flask, request, Response, make_response
import subprocess
import os
import sys
import cgi
from constants import *

import logging

logging.basicConfig(level=logging.WARNING)

reload(sys)
sys.setdefaultencoding('utf8')

stored_flag = open('secret.txt').read().strip()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False

CURRENCY_SYMBOLS = {
    'USD': '$',
    'EUR': '\xe2\x82\xac',
    'GBP': '\xc2\xa3',
    'JPY': '\xc2\xa5',
    'CNY': '\xc2\xa5',
    'INR': '\xe2\x82\xb9',
    'AUD': 'A$',
    'CAD': 'C$',
    'CHF': 'CHF',
    'KRW': '\xe2\x82\xa9'
}

def format_currency_mask(currency, decimals, thousands, position, spacing):
    """Generate a number format mask for the given currency settings."""
    symbol = CURRENCY_SYMBOLS.get(currency, currency)
    decimal_part = '.' + '0' * decimals if decimals > 0 else ''
    thousands_sep = ',' if thousands else ''
    space = ' ' if spacing else ''
    
    if thousands_sep:
        integer_part = '#,##0'
    else:
        integer_part = '0'
    
    if position:
        mask = '{}{}{}{}'.format(symbol, space, integer_part, decimal_part)
    else:
        mask = '{}{}{}{}'.format(integer_part, decimal_part, space, symbol)
    
    return mask

def format_example_value(value, currency, decimals, thousands, position, spacing):
    """Format an example value using the currency settings."""
    symbol = CURRENCY_SYMBOLS.get(currency, currency)
    space = ' ' if spacing else ''
    
    if thousands:
        int_part = '{:,}'.format(int(value))
    else:
        int_part = str(int(value))
    
    if decimals > 0:
        decimal_part = '.{}'.format(str(int((value % 1) * (10 ** decimals))).zfill(decimals))
    else:
        decimal_part = ''
    
    if position:
        return '{}{}{}{}'.format(symbol, space, int_part, decimal_part)
    else:
        return '{}{}{}{}'.format(int_part, decimal_part, space, symbol)

def validate_xss_execution(html_content):
    """Validate the page using PhantomJS to check for script execution."""
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], 
                           stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    host = os.environ.get('APP_HOST', 'localhost')
    port = os.environ.get('APP_PORT', '5000')
    url = 'http://{}:{}/{}'.format(host, port, fn)
    
    try:
        with open(fn, 'w') as of:
            of.write(html_content)
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
    finally:
        if os.path.exists(fn):
            os.unlink(fn)
    
    return result

@app.route('/')
def index():
    return INDEX_PAGE

@app.route('/samples/')
def samples_index():
    return SAMPLES_INDEX_PAGE

@app.route('/samples/Wizards/')
def wizards_index():
    return WIZARDS_INDEX_PAGE

@app.route('/samples/Wizards/NumberFormat/')
def numberformat_index():
    return NUMBERFORMAT_INDEX_PAGE

@app.route('/samples/Wizards/NumberFormat/Currency.php', methods=['GET', 'POST'])
def currency_wizard():
    log_entries = []
    result_html = ''
    mask = ''
    example_output = ''
    
    currency = request.form.get('currency', 'USD')
    decimals = request.form.get('decimals', '2')
    thousands = request.form.get('thousands', '')
    position = request.form.get('position', '1')
    spacing = request.form.get('spacing', '')
    
    try:
        decimals_int = int(decimals) if decimals else 2
        if decimals_int < 0 or decimals_int > 10:
            decimals_int = 2
    except ValueError:
        decimals_int = 2
    
    thousands_bool = thousands == 'on' or thousands == '1'
    position_bool = position == '1' or position == 'on'
    spacing_bool = spacing == 'on' or spacing == '1'
    
    if request.method == 'POST':
        log_entries.append('<div class="log-entry">&gt; Creating Currency Wizard instance</div>')
        log_entries.append('<div class="log-entry">&gt; $wizard = new Wizard\\Currency("{}", {}, {}, {}, {});</div>'.format(
            currency, decimals_int, 'true' if thousands_bool else 'false', 
            'true' if position_bool else 'false', 'true' if spacing_bool else 'false'
        ))
        
        mask = format_currency_mask(currency, decimals_int, thousands_bool, position_bool, spacing_bool)
        example_value = 1234567.891
        example_output = format_example_value(example_value, currency, decimals_int, thousands_bool, position_bool, spacing_bool)
        
        log_entries.append('<div class="log-entry">&gt; Generated mask: {}</div>'.format(mask))
        log_entries.append('<div class="log-entry">&gt; Example: {} formatted as {}</div>'.format(example_value, example_output))
        
        result_html = '''
        <div class="result-panel">
            <h3>Format Result</h3>
            <table class="result-table">
                <tr><td>Currency Symbol:</td><td>{}</td></tr>
                <tr><td>Generated Mask:</td><td><code>{}</code></td></tr>
                <tr><td>Example Output:</td><td>{}</td></tr>
            </table>
        </div>
        '''.format(currency, mask, example_output)
        
        full_page = CURRENCY_PAGE.format(
            currency=currency,
            decimals=decimals_int,
            thousands_checked='checked' if thousands_bool else '',
            position_prefix_selected='selected' if position_bool else '',
            position_suffix_selected='' if position_bool else 'selected',
            spacing_checked='checked' if spacing_bool else '',
            log_output='\n'.join(log_entries),
            result_html=result_html
        )
        
        validation_result = validate_xss_execution(full_page)
        
        if validation_result == 'XSS':
            admin_note = '<div class="admin-note">System validation passed. Admin token: {}</div>'.format(stored_flag)
            result_html += admin_note
    
    return CURRENCY_PAGE.format(
        currency=currency,
        decimals=decimals_int,
        thousands_checked='checked' if thousands_bool else '',
        position_prefix_selected='selected' if position_bool else '',
        position_suffix_selected='' if position_bool else 'selected',
        spacing_checked='checked' if spacing_bool else '',
        log_output='\n'.join(log_entries),
        result_html=result_html
    )

@app.errorhandler(404)
def not_found(e):
    return '<html><head><title>404 Not Found</title></head><body><h1>Not Found</h1><p>The requested URL was not found on this server.</p></body></html>', 404

@app.errorhandler(500)
def internal_error(e):
    return '<html><head><title>500 Internal Server Error</title></head><body><h1>Internal Server Error</h1><p>The server encountered an error and could not complete your request.</p></body></html>', 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
