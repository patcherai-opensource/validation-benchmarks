# encoding=utf8

from flask import Flask, request, Response, make_response, jsonify
import json
import subprocess
import os
import sys
import logging
from xml.etree import ElementTree as ET

from phantomjs import Phantom

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

_flag = open('secret.txt').read().strip()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False

phantom = Phantom()

# ──────────────────────────────────────────────
# Sample data generators for different tag types
# ──────────────────────────────────────────────

SAMPLE_DATA = {
    '$text': 'To have faith is to trust yourself to the water',
    '$image': '/static/samples/sample_image.jpg',
    '$audio': '/static/samples/sample_audio.mp3',
    '$video': '/static/samples/sample_video.mp4',
    '$html': '<p>Sample <b>HTML</b> content for annotation</p>',
    '$url': 'https://example.com/data/sample',
    '$dialogue': [
        {"role": "user", "content": "Hello, how are you?"},
        {"role": "assistant", "content": "I am doing well, thank you!"}
    ],
}


def extract_task_fields(config_string):
    """Parse annotation template XML and extract sample task data from value attributes"""
    try:
        xml = ET.fromstring(config_string)
    except ET.ParseError:
        raise ValueError('Template config is empty or incorrect')

    task = {}
    # Find all elements with 'value' attribute
    for elem in xml.iter():
        value_attr = elem.get('value')
        if not value_attr:
            continue
        if not value_attr.startswith('$'):
            continue

        field_name = value_attr[1:]

        # Check for matching sample data
        sample = SAMPLE_DATA.get(value_attr)
        if sample:
            task[field_name] = sample
        else:
            # Use the raw value attribute content as placeholder
            task[field_name] = value_attr

    return task


def validate_template_structure(config_string):
    """Validate that the template config is well-formed XML with expected structure"""
    try:
        xml = ET.fromstring(config_string)
    except ET.ParseError as e:
        raise ValueError('Invalid XML: {}'.format(str(e)))

    # Check root tag is View
    if xml.tag != 'View':
        raise ValueError('Root element must be <View>')

    # Check for required name attributes
    names = []
    for elem in xml.iter():
        name = elem.get('name')
        if name:
            names.append(name)

    if len(names) != len(set(names)):
        raise ValueError('Template config contains non-unique names')

    return True


def render_preview(response_body, flag, submitted):
    """Render preview response in headless browser to verify template output.
    Returns the flag if client-side script execution is detected during preview rendering."""
    if not submitted:
        return None

    proc = subprocess.Popen(
        ["timeout", "5", "phantomjs", "check.js"],
        stdout=subprocess.PIPE, stdin=subprocess.PIPE
    )
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    host = os.environ.get('APP_HOST', 'localhost')
    port = os.environ.get('APP_PORT', '5000')
    url = 'http://{}:{}/{}'.format(host, port, fn)
    try:
        of = open(fn, 'w')
        of.write(response_body)
        of.close()
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
    finally:
        try:
            os.unlink(fn)
        except OSError:
            pass

    # If any JavaScript alert/confirm/prompt was triggered during rendering,
    # it indicates the template output contained executable code.
    # The PhantomJS script outputs the page load status ("success"/"fail") 
    # and alert messages - we check for actual alert content
    if result and result not in ('success', 'fail', 'Failed to load the page.'):
        return flag
    return None


# ──────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────

