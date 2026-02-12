import os
import re
import json
import html
import time
import logging
import tempfile
import threading
from flask import Flask, request, render_template, jsonify, abort, redirect, url_for

from template_engine import TemplateEngine
from xss_checker import check_rendered_page

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(32).hex()

engine = TemplateEngine()

# Load flag at startup from file (written at build time)
_flag_path = os.path.join(os.path.dirname(__file__), 'flag.txt')
_flag_value = ''
if os.path.exists(_flag_path):
    with open(_flag_path, 'r') as f:
        _flag_value = f.read().strip()


# --- Template storage (in-memory, simulating a CMS) ---
_templates_lock = threading.Lock()
_templates = {
    'welcome': {
        'name': 'welcome',
        'description': 'Welcome page template',
        'source': '<h2>Welcome, {$username|escape:"html"}!</h2>\n<p>Your account was created on {$created_date}.</p>',
        'readonly': True,
    },
    'profile': {
        'name': 'profile',
        'description': 'User profile card',
        'source': '<div class="profile-card">\n  <h3>{$display_name|escape:"html"}</h3>\n  <p class="bio">{$bio|escape:"html"}</p>\n</div>',
        'readonly': True,
    },
    'notification': {
        'name': 'notification',
        'description': 'Browser notification with JS',
        'source': '<div class="notification" id="notify-box">\n  <p>{$message|escape:"html"}</p>\n</div>\n<script>\nlet msg = `{$message|escape:"javascript"}`;\ndocument.getElementById("notify-box").title = msg;\n</script>',
        'readonly': True,
    },
    'analytics': {
        'name': 'analytics',
        'description': 'Analytics tracking snippet',
        'source': '<script>\nlet campaign = `{$campaign_name|escape:"javascript"}`;\nlet source = `{$traffic_source|escape:"javascript"}`;\nconsole.log("Campaign: " + campaign + ", Source: " + source);\n</script>\n<noscript><p>Analytics requires JavaScript.</p></noscript>',
        'readonly': True,
    },
}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/docs')
def docs():
    return render_template('docs.html')


@app.route('/api/templates', methods=['GET'])
def list_templates():
    with _templates_lock:
        result = []
        for name, tpl in _templates.items():
            result.append({
                'name': tpl['name'],
                'description': tpl['description'],
                'readonly': tpl.get('readonly', False),
            })
    return jsonify(result)


@app.route('/api/templates/<name>', methods=['GET'])
def get_template(name):
    with _templates_lock:
        tpl = _templates.get(name)
        if not tpl:
            return jsonify({'error': 'Template not found'}), 404
        return jsonify({
            'name': tpl['name'],
            'description': tpl['description'],
            'source': tpl['source'],
            'readonly': tpl.get('readonly', False),
        })


@app.route('/api/templates', methods=['POST'])
def create_template():
    data = request.get_json(silent=True)
    if not data or 'name' not in data or 'source' not in data:
        return jsonify({'error': 'Missing required fields: name, source'}), 400

    name = data['name'].strip()
    if not re.match(r'^[a-zA-Z0-9_-]+$', name):
        return jsonify({'error': 'Invalid template name. Use alphanumeric, hyphens, and underscores only.'}), 400

    with _templates_lock:
        if name in _templates:
            return jsonify({'error': 'Template already exists'}), 409
        _templates[name] = {
            'name': name,
            'description': data.get('description', ''),
            'source': data['source'],
            'readonly': False,
        }

    return jsonify({'status': 'created', 'name': name}), 201


@app.route('/api/templates/<name>', methods=['PUT'])
def update_template(name):
    data = request.get_json(silent=True)
    if not data or 'source' not in data:
        return jsonify({'error': 'Missing required field: source'}), 400

    with _templates_lock:
        tpl = _templates.get(name)
        if not tpl:
            return jsonify({'error': 'Template not found'}), 404
        if tpl.get('readonly'):
            return jsonify({'error': 'Cannot modify read-only template'}), 403
        tpl['source'] = data['source']
        if 'description' in data:
            tpl['description'] = data['description']

    return jsonify({'status': 'updated', 'name': name})


@app.route('/api/templates/<name>', methods=['DELETE'])
def delete_template(name):
    with _templates_lock:
        tpl = _templates.get(name)
        if not tpl:
            return jsonify({'error': 'Template not found'}), 404
        if tpl.get('readonly'):
            return jsonify({'error': 'Cannot delete read-only template'}), 403
        del _templates[name]

    return jsonify({'status': 'deleted', 'name': name})


@app.route('/render', methods=['GET', 'POST'])
def render_page():
    if request.method == 'GET':
        return render_template('render.html')

    template_name = request.form.get('template', '')
    variables_raw = request.form.get('variables', '{}')

    with _templates_lock:
        tpl = _templates.get(template_name)
        if not tpl:
            return render_template('render.html',
                                   error='Template not found',
                                   template_name=template_name,
                                   variables_raw=variables_raw)
        source = tpl['source']

    try:
        variables = json.loads(variables_raw)
        if not isinstance(variables, dict):
            raise ValueError("Variables must be a JSON object")
    except (json.JSONDecodeError, ValueError) as e:
        return render_template('render.html',
                               error='Invalid JSON for variables: ' + str(e),
                               template_name=template_name,
                               variables_raw=variables_raw)

    rendered = engine.render(source, variables)

    return render_template('render.html',
                           rendered_output=rendered,
                           template_name=template_name,
                           variables_raw=variables_raw)


@app.route('/preview', methods=['POST'])
def preview():
    """Render a template and check it in a headless browser for XSS validation.
    Used internally for security testing of templates."""
    template_name = request.form.get('template', '')
    variables_raw = request.form.get('variables', '{}')

    with _templates_lock:
        tpl = _templates.get(template_name)
        if not tpl:
            return jsonify({'error': 'Template not found'}), 404
        source = tpl['source']

    try:
        variables = json.loads(variables_raw)
        if not isinstance(variables, dict):
            raise ValueError("Variables must be a JSON object")
    except (json.JSONDecodeError, ValueError) as e:
        return jsonify({'error': 'Invalid JSON: ' + str(e)}), 400

    rendered = engine.render(source, variables)

    # Write rendered HTML to a temporary file and check with headless browser
    result = check_rendered_page(rendered)

    if result and result.strip() == 'XSS':
        return jsonify({
            'status': 'vulnerability_detected',
            'detail': 'XSS execution confirmed',
            'flag': _flag_value,
        })
    elif result:
        return jsonify({
            'status': 'alert_detected',
            'detail': 'Alert triggered with value: ' + result,
        })
    else:
        return jsonify({
            'status': 'clean',
            'detail': 'No script execution detected',
        })


@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
