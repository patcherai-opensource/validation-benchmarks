# encoding=utf8

from flask import Flask, request, make_response, jsonify
import subprocess
import os
import json
import sys
import xml.etree.ElementTree as ET

from phantomjs import Phantom

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flag = open('secret.txt').read().strip()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

phantom = Phantom()

# Label Studio-style project templates
TEMPLATES = [
    {
        "id": 1,
        "title": "Image Classification",
        "group": "Computer Vision",
        "config": '<View><Image name="image" value="$image"/><Choices name="choice" toName="image"><Choice value="Cat"/><Choice value="Dog"/></Choices></View>'
    },
    {
        "id": 2,
        "title": "Text Classification",
        "group": "Natural Language Processing",
        "config": '<View><Text name="text" value="$text"/><Choices name="sentiment" toName="text"><Choice value="Positive"/><Choice value="Negative"/><Choice value="Neutral"/></Choices></View>'
    },
    {
        "id": 3,
        "title": "Named Entity Recognition",
        "group": "Natural Language Processing",
        "config": '<View><Text name="text" value="$text"/><Labels name="label" toName="text"><Label value="Person"/><Label value="Organization"/><Label value="Location"/></Labels></View>'
    },
    {
        "id": 4,
        "title": "Audio Transcription",
        "group": "Audio/Speech Processing",
        "config": '<View><Audio name="audio" value="$audio"/><TextArea name="transcription" toName="audio" rows="4"/></View>'
    }
]

# Sample data mappings - keyed by $variable name and by tag type
DATA_EXAMPLES = {
    # By variable name
    "$image": "/static/samples/kittens.jpg",
    "$audio": "/static/samples/audio.mp3",
    "$video": "/static/samples/video.mp4",
    "$text": "To have faith is to trust yourself to the water",
    "$html": "<p>This is a <b>sample</b> paragraph for annotation.</p>",
    "$csv": "/static/samples/time-series.csv",
    # By tag type (fallback)
    "Image": "/static/samples/kittens.jpg",
    "Audio": "/static/samples/audio.mp3",
    "Video": "/static/samples/video.mp4",
    "Text": "To have faith is to trust yourself to the water",
    "HyperText": "<p>This is a <b>sample</b> paragraph for annotation.</p>",
    "TimeSeries": "/static/samples/time-series.csv",
    "Table": "/static/samples/table.csv"
}


def generate_sample_task_without_check(config_string, mode='upload', secure_mode=False):
    """Generate sample task from label config XML"""
    try:
        root = ET.fromstring(config_string)
    except ET.ParseError as e:
        raise ValueError("Invalid XML: {}".format(str(e)))

    task = {}
    # iterate over xml tree and find elements with 'value' attribute
    for elem in root.iter():
        value = elem.get('value') or elem.get('valueList')
        if not value or not value.startswith('$'):
            continue

        # Extract data placeholder key (strip the $ prefix)
        value = value[1:]

        # detect secured mode - objects served as URLs
        value_type = elem.get('valueType') or elem.get('valuetype')
        only_urls = secure_mode or value_type == 'url'

        # Try to get example by variable name
        example_from_field_name = DATA_EXAMPLES.get('$' + value)
        if example_from_field_name:
            task[value] = example_from_field_name
        else:
            # Not found by name, try to get example by tag type
            example_value = DATA_EXAMPLES.get(elem.tag, 'Something')
            task[value] = example_value

    return task


def get_task_from_labeling_config(config):
    """Get task data from labeling config comment"""
    task_data = {}
    start = config.find('<!-- {')
    if start < 0:
        start = config.find('<!--{')
    if start >= 0:
        start += 4
        end = config[start:].find('-->')
        if end > 0:
            try:
                body = json.loads(config[start:start + end])
                task_data = body.get('data', body)
            except:
                pass
    return task_data


def get_sample_task(config_string, secure_mode=False):
    """Get sample task from labeling config and combine with generated sample task"""
    predefined_task = get_task_from_labeling_config(config_string)
    generated_task = generate_sample_task_without_check(config_string, mode='upload', secure_mode=secure_mode)
    if predefined_task:
        generated_task.update(predefined_task)
    return generated_task


def validate_label_config(config_string):
    """Validate structural correctness of label config XML"""
    if not config_string or not config_string.strip():
        raise ValueError("Label config is empty")

    try:
        root = ET.fromstring(config_string)
    except ET.ParseError as e:
        raise ValueError("Invalid XML: {}".format(str(e)))

    if root.tag not in ('View', 'Relations', 'Choices', 'Labels'):
        # Structural validation only - check that it has a valid root element
        pass

    return True