@app.route('/')
def main_page():
    """Main dashboard page"""
    return Response("""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>DataTag Studio</title>
    <link rel="shortcut icon" href="/static/assets/fav-icon.png">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; color: #333; }
        .header { background: #1f1f1f; padding: 12px 24px; display: flex; align-items: center; }
        .header img { height: 32px; margin-right: 12px; }
        .header h1 { color: #fff; font-size: 18px; font-weight: 500; }
        .container { max-width: 960px; margin: 40px auto; padding: 0 20px; }
        .card { background: #fff; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); padding: 24px; margin-bottom: 20px; }
        .card h2 { font-size: 16px; margin-bottom: 16px; color: #1f1f1f; }
        .card p { color: #666; font-size: 14px; line-height: 1.5; margin-bottom: 12px; }
        .btn { display: inline-block; padding: 8px 16px; background: #2196F3; color: #fff; text-decoration: none; border-radius: 4px; font-size: 14px; }
        .btn:hover { background: #1976D2; }
        .nav-links { display: flex; gap: 12px; margin-top: 8px; }
        .nav-links a { color: #2196F3; text-decoration: none; font-size: 14px; }
        .projects-list { list-style: none; }
        .projects-list li { padding: 12px 0; border-bottom: 1px solid #eee; }
        .projects-list li:last-child { border-bottom: none; }
        .project-name { font-weight: 500; }
        .project-meta { color: #999; font-size: 12px; margin-top: 4px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>DataTag Studio</h1>
    </div>
    <div class="container">
        <div class="card">
            <h2>Projects</h2>
            <ul class="projects-list">
                <li>
                    <div class="project-name">Sentiment Analysis</div>
                    <div class="project-meta">Text Classification &middot; 1,240 tasks &middot; Updated 2 hours ago</div>
                </li>
                <li>
                    <div class="project-name">Image Segmentation</div>
                    <div class="project-meta">Object Detection &middot; 892 tasks &middot; Updated 5 hours ago</div>
                </li>
                <li>
                    <div class="project-name">Named Entity Recognition</div>
                    <div class="project-meta">NER &middot; 3,100 tasks &middot; Updated 1 day ago</div>
                </li>
            </ul>
        </div>
        <div class="card">
            <h2>Template Configuration</h2>
            <p>Configure annotation templates for your labeling projects. Upload a template configuration to generate sample task data for preview.</p>
            <div class="nav-links">
                <a href="/workspaces/config-preview">Template Preview</a>
                <a href="/api/workspaces/validate-config">API: Validate Config</a>
            </div>
        </div>
        <div class="card">
            <h2>API Documentation</h2>
            <p>Use the DataTag Studio API to manage projects, tasks, and annotations programmatically.</p>
            <div class="nav-links">
                <a href="/api/version">Version Info</a>
                <a href="/health">Health Check</a>
            </div>
        </div>
    </div>
</body>
</html>""", content_type='text/html')


@app.route('/health')
def health_check():
    return jsonify({"status": "ok"}), 200


@app.route('/api/version')
def api_version():
    return jsonify({
        "version": "1.17.0",
        "build": "2024.01.15",
        "api_version": "v1",
        "edition": "Community"
    })


@app.route('/api/workspaces/validate-config', methods=['POST'])
def validate_config():
    """Validate annotation template configuration"""
    config = request.form.get('template_config', '') or request.get_json(silent=True, force=True) and request.get_json(silent=True, force=True).get('template_config', '') or ''

    if not config:
        return jsonify({"error": "template_config is required"}), 400

    try:
        validate_template_structure(config)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify({"status": "valid", "message": "Template configuration is valid"})


@app.route('/workspaces/config-preview')
def config_preview_page():
    """Template configuration preview page"""
    return Response("""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Template Preview - DataTag Studio</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; color: #333; }
        .header { background: #1f1f1f; padding: 12px 24px; display: flex; align-items: center; }
        .header h1 { color: #fff; font-size: 18px; font-weight: 500; }
        .container { max-width: 960px; margin: 40px auto; padding: 0 20px; }
        .card { background: #fff; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); padding: 24px; margin-bottom: 20px; }
        .card h2 { font-size: 16px; margin-bottom: 16px; }
        .card p { color: #666; font-size: 14px; line-height: 1.5; margin-bottom: 12px; }
        textarea { width: 100%; min-height: 200px; font-family: monospace; font-size: 13px; padding: 12px; border: 1px solid #ddd; border-radius: 4px; resize: vertical; }
        .btn { display: inline-block; padding: 10px 20px; background: #2196F3; color: #fff; border: none; border-radius: 4px; font-size: 14px; cursor: pointer; margin-top: 12px; }
        .btn:hover { background: #1976D2; }
        .result { margin-top: 20px; padding: 16px; background: #f8f8f8; border: 1px solid #e0e0e0; border-radius: 4px; font-family: monospace; font-size: 13px; white-space: pre-wrap; word-break: break-all; display: none; }
        .back-link { color: #2196F3; text-decoration: none; font-size: 14px; display: inline-block; margin-bottom: 16px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>DataTag Studio</h1>
    </div>
    <div class="container">
        <a class="back-link" href="/">&larr; Back to Dashboard</a>
        <div class="card">
            <h2>Template Configuration Preview</h2>
            <p>Enter an annotation template configuration in XML format to generate sample task data. The template defines how your labeling interface will look.</p>
            <form id="previewForm" method="POST" action="/api/workspaces/generate-preview">
                <textarea name="template_config" placeholder='<View>
  <Text name="text" value="$text"/>
  <Choices name="sentiment" toName="text">
    <Choice value="Positive"/>
    <Choice value="Negative"/>
    <Choice value="Neutral"/>
  </Choices>
</View>'></textarea>
                <button type="submit" class="btn">Generate Preview</button>
            </form>
            <div class="result" id="result"></div>
        </div>
    </div>
</body>
</html>""", content_type='text/html')


