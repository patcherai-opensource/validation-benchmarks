# encoding=utf8

from flask import Flask, request, Response, jsonify
import subprocess
import os
import json
import sys

try:
    import xml.etree.ElementTree as ET
except ImportError:
    import xml.etree.cElementTree as ET

from phantomjs import Phantom

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

secret_data = open('secret.txt').read().strip()

app = Flask(__name__)

phantom = Phantom()

# Data annotation platform configuration
ANNOTATION_TEMPLATES = {
    "sentiment": {
        "title": "Sentiment Analysis",
        "description": "Classify text sentiment as positive, negative, or neutral",
        "config": '<View><Text name="text" value="$text"/><Choices name="sentiment" toName="text"><Choice value="Positive"/><Choice value="Negative"/><Choice value="Neutral"/></Choices></View>'
    },
    "ner": {
        "title": "Named Entity Recognition",
        "description": "Label named entities in text passages",
        "config": '<View><Labels name="label" toName="text"><Label value="Person"/><Label value="Organization"/><Label value="Location"/></Labels><Text name="text" value="$text"/></View>'
    },
    "classification": {
        "title": "Image Classification",
        "description": "Classify images into categories",
        "config": '<View><Image name="image" value="$image"/><Choices name="choice" toName="image"><Choice value="Cat"/><Choice value="Dog"/></Choices></View>'
    }
}

SAMPLE_DATA = {
    "Text": "The quick brown fox jumps over the lazy dog.",
    "Image": "/static/samples/placeholder.png",
    "Audio": "/static/samples/placeholder.mp3",
    "Video": "/static/samples/placeholder.mp4",
    "HyperText": "<p>Sample HTML content for annotation.</p>",
    "Labels": "This is a sample text for labeling.",
    "Choices": "Sample text for classification.",
    "Default": "Sample data"
}


def parse_label_config(config_string):
    """Parse and validate an XML label config, returning structured tag info."""
    try:
        root = ET.fromstring(config_string)
    except ET.ParseError as e:
        raise ValueError("Invalid XML configuration: {}".format(str(e)))

    tags = {}
    for elem in root.iter():
        name = elem.get('name')
        if name:
            tags[name] = {
                'type': elem.tag,
                'value': elem.get('value', ''),
                'toName': elem.get('toName', ''),
                'attributes': dict(elem.attrib)
            }
    return tags


def validate_config_structure(config_string):
    """Validate that the config is well-formed XML with required structure."""
    try:
        root = ET.fromstring(config_string)
    except ET.ParseError as e:
        raise ValueError("XML parse error: {}".format(str(e)))

    # Must have a root View element
    if root.tag != 'View':
        raise ValueError("Root element must be 'View', got '{}'".format(root.tag))

    # Must have at least one named element
    names = []
    for elem in root.iter():
        n = elem.get('name')
        if n:
            names.append(n)
    if not names:
        raise ValueError("Config must contain at least one named element")

    # Check for unique names
    if len(set(names)) != len(names):
        raise ValueError("Config contains non-unique names")

    # Check toName references
    name_set = set(names)
    for elem in root.iter():
        to_name = elem.get('toName')
        if to_name and to_name not in name_set:
            raise ValueError("toName='{}' not found in config names".format(to_name))

    return True


def extract_task_data(config_string):
    """Extract sample task data from a label config.

    Parses the XML config and generates example data for each
    element that references a data variable via $variable syntax.
    """
    try:
        root = ET.fromstring(config_string)
    except ET.ParseError as e:
        raise ValueError("Invalid config: {}".format(str(e)))

    task = {}
    for elem in root.iter():
        value_attr = elem.get('value') or elem.get('valueList')
        if not value_attr:
            continue

        if value_attr.startswith('$'):
            key = value_attr[1:]
            tag_type = elem.tag

            # Map tag types to sample data
            if tag_type in SAMPLE_DATA:
                task[key] = SAMPLE_DATA[tag_type]
            elif tag_type.lower().endswith('labels'):
                task[key] = SAMPLE_DATA.get('Labels', 'Sample text')
            elif tag_type.lower() == 'choices':
                task[key] = SAMPLE_DATA.get('Choices', 'Sample text')
            else:
                task[key] = SAMPLE_DATA.get('Default', 'Sample data')
        else:
            # Non-variable values are treated as literal content
            key = elem.get('name')
            if key:
                task[key] = value_attr

    return task


