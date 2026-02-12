# encoding=utf8

from flask import Flask, request, Response, make_response, jsonify, redirect, url_for, session
import json
import subprocess
import os
import re
import urllib
import sys
import hashlib
import time
from xml.etree import ElementTree as ET

from phantomjs import Phantom

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flag_value = open('secret.txt').read().strip()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False
app.secret_key = os.urandom(24).encode('hex')

phantom = Phantom()

# In-memory project storage
projects_db = {
    1: {
        'id': 1,
        'title': 'Sentiment Analysis',
        'description': 'Classify text sentiment as positive, negative, or neutral',
        'label_config': '<View><Text name="text" value="$text"/><Choices name="sentiment" toName="text"><Choice value="Positive"/><Choice value="Negative"/><Choice value="Neutral"/></Choices></View>',
        'created_at': '2024-01-15T10:30:00Z',
        'task_count': 142,
        'created_by': 'admin'
    },
    2: {
        'id': 2,
        'title': 'Named Entity Recognition',
        'description': 'Label named entities in text documents',
        'label_config': '<View><Text name="text" value="$text"/><Labels name="label" toName="text"><Label value="Person"/><Label value="Organization"/><Label value="Location"/></Labels></View>',
        'created_at': '2024-02-20T14:15:00Z',
        'task_count': 87,
        'created_by': 'admin'
    },
    3: {
        'id': 3,
        'title': 'Image Classification',
        'description': 'Classify images into predefined categories',
        'label_config': '<View><Image name="image" value="$image"/><Choices name="category" toName="image"><Choice value="Cat"/><Choice value="Dog"/><Choice value="Bird"/></Choices></View>',
        'created_at': '2024-03-10T09:00:00Z',
        'task_count': 256,
        'created_by': 'admin'
    }
}

next_project_id = 4


def parse_config_to_sample_task(label_config):
    """Parse label config XML and generate sample task data.
    Extracts value attributes from tags that reference data keys (starting with $).
    Returns a dictionary with sample data for each data variable found in the config.
    """
    try:
        root = ET.fromstring(label_config)
    except ET.ParseError as e:
        raise ValueError('Invalid XML in label configuration: {}'.format(str(e)))

    task_data = {}
    for element in root.iter():
        value_attr = element.attrib.get('value', '')
        name_attr = element.attrib.get('name', '')

        if value_attr.startswith('$'):
            # Extract the variable reference and generate sample content
            raw_value = value_attr[1:]  # strip the leading $
            tag_name = element.tag.lower()

            # The key is derived from the variable name portion
            # In production configs this is typically just a field name like "text"
            # but we pass through the full value for sample generation
            if tag_name in ('text', 'header', 'hypertext'):
                task_data[name_attr] = raw_value
            elif tag_name in ('image',):
                task_data[name_attr] = '/data/upload/' + name_attr + '.jpg'
            elif tag_name in ('audio',):
                task_data[name_attr] = '/data/upload/' + name_attr + '.mp3'
            elif tag_name in ('video',):
                task_data[name_attr] = '/data/upload/' + name_attr + '.mp4'
            else:
                task_data[name_attr] = raw_value

    return task_data


def validate_label_config(config):
    """Validate that the label config is structurally valid XML with a root View element."""
    try:
        root = ET.fromstring(config)
    except ET.ParseError:
        return False, 'Invalid XML format'
    if root.tag != 'View':
        return False, 'Root element must be <View>'
    return True, None


