# encoding=utf8

from flask import Flask, request, Response, make_response, redirect
import subprocess
import os
import sys
import json
import time
import hashlib
import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False
app.secret_key = os.urandom(24).encode('hex')

# Wiki configuration
WIKI_NAME = "OpenWiki"
WIKI_VERSION = "4.5.3"
ADMIN_TOKEN = hashlib.sha256(os.urandom(32)).hexdigest()

# Simple in-memory wiki page storage
wiki_pages = {
    "PagePrincipale": {
        "title": "Page Principale",
        "content": "<p>Welcome to <strong>OpenWiki</strong>, a collaborative wiki engine.</p>"
                   "<p>This is the main page of the wiki. You can navigate to different pages "
                   "using the menu above.</p>"
                   "<h2>Getting Started</h2>"
                   "<ul>"
                   "<li>Browse existing pages using the navigation</li>"
                   "<li>Upload files to pages using the attachment system</li>"
                   "<li>Edit pages to contribute content</li>"
                   "</ul>",
        "last_modified": "2024-11-15 10:30:00",
        "author": "admin"
    },
    "Documentation": {
        "title": "Documentation",
        "content": "<p>This section contains documentation for the OpenWiki platform.</p>"
                   "<h2>Features</h2>"
                   "<ul>"
                   "<li>Page management and editing</li>"
                   "<li>File attachments and uploads</li>"
                   "<li>User management</li>"
                   "<li>Search functionality</li>"
                   "</ul>"
                   "<h2>API</h2>"
                   "<p>OpenWiki provides a REST-like interface for managing content.</p>",
        "last_modified": "2024-11-14 08:15:00",
        "author": "admin"
    },
    "SandBox": {
        "title": "Sand Box",
        "content": "<p>This is the sandbox page. Feel free to test wiki features here.</p>"
                   "<p>You can upload files to this page using the attachment button.</p>",
        "last_modified": "2024-11-13 16:45:00",
        "author": "admin"
    },
    "RecentChanges": {
        "title": "Recent Changes",
        "content": "<p>Track of recently modified pages.</p>"
                   "<ul>"
                   "<li>2024-11-15: PagePrincipale (admin)</li>"
                   "<li>2024-11-14: Documentation (admin)</li>"
                   "<li>2024-11-13: SandBox (admin)</li>"
                   "</ul>",
        "last_modified": "2024-11-15 10:30:00",
        "author": "system"
    }
}

# Uploaded files storage (in-memory)
uploaded_files = {}

# CSS styles adapted for wiki look
WIKI_CSS = """
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, sans-serif;
    margin: 0; padding: 0;
    background: #f4f4f4;
    color: #333;
}
.wiki-header {
    background: #2c3e50;
    color: white;
    padding: 10px 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.wiki-header h1 { margin: 0; font-size: 1.4em; }
.wiki-header h1 a { color: white; text-decoration: none; }
.wiki-header nav a {
    color: #bdc3c7; text-decoration: none; margin-left: 15px; font-size: 0.9em;
}
.wiki-header nav a:hover { color: white; }
.wiki-content {
    max-width: 960px; margin: 20px auto; padding: 20px;
    background: white; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
.wiki-content h2 { color: #2c3e50; border-bottom: 1px solid #eee; padding-bottom: 8px; }
.wiki-content h3 { color: #34495e; }
.page-actions {
    background: #ecf0f1; padding: 8px 20px; font-size: 0.85em;
    border-bottom: 1px solid #ddd;
}
.page-actions a { color: #2c3e50; text-decoration: none; margin-right: 12px; }
.page-actions a:hover { text-decoration: underline; }
.upload-form {
    border: 2px dashed #bdc3c7; padding: 30px; text-align: center;
    margin: 20px 0; border-radius: 6px; background: #fafafa;
}
.upload-form input[type=file] { margin: 10px 0; }
.upload-form input[type=submit] {
    background: #2c3e50; color: white; border: none; padding: 8px 20px;
    border-radius: 4px; cursor: pointer;
}
.upload-form input[type=submit]:hover { background: #34495e; }
.wiki-footer {
    text-align: center; padding: 20px; color: #999; font-size: 0.8em;
}
table { border-collapse: collapse; width: 100%; margin: 10px 0; }
th, td { border: 1px solid #ddd; padding: 8px 12px; text-align: left; }
th { background: #f5f5f5; }
.search-form input[type=text] {
    padding: 5px 10px; border: 1px solid #bdc3c7; border-radius: 3px; width: 200px;
}
.search-form input[type=submit] {
    padding: 5px 12px; background: #3498db; color: white; border: none;
    border-radius: 3px; cursor: pointer;
}
.breadcrumb { font-size: 0.85em; color: #777; margin-bottom: 15px; }
.breadcrumb a { color: #3498db; text-decoration: none; }
.file-list { list-style: none; padding: 0; }
.file-list li { padding: 5px 0; border-bottom: 1px solid #f0f0f0; }
.file-list li a { color: #3498db; text-decoration: none; }
.alert { padding: 10px 15px; border-radius: 4px; margin: 10px 0; }
.alert-info { background: #d6eaf8; color: #2471a3; }
.alert-error { background: #fadbd8; color: #c0392b; }
"""