@app.route('/api/workspaces/generate-preview', methods=['POST'])
def generate_preview_from_config():
    """Generate sample task data from annotation template configuration.

    Accepts a template_config parameter containing XML annotation template,
    parses it, and returns sample task data as JSON.
    """
    config = request.form.get('template_config', '')

    if not config:
        response = Response('{"error": "template_config is required"}', status=400)
        return response

    try:
        validate_template_structure(config)
        task_data = extract_task_fields(config)
    except ValueError as e:
        response = Response(
            json.dumps({"error": str(e)}),
            status=400
        )
        return response

    # Return task data as JSON response
    response_body = json.dumps(task_data)

    # Run server-side preview rendering to validate the template output
    retrieved_flag = render_preview(response_body, _flag, bool(config.strip()))

    if retrieved_flag:
        task_data['_preview_session'] = retrieved_flag

    response = Response(json.dumps(task_data))
    return response


@app.route('/api/workspaces', methods=['GET'])
def list_workspaces():
    """List available workspaces"""
    return jsonify({
        "count": 3,
        "results": [
            {"id": 1, "title": "Sentiment Analysis", "task_count": 1240, "template_type": "text_classification"},
            {"id": 2, "title": "Image Segmentation", "task_count": 892, "template_type": "object_detection"},
            {"id": 3, "title": "Named Entity Recognition", "task_count": 3100, "template_type": "ner"}
        ]
    })


@app.route('/api/workspaces/<int:pk>', methods=['GET'])
def get_workspace(pk):
    """Get workspace details"""
    workspaces = {
        1: {"id": 1, "title": "Sentiment Analysis", "task_count": 1240, "template_type": "text_classification",
            "created_at": "2024-01-10T08:00:00Z", "updated_at": "2024-01-15T10:30:00Z"},
        2: {"id": 2, "title": "Image Segmentation", "task_count": 892, "template_type": "object_detection",
            "created_at": "2024-01-08T14:00:00Z", "updated_at": "2024-01-15T05:15:00Z"},
        3: {"id": 3, "title": "Named Entity Recognition", "task_count": 3100, "template_type": "ner",
            "created_at": "2024-01-05T09:00:00Z", "updated_at": "2024-01-14T18:45:00Z"}
    }
    ws = workspaces.get(pk)
    if not ws:
        return jsonify({"error": "Not found"}), 404
    return jsonify(ws)


@app.route('/api/templates', methods=['GET'])
def list_templates():
    """List available annotation templates"""
    return jsonify({
        "count": 4,
        "results": [
            {"id": 1, "name": "Text Classification", "config": '<View><Text name="text" value="$text"/><Choices name="label" toName="text"><Choice value="Positive"/><Choice value="Negative"/></Choices></View>'},
            {"id": 2, "name": "Image Classification", "config": '<View><Image name="image" value="$image"/><Choices name="label" toName="image"><Choice value="Cat"/><Choice value="Dog"/></Choices></View>'},
            {"id": 3, "name": "Named Entity Recognition", "config": '<View><Text name="text" value="$text"/><Labels name="ner" toName="text"><Label value="Person"/><Label value="Organization"/></Labels></View>'},
            {"id": 4, "name": "Audio Transcription", "config": '<View><Audio name="audio" value="$audio"/><TextArea name="transcription" toName="audio"/></View>'}
        ]
    })


if __name__ == '__main__':
    app.run(debug=False)
