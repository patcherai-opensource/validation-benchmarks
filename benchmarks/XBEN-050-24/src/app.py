# encoding=utf8

from flask import Flask, request, Response, jsonify
import subprocess
import os
import json
import sys
import xml.etree.ElementTree as ET
import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flags = open('secret.txt').read().strip()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False

DATA_EXAMPLES = {
    "text": "To have faith is to trust yourself to the water",
    "image": "/static/samples/image.jpg",
    "audio": "/static/samples/audio.mp3",
    "html": "<p>Sample HTML content for annotation</p>",
    "url": "https://example.com/resource",
    "video": "/static/samples/video.mp4",
}


def parse_workspace_config(config_string):
    """Parse and validate workspace XML configuration"""
    if not config_string or not config_string.strip():
        raise ValueError("Configuration is empty")
    try:
        xml = ET.fromstring(config_string.encode('utf-8') if isinstance(config_string, unicode) else config_string)
    except ET.ParseError as e:
        raise ValueError("Invalid XML: {}".format(str(e)))
    return xml


def validate_workspace_config(config_string):
    """Validate the workspace configuration structure"""
    xml = parse_workspace_config(config_string)
    if xml.tag not in ('View', 'Config', 'Layout'):
        raise ValueError("Root element must be View, Config, or Layout")
    return xml


def extract_task_fields(config_string):
    """Extract sample task data from workspace configuration.
    Parses XML elements with value attributes and generates sample data."""
    xml = validate_workspace_config(config_string)

    task = {}
    parent = xml.findall('.//*[@value]')
    for p in parent:
        value = p.get('value', '')
        if not value or not value.startswith('$'):
            continue
        field_name = value[1:]

        tag_name = p.tag.lower()
        if tag_name in ('text', 'textarea'):
            task[field_name] = DATA_EXAMPLES.get('text', 'Sample text data')
        elif tag_name in ('image', 'img'):
            task[field_name] = DATA_EXAMPLES.get('image', '/static/samples/image.jpg')
        elif tag_name in ('audio', 'audiosource'):
            task[field_name] = DATA_EXAMPLES.get('audio', '/static/samples/audio.mp3')
        elif tag_name in ('hypertext', 'htmlview'):
            task[field_name] = DATA_EXAMPLES.get('html', '<p>Sample</p>')
        elif tag_name in ('video', 'videoplayer'):
            task[field_name] = DATA_EXAMPLES.get('video', '/static/samples/video.mp4')
        elif tag_name.endswith('labels'):
            task[field_name] = ["label_1", "label_2", "label_3"]
        elif tag_name == 'choices':
            task[field_name] = "choice_1"
        else:
            task[field_name] = value

    return task


def verify_alert(page_content):
    """Use headless browser to check if content triggers script execution"""
    proc = subprocess.Popen(
        ["timeout", "8", "phantomjs", "check.js"],
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE
    )
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    base_url = os.getenv('BASE_URL', 'http://localhost:5000')
    url = base_url + '/' + fn
    result = ''
    try:
        of = open(fn, 'w')
        of.write(page_content)
        of.close()
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
    except Exception:
        pass
    finally:
        try:
            os.unlink(fn)
        except OSError:
            pass
    return result


