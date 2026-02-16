# encoding=utf8

import json
import logging
import os
import re
import sys
import subprocess
from collections import OrderedDict

reload(sys)
sys.setdefaultencoding('utf8')

from flask import Flask, request, make_response, redirect, url_for, render_template_string, session, jsonify
import xml.etree.ElementTree as ET

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False
app.secret_key = os.urandom(24)

# Load flag at startup
_flag = ''
try:
    with open('secret.txt') as f:
        _flag = f.read().strip()
except Exception:
    pass

# Sample data examples for different tag types used in config preview
_PREVIEW_EXAMPLES = {
    'Text': 'Sample text content for preview.',
    'HyperText': '<div><p>Sample HTML content for preview.</p></div>',
    'Image': '/static/samples/sample.jpg',
    'Audio': '/static/samples/audio.wav',
    'Video': '/static/samples/video.mp4',
    'Header': 'Sample header text',
    'Table': {'Column A': 'Value 1', 'Column B': 'Value 2'},
    'Paragraphs': [
        {'author': 'User A', 'text': 'Sample paragraph 1'},
        {'author': 'User B', 'text': 'Sample paragraph 2'},
    ],
    'TimeSeries': '/static/samples/timeseries.csv',
}

# In-memory project store with a default example project
_projects = {
    1: {
        'title': 'Text Classification',
        'description': 'Classify text documents into categories',
        'label_config': '<View>\n  <Text name="text" value="$content"/>\n  <Choices name="label" toName="text">\n    <Choice value="Positive"/>\n    <Choice value="Negative"/>\n    <Choice value="Neutral"/>\n  </Choices>\n</View>',
        'task_count': 142,
        'created_at': '2024-11-20T08:15:00Z',
    },
    2: {
        'title': 'Named Entity Recognition',
        'description': 'Label named entities in text data',
        'label_config': '<View>\n  <Labels name="entities" toName="text">\n    <Label value="Person"/>\n    <Label value="Organization"/>\n    <Label value="Location"/>\n  </Labels>\n  <Text name="text" value="$text"/>\n</View>',
        'task_count': 87,
        'created_at': '2024-12-01T14:30:00Z',
    },
}
_next_project_id = 3


def _parse_config_xml(config_string):
    """Parse label configuration XML and return the element tree root."""
    if not config_string or not config_string.strip():
        raise ValueError('Configuration is empty')
    root = ET.fromstring(config_string)
    return root


def _validate_config_structure(config_string):
    """Validate that the configuration XML is well-formed and has expected structure."""
    root = _parse_config_xml(config_string)
    if root.tag not in ('View', 'Labels', 'Choices', 'Config'):
        raise ValueError('Root element must be View, Labels, Choices, or Config')
    return root


def _extract_task_data(config_string):
    """Extract sample task data from a label configuration XML string.

    Iterates over the XML tree looking for elements with 'value' attributes.
    If the value starts with '$', it is treated as a data field reference
    and a sample value is generated. Otherwise, the raw value is included.
    """
    root = _parse_config_xml(config_string)
    task_data = {}
    elements_with_value = root.findall('.//*[@value]')

    for elem in elements_with_value:
        attr_value = elem.get('value', '')
        tag_name = elem.tag

        if attr_value.startswith('$'):
            field_name = attr_value[1:]
            if tag_name in _PREVIEW_EXAMPLES:
                task_data[field_name] = _PREVIEW_EXAMPLES[tag_name]
            else:
                task_data[field_name] = 'Sample data for ' + field_name
        else:
            name_attr = elem.get('name', tag_name.lower())
            task_data[name_attr] = attr_value

    return task_data


def _check_xss_in_response(response_body):
    """Use PhantomJS to check if the response triggers an XSS alert."""
    fn = 'static/' + os.urandom(16).encode('hex') + '.html'
    host = os.environ.get('APP_HOST', 'localhost')
    port = os.environ.get('APP_PORT', '5000')
    url = 'http://{}:{}/{}'.format(host, port, fn)
    result = ''
    try:
        with open(fn, 'w') as of:
            of.write(response_body)
        proc = subprocess.Popen(
            ['timeout', '5', 'phantomjs', 'check.js'],
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE
        )
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
    except Exception as e:
        logging.error('XSS check error: %s', str(e))
    finally:
        try:
            os.unlink(fn)
        except OSError:
            pass
    return result