def check_xss_response(response_body, flag_value):
    """Check if XSS executes in the given response using headless browser"""
    proc = subprocess.Popen(
        ["timeout", "5", "phantomjs", "check.js"],
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE
    )
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    base_url = os.getenv('BASE_URL', 'http://localhost:5000')
    url = base_url + '/' + fn
    result = ''
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
        except:
            pass

    return result


# ---- Application Routes ----

INDEX_PAGE = """<!DOCTYPE html>
<html>
<head>
    <title>Label Studio</title>
    <link rel="shortcut icon" href="/static/favicon.ico">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }
        .header { background: #2196F3; color: white; padding: 16px 32px; display: flex; align-items: center; justify-content: space-between; }
        .header h1 { font-size: 20px; font-weight: 500; }
        .header nav a { color: white; text-decoration: none; margin-left: 24px; font-size: 14px; }
        .container { max-width: 1200px; margin: 32px auto; padding: 0 16px; }
        .card { background: white; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.12); padding: 24px; margin-bottom: 24px; }
        .card h2 { font-size: 18px; margin-bottom: 16px; color: #333; }
        .card p { color: #666; line-height: 1.6; }
        .btn { display: inline-block; padding: 8px 16px; background: #2196F3; color: white; text-decoration: none; border-radius: 4px; font-size: 14px; border: none; cursor: pointer; }
        .btn:hover { background: #1976D2; }
        .project-list { list-style: none; }
        .project-list li { padding: 12px 0; border-bottom: 1px solid #eee; }
        .project-list li:last-child { border-bottom: none; }
        .project-list a { color: #2196F3; text-decoration: none; font-weight: 500; }
        .footer { text-align: center; padding: 32px; color: #999; font-size: 12px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Label Studio</h1>
        <nav>
            <a href="/projects/">Projects</a>
            <a href="/api/templates/">Templates</a>
            <a href="/api/version">API</a>
        </nav>
    </div>
    <div class="container">
        <div class="card">
            <h2>Welcome to Label Studio</h2>
            <p>The most flexible data labeling tool. Create labeling projects, configure labeling interfaces, and manage your annotation workflows.</p>
        </div>
        <div class="card">
            <h2>Quick Start</h2>
            <p>Create a new project or browse existing templates to get started with data labeling.</p>
            <br>
            <a href="/projects/" class="btn">View Projects</a>
        </div>
    </div>
    <div class="footer">Label Studio Community Edition</div>
</body>
</html>"""


@app.route('/')
def index():
    return INDEX_PAGE


@app.route('/projects/')
def project_list():
    return """<!DOCTYPE html>
<html>
<head>
    <title>Projects - Label Studio</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }
        .header { background: #2196F3; color: white; padding: 16px 32px; display: flex; align-items: center; justify-content: space-between; }
        .header h1 { font-size: 20px; font-weight: 500; }
        .header nav a { color: white; text-decoration: none; margin-left: 24px; font-size: 14px; }
        .container { max-width: 1200px; margin: 32px auto; padding: 0 16px; }
        .card { background: white; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.12); padding: 24px; margin-bottom: 16px; }
        .project-card { display: flex; justify-content: space-between; align-items: center; }
        .project-card h3 { font-size: 16px; color: #333; }
        .project-card .meta { color: #999; font-size: 13px; }
        .btn { display: inline-block; padding: 8px 16px; background: #2196F3; color: white; text-decoration: none; border-radius: 4px; font-size: 14px; }
        .section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
        .section-header h2 { font-size: 22px; color: #333; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Label Studio</h1>
        <nav>
            <a href="/">Home</a>
            <a href="/projects/">Projects</a>
            <a href="/api/templates/">Templates</a>
        </nav>
    </div>
    <div class="container">
        <div class="section-header">
            <h2>Projects</h2>
        </div>
        <div class="card">
            <div class="project-card">
                <div>
                    <h3>Sentiment Analysis</h3>
                    <div class="meta">NLP &middot; 1,250 tasks &middot; Updated 2 hours ago</div>
                </div>
                <a href="/projects/1/settings/" class="btn">Settings</a>
            </div>
        </div>
        <div class="card">
            <div class="project-card">
                <div>
                    <h3>Image Object Detection</h3>
                    <div class="meta">Computer Vision &middot; 3,400 tasks &middot; Updated 1 day ago</div>
                </div>
                <a href="/projects/2/settings/" class="btn">Settings</a>
            </div>
        </div>
        <div class="card">
            <div class="project-card">
                <div>
                    <h3>Audio Transcription</h3>
                    <div class="meta">Audio &middot; 890 tasks &middot; Updated 3 days ago</div>
                </div>
                <a href="/projects/3/settings/" class="btn">Settings</a>
            </div>
        </div>
    </div>
</body>
</html>"""


