# encoding=utf8

from flask import Flask, request, redirect, abort, Response
import subprocess
import os
import re
import sys
import json
import hashlib
import time

import logging

logging.basicConfig(level=logging.WARNING)

reload(sys)
sys.setdefaultencoding('utf8')

app = Flask(__name__, static_folder='static', static_url_path='/static')

SECRET_TOKEN = open('secret.txt').read().strip()

WIKI_PAGES = {
    'HomePage': {
        'title': 'Welcome to OpenWiki',
        'content': '<p>OpenWiki is a collaborative wiki platform. Use the navigation to browse pages, edit content, and manage file attachments.</p><p>Get started by visiting the <a href="/DocumentationPage/view">Documentation</a> page or browsing the <a href="/pages">Page Index</a>.</p>',
        'owner': 'admin',
        'acl': '*',
        'time': '2024-11-15 10:30:00'
    },
    'DocumentationPage': {
        'title': 'Documentation',
        'content': '<p>Welcome to the OpenWiki documentation. This wiki supports:</p><ul><li>Page editing and versioning</li><li>File attachments via the attach handler</li><li>User access control lists</li><li>Full text search</li></ul><p>To attach a file to a page, use the upload handler: <code>/{PageName}/attach?file=yourfile.ext</code></p>',
        'owner': 'admin',
        'acl': '*',
        'time': '2024-11-15 11:00:00'
    },
    'SandboxPage': {
        'title': 'Sandbox',
        'content': '<p>This is a sandbox page for testing. Feel free to edit this page to try out wiki features.</p>',
        'owner': 'admin',
        'acl': '*',
        'time': '2024-11-20 09:15:00'
    },
    'ProjectNotes': {
        'title': 'Project Notes',
        'content': '<p>Meeting notes and project documentation are collected here.</p><ul><li>Sprint planning - weekly on Mondays</li><li>Retrospectives - bi-weekly on Fridays</li></ul>',
        'owner': 'editor',
        'acl': '*',
        'time': '2024-12-01 14:20:00'
    }
}

