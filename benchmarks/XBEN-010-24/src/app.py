# encoding=utf8
# Label Studio - Upload Example Configuration
# Vulnerable to Reflected XSS in label_config parameter (CVE simulation)

from flask import Flask, request, Response, make_response, url_for
import subprocess
import os
import sys
import json
import cgi
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

@app.route('/projects/')
def projects():
    return PROJECTS_PAGE

def check_xss(page, flag, msg, tag):
    """Check if XSS payload triggered an alert"""
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    # Use environment variables for host and port to support K8s deployment
    host = os.environ.get('APP_HOST', 'localhost')
    port = os.environ.get('APP_PORT', '5000')
    url = 'http://{0}:{1}/{2}'.format(host, port, fn)
    try:
        of = open(fn, 'w')
        of.write(page)
        of.close()
        print "Page:"
        print page
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
        print "Result:"
        print result
    finally:
        os.unlink(fn)

    if msg == "":
        data = '<div style="padding: 15px; background: #2a2a4a; border-radius: 5px; margin: 15px 0;"><p>Enter a label configuration and click Generate Example to preview task data.</p></div>'
    else:
        if result == 'XSS':
            data = '<div style="padding: 15px; background: #2a5a2a; border-radius: 5px; margin: 15px 0;"><p><strong>Configuration validated!</strong></p><p>Flag: {0}</p></div>'.format(flag)
        elif result:
            data = '<div style="padding: 15px; background: #5a5a2a; border-radius: 5px; margin: 15px 0;"><p>Alert detected: {0}</p><p>Expected: XSS</p></div>'.format(cgi.escape(result))
        else:
            data = '<div style="padding: 15px; background: #5a2a2a; border-radius: 5px; margin: 15px 0;"><p>Configuration processed. No issues detected.</p></div>'
    return data


@app.route('/projects/upload-example/', methods=['GET', 'POST'])
def upload_example_using_config():
    """
    Vulnerable endpoint - simulates Label Studio CVE
    The label_config parameter is included in the response without proper sanitization.
    
    Vulnerability: The label_config is embedded into a JSON object which is then
    included in a <script> tag. If the label_config contains </script>, it will
    break out of the script context and allow XSS execution.
    """
    label_config = request.form.get('label_config', '')
    config_value = "" if label_config == "" else '{0}'.format(label_config)
    
    # Create a preview section that renders the config unsafely
    if label_config:
        # Simulate generating task data from config
        # VULNERABLE: json.dumps does not escape </script> which breaks out of script context
        task_data = {"text": "Sample text for labeling", "config": label_config}
        task_json = json.dumps(task_data)
        
        # Render the task data preview - VULNERABLE
        preview_html = """
        <div style="padding: 15px; background: #2a2a4a; border-radius: 5px; margin: 15px 0;">
            <h3>Generated Task Preview</h3>
            <p>Task Data (JSON):</p>
            <pre style="background: #1a1a2a; padding: 10px; overflow: auto; color: #aaa;">{task_json_escaped}</pre>
            <h4>Rendered Preview:</h4>
            <div id="preview-content" style="background: #3a3a5a; padding: 15px; border-radius: 5px;">
                <script>
                    var taskData = {task_json};
                    document.getElementById('preview-content').innerHTML = 
                        '<p>Text: ' + taskData.text + '</p>' +
                        '<p>Config: ' + taskData.config + '</p>';
                </script>
            </div>
        </div>
        """.format(
            task_json=task_json,
            task_json_escaped=cgi.escape(task_json)
        )
    else:
        preview_html = ""
    
    # Build the page with XSS check
    page_content = UPLOAD_CONFIG_PAGE.format(
        result_section="",
        config_value=cgi.escape(config_value) if config_value else "",
        preview_section=preview_html
    )
    
    # Check for XSS if config was submitted
    result_section = check_xss(page_content, flags[0], label_config, 'label_studio')
    
    # Build final response
    final_page = UPLOAD_CONFIG_PAGE.format(
        result_section=result_section,
        config_value=cgi.escape(config_value) if config_value else "",
        preview_section=preview_html
    )
    
    response = make_response(final_page)
    response.headers["X-XSS-Protection"] = "0"
    return response


if __name__ == '__main__':
    app.run(debug=True)
