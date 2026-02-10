from flask import Flask, render_template
import paramiko
import os

app = Flask(__name__)

def get_system_status():
    """Get basic system status for the dashboard"""
    hostname = 'localhost'
    port = 22
    username = 'guest'
    password = 'guest'
    command = 'uptime && echo "---" && df -h / | tail -1'
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname, port=port, username=username, password=password)
        stdin, stdout, stderr = client.exec_command(command)
        status = stdout.read().decode('utf-8')
        client.close()
        return status
    except Exception as e:
        return "Status unavailable"

@app.route('/')
def index():
    status = get_system_status()
    return render_template('index.html', status=status)

@app.route('/docs')
def docs():
    return render_template('docs.html')

@app.errorhandler(404)
def not_found(e):
    return "Not Found", 404

@app.errorhandler(500)
def server_error(e):
    return "Internal Server Error", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)

