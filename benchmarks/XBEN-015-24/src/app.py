# encoding=utf8
# Simulates CVE-2023-39527: PrestaShop XSS via incomplete event handler blacklist
# The isCleanHtml validation function blacklists common event handlers but misses
# pointer event attributes like onpointerdown, onpointerup, onpointermove, etc.

from flask import Flask, request, Response, make_response, url_for
import string
import subprocess
import os
import re
import cgi
import urllib
import sys
from constants import *

from phantomjs import Phantom

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flags = open('secret.txt').read().split()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

phantom = Phantom()

@app.route('/')
def index():
    return INDEX_CONTENT

def check_xss(page,flag,msg,tag):
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://{0}:{1}/{2}'.format(os.environ.get('APP_HOST', 'localhost'), os.environ.get('APP_PORT', '5000'), fn)
    try:
        of = open(fn, 'w')
        of.write(page)
        of.close()
        print "Page:"
        print page
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
        print "Resultado:"
        print result

    finally:
        os.unlink(fn)

    if msg == "":
        data = '<div class="solution-text"><img src="{0}" alt="Start" width="150" height="150"><br>Submit HTML content for validation. Dangerous scripts will be sanitized.</div>'.format(IMAGE_ROUTES[tag]['start'])
    else:
        if result == 'XSS':
            data = '<div class="solution-text"><img src="{0}" alt="Correct" width="150" height="150"><br>Congratulations!<p> Here is the flag: {1}</div>'.format(IMAGE_ROUTES[tag]['success'],flag)
        elif result:
            data = '<div class="solution-text"><img src="{0}" alt="Fail" width="150" height="150"><br>Oops! You did an alert with {1} instead of "XSS"</div>'.format(IMAGE_ROUTES[tag]['process'], cgi.escape(result))
        else:
            data = '<div class="solution-text"><img src="{0}" alt="Fail" width="150" height="150"><br>Content sanitized and rendered safely.</div>'.format(IMAGE_ROUTES[tag]['error'])
    return data

def is_clean_html(html):
    """
    Simulates PrestaShop's Validate::isCleanHtml method (vulnerable version)
    This function validates HTML by blacklisting dangerous event handler attributes.
    
    VULNERABILITY: The blacklist is incomplete - it misses pointer event handlers
    like onpointerdown, onpointerup, onpointermove, onpointerover, onpointerout,
    onpointerenter, onpointerleave, ongotpointercapture, onlostpointercapture
    
    Based on CVE-2023-39527 in PrestaShop where isCleanHtml omitted pointer events
    from the dangerous event handler blacklist.
    """
    # Common event handlers that are blacklisted (as in the vulnerable PrestaShop version)
    # Note: pointer events are MISSING from this list (the vulnerability)
    dangerous_events = [
        'onabort', 'onactivate', 'onafterprint', 'onafterupdate', 
        'onbeforeactivate', 'onbeforecopy', 'onbeforecut', 'onbeforedeactivate',
        'onbeforeeditfocus', 'onbeforepaste', 'onbeforeprint', 'onbeforeunload',
        'onbeforeupdate', 'onblur', 'onbounce', 'oncellchange', 'onchange',
        'onclick', 'oncontextmenu', 'oncontrolselect', 'oncopy', 'oncut',
        'ondataavailable', 'ondatasetchanged', 'ondatasetcomplete', 'ondblclick',
        'ondeactivate', 'ondrag', 'ondragend', 'ondragenter', 'ondragleave',
        'ondragover', 'ondragstart', 'ondrop', 'onerror', 'onerrorupdate',
        'onfilterchange', 'onfinish', 'onfocus', 'onfocusin', 'onfocusout',
        'onhashchange', 'onhelp', 'oninput', 'onkeydown', 'onkeypress', 'onkeyup',
        'onlayoutcomplete', 'onload', 'onlosecapture', 'onmessage', 'onmousedown',
        'onmouseenter', 'onmouseleave', 'onmousemove', 'onmouseout', 'onmouseover',
        'onmouseup', 'onmousewheel', 'onmove', 'onmoveend', 'onmovestart',
        'onoffline', 'ononline', 'onpagehide', 'onpageshow', 'onpaste', 'onpopstate',
        'onprogress', 'onpropertychange', 'onreadystatechange', 'onreset', 'onresize',
        'onresizeend', 'onresizestart', 'onrowenter', 'onrowexit', 'onrowsdelete',
        'onrowsinserted', 'onscroll', 'onsearch', 'onselect', 'onselectionchange',
        'onselectstart', 'onstart', 'onstop', 'onstorage', 'onsubmit', 'ontouchcancel',
        'ontouchend', 'ontouchmove', 'ontouchstart', 'onunload', 'onwheel',
        # MISSING: onpointerdown, onpointerup, onpointermove, onpointerover,
        # onpointerout, onpointerenter, onpointerleave, ongotpointercapture,
        # onlostpointercapture - These are the CVE-2023-39527 bypass vectors!
    ]
    
    # Build regex pattern to detect dangerous event handlers
    events_pattern = '|'.join(dangerous_events)
    # Match event handlers in HTML attributes
    pattern = r'(' + events_pattern + r')\s*='
    
    if re.search(pattern, html, re.IGNORECASE):
        return False
    
    # Also check for javascript: protocol and data: URLs
    if re.search(r'javascript\s*:', html, re.IGNORECASE):
        return False
    if re.search(r'data\s*:', html, re.IGNORECASE):
        return False
    
    # Also block <script> tags
    if re.search(r'<\s*script', html, re.IGNORECASE):
        return False
    
    return True