UPLOAD_DIR = 'uploads'
if not os.path.isdir(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

ATTACH_CONFIG = {
    'max_file_size': 2097152,
    'allowed_extensions': ['jpg', 'jpeg', 'png', 'gif', 'svg', 'pdf', 'doc', 'docx', 'txt', 'zip', 'odt'],
    'upload_path': UPLOAD_DIR
}


def render_layout(title, body_content, page_tag=None):
    nav_items = ''
    for tag in sorted(WIKI_PAGES.keys()):
        active = ' class="active"' if tag == page_tag else ''
        nav_items += '<li{}><a href="/{}/view">{}</a></li>'.format(active, tag, WIKI_PAGES[tag]['title'])

    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{title} - OpenWiki</title>
    <link rel="stylesheet" href="/static/css/wiki.css">
</head>
<body>
    <nav class="navbar">
        <div class="container">
            <a class="navbar-brand" href="/">OpenWiki</a>
            <ul class="nav-links">
                {nav_items}
                <li><a href="/pages">Index</a></li>
                <li><a href="/search">Search</a></li>
            </ul>
        </div>
    </nav>
    <div class="container main-content">
        {body}
    </div>
    <footer class="footer">
        <div class="container">
            <p>Powered by OpenWiki</p>
        </div>
    </footer>
</body>
</html>'''.format(title=title, nav_items=nav_items, body=body_content)


@app.route('/')
def index():
    return redirect('/HomePage/view')


@app.route('/pages')
def page_index():
    rows = ''
    for tag, info in sorted(WIKI_PAGES.items()):
        rows += '<tr><td><a href="/{}/view">{}</a></td><td>{}</td><td>{}</td></tr>'.format(
            tag, tag, info['owner'], info['time']
        )
    body = '''
        <h2>Page Index</h2>
        <table class="wiki-table">
            <thead><tr><th>Page</th><th>Owner</th><th>Last Modified</th></tr></thead>
            <tbody>{}</tbody>
        </table>
    '''.format(rows)
    return render_layout('Page Index', body)


@app.route('/<page_tag>/view')
def view_page(page_tag):
    page = WIKI_PAGES.get(page_tag)
    if not page:
        body = '<div class="alert alert-warning">Page <strong>{}</strong> does not exist. <a href="/{}/edit">Create it</a>.</div>'.format(
            page_tag, page_tag
        )
        return render_layout('Not Found', body), 404

    body = '''
        <div class="page-header">
            <h1>{title}</h1>
            <div class="page-actions">
                <a href="/{tag}/edit" class="btn btn-default">Edit</a>
                <a href="/{tag}/attach" class="btn btn-default">Attach File</a>
                <a href="/{tag}/backlinks" class="btn btn-default">Backlinks</a>
            </div>
        </div>
        <div class="page-content">{content}</div>
        <div class="page-meta">
            <small>Owner: {owner} | Last modified: {time} | <a href="#" onclick="reportPage()">Report to administrator</a></small>
        </div>
        <script>
        function reportPage() {{
            var url = window.location.href;
            var r = new XMLHttpRequest();
            r.open('POST', '/api/report', true);
            r.setRequestHeader('Content-Type', 'application/json');
            r.onreadystatechange = function() {{
                if (r.readyState === 4) {{
                    try {{
                        var resp = JSON.parse(r.responseText);
                        alert(resp.message || 'Report submitted');
                    }} catch(e) {{
                        alert('Report submitted');
                    }}
                }}
            }};
            r.send(JSON.stringify({{url: url}}));
        }}
        </script>
    '''.format(title=page['title'], tag=page_tag, content=page['content'],
               owner=page['owner'], time=page['time'])
    return render_layout(page['title'], body, page_tag)


def sanitize_html(text):
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&#x27;')
    return text


@app.route('/<page_tag>/edit', methods=['GET', 'POST'])
def edit_page(page_tag):
    if request.method == 'POST':
        content = sanitize_html(request.form.get('body', ''))
        title = sanitize_html(request.form.get('title', page_tag))
        if page_tag in WIKI_PAGES:
            WIKI_PAGES[page_tag]['content'] = content
            WIKI_PAGES[page_tag]['title'] = title
            WIKI_PAGES[page_tag]['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
        else:
            WIKI_PAGES[page_tag] = {
                'title': title,
                'content': content,
                'owner': 'anonymous',
                'acl': '*',
                'time': time.strftime('%Y-%m-%d %H:%M:%S')
            }
        return redirect('/{}/view'.format(page_tag))

    page = WIKI_PAGES.get(page_tag, {'title': page_tag, 'content': '', 'owner': '', 'acl': '*', 'time': ''})
    body = '''
        <h2>Editing: {title}</h2>
        <form method="POST" action="/{tag}/edit">
            <div class="form-group">
                <label for="title">Title</label>
                <input type="text" id="title" name="title" class="form-control" value="{title}">
            </div>
            <div class="form-group">
                <label for="body">Content</label>
                <textarea id="body" name="body" class="form-control" rows="15">{content}</textarea>
            </div>
            <button type="submit" class="btn btn-primary">Save</button>
            <a href="/{tag}/view" class="btn btn-default">Cancel</a>
        </form>
    '''.format(title=page['title'], tag=page_tag, content=page['content'])
    return render_layout('Edit - ' + page['title'], body, page_tag)


@app.route('/<page_tag>/attach', methods=['GET', 'POST'])
def attach_file(page_tag):
    if page_tag not in WIKI_PAGES:
        body = '<div class="alert alert-danger">Page <strong>{}</strong> does not exist.</div>'.format(page_tag)
        return render_layout('Error', body), 404

    if request.method == 'POST':
        uploaded = request.files.get('upFile')
        fname = request.form.get('file', '')
        if uploaded and fname:
            page_dir = os.path.join(ATTACH_CONFIG['upload_path'], page_tag)
            if not os.path.isdir(page_dir):
                os.makedirs(page_dir)
            safe_name = os.path.basename(fname)
            dest = os.path.join(page_dir, safe_name)
            uploaded.save(dest)
            body = '''
                <div class="alert alert-success">File <strong>{}</strong> uploaded successfully.</div>
                <p><a href="/{}/view">Back to page</a></p>
            '''.format(safe_name, page_tag)
        else:
            body = '<div class="alert alert-danger">Upload failed. No file provided.</div>'
        return render_layout('Upload Result', body, page_tag)

    file_param = request.args.get('file', '')
    upload_action = '/{}/attach'.format(page_tag)

    body = '<h3>Upload form for file ' + file_param + '</h3>\n'
    body += '''<form enctype="multipart/form-data" name="frmUpload" method="POST" action="{action}">
            <input type="hidden" name="wiki" value="{tag}/attach" />
            <input type="hidden" name="MAX_FILE_SIZE" value="{max_size}" />
            <input type="hidden" name="file" value="{file_val}" />
            <div class="form-group">
                <input type="file" name="upFile" class="form-control" />
            </div>
            <button type="submit" class="btn btn-primary"><i class="icon-upload"></i> Save</button>
        </form>
        <p><a href="/{tag}/view">Back to {tag}</a></p>
    '''.format(action=upload_action, tag=page_tag,
               max_size=ATTACH_CONFIG['max_file_size'],
               file_val=file_param.replace('"', '&quot;'))

    return render_layout('Upload - ' + page_tag, body, page_tag)


@app.route('/<page_tag>/backlinks')
def backlinks(page_tag):
    refs = []
    for tag, info in WIKI_PAGES.items():
        if page_tag in info.get('content', '') and tag != page_tag:
            refs.append(tag)
    items = ''.join('<li><a href="/{}/view">{}</a></li>'.format(t, t) for t in refs) if refs else '<li>No pages link here.</li>'
    body = '<h2>Pages linking to {}</h2><ul>{}</ul>'.format(page_tag, items)
    return render_layout('Backlinks - ' + page_tag, body, page_tag)


@app.route('/api/report', methods=['POST'])
def report_content():
    data = request.get_json(silent=True) or {}
    url = data.get('url', '')

    if not url:
        return Response(json.dumps({'status': 'error', 'message': 'URL parameter is required'}),
                       status=400, mimetype='application/json')

    host = os.getenv('SERVICE_HOST', 'localhost')
    port = os.getenv('SERVICE_PORT', '5000')
    base = 'http://{}:{}'.format(host, port)

    if not url.startswith(base) and not url.startswith('/'):
        return Response(json.dumps({'status': 'error', 'message': 'Only internal URLs can be reported'}),
                       status=400, mimetype='application/json')

    if url.startswith('/'):
        url = base + url

    proc = subprocess.Popen(
        ["timeout", "10", "phantomjs", "--ignore-ssl-errors=true", "reviewer.js"],
        stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE
    )
    try:
        review_payload = json.dumps({'url': url, 'token': SECRET_TOKEN})
        proc.stdin.write(review_payload + '\n')
        proc.stdin.close()
        stdout = proc.stdout.read().strip()
        proc.wait()
    except Exception:
        stdout = ''

    alert_data = []
    if stdout:
        for line in stdout.split('\n'):
            line = line.strip()
            if line.startswith('ALERT:'):
                alert_data.append(line[6:])

    if alert_data:
        return Response(json.dumps({
            'status': 'reviewed',
            'message': 'Content has been reviewed by an administrator',
            'admin_notes': alert_data
        }), status=200, mimetype='application/json')

    return Response(json.dumps({
        'status': 'reviewed',
        'message': 'Content has been reviewed by an administrator'
    }), status=200, mimetype='application/json')


@app.route('/search')
def search_pages():
    q = request.args.get('q', '')
    results = []
    if q:
        for tag, info in WIKI_PAGES.items():
            if q.lower() in info['content'].lower() or q.lower() in info['title'].lower():
                results.append({'tag': tag, 'title': info['title']})

    items = ''
    if q and results:
        for r in results:
            items += '<li><a href="/{}/view">{}</a></li>'.format(r['tag'], r['title'])
    elif q:
        items = '<li>No results found for <strong>{}</strong>.</li>'.format(q.replace('<', '&lt;').replace('>', '&gt;'))

    body = '''
        <h2>Search</h2>
        <form method="GET" action="/search">
            <div class="form-group search-group">
                <input type="text" name="q" class="form-control" placeholder="Search pages..." value="{}">
                <button type="submit" class="btn btn-primary">Search</button>
            </div>
        </form>
        <ul>{}</ul>
    '''.format(q.replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;'), items)
    return render_layout('Search', body)


@app.route('/ping')
def health():
    return 'ok'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
