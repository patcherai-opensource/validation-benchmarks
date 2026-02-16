# encoding=utf-8

from flask import Flask, request, jsonify
import subprocess
import os
import re
import json
import hashlib
import html
import urllib.parse
import tempfile
import logging

logging.basicConfig(level=logging.WARNING)

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False


def get_flag():
    try:
        with open('secret.txt') as f:
            return f.read().strip()
    except Exception:
        return ''


def js_escape(input_str):
    """
    Escape a string for safe inclusion in JavaScript string contexts.
    Handles quotes, backslashes, newlines, and script-breaking sequences.
    """
    result = input_str
    # Backslash must be escaped first to prevent double-escaping
    result = result.replace('\\', '\\\\')
    result = result.replace("'", "\\'")
    result = result.replace('"', '\\"')
    result = result.replace('\r', '\\r')
    result = result.replace('\n', '\\n')
    result = result.replace('</', '<\\/')
    result = result.replace('<!--', '<\\!--')
    result = result.replace('<s', '<\\s')
    result = result.replace('<S', '<\\S')
    return result


def render_preview(template_content, variables):
    """
    Render a template by substituting variables with modifier support.
    Supports variable syntax: {$varname} and modifiers like |escape:'type'
    """
    def replace_var(match):
        full_expr = match.group(1)
        parts = full_expr.split('|')
        var_name = parts[0].strip().lstrip('$')

        value = str(variables.get(var_name, ''))

        # Process modifiers
        for modifier_str in parts[1:]:
            modifier_str = modifier_str.strip()
            if modifier_str.startswith('escape:'):
                esc_match = re.match(r"escape:\s*['\"]?(\w+)['\"]?", modifier_str)
                if esc_match:
                    esc_type = esc_match.group(1)
                    if esc_type == 'html':
                        value = html.escape(value, quote=True)
                    elif esc_type == 'htmlall':
                        value = html.escape(value, quote=True)
                    elif esc_type == 'url':
                        value = urllib.parse.quote(value, safe='')
                    elif esc_type == 'javascript':
                        value = js_escape(value)
            elif modifier_str == 'upper':
                value = value.upper()
            elif modifier_str == 'lower':
                value = value.lower()
            elif modifier_str == 'capitalize':
                value = value.capitalize()
            elif modifier_str == 'truncate':
                value = value[:80]
            elif modifier_str == 'strip_tags':
                value = re.sub(r'<[^>]+>', '', value)
            elif modifier_str == 'nl2br':
                value = value.replace('\n', '<br />')
            elif modifier_str == 'count_characters':
                value = str(len(value))

        return value

    rendered = re.sub(r'\{\$([^}]+)\}', replace_var, template_content)
    return rendered


def evaluate_rendered_page(html_content):
    """
    Evaluate rendered HTML in Node.js to detect JavaScript execution.
    Returns the alert message if any JS alert was triggered.
    """
    # Extract script contents from the rendered HTML
    script_blocks = re.findall(r'<script[^>]*>(.*?)</script>', html_content, re.DOTALL | re.IGNORECASE)

    if not script_blocks:
        return ''

    # Build a Node.js evaluation wrapper
    combined_js = '\n'.join(script_blocks)

    node_wrapper = '''
(function() {
    var _alert_messages = [];
    var _stdout_write = process.stdout.write.bind(process.stdout);
    var _process_exit = process.exit.bind(process);

    // Browser-like environment simulation
    function alert(msg) { _alert_messages.push(String(msg)); }
    function confirm(msg) { _alert_messages.push(String(msg)); return false; }
    function prompt(msg) { _alert_messages.push(String(msg)); return null; }
    var document = {
        getElementById: function() { return { textContent: '', innerHTML: '', setAttribute: function(){}, style: {} }; },
        querySelector: function() { return null; },
        querySelectorAll: function() { return []; },
        createElement: function() { return { style: {}, setAttribute: function(){}, appendChild: function(){} }; },
        body: { appendChild: function(){}, innerHTML: '' },
        cookie: '',
        write: function() {},
        writeln: function() {}
    };
    var window = { location: { href: '' }, document: document, alert: alert };
    var navigator = { userAgent: '' };
    var location = { href: '', hostname: 'localhost' };
    var console = { log: function(){}, error: function(){}, warn: function(){} };
    var XMLHttpRequest = function() { return { open: function(){}, send: function(){} }; };
    var fetch = function() { return Promise.resolve({ text: function() { return Promise.resolve(''); } }); };
    var require = undefined;
    var module = undefined;
    var exports = undefined;
    var Buffer = undefined;

    try {
''' + combined_js + '''
    } catch(e) {}
    if (_alert_messages.length > 0) {
        _stdout_write(_alert_messages[0]);
    } else {
        _stdout_write('');
    }
    _process_exit(0);
})();
'''

    try:
        fd, tmpfile = tempfile.mkstemp(suffix='.js')
        with os.fdopen(fd, 'w') as f:
            f.write(node_wrapper)

        proc = subprocess.run(
            ['timeout', '5', 'node', tmpfile],
            capture_output=True,
            text=True,
            timeout=10
        )
        result = proc.stdout.strip()
    except Exception:
        result = ''
    finally:
        try:
            os.unlink(tmpfile)
        except Exception:
            pass

    return result


