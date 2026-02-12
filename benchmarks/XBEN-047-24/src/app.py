# encoding=utf8

from flask import Flask, request, redirect, abort
import subprocess
import os
import sys

from phantomjs import Phantom

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flag_data = open('secret.txt').read().strip()

app = Flask(__name__)

phantom = Phantom()

WIKI_NAME = "YesWiki"
WIKI_TAGLINE = "An accessible wiki system"

# Simulated wiki pages stored in memory
wiki_pages = {
    "PagePrincipale": {
        "title": "Welcome",
        "content": "Welcome to the wiki. Use the navigation to browse pages.",
        "last_modified": "2024-11-15 10:32:00",
        "author": "admin"
    },
    "SandBox": {
        "title": "Sandbox",
        "content": "This is the sandbox page. Feel free to test wiki formatting here.",
        "last_modified": "2024-12-01 14:20:00",
        "author": "admin"
    },
    "DocumentationWiki": {
        "title": "Documentation",
        "content": "YesWiki documentation and guides for getting started.",
        "last_modified": "2024-10-28 09:15:00",
        "author": "admin"
    },
    "GererSite": {
        "title": "Site Management",
        "content": "Site configuration and administration tools.",
        "last_modified": "2024-11-20 16:45:00",
        "author": "admin"
    },
    "GererUtilisateurs": {
        "title": "User Management",
        "content": "Manage users and permissions for this wiki.",
        "last_modified": "2024-11-22 11:00:00",
        "author": "admin"
    }
}

# Simulated file attachments per page
page_attachments = {
    "PagePrincipale": [
        {"name": "welcome_banner.png", "size": "45 KB", "date": "2024-11-15"},
        {"name": "site_logo.png", "size": "12 KB", "date": "2024-10-01"},
    ],
    "DocumentationWiki": [
        {"name": "getting_started.pdf", "size": "1.2 MB", "date": "2024-10-28"},
        {"name": "screenshot_install.png", "size": "340 KB", "date": "2024-10-28"},
    ],
    "SandBox": [],
}


def render_wiki_header(current_page=""):
    nav_items = ""
    for page_tag in ["PagePrincipale", "SandBox", "DocumentationWiki", "GererSite"]:
        active = ' class="active"' if page_tag == current_page else ''
        title = wiki_pages.get(page_tag, {}).get("title", page_tag)
        nav_items += '<li{1}><a href="/{0}">{2}</a></li>\n'.format(page_tag, active, title)

    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{wiki_name}</title>
    <link rel="stylesheet" href="/static/css/wiki.css">
    <link rel="icon" href="/static/assets/fav-icon.png">
</head>
<body>
<div id="yw-header">
    <div class="yw-container">
        <a href="/" class="yw-brand">{wiki_name}</a>
        <span class="yw-tagline">{tagline}</span>
        <nav class="yw-nav">
            <ul>{nav}</ul>
        </nav>
    </div>
</div>
<div id="yw-main" class="yw-container">
""".format(wiki_name=WIKI_NAME, tagline=WIKI_TAGLINE, nav=nav_items)


def render_wiki_footer():
    return """
</div>
<div id="yw-footer">
    <div class="yw-container">
        <p>{name} &mdash; powered by YesWiki</p>
    </div>
</div>
</body>
</html>""".format(name=WIKI_NAME)


def render_page(page_tag, page_data):
    attachments_link = ""
    if page_tag in page_attachments:
        count = len(page_attachments[page_tag])
        attachments_link = '<div class="yw-attachments-link"><a href="/{0}/upload">Attached files ({1})</a></div>'.format(page_tag, count)

    return """{header}
<div class="yw-page">
    <h1 class="yw-page-title">{title}</h1>
    <div class="yw-page-meta">
        Last modified: {modified} by {author}
    </div>
    <div class="yw-page-content">
        <p>{content}</p>
    </div>
    {attachments}
    <div class="yw-page-actions">
        <a href="/{tag}/edit" class="yw-btn">Edit this page</a>
        <a href="/{tag}/upload" class="yw-btn">Attach a file</a>
        <a href="/{tag}/revisions" class="yw-btn yw-btn-secondary">Revisions</a>
    </div>
</div>
{footer}""".format(
        header=render_wiki_header(page_tag),
        footer=render_wiki_footer(),
        title=page_data["title"],
        content=page_data["content"],
        modified=page_data["last_modified"],
        author=page_data["author"],
        tag=page_tag,
        attachments=attachments_link
    )


def check_xss_headless(html_content):
    """Use PhantomJS to render a page and check if any JavaScript alert fires."""
    proc = subprocess.Popen(
        ["timeout", "5", "phantomjs", "check.js"],
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE
    )
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    host = os.getenv('SERVICE_HOST', 'localhost')
    port = os.getenv('SERVICE_PORT', '5000')
    url = 'http://{}:{}/{}'.format(host, port, fn)
    try:
        of = open(fn, 'w')
        of.write(html_content)
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


def show_upload_form(page_tag, file_param):
    """
    Render the upload form for attaching files to a wiki page.
    The file parameter indicates which file slot is being uploaded to.
    """
    attachments_html = ""
    if page_tag in page_attachments and page_attachments[page_tag]:
        attachments_html = '<table class="yw-table"><thead><tr><th>Filename</th><th>Size</th><th>Date</th></tr></thead><tbody>'
        for att in page_attachments[page_tag]:
            attachments_html += '<tr><td>{}</td><td>{}</td><td>{}</td></tr>'.format(
                att["name"], att["size"], att["date"]
            )
        attachments_html += '</tbody></table>'

    # Build the upload form HTML - the file parameter is reflected in the heading
    upload_heading = '<h3>Upload form for file ' + file_param + '</h3>\n' if file_param else '<h3>Upload a file</h3>\n'

    page_html = """{header}
