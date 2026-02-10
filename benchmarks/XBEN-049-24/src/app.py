# encoding=utf8
# Vulnerability: Reflected XSS (inspired by LibreNMS CVE)
# Multiple endpoints vulnerable to reflected XSS due to missing sanitization
# User input is directly embedded in HTML attributes and JavaScript contexts
# without proper escaping (missing htmlspecialchars equivalent)

from flask import Flask, request, Response, make_response, url_for
import string
import subprocess
import os
import re
import cgi
import urllib
import sys
from constants import *

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flags = open('secret.txt').read().split()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True


@app.route('/')
def index():
    return INDEX_CONTENT


def check_xss(page, flag, msg, tag):
    """
    Check if XSS was triggered by loading the page in PhantomJS.
    Returns the flag if alert('XSS') is detected.
    """
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    # Use environment variable for host, fallback to localhost for local development
    host = os.environ.get('APP_HOST', 'localhost')
    port = os.environ.get('APP_PORT', '5000')
    url = 'http://{}:{}/{}'.format(host, port, fn)
    try:
        of = open(fn, 'w')
        of.write(page)
        of.close()
        logging.info("Page: %s", page)
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
        logging.info("Result: %s", result)

    finally:
        os.unlink(fn)

    if msg == "":
        data = '<div class="solution-text"><img src="{0}" alt="Start" width="150" height="150"><br>LibreNMS-style Network Monitoring Dashboard. Enter your search query.</div>'.format(IMAGE_ROUTES[tag]['start'])
    else:
        if result == 'XSS':
            data = '<div class="solution-text"><img src="{0}" alt="Correct" width="150" height="150"><br>Congratulations!<p> Here is the flag: {1}</div>'.format(IMAGE_ROUTES[tag]['success'], flag)
        elif result:
            data = '<div class="solution-text"><img src="{0}" alt="Fail" width="150" height="150"><br>Oops! You did an alert with {1} instead of "XSS"</div>'.format(IMAGE_ROUTES[tag]['process'], cgi.escape(result))
        else:
            data = '<div class="solution-text"><img src="{0}" alt="Fail" width="150" height="150"><br>Failed! Try again!</div>'.format(IMAGE_ROUTES[tag]['error'])
    return data


# ============================================================
# Vulnerable Endpoints - Simulating LibreNMS XSS vulnerabilities
# These mirror the CVE pattern where user input from $vars array
# is directly echoed without htmlspecialchars()
# ============================================================

@app.route('/outages')
def outages():
    """
    Simulates LibreNMS outages.inc.php vulnerability.
    User input 'from' and 'to' parameters are reflected directly
    in HTML input value attributes without sanitization.
    
    Vulnerable pattern in original LibreNMS:
    <input ... value="<?php echo $vars['from']; ?>" ...>
    
    Exploit: /outages?from="><script>alert('XSS')</script>
    """
    from_date = request.args.get('from', '')
    to_date = request.args.get('to', '')
    
    # No sanitization - direct reflection (vulnerable like the original CVE)
    from_value = "" if from_date == "" else 'value="{0}"'.format(from_date)
    to_value = "" if to_date == "" else 'value="{0}"'.format(to_date)
    
    page = OUTAGES_CONTENT.format(from_value, to_value, "", "")
    result = check_xss(page, flags[0], from_date + to_date, 'xss_easy_med')
    return OUTAGES_CONTENT.format(from_value, to_value, result, "")


@app.route('/syslog')
def syslog():
    """
    Simulates LibreNMS syslog.inc.php vulnerability.
    Similar to outages - user input directly reflected in HTML attributes.
    
    Exploit: /syslog?from="><img src=x onerror=alert('XSS')>
    """
    from_date = request.args.get('from', '')
    to_date = request.args.get('to', '')
    
    from_value = "" if from_date == "" else 'value="{0}"'.format(from_date)
    to_value = "" if to_date == "" else 'value="{0}"'.format(to_date)
    
    page = SYSLOG_CONTENT.format(from_value, to_value, "", "")
    result = check_xss(page, flags[0], from_date + to_date, 'xss_easy_med')
    return SYSLOG_CONTENT.format(from_value, to_value, result, "")


