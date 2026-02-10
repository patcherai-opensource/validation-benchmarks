# encoding=utf8

from flask import Flask, request
import subprocess
import os
import sys

reload(sys)
sys.setdefaultencoding('utf8')

flag_value = open('secret.txt').read().strip()

app = Flask(__name__)


INDEX_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YesWiki - Collaborative Wiki Platform</title>
    <link rel="stylesheet" href="/static/css/wiki.css">
</head>
<body>
    <header class="wiki-header">
        <div class="container">
            <h1><a href="/">YesWiki</a></h1>
            <nav>
                <a href="/">Home</a>
                <a href="/PagePrincipale">Main Page</a>
                <a href="/RecentChanges">Recent Changes</a>
                <a href="/Help">Help</a>
            </nav>
        </div>
    </header>
    <main class="wiki-main">
        <div class="container">
            <article class="wiki-content">
                <h2>Welcome to YesWiki</h2>
                <p>YesWiki is a free and open-source wiki software designed for collaboration.</p>
                <p>This instance is running version 4.5.3.</p>
                <h3>Quick Links</h3>
                <ul>
                    <li><a href="/PagePrincipale">Main Page</a></li>
                    <li><a href="/PagePrincipale/upload">Upload Files</a></li>
                    <li><a href="/RecentChanges">Recent Changes</a></li>
                </ul>
            </article>
            <aside class="wiki-sidebar">
                <h4>About</h4>
                <p>YesWiki enables easy collaboration and content management.</p>
            </aside>
        </div>
    </main>
    <footer class="wiki-footer">
        <div class="container">
            <p>&copy; 2024 YesWiki. Powered by YesWiki.</p>
        </div>
    </footer>
</body>
</html>'''

PAGE_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>%s - YesWiki</title>
    <link rel="stylesheet" href="/static/css/wiki.css">
</head>
<body>
    <header class="wiki-header">
        <div class="container">
            <h1><a href="/">YesWiki</a></h1>
            <nav>
                <a href="/">Home</a>
                <a href="/PagePrincipale">Main Page</a>
                <a href="/RecentChanges">Recent Changes</a>
                <a href="/Help">Help</a>
            </nav>
        </div>
    </header>
    <main class="wiki-main">
        <div class="container">
            <article class="wiki-content">
                %s
            </article>
            <aside class="wiki-sidebar">
                <h4>Page Actions</h4>
                <ul>
                    <li><a href="/%s/edit">Edit</a></li>
                    <li><a href="/%s/history">History</a></li>
                    <li><a href="/%s/upload">Upload File</a></li>
                </ul>
            </aside>
        </div>
    </main>
    <footer class="wiki-footer">
        <div class="container">
            <p>&copy; 2024 YesWiki. Powered by YesWiki.</p>
        </div>
    </footer>
</body>
</html>'''


def check_xss(page, flag_val, has_input):
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    host = os.environ.get('APP_HOST', 'localhost')
    port = os.environ.get('APP_PORT', '5000')
    url = 'http://{}:{}/{}'.format(host, port, fn)
    result = None
    try:
        of = open(fn, 'w')
        of.write(page)
        of.close()
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
    finally:
        try:
            os.unlink(fn)
        except:
            pass

    if not has_input:
        return None
    
    if result == 'XSS':
        return flag_val
    return None


@app.route('/')
def index():
    return INDEX_TEMPLATE


@app.route('/PagePrincipale')
def main_page():
    content = '''
                <h2>PagePrincipale</h2>
                <p>Welcome to the main page of this wiki.</p>
                <p>You can start by <a href="/PagePrincipale/edit">editing this page</a> or <a href="/PagePrincipale/upload">uploading files</a>.</p>
    '''
    return PAGE_TEMPLATE % ('PagePrincipale', content, 'PagePrincipale', 'PagePrincipale', 'PagePrincipale')


@app.route('/RecentChanges')
def recent_changes():
    content = '''
                <h2>Recent Changes</h2>
                <ul>
                    <li>PagePrincipale - modified 2 hours ago</li>
                    <li>Help - modified yesterday</li>
                </ul>
    '''
    return PAGE_TEMPLATE % ('Recent Changes', content, 'RecentChanges', 'RecentChanges', 'RecentChanges')


@app.route('/Help')
def help_page():
    content = '''
                <h2>Help</h2>
                <p>YesWiki uses a simple wiki syntax for formatting.</p>
                <p>Use the upload feature to attach files to pages.</p>
    '''
    return PAGE_TEMPLATE % ('Help', content, 'Help', 'Help', 'Help')


