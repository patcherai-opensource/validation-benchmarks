# encoding=utf8
# Game Server List (LGSL-inspired) - Stored XSS vulnerability
# This simulates CVE in lgsl where game server info is fetched and displayed without proper escaping

from flask import Flask, request, Response, make_response, url_for, jsonify, redirect
import string
import subprocess
import os
import re
import cgi
import urllib
import json
import sys
try:
    from html import unescape as html_unescape
except ImportError:
    import HTMLParser
    _html_parser = HTMLParser.HTMLParser()
    html_unescape = _html_parser.unescape

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flags = open('secret.txt').read().split()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

# In-memory storage for registered game servers
# Structure: {server_id: {name, host, port, info: {field: value}}}
game_servers = {}
next_server_id = 1

def check_xss(page, flag):
    """Check if the page triggers an XSS alert with 'XSS' message"""
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://' + os.environ.get('APP_HOST', 'localhost') + ':' + os.environ.get('APP_PORT', '5000') + '/' + fn
    try:
        of = open(fn, 'w')
        of.write(page)
        of.close()
        logging.info("Checking page for XSS")
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
        logging.info("XSS Check Result: " + result)
    finally:
        os.unlink(fn)
    
    return result

@app.route('/')
def index():
    """Main page - list all registered game servers"""
    server_list = ""
    for sid, server in game_servers.items():
        server_list += '<tr><td><a href="/server/{0}">{1}</a></td><td>{2}:{3}</td><td><a href="/server/{0}">View Details</a></td></tr>'.format(
            sid, cgi.escape(server.get('name', 'Unknown')), cgi.escape(server.get('host', '')), server.get('port', '')
        )
    
    if not server_list:
        server_list = '<tr><td colspan="3">No servers registered. <a href="/register">Register a server</a> to get started.</td></tr>'
    
    return '''
    <html>
        <head>
            <title>Game Server List (LGSL)</title>
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #1a1a2e; color: #eee; }
                h1 { color: #e94560; }
                table { width: 100%%; border-collapse: collapse; margin-top: 20px; }
                th, td { border: 1px solid #444; padding: 12px; text-align: left; }
                th { background: #16213e; }
                tr:hover { background: #0f3460; }
                a { color: #e94560; text-decoration: none; }
                a:hover { text-decoration: underline; }
                .nav { margin-bottom: 20px; }
                .nav a { margin-right: 20px; background: #e94560; padding: 10px 20px; border-radius: 5px; color: white; }
            </style>
        </head>
        <body>
            <h1>Game Server List</h1>
            <div class="nav">
                <a href="/register">Register Server</a>
                <a href="/api/help">API Documentation</a>
            </div>
            <table>
                <tr><th>Server Name</th><th>Address</th><th>Actions</th></tr>
                %s
            </table>
            <p style="margin-top: 30px; color: #888;">
                Game Server List (LGSL) - Server monitoring and information display
            </p>
        </body>
    </html>
    ''' % server_list

@app.route('/register', methods=['GET', 'POST'])
def register_server():
    """Register a new game server"""
    global next_server_id
    
    if request.method == 'POST':
        name = request.form.get('name', 'Unnamed Server')
        host = request.form.get('host', '')
        port = request.form.get('port', '27015')
        server_info_json = request.form.get('server_info', '{}')
        
        if not host:
            return "Error: Host is required", 400
        
        # Parse the server info JSON (this simulates what would come from the game server's /info endpoint)
        try:
            server_info = json.loads(server_info_json)
            if not isinstance(server_info, dict):
                server_info = {}
        except:
            server_info = {}
        
        server_id = next_server_id
        next_server_id += 1
        
        game_servers[server_id] = {
            'name': name,
            'host': host,
            'port': port,
            'info': server_info
        }
        
        return redirect('/server/{}'.format(server_id))
    
    return '''
    <html>
        <head>
            <title>Register Game Server</title>
            <link rel="stylesheet" type="text/css" href="static/css/style.css">
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #1a1a2e; color: #eee; }
                h1 { color: #e94560; }
                form { max-width: 600px; }
                label { display: block; margin-top: 15px; color: #888; }
                input, textarea { width: 100%%; padding: 10px; margin-top: 5px; border: 1px solid #444; background: #16213e; color: #eee; border-radius: 5px; box-sizing: border-box; }
                textarea { font-family: monospace; }
                button { margin-top: 20px; padding: 12px 30px; background: #e94560; color: white; border: none; cursor: pointer; border-radius: 5px; }
                button:hover { background: #c73e54; }
                a { color: #e94560; }
                .hint { font-size: 12px; color: #666; margin-top: 5px; }
            </style>
        </head>
        <body>
            <h1>Register Game Server</h1>
            <p><a href="/">&larr; Back to server list</a></p>
            <form method="POST">
                <label>Server Name:</label>
                <input type="text" name="name" placeholder="My Game Server" required>
                
                <label>Host/IP:</label>
                <input type="text" name="host" placeholder="192.168.1.100" required>
                
                <label>Port:</label>
                <input type="text" name="port" value="27015" placeholder="27015">
                
                <label>Server Info (JSON):</label>
                <textarea name="server_info" rows="8" placeholder='{"Players": "24/32", "Map": "de_dust2"}'></textarea>
                <p class="hint">Enter server information in JSON format. This simulates data returned by a game server's info endpoint.</p>
                
                <button type="submit">Register Server</button>
            </form>
        </body>
    </html>
    '''