def check_xss_content(html_content):
    """Render HTML content in headless browser and check for alert execution."""
    proc = subprocess.Popen(
        ["timeout", "8", "phantomjs", "check.js"],
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
        except:
            pass
    return result


@app.route('/')
def index():
    return redirect('/projects/')


@app.route('/user/login/', methods=['GET'])
def login_page():
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Label Studio</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }
        .login-container { max-width: 400px; margin: 100px auto; background: #fff; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); padding: 40px; }
        .login-container h1 { text-align: center; color: #333; margin-bottom: 8px; font-size: 24px; }
        .login-container .subtitle { text-align: center; color: #999; margin-bottom: 30px; font-size: 14px; }
        .form-group { margin-bottom: 16px; }
        .form-group label { display: block; margin-bottom: 4px; font-weight: 500; color: #555; font-size: 14px; }
        .form-group input { width: 100%; padding: 10px 12px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; }
        .btn-primary { width: 100%; padding: 12px; background: #2196f3; color: #fff; border: none; border-radius: 4px; font-size: 16px; cursor: pointer; }
        .btn-primary:hover { background: #1976d2; }
    </style>
</head>
<body>
    <div class="login-container">
        <h1>Label Studio</h1>
        <p class="subtitle">Sign in to your account</p>
        <form method="POST" action="/user/login/">
            <div class="form-group">
                <label>Email</label>
                <input type="email" name="email" required placeholder="Enter your email">
            </div>
            <div class="form-group">
                <label>Password</label>
                <input type="password" name="password" required placeholder="Enter password">
            </div>
            <button type="submit" class="btn-primary">Sign In</button>
        </form>
    </div>
</body>
</html>'''


@app.route('/user/login/', methods=['POST'])
def login():
    email = request.form.get('email', '')
    password = request.form.get('password', '')
    return redirect('/projects/')


@app.route('/user/logout/', methods=['POST', 'GET'])
def logout():
    session.pop('user', None)
    return redirect('/user/login/')


@app.route('/api/current-user/whoami/', methods=['GET'])
def whoami():
    return jsonify({
        'username': 'anonymous',
        'email': '',
        'active_organization': 1,
    })


@app.route('/projects/', methods=['GET'])
def list_projects():
    project_items = ''
    for pid, proj in sorted(projects_db.items()):
        project_items += '''
        <div class="project-card">
            <h3><a href="/projects/{id}/">{title}</a></h3>
            <p>{description}</p>
            <div class="project-meta">
                <span>{task_count} tasks</span>
                <span>Created {created_at}</span>
            </div>
        </div>'''.format(
            id=proj['id'],
            title=proj['title'],
            description=proj['description'],
            task_count=proj['task_count'],
            created_at=proj['created_at'][:10]
        )

    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Projects - Label Studio</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }}
        .navbar {{ background: #fff; border-bottom: 1px solid #e0e0e0; padding: 12px 24px; display: flex; justify-content: space-between; align-items: center; }}
        .navbar h1 {{ font-size: 18px; color: #333; }}
        .navbar a {{ color: #2196f3; text-decoration: none; font-size: 14px; margin-left: 16px; }}
        .container {{ max-width: 960px; margin: 24px auto; padding: 0 16px; }}
        .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }}
        .header h2 {{ font-size: 22px; color: #333; }}
        .btn {{ padding: 8px 16px; border-radius: 4px; text-decoration: none; font-size: 14px; }}
        .btn-primary {{ background: #2196f3; color: #fff; border: none; cursor: pointer; }}
        .project-card {{ background: #fff; border-radius: 8px; padding: 20px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }}
        .project-card h3 {{ margin-bottom: 8px; }}
        .project-card h3 a {{ color: #333; text-decoration: none; }}
        .project-card h3 a:hover {{ color: #2196f3; }}
        .project-card p {{ color: #666; font-size: 14px; margin-bottom: 12px; }}
        .project-meta {{ color: #999; font-size: 12px; }}
        .project-meta span {{ margin-right: 16px; }}
    </style>
</head>
<body>
    <div class="navbar">
        <h1>Label Studio</h1>
        <div>
            <a href="/projects/">Projects</a>
            <a href="/user/login/">Sign In</a>
        </div>
    </div>
    <div class="container">
        <div class="header">
            <h2>Projects</h2>
            <a class="btn btn-primary" href="/projects/create/">Create Project</a>
        </div>
        {projects}
    </div>
</body>
</html>'''.format(projects=project_items)


@app.route('/projects/<int:project_id>/', methods=['GET'])
def project_detail(project_id):
    proj = projects_db.get(project_id)
    if not proj:
        return make_response('Not found', 404)

    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>{title} - Label Studio</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }}
        .navbar {{ background: #fff; border-bottom: 1px solid #e0e0e0; padding: 12px 24px; display: flex; justify-content: space-between; align-items: center; }}
        .navbar h1 {{ font-size: 18px; color: #333; }}
        .navbar a {{ color: #2196f3; text-decoration: none; font-size: 14px; }}
        .container {{ max-width: 960px; margin: 24px auto; padding: 0 16px; }}
        .detail-card {{ background: #fff; border-radius: 8px; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }}
        .detail-card h2 {{ margin-bottom: 12px; }}
        .detail-card p {{ color: #666; margin-bottom: 16px; }}
        .config-block {{ background: #f8f8f8; border: 1px solid #eee; border-radius: 4px; padding: 16px; margin-top: 16px; }}
        .config-block pre {{ font-size: 13px; overflow-x: auto; white-space: pre-wrap; }}
        .meta {{ color: #999; font-size: 13px; margin-top: 16px; }}
    </style>
</head>
<body>
    <div class="navbar">
        <h1>Label Studio</h1>
        <a href="/projects/">Projects</a>
    </div>
    <div class="container">
        <div class="detail-card">
            <h2>{title}</h2>
            <p>{description}</p>
            <div class="config-block">
                <strong>Label Configuration</strong>
                <pre>{label_config}</pre>
            </div>
            <div class="meta">
                <p>Tasks: {task_count} &middot; Created by: {created_by} &middot; {created_at}</p>
            </div>
        </div>
    </div>
</body>
</html>'''.format(
        title=proj['title'],
        description=proj['description'],
        label_config=proj['label_config'].replace('<', '&lt;').replace('>', '&gt;'),
        task_count=proj['task_count'],
        created_by=proj['created_by'],
        created_at=proj['created_at'][:10]
    )


@app.route('/projects/create/', methods=['GET'])
def create_project_page():
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Create Project - Label Studio</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }
        .navbar { background: #fff; border-bottom: 1px solid #e0e0e0; padding: 12px 24px; display: flex; justify-content: space-between; align-items: center; }
        .navbar h1 { font-size: 18px; color: #333; }
        .navbar a { color: #2196f3; text-decoration: none; font-size: 14px; }
        .container { max-width: 720px; margin: 24px auto; padding: 0 16px; }
        .form-card { background: #fff; border-radius: 8px; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
        .form-group { margin-bottom: 16px; }
        .form-group label { display: block; font-weight: 500; margin-bottom: 4px; color: #555; }
        .form-group input, .form-group textarea { width: 100%; padding: 10px 12px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; }
        .form-group textarea { font-family: monospace; }
        .btn-primary { padding: 10px 20px; background: #2196f3; color: #fff; border: none; border-radius: 4px; font-size: 14px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="navbar">
        <h1>Label Studio</h1>
        <a href="/projects/">Projects</a>
    </div>
    <div class="container">
        <div class="form-card">
            <h2 style="margin-bottom: 20px;">Create New Project</h2>
            <form method="POST" action="/projects/create/">
                <div class="form-group">
                    <label>Project Title</label>
                    <input type="text" name="title" required placeholder="My Project">
                </div>
                <div class="form-group">
                    <label>Description</label>
                    <input type="text" name="description" placeholder="Project description">
                </div>
                <div class="form-group">
                    <label>Label Configuration (XML)</label>
                    <textarea name="label_config" rows="8" placeholder="<View>...</View>"></textarea>
                </div>
                <button type="submit" class="btn-primary">Create Project</button>
            </form>
        </div>
    </div>
</body>
</html>'''


@app.route('/projects/create/', methods=['POST'])
def create_project():
    global next_project_id
    title = request.form.get('title', 'Untitled')
    description = request.form.get('description', '')
    label_config = request.form.get('label_config', '')

    valid, error = validate_label_config(label_config)
    if not valid:
        return make_response(json.dumps({'error': error}), 400)

    pid = next_project_id
    next_project_id += 1
    projects_db[pid] = {
        'id': pid,
        'title': title,
        'description': description,
        'label_config': label_config,
        'created_at': time.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'task_count': 0,
        'created_by': session.get('user', 'anonymous')
    }
    return redirect('/projects/{}/'.format(pid))


@app.route('/api/projects/', methods=['GET'])
def api_list_projects():
    return jsonify(list(projects_db.values()))


@app.route('/api/projects/<int:project_id>/', methods=['GET'])
def api_project_detail(project_id):
    proj = projects_db.get(project_id)
    if not proj:
        return jsonify({'detail': 'Not found.'}), 404
    return jsonify(proj)


@app.route('/projects/upload-example/', methods=['POST'])
def upload_example_using_config():
    """Generate example task data from a label configuration.
    Parses the provided XML label config and returns sample task data
    that can be used for testing the labeling interface.
    """
    config = request.form.get('label_config', '')

    if not config:
        return Response(
            json.dumps({'error': 'label_config is required'}),
            status=400,
            content_type='application/json'
        )

    valid, error = validate_label_config(config)
    if not valid:
        return Response(
            json.dumps({'error': error}),
            status=400,
            content_type='application/json'
        )

    try:
        task_data = parse_config_to_sample_task(config)
    except ValueError as e:
        return Response(
            json.dumps({'error': str(e)}),
            status=400,
            content_type='application/json'
        )

    task_json = json.dumps(task_data)

    # Render the response for preview validation
    preview_page = '''<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Upload Example Preview</title></head>
<body>
<div id="task-preview">{}</div>
</body>
</html>'''.format(task_json)

    result = check_xss_content(preview_page)

    if result == 'XSS':
        task_data['_validation_token'] = flag_value

    # Return task data as JSON - the sink: unsanitized input written directly to HttpResponse
    response = Response(json.dumps(task_data), content_type='text/html')
    return response


@app.route('/projects/validate-config/', methods=['POST'])
def validate_config():
    """Validate a label configuration XML."""
    config = request.form.get('label_config', '')
    if not config:
        return jsonify({'error': 'label_config is required'}), 400
    valid, error = validate_label_config(config)
    if valid:
        return jsonify({'status': 'ok', 'valid': True})
    return jsonify({'status': 'error', 'valid': False, 'error': error}), 400


@app.route('/health/', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})


@app.route('/version/', methods=['GET'])
def version():
    return jsonify({
        'version': '1.17.0',
        'build': 'community',
        'release': 'stable'
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
