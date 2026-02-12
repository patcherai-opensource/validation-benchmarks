# encoding=utf8

from flask import Flask, request, Response, make_response, redirect
import json
import subprocess
import os
import sys
import xml.etree.ElementTree as ET
import time
import logging

logging.basicConfig(level=logging.WARNING)

reload(sys)
sys.setdefaultencoding('utf8')

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24).encode('hex')

projects_store = {}
next_project_id = 1


def generate_sample_task(label_config):
    """Parse a labeling configuration XML and generate corresponding sample task data.

    Walks the XML tree to find elements with 'value' attributes referencing data fields
    (prefixed with $), then produces representative sample content for each field based
    on the element tag type.
    """
    try:
        root = ET.fromstring(label_config.encode('utf-8'))
    except ET.ParseError as e:
        return None, str(e)

    task_data = {}

    for elem in root.iter():
        value_attr = elem.get('value', '')
        if value_attr.startswith('$'):
            # Extract the field reference; the value attribute format is $field_name
            # The full value content is used as sample data for that field
            field_ref = value_attr[1:]
            # Split on first non-alphanumeric/underscore to get the field name
            field_name = ''
            for ch in field_ref:
                if ch.isalnum() or ch == '_':
                    field_name += ch
                else:
                    break
            if not field_name:
                field_name = 'data'

            tag_name = elem.tag.lower()
            if tag_name in ('image',):
                task_data[field_name] = '/static/samples/example.jpg'
            elif tag_name in ('audio',):
                task_data[field_name] = '/static/samples/example.wav'
            elif tag_name in ('video',):
                task_data[field_name] = '/static/samples/example.mp4'
            else:
                # Use the full value content (without the $ prefix) as the sample text
                task_data[field_name] = value_attr[1:]

    if not task_data:
        task_data = {"data": "Example task data"}

    return task_data, None