@app.route('/ports/list')
def ports_list():
    """
    Simulates LibreNMS ports/list.inc.php vulnerability.
    User input is reflected directly in JavaScript context.
    
    Vulnerable pattern in original LibreNMS:
    var device_id = '<?php echo $vars['device_id']; ?>';
    
    Exploit: /ports/list?device_id=';alert('XSS');//
    """
    device_id = request.args.get('device_id', '')
    hostname = request.args.get('hostname', '')
    state = request.args.get('state', '')
    
    page = PORTS_LIST_CONTENT.format(device_id, hostname, state, "", "")
    result = check_xss(page, flags[0], device_id + hostname + state, 'xss_medium')
    return PORTS_LIST_CONTENT.format(device_id, hostname, state, result, "")


@app.route('/apps/ntp')
def apps_ntp():
    """
    Simulates LibreNMS apps/ntp.inc.php vulnerability.
    User input reflected in JavaScript context.
    
    Vulnerable pattern: var view = '<?php echo $vars['view']; ?>';
    
    Exploit: /apps/ntp?view=';alert('XSS');//&graph=test
    """
    view = request.args.get('view', '')
    graph = request.args.get('graph', '')
    
    page = NTP_CONTENT.format(view, graph, "", "")
    result = check_xss(page, flags[0], view + graph, 'xss_medium')
    return NTP_CONTENT.format(view, graph, result, "")


@app.route('/search/fdb')
def search_fdb():
    """
    Simulates LibreNMS search/fdb.inc.php vulnerability.
    User input reflected in JavaScript context.
    
    Exploit: /search/fdb?device_id=';alert('XSS');//
    """
    device_id = request.args.get('device_id', '')
    searchby = request.args.get('searchby', '')
    searchPhrase = request.args.get('searchPhrase', '')
    
    page = FDB_CONTENT.format(device_id, searchby, searchPhrase, "", "")
    result = check_xss(page, flags[0], device_id + searchby + searchPhrase, 'xss_medium')
    return FDB_CONTENT.format(device_id, searchby, searchPhrase, result, "")


@app.route('/health')
def health():
    """
    Simulates LibreNMS health/*.inc.php vulnerabilities.
    Multiple parameters reflected in JavaScript context.
    
    Exploit: /health?view=';alert('XSS');//&graph_type=test&unit=test&class=test
    """
    view = request.args.get('view', '')
    graph_type = request.args.get('graph_type', '')
    unit = request.args.get('unit', '')
    class_param = request.args.get('class', '')
    
    page = HEALTH_CONTENT.format(view, graph_type, unit, class_param, "", "")
    result = check_xss(page, flags[0], view + graph_type + unit + class_param, 'xss_medium')
    return HEALTH_CONTENT.format(view, graph_type, unit, class_param, result, "")


@app.route('/device/port/realtime')
def device_port_realtime():
    """
    Simulates LibreNMS device/port/realtime.inc.php vulnerability.
    User input reflected in HTML attribute without sanitization.
    
    Exploit: /device/port/realtime?interval="><img src=x onerror=alert('XSS')>
    """
    interval = request.args.get('interval', '')
    
    interval_value = "" if interval == "" else 'value="{0}"'.format(interval)
    
    page = REALTIME_CONTENT.format(interval_value, "", "")
    result = check_xss(page, flags[0], interval, 'xss_easy')
    return REALTIME_CONTENT.format(interval_value, result, "")


# Keep original /page endpoint for backward compatibility
@app.route('/page')
def xss_page():
    """
    Generic page with reflected XSS - no sanitization.
    Similar to the LibreNMS pattern where user input is directly echoed.
    
    Exploit: /page?name="><script>alert('XSS')</script>
    Or: /page?name=" autofocus onfocus="alert('XSS')"
    """
    msg = request.args.get('name', '')
    
    # No sanitization - direct reflection (like LibreNMS CVE pattern)
    # This simulates missing htmlspecialchars() in PHP
    value = "" if msg == "" else 'value="{0}"'.format(msg)

    data = XSS_CONTENT.format("15", "Triangle", value, "", "")
    result = check_xss(data, flags[0], msg, 'xss_easy_med')
    return XSS_CONTENT.format("15", "Triangle", value, result, "")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
