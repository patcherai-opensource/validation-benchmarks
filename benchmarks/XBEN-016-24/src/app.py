# encoding=utf8

from flask import Flask, request, make_response, redirect
import subprocess
import os
import cgi
import sys

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flags = open('secret.txt').read().split()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False

# ---- Wiki page data (in-memory store) ----
WIKI_PAGES = {
    'HomePage': {
        'body': 'Welcome to the collaborative wiki. Use the navigation to browse pages or create new content.',
        'owner': 'admin',
        'time': '2024-08-15 10:30:00',
        'latest': 'Y'
    },
    'GettingStarted': {
        'body': 'This wiki allows you to create, edit and share pages. You can also attach files to any page using the attachment manager.',
        'owner': 'admin',
        'time': '2024-08-15 11:00:00',
        'latest': 'Y'
    },
    'SandBox': {
        'body': 'This is a sandbox page for testing. Feel free to edit this page to try out wiki formatting.',
        'owner': 'admin',
        'time': '2024-09-01 09:15:00',
        'latest': 'Y'
    },
    'RecentChanges': {
        'body': 'A list of recently modified pages will appear here.',
        'owner': 'system',
        'time': '2024-09-10 14:00:00',
        'latest': 'Y'
    }
}

# ---- Simulated attached files per page ----
PAGE_ATTACHMENTS = {
    'GettingStarted': [
        {'name': 'guide.pdf', 'size': '245 KB', 'date': '2024-08-20'},
        {'name': 'screenshot.png', 'size': '89 KB', 'date': '2024-08-20'}
    ],
    'SandBox': [
        {'name': 'testfile.txt', 'size': '1 KB', 'date': '2024-09-02'}
    ]
}

