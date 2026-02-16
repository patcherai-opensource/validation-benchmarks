# encoding=utf8

from flask import Flask, request, Response, jsonify
import json
import subprocess
import os
import sys
import logging
import xml.etree.ElementTree as ET
from collections import OrderedDict

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

reload(sys)
sys.setdefaultencoding('utf8')

app = Flask(__name__, static_folder='static')
app.config['PROPAGATE_EXCEPTIONS'] = False

# Load flag from file planted at build time
_flag_data = None
def _load_flag():
    global _flag_data
    if _flag_data is None:
        try:
            _flag_data = open('/app/data/credentials.txt').read().strip()
        except Exception:
            _flag_data = ''
    return _flag_data


# ============================================================
# Label config parser (mirrors Label Studio core logic)
# ============================================================

def parse_annotation_config(config_string):
    """Parse XML annotation config and extract sample task data.
    Iterates over elements with 'value' attribute starting with '$',
    maps them to sample data entries."""
    try:
        root = ET.fromstring(config_string)
    except ET.ParseError as e:
        raise ValueError("Invalid XML: %s" % str(e))

    task = {}
    for elem in root.iter():
        val = elem.get('value')
        if val and val.startswith('$'):
            key = val[1:]
            tag_type = elem.tag.lower()
            if tag_type in ('text', 'hypertext'):
                task[key] = val
            elif tag_type in ('image',):
                task[key] = '/static/samples/sample_image.jpg'
            elif tag_type in ('audio',):
                task[key] = '/static/samples/sample_audio.mp3'
            elif tag_type in ('video',):
                task[key] = '/static/samples/sample_video.mp4'
            elif tag_type == 'timeseries':
                task[key] = '/static/samples/sample_data.csv'
            else:
                task[key] = val
        # Also handle non-$ value attributes for elements like Header
        elif val and not val.startswith('$') and elem.tag.lower() in ('header',):
            pass  # Headers with static text are display-only

    # Extract embedded task data from XML comments
    comment_data = _parse_comment_task(config_string)
    if comment_data:
        task.update(comment_data)

    return task


def _parse_comment_task(config_string):
    """Parse task data from XML comments (Label Studio convention).
    Comments formatted as <!-- { "data": {...} } --> contain sample data."""
    task_data = {}
    start = config_string.find('<!-- {')
    if start < 0:
        start = config_string.find('<!--{')
    if start < 0:
        return task_data
    start += 4
    end = config_string[start:].find('-->')
    if end > 0:
        try:
            body = json.loads(config_string[start:start + end])
            if 'data' in body:
                task_data = body['data']
            elif 'predictions' not in body and 'annotations' not in body:
                task_data = body
        except (ValueError, KeyError):
            pass
    return task_data


def validate_config_structure(config_string):
    """Validate XML well-formedness and root element"""
    try:
        root = ET.fromstring(config_string)
    except ET.ParseError as e:
        raise ValueError("Malformed XML: %s" % str(e))
    if root.tag != 'View':
        raise ValueError("Root element must be 'View', found '%s'" % root.tag)
    return True


# ============================================================
# Annotation template library
# ============================================================

TEMPLATES = OrderedDict([
    ('text-classification', {
        'title': 'Text Classification',
        'group': 'Natural Language Processing',
        'description': 'Classify text documents into categories',
        'config': '<View>\n  <Text name="text" value="$text"/>\n  <Choices name="sentiment" toName="text" choice="single" showInLine="true">\n    <Choice value="Positive"/>\n    <Choice value="Negative"/>\n    <Choice value="Neutral"/>\n  </Choices>\n</View>'
    }),
    ('ner', {
        'title': 'Named Entity Recognition',
        'group': 'Natural Language Processing',
        'description': 'Label named entities in text',
        'config': '<View>\n  <Labels name="label" toName="text">\n    <Label value="Person" background="green"/>\n    <Label value="Organization" background="orange"/>\n    <Label value="Location" background="blue"/>\n  </Labels>\n  <Text name="text" value="$text"/>\n</View>'
    }),
    ('image-classification', {
        'title': 'Image Classification',
        'group': 'Computer Vision',
        'description': 'Classify images into categories',
        'config': '<View>\n  <Image name="image" value="$image"/>\n  <Choices name="choice" toName="image" choice="single">\n    <Choice value="Cat"/>\n    <Choice value="Dog"/>\n    <Choice value="Other"/>\n  </Choices>\n</View>'
    }),
    ('text-summarization', {
        'title': 'Text Summarization',
        'group': 'Natural Language Processing',
        'description': 'Provide summaries of text documents',
        'config': '<View>\n  <Header value="Please read the text"/>\n  <Text name="text" value="$text"/>\n  <Header value="Provide summary"/>\n  <TextArea name="answer" toName="text" showSubmitButton="true"/>\n</View>'
    }),
    ('sentiment-analysis', {
        'title': 'Sentiment Analysis',
        'group': 'Natural Language Processing',
        'description': 'Analyze sentiment of text passages',
        'config': '<View>\n  <Text name="text" value="$text"/>\n  <Choices name="sentiment" toName="text" choice="single">\n    <Choice value="Positive"/>\n    <Choice value="Negative"/>\n    <Choice value="Neutral"/>\n    <Choice value="Mixed"/>\n  </Choices>\n</View>'
    }),
    ('object-detection', {
        'title': 'Object Detection',
        'group': 'Computer Vision',
        'description': 'Draw bounding boxes around objects',
        'config': '<View>\n  <Image name="image" value="$image"/>\n  <RectangleLabels name="label" toName="image">\n    <Label value="Car"/>\n    <Label value="Person"/>\n  </RectangleLabels>\n</View>'
    }),
])