@app.route('/')
def index():
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DataTag Studio</title>
    <link rel="shortcut icon" href="/static/assets/fav-icon.png">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, sans-serif; background: #f5f5f5; color: #333; }
        .header { background: #2c3e50; color: white; padding: 20px 40px; display: flex; align-items: center; justify-content: space-between; }
        .header h1 { font-size: 24px; font-weight: 600; }
        .header nav a { color: #ecf0f1; text-decoration: none; margin-left: 24px; font-size: 14px; }
        .header nav a:hover { color: #3498db; }
        .container { max-width: 1200px; margin: 0 auto; padding: 40px 20px; }
        .hero { text-align: center; margin-bottom: 48px; }
        .hero h2 { font-size: 32px; margin-bottom: 12px; color: #2c3e50; }
        .hero p { font-size: 16px; color: #7f8c8d; max-width: 600px; margin: 0 auto; }
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 24px; }
        .card { background: white; border-radius: 8px; padding: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); transition: transform 0.2s; }
        .card:hover { transform: translateY(-2px); box-shadow: 0 4px 16px rgba(0,0,0,0.12); }
        .card h3 { font-size: 18px; margin-bottom: 8px; color: #2c3e50; }
        .card p { font-size: 14px; color: #7f8c8d; margin-bottom: 16px; }
        .card a { color: #3498db; text-decoration: none; font-size: 14px; font-weight: 500; }
        .card a:hover { text-decoration: underline; }
        .footer { text-align: center; padding: 24px; color: #95a5a6; font-size: 12px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>DataTag Studio</h1>
        <nav>
            <a href="/">Projects</a>
            <a href="/api/templates/">Templates</a>
            <a href="/projects/config-editor">Config Editor</a>
        </nav>
    </div>
    <div class="container">
        <div class="hero">
            <h2>Data Annotation Platform</h2>
            <p>Create and manage annotation projects for machine learning datasets. Define labeling interfaces and generate sample tasks.</p>
        </div>
        <div class="grid">
            <div class="card">
                <h3>Annotation Templates</h3>
                <p>Browse pre-built templates for common annotation tasks including NER, sentiment analysis, and image classification.</p>
                <a href="/api/templates/">View Templates &rarr;</a>
            </div>
            <div class="card">
                <h3>Config Editor</h3>
                <p>Design custom labeling interfaces using XML configuration. Preview sample tasks generated from your config.</p>
                <a href="/projects/config-editor">Open Editor &rarr;</a>
            </div>
            <div class="card">
                <h3>API Documentation</h3>
                <p>Use the REST API to programmatically manage projects, validate configs, and generate sample data.</p>
                <a href="/api/docs/">API Reference &rarr;</a>
            </div>
        </div>
    </div>
    <div class="footer">DataTag Studio v2.14.0</div>
</body>
</html>"""


@app.route('/api/templates/')
def template_list():
    """List available annotation templates."""
    templates = []
    for key, tmpl in ANNOTATION_TEMPLATES.items():
        templates.append({
            'id': key,
            'title': tmpl['title'],
            'description': tmpl['description']
        })
    return jsonify(templates)


@app.route('/api/templates/<template_id>')
def template_detail(template_id):
    """Get a specific template with its config."""
    if template_id not in ANNOTATION_TEMPLATES:
        return jsonify({'error': 'Template not found'}), 404
    tmpl = ANNOTATION_TEMPLATES[template_id]
    return jsonify({
        'id': template_id,
        'title': tmpl['title'],
        'description': tmpl['description'],
        'label_config': tmpl['config']
    })


@app.route('/api/projects/validate/', methods=['POST'])
def validate_config():
    """Validate a label configuration."""
    config = request.form.get('label_config', '')
    if not config and request.content_type and 'json' in request.content_type:
        try:
            data = request.get_json(force=True) or {}
            config = data.get('label_config', '')
        except Exception:
            config = ''
    if not config:
        return jsonify({'error': 'label_config is required'}), 400

    try:
        validate_config_structure(config)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    return jsonify({'status': 'valid', 'message': 'Configuration is valid'})


@app.route('/projects/config-editor')
def config_editor():
    """Interactive config editor page."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Config Editor - DataTag Studio</title>
    <link rel="shortcut icon" href="/static/assets/fav-icon.png">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, sans-serif; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 16px 40px; display: flex; align-items: center; justify-content: space-between; }
        .header h1 { font-size: 20px; }
        .header a { color: #ecf0f1; text-decoration: none; font-size: 14px; }
        .editor-container { display: flex; height: calc(100vh - 56px); }
        .editor-panel { flex: 1; padding: 20px; display: flex; flex-direction: column; }
        .editor-panel h3 { margin-bottom: 12px; color: #2c3e50; font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px; }
        textarea { flex: 1; width: 100%; font-family: 'Monaco', 'Menlo', monospace; font-size: 13px; padding: 16px; border: 1px solid #ddd; border-radius: 4px; resize: none; background: #fafafa; }
        .preview-panel { flex: 1; padding: 20px; background: white; border-left: 1px solid #e0e0e0; overflow: auto; }
        .btn { background: #3498db; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; font-size: 14px; margin-top: 12px; }
        .btn:hover { background: #2980b9; }
        .btn-secondary { background: #95a5a6; }
        .btn-secondary:hover { background: #7f8c8d; }
        .btn-group { display: flex; gap: 8px; }
        #preview-output { padding: 16px; background: #fafafa; border-radius: 4px; border: 1px solid #eee; min-height: 200px; font-family: monospace; font-size: 13px; white-space: pre-wrap; word-wrap: break-word; }
        .status { padding: 8px 0; font-size: 13px; }
        .status.valid { color: #27ae60; }
        .status.error { color: #e74c3c; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Config Editor</h1>
        <a href="/">&larr; Back to Projects</a>
    </div>
    <div class="editor-container">
        <div class="editor-panel">
            <h3>Label Configuration (XML)</h3>
            <textarea id="config-input" placeholder="Enter your XML label configuration...">&lt;View&gt;
  &lt;Text name="text" value="$text"/&gt;
  &lt;Choices name="sentiment" toName="text"&gt;
    &lt;Choice value="Positive"/&gt;
    &lt;Choice value="Negative"/&gt;
    &lt;Choice value="Neutral"/&gt;
  &lt;/Choices&gt;
&lt;/View&gt;</textarea>
            <div class="btn-group">
                <button class="btn" onclick="previewConfig()">Generate Preview</button>
                <button class="btn btn-secondary" onclick="validateConfig()">Validate</button>
            </div>
            <div id="status" class="status"></div>
        </div>
        <div class="preview-panel">
            <h3>Sample Task Data</h3>
            <div id="preview-output">Click "Generate Preview" to see sample task data generated from your configuration.</div>
        </div>
    </div>
    <script>
        function previewConfig() {
            var config = document.getElementById('config-input').value;
            var formData = new FormData();
            formData.append('label_config', config);

            fetch('/projects/preview-config/', {
                method: 'POST',
                body: formData
            })
            .then(function(response) { return response.text(); })
            .then(function(data) {
                document.getElementById('preview-output').textContent = data;
                document.getElementById('status').className = 'status valid';
                document.getElementById('status').textContent = 'Preview generated successfully';
            })
            .catch(function(error) {
                document.getElementById('status').className = 'status error';
                document.getElementById('status').textContent = 'Error: ' + error;
            });
        }

        function validateConfig() {
            var config = document.getElementById('config-input').value;
            var formData = new FormData();
            formData.append('label_config', config);

            fetch('/api/projects/validate/', {
                method: 'POST',
                body: formData
            })
            .then(function(response) { return response.json(); })
            .then(function(data) {
                if (data.status === 'valid') {
                    document.getElementById('status').className = 'status valid';
                    document.getElementById('status').textContent = data.message;
                } else {
                    document.getElementById('status').className = 'status error';
                    document.getElementById('status').textContent = data.error;
                }
            })
            .catch(function(error) {
                document.getElementById('status').className = 'status error';
                document.getElementById('status').textContent = 'Error: ' + error;
            });
        }
    </script>
</body>
</html>"""


@app.route('/projects/preview-config/', methods=['POST'])
def preview_config_handler():
    """Generate sample task data from a label configuration.

    Accepts a POST request with 'label_config' parameter containing XML configuration.
    Returns JSON with generated sample task data for previewing the annotation interface.
    """
    config = request.form.get('label_config', '')
    if not config:
        return Response('label_config parameter is required', status=400)

    try:
        validate_config_structure(config)
        task_data = extract_task_data(config)
    except (ValueError, ET.ParseError) as e:
        return Response('error while generating preview', status=400)

    response = Response(json.dumps(task_data))
    return response


@app.route('/projects/render-preview/', methods=['POST'])
def render_preview():
    """Render preview of generated task data in the browser context.

    This endpoint generates sample task data from the provided config and
    renders it server-side for preview purposes, checking the output.
    """
    config = request.form.get('label_config', '')
    if not config:
        return jsonify({'error': 'label_config parameter is required'}), 400

    try:
        validate_config_structure(config)
        task_data = extract_task_data(config)
    except (ValueError, ET.ParseError) as e:
        return jsonify({'error': 'Invalid configuration'}), 400

    # Generate HTML preview containing the task data
    task_json = json.dumps(task_data)
    preview_html = """<!DOCTYPE html>
<html>
<head><title>Task Preview</title></head>
<body>
<div id="task-data">{}</div>
</body>
</html>""".format(task_json)

    # Use headless browser to render the preview and check output
    result = render_with_browser(preview_html)

    if result == 'XSS':
        return Response(
            json.dumps({'status': 'preview_complete', 'result': secret_data}),
            content_type='application/json'
        )
    elif result:
        return jsonify({'status': 'preview_rendered', 'output': result})
    else:
        return jsonify({'status': 'preview_rendered', 'task_data': task_data})


def render_with_browser(html_content):
    """Render HTML content in headless browser for preview verification."""
    proc = subprocess.Popen(
        ["timeout", "5", "phantomjs", "check.js"],
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE
    )
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://127.0.0.1:5000/' + fn
    try:
        of = open(fn, 'w')
        of.write(html_content)
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


@app.route('/api/docs/')
def api_docs():
    """API documentation page."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>API Documentation - DataTag Studio</title>
    <link rel="shortcut icon" href="/static/assets/fav-icon.png">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 16px 40px; }
        .header h1 { font-size: 20px; }
        .container { max-width: 900px; margin: 0 auto; padding: 40px 20px; }
        .endpoint { background: white; border-radius: 8px; padding: 24px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
        .method { display: inline-block; padding: 4px 10px; border-radius: 4px; font-size: 12px; font-weight: 700; color: white; margin-right: 8px; }
        .method.get { background: #27ae60; }
        .method.post { background: #3498db; }
        .path { font-family: monospace; font-size: 15px; font-weight: 600; }
        .endpoint p { margin-top: 12px; color: #555; font-size: 14px; line-height: 1.5; }
        .params { margin-top: 16px; }
        .params h4 { font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px; color: #7f8c8d; margin-bottom: 8px; }
        .param { padding: 8px 12px; background: #f8f9fa; border-radius: 4px; margin-bottom: 4px; font-size: 13px; }
        .param code { font-weight: 600; }
        h2 { font-size: 22px; color: #2c3e50; margin-bottom: 24px; }
        a { color: #3498db; }
    </style>
</head>
<body>
    <div class="header">
        <h1><a href="/" style="color:white;text-decoration:none">&larr;</a> API Documentation</h1>
    </div>
    <div class="container">
        <h2>REST API Endpoints</h2>

        <div class="endpoint">
            <span class="method get">GET</span>
            <span class="path">/api/templates/</span>
            <p>List all available annotation templates.</p>
        </div>

        <div class="endpoint">
            <span class="method get">GET</span>
            <span class="path">/api/templates/{template_id}</span>
            <p>Get a specific template with its XML label configuration.</p>
        </div>

        <div class="endpoint">
            <span class="method post">POST</span>
            <span class="path">/api/projects/validate/</span>
            <p>Validate a label configuration for structural correctness.</p>
            <div class="params">
                <h4>Parameters</h4>
                <div class="param"><code>label_config</code> (string, required) - XML label configuration to validate</div>
            </div>
        </div>

        <div class="endpoint">
            <span class="method post">POST</span>
            <span class="path">/projects/preview-config/</span>
            <p>Generate sample task data from a label configuration. Returns JSON with example data for each variable referenced in the config.</p>
            <div class="params">
                <h4>Parameters</h4>
                <div class="param"><code>label_config</code> (string, required) - XML label configuration</div>
            </div>
        </div>

        <div class="endpoint">
            <span class="method post">POST</span>
            <span class="path">/projects/render-preview/</span>
            <p>Generate and render a preview of sample task data in a browser context. Returns the rendered output for verification.</p>
            <div class="params">
                <h4>Parameters</h4>
                <div class="param"><code>label_config</code> (string, required) - XML label configuration</div>
            </div>
        </div>
    </div>
</body>
</html>"""


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