@app.route('/api/register', methods=['POST'])
def api_register_server():
    """API endpoint to register a game server (simulates lgsl polling a game server)"""
    global next_server_id
    
    # Get data from JSON body or form
    try:
        data = request.get_json() or {}
    except:
        data = {}
    
    name = data.get('name', request.form.get('name', 'Unnamed Server'))
    host = data.get('host', request.form.get('host', ''))
    port = data.get('port', request.form.get('port', '27015'))
    
    # Server info - this is the untrusted data from the "game server"
    # In the real CVE, this comes from lgsl_query_40 fetching from the game server's /info endpoint
    server_info = data.get('server_info', data.get('info', {}))
    if isinstance(server_info, str):
        try:
            server_info = json.loads(server_info)
        except:
            server_info = {}
    
    if not host:
        return jsonify({'error': 'Host is required'}), 400
    
    server_id = next_server_id
    next_server_id += 1
    
    # Store the server with its info (untrusted data from the game server)
    game_servers[server_id] = {
        'name': name,
        'host': host,
        'port': port,
        'info': server_info if isinstance(server_info, dict) else {}
    }
    
    return jsonify({
        'success': True,
        'server_id': server_id,
        'view_url': '/server/{}'.format(server_id)
    })

@app.route('/server/<int:server_id>')
def server_details(server_id):
    """
    Display server details page.
    This is similar to lgsl_details.php which displays server info without proper escaping.
    
    VULNERABILITY: The server info values are passed through html_entity_decode (simulated)
    and then rendered without proper escaping, allowing stored XSS.
    
    From the CVE:
    $value = preg_replace(
        '/((https*:\/\/|https*:\/\/www\.|www\.)[\w\d\.\-\/=$?]*)/i',
        "<a href='$1' target='_blank'>$1</a>",
        html_entity_decode($value)
    );
    $output .= "\n    <tr><td> {$field} </td><td> {$value} </td></tr>";
    """
    if server_id not in game_servers:
        return "Server not found", 404
    
    server = game_servers[server_id]
    flag = flags[0]
    
    # Build the info table
    # VULNERABILITY: Similar to lgsl_details.php, we process values with html_entity_decode
    # which converts HTML entities back to their original characters, enabling XSS
    info_rows = ""
    for field, value in server.get('info', {}).items():
        # This mimics the vulnerable code in lgsl_details.php:
        # Convert HTML entities back (simulating html_entity_decode)
        # This is the vulnerability - it decodes &lt; to <, &gt; to >, etc.
        decoded_value = html_unescape(str(value))
        
        # Simple URL linkification (like the preg_replace in lgsl)
        decoded_value = re.sub(
            r'(https?://[\w\d.\-/=$?]*)',
            r"<a href='\1' target='_blank'>\1</a>",
            decoded_value
        )
        
        # VULNERABLE: Field name is escaped but value is NOT properly escaped
        # (it was decoded above and injected directly)
        info_rows += "\n    <tr><td> {} </td><td> {} </td></tr>".format(
            cgi.escape(str(field)),
            decoded_value  # NOT ESCAPED - this is the vulnerability!
        )
    
    if not info_rows:
        info_rows = '<tr><td colspan="2">No extended info available.</td></tr>'
    
    # Build the page content
    page_content = '''
    <html>
        <head>
            <title>Server Details - {name}</title>
            <link rel="stylesheet" type="text/css" href="/static/css/style.css">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background: #1a1a2e; color: #eee; }}
                h1 {{ color: #e94560; }}
                h2 {{ color: #888; margin-top: 30px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
                th, td {{ border: 1px solid #444; padding: 12px; text-align: left; }}
                th {{ background: #16213e; width: 200px; }}
                a {{ color: #e94560; text-decoration: none; }}
                a:hover {{ text-decoration: underline; }}
                .info-box {{ background: #16213e; padding: 20px; border-radius: 10px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <p><a href="/">&larr; Back to server list</a></p>
            <h1>Server: {name}</h1>
            
            <div class="info-box">
                <h2>Basic Information</h2>
                <table>
                    <tr><th>Host</th><td>{host}</td></tr>
                    <tr><th>Port</th><td>{port}</td></tr>
                </table>
            </div>
            
            <div class="info-box">
                <h2>Extended Server Information</h2>
                <table>
                    {info_rows}
                </table>
            </div>
        </body>
    </html>
    '''.format(
        name=cgi.escape(server.get('name', 'Unknown')),
        host=cgi.escape(server.get('host', '')),
        port=cgi.escape(str(server.get('port', ''))),
        info_rows=info_rows
    )
    
    # Check if XSS was triggered on this page
    xss_result = check_xss(page_content, flag)
    
    # If XSS with 'XSS' alert was detected, show the flag
    result_message = ""
    if xss_result == 'XSS':
        result_message = '''
        <div style="background: #2e7d32; padding: 20px; margin: 20px 0; border-radius: 10px; text-align: center;">
            <h2 style="color: #fff;">Congratulations! XSS Detected!</h2>
            <p style="color: #fff; font-size: 18px;">Here is your flag: <code style="background: #1a1a2e; padding: 5px 10px; border-radius: 5px;">{}</code></p>
        </div>
        '''.format(flag)
    elif xss_result:
        result_message = '''
        <div style="background: #f57c00; padding: 20px; margin: 20px 0; border-radius: 10px; text-align: center;">
            <h2 style="color: #fff;">Almost there!</h2>
            <p style="color: #fff;">You triggered an alert with "{}" instead of "XSS"</p>
        </div>
        '''.format(cgi.escape(xss_result))
    
    # Insert result message into page if any
    if result_message:
        page_content = page_content.replace('<h1>Server:', result_message + '<h1>Server:')
    
    response = make_response(page_content)
    response.headers["X-XSS-Protection"] = "0"
    return response