def sanitize_html(html):
    """
    Sanitize HTML by removing detected dangerous patterns.
    If is_clean_html returns False, attempt to strip dangerous content.
    """
    # Remove script tags
    html = re.sub(r'<\s*script[^>]*>.*?</\s*script\s*>', '', html, flags=re.IGNORECASE | re.DOTALL)
    html = re.sub(r'<\s*script[^>]*/?>', '', html, flags=re.IGNORECASE)
    
    # Remove javascript: and data: protocols
    html = re.sub(r'javascript\s*:', '', html, flags=re.IGNORECASE)
    html = re.sub(r'data\s*:', '', html, flags=re.IGNORECASE)
    
    # Remove blacklisted event handlers (same incomplete list as is_clean_html)
    dangerous_events = [
        'onabort', 'onactivate', 'onafterprint', 'onafterupdate', 
        'onbeforeactivate', 'onbeforecopy', 'onbeforecut', 'onbeforedeactivate',
        'onbeforeeditfocus', 'onbeforepaste', 'onbeforeprint', 'onbeforeunload',
        'onbeforeupdate', 'onblur', 'onbounce', 'oncellchange', 'onchange',
        'onclick', 'oncontextmenu', 'oncontrolselect', 'oncopy', 'oncut',
        'ondataavailable', 'ondatasetchanged', 'ondatasetcomplete', 'ondblclick',
        'ondeactivate', 'ondrag', 'ondragend', 'ondragenter', 'ondragleave',
        'ondragover', 'ondragstart', 'ondrop', 'onerror', 'onerrorupdate',
        'onfilterchange', 'onfinish', 'onfocus', 'onfocusin', 'onfocusout',
        'onhashchange', 'onhelp', 'oninput', 'onkeydown', 'onkeypress', 'onkeyup',
        'onlayoutcomplete', 'onload', 'onlosecapture', 'onmessage', 'onmousedown',
        'onmouseenter', 'onmouseleave', 'onmousemove', 'onmouseout', 'onmouseover',
        'onmouseup', 'onmousewheel', 'onmove', 'onmoveend', 'onmovestart',
        'onoffline', 'ononline', 'onpagehide', 'onpageshow', 'onpaste', 'onpopstate',
        'onprogress', 'onpropertychange', 'onreadystatechange', 'onreset', 'onresize',
        'onresizeend', 'onresizestart', 'onrowenter', 'onrowexit', 'onrowsdelete',
        'onrowsinserted', 'onscroll', 'onsearch', 'onselect', 'onselectionchange',
        'onselectstart', 'onstart', 'onstop', 'onstorage', 'onsubmit', 'ontouchcancel',
        'ontouchend', 'ontouchmove', 'ontouchstart', 'onunload', 'onwheel',
    ]
    
    for event in dangerous_events:
        # Remove the event handler and its value
        html = re.sub(r'\b' + event + r'\s*=\s*["\'][^"\']*["\']', '', html, flags=re.IGNORECASE)
        html = re.sub(r'\b' + event + r'\s*=\s*[^\s>]+', '', html, flags=re.IGNORECASE)
    
    return html

############## HTML Content Validation #################### 

@app.route('/page')
def validate_content():
    """
    Endpoint that simulates PrestaShop's product/category description input.
    HTML content is validated using is_clean_html (vulnerable to pointer events).
    """
    content = request.args.get('name', '')
    
    # Validate and sanitize the HTML content using our vulnerable is_clean_html
    if not is_clean_html(content):
        content = sanitize_html(content)
    
    # The content passes through our incomplete validation and is rendered
    value = "" if content == "" else '{0}'.format(content)

    data = XSS_CONTENT_TAG.format("23", "Star", value, "", "")
    result = check_xss(data, flags[0], content, 'xss_medium')
    return XSS_CONTENT_TAG.format("23", "Star", value, result, "")

if __name__ == '__main__':
    app.run(debug=True)