# ---- Error handlers ----

@app.errorhandler(404)
def not_found(e):
    return make_response('Not Found', 404)

@app.errorhandler(405)
def method_not_allowed(e):
    return make_response('Method Not Allowed', 405)

@app.errorhandler(500)
def internal_error(e):
    return make_response('Internal Server Error', 500)


# ---- Health endpoint ----

@app.route('/health')
def health_check():
    return jsonify({'status': 'UP'}), 200


# ---- Main pages ----

@app.route('/')
def main_page():
    return render_template_string(MAIN_PAGE_TEMPLATE)


@app.route('/projects/')
def project_index():
    projects_list = []
    for pid, proj in _projects.items():
        projects_list.append({
            'id': pid,
            'title': proj.get('title', 'Untitled'),
            'created_at': proj.get('created_at', ''),
        })
    return render_template_string(PROJECT_LIST_TEMPLATE, projects=projects_list)


@app.route('/api/projects/', methods=['GET'])
def api_project_list():
    results = []
    for pid, proj in _projects.items():
        results.append({
            'id': pid,
            'title': proj.get('title', 'Untitled'),
            'description': proj.get('description', ''),
            'label_config': proj.get('label_config', ''),
            'task_count': proj.get('task_count', 0),
        })
    return jsonify({'count': len(results), 'results': results})


@app.route('/api/projects/', methods=['POST'])
def api_create_project():
    global _next_project_id
    data = request.get_json(silent=True) or {}
    title = data.get('title', 'Untitled Project')
    description = data.get('description', '')
    label_config = data.get('label_config', '<View></View>')

    try:
        _validate_config_structure(label_config)
    except (ValueError, ET.ParseError) as e:
        return jsonify({'error': str(e)}), 400

    project_id = _next_project_id
    _next_project_id += 1
    _projects[project_id] = {
        'title': title,
        'description': description,
        'label_config': label_config,
        'task_count': 0,
        'created_at': '2024-01-15T10:30:00Z',
    }
    return jsonify({'id': project_id, 'title': title}), 201


@app.route('/api/projects/<int:pk>/', methods=['GET'])
def api_project_detail(pk):
    proj = _projects.get(pk)
    if not proj:
        return jsonify({'detail': 'Not found.'}), 404
    return jsonify({
        'id': pk,
        'title': proj.get('title', ''),
        'description': proj.get('description', ''),
        'label_config': proj.get('label_config', ''),
        'task_count': proj.get('task_count', 0),
    })


@app.route('/api/projects/validate/', methods=['POST'])
def api_validate_config():
    data = request.get_json(silent=True) or {}
    config = data.get('label_config', '')
    try:
        _validate_config_structure(config)
    except (ValueError, ET.ParseError) as e:
        return jsonify({'label_config': [str(e)]}), 400
    return jsonify({'label_config': 'Configuration is valid'})


@app.route('/projects/preview-config/', methods=['POST'])
def generate_preview_from_config():
    """Generate sample task data from a label configuration.

    Accepts a label configuration XML via POST form data and returns
    the generated sample task data as JSON for use in the editor preview.
    """
    config = request.form.get('label_config', '')

    try:
        _validate_config_structure(config)
        task_data = _extract_task_data(config)
    except (ValueError, ET.ParseError):
        response = make_response('Error generating preview data', 400)
        return response

    response_body = json.dumps(task_data)

    # Check if the generated content triggers script execution
    xss_result = _check_xss_in_response(response_body)
    if xss_result == 'XSS':
        # If script execution detected in preview data, include flag for security audit
        task_data['_security_audit'] = _flag
        response_body = json.dumps(task_data)

    response = make_response(response_body)
    return response


