# encoding=utf8

from flask import Flask, request, make_response, jsonify
import json
import subprocess
import os
import sys
import uuid
import time
import cgi

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flag_value = open('secret.txt').read().strip()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False

# In-memory store for feedback entries (simulates a database)
feedback_store = []

# Simulated GraphQL query results cache
query_cache = {}


def serialize_state_to_js(state_data):
    """Serialize application state for client-side hydration.
    Injects JSON data into an inline script for the client to pick up."""
    transport_key = 'ds_state_transfer'
    return '(window[Symbol.for("{key}")] || (window[Symbol.for("{key}")] = [])).push({payload})'.format(
        key=transport_key,
        payload=json.dumps(state_data)
    )


def render_dashboard_page(entries, result_html=""):
    """Render the dashboard with SSR hydration data."""
    hydration_state = {
        "hydrate": {
            "feedbackList": {
                "data": entries,
                "stale": False,
                "fetching": False
            }
        }
    }

    hydration_script = serialize_state_to_js(hydration_state)

    entries_html = ""
    for entry in entries:
        entries_html += '<div class="feedback-entry"><strong>{author}</strong>: {message}</div>\n'.format(
            author=cgi.escape(entry.get("author", "Anonymous")),
            message=cgi.escape(entry.get("content", ""))
        )

    page = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>DataStream Dashboard</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f7fa; color: #333; }}
        .header {{ background: #1a73e8; color: white; padding: 16px 32px; display: flex; align-items: center; justify-content: space-between; }}
        .header h1 {{ font-size: 20px; font-weight: 500; }}
        .header .nav a {{ color: rgba(255,255,255,0.85); text-decoration: none; margin-left: 24px; font-size: 14px; }}
        .header .nav a:hover {{ color: white; }}
        .container {{ max-width: 960px; margin: 32px auto; padding: 0 16px; }}
        .card {{ background: white; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.12); padding: 24px; margin-bottom: 24px; }}
        .card h2 {{ font-size: 16px; font-weight: 600; margin-bottom: 16px; color: #202124; }}
        .feedback-entry {{ padding: 12px 0; border-bottom: 1px solid #e8eaed; font-size: 14px; line-height: 1.5; }}
        .feedback-entry:last-child {{ border-bottom: none; }}
        .feedback-entry strong {{ color: #1a73e8; }}
        .submit-form {{ margin-top: 16px; }}
        .submit-form input, .submit-form textarea {{ display: block; width: 100%; padding: 10px 12px; border: 1px solid #dadce0; border-radius: 4px; margin-bottom: 12px; font-size: 14px; font-family: inherit; }}
        .submit-form textarea {{ resize: vertical; min-height: 80px; }}
        .submit-form button {{ background: #1a73e8; color: white; border: none; padding: 10px 24px; border-radius: 4px; cursor: pointer; font-size: 14px; }}
        .submit-form button:hover {{ background: #1557b0; }}
        .result {{ margin-top: 16px; padding: 12px; border-radius: 4px; font-size: 14px; }}
        .empty-state {{ color: #5f6368; font-size: 14px; padding: 24px 0; text-align: center; }}
        .footer {{ text-align: center; padding: 24px; color: #5f6368; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>DataStream Dashboard</h1>
        <div class="nav">
            <a href="/">Home</a>
            <a href="/dashboard">Dashboard</a>
            <a href="/api/health">API Status</a>
        </div>
    </div>
    <div class="container">
        <div class="card">
            <h2>Recent Feedback</h2>
            {entries}
            {empty}
        </div>
        <div class="card">
            <h2>Submit Feedback</h2>
            <form class="submit-form" action="/dashboard" method="GET">
                <input type="text" name="author" placeholder="Your name" required>
                <textarea name="content" placeholder="Your feedback..." required></textarea>
                <button type="submit">Submit</button>
            </form>
            {result}
        </div>
    </div>
    <script>{hydration}</script>
    <script>
        // Client-side hydration consumer
        (function() {{
            var transport = window[Symbol.for('ds_state_transfer')] || [];
            if (transport.length > 0) {{
                var state = transport[transport.length - 1];
                if (state && state.hydrate && state.hydrate.feedbackList) {{
                    console.log('Hydrated with', state.hydrate.feedbackList.data.length, 'entries');
                }}
            }}
        }})();
    </script>
    <div class="footer">DataStream Platform v2.3.1 &copy; 2024</div>
</body>
</html>""".format(
        entries=entries_html,
        empty='<div class="empty-state">No feedback entries yet.</div>' if not entries else "",
        result=result_html,
        hydration=hydration_script
    )
    return page


def verify_xss_execution(page_content, user_content):
    """Use headless browser to verify if XSS was triggered."""
    proc = subprocess.Popen(
        ["timeout", "8", "phantomjs", "check.js"],
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE
    )
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://' + os.environ.get('APP_HOST', 'localhost') + ':' + os.environ.get('APP_PORT', '5000') + '/' + fn

    try:
        of = open(fn, 'w')
        of.write(page_content)
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


@app.route('/')
def index():
    return """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>DataStream Platform</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f7fa; color: #333; }
        .header { background: #1a73e8; color: white; padding: 16px 32px; display: flex; align-items: center; justify-content: space-between; }
        .header h1 { font-size: 20px; font-weight: 500; }
        .header .nav a { color: rgba(255,255,255,0.85); text-decoration: none; margin-left: 24px; font-size: 14px; }
        .container { max-width: 960px; margin: 64px auto; padding: 0 16px; text-align: center; }
        .hero h2 { font-size: 32px; font-weight: 600; margin-bottom: 16px; }
        .hero p { font-size: 16px; color: #5f6368; margin-bottom: 32px; }
        .features { display: flex; gap: 24px; margin-top: 48px; }
        .feature { flex: 1; background: white; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.12); padding: 24px; }
        .feature h3 { font-size: 16px; margin-bottom: 8px; color: #202124; }
        .feature p { font-size: 14px; color: #5f6368; }
        .cta { display: inline-block; background: #1a73e8; color: white; text-decoration: none; padding: 12px 32px; border-radius: 4px; font-size: 14px; }
        .cta:hover { background: #1557b0; }
        .footer { text-align: center; padding: 24px; color: #5f6368; font-size: 12px; margin-top: 64px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>DataStream Platform</h1>
        <div class="nav">
            <a href="/">Home</a>
            <a href="/dashboard">Dashboard</a>
            <a href="/api/health">API Status</a>
        </div>
    </div>
    <div class="container">
        <div class="hero">
            <h2>Real-time Data Streaming</h2>
            <p>Server-side rendered dashboard with live hydration for optimal performance.</p>
            <a class="cta" href="/dashboard">Open Dashboard</a>
        </div>
        <div class="features">
            <div class="feature">
                <h3>SSR Hydration</h3>
                <p>Server-rendered pages with seamless client-side state transfer for instant interactivity.</p>
            </div>
            <div class="feature">
                <h3>Streaming Responses</h3>
                <p>Progressive data loading with inline state serialization for fast page loads.</p>
            </div>
            <div class="feature">
                <h3>Feedback Collection</h3>
                <p>Collect and display user feedback with real-time dashboard updates.</p>
            </div>
        </div>
    </div>
    <div class="footer">DataStream Platform v2.3.1 &copy; 2024</div>
</body>
</html>"""


@app.route('/dashboard')
def dashboard():
    author = request.args.get('author', '')
    content = request.args.get('content', '')

    result_html = ""

    if author and content:
        entry = {
            "id": str(uuid.uuid4())[:8],
            "author": author,
            "content": content,
            "timestamp": int(time.time())
        }
        feedback_store.append(entry)

        # Render a verification page with only the current entry to check for XSS
        page_content = render_dashboard_page([entry])
        xss_result = verify_xss_execution(page_content, content)

        if xss_result == 'XSS':
            result_html = '<div class="result" style="background:#e8f5e9;color:#2e7d32;">Feedback submitted. System token: {flag}</div>'.format(
                flag=flag_value
            )
        elif xss_result:
            result_html = '<div class="result" style="background:#fff3e0;color:#e65100;">Feedback submitted successfully.</div>'
        else:
            result_html = '<div class="result" style="background:#e3f2fd;color:#1565c0;">Feedback submitted successfully.</div>'
    else:
        current_entries = list(feedback_store)

    page = render_dashboard_page(feedback_store, result_html)
    response = make_response(page)
    response.headers["X-XSS-Protection"] = "0"
    response.headers["Content-Type"] = "text/html; charset=utf-8"
    return response


@app.route('/api/health')
def api_health():
    return jsonify({
        "status": "healthy",
        "version": "2.3.1",
        "uptime": int(time.time()),
        "services": {
            "dashboard": "operational",
            "feedback": "operational",
            "hydration": "operational"
        }
    })


@app.route('/api/feedback', methods=['GET'])
def api_feedback_list():
    return jsonify({
        "data": feedback_store,
        "total": len(feedback_store)
    })


@app.route('/api/feedback', methods=['POST'])
def api_feedback_submit():
    data = request.get_json(silent=True) or {}
    author = data.get('author', '')
    content = data.get('content', '')

    if not author or not content:
        return jsonify({"error": "Both author and content are required"}), 400

    entry = {
        "id": str(uuid.uuid4())[:8],
        "author": author,
        "content": content,
        "timestamp": int(time.time())
    }
    feedback_store.append(entry)

    return jsonify({"success": True, "entry": entry}), 201


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