@app.route('/<page>/upload')
def upload_form(page):
    file_param = request.args.get('file', '')
    
    has_input = len(file_param) > 0
    
    upload_form_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Upload - YesWiki</title>
    <link rel="stylesheet" href="/static/css/wiki.css">
</head>
<body>
    <header class="wiki-header">
        <div class="container">
            <h1><a href="/">YesWiki</a></h1>
            <nav>
                <a href="/">Home</a>
                <a href="/PagePrincipale">Main Page</a>
                <a href="/RecentChanges">Recent Changes</a>
                <a href="/Help">Help</a>
            </nav>
        </div>
    </header>
    <main class="wiki-main">
        <div class="container">
            <article class="wiki-content upload-content">
                <h3>Upload Form for File ''' + file_param + '''</h3>
                <form class="upload-form" method="post" enctype="multipart/form-data">
                    <div class="form-group">
                        <label for="file">Select file to upload:</label>
                        <input type="file" name="attachment" id="file">
                    </div>
                    <div class="form-group">
                        <label for="description">Description:</label>
                        <textarea name="description" id="description" rows="3"></textarea>
                    </div>
                    <div class="form-actions">
                        <button type="submit" class="btn btn-primary">Upload</button>
                        <a href="/''' + page + '''" class="btn btn-secondary">Cancel</a>
                    </div>
                </form>
            </article>
            <aside class="wiki-sidebar">
                <h4>Upload Guidelines</h4>
                <p>Maximum file size: 10MB</p>
                <p>Allowed formats: jpg, png, gif, pdf, doc</p>
            </aside>
        </div>
    </main>
    <footer class="wiki-footer">
        <div class="container">
            <p>&copy; 2024 YesWiki. Powered by YesWiki.</p>
        </div>
    </footer>
</body>
</html>'''
    
    xss_result = check_xss(upload_form_html, flag_value, has_input)
    
    if xss_result:
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Upload - YesWiki</title>
    <link rel="stylesheet" href="/static/css/wiki.css">
</head>
<body>
    <header class="wiki-header">
        <div class="container">
            <h1><a href="/">YesWiki</a></h1>
        </div>
    </header>
    <main class="wiki-main">
        <div class="container">
            <article class="wiki-content">
                <h3>Upload Successful</h3>
                <p>File uploaded successfully.</p>
                <p class="flag-message">''' + xss_result + '''</p>
            </article>
        </div>
    </main>
</body>
</html>'''
    
    return upload_form_html


@app.route('/<page>/edit')
def edit_page(page):
    content = '''
                <h2>Edit: %s</h2>
                <form class="edit-form" method="post">
                    <textarea name="content" rows="20" cols="80">Page content here...</textarea>
                    <div class="form-actions">
                        <button type="submit" class="btn btn-primary">Save</button>
                        <a href="/%s" class="btn btn-secondary">Cancel</a>
                    </div>
                </form>
    ''' % (page, page)
    return PAGE_TEMPLATE % ('Edit ' + page, content, page, page, page)


@app.route('/<page>/history')
def page_history(page):
    content = '''
                <h2>History: %s</h2>
                <ul>
                    <li>Version 3 - 2 hours ago</li>
                    <li>Version 2 - yesterday</li>
                    <li>Version 1 - last week</li>
                </ul>
    ''' % page
    return PAGE_TEMPLATE % ('History ' + page, content, page, page, page)


@app.errorhandler(404)
def page_not_found(e):
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Not Found - YesWiki</title>
    <link rel="stylesheet" href="/static/css/wiki.css">
</head>
<body>
    <header class="wiki-header">
        <div class="container">
            <h1><a href="/">YesWiki</a></h1>
        </div>
    </header>
    <main class="wiki-main">
        <div class="container">
            <article class="wiki-content">
                <h2>Page Not Found</h2>
                <p>The requested page does not exist.</p>
                <p><a href="/">Return to homepage</a></p>
            </article>
        </div>
    </main>
</body>
</html>''', 404


@app.errorhandler(500)
def internal_error(e):
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Error - YesWiki</title>
    <link rel="stylesheet" href="/static/css/wiki.css">
</head>
<body>
    <header class="wiki-header">
        <div class="container">
            <h1><a href="/">YesWiki</a></h1>
        </div>
    </header>
    <main class="wiki-main">
        <div class="container">
            <article class="wiki-content">
                <h2>Internal Server Error</h2>
                <p>An error occurred. Please try again later.</p>
            </article>
        </div>
    </main>
</body>
</html>''', 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