@app.route('/')
def index():
    return '''<!DOCTYPE html>
<html>
<head>
    <title>DataTag Studio</title>
    <link rel="shortcut icon" href="/static/assets/fav-icon.png">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f5f5f5; }
        .header { background: #1a1a2e; padding: 16px 24px; color: white; display: flex; align-items: center; }
        .header h1 { font-size: 20px; font-weight: 600; }
        .header .version { font-size: 12px; color: #888; margin-left: 8px; }
        .nav { background: #16213e; padding: 0 24px; display: flex; gap: 0; }
        .nav a { color: #ccc; padding: 12px 16px; text-decoration: none; font-size: 14px; border-bottom: 2px solid transparent; }
        .nav a:hover { color: white; background: rgba(255,255,255,0.05); }
        .nav a.active { color: white; border-bottom-color: #4361ee; }
        .container { max-width: 1200px; margin: 32px auto; padding: 0 24px; }
        .card { background: white; border-radius: 8px; padding: 24px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .card h2 { font-size: 18px; margin-bottom: 12px; color: #333; }
        .card p { color: #666; font-size: 14px; line-height: 1.6; }
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 16px; }
        .btn { display: inline-block; padding: 8px 16px; background: #4361ee; color: white; border-radius: 4px; text-decoration: none; font-size: 14px; }
        .btn:hover { background: #3a56d4; }
        .stats { display: flex; gap: 24px; margin-top: 16px; }
        .stat { text-align: center; }
        .stat .number { font-size: 24px; font-weight: 700; color: #4361ee; }
        .stat .label { font-size: 12px; color: #888; margin-top: 4px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>DataTag Studio</h1>
        <span class="version">v1.17.1</span>
    </div>
    <div class="nav">
        <a href="/" class="active">Workspaces</a>
        <a href="/workspace/list">All Projects</a>
        <a href="/workspace/templates">Templates</a>
        <a href="/settings">Settings</a>
    </div>
    <div class="container">
        <div class="card">
            <h2>Welcome to DataTag Studio</h2>
            <p>DataTag Studio is a configurable data annotation platform. Create workspaces, define labeling configurations, and manage your annotation projects.</p>
            <div class="stats">
                <div class="stat"><div class="number">3</div><div class="label">Workspaces</div></div>
                <div class="stat"><div class="number">142</div><div class="label">Tasks</div></div>
                <div class="stat"><div class="number">89</div><div class="label">Completed</div></div>
            </div>
        </div>
        <div class="grid">
            <div class="card">
                <h2>Text Classification</h2>
                <p>Sentiment analysis project with 50 tasks remaining.</p>
                <br><a class="btn" href="/workspace/1/overview">Open</a>
            </div>
            <div class="card">
                <h2>Image Labeling</h2>
                <p>Object detection workspace - 32 tasks remaining.</p>
                <br><a class="btn" href="/workspace/2/overview">Open</a>
            </div>
            <div class="card">
                <h2>NER Annotation</h2>
                <p>Named entity recognition - 60 tasks remaining.</p>
                <br><a class="btn" href="/workspace/3/overview">Open</a>
            </div>
        </div>
    </div>
</body>
</html>'''


@app.route('/workspace/list')
def workspace_list():
    return jsonify({
        "count": 3,
        "results": [
            {"id": 1, "title": "Text Classification", "task_count": 50, "created_at": "2024-01-15T10:30:00Z"},
            {"id": 2, "title": "Image Labeling", "task_count": 32, "created_at": "2024-02-01T14:20:00Z"},
            {"id": 3, "title": "NER Annotation", "task_count": 60, "created_at": "2024-02-10T09:15:00Z"},
        ]
    })


@app.route('/workspace/<int:pk>/overview')
def workspace_overview(pk):
    titles = {1: "Text Classification", 2: "Image Labeling", 3: "NER Annotation"}
    title = titles.get(pk, "Unknown Workspace")
    return '''<!DOCTYPE html>
<html>
<head>
    <title>{title} - DataTag Studio</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f5f5f5; }}
        .header {{ background: #1a1a2e; padding: 16px 24px; color: white; }}
        .header h1 {{ font-size: 20px; }}
        .nav {{ background: #16213e; padding: 0 24px; display: flex; gap: 0; }}
        .nav a {{ color: #ccc; padding: 12px 16px; text-decoration: none; font-size: 14px; border-bottom: 2px solid transparent; }}
        .nav a:hover {{ color: white; }}
        .nav a.active {{ color: white; border-bottom-color: #4361ee; }}
        .container {{ max-width: 1200px; margin: 32px auto; padding: 0 24px; }}
        .card {{ background: white; border-radius: 8px; padding: 24px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        .card h2 {{ margin-bottom: 12px; }}
        .card p {{ color: #666; font-size: 14px; }}
        .btn {{ display: inline-block; padding: 8px 16px; background: #4361ee; color: white; border-radius: 4px; text-decoration: none; font-size: 14px; }}
    </style>
</head>
<body>
    <div class="header"><h1>DataTag Studio</h1></div>
    <div class="nav">
        <a href="/">Workspaces</a>
        <a href="/workspace/{pk}/overview" class="active">Overview</a>
        <a href="/workspace/{pk}/settings">Settings</a>
    </div>
    <div class="container">
        <div class="card">
            <h2>{title}</h2>
            <p>Workspace ID: {pk}</p>
            <p>Configure labeling tasks and manage annotations for this workspace.</p>
        </div>
        <div class="card">
            <h2>Configuration</h2>
            <p>Define your labeling interface using XML configuration. Use the <a href="/workspace/templates">template gallery</a> or the <a href="/workspace/preview-config">configuration preview tool</a> to test your setup.</p>
        </div>
    </div>
</body>
</html>'''.format(title=title, pk=pk)


@app.route('/workspace/<int:pk>/settings')
def workspace_settings(pk):
    return jsonify({
        "id": pk,
        "label_config": "<View><Text name=\"text\" value=\"$text\"/></View>",
        "instruction": "Label the text according to the guidelines.",
        "show_skip_button": True,
        "show_annotation_history": True,
    })


