from flask import Flask, render_template
import subprocess
app = Flask(__name__)

def get_process_list():
    """Get list of running processes"""
    try:
        result = subprocess.run(['ps', '-aux'], capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        return str(e)

@app.route('/')
def index():
    processes = get_process_list()
    return render_template('index.html', processes=processes.splitlines())

@app.route('/status')
def status():
    """Server status page with system information"""
    return render_template('status.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)