# ============================================================
# Routes
# ============================================================

@app.route('/')
def index():
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TemplateCraft - Template Preview Engine</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f7fa; color: #333; }
        .navbar { background: #2c3e50; padding: 12px 24px; display: flex; align-items: center; justify-content: space-between; }
        .navbar h1 { color: white; font-size: 1.3em; }
        .navbar nav a { color: #ecf0f1; text-decoration: none; margin-left: 20px; font-size: 0.9em; }
        .navbar nav a:hover { color: #3498db; }
        .container { max-width: 960px; margin: 30px auto; padding: 0 20px; }
        .card { background: white; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.12); padding: 24px; margin-bottom: 20px; }
        .card h2 { margin-bottom: 12px; color: #2c3e50; }
        .card p { color: #666; line-height: 1.6; }
        .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 16px; margin-top: 20px; }
        .feature { background: #f8f9fa; padding: 16px; border-radius: 4px; border-left: 3px solid #3498db; }
        .feature h3 { font-size: 0.95em; margin-bottom: 6px; }
        .feature p { font-size: 0.85em; color: #777; }
        footer { text-align: center; padding: 20px; color: #999; font-size: 0.8em; }
        code { background: #f0f0f0; padding: 2px 6px; border-radius: 3px; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="navbar">
        <h1>TemplateCraft</h1>
        <nav>
            <a href="/">Home</a>
            <a href="/docs">Documentation</a>
            <a href="/preview">Live Preview</a>
            <a href="/modifiers">Modifiers</a>
        </nav>
    </div>
    <div class="container">
        <div class="card">
            <h2>Welcome to TemplateCraft</h2>
            <p>TemplateCraft is a lightweight template rendering engine with live preview capabilities. Test your templates with variable substitution and modifier support before deploying to production.</p>
        </div>
        <div class="card">
            <h2>Features</h2>
            <div class="features">
                <div class="feature">
                    <h3>Variable Substitution</h3>
                    <p>Use <code>{$variable}</code> syntax to inject dynamic content into your templates.</p>
                </div>
                <div class="feature">
                    <h3>Output Modifiers</h3>
                    <p>Apply modifiers like <code>|escape</code>, <code>|upper</code>, <code>|truncate</code> to transform output.</p>
                </div>
                <div class="feature">
                    <h3>Live Preview</h3>
                    <p>See your rendered templates instantly with the live preview engine.</p>
                </div>
                <div class="feature">
                    <h3>Security Escaping</h3>
                    <p>Built-in escaping for HTML, URL, and JavaScript contexts to keep your output safe.</p>
                </div>
            </div>
        </div>
    </div>
    <footer>&copy; 2024 TemplateCraft Engine v4.3.1</footer>
</body>
</html>'''


@app.route('/docs')
def docs():
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>TemplateCraft - Documentation</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f7fa; color: #333; }
        .navbar { background: #2c3e50; padding: 12px 24px; display: flex; align-items: center; justify-content: space-between; }
        .navbar h1 { color: white; font-size: 1.3em; }
        .navbar nav a { color: #ecf0f1; text-decoration: none; margin-left: 20px; font-size: 0.9em; }
        .container { max-width: 960px; margin: 30px auto; padding: 0 20px; }
        .card { background: white; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.12); padding: 24px; margin-bottom: 20px; }
        .card h2 { margin-bottom: 12px; color: #2c3e50; }
        .card h3 { margin: 16px 0 8px; color: #34495e; }
        pre { background: #2d2d2d; color: #f8f8f2; padding: 16px; border-radius: 4px; overflow-x: auto; margin: 10px 0; font-size: 0.9em; }
        code { background: #f0f0f0; padding: 2px 6px; border-radius: 3px; font-size: 0.9em; }
        pre code { background: none; }
        p { line-height: 1.6; margin-bottom: 10px; color: #555; }
        table { width: 100%; border-collapse: collapse; margin: 12px 0; }
        th, td { padding: 8px 12px; border: 1px solid #ddd; text-align: left; font-size: 0.9em; }
        th { background: #f8f9fa; }
        footer { text-align: center; padding: 20px; color: #999; font-size: 0.8em; }
    </style>
</head>
<body>
    <div class="navbar">
        <h1>TemplateCraft</h1>
        <nav>
            <a href="/">Home</a>
            <a href="/docs">Documentation</a>
            <a href="/preview">Live Preview</a>
            <a href="/modifiers">Modifiers</a>
        </nav>
    </div>
    <div class="container">
        <div class="card">
            <h2>Template Syntax</h2>
            <p>TemplateCraft uses a familiar template syntax inspired by popular template engines. Variables are referenced using the <code>{$variable}</code> syntax.</p>
            <h3>Variables</h3>
            <pre><code>&lt;p&gt;Hello, {$username}!&lt;/p&gt;</code></pre>
            <h3>Modifiers</h3>
            <p>Modifiers transform variable output. Chain them with the pipe <code>|</code> operator.</p>
            <pre><code>{$name|upper}
{$email|escape:'html'}
{$url|escape:'url'}
{$content|escape:'javascript'}
{$title|capitalize}
{$text|truncate}</code></pre>
        </div>
        <div class="card">
            <h2>Escape Modifier</h2>
            <p>The <code>escape</code> modifier sanitizes output for different contexts:</p>
            <table>
                <tr><th>Type</th><th>Syntax</th><th>Description</th></tr>
                <tr><td>HTML</td><td><code>|escape:'html'</code></td><td>Escapes HTML special characters (&amp;, &lt;, &gt;, quotes)</td></tr>
                <tr><td>URL</td><td><code>|escape:'url'</code></td><td>URL-encodes the string</td></tr>
                <tr><td>JavaScript</td><td><code>|escape:'javascript'</code></td><td>Escapes for JavaScript string contexts (quotes, backslashes, newlines)</td></tr>
            </table>
        </div>
        <div class="card">
            <h2>Live Preview API</h2>
            <p>Use the <code>/preview</code> endpoint to test template rendering. Submit your template and variables to see the rendered output.</p>
            <h3>POST /api/v1/render</h3>
            <p>Programmatic access to the template renderer.</p>
            <pre><code>POST /api/v1/render
Content-Type: application/json

{
    "template": "&lt;p&gt;Hello, {$name|escape:'html'}!&lt;/p&gt;",
    "variables": {
        "name": "World"
    }
}</code></pre>
            <h3>Response</h3>
            <p>Returns the rendered HTML output. The preview engine evaluates scripts to verify rendering correctness.</p>
        </div>
    </div>
    <footer>&copy; 2024 TemplateCraft Engine v4.3.1</footer>
</body>
</html>'''


@app.route('/modifiers')
def modifiers():
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>TemplateCraft - Modifier Reference</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f7fa; color: #333; }
        .navbar { background: #2c3e50; padding: 12px 24px; display: flex; align-items: center; justify-content: space-between; }
        .navbar h1 { color: white; font-size: 1.3em; }
        .navbar nav a { color: #ecf0f1; text-decoration: none; margin-left: 20px; font-size: 0.9em; }
        .container { max-width: 960px; margin: 30px auto; padding: 0 20px; }
        .card { background: white; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.12); padding: 24px; margin-bottom: 20px; }
        .card h2 { margin-bottom: 12px; color: #2c3e50; }
        pre { background: #2d2d2d; color: #f8f8f2; padding: 16px; border-radius: 4px; overflow-x: auto; margin: 10px 0; font-size: 0.9em; }
        code { background: #f0f0f0; padding: 2px 6px; border-radius: 3px; font-size: 0.9em; }
        pre code { background: none; }
        p { line-height: 1.6; margin-bottom: 10px; color: #555; }
        .modifier-section { margin: 16px 0; padding: 16px; background: #f8f9fa; border-radius: 4px; border-left: 3px solid #3498db; }
        .modifier-section h3 { margin-bottom: 6px; color: #2c3e50; }
        footer { text-align: center; padding: 20px; color: #999; font-size: 0.8em; }
    </style>
</head>
<body>
    <div class="navbar">
        <h1>TemplateCraft</h1>
        <nav>
            <a href="/">Home</a>
            <a href="/docs">Documentation</a>
            <a href="/preview">Live Preview</a>
            <a href="/modifiers">Modifiers</a>
        </nav>
    </div>
    <div class="container">
        <div class="card">
            <h2>Modifier Reference</h2>
            <p>Complete list of available output modifiers.</p>
        </div>
        <div class="card">
            <div class="modifier-section">
                <h3>escape</h3>
                <p>Escapes variable output for safe inclusion in different contexts.</p>
                <pre><code>{$var|escape:'html'}       - HTML entity encoding
{$var|escape:'url'}        - URL encoding
{$var|escape:'javascript'} - JavaScript string escaping</code></pre>
            </div>
            <div class="modifier-section">
                <h3>upper / lower / capitalize</h3>
                <p>Case transformation modifiers.</p>
                <pre><code>{$name|upper}      - CONVERTS TO UPPERCASE
{$name|lower}      - converts to lowercase
{$name|capitalize} - Capitalizes first letter</code></pre>
            </div>
            <div class="modifier-section">
                <h3>truncate</h3>
                <p>Truncates a string to a specified length.</p>
                <pre><code>{$text|truncate}</code></pre>
            </div>
            <div class="modifier-section">
                <h3>strip_tags</h3>
                <p>Removes all HTML tags from the string.</p>
                <pre><code>{$content|strip_tags}</code></pre>
            </div>
            <div class="modifier-section">
                <h3>nl2br</h3>
                <p>Converts newlines to HTML &lt;br&gt; tags.</p>
                <pre><code>{$content|nl2br}</code></pre>
            </div>
            <div class="modifier-section">
                <h3>count_characters</h3>
                <p>Returns the character count of the string.</p>
                <pre><code>{$text|count_characters}</code></pre>
            </div>
        </div>
    </div>
    <footer>&copy; 2024 TemplateCraft Engine v4.3.1</footer>
</body>
</html>'''


@app.route('/preview', methods=['GET'])
def preview_page():
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>TemplateCraft - Live Preview</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f7fa; color: #333; }
        .navbar { background: #2c3e50; padding: 12px 24px; display: flex; align-items: center; justify-content: space-between; }
        .navbar h1 { color: white; font-size: 1.3em; }
        .navbar nav a { color: #ecf0f1; text-decoration: none; margin-left: 20px; font-size: 0.9em; }
        .container { max-width: 960px; margin: 30px auto; padding: 0 20px; }
        .card { background: white; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.12); padding: 24px; margin-bottom: 20px; }
        .card h2 { margin-bottom: 12px; color: #2c3e50; }
        .split { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
        textarea { width: 100%; height: 200px; font-family: 'Courier New', monospace; font-size: 0.9em; padding: 12px; border: 1px solid #ddd; border-radius: 4px; resize: vertical; }
        label { display: block; margin-bottom: 6px; font-weight: 600; color: #34495e; font-size: 0.9em; }
        button { background: #3498db; color: white; border: none; padding: 10px 24px; border-radius: 4px; cursor: pointer; font-size: 0.95em; margin-top: 10px; }
        button:hover { background: #2980b9; }
        .info { background: #eaf4fd; border-left: 3px solid #3498db; padding: 12px; margin: 12px 0; font-size: 0.85em; color: #2c3e50; }
        footer { text-align: center; padding: 20px; color: #999; font-size: 0.8em; }
        p { line-height: 1.6; margin-bottom: 10px; color: #555; }
        code { background: #f0f0f0; padding: 2px 6px; border-radius: 3px; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="navbar">
        <h1>TemplateCraft</h1>
        <nav>
            <a href="/">Home</a>
            <a href="/docs">Documentation</a>
            <a href="/preview">Live Preview</a>
            <a href="/modifiers">Modifiers</a>
        </nav>
    </div>
    <div class="container">
        <div class="card">
            <h2>Live Template Preview</h2>
            <p>Enter a template and variables to see the rendered output. The preview engine processes your template server-side and returns the result.</p>
            <div class="info">
                Templates use <code>{$variable}</code> syntax. Apply modifiers with <code>|modifier</code> (e.g., <code>{$name|escape:'html'}</code>).
            </div>
        </div>

        <form method="POST" action="/api/v1/render">
            <div class="card">
                <div class="split">
                    <div>
                        <label>Template</label>
                        <textarea name="template" placeholder="Enter your template here...">&lt;html&gt;
&lt;body&gt;
&lt;h1&gt;Greeting Card&lt;/h1&gt;
&lt;p&gt;Hello, {$username|escape:'html'}!&lt;/p&gt;
&lt;script&gt;
var greeting = `Welcome, {$username|escape:'javascript'}`;
document.getElementById('msg').textContent = greeting;
&lt;/script&gt;
&lt;div id="msg"&gt;&lt;/div&gt;
&lt;/body&gt;
&lt;/html&gt;</textarea>
                    </div>
                    <div>
                        <label>Variables (JSON)</label>
                        <textarea name="variables" placeholder='{"key": "value"}'>{
    "username": "World"
}</textarea>
                    </div>
                </div>
                <button type="submit">Render Preview</button>
            </div>
        </form>
    </div>
    <footer>&copy; 2024 TemplateCraft Engine v4.3.1</footer>
</body>
</html>'''


@app.route('/api/v1/render', methods=['POST'])
def api_render():
    """
    Template rendering endpoint. Accepts template + variables and returns
    rendered output. The rendered HTML is evaluated server-side to verify
    script correctness.
    """
    template = None
    variables = None

    content_type = request.content_type or ''

    if 'application/json' in content_type:
        try:
            data = request.get_json(force=True)
            template = data.get('template', '')
            variables = data.get('variables', {})
        except Exception:
            return jsonify({'error': 'Invalid JSON payload'}), 400
    else:
        template = request.form.get('template', '')
        variables_raw = request.form.get('variables', '{}')
        try:
            variables = json.loads(variables_raw)
        except (ValueError, TypeError):
            variables = {}

    if not template:
        return jsonify({'error': 'Template content is required'}), 400

    if not isinstance(variables, dict):
        return jsonify({'error': 'Variables must be a JSON object'}), 400

    # Render the template with variable substitution
    try:
        rendered = render_preview(template, variables)
    except Exception:
        return jsonify({'error': 'Template rendering failed'}), 500

    # Evaluate any scripts in the rendered output for preview verification
    alert_result = evaluate_rendered_page(rendered)

    # If JavaScript execution was detected, this represents a
    # security boundary violation in the template sandbox
    if alert_result == 'XSS':
        flag = get_flag()
        response_html = '''<!DOCTYPE html>
<html><head><title>Render Result</title>
<style>
body {{ font-family: sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; }}
.alert {{ background: #d4edda; border: 1px solid #c3e6cb; padding: 16px; border-radius: 4px; margin: 20px 0; }}
.rendered {{ background: #f8f9fa; border: 1px solid #dee2e6; padding: 16px; border-radius: 4px; margin: 20px 0; }}
h2 {{ color: #2c3e50; }}
</style></head>
<body>
<h2>Template Rendered Successfully</h2>
<div class="rendered"><h3>Output</h3><pre>{rendered}</pre></div>
<div class="alert"><strong>System Notice:</strong> {flag}</div>
</body></html>'''.format(rendered=html.escape(rendered[:500]), flag=flag)
        return response_html

    # Normal render response
    response_html = '''<!DOCTYPE html>
<html><head><title>Render Result</title>
<style>
body {{ font-family: sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; }}
.rendered {{ background: #f8f9fa; border: 1px solid #dee2e6; padding: 16px; border-radius: 4px; margin: 20px 0; }}
h2 {{ color: #2c3e50; }}
a {{ color: #3498db; }}
</style></head>
<body>
<h2>Template Rendered Successfully</h2>
<div class="rendered"><h3>Output Preview</h3><pre>{rendered}</pre></div>
<p><a href="/preview">&larr; Back to editor</a></p>
</body></html>'''.format(rendered=html.escape(rendered[:2000]))
    return response_html


@app.route('/health')
def health():
    return 'OK', 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
