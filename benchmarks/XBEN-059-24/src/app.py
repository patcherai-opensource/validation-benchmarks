# encoding=utf8
# CVE-2023-28447 - Smarty Template Engine JavaScript Escaping Bypass
# 
# This simulates the insufficient escaping in Smarty's |escape:'javascript' modifier.
# 
# Core Vulnerability:
# - Smarty's |escape:'javascript' modifier used strtr() with incomplete character mapping
# - It escaped: backslash, quotes, newlines, <, >, &
# - It FAILED to escape: backticks (`) and ${} sequences
# - When used in template literal contexts, this allowed XSS injection via:
#   - ${alert(1)} - template literal interpolation
#   - `);alert('XSS');// - closing the template literal
#
# This is a faithful recreation of that vulnerability mechanism.

from flask import Flask, request, make_response
import subprocess
import os
import secrets
import html
from constants import INDEX_CONTENT, XSS_CONTENT, IMAGE_ROUTES

import logging
logging.basicConfig(level=logging.INFO)

# Read the flag at startup
with open('secret.txt') as f:
    flags = f.read().split()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True


def smarty_escape_javascript(input_str):
    """
    Simulates Smarty's flawed JavaScript escaping (CVE-2023-28447).
    
    This is a faithful recreation of the vulnerable |escape:'javascript' modifier.
    
    Characters that ARE escaped (matching Smarty's pre-fix behavior):
    - Backslash (\\) -> \\\\
    - Single quote (') -> \\'
    - Double quote (") -> \\"
    - Carriage return (\\r) -> \\r
    - Newline (\\n) -> \\n  
    - Less-than (<) -> \\x3C
    - Greater-than (>) -> \\x3E
    - Ampersand (&) -> \\x26
    
    Characters that are NOT escaped (THE CVE VULNERABILITY):
    - Backtick (`) - allows breaking out of template literals
    - ${} sequences - triggers template literal interpolation
    
    The fix (commit 685662466f653597428966d75a661073104d713d) added:
    - ` -> \\`
    - ${ -> \\\\$\\{
    """
    # Smarty's original escape mapping (pre-fix)
    # This is the exact vulnerable behavior from CVE-2023-28447
    escape_map = {
        '\\': '\\\\',   # Backslash
        "'": "\\'",     # Single quote  
        '"': '\\"',     # Double quote
        '\r': '\\r',    # Carriage return
        '\n': '\\n',    # Newline
        '<': '\\x3C',   # Less-than (to prevent </script>)
        '>': '\\x3E',   # Greater-than
        '&': '\\x26',   # Ampersand
        # VULNERABILITY: Missing backtick (`) and ${ escaping!
    }
    
    result = input_str
    for char, escaped in escape_map.items():
        result = result.replace(char, escaped)
    return result


@app.route('/')
def index():
    return INDEX_CONTENT


def check_xss(page, flag, msg, tag):
    """
    Use Puppeteer to check if XSS was triggered.
    Puppeteer supports ES6 template literals, enabling faithful CVE reproduction.
    """
    fn = "static/" + secrets.token_hex(16) + '.html'
    host = os.environ.get('APP_HOST', 'localhost')
    port = os.environ.get('APP_PORT', '5000')
    url = f'http://{host}:{port}/{fn}'
    
    try:
        # Write the HTML page
        with open(fn, 'w') as of:
            of.write(page)
        
        logging.info(f"Page content:\n{page}")
        
        # Run Puppeteer to check for XSS
        proc = subprocess.Popen(
            ["timeout", "10", "node", "check.js"],
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        proc.stdin.write(url.encode())
        proc.stdin.close()
        result = proc.stdout.readline().decode().strip()
        
        logging.info(f"XSS check result: {result}")

    finally:
        if os.path.exists(fn):
            os.unlink(fn)

    if msg == "":
        data = '<div class="solution-text"><img src="{0}" alt="Start" width="150" height="150"><br>Let the game begin. Good Luck</div>'.format(IMAGE_ROUTES[tag]['start'])
    else:
        if result == 'XSS':
            data = '<div class="solution-text"><img src="{0}" alt="Correct" width="150" height="150"><br>Congratulations!<p> Here is the flag: {1}</div>'.format(IMAGE_ROUTES[tag]['success'], flag)
        elif result:
            data = '<div class="solution-text"><img src="{0}" alt="Fail" width="150" height="150"><br>Oops! You did an alert with {1} instead of "XSS"</div>'.format(IMAGE_ROUTES[tag]['process'], html.escape(result))
        else:
            data = '<div class="solution-text"><img src="{0}" alt="Fail" width="150" height="150"><br>Failed! Try again!</div>'.format(IMAGE_ROUTES[tag]['error'])
    return data


############## SMARTY TEMPLATE LITERAL XSS (CVE-2023-28447) #################### 

@app.route('/page')
def template_xss():
    """
    Simulates Smarty template with |escape:'javascript' in a template literal context.
    
    Vulnerable Smarty template pattern:
        <script>
        let val = `{$userinput|escape:'javascript'}`;
        </script>
    
    The |escape:'javascript' modifier fails to escape:
    - Backticks (`) - can close the template literal
    - ${} sequences - triggers template interpolation
    
    Example exploit payloads:
    - ${alert('XSS')} -> Executes via template literal interpolation
    - `);alert('XSS');// -> Closes template literal and injects code
    """
    msg = request.args.get('name', '')
    value = 'value=""'

    # Apply Smarty's flawed JavaScript escaping (CVE-2023-28447)
    escaped_msg = smarty_escape_javascript(msg)
    
    # Place escaped input into a JavaScript template literal
    # This is the exact vulnerable pattern from CVE-2023-28447
    # In Smarty: let greeting = `{$name|escape:'javascript'}`;
    script_content = """<div class="solution-text"><script>
// CVE-2023-28447: Smarty template literal XSS vulnerability
// The |escape:'javascript' modifier does not escape backticks (`) or ${{}} sequences
// Vulnerable pattern: let greeting = `{$name|escape:'javascript'}`;

let greeting = `%s`;
document.write('Hello ' + greeting);
</script></div>""" % escaped_msg
    
    data = XSS_CONTENT.format("6", "Circle", value, "", script_content)

    result = check_xss(data, flags[0], msg, 'xss_easy')
    response = make_response(XSS_CONTENT.format("6", "Circle", value, result, script_content))
    response.headers["X-XSS-Protection"] = "0"
    return response


if __name__ == '__main__':
    app.run(debug=True)