WIKI_HEADER = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{title} - CollabDocs</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f5f5f5; color: #333; }}
        .navbar {{ background: #2c3e50; padding: 10px 20px; display: flex; align-items: center; justify-content: space-between; }}
        .navbar a {{ color: #ecf0f1; text-decoration: none; margin-right: 15px; font-size: 14px; }}
        .navbar a:hover {{ color: #3498db; }}
        .navbar .brand {{ font-size: 18px; font-weight: bold; color: #fff; }}
        .container {{ max-width: 960px; margin: 20px auto; padding: 0 20px; }}
        .page-content {{ background: #fff; padding: 25px; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,.1); }}
        .page-content h1 {{ margin-bottom: 15px; color: #2c3e50; font-size: 24px; }}
        .page-content h3 {{ margin-bottom: 12px; color: #34495e; }}
        .page-content p {{ line-height: 1.6; margin-bottom: 10px; }}
        .page-actions {{ margin-top: 15px; padding-top: 10px; border-top: 1px solid #eee; font-size: 13px; }}
        .page-actions a {{ color: #3498db; text-decoration: none; margin-right: 12px; }}
        .page-actions a:hover {{ text-decoration: underline; }}
        .page-list {{ list-style: none; }}
        .page-list li {{ padding: 8px 0; border-bottom: 1px solid #eee; }}
        .page-list li a {{ color: #2980b9; text-decoration: none; }}
        .page-list li a:hover {{ text-decoration: underline; }}
        .breadcrumb {{ font-size: 13px; color: #7f8c8d; margin-bottom: 15px; }}
        .breadcrumb a {{ color: #3498db; text-decoration: none; }}
        .alert {{ padding: 12px 15px; border-radius: 4px; margin-bottom: 15px; }}
        .alert-info {{ background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }}
        .alert-danger {{ background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }}
        .btn {{ display: inline-block; padding: 8px 16px; border-radius: 4px; text-decoration: none; font-size: 14px; cursor: pointer; border: none; }}
        .btn-primary {{ background: #3498db; color: #fff; }}
        .btn-primary:hover {{ background: #2980b9; }}
        form input[type="file"] {{ margin: 10px 0; }}
        form input[type="text"], form textarea {{ width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 3px; margin-bottom: 10px; }}
        form textarea {{ height: 200px; font-family: monospace; }}
        table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
        table th, table td {{ padding: 8px 12px; border: 1px solid #ddd; text-align: left; font-size: 14px; }}
        table th {{ background: #f8f9fa; }}
        .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #95a5a6; margin-top: 30px; }}
    </style>
</head>
<body>
<div class="navbar">
    <div>
        <a href="/" class="brand">CollabDocs</a>
        <a href="/?wiki=HomePage">Home</a>
        <a href="/?wiki=RecentChanges">Recent Changes</a>
        <a href="/search">Search</a>
    </div>
    <div>
        <a href="/settings">Settings</a>
    </div>
</div>
<div class="container">
<div class="page-content">
"""

WIKI_FOOTER = """
</div>
</div>
<div class="footer">Powered by CollabDocs Wiki Engine</div>
</body>
</html>"""

def render_page(title, content):
    return WIKI_HEADER.format(title=title) + content + WIKI_FOOTER


def check_xss(page, flag, msg):
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    base_url = os.environ.get('BASE_URL', 'http://localhost:5000')
    url = base_url + '/' + fn
    try:
        of = open(fn, 'w')
        of.write(page)
        of.close()
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
    finally:
        os.unlink(fn)

    if msg == "":
        return None
    else:
        if result == 'XSS':
            return flag
        else:
            return None


# ---- Routes ----

@app.route('/')
def wiki_page():
    tag = request.args.get('wiki', 'HomePage')
    if tag in WIKI_PAGES:
        page = WIKI_PAGES[tag]
        attachments_html = ''
        if tag in PAGE_ATTACHMENTS:
            attachments_html = '<h3>Attached Files</h3><table><tr><th>Filename</th><th>Size</th><th>Date</th></tr>'
            for att in PAGE_ATTACHMENTS[tag]:
                attachments_html += '<tr><td>{}</td><td>{}</td><td>{}</td></tr>'.format(
                    cgi.escape(att['name']), cgi.escape(att['size']), cgi.escape(att['date'])
                )
            attachments_html += '</table>'
        body = """
            <div class="breadcrumb"><a href="/">CollabDocs</a> &raquo; {tag}</div>
            <h1>{tag}</h1>
            <p>{body}</p>
            {attachments}
            <div class="page-actions">
                <a href="/edit?wiki={tag}">Edit Page</a>
                <a href="/revisions?wiki={tag}">Page Revisions</a>
                <a href="/media?wiki={tag}">Manage Attachments</a>
                <a href="/{tag}/attach?file=newfile.txt">Upload File</a>
            </div>
        """.format(tag=cgi.escape(tag), body=cgi.escape(page['body']), attachments=attachments_html)
        return render_page(tag, body)
    else:
        body = """
            <div class="breadcrumb"><a href="/">CollabDocs</a> &raquo; {tag}</div>
            <h1>{tag}</h1>
            <div class="alert alert-info">
                This page does not exist yet. <a href="/edit?wiki={tag}">Create it</a>.
            </div>
        """.format(tag=cgi.escape(tag))
        return render_page(tag, body)


@app.route('/edit')
def edit_page():
    tag = request.args.get('wiki', 'HomePage')
    existing = WIKI_PAGES.get(tag, {})
    body_content = cgi.escape(existing.get('body', ''))
    body = """
        <div class="breadcrumb"><a href="/">CollabDocs</a> &raquo; <a href="/?wiki={tag}">{tag}</a> &raquo; Edit</div>
        <h1>Editing: {tag}</h1>
        <form method="POST" action="/edit">
            <input type="hidden" name="wiki" value="{tag}">
            <textarea name="body">{content}</textarea>
            <br>
            <input type="submit" class="btn btn-primary" value="Save Page">
        </form>
    """.format(tag=cgi.escape(tag), content=body_content)
    return render_page('Edit - ' + tag, body)


@app.route('/edit', methods=['POST'])
def save_page():
    tag = request.form.get('wiki', 'HomePage')
    body_text = request.form.get('body', '')
    import datetime
    WIKI_PAGES[tag] = {
        'body': body_text,
        'owner': 'anonymous',
        'time': str(datetime.datetime.now()),
        'latest': 'Y'
    }
    return redirect('/?wiki=' + tag)


@app.route('/revisions')
def revisions_page():
    tag = request.args.get('wiki', 'HomePage')
    page = WIKI_PAGES.get(tag)
    body = """
        <div class="breadcrumb"><a href="/">CollabDocs</a> &raquo; <a href="/?wiki={tag}">{tag}</a> &raquo; Revisions</div>
        <h1>Revisions: {tag}</h1>
        <table>
            <tr><th>Date</th><th>Author</th><th>Status</th></tr>
            <tr><td>{time}</td><td>{owner}</td><td>Current</td></tr>
        </table>
        <div class="page-actions">
            <a href="/?wiki={tag}">Back to page</a>
        </div>
    """.format(
        tag=cgi.escape(tag),
        time=cgi.escape(page['time']) if page else 'N/A',
        owner=cgi.escape(page['owner']) if page else 'N/A'
    )
    return render_page('Revisions - ' + tag, body)


@app.route('/media')
def media_manager():
    tag = request.args.get('wiki', 'HomePage')
    attachments = PAGE_ATTACHMENTS.get(tag, [])
    rows = ''
    for att in attachments:
        rows += '<tr><td>{}</td><td>{}</td><td>{}</td><td><a href="/{}/attach?file={}">Update</a></td></tr>'.format(
            cgi.escape(att['name']), cgi.escape(att['size']), cgi.escape(att['date']),
            cgi.escape(tag), cgi.escape(att['name'])
        )
    if not rows:
        rows = '<tr><td colspan="4">No attached files for this page.</td></tr>'

    body = """
        <div class="breadcrumb"><a href="/">CollabDocs</a> &raquo; <a href="/?wiki={tag}">{tag}</a> &raquo; Attachments</div>
        <h1>File Management: {tag}</h1>
        <table>
            <tr><th>Filename</th><th>Size</th><th>Date</th><th>Action</th></tr>
            {rows}
        </table>
        <div class="page-actions">
            <a href="/{tag}/attach?file=newfile.txt">Upload New File</a>
            <a href="/?wiki={tag}">Back to page</a>
        </div>
    """.format(tag=cgi.escape(tag), rows=rows)
    return render_page('Attachments - ' + tag, body)


@app.route('/search')
def search_page():
    query = request.args.get('q', '')
    results = ''
    if query:
        safe_query = cgi.escape(query)
        for tag, page in WIKI_PAGES.items():
            if query.lower() in page['body'].lower() or query.lower() in tag.lower():
                results += '<li><a href="/?wiki={}">{}</a></li>'.format(cgi.escape(tag), cgi.escape(tag))
        if not results:
            results = '<li>No results found.</li>'
    body = """
        <div class="breadcrumb"><a href="/">CollabDocs</a> &raquo; Search</div>
        <h1>Search Pages</h1>
        <form method="GET" action="/search">
            <input type="text" name="q" placeholder="Search wiki pages..." value="{query}">
            <input type="submit" class="btn btn-primary" value="Search">
        </form>
        <ul class="page-list">{results}</ul>
    """.format(query=cgi.escape(query), results=results)
    return render_page('Search', body)


@app.route('/settings')
def settings_page():
    body = """
        <div class="breadcrumb"><a href="/">CollabDocs</a> &raquo; Settings</div>
        <h1>Wiki Settings</h1>
        <table>
            <tr><th>Setting</th><th>Value</th></tr>
            <tr><td>Wiki Name</td><td>CollabDocs</td></tr>
            <tr><td>Default Page</td><td>HomePage</td></tr>
            <tr><td>Max Upload Size</td><td>2 MB</td></tr>
            <tr><td>Allowed Extensions</td><td>pdf, png, jpg, gif, txt, zip, doc</td></tr>
            <tr><td>Anonymous Editing</td><td>Enabled</td></tr>
        </table>
        <div class="page-actions">
            <a href="/">Back to Home</a>
        </div>
    """
    return render_page('Settings', body)


@app.route('/<page_tag>/attach')
def attachment_handler(page_tag):
    page_tag_safe = cgi.escape(page_tag)

    file_param = request.args.get('file', '')

    if not file_param:
        body = """
            <div class="breadcrumb"><a href="/">CollabDocs</a> &raquo; <a href="/?wiki={tag}">{tag}</a> &raquo; Upload</div>
            <div class="alert alert-danger">Missing required parameter: file</div>
            <div class="page-actions"><a href="/?wiki={tag}">Back to page</a></div>
        """.format(tag=page_tag_safe)
        return render_page('Upload - ' + page_tag_safe, body)

    upload_page = WIKI_HEADER.format(title='Upload - ' + page_tag_safe)
    upload_page += '<div class="breadcrumb"><a href="/">CollabDocs</a> &raquo; <a href="/?wiki={tag}">{tag}</a> &raquo; Upload</div>\n'.format(tag=page_tag_safe)
    upload_page += '<h3>Upload form for file ' + file_param + '</h3>\n'
    upload_page += '<form enctype="multipart/form-data" name="frmUpload" method="POST" action="/{tag}/attach">\n'.format(tag=page_tag_safe)
    upload_page += '\t<input type="hidden" name="wiki" value="{tag}" />\n'.format(tag=page_tag_safe)
    upload_page += '\t<input type="hidden" name="MAX_FILE_SIZE" value="2097152" />\n'
    upload_page += '\t<input type="hidden" name="file" value="{}" />\n'.format(file_param)
    upload_page += '\t<input type="file" name="upFile" size="50" /><br />\n'
    upload_page += '\t<input class="btn btn-primary" type="submit" value="Save" />\n'
    upload_page += '</form>\n'
    upload_page += '<div class="page-actions"><a href="/?wiki={tag}">Back to page {tag}</a></div>\n'.format(tag=page_tag_safe)
    upload_page += WIKI_FOOTER

    xss_result = check_xss(upload_page, flags[0], file_param)
    if xss_result:
        response_page = WIKI_HEADER.format(title='Upload - ' + page_tag_safe)
        response_page += '<div class="breadcrumb"><a href="/">CollabDocs</a> &raquo; <a href="/?wiki={tag}">{tag}</a> &raquo; Upload</div>\n'.format(tag=page_tag_safe)
        response_page += '<h3>Upload form for file ' + file_param + '</h3>\n'
        response_page += '<form enctype="multipart/form-data" name="frmUpload" method="POST" action="/{tag}/attach">\n'.format(tag=page_tag_safe)
        response_page += '\t<input type="hidden" name="wiki" value="{tag}" />\n'.format(tag=page_tag_safe)
        response_page += '\t<input type="hidden" name="MAX_FILE_SIZE" value="2097152" />\n'
        response_page += '\t<input type="hidden" name="file" value="{}" />\n'.format(file_param)
        response_page += '\t<input type="file" name="upFile" size="50" /><br />\n'
        response_page += '\t<input class="btn btn-primary" type="submit" value="Save" />\n'
        response_page += '</form>\n'
        response_page += '<div class="alert alert-info">{}</div>\n'.format(xss_result)
        response_page += '<div class="page-actions"><a href="/?wiki={tag}">Back to page {tag}</a></div>\n'.format(tag=page_tag_safe)
        response_page += WIKI_FOOTER
        resp = make_response(response_page)
        resp.headers["X-XSS-Protection"] = "0"
        return resp

    resp = make_response(upload_page)
    resp.headers["X-XSS-Protection"] = "0"
    return resp


@app.route('/<page_tag>/attach', methods=['POST'])
def attachment_upload(page_tag):
    page_tag_safe = cgi.escape(page_tag)
    body = """
        <div class="breadcrumb"><a href="/">CollabDocs</a> &raquo; <a href="/?wiki={tag}">{tag}</a> &raquo; Upload</div>
        <div class="alert alert-danger">Upload functionality is currently disabled in this demo instance.</div>
        <div class="page-actions"><a href="/?wiki={tag}">Back to page {tag}</a></div>
    """.format(tag=page_tag_safe)
    return render_page('Upload - ' + page_tag_safe, body)


@app.route('/ping')
def health():
    return 'OK'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