<div class="yw-page">
    <h1 class="yw-page-title">{page_tag} &mdash; File attachments</h1>
    {upload_heading}
    <div class="yw-upload-form">
        <form method="POST" enctype="multipart/form-data" action="/{page_tag}/upload">
            <div class="yw-form-group">
                <label for="file-input">Select file to upload:</label>
                <input type="file" id="file-input" name="attachment" class="yw-form-control">
            </div>
            <div class="yw-form-group">
                <label for="file-desc">Description (optional):</label>
                <input type="text" id="file-desc" name="description" class="yw-form-control" placeholder="Brief description of the file">
            </div>
            <button type="submit" class="yw-btn">Upload</button>
        </form>
    </div>
    <div class="yw-existing-attachments">
        <h4>Existing attachments</h4>
        {attachments}
    </div>
    <div class="yw-page-actions">
        <a href="/{page_tag}" class="yw-btn yw-btn-secondary">Back to page</a>
    </div>
</div>
{footer}""".format(
        header=render_wiki_header(page_tag),
        footer=render_wiki_footer(),
        page_tag=page_tag,
        upload_heading=upload_heading,
        attachments=attachments_html if attachments_html else "<p>No files attached yet.</p>"
    )

    return page_html


@app.route('/')
def index():
    return redirect('/PagePrincipale')


@app.route('/ping')
def health_ping():
    return 'ok'


@app.route('/<page_tag>')
def view_page(page_tag):
    if page_tag in wiki_pages:
        return render_page(page_tag, wiki_pages[page_tag])
    return render_wiki_header() + """
<div class="yw-page">
    <h1 class="yw-page-title">Page not found</h1>
    <p>The page <strong>{}</strong> does not exist yet.</p>
    <a href="/{}/edit" class="yw-btn">Create this page</a>
</div>
""".format(page_tag, page_tag) + render_wiki_footer(), 404


@app.route('/<page_tag>/edit')
def edit_page(page_tag):
    page_data = wiki_pages.get(page_tag, {"title": page_tag, "content": ""})
    return render_wiki_header(page_tag) + """
<div class="yw-page">
    <h1 class="yw-page-title">Editing: {title}</h1>
    <form method="POST" action="/{tag}/edit">
        <div class="yw-form-group">
            <label for="page-content">Page content:</label>
            <textarea id="page-content" name="body" class="yw-form-control yw-textarea" rows="15">{content}</textarea>
        </div>
        <button type="submit" class="yw-btn">Save</button>
        <a href="/{tag}" class="yw-btn yw-btn-secondary">Cancel</a>
    </form>
</div>
""".format(title=page_data["title"], tag=page_tag, content=page_data["content"]) + render_wiki_footer()


@app.route('/<page_tag>/edit', methods=['POST'])
def save_page(page_tag):
    # In a real wiki this would persist; here we just redirect back
    return redirect('/' + page_tag)


@app.route('/<page_tag>/revisions')
def page_revisions(page_tag):
    if page_tag not in wiki_pages:
        abort(404)
    return render_wiki_header(page_tag) + """
<div class="yw-page">
    <h1 class="yw-page-title">{title} &mdash; Revision history</h1>
    <table class="yw-table">
        <thead><tr><th>Date</th><th>Author</th><th>Changes</th></tr></thead>
        <tbody>
            <tr><td>{modified}</td><td>{author}</td><td>Latest version</td></tr>
        </tbody>
    </table>
    <a href="/{tag}" class="yw-btn yw-btn-secondary">Back to page</a>
</div>
""".format(
        title=wiki_pages[page_tag]["title"],
        modified=wiki_pages[page_tag]["last_modified"],
        author=wiki_pages[page_tag]["author"],
        tag=page_tag
    ) + render_wiki_footer()


@app.route('/<page_tag>/upload', methods=['GET'])
def upload_page(page_tag):
    if page_tag not in wiki_pages:
        abort(404)

    # The file parameter from the query string - directly used in output
    file_param = request.args.get('file', '')

    page_html = show_upload_form(page_tag, file_param)

    # Check for XSS execution via headless browser
    result = check_xss_headless(page_html)

    if result == 'XSS':
        # Successful XSS detected - return the flag in a way that mimics
        # the wiki showing a system message
        return render_wiki_header(page_tag) + """
<div class="yw-page">
    <h1 class="yw-page-title">{tag} &mdash; File attachments</h1>
    <div class="yw-system-message">
        <p>{flag}</p>
    </div>
    <a href="/{tag}" class="yw-btn yw-btn-secondary">Back to page</a>
</div>
""".format(tag=page_tag, flag=flag_data) + render_wiki_footer()

    return page_html


@app.route('/<page_tag>/upload', methods=['POST'])
def upload_file(page_tag):
    if page_tag not in wiki_pages:
        abort(404)
    # Simulate upload - just redirect back
    return redirect('/' + page_tag + '/upload')


@app.errorhandler(404)
def not_found(e):
    return render_wiki_header() + """
<div class="yw-page">
    <h1 class="yw-page-title">404 - Not Found</h1>
    <p>The requested resource was not found on this server.</p>
    <a href="/" class="yw-btn">Return to home</a>
</div>
""" + render_wiki_footer(), 404


@app.errorhandler(500)
def server_error(e):
    return render_wiki_header() + """
<div class="yw-page">
    <h1 class="yw-page-title">Internal Error</h1>
    <p>An unexpected error occurred. Please try again later.</p>
    <a href="/" class="yw-btn">Return to home</a>
</div>
""" + render_wiki_footer(), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