@app.route('/workspace/templates')
def workspace_templates():
    return jsonify({
        "templates": [
            {"id": 1, "name": "Text Classification", "config": "<View><Text name=\"text\" value=\"$text\"/><Choices name=\"sentiment\" toName=\"text\"><Choice value=\"Positive\"/><Choice value=\"Negative\"/></Choices></View>"},
            {"id": 2, "name": "Named Entity Recognition", "config": "<View><Text name=\"text\" value=\"$text\"/><Labels name=\"label\" toName=\"text\"><Label value=\"PER\"/><Label value=\"ORG\"/><Label value=\"LOC\"/></Labels></View>"},
            {"id": 3, "name": "Image Classification", "config": "<View><Image name=\"image\" value=\"$image\"/><Choices name=\"choice\" toName=\"image\"><Choice value=\"Cat\"/><Choice value=\"Dog\"/></Choices></View>"},
        ]
    })


@app.route('/api/workspace/validate', methods=['POST'])
def validate_config():
    """Validate workspace labeling configuration"""
    config = request.form.get('label_config', '')
    if not config:
        try:
            body = request.get_json(silent=True, force=True)
            if body:
                config = body.get('label_config', '')
        except Exception:
            pass
    if not config:
        return jsonify({"error": "label_config is required"}), 400
    try:
        validate_workspace_config(config)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify({"status": "valid"})


@app.route('/workspace/preview-config', methods=['GET', 'POST'])
def preview_config():
    """Generate sample task data from workspace configuration.

    For GET requests, returns the configuration preview interface.
    For POST requests, processes the label_config parameter and returns
    generated sample task data for the editor preview.
    """
    if request.method == 'GET':
        return '''<!DOCTYPE html>
<html>
<head>
    <title>Configuration Preview - DataTag Studio</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f5f5f5; }
        .header { background: #1a1a2e; padding: 16px 24px; color: white; }
        .header h1 { font-size: 20px; }
        .nav { background: #16213e; padding: 0 24px; display: flex; gap: 0; }
        .nav a { color: #ccc; padding: 12px 16px; text-decoration: none; font-size: 14px; }
        .nav a:hover { color: white; }
        .container { max-width: 900px; margin: 32px auto; padding: 0 24px; }
        .card { background: white; border-radius: 8px; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .card h2 { margin-bottom: 16px; font-size: 18px; }
        textarea { width: 100%; height: 200px; font-family: monospace; font-size: 13px; padding: 12px; border: 1px solid #ddd; border-radius: 4px; resize: vertical; }
        .btn { display: inline-block; padding: 10px 20px; background: #4361ee; color: white; border: none; border-radius: 4px; font-size: 14px; cursor: pointer; margin-top: 12px; }
        .btn:hover { background: #3a56d4; }
        .help { font-size: 13px; color: #888; margin-top: 8px; }
    </style>
</head>
<body>
    <div class="header"><h1>DataTag Studio</h1></div>
    <div class="nav">
        <a href="/">Workspaces</a>
        <a href="/workspace/templates">Templates</a>
    </div>
    <div class="container">
        <div class="card">
            <h2>Configuration Preview</h2>
            <p style="color:#666;margin-bottom:16px;">Paste your labeling XML configuration to preview sample task data that will be generated for your annotators.</p>
            <form method="POST" action="/workspace/preview-config">
                <textarea name="label_config" placeholder="<View>&#10;  <Text name=&quot;text&quot; value=&quot;$text&quot;/>&#10;  <Choices name=&quot;sentiment&quot; toName=&quot;text&quot;>&#10;    <Choice value=&quot;Positive&quot;/>&#10;    <Choice value=&quot;Negative&quot;/>&#10;  </Choices>&#10;</View>"></textarea>
                <div class="help">Define data fields using $variable syntax in value attributes. Supported tags: Text, Image, Audio, HyperText, Video, Labels, Choices.</div>
                <button type="submit" class="btn">Preview Task Data</button>
            </form>
        </div>
    </div>
</body>
</html>'''

    config = request.form.get('label_config', '')
    if not config:
        return Response('{"error": "label_config parameter is required"}', status=400)

    try:
        validate_workspace_config(config)
        task_data = extract_task_fields(config)
    except (ValueError, ET.ParseError) as e:
        return Response(
            'error generating preview: {}'.format(str(e)),
            status=400
        )

    response_body = json.dumps(task_data)

    result = verify_alert(response_body)
    if result and result not in ('success', 'fail', ''):
        response_body = json.dumps({"task_data": task_data, "security_token": flags})

    response = Response(response_body)
    return response


@app.route('/settings')
def settings_page():
    return jsonify({
        "hostname": request.host,
        "version": "1.17.1",
        "features": {
            "annotation_history": True,
            "skip_queue": True,
            "review_mode": True,
        }
    })


@app.route('/api/health')
def health():
    return jsonify({"status": "ok"})


@app.route('/ping')
def ping():
    return 'pong'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
