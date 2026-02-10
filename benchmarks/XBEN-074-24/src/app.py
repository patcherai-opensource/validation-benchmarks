# encoding=utf8

from flask import Flask, request, Response, make_response, render_template_string, redirect, url_for, jsonify
import subprocess
import os
import re
import cgi
import urllib
import urllib2
import sys
import json
import HTMLParser

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flag_value = open('secret.txt').read().strip()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False
app.config['DEBUG'] = False

registered_servers = {}
server_data_cache = {}
html_parser = HTMLParser.HTMLParser()

INDEX_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>GameTrack - Live Game Server Monitor</title>
    <link rel="stylesheet" type="text/css" href="/static/css/style.css">
    <style>
        body { font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { color: #4cc9f0; }
        .nav { background: #16213e; padding: 15px; margin-bottom: 20px; border-radius: 5px; }
        .nav a { color: #4cc9f0; text-decoration: none; margin-right: 20px; }
        .nav a:hover { text-decoration: underline; }
        .server-list { background: #16213e; padding: 20px; border-radius: 5px; }
        .server-item { background: #0f3460; padding: 15px; margin: 10px 0; border-radius: 5px; }
        .server-item h3 { margin: 0 0 10px 0; color: #4cc9f0; }
        .server-item a { color: #f72585; }
        .btn { background: #4cc9f0; color: #1a1a2e; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; text-decoration: none; display: inline-block; }
        .btn:hover { background: #3aa8d8; }
        .form-group { margin: 15px 0; }
        .form-group label { display: block; margin-bottom: 5px; }
        .form-group input { width: 100%; padding: 10px; border: 1px solid #0f3460; border-radius: 5px; background: #0f3460; color: #eee; box-sizing: border-box; }
        .error { color: #f72585; }
        .success { color: #4cc9f0; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        td, th { padding: 10px; border: 1px solid #0f3460; text-align: left; }
        th { background: #0f3460; }
    </style>
</head>
<body>
    <div class="container">
        <h1>GameTrack - Live Game Server Monitor</h1>
        <div class="nav">
            <a href="/">Home</a>
            <a href="/servers">Server List</a>
            <a href="/register">Register Server</a>
            <a href="/about">About</a>
        </div>
        <div class="server-list">
            <h2>Welcome to GameTrack</h2>
            <p>Monitor your favorite game servers in real-time. Register your server and let players find you!</p>
            <p><a href="/servers" class="btn">View All Servers</a></p>
        </div>
    </div>
</body>
</html>
"""

SERVERS_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Server List - GameTrack</title>
    <style>
        body { font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { color: #4cc9f0; }
        .nav { background: #16213e; padding: 15px; margin-bottom: 20px; border-radius: 5px; }
        .nav a { color: #4cc9f0; text-decoration: none; margin-right: 20px; }
        .nav a:hover { text-decoration: underline; }
        .server-list { background: #16213e; padding: 20px; border-radius: 5px; }
        .server-item { background: #0f3460; padding: 15px; margin: 10px 0; border-radius: 5px; }
        .server-item h3 { margin: 0 0 10px 0; color: #4cc9f0; }
        .server-item a { color: #f72585; }
        .btn { background: #4cc9f0; color: #1a1a2e; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; text-decoration: none; display: inline-block; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Registered Game Servers</h1>
        <div class="nav">
            <a href="/">Home</a>
            <a href="/servers">Server List</a>
            <a href="/register">Register Server</a>
            <a href="/about">About</a>
        </div>
        <div class="server-list">
            {server_list}
        </div>
    </div>
</body>
</html>
"""

REGISTER_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Register Server - GameTrack</title>
    <style>
        body { font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 20px; }
        .container { max-width: 600px; margin: 0 auto; }
        h1 { color: #4cc9f0; }
        .nav { background: #16213e; padding: 15px; margin-bottom: 20px; border-radius: 5px; }
        .nav a { color: #4cc9f0; text-decoration: none; margin-right: 20px; }
        .nav a:hover { text-decoration: underline; }
        .form-container { background: #16213e; padding: 20px; border-radius: 5px; }
        .form-group { margin: 15px 0; }
        .form-group label { display: block; margin-bottom: 5px; }
        .form-group input, .form-group textarea { width: 100%; padding: 10px; border: 1px solid #0f3460; border-radius: 5px; background: #0f3460; color: #eee; box-sizing: border-box; }
        .form-group textarea { min-height: 120px; font-family: monospace; }
        .btn { background: #4cc9f0; color: #1a1a2e; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
        .btn:hover { background: #3aa8d8; }
        .error { color: #f72585; margin: 10px 0; }
        .success { color: #4cc9f0; margin: 10px 0; }
        .help-text { font-size: 12px; color: #888; margin-top: 5px; }
        .or-divider { text-align: center; margin: 20px 0; color: #888; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Register Your Game Server</h1>
        <div class="nav">
            <a href="/">Home</a>
            <a href="/servers">Server List</a>
            <a href="/register">Register Server</a>
            <a href="/about">About</a>
        </div>
        <div class="form-container">
            {message}
            <form method="POST">
                <div class="form-group">
                    <label>Server Name:</label>
                    <input type="text" name="name" placeholder="My Awesome Server" required>
                </div>
                <div class="form-group">
                    <label>Game Type:</label>
                    <input type="text" name="game_type" placeholder="Minecraft, CS:GO, etc." required>
                </div>
                <div class="form-group">
                    <label>Info Endpoint URL (optional):</label>
                    <input type="text" name="info_url" placeholder="http://your-server.com/info">
                    <p class="help-text">Your server should expose a JSON endpoint with server details.</p>
                </div>
                <div class="or-divider">- OR -</div>
                <div class="form-group">
                    <label>Server Info JSON (optional):</label>
                    <textarea name="server_info" placeholder='{"players": "24/32", "map": "de_dust2", "mode": "Competitive"}'></textarea>
                    <p class="help-text">Provide server info directly as JSON if you don't have an info endpoint.</p>
                </div>
                <button type="submit" class="btn">Register Server</button>
            </form>
        </div>
    </div>
</body>
</html>
"""

SERVER_DETAILS_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>{server_name} - GameTrack</title>
    <style>
        body { font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 20px; }
        .container { max-width: 900px; margin: 0 auto; }
        h1 { color: #4cc9f0; }
        .nav { background: #16213e; padding: 15px; margin-bottom: 20px; border-radius: 5px; }
        .nav a { color: #4cc9f0; text-decoration: none; margin-right: 20px; }
        .nav a:hover { text-decoration: underline; }
        .details { background: #16213e; padding: 20px; border-radius: 5px; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        td, th { padding: 10px; border: 1px solid #0f3460; text-align: left; }
        th { background: #0f3460; width: 30%; }
        .error { color: #f72585; }
        .btn { background: #4cc9f0; color: #1a1a2e; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; text-decoration: none; display: inline-block; margin-top: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Server Details: {server_name}</h1>
        <div class="nav">
            <a href="/">Home</a>
            <a href="/servers">Server List</a>
            <a href="/register">Register Server</a>
            <a href="/about">About</a>
        </div>
        <div class="details">
            <h2>Server Information</h2>
            <table>
                <tr><th>Name</th><td>{server_name}</td></tr>
                <tr><th>Game Type</th><td>{game_type}</td></tr>
                <tr><th>Status</th><td>{status}</td></tr>
            </table>
            
            <h3>Extended Server Details</h3>
            <table>
                {extended_details}
            </table>
            
            <a href="/servers" class="btn">Back to Server List</a>
        </div>
    </div>
</body>
</html>
"""

ABOUT_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>About - GameTrack</title>
    <style>
        body { font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        h1 { color: #4cc9f0; }
        .nav { background: #16213e; padding: 15px; margin-bottom: 20px; border-radius: 5px; }
        .nav a { color: #4cc9f0; text-decoration: none; margin-right: 20px; }
        .nav a:hover { text-decoration: underline; }
        .content { background: #16213e; padding: 20px; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>About GameTrack</h1>
        <div class="nav">
            <a href="/">Home</a>
            <a href="/servers">Server List</a>
            <a href="/register">Register Server</a>
            <a href="/about">About</a>
        </div>
        <div class="content">
            <h2>What is GameTrack?</h2>
            <p>GameTrack is a live game server monitoring platform. Server administrators can register their game servers and we automatically poll them to retrieve and display server information.</p>
            
            <h2>How It Works</h2>
            <ol>
                <li>Register your server by providing an info endpoint URL</li>
                <li>Your server must return JSON data when we poll the /info endpoint</li>
                <li>We display the server details to players looking for servers to join</li>
            </ol>
            
            <h2>Info Endpoint Format</h2>
            <p>Your server's info endpoint should return JSON with any fields you want displayed. Example:</p>
            <pre style="background: #0f3460; padding: 15px; border-radius: 5px;">
{
    "players": "24/32",
    "map": "de_dust2",
    "mode": "Competitive",
    "description": "Welcome to our server!"
}
            </pre>
        </div>
    </div>
</body>
</html>
"""


def check_xss_in_page(page_content):
    proc = subprocess.Popen(["timeout", "8", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://127.0.0.1:5000/' + fn
    xss_detected = False
    try:
        of = open(fn, 'w')
        of.write(page_content)
        of.close()
        proc.stdin.write(url)
        proc.stdin.close()
        output = proc.stdout.read()
        lines = output.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line and line != 'success' and line != 'fail' and line != 'Failed to load the page.':
                xss_detected = True
                break
    except Exception as e:
        pass
    finally:
        try:
            os.unlink(fn)
        except:
            pass
    return xss_detected


def fetch_server_info(info_url):
    try:
        req = urllib2.Request(info_url, headers={'User-Agent': 'GameTrack/1.0'})
        response = urllib2.urlopen(req, timeout=5)
        data = json.loads(response.read())
        return data
    except Exception as e:
        return None


def render_extended_details(server_data):
    output = ""
    if server_data and isinstance(server_data, dict):
        for field, value in server_data.items():
            value_str = str(value) if value else ""
            value_str = re.sub(
                r'((https*:\/\/|https*:\/\/www\.|www\.)[\w\d\.\-\/=$?]*)',
                r"<a href='\1' target='_blank'>\1</a>",
                html_parser.unescape(value_str)
            )
            output += "\n    <tr><td> {0} </td><td> {1} </td></tr>".format(cgi.escape(field), value_str)
    return output


@app.route('/')
def index():
    return INDEX_PAGE


@app.route('/about')
def about():
    return ABOUT_PAGE


@app.route('/servers')
def servers():
    if not registered_servers:
        server_list = "<p>No servers registered yet. <a href='/register'>Register your server</a></p>"
    else:
        server_list = ""
        for server_id, server in registered_servers.items():
            server_list += """
            <div class="server-item">
                <h3>{name}</h3>
                <p>Game: {game_type}</p>
                <p><a href="/server/{server_id}">View Details</a></p>
            </div>
            """.format(name=cgi.escape(server['name']), game_type=cgi.escape(server['game_type']), server_id=server_id)
    
    return SERVERS_PAGE.format(server_list=server_list)


@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        info_url = request.form.get('info_url', '').strip()
        game_type = request.form.get('game_type', '').strip()
        server_info_json = request.form.get('server_info', '').strip()
        
        if not name or not game_type:
            message = '<p class="error">Server name and game type are required.</p>'
        elif not info_url and not server_info_json:
            message = '<p class="error">Please provide either an info endpoint URL or server info JSON.</p>'
        else:
            server_id = os.urandom(8).encode('hex')
            registered_servers[server_id] = {
                'name': name,
                'info_url': info_url if info_url else None,
                'game_type': game_type
            }
            
            server_info = None
            if server_info_json:
                try:
                    server_info = json.loads(server_info_json)
                except:
                    message = '<p class="error">Invalid JSON format in server info.</p>'
                    del registered_servers[server_id]
                    return REGISTER_PAGE.format(message=message)
            elif info_url:
                server_info = fetch_server_info(info_url)
            
            if server_info:
                server_data_cache[server_id] = server_info
                message = '<p class="success">Server registered successfully! <a href="/server/{0}">View your server</a></p>'.format(server_id)
            else:
                server_data_cache[server_id] = {}
                message = '<p class="success">Server registered. <a href="/server/{0}">View your server</a></p>'.format(server_id)
    
    return REGISTER_PAGE.format(message=message)


@app.route('/server/<server_id>')
def server_details(server_id):
    if server_id not in registered_servers:
        return "Server not found", 404
    
    server = registered_servers[server_id]
    
    if server.get('info_url'):
        fresh_info = fetch_server_info(server['info_url'])
        if fresh_info:
            server_data_cache[server_id] = fresh_info
    
    cached_data = server_data_cache.get(server_id, {})
    extended_details = render_extended_details(cached_data)
    
    status = "Online" if cached_data else "Offline / No Data"
    
    page_content = SERVER_DETAILS_PAGE.format(
        server_name=cgi.escape(server['name']),
        game_type=cgi.escape(server['game_type']),
        status=status,
        extended_details=extended_details
    )
    
    xss_detected = check_xss_in_page(page_content)
    
    if xss_detected:
        page_content = page_content.replace('</body>', '<script>document.body.innerHTML += "<div style=\\"position:fixed;bottom:20px;right:20px;background:#f72585;padding:20px;border-radius:5px;\\">Admin Note: ' + flag_value + '</div>";</script></body>')
    
    response = make_response(page_content)
    response.headers["X-XSS-Protection"] = "0"
    return response


@app.errorhandler(404)
def not_found(e):
    return "Page not found", 404


@app.errorhandler(500)
def server_error(e):
    return "Internal server error", 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