@app.route('/projects/<int:pk>/settings/', defaults={'sub_path': ''})
@app.route('/projects/<int:pk>/settings/<path:sub_path>')
def project_settings(pk, sub_path):
    return """<!DOCTYPE html>
<html>
<head>
    <title>Project Settings - Label Studio</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }
        .header { background: #2196F3; color: white; padding: 16px 32px; }
        .header h1 { font-size: 20px; font-weight: 500; }
        .container { max-width: 900px; margin: 32px auto; padding: 0 16px; }
        .card { background: white; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.12); padding: 24px; margin-bottom: 24px; }
        h2 { font-size: 18px; margin-bottom: 16px; }
        textarea { width: 100%; padding: 12px; font-family: monospace; font-size: 13px; border: 1px solid #ddd; border-radius: 4px; resize: vertical; }
        .btn { padding: 10px 20px; background: #2196F3; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; }
        label { display: block; margin-bottom: 8px; font-weight: 500; color: #333; }
    </style>
</head>
<body>
    <div class="header"><h1>Label Studio - Project Settings</h1></div>
    <div class="container">
        <div class="card">
            <h2>Labeling Interface</h2>
            <form method="POST" action="/projects/upload-example/">
                <label for="label_config">Label Config (XML)</label>
                <textarea id="label_config" name="label_config" rows="10"><View>
  <Text name="text" value="$text"/>
  <Choices name="sentiment" toName="text">
    <Choice value="Positive"/>
    <Choice value="Negative"/>
  </Choices>
</View></textarea>
                <br><br>
                <button type="submit" class="btn">Preview Example Task</button>
            </form>
        </div>
    </div>
</body>
</html>"""


@app.route('/projects/upload-example/', methods=['POST'])
def upload_example_using_config():
    """Generate upload data example by config only"""
    config = request.form.get('label_config', '')

    try:
        validate_label_config(config)
        task_data = get_sample_task(config)
    except (ValueError, ET.ParseError) as e:
        response = make_response('error while example generating', 400)
        return response

    # Return JSON-serialized task data via Response
    # NOTE: Using default text/html content type (matching Django's HttpResponse default behavior)
    response_body = json.dumps(task_data)
    response = make_response(response_body, 200)

    # Check for XSS in the response body using headless browser
    xss_result = check_xss_response(response_body, flag)
    if xss_result == 'XSS':
        response = make_response(flag, 200)

    return response


@app.route('/api/templates/')
def template_list():
    templates = []
    for t in TEMPLATES:
        templates.append({
            "id": t["id"],
            "title": t["title"],
            "group": t["group"]
        })
    return jsonify(templates)


@app.route('/api/templates/<int:template_id>')
def template_detail(template_id):
    for t in TEMPLATES:
        if t["id"] == template_id:
            return jsonify(t)
    return jsonify({"detail": "Not found."}), 404


@app.route('/api/projects/', methods=['GET'])
def api_project_list():
    projects = [
        {"id": 1, "title": "Sentiment Analysis", "task_count": 1250, "created_at": "2024-01-15T10:30:00Z"},
        {"id": 2, "title": "Image Object Detection", "task_count": 3400, "created_at": "2024-01-10T14:20:00Z"},
        {"id": 3, "title": "Audio Transcription", "task_count": 890, "created_at": "2024-01-05T09:15:00Z"},
    ]
    return jsonify({"results": projects, "count": len(projects)})


@app.route('/api/projects/validate/', methods=['POST'])
def api_validate_config():
    config = request.json.get('label_config', '') if request.is_json else request.form.get('label_config', '')
    try:
        validate_label_config(config)
        return jsonify({"status": "ok"})
    except ValueError as e:
        return jsonify({"detail": str(e)}), 400


@app.route('/api/version')
def api_version():
    return jsonify({
        "version": "1.17.0",
        "release": "community",
        "commit": "a1b2c3d"
    })


@app.route('/api/health')
def api_health():
    return jsonify({"status": "UP"})


if __name__ == '__main__':
    app.run(debug=False)