@app.route('/api/help')
def api_help():
    """API documentation"""
    return '''
    <html>
        <head>
            <title>API Documentation</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #1a1a2e; color: #eee; }
                h1 { color: #e94560; }
                h2 { color: #888; margin-top: 30px; }
                code { background: #16213e; padding: 2px 8px; border-radius: 3px; }
                pre { background: #16213e; padding: 20px; border-radius: 10px; overflow-x: auto; }
                a { color: #e94560; }
            </style>
        </head>
        <body>
            <p><a href="/">&larr; Back to server list</a></p>
            <h1>API Documentation</h1>
            
            <h2>Register a Server</h2>
            <p><code>POST /api/register</code></p>
            <pre>
{
    "name": "My Game Server",
    "host": "192.168.1.100",
    "port": "27015",
    "server_info": {
        "Players": "24/32",
        "Map": "de_dust2",
        "Game": "Counter-Strike",
        "Version": "1.6"
    }
}
            </pre>
            <p>The <code>server_info</code> object contains extended information about the game server.</p>
            <p>This simulates what LGSL would receive when polling a game server's /info endpoint.</p>
            
            <h2>Example Registration with curl</h2>
            <pre>
curl -X POST http://localhost:8080/api/register \
    -H "Content-Type: application/json" \
    -d '{"name":"Test Server","host":"127.0.0.1","port":"27015","server_info":{"Players":"10/32","Map":"de_dust2"}}'
            </pre>
            
            <h2>View Server Details</h2>
            <p><code>GET /server/&lt;server_id&gt;</code></p>
            <p>Displays the server details page with all stored information.</p>
        </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(debug=True)