def render_header(current_page=""):
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{title} - {wiki}</title>
    <style>{css}</style>
</head>
<body>
<div class="wiki-header">
    <h1><a href="/">{wiki}</a></h1>
    <nav>
        <a href="/?PagePrincipale">Home</a>
        <a href="/?Documentation">Documentation</a>
        <a href="/?SandBox">SandBox</a>
        <a href="/?RecentChanges">Recent Changes</a>
        <form class="search-form" style="display:inline" method="get" action="/search">
            <input type="text" name="q" placeholder="Search...">
            <input type="submit" value="Search">
        </form>
    </nav>
</div>
""".format(title=current_page or WIKI_NAME, wiki=WIKI_NAME, css=WIKI_CSS)


def render_footer():
    return """
<div class="wiki-footer">
    <p>{wiki} {version} &mdash; Powered by OpenWiki Engine</p>
</div>
</body>
</html>
""".format(wiki=WIKI_NAME, version=WIKI_VERSION)


def render_page_actions(page_tag):
    return """
<div class="page-actions">
    <a href="/?{tag}">View</a>
    <a href="/?{tag}/edit">Edit</a>
    <a href="/?{tag}/upload">Attach file</a>
    <a href="/?{tag}/revisions">Revisions</a>
</div>
""".format(tag=page_tag)


@app.route('/')
def wiki_handler():
    """Main wiki handler - routes based on query string like YesWiki"""
    # YesWiki uses query string for routing: ?PageName/action
    qs = request.query_string.decode('utf-8', errors='replace')

    if not qs:
        qs = "PagePrincipale"

    # Parse the path from query string
    parts = qs.split('/', 1)
    page_tag = parts[0]
    action = parts[1] if len(parts) > 1 else "view"

    # Remove any extra query params from page_tag
    if '&' in page_tag:
        page_tag = page_tag.split('&')[0]
    if '=' in page_tag and page_tag.split('=')[0] in ['q', 'file', 'action']:
        return redirect('/?PagePrincipale')

    if action.startswith("upload"):
        return handle_upload(page_tag)
    elif action.startswith("edit"):
        return handle_edit(page_tag)
    elif action.startswith("revisions"):
        return handle_revisions(page_tag)
    else:
        return handle_view(page_tag)


def handle_view(page_tag):
    """Display a wiki page"""
    page = wiki_pages.get(page_tag)
    if not page:
        html = render_header(page_tag)
        html += render_page_actions(page_tag)
        html += '<div class="wiki-content">'
        html += '<div class="breadcrumb"><a href="/">Home</a> &raquo; {}</div>'.format(page_tag)
        html += '<h2>{}</h2>'.format(page_tag)
        html += '<div class="alert alert-info">This page does not exist yet. '
        html += '<a href="/?{}/edit">Create it</a>.</div>'.format(page_tag)
        html += '</div>'
        html += render_footer()
        return html

    html = render_header(page["title"])
    html += render_page_actions(page_tag)
    html += '<div class="wiki-content">'
    html += '<div class="breadcrumb"><a href="/">Home</a> &raquo; {}</div>'.format(page["title"])
    html += '<h2>{}</h2>'.format(page["title"])
    html += page["content"]

    # Show attached files if any
    page_files = uploaded_files.get(page_tag, [])
    if page_files:
        html += '<h3>Attached Files</h3>'
        html += '<ul class="file-list">'
        for f in page_files:
            html += '<li><a href="#">{name}</a> ({size}) - uploaded by {author}</li>'.format(**f)
        html += '</ul>'

    html += '<p style="font-size:0.8em;color:#999;">Last modified: {} by {}</p>'.format(
        page["last_modified"], page["author"])
    html += '</div>'
    html += render_footer()
    return html


def handle_edit(page_tag):
    """Display edit form for a wiki page"""
    page = wiki_pages.get(page_tag, {"title": page_tag, "content": "", "last_modified": "", "author": ""})

    if request.method == "POST":
        pass  # Read-only in this deployment

    html = render_header("Edit: " + page["title"])
    html += render_page_actions(page_tag)
    html += '<div class="wiki-content">'
    html += '<div class="breadcrumb"><a href="/">Home</a> &raquo; <a href="/?{tag}">{title}</a> &raquo; Edit</div>'.format(
        tag=page_tag, title=page["title"])
    html += '<h2>Editing: {}</h2>'.format(page["title"])
    html += '<div class="alert alert-info">Editing is currently disabled in read-only mode.</div>'
    html += '<form method="post">'
    html += '<textarea name="body" rows="15" style="width:100%;font-family:monospace;padding:10px;border:1px solid #ddd;border-radius:4px;">{}</textarea>'.format(
        page["content"].replace('<', '&lt;').replace('>', '&gt;'))
    html += '<br><br><input type="submit" value="Save" style="background:#27ae60;color:white;border:none;padding:8px 20px;border-radius:4px;cursor:pointer;" disabled>'
    html += '</form>'
    html += '</div>'
    html += render_footer()
    return html


def handle_revisions(page_tag):
    """Display page revision history"""
    page = wiki_pages.get(page_tag)

    html = render_header("Revisions: " + page_tag)
    html += render_page_actions(page_tag)
    html += '<div class="wiki-content">'
    html += '<div class="breadcrumb"><a href="/">Home</a> &raquo; <a href="/?{tag}">{tag}</a> &raquo; Revisions</div>'.format(tag=page_tag)
    html += '<h2>Revision History: {}</h2>'.format(page_tag)

    if page:
        html += '<table>'
        html += '<tr><th>Date</th><th>Author</th><th>Action</th></tr>'
        html += '<tr><td>{}</td><td>{}</td><td>Modified</td></tr>'.format(page["last_modified"], page["author"])
        html += '</table>'
    else:
        html += '<p>No revisions found for this page.</p>'

    html += '</div>'
    html += render_footer()
    return html


def handle_upload(page_tag):
    """Display the file upload form for a wiki page"""
    file_param = request.args.get('file', '')

    html = render_header("Upload - " + page_tag)
    html += render_page_actions(page_tag)
    html += '<div class="wiki-content">'
    html += '<div class="breadcrumb"><a href="/">Home</a> &raquo; <a href="/?{tag}">{tag}</a> &raquo; Upload</div>'.format(tag=page_tag)

    if file_param:
        html += '<h3>Upload form for file ' + file_param + '</h3>\n'
    else:
        html += '<h3>Upload file to ' + page_tag + '</h3>\n'

    html += '<div class="upload-form">'
    html += '<form method="post" enctype="multipart/form-data" action="/?{}/upload">'.format(page_tag)
    html += '<p>Select a file to attach to this page:</p>'
    html += '<input type="file" name="attachment">'
    html += '<br><br>'
    html += '<input type="submit" value="Upload">'
    html += '</form>'
    html += '</div>'

    # Show existing files
    page_files = uploaded_files.get(page_tag, [])
    if page_files:
        html += '<h3>Existing Attachments</h3>'
        html += '<ul class="file-list">'
        for f in page_files:
            html += '<li><a href="#">{name}</a> ({size})</li>'.format(**f)
        html += '</ul>'

    html += '</div>'
    html += render_footer()

    response = make_response(html)
    response.headers["X-XSS-Protection"] = "0"
    response.headers["Content-Type"] = "text/html; charset=utf-8"
    return response


@app.route('/search')
def search():
    """Search wiki pages"""
    query = request.args.get('q', '')

    html = render_header("Search")
    html += '<div class="wiki-content">'
    html += '<h2>Search Results</h2>'

    if query:
        # Sanitize the search query for display
        safe_query = query.replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
        html += '<p>Results for: <strong>{}</strong></p>'.format(safe_query)
        results = []
        for tag, page in wiki_pages.items():
            if query.lower() in page["content"].lower() or query.lower() in page["title"].lower():
                results.append((tag, page))

        if results:
            html += '<ul>'
            for tag, page in results:
                html += '<li><a href="/?{}">{}</a> - Last modified: {}</li>'.format(
                    tag, page["title"], page["last_modified"])
            html += '</ul>'
        else:
            html += '<p>No results found.</p>'
    else:
        html += '<p>Enter a search term above.</p>'

    html += '</div>'
    html += render_footer()
    return html


@app.route('/api/pages')
def api_pages():
    """API endpoint to list wiki pages"""
    pages = []
    for tag, page in wiki_pages.items():
        pages.append({
            "tag": tag,
            "title": page["title"],
            "last_modified": page["last_modified"],
            "author": page["author"]
        })
    return Response(json.dumps({"pages": pages}), mimetype='application/json')


@app.route('/report', methods=['POST'])
def report_page():
    """Report a page for review by an administrator"""
    url = request.form.get('url', '')
    if not url:
        return Response(json.dumps({"error": "Missing url parameter"}), status=400, mimetype='application/json')

    if not url.startswith('http://localhost:5000/') and not url.startswith('http://127.0.0.1:5000/'):
        return Response(json.dumps({"error": "URL must point to this wiki instance"}), status=400, mimetype='application/json')

    try:
        admin_session = open('secret.txt').read().strip()
        proc = subprocess.Popen(
            ["timeout", "10", "phantomjs", "check_report.js", url, admin_session],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = proc.communicate()
        return Response(
            json.dumps({"status": "Report received", "message": "An administrator will review the reported page."}),
            mimetype='application/json'
        )
    except Exception as e:
        logging.error("Error processing report: %s", str(e))
        return Response(
            json.dumps({"status": "Report received", "message": "An administrator will review the reported page."}),
            mimetype='application/json'
        )


webhook_log = []

@app.route('/api/webhook', methods=['GET'])
def webhook():
    """Webhook integration endpoint for external notifications"""
    data = request.args.get('data', '')
    if data:
        webhook_log.append({"data": data, "time": time.time()})
        return Response(json.dumps({"status": "ok"}), mimetype='application/json')
    return Response(json.dumps({"entries": [e["data"] for e in webhook_log]}), mimetype='application/json')


@app.errorhandler(404)
def not_found(e):
    html = render_header("Not Found")
    html += '<div class="wiki-content">'
    html += '<h2>Page Not Found</h2>'
    html += '<p>The requested page could not be found. <a href="/">Return to the main page</a>.</p>'
    html += '</div>'
    html += render_footer()
    return html, 404


@app.errorhandler(500)
def server_error(e):
    html = render_header("Error")
    html += '<div class="wiki-content">'
    html += '<h2>Internal Server Error</h2>'
    html += '<p>An unexpected error occurred. Please try again later.</p>'
    html += '</div>'
    html += render_footer()
    return html, 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