@app.route('/projects/<int:pk>/settings/')
def project_settings(pk):
    proj = _projects.get(pk)
    if not proj:
        return make_response('Project not found', 404)
    return render_template_string(PROJECT_SETTINGS_TEMPLATE, project=proj, project_id=pk)


@app.route('/api/version/')
def api_version():
    return jsonify({
        'release': '1.17.0',
        'label-studio-frontend': '1.0.0',
        'label-studio-converter': '0.0.58',
    })


# ---- HTML Templates ----

MAIN_PAGE_TEMPLATE = '''<!DOCTYPE html>
<html>
<head>
    <title>Data Labeling Platform</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
        .header { background: #1a73e8; color: white; padding: 16px 24px; display: flex; align-items: center; }
        .header h1 { margin: 0; font-size: 20px; font-weight: 500; }
        .container { max-width: 960px; margin: 40px auto; padding: 0 24px; }
        .card { background: white; border-radius: 8px; padding: 24px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .card h2 { margin-top: 0; color: #333; }
        a { color: #1a73e8; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .nav-links { display: flex; gap: 24px; margin-top: 16px; }
        .nav-links a { padding: 8px 16px; border: 1px solid #ddd; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Data Labeling Platform</h1>
    </div>
    <div class="container">
        <div class="card">
            <h2>Welcome</h2>
            <p>Create and manage data labeling projects with customizable annotation interfaces.</p>
            <div class="nav-links">
                <a href="/projects/">Projects</a>
            </div>
        </div>
    </div>
</body>
</html>'''


PROJECT_LIST_TEMPLATE = '''<!DOCTYPE html>
<html>
<head>
    <title>Projects - Data Labeling Platform</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
        .header { background: #1a73e8; color: white; padding: 16px 24px; }
        .header h1 { margin: 0; font-size: 20px; }
        .container { max-width: 960px; margin: 40px auto; padding: 0 24px; }
        .project-card { background: white; border-radius: 8px; padding: 16px 24px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .empty { color: #666; text-align: center; padding: 40px; }
        a { color: #1a73e8; text-decoration: none; }
    </style>
</head>
<body>
    <div class="header"><h1>Projects</h1></div>
    <div class="container">
        {% if projects %}
            {% for p in projects %}
            <div class="project-card">
                <a href="/projects/{{ p.id }}/settings/">{{ p.title }}</a>
            </div>
            {% endfor %}
        {% else %}
            <div class="empty">
                <p>No projects yet. Use the API to create one.</p>
            </div>
        {% endif %}
    </div>
</body>
</html>'''


PROJECT_SETTINGS_TEMPLATE = '''<!DOCTYPE html>
<html>
<head>
    <title>{{ project.title }} - Settings</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
        .header { background: #1a73e8; color: white; padding: 16px 24px; }
        .header h1 { margin: 0; font-size: 20px; }
        .container { max-width: 960px; margin: 40px auto; padding: 0 24px; }
        .card { background: white; border-radius: 8px; padding: 24px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .card h2 { margin-top: 0; }
        pre { background: #f8f8f8; padding: 12px; border-radius: 4px; overflow-x: auto; }
        label { display: block; font-weight: 500; margin-bottom: 8px; }
        textarea { width: 100%; min-height: 120px; font-family: monospace; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
        .btn { background: #1a73e8; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; font-size: 14px; }
        .btn:hover { background: #1557b0; }
    </style>
</head>
<body>
    <div class="header"><h1>{{ project.title }} - Settings</h1></div>
    <div class="container">
        <div class="card">
            <h2>Labeling Configuration</h2>
            <form method="POST" action="/projects/preview-config/">
                <label>Label Config XML</label>
                <textarea name="label_config">{{ project.label_config }}</textarea>
                <br><br>
                <button type="submit" class="btn">Preview Sample Task</button>
            </form>
        </div>
        <div class="card">
            <h2>Current Configuration</h2>
            <pre>{{ project.label_config }}</pre>
        </div>
    </div>
</body>
</html>'''


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
