# encoding=utf8

from flask import Flask, request, Response, make_response, render_template_string
import subprocess
import os
import sys
from jinja2 import Environment, BaseLoader
import logging
import datetime

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flags = open('secret.txt').read().split()

app = Flask(__name__)

STATIC_FILES = [
    {"name": "documents", "type": "folder", "size": "-", "modified": "2024-01-15 09:30"},
    {"name": "images", "type": "folder", "size": "-", "modified": "2024-01-12 14:22"},
    {"name": "backups", "type": "folder", "size": "-", "modified": "2024-01-10 11:00"},
    {"name": "readme.txt", "type": "file", "size": "2.4 KB", "modified": "2024-01-14 16:45"},
    {"name": "config.xml", "type": "file", "size": "1.1 KB", "modified": "2024-01-13 08:12"},
    {"name": "report.pdf", "type": "file", "size": "456 KB", "modified": "2024-01-11 10:33"},
]

DIR_BROWSER_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>WebDAV Directory Browser - {{ current_path }}</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 8px 8px 0 0; }
        .header h1 { margin: 0 0 10px 0; font-size: 24px; }
        .auth-info { font-size: 13px; color: #bdc3c7; margin-top: 15px; padding-top: 15px; border-top: 1px solid #34495e; }
        .breadcrumb { padding: 15px 20px; background: #ecf0f1; border-bottom: 1px solid #ddd; }
        .breadcrumb a { color: #3498db; text-decoration: none; }
        .breadcrumb a:hover { text-decoration: underline; }
        table { width: 100%; border-collapse: collapse; }
        th { background: #f8f9fa; padding: 12px 20px; text-align: left; font-weight: 600; color: #555; border-bottom: 2px solid #ddd; }
        td { padding: 12px 20px; border-bottom: 1px solid #eee; }
        tr:hover { background: #f8f9fa; }
        .icon { width: 24px; margin-right: 10px; vertical-align: middle; }
        .folder { color: #f39c12; }
        .file { color: #7f8c8d; }
        a.item-link { color: #2c3e50; text-decoration: none; }
        a.item-link:hover { color: #3498db; }
        .footer { padding: 15px 20px; background: #f8f9fa; border-radius: 0 0 8px 8px; font-size: 12px; color: #7f8c8d; }
        .upload-form { padding: 20px; background: #fff; border-bottom: 1px solid #eee; }
        .upload-form input[type="text"] { padding: 8px 12px; border: 1px solid #ddd; border-radius: 4px; width: 300px; margin-right: 10px; }
        .upload-form button { padding: 8px 16px; background: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer; }
        .upload-form button:hover { background: #2980b9; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>WebDAV Directory Browser</h1>
            <p>Browsing: {{ current_path }}</p>
            <div class="auth-info">
                Authenticated user: "{{ user_name }}", realm: "{{ realm }}", access: {{ access_mode }}
            </div>
        </div>
        
        <div class="breadcrumb">
            <a href="/">Home</a> / <a href="/dav">dav</a> / {{ current_path }}
        </div>
        
        <div class="upload-form">
            <form action="/dav/browse" method="GET">
                <input type="text" name="realm" placeholder="Enter realm name..." value="">
                <button type="submit">Set Realm</button>
            </form>
        </div>
        
        <table>
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Type</th>
                    <th>Size</th>
                    <th>Last Modified</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td colspan="4"><a href="/dav" class="item-link">&#x1F4C1; ..</a></td>
                </tr>
                {% for item in files %}
                <tr>
                    <td>
                        {% if item.type == 'folder' %}
                        <span class="folder">&#x1F4C1;</span>
                        {% else %}
                        <span class="file">&#x1F4C4;</span>
                        {% endif %}
                        <a href="/dav/browse?path={{ item.name }}" class="item-link">{{ item.name }}</a>
                    </td>
                    <td>{{ item.type }}</td>
                    <td>{{ item.size }}</td>
                    <td>{{ item.modified }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        
        <div class="footer">
            {{ trailer }}
        </div>
    </div>
</body>
</html>"""

def check_xss(page, flag, msg):
    proc = subprocess.Popen(["timeout","5","phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://localhost:5000/' + fn
    try:
        of = open(fn, 'w')
        of.write(page)
        of.close()
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
    finally:
        os.unlink(fn)
    
    return result == 'XSS'


@app.route('/')
def index():
    return '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>FileShare Pro - Enterprise WebDAV Server</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .hero { display: flex; align-items: center; justify-content: center; min-height: 100vh; }
        .card { background: white; padding: 60px; border-radius: 16px; box-shadow: 0 25px 50px rgba(0,0,0,0.25); text-align: center; max-width: 500px; }
        h1 { color: #2c3e50; margin-bottom: 10px; font-size: 32px; }
        .subtitle { color: #7f8c8d; margin-bottom: 30px; }
        .features { text-align: left; margin: 30px 0; }
        .feature { padding: 10px 0; color: #555; }
        .feature:before { content: "\\2713"; color: #27ae60; margin-right: 10px; font-weight: bold; }
        .btn { display: inline-block; padding: 15px 40px; background: #3498db; color: white; text-decoration: none; border-radius: 8px; font-weight: 600; margin-top: 20px; }
        .btn:hover { background: #2980b9; }
        .version { color: #bdc3c7; font-size: 12px; margin-top: 30px; }
    </style>
</head>
<body>
    <div class="hero">
        <div class="card">
            <h1>FileShare Pro</h1>
            <p class="subtitle">Enterprise WebDAV File Sharing Solution</p>
            <div class="features">
                <div class="feature">Secure file storage and sharing</div>
                <div class="feature">WebDAV protocol support</div>
                <div class="feature">Directory browsing interface</div>
                <div class="feature">Multi-user authentication</div>
            </div>
            <a href="/dav" class="btn">Browse Files</a>
            <p class="version">Version 4.0.2</p>
        </div>
    </div>
</body>
</html>'''


@app.route('/dav')
def dav_root():
    return '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>WebDAV - Root Directory</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 8px 8px 0 0; }
        .header h1 { margin: 0; font-size: 24px; }
        .content { padding: 40px; text-align: center; }
        .folder-icon { font-size: 80px; margin-bottom: 20px; }
        h2 { color: #2c3e50; }
        p { color: #7f8c8d; }
        .btn { display: inline-block; padding: 12px 30px; background: #3498db; color: white; text-decoration: none; border-radius: 6px; margin-top: 20px; }
        .btn:hover { background: #2980b9; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>WebDAV Server</h1>
        </div>
        <div class="content">
            <div class="folder-icon">&#x1F4C2;</div>
            <h2>Welcome to WebDAV</h2>
            <p>Access the directory browser to view and manage files.</p>
            <a href="/dav/browse" class="btn">Open Directory Browser</a>
        </div>
    </div>
</body>
</html>'''


@app.route('/dav/browse')
def directory_browser():
    realm = request.args.get('realm', 'default')
    user_name = request.args.get('user', 'anonymous')
    path = request.args.get('path', 'shared')
    
    env = Environment(loader=BaseLoader(), autoescape=False)
    template = env.from_string(DIR_BROWSER_TEMPLATE)
    
    context = {
        'current_path': path,
        'user_name': user_name,
        'realm': realm,
        'access_mode': 'read-write',
        'files': STATIC_FILES,
        'trailer': 'Powered by WsgiDAV/4.0.2 - <a href="https://github.com/mar10/wsgidav">GitHub</a>'
    }
    
    rendered_page = template.render(**context)
    
    xss_triggered = check_xss(rendered_page, flags[0], realm + user_name)
    
    if xss_triggered:
        context['trailer'] = 'Congratulations! Flag: ' + flags[0]
        rendered_page = template.render(**context)
    
    response = make_response(rendered_page)
    response.headers["X-XSS-Protection"] = "0"
    response.headers["Content-Type"] = "text/html; charset=utf-8"
    return response


@app.errorhandler(404)
def not_found(e):
    return '''<!DOCTYPE html>
<html>
<head><title>404 - Not Found</title></head>
<body style="font-family: sans-serif; text-align: center; padding: 50px;">
<h1>404 - Page Not Found</h1>
<p>The requested resource could not be found.</p>
<a href="/">Return to Home</a>
</body>
</html>''', 404


@app.errorhandler(500)
def server_error(e):
    return '''<!DOCTYPE html>
<html>
<head><title>500 - Server Error</title></head>
<body style="font-family: sans-serif; text-align: center; padding: 50px;">
<h1>500 - Internal Server Error</h1>
<p>An unexpected error occurred.</p>
<a href="/">Return to Home</a>
</body>
</html>''', 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