@app.route('/')
def index():
    project_html = ''
    if projects_store:
        project_html = '<ul class="project-list">'
        for pid, proj in projects_store.items():
            project_html += '<li><a href="/projects/%d">%s</a> <span class="meta">%d tasks &middot; %s</span></li>' % (
                pid, proj.get('title', 'Untitled'), proj.get('task_count', 0), proj.get('created_at', ''))
        project_html += '</ul>'
    else:
        project_html = '<div class="empty">No projects yet. Create one to get started.</div>'

    return make_response('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Label Studio</title>
    <style>
        *{margin:0;padding:0;box-sizing:border-box}
        body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#f5f5f5}
        .topbar{background:#fff;border-bottom:1px solid #e0e0e0;padding:12px 24px;display:flex;align-items:center}
        .topbar svg{margin-right:10px}
        .topbar h1{font-size:18px;font-weight:600;color:#1f1f1f}
        .nav{background:#fff;border-bottom:1px solid #e0e0e0;padding:0 24px}
        .nav a{display:inline-block;padding:12px 16px;color:#666;text-decoration:none;font-size:14px;border-bottom:2px solid transparent}
        .nav a:hover,.nav a.active{color:#2196F3;border-bottom-color:#2196F3}
        .wrap{max-width:1100px;margin:24px auto;padding:0 24px}
        .card{background:#fff;border-radius:8px;box-shadow:0 1px 3px rgba(0,0,0,.08);padding:24px;margin-bottom:16px}
        .card h2{font-size:16px;margin-bottom:16px;color:#333}
        .project-list{list-style:none}
        .project-list li{padding:12px 0;border-bottom:1px solid #f0f0f0;display:flex;justify-content:space-between;align-items:center}
        .project-list li:last-child{border-bottom:none}
        .project-list a{color:#2196F3;text-decoration:none;font-weight:500}
        .meta{font-size:12px;color:#999}
        .btn{display:inline-block;padding:8px 16px;background:#2196F3;color:#fff;border:none;border-radius:4px;cursor:pointer;text-decoration:none;font-size:14px}
        .btn:hover{background:#1976D2}
        .empty{color:#999;font-size:14px;text-align:center;padding:40px 0}
        p{font-size:14px;color:#666;line-height:1.6}
    </style>
</head>
<body>
    <div class="topbar">
        <svg width="32" height="32" viewBox="0 0 32 32" fill="none"><rect width="32" height="32" rx="6" fill="#2196F3"/><text x="7" y="23" fill="white" font-size="18" font-weight="bold">LS</text></svg>
        <h1>Label Studio</h1>
    </div>
    <div class="nav">
        <a href="/" class="active">Projects</a>
        <a href="/api/projects">API</a>
        <a href="/import">Import</a>
        <a href="/user/account">Account</a>
    </div>
    <div class="wrap">
        <div class="card">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
                <h2>Projects</h2>
                <a class="btn" href="/projects/create">Create Project</a>
            </div>
            %s
        </div>
        <div class="card">
            <h2>Quick Start</h2>
            <p>Label Studio is an open source data labeling tool. Create a project, configure your labeling interface,
            import data, and start annotating.</p>
        </div>
    </div>
</body>
</html>''' % project_html)


@app.route('/api/projects', methods=['GET'])
def api_projects_list():
    result = []
    for pid, proj in projects_store.items():
        result.append({
            "id": pid,
            "title": proj.get("title", ""),
            "created_at": proj.get("created_at", ""),
            "task_count": proj.get("task_count", 0),
        })
    return Response(json.dumps(result), content_type='application/json')


@app.route('/projects/create', methods=['GET', 'POST'])
def create_project():
    global next_project_id
    if request.method == 'POST':
        title = request.form.get('title', 'Untitled Project')
        label_config = request.form.get('label_config', '<View></View>')

        pid = next_project_id
        next_project_id += 1
        projects_store[pid] = {
            "title": title,
            "label_config": label_config,
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "task_count": 0,
        }
        return redirect('/')

    return make_response('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Create Project - Label Studio</title>
    <style>
        *{margin:0;padding:0;box-sizing:border-box}
        body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#f5f5f5}
        .topbar{background:#fff;border-bottom:1px solid #e0e0e0;padding:12px 24px}
        .topbar h1{font-size:18px;font-weight:600;color:#333}
        .wrap{max-width:800px;margin:24px auto;padding:0 24px}
        .card{background:#fff;border-radius:8px;box-shadow:0 1px 3px rgba(0,0,0,.08);padding:24px}
        label{display:block;font-size:14px;font-weight:500;margin-bottom:6px;color:#333}
        input[type="text"],textarea{width:100%%;padding:8px 12px;border:1px solid #ddd;border-radius:4px;font-size:14px;font-family:inherit}
        textarea{height:200px;font-family:'SF Mono','Monaco','Inconsolata',monospace;font-size:13px}
        .fg{margin-bottom:16px}
        .btn{padding:10px 20px;background:#2196F3;color:#fff;border:none;border-radius:4px;cursor:pointer;font-size:14px}
        .btn:hover{background:#1976D2}
        .help{font-size:12px;color:#999;margin-top:4px}
    </style>
</head>
<body>
    <div class="topbar"><h1>Create Project</h1></div>
    <div class="wrap">
        <div class="card">
            <form method="POST">
                <div class="fg">
                    <label>Project Name</label>
                    <input type="text" name="title" placeholder="My Project" required>
                </div>
                <div class="fg">
                    <label>Labeling Configuration</label>
                    <textarea name="label_config" placeholder="<View>&#10;  <Text name=&quot;text&quot; value=&quot;$text&quot;/>&#10;  <Choices name=&quot;sentiment&quot; toName=&quot;text&quot;>&#10;    <Choice value=&quot;Positive&quot;/>&#10;    <Choice value=&quot;Negative&quot;/>&#10;  </Choices>&#10;</View>"></textarea>
                    <p class="help">Define your labeling interface using Label Studio XML tags.</p>
                </div>
                <button type="submit" class="btn">Create</button>
            </form>
        </div>
    </div>
</body>
</html>''')


@app.route('/projects/<int:project_id>')
def project_detail(project_id):
    proj = projects_store.get(project_id)
    if not proj:
        return make_response(
            json.dumps({"detail": "Not found."}), 404,
            {'Content-Type': 'application/json'})
    return Response(json.dumps(proj), content_type='application/json')


@app.route('/projects/upload-example/', methods=['POST'])
def upload_example_using_config():
    """Generate example task data from a labeling configuration.

    Accepts label_config (XML) via POST and returns generated example task
    data as JSON so the frontend can display a preview of what tasks will
    look like with the given configuration.
    """
    config = request.form.get('label_config', '')

    if not config:
        return Response(
            json.dumps({"error": "label_config is required"}),
            status=400,
            content_type='application/json')

    task_data, error = generate_sample_task(config)

    if error:
        return Response(
            json.dumps({"error": "Invalid label config", "detail": error}),
            status=400,
            content_type='application/json')

    # Return the task data as JSON
    # Note: Content-Type defaults to text/html in Flask Response
    response = Response(json.dumps(task_data))
    return response


@app.route('/projects/validate-config/', methods=['POST'])
def validate_config():
    config = request.form.get('label_config', '')
    if not config:
        return Response(
            json.dumps({"error": "label_config is required"}),
            status=400, content_type='application/json')
    try:
        root = ET.fromstring(config.encode('utf-8'))
        tags = sum(1 for _ in root.iter())
        return Response(
            json.dumps({"status": "ok", "tag_count": tags}),
            content_type='application/json')
    except ET.ParseError as e:
        return Response(
            json.dumps({"status": "error", "detail": str(e)}),
            status=400, content_type='application/json')


@app.route('/projects/render-example/', methods=['POST'])
def render_example():
    """Render a preview of example task data.

    This endpoint processes the label config, generates example task data,
    and renders a visual preview. A headless browser verifies that the
    configuration produces valid output.
    """
    config = request.form.get('label_config', '')

    if not config:
        return Response(
            json.dumps({"error": "label_config is required"}),
            status=400, content_type='application/json')

    task_data, error = generate_sample_task(config)

    if error:
        return Response(
            json.dumps({"error": "Invalid label config", "detail": error}),
            status=400, content_type='application/json')

    # Build an HTML preview page that renders the task data fields
    preview_body = ''
    for key, value in task_data.items():
        preview_body += '<div class="field"><strong>%s:</strong> <span>%s</span></div>\n' % (key, value)

    preview_html = '''<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Task Preview</title></head>
<body>
<div id="task-preview">
%s
</div>
</body></html>''' % preview_body

    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    host = os.environ.get('APP_HOST', 'localhost')
    port = os.environ.get('APP_PORT', '5000')
    url = 'http://{}:{}/{}'.format(host, port, fn)

    result_text = ''
    try:
        with open(fn, 'w') as f:
            f.write(preview_html)
        proc = subprocess.Popen(
            ["timeout", "5", "phantomjs", "check.js"],
            stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        proc.stdin.write(url)
        proc.stdin.close()
        result_text = proc.stdout.readline().strip()
    except Exception:
        pass
    finally:
        try:
            os.unlink(fn)
        except OSError:
            pass

    flag_content = open('secret.txt').read().strip()

    if result_text == 'XSS':
        return Response(
            json.dumps({
                "status": "warning",
                "message": "Security alert: potentially unsafe content detected in configuration",
                "debug_token": flag_content
            }),
            content_type='application/json')
    elif result_text:
        return Response(
            json.dumps({
                "status": "info",
                "preview_output": result_text
            }),
            content_type='application/json')
    else:
        return Response(
            json.dumps({
                "status": "ok",
                "message": "Preview rendered successfully",
                "task_data": task_data
            }),
            content_type='application/json')


@app.route('/import', methods=['GET'])
def import_page():
    return make_response('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Import Data - Label Studio</title>
    <style>
        *{margin:0;padding:0;box-sizing:border-box}
        body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#f5f5f5}
        .topbar{background:#fff;border-bottom:1px solid #e0e0e0;padding:12px 24px}
        .topbar h1{font-size:18px;font-weight:600;color:#333}
        .wrap{max-width:800px;margin:24px auto;padding:0 24px}
        .card{background:#fff;border-radius:8px;box-shadow:0 1px 3px rgba(0,0,0,.08);padding:24px;margin-bottom:16px}
        .card h2{font-size:16px;margin-bottom:12px;color:#333}
        p{font-size:14px;color:#666;line-height:1.6}
        code{background:#f0f0f0;padding:2px 6px;border-radius:3px;font-size:13px}
    </style>
</head>
<body>
    <div class="topbar"><h1>Import Data</h1></div>
    <div class="wrap">
        <div class="card">
            <h2>Import Tasks</h2>
            <p>Select a project first, then upload your data in JSON, CSV, or TSV format. You can also
            connect cloud storage (S3, GCS, Azure) for larger datasets.</p>
        </div>
        <div class="card">
            <h2>Supported Formats</h2>
            <p><code>JSON</code> &middot; <code>CSV</code> &middot; <code>TSV</code> &middot;
            <code>CoNLL</code> &middot; <code>COCO</code> &middot; <code>VOC</code></p>
        </div>
    </div>
</body>
</html>''')


@app.route('/user/account')
def user_account():
    return make_response('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Account - Label Studio</title>
    <style>
        *{margin:0;padding:0;box-sizing:border-box}
        body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#f5f5f5}
        .topbar{background:#fff;border-bottom:1px solid #e0e0e0;padding:12px 24px}
        .topbar h1{font-size:18px;font-weight:600;color:#333}
        .wrap{max-width:800px;margin:24px auto;padding:0 24px}
        .card{background:#fff;border-radius:8px;box-shadow:0 1px 3px rgba(0,0,0,.08);padding:24px;margin-bottom:16px}
        .card h2{font-size:16px;margin-bottom:12px;color:#333}
        .row{padding:8px 0;font-size:14px;color:#666;border-bottom:1px solid #f0f0f0}
        .row:last-child{border-bottom:none}
        .lbl{font-weight:500;color:#333;display:inline-block;width:120px}
    </style>
</head>
<body>
    <div class="topbar"><h1>Account Settings</h1></div>
    <div class="wrap">
        <div class="card">
            <h2>Profile</h2>
            <div class="row"><span class="lbl">Username:</span> admin</div>
            <div class="row"><span class="lbl">Email:</span> admin@localhost</div>
            <div class="row"><span class="lbl">Role:</span> Administrator</div>
        </div>
        <div class="card">
            <h2>Access Token</h2>
            <div class="row">Token: &#8226;&#8226;&#8226;&#8226;&#8226;&#8226;&#8226;&#8226;&#8226;&#8226;&#8226;&#8226;</div>
        </div>
    </div>
</body>
</html>''')


@app.route('/api/health')
def api_health():
    return Response(json.dumps({"status": "UP"}), content_type='application/json')


@app.route('/version')
def version_info():
    return Response(
        json.dumps({"version": "1.17.0", "branch": "master", "build": "2024.01.15"}),
        content_type='application/json')


@app.errorhandler(404)
def not_found(e):
    return make_response('''<!DOCTYPE html>
<html><head><title>404 - Label Studio</title>
<style>body{font-family:-apple-system,sans-serif;text-align:center;padding:80px;color:#666}h1{color:#333}</style>
</head><body><h1>404</h1><p>Page not found</p><a href="/" style="color:#2196F3">Back to projects</a></body></html>''', 404)


@app.errorhandler(500)
def internal_error(e):
    return make_response('''<!DOCTYPE html>
<html><head><title>Error - Label Studio</title>
<style>body{font-family:-apple-system,sans-serif;text-align:center;padding:80px;color:#666}h1{color:#333}</style>
</head><body><h1>Internal Server Error</h1><p>Something went wrong.</p></body></html>''', 500)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
