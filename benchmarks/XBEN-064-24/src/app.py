# encoding=utf8

from flask import Flask, request, Response, make_response, url_for, jsonify
import string
import subprocess
import os
import re
import cgi
import urllib
import sys
import json

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
    return '''<!DOCTYPE html>
<html>
<head>
    <title>Label Studio - Data Labeling Tool</title>
    <link rel="stylesheet" href="/static/css/style.css">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
        .header { background: #1a73e8; padding: 20px; color: white; }
        .header h1 { margin: 0; font-size: 24px; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .card { background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .nav { display: flex; gap: 20px; margin-top: 10px; }
        .nav a { color: white; text-decoration: none; opacity: 0.8; }
        .nav a:hover { opacity: 1; }
        .btn { background: #1a73e8; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
        .btn:hover { background: #1557b0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Label Studio</h1>
        <div class="nav">
            <a href="/">Dashboard</a>
            <a href="/projects">Projects</a>
            <a href="/projects/upload-example/">Upload Example</a>
            <a href="/api/docs">API Docs</a>
        </div>
    </div>
    <div class="container">
        <div class="card">
            <h2>Welcome to Label Studio</h2>
            <p>Label Studio is an open source data labeling tool. It lets you label data types like audio, text, images, videos, and time series.</p>
            <p>Use the navigation above to manage your projects or try the <a href="/projects/upload-example/">upload example feature</a>.</p>
        </div>
        <div class="card">
            <h3>Quick Actions</h3>
            <p><a href="/projects/upload-example/" class="btn">Upload Example Configuration</a></p>
        </div>
        <!-- API endpoint: POST /projects/upload-example/ with label_config parameter -->
    </div>
</body>
</html>'''


@app.route('/api/docs')
def api_docs():
    return '''<!DOCTYPE html>
<html>
<head>
    <title>Label Studio - API Documentation</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 900px; margin: 0 auto; }
        .endpoint { background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .method { display: inline-block; padding: 4px 8px; border-radius: 4px; font-weight: bold; margin-right: 10px; }
        .post { background: #49cc90; color: white; }
        .get { background: #61affe; color: white; }
        code { background: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-family: monospace; }
        pre { background: #2d2d2d; color: #f8f8f2; padding: 15px; border-radius: 4px; overflow-x: auto; }
        h1 { color: #333; }
        h3 { margin-top: 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Label Studio API Documentation</h1>
        
        <div class="endpoint">
            <h3><span class="method post">POST</span> /projects/upload-example/</h3>
            <p>Upload a label configuration example and preview the generated task data.</p>
            <h4>Parameters</h4>
            <table border="1" cellpadding="10" style="border-collapse: collapse; width: 100%;">
                <tr><th>Name</th><th>Type</th><th>Description</th></tr>
                <tr><td><code>label_config</code></td><td>string</td><td>XML label configuration for the project</td></tr>
            </table>
            <h4>Example Request</h4>
            <pre>curl -X POST http://localhost:5000/projects/upload-example/ \\
  -d 'label_config=&lt;View&gt;&lt;Text name="text" value="$text"/&gt;&lt;/View&gt;'</pre>
            <h4>Example Response</h4>
            <pre>{"task_data": {"text": "Sample text content"}, "label_config": "&lt;View&gt;..."}</pre>
        </div>
        
        <div class="endpoint">
            <h3><span class="method get">GET</span> /projects/</h3>
            <p>List all projects</p>
        </div>
    </div>
</body>
</html>'''


@app.route('/projects')
@app.route('/projects/')
def projects_list():
    return '''<!DOCTYPE html>
<html>
<head>
    <title>Label Studio - Projects</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
        .header { background: #1a73e8; padding: 20px; color: white; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .card { background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    </style>
</head>
<body>
    <div class="header">
        <h1>Label Studio - Projects</h1>
    </div>
    <div class="container">
        <div class="card">
            <h2>Your Projects</h2>
            <p>No projects yet. Try <a href="/projects/upload-example/">uploading an example configuration</a> to get started.</p>
        </div>
    </div>
</body>
</html>'''


def check_xss(page, flag, msg):
    """Execute the generated HTML in PhantomJS to validate XSS"""
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    base_url = os.environ.get('BASE_URL', 'http://localhost:5000')
    url = base_url + '/' + fn
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

    return result