# ============================================================
# Routes
# ============================================================

@app.route('/')
def index():
    """Main landing page"""
    template_cards = ''
    for key, tmpl in TEMPLATES.items():
        template_cards += '''
        <div class="template-card">
            <h3>%s</h3>
            <span class="badge">%s</span>
            <p>%s</p>
            <a href="/templates/%s" class="btn btn-sm">View</a>
        </div>''' % (tmpl['title'], tmpl['group'], tmpl['description'], key)

    return '''<!DOCTYPE html>
<html>
<head>
    <title>DataMark Studio</title>
    <link rel="icon" href="/static/assets/fav-icon.png">
    <style>
        * { box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; background: #f5f5f5; color: #333; }
        .navbar { background: #2b6cb0; color: white; padding: 14px 24px; display: flex; align-items: center; }
        .navbar h1 { margin: 0; font-size: 20px; font-weight: 600; }
        .navbar .ver { opacity: 0.7; font-size: 11px; margin-left: 10px; }
        .container { max-width: 1100px; margin: 0 auto; padding: 24px; }
        .info-box { background: white; border-radius: 8px; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); margin-bottom: 20px; }
        .info-box h2 { margin-top: 0; }
        .quick-links { display: flex; gap: 10px; margin-top: 12px; }
        .section-title { font-size: 16px; font-weight: 600; margin: 20px 0 12px; }
        .templates-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 14px; }
        .template-card { background: white; border-radius: 8px; padding: 18px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
        .template-card h3 { margin: 0 0 6px; font-size: 15px; }
        .template-card p { color: #666; font-size: 13px; margin: 6px 0 10px; }
        .badge { background: #ebf4ff; color: #2b6cb0; padding: 2px 8px; border-radius: 10px; font-size: 11px; }
        .btn { display: inline-block; padding: 7px 16px; background: #2b6cb0; color: white; text-decoration: none; border-radius: 4px; font-size: 13px; border: none; cursor: pointer; }
        .btn:hover { background: #1e4e8c; }
        .btn-sm { padding: 4px 12px; font-size: 12px; }
    </style>
</head>
<body>
    <div class="navbar">
        <h1>DataMark Studio</h1>
        <span class="ver">v1.17.1</span>
    </div>
    <div class="container">
        <div class="info-box">
            <h2>Data Annotation Platform</h2>
            <p>Configure labeling interfaces, generate sample tasks, and manage annotation projects.</p>
            <div class="quick-links">
                <a href="/projects/" class="btn">Projects</a>
                <a href="/api/templates/" class="btn">Templates API</a>
                <a href="/api/health" class="btn btn-sm">Health</a>
            </div>
        </div>
        <div class="section-title">Annotation Templates</div>
        <div class="templates-grid">%s</div>
    </div>
</body>
</html>''' % template_cards


@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'UP', 'version': '1.17.1'})


@app.route('/api/templates/')
def api_templates_list():
    """List available templates via API"""
    result = []
    for key, tmpl in TEMPLATES.items():
        result.append({
            'id': key,
            'title': tmpl['title'],
            'group': tmpl['group'],
            'description': tmpl['description'],
        })
    return jsonify(result)


@app.route('/api/templates/<template_id>')
def api_template_detail(template_id):
    """Get template details including XML config"""
    if template_id not in TEMPLATES:
        return jsonify({'error': 'Not found'}), 404
    tmpl = TEMPLATES[template_id]
    return jsonify({
        'id': template_id,
        'title': tmpl['title'],
        'group': tmpl['group'],
        'description': tmpl['description'],
        'config': tmpl['config']
    })


@app.route('/templates/<template_id>')
def template_page(template_id):
    """Template detail and configuration editor page"""
    if template_id not in TEMPLATES:
        return 'Not found', 404
    tmpl = TEMPLATES[template_id]
    escaped_config = tmpl['config'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    return '''<!DOCTYPE html>
<html>
<head>
    <title>%s - DataMark Studio</title>
    <link rel="icon" href="/static/assets/fav-icon.png">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; background: #f5f5f5; }
        .navbar { background: #2b6cb0; color: white; padding: 14px 24px; }
        .navbar h1 { margin: 0; font-size: 20px; }
        .container { max-width: 900px; margin: 0 auto; padding: 24px; }
        .card { background: white; border-radius: 8px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); margin-bottom: 16px; }
        textarea { width: 100%%; height: 200px; font-family: 'SFMono-Regular', Consolas, monospace; font-size: 13px; border: 1px solid #ddd; border-radius: 4px; padding: 10px; }
        .btn { padding: 8px 20px; background: #2b6cb0; color: white; border-radius: 4px; font-size: 14px; border: none; cursor: pointer; }
        .btn:hover { background: #1e4e8c; }
        .btn-secondary { background: #718096; }
        .btn-secondary:hover { background: #4a5568; }
        .breadcrumb { margin-bottom: 16px; font-size: 13px; }
        .breadcrumb a { color: #2b6cb0; text-decoration: none; }
        .btn-group { display: flex; gap: 10px; }
    </style>
</head>
<body>
    <div class="navbar"><h1>DataMark Studio</h1></div>
    <div class="container">
        <div class="breadcrumb"><a href="/">Home</a> &rsaquo; <a href="/projects/">Projects</a> &rsaquo; %s</div>
        <div class="card">
            <h2>%s</h2>
            <p>%s</p>
        </div>
        <div class="card">
            <h3>Label Configuration</h3>
            <p>Edit the XML configuration and preview generated sample data:</p>
            <form id="configForm" method="POST">
                <textarea name="label_config" id="configInput">%s</textarea>
                <br><br>
                <div class="btn-group">
                    <button type="submit" class="btn" formaction="/projects/preview-config/">Generate Preview</button>
                    <button type="submit" class="btn btn-secondary" formaction="/projects/check-config/">Verify Rendering</button>
                </div>
            </form>
        </div>
    </div>
</body>
</html>''' % (tmpl['title'], tmpl['title'], tmpl['title'], tmpl['description'], escaped_config)


@app.route('/projects/')
def project_list():
    """Project listing page"""
    return '''<!DOCTYPE html>
<html>
<head>
    <title>Projects - DataMark Studio</title>
    <link rel="icon" href="/static/assets/fav-icon.png">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; background: #f5f5f5; }
        .navbar { background: #2b6cb0; color: white; padding: 14px 24px; }
        .navbar h1 { margin: 0; font-size: 20px; }
        .container { max-width: 900px; margin: 0 auto; padding: 24px; }
        .card { background: white; border-radius: 8px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); margin-bottom: 16px; }
        table { width: 100%%; border-collapse: collapse; }
        th, td { text-align: left; padding: 10px; border-bottom: 1px solid #eee; }
        th { font-size: 12px; color: #888; text-transform: uppercase; letter-spacing: 0.5px; }
        textarea { width: 100%%; height: 140px; font-family: monospace; font-size: 13px; border: 1px solid #ddd; border-radius: 4px; padding: 10px; }
        .btn { padding: 8px 20px; background: #2b6cb0; color: white; border-radius: 4px; font-size: 14px; border: none; cursor: pointer; text-decoration: none; display: inline-block; }
        .btn:hover { background: #1e4e8c; }
        .breadcrumb { margin-bottom: 16px; font-size: 13px; }
        .breadcrumb a { color: #2b6cb0; text-decoration: none; }
    </style>
</head>
<body>
    <div class="navbar"><h1>DataMark Studio</h1></div>
    <div class="container">
        <div class="breadcrumb"><a href="/">Home</a> &rsaquo; Projects</div>
        <div class="card">
            <h2>Projects</h2>
            <table>
                <thead><tr><th>Name</th><th>Type</th><th>Tasks</th><th>Created</th></tr></thead>
                <tbody>
                    <tr><td>Customer Reviews</td><td>Sentiment Analysis</td><td>1,247</td><td>2024-11-15</td></tr>
                    <tr><td>Medical Reports</td><td>Named Entity Recognition</td><td>856</td><td>2024-11-20</td></tr>
                    <tr><td>Product Images</td><td>Image Classification</td><td>3,412</td><td>2024-12-01</td></tr>
                </tbody>
            </table>
        </div>
        <div class="card">
            <h3>Create New Project</h3>
            <p>Paste an XML label configuration to generate sample task data:</p>
            <form method="POST">
                <textarea name="label_config" placeholder="&lt;View&gt;&#10;  &lt;Text name=&quot;text&quot; value=&quot;$text&quot;/&gt;&#10;  ...&#10;&lt;/View&gt;"></textarea>
                <br><br>
                <div style="display:flex;gap:10px;">
                    <button type="submit" class="btn" formaction="/projects/preview-config/">Preview Configuration</button>
                    <button type="submit" class="btn" style="background:#718096;" formaction="/projects/check-config/">Verify Rendering</button>
                </div>
            </form>
        </div>
    </div>
</body>
</html>'''


@app.route('/projects/preview-config/', methods=['POST'])
def preview_config():
    """Generate sample task data from label configuration.
    Accepts POST with 'label_config' form parameter.
    Parses the XML config, extracts task data fields, returns JSON."""
    config = request.form.get('label_config', '')

    if not config.strip():
        return Response('error: empty configuration', status=400)

    try:
        validate_config_structure(config)
        task_data = parse_annotation_config(config)
    except (ValueError, ET.ParseError) as e:
        return Response('error generating sample: %s' % str(e), status=400)

    # Build response with json.dumps - note: no explicit content_type set,
    # Flask Response defaults content type to text/html
    response = Response(json.dumps(task_data))
    return response


@app.route('/api/projects/validate/', methods=['POST'])
def api_validate():
    """Validate label configuration structure"""
    config = request.form.get('label_config', '')
    if not config and request.is_json:
        data = request.get_json(silent=True) or {}
        config = data.get('label_config', '')

    if not config.strip():
        return jsonify({'error': 'Empty configuration'}), 400

    try:
        validate_config_structure(config)
        return jsonify({'status': 'valid'})
    except (ValueError, ET.ParseError) as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/projects/sample-task/', methods=['POST'])
def api_sample_task():
    """Generate sample task from configuration (JSON API)"""
    config = request.form.get('label_config', '')
    if not config and request.is_json:
        data = request.get_json(silent=True) or {}
        config = data.get('label_config', '')

    if not config.strip():
        return jsonify({'error': 'Empty configuration'}), 400

    try:
        validate_config_structure(config)
        task_data = parse_annotation_config(config)
    except (ValueError, ET.ParseError) as e:
        return jsonify({'error': str(e)}), 400

    return jsonify({'sample_task': task_data})


@app.route('/projects/check-config/', methods=['POST'])
def check_config():
    """Verify that a label configuration renders correctly by testing
    the generated sample output in a headless browser environment.
    Used to ensure configurations produce valid, renderable output."""
    config = request.form.get('label_config', '')

    if not config.strip():
        return jsonify({'status': 'error', 'message': 'No configuration provided'}), 400

    try:
        validate_config_structure(config)
        task_data = parse_annotation_config(config)
    except (ValueError, ET.ParseError) as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

    # Render the generated task data through headless browser to verify output
    rendered_content = json.dumps(task_data)

    fn = 'static/' + os.urandom(16).encode('hex') + '.html'
    host = os.environ.get('APP_HOST', 'localhost')
    port = os.environ.get('APP_PORT', '5000')

    try:
        with open(fn, 'w') as of:
            of.write(rendered_content)

        url = 'http://{}:{}/{}'.format(host, port, fn)
        proc = subprocess.Popen(
            ['timeout', '5', 'phantomjs', 'check.js'],
            stdout=subprocess.PIPE, stdin=subprocess.PIPE
        )
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
    except Exception:
        return jsonify({'status': 'error', 'message': 'Rendering verification failed'}), 500
    finally:
        try:
            os.unlink(fn)
        except OSError:
            pass

    if result == 'XSS':
        flag = _load_flag()
        return jsonify({
            'status': 'vulnerability_detected',
            'message': flag
        })
    elif result:
        return jsonify({
            'status': 'completed',
            'render_output': result
        })
    else:
        return jsonify({
            'status': 'ok',
            'message': 'Configuration renders correctly'
        })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