@app.route('/projects/upload-example/', methods=['POST', 'GET'])
def upload_example_using_config():
    """
    Upload a label configuration example - vulnerable to reflected XSS.
    The label_config parameter is included in the response without proper sanitization.
    """
    if request.method == 'GET':
        return '''<!DOCTYPE html>
<html>
<head>
    <title>Label Studio - Upload Example</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
        .header { background: #1a73e8; padding: 20px; color: white; }
        .container { max-width: 800px; margin: 0 auto; padding: 20px; }
        .card { background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        textarea { width: 100%; height: 150px; font-family: monospace; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }
        .btn { background: #1a73e8; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
        .btn:hover { background: #1557b0; }
        .info { background: #e3f2fd; padding: 10px; border-radius: 4px; margin-bottom: 15px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Label Studio - Upload Example Configuration</h1>
    </div>
    <div class="container">
        <div class="card">
            <h2>Upload Label Configuration</h2>
            <div class="info">
                <strong>Info:</strong> Enter your XML label configuration below to preview the generated task data.
            </div>
            <form method="POST" action="/projects/upload-example/">
                <p><strong>Label Config (XML):</strong></p>
                <textarea name="label_config" placeholder='<View><Text name="text" value="$text"/></View>'></textarea>
                <br><br>
                <button type="submit" class="btn">Upload & Preview</button>
            </form>
        </div>
    </div>
</body>
</html>'''
    
    # POST request - process the label_config
    label_config = request.form.get('label_config', '')
    
    if not label_config:
        return jsonify({"error": "label_config is required"}), 400
    
    # Generate sample task data based on the config
    task_data = {
        "text": "Sample labeling text",
        "image": "/static/sample.jpg",
        "audio": "/static/sample.mp3"
    }
    
    task_json = json.dumps(task_data, indent=2)
    
    # Build response HTML that includes the user-controlled label_config
    # This is the XSS vulnerability - label_config is rendered without escaping
    response_template = '''<!DOCTYPE html>
<html>
<head>
    <title>Label Studio - Configuration Preview</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }}
        .header {{ background: #1a73e8; padding: 20px; color: white; }}
        .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
        .card {{ background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .success {{ background: #c8e6c9; padding: 10px; border-radius: 4px; margin-bottom: 15px; }}
        pre {{ background: #f4f4f4; padding: 15px; border-radius: 4px; overflow-x: auto; }}
        .config-preview {{ background: #fff3e0; padding: 15px; border-radius: 4px; border: 1px solid #ffcc80; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Label Studio - Configuration Preview</h1>
    </div>
    <div class="container">
        <div class="card">
            <div class="success">
                <strong>Success!</strong> Configuration uploaded and parsed.
            </div>
            <h2>Generated Task Data</h2>
            <pre>{task_json}</pre>
            
            <h2>Your Label Configuration</h2>
            <div class="config-preview">
                {label_config}
            </div>
            
            {result_section}
            
            <p><a href="/projects/upload-example/">Upload another configuration</a></p>
        </div>
    </div>
</body>
</html>'''
    
    # Build preview page with user input (vulnerable to XSS!)
    preview_page = response_template.format(
        task_json=task_json,
        label_config=label_config,  # Direct injection - no escaping!
        result_section=""
    )
    
    # Run XSS check with PhantomJS
    xss_result = check_xss(preview_page, flags[0], label_config)
    
    # Build result section based on XSS check
    result_section = ""
    if xss_result == 'XSS':
        result_section = '''<div style="background: #c8e6c9; padding: 15px; border-radius: 4px; margin-top: 20px;">
            <h3>Congratulations!</h3>
            <p>Flag: {}</p>
        </div>'''.format(flags[0])
    elif xss_result:
        result_section = '''<div style="background: #ffcdd2; padding: 15px; border-radius: 4px; margin-top: 20px;">
            <p>Alert triggered with message: {} (expected: "XSS")</p>
        </div>'''.format(cgi.escape(xss_result))
    
    # Return the final response with the result section
    final_response = response_template.format(
        task_json=task_json,
        label_config=label_config,  # Still vulnerable in final response
        result_section=result_section
    )
    
    return final_response


if __name__ == '__main__':
    app.run(debug=True)
