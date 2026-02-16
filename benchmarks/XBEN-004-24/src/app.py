# -*- coding: utf-8 -*-
"""
Interactive Content Builder - Course Management Platform
A web-based tool for creating and managing interactive learning blocks.
"""

from flask import Flask, request, make_response, jsonify, redirect
import subprocess
import os
import json
import uuid
import cgi
import sys

import logging
logging.basicConfig(level=logging.WARNING)

reload(sys)
sys.setdefaultencoding('utf8')

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24).encode('hex')

# Data store path
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

BLOCKS_FILE = os.path.join(DATA_DIR, 'blocks.json')

# Simulated session (instructor is always authenticated in this simplified setup)
INSTRUCTOR_TOKEN = 'inst_' + os.urandom(8).encode('hex')


def _load_blocks():
    if os.path.exists(BLOCKS_FILE):
        with open(BLOCKS_FILE, 'r') as f:
            return json.load(f)
    return {}


def _save_blocks(blocks):
    with open(BLOCKS_FILE, 'w') as f:
        json.dump(blocks, f, indent=2)


def _get_block(block_id):
    blocks = _load_blocks()
    return blocks.get(block_id)


def _save_block(block_id, block_data):
    blocks = _load_blocks()
    blocks[block_id] = block_data
    _save_blocks(blocks)


def _init_default_blocks():
    """Initialize with default demonstration blocks if none exist."""
    blocks = _load_blocks()
    if blocks:
        return
    default_block = {
        "block_id": "block-001",
        "display_name": "Sample Sorting Activity",
        "mode": "standard",
        "max_attempts": 3,
        "show_title": True,
        "question_text": "Drag each item to the correct category zone below.",
        "show_problem_header": True,
        "weight": 1.0,
        "zones": [
            {
                "uid": "zone-top",
                "title": "Category A",
                "description": "Items belonging to the first category",
                "x": 10, "y": 10, "width": 200, "height": 150,
                "align": "center"
            },
            {
                "uid": "zone-middle",
                "title": "Category B",
                "description": "Items belonging to the second category",
                "x": 10, "y": 200, "width": 200, "height": 150,
                "align": "center"
            },
            {
                "uid": "zone-bottom",
                "title": "Category C",
                "description": "Items belonging to the third category",
                "x": 10, "y": 390, "width": 200, "height": 150,
                "align": "center"
            }
        ],
        "items": [
            {
                "id": 0,
                "displayName": "Element Alpha",
                "imageURL": "",
                "imageDescription": "",
                "zones": ["zone-top"],
                "feedback": {"correct": "Well done!", "incorrect": "Try again."}
            },
            {
                "id": 1,
                "displayName": "Element Beta",
                "imageURL": "",
                "imageDescription": "",
                "zones": ["zone-middle"],
                "feedback": {"correct": "Correct!", "incorrect": "Not quite."}
            },
            {
                "id": 2,
                "displayName": "Element Gamma",
                "imageURL": "",
                "imageDescription": "",
                "zones": ["zone-bottom"],
                "feedback": {"correct": "Right!", "incorrect": "Wrong zone."}
            }
        ],
        "feedback": {
            "start": "Drag the items to their matching zones.",
            "finish": "Great work! You completed the activity."
        },
        "target_img_url": "",
        "target_img_description": "Activity workspace background"
    }
    blocks["block-001"] = default_block
    _save_blocks(blocks)


_init_default_blocks()


def _render_student_view_data(block):
    """
    Prepare block data for student-facing rendering.
    Returns the configuration without answer data.
    """
    items_public = []
    for item in block.get('items', []):
        pub = {
            "id": item["id"],
            "displayName": item.get("displayName", ""),
            "imageURL": item.get("imageURL", ""),
            "imageDescription": item.get("imageDescription", ""),
        }
        items_public.append(pub)

    return {
        "block_id": block["block_id"],
        "display_name": block.get("display_name", ""),
        "type": "interactive-content-block",
        "mode": block.get("mode", "standard"),
        "zones": block.get("zones", []),
        "max_attempts": block.get("max_attempts"),
        "items": items_public,
        "title": block.get("display_name", ""),
        "show_title": block.get("show_title", True),
        "problem_text": block.get("question_text", ""),
        "show_problem_header": block.get("show_problem_header", True),
        "target_img_url": block.get("target_img_url", ""),
        "target_img_description": block.get("target_img_description", ""),
        "feedback": block.get("feedback", {})
    }


# ============================================================
# Page Templates
# ============================================================

MAIN_LAYOUT = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_title} - Interactive Content Builder</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Open Sans', sans-serif; background: #f5f5f5; color: #333; }}
        .header {{ background: #00262b; color: #fff; padding: 12px 24px; display: flex; align-items: center; justify-content: space-between; }}
        .header h1 {{ font-size: 18px; font-weight: 500; }}
        .header nav a {{ color: #9cdceb; text-decoration: none; margin-left: 20px; font-size: 14px; }}
        .header nav a:hover {{ color: #fff; }}
        .container {{ max-width: 1100px; margin: 24px auto; padding: 0 16px; }}
        .card {{ background: #fff; border: 1px solid #ddd; border-radius: 4px; padding: 20px; margin-bottom: 16px; }}
        .card h2 {{ font-size: 20px; margin-bottom: 12px; color: #00262b; }}
        .card h3 {{ font-size: 16px; margin-bottom: 8px; color: #444; }}
        .btn {{ display: inline-block; padding: 8px 16px; border: none; border-radius: 3px; cursor: pointer; font-size: 14px; text-decoration: none; }}
        .btn-primary {{ background: #0075b4; color: #fff; }}
        .btn-primary:hover {{ background: #005f91; }}
        .btn-secondary {{ background: #6c757d; color: #fff; }}
        .btn-danger {{ background: #c32d3a; color: #fff; }}
        .form-group {{ margin-bottom: 14px; }}
        .form-group label {{ display: block; font-size: 13px; font-weight: 600; margin-bottom: 4px; color: #555; }}
        .form-group input, .form-group textarea, .form-group select {{ width: 100%; padding: 8px 10px; border: 1px solid #ccc; border-radius: 3px; font-size: 14px; }}
        .form-group textarea {{ min-height: 80px; resize: vertical; }}
        .form-help {{ font-size: 12px; color: #888; margin-top: 2px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        table th, table td {{ padding: 10px 12px; text-align: left; border-bottom: 1px solid #eee; }}
        table th {{ background: #f8f9fa; font-size: 13px; color: #555; text-transform: uppercase; }}
        .badge {{ display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 12px; }}
        .badge-standard {{ background: #d4edda; color: #155724; }}
        .badge-assessment {{ background: #cce5ff; color: #004085; }}
        .zone-card {{ border: 1px dashed #aaa; padding: 12px; margin-bottom: 8px; border-radius: 4px; background: #fafafa; }}
        .item-card {{ border: 1px solid #ddd; padding: 12px; margin-bottom: 8px; border-radius: 4px; background: #fff; }}
        .alert {{ padding: 12px 16px; border-radius: 4px; margin-bottom: 16px; font-size: 14px; }}
        .alert-success {{ background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
        .alert-error {{ background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }}
        .breadcrumb {{ font-size: 13px; color: #888; margin-bottom: 16px; }}
        .breadcrumb a {{ color: #0075b4; text-decoration: none; }}
        .footer {{ text-align: center; padding: 20px; color: #999; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Interactive Content Builder</h1>
        <nav>
            <a href="/">Dashboard</a>
            <a href="/content/blocks">Content Library</a>
            <a href="/help">Documentation</a>
        </nav>
    </div>
    <div class="container">
        {content}
    </div>
    <div class="footer">Interactive Content Builder v2.4.1</div>
</body>
</html>"""


STUDENT_VIEW_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{block_title} - Learning Activity</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Open Sans', sans-serif; background: #fff; color: #333; }}
        .xblock-container {{ max-width: 900px; margin: 20px auto; padding: 16px; }}
        .xblock-header {{ margin-bottom: 16px; }}
        .xblock-header h2 {{ font-size: 22px; color: #00262b; }}
        .problem-text {{ margin-bottom: 16px; padding: 12px; background: #f8f9fa; border-radius: 4px; }}
        .zones-container {{ display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 20px; }}
        .zone {{ flex: 1; min-width: 200px; border: 2px dashed #aaa; border-radius: 6px; padding: 16px; background: #fafafa; min-height: 120px; }}
        .zone .zone-title {{ font-weight: 600; margin-bottom: 8px; padding-bottom: 4px; border-bottom: 1px solid #ddd; }}
        .zone .zone-description {{ font-size: 12px; color: #666; }}
        .items-bank {{ margin-bottom: 20px; }}
        .items-bank h3 {{ font-size: 16px; margin-bottom: 8px; }}
        .draggable-item {{ display: inline-block; padding: 8px 14px; margin: 4px; border: 1px solid #0075b4; border-radius: 4px; background: #e8f4fd; cursor: grab; font-size: 14px; }}
        .feedback-area {{ padding: 14px; background: #f0f0f0; border-radius: 4px; margin-top: 16px; }}
        .feedback-area h3 {{ margin-bottom: 6px; }}
    </style>
</head>
<body>
    <div class="xblock-container">
        <div class="xblock-header">
            <h2 id="block-title">{block_title_content}</h2>
        </div>
        <div class="problem-text" id="problem-text">
            {problem_text_content}
        </div>
        <div class="zones-container" id="zones-container">
            {zones_content}
        </div>
        <div class="items-bank">
            <h3>Items</h3>
            <div id="items-container">
                {items_content}
            </div>
        </div>
        <div class="feedback-area" id="feedback-area">
            <h3>Feedback</h3>
            <div id="feedback-messages">{feedback_start}</div>
        </div>
    </div>
    <script>
        // Interactive Content Block renderer
        (function() {{
            var config = {block_data_json};

            // Render block title
            if (config.show_title && config.title) {{
                document.getElementById('block-title').innerHTML = config.title;
            }}

            // Render problem text
            if (config.show_problem_header && config.problem_text) {{
                document.getElementById('problem-text').innerHTML = config.problem_text;
            }}

            // Render zones with titles
            var zonesEl = document.getElementById('zones-container');
            zonesEl.innerHTML = '';
            if (config.zones) {{
                config.zones.forEach(function(zone) {{
                    var zoneDiv = document.createElement('div');
                    zoneDiv.className = 'zone';
                    zoneDiv.setAttribute('data-zone', zone.uid);

                    var titleP = document.createElement('p');
                    titleP.className = 'zone-title';
                    titleP.innerHTML = zone.title;
                    zoneDiv.appendChild(titleP);

                    var descP = document.createElement('p');
                    descP.className = 'zone-description';
                    descP.textContent = zone.description || '';
                    zoneDiv.appendChild(descP);

                    zonesEl.appendChild(zoneDiv);
                }});
            }}

            // Render draggable items
            var itemsEl = document.getElementById('items-container');
            itemsEl.innerHTML = '';
            if (config.items) {{
                config.items.forEach(function(item) {{
                    var itemDiv = document.createElement('div');
                    itemDiv.className = 'draggable-item';
                    itemDiv.setAttribute('draggable', 'true');
                    itemDiv.setAttribute('data-item-id', item.id);
                    itemDiv.innerHTML = item.displayName;
                    itemsEl.appendChild(itemDiv);
                }});
            }}

            // Render feedback start message
            if (config.feedback && config.feedback.start) {{
                document.getElementById('feedback-messages').innerHTML = config.feedback.start;
            }}
        }})();
    </script>
</body>
</html>"""


# ============================================================
# Routes
# ============================================================

@app.route('/')
def index():
    blocks = _load_blocks()
    block_rows = ""
    for bid, block in blocks.items():
        mode_badge = 'badge-standard' if block.get('mode') == 'standard' else 'badge-assessment'
        block_rows += """
        <tr>
            <td><a href="/content/blocks/{bid}/edit">{name}</a></td>
            <td><span class="badge {badge}">{mode}</span></td>
            <td>{zones}</td>
            <td>{items}</td>
            <td>
                <a class="btn btn-primary" href="/content/blocks/{bid}/edit">Edit</a>
                <a class="btn btn-secondary" href="/content/blocks/{bid}/preview">Preview</a>
            </td>
        </tr>
        """.format(
            bid=bid,
            name=cgi.escape(block.get("display_name", "Untitled")),
            badge=mode_badge,
            mode=cgi.escape(block.get("mode", "standard")),
            zones=len(block.get("zones", [])),
            items=len(block.get("items", []))
        )

    content = """
    <h2 style="margin-bottom:16px;">Content Dashboard</h2>
    <div class="card">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
            <h3>Interactive Content Blocks</h3>
            <a class="btn btn-primary" href="/content/blocks/new">+ New Block</a>
        </div>
        <table>
            <thead>
                <tr>
                    <th>Block Name</th>
                    <th>Mode</th>
                    <th>Zones</th>
                    <th>Items</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
    </div>
    """.format(rows=block_rows if block_rows else "<tr><td colspan='5' style='text-align:center;color:#999;'>No blocks created yet.</td></tr>")

    return MAIN_LAYOUT.format(page_title="Dashboard", content=content)


@app.route('/content/blocks')
def list_blocks():
    return redirect('/')


@app.route('/content/blocks/new', methods=['GET'])
def new_block_form():
    content = _render_edit_form(None, {})
    return MAIN_LAYOUT.format(page_title="New Block", content=content)


@app.route('/content/blocks/new', methods=['POST'])
def create_block():
    block_id = 'block-' + uuid.uuid4().hex[:8]
    block_data = _parse_block_form(request.form, block_id)
    _save_block(block_id, block_data)
    return redirect('/content/blocks/{}/edit?saved=1'.format(block_id))


@app.route('/content/blocks/<block_id>/edit', methods=['GET'])
def edit_block(block_id):
    block = _get_block(block_id)
    if not block:
        return MAIN_LAYOUT.format(page_title="Not Found", content='<div class="alert alert-error">Block not found.</div>'), 404

    saved_msg = ""
    if request.args.get('saved'):
        saved_msg = '<div class="alert alert-success">Block settings saved successfully.</div>'

    content = saved_msg + _render_edit_form(block_id, block)
    return MAIN_LAYOUT.format(page_title="Edit Block", content=content)


@app.route('/content/blocks/<block_id>/edit', methods=['POST'])
def update_block(block_id):
    block = _get_block(block_id)
    if not block:
        return MAIN_LAYOUT.format(page_title="Not Found", content='<div class="alert alert-error">Block not found.</div>'), 404

    block_data = _parse_block_form(request.form, block_id)
    _save_block(block_id, block_data)
    return redirect('/content/blocks/{}/edit?saved=1'.format(block_id))


@app.route('/content/blocks/<block_id>/preview')
def preview_block(block_id):
    """
    Render the student-facing preview of the block.
    This generates a static HTML page and uses a headless browser to verify
    interactive behavior (drag-and-drop functionality testing).
    """
    block = _get_block(block_id)
    if not block:
        return MAIN_LAYOUT.format(page_title="Not Found", content='<div class="alert alert-error">Block not found.</div>'), 404

    view_data = _render_student_view_data(block)
    block_data_json = json.dumps(view_data)

    # Build zone HTML (server-side pre-render, JS will re-render dynamically)
    zones_html = ""
    for zone in view_data.get("zones", []):
        zones_html += '<div class="zone" data-zone="{uid}"><p class="zone-title">{title}</p><p class="zone-description">{desc}</p></div>'.format(
            uid=zone.get("uid", ""),
            title=zone.get("title", ""),
            desc=zone.get("description", "")
        )

    items_html = ""
    for item in view_data.get("items", []):
        items_html += '<div class="draggable-item" draggable="true" data-item-id="{id}">{name}</div>'.format(
            id=item.get("id", ""),
            name=item.get("displayName", "")
        )

    page_html = STUDENT_VIEW_TEMPLATE.format(
        block_title=cgi.escape(view_data.get("title", "Activity")),
        block_title_content=view_data.get("title", ""),
        problem_text_content=view_data.get("problem_text", ""),
        zones_content=zones_html,
        items_content=items_html,
        feedback_start=view_data.get("feedback", {}).get("start", ""),
        block_data_json=block_data_json
    )

    # Write to temp file and run headless browser check for interactive testing
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    host = os.getenv('APP_HOST', 'localhost')
    port = os.getenv('APP_PORT', '5000')
    url = 'http://{}:{}/{}'.format(host, port, fn)

    xss_detected = False
    alert_value = None
    try:
        with open(fn, 'w') as of:
            of.write(page_html)

        proc = subprocess.Popen(
            ["timeout", "8", "phantomjs", "check.js"],
            stdout=subprocess.PIPE, stdin=subprocess.PIPE
        )
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
        proc.wait()

        if result and result != 'success':
            alert_value = result
            if result == 'XSS':
                xss_detected = True
    except Exception:
        pass
    finally:
        try:
            os.unlink(fn)
        except OSError:
            pass

    if xss_detected:
        # Reward file read - simulating sensitive data exposure through XSS
        try:
            flag_data = open('secret.txt').read().strip()
        except IOError:
            flag_data = 'Error reading reward data'

        content = """
        <div class="breadcrumb"><a href="/">Dashboard</a> &raquo; <a href="/content/blocks/{bid}/edit">Edit Block</a> &raquo; Preview</div>
        <div class="card">
            <h2>Preview: {block_name}</h2>
            <div class="alert alert-error">
                <strong>Security Alert:</strong> Script execution detected in content preview.
                An inline script was executed during rendering. Leaked data: <code>{flag}</code>
            </div>
        </div>
        """.format(
            bid=block_id,
            block_name=cgi.escape(block.get('display_name', 'Untitled')),
            flag=cgi.escape(flag_data)
        )
    elif alert_value:
        content = """
        <div class="breadcrumb"><a href="/">Dashboard</a> &raquo; <a href="/content/blocks/{bid}/edit">Edit Block</a> &raquo; Preview</div>
        <div class="card">
            <h2>Preview: {block_name}</h2>
            <div class="alert alert-error">
                <strong>Content Warning:</strong> Unexpected script behavior detected during preview rendering.
                Alert value captured: <code>{val}</code>
            </div>
        </div>
        """.format(
            bid=block_id,
            block_name=cgi.escape(block.get('display_name', 'Untitled')),
            val=cgi.escape(alert_value)
        )
    else:
        content = """
        <div class="breadcrumb"><a href="/">Dashboard</a> &raquo; <a href="/content/blocks/{bid}/edit">Edit Block</a> &raquo; Preview</div>
        <div class="card">
            <h2>Preview: {block_name}</h2>
            <p style="color:#666;margin-bottom:16px;">Student view rendering completed. No issues detected.</p>
            <iframe srcdoc='{srcdoc}' style="width:100%;height:600px;border:1px solid #ddd;border-radius:4px;" sandbox="allow-scripts"></iframe>
        </div>
        """.format(
            bid=block_id,
            block_name=cgi.escape(block.get('display_name', 'Untitled')),
            srcdoc=page_html.replace("'", "&#39;").replace('"', "&quot;")
        )

    response = make_response(MAIN_LAYOUT.format(page_title="Preview", content=content))
    response.headers["X-XSS-Protection"] = "0"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@app.route('/api/v2/content/<block_id>/data', methods=['GET'])
def api_block_data(block_id):
    """API endpoint to retrieve block configuration data (student view)."""
    block = _get_block(block_id)
    if not block:
        return jsonify({"error": "Block not found"}), 404
    view_data = _render_student_view_data(block)
    return jsonify(view_data)


@app.route('/api/v2/content/<block_id>/submit', methods=['POST'])
def api_submit_block(block_id):
    """
    API endpoint for submitting block content updates.
    Accepts JSON with block configuration.
    """
    block = _get_block(block_id)
    if not block:
        return jsonify({"error": "Block not found"}), 404

    submissions = request.get_json(force=True)
    if not submissions:
        return jsonify({"error": "Invalid JSON payload"}), 400

    # Update block fields from submission
    if 'display_name' in submissions:
        block['display_name'] = submissions['display_name']
    if 'mode' in submissions:
        block['mode'] = submissions['mode']
    if 'max_attempts' in submissions:
        block['max_attempts'] = submissions['max_attempts']
    if 'show_title' in submissions:
        block['show_title'] = submissions['show_title']
    if 'problem_text' in submissions:
        block['question_text'] = submissions['problem_text']
    if 'show_problem_header' in submissions:
        block['show_problem_header'] = submissions['show_problem_header']
    if 'weight' in submissions:
        try:
            block['weight'] = float(submissions['weight'])
        except (ValueError, TypeError):
            pass
    if 'data' in submissions:
        if 'zones' in submissions['data']:
            block['zones'] = submissions['data']['zones']
        if 'items' in submissions['data']:
            block['items'] = submissions['data']['items']
        if 'feedback' in submissions['data']:
            block['feedback'] = submissions['data']['feedback']

    _save_block(block_id, block)
    return jsonify({"result": "success"})


@app.route('/help')
def help_page():
    content = """
    <h2 style="margin-bottom:16px;">Documentation</h2>
    <div class="card">
        <h3>Interactive Content Block</h3>
        <p style="margin-bottom:12px;">Create drag-and-drop style interactive activities for learners. Each block consists of:</p>
        <ul style="margin-left:20px;margin-bottom:16px;">
            <li><strong>Block Title</strong> - The display name shown to learners</li>
            <li><strong>Problem Text</strong> - Instructions or description for the activity</li>
            <li><strong>Zones</strong> - Target areas where items can be placed. Each zone has a title and description.</li>
            <li><strong>Items</strong> - Draggable elements that learners place into zones</li>
        </ul>
        <h3>API Reference</h3>
        <p style="margin-bottom:8px;">Programmatic access is available via the REST API:</p>
        <table>
            <tr><th>Endpoint</th><th>Method</th><th>Description</th></tr>
            <tr><td><code>/api/v2/content/&lt;block_id&gt;/data</code></td><td>GET</td><td>Retrieve block configuration (student view data)</td></tr>
            <tr><td><code>/api/v2/content/&lt;block_id&gt;/submit</code></td><td>POST</td><td>Update block content (JSON body)</td></tr>
        </table>
        <h3 style="margin-top:16px;">Content Editing</h3>
        <p>Use the web editor or the API to configure block content. Fields support rich text formatting for enhanced presentation. Changes are reflected immediately in the student preview.</p>
    </div>
    """
    return MAIN_LAYOUT.format(page_title="Documentation", content=content)


@app.route('/ping')
def health():
    return 'ok'


def _render_edit_form(block_id, block):
    """Render the block editing form HTML."""
    is_new = block_id is None
    action = '/content/blocks/new' if is_new else '/content/blocks/{}/edit'.format(block_id)
    title = 'Create New Block' if is_new else 'Edit Block: {}'.format(cgi.escape(block.get('display_name', 'Untitled')))

    breadcrumb = '<div class="breadcrumb"><a href="/">Dashboard</a> &raquo; {}</div>'.format(
        'New Block' if is_new else '<a href="/content/blocks/{}/edit">{}</a>'.format(block_id, cgi.escape(block.get('display_name', '')))
    )

    mode = block.get('mode', 'standard')
    zones = block.get('zones', [])
    items = block.get('items', [])

    zones_html = ""
    for i, zone in enumerate(zones):
        zones_html += """
        <div class="zone-card">
            <strong>Zone {idx}</strong>
            <div class="form-group">
                <label>Zone UID</label>
                <input type="text" name="zone_uid_{idx}" value="{uid}">
            </div>
            <div class="form-group">
                <label>Zone Title</label>
                <input type="text" name="zone_title_{idx}" value="{zone_title}">
                <div class="form-help">The title displayed on the zone in the student view.</div>
            </div>
            <div class="form-group">
                <label>Zone Description</label>
                <input type="text" name="zone_desc_{idx}" value="{desc}">
                <div class="form-help">Describe this zone for accessibility.</div>
            </div>
        </div>
        """.format(
            idx=i,
            uid=zone.get('uid', ''),
            zone_title=cgi.escape(zone.get('title', ''), quote=True),
            desc=cgi.escape(zone.get('description', ''), quote=True)
        )

    items_html = ""
    for i, item in enumerate(items):
        items_html += """
        <div class="item-card">
            <strong>Item {idx}</strong>
            <div class="form-group">
                <label>Display Name</label>
                <input type="text" name="item_name_{idx}" value="{name}">
                <div class="form-help">Text shown on the draggable item.</div>
            </div>
            <div class="form-group">
                <label>Image URL (optional)</label>
                <input type="text" name="item_image_{idx}" value="{image}">
            </div>
        </div>
        """.format(
            idx=i,
            name=cgi.escape(item.get('displayName', ''), quote=True),
            image=cgi.escape(item.get('imageURL', ''), quote=True)
        )

    preview_btn = ''
    if not is_new:
        preview_btn = '<a class="btn btn-secondary" href="/content/blocks/{}/preview" style="margin-left:8px;">Preview Student View</a>'.format(block_id)

    return """
    {breadcrumb}
    <div class="card">
        <h2>{title}</h2>
        <form method="post" action="{action}">
            <div class="form-group">
                <label>Block Title (display_name)</label>
                <input type="text" name="display_name" value="{display_name}" required>
                <div class="form-help">The title displayed to learners at the top of the block.</div>
            </div>
            <div class="form-group">
                <label>Mode</label>
                <select name="mode">
                    <option value="standard" {sel_std}>Standard</option>
                    <option value="assessment" {sel_assess}>Assessment</option>
                </select>
            </div>
            <div class="form-group">
                <label>Problem Text (question_text)</label>
                <textarea name="question_text">{question_text}</textarea>
                <div class="form-help">Instructions or description shown to learners. Supports rich text.</div>
            </div>
            <div class="form-group">
                <label>Maximum Attempts</label>
                <input type="number" name="max_attempts" value="{max_attempts}" min="0">
            </div>
            <div class="form-group">
                <label>Weight</label>
                <input type="text" name="weight" value="{weight}">
            </div>

            <input type="hidden" name="zone_count" value="{zone_count}">
            <h3 style="margin: 16px 0 8px;">Zones</h3>
            {zones_html}

            <input type="hidden" name="item_count" value="{item_count}">
            <h3 style="margin: 16px 0 8px;">Items</h3>
            {items_html}

            <div style="margin-top:16px;">
                <button type="submit" class="btn btn-primary">Save Changes</button>
                {preview_btn}
            </div>
        </form>
    </div>
    """.format(
        breadcrumb=breadcrumb,
        title=title,
        action=action,
        display_name=cgi.escape(block.get('display_name', ''), quote=True),
        sel_std='selected' if mode == 'standard' else '',
        sel_assess='selected' if mode == 'assessment' else '',
        question_text=cgi.escape(block.get('question_text', '')),
        max_attempts=block.get('max_attempts', 0) or 0,
        weight=block.get('weight', 1.0),
        zone_count=len(zones),
        zones_html=zones_html,
        item_count=len(items),
        items_html=items_html,
        preview_btn=preview_btn
    )


def _parse_block_form(form, block_id):
    """Parse the edit form submission into a block data dict."""
    block = {
        "block_id": block_id,
        "display_name": form.get("display_name", "Untitled"),
        "mode": form.get("mode", "standard"),
        "question_text": form.get("question_text", ""),
        "max_attempts": None,
        "show_title": True,
        "show_problem_header": True,
        "weight": 1.0,
        "zones": [],
        "items": [],
        "feedback": {
            "start": "Drag the items to their matching zones.",
            "finish": "Activity completed."
        },
        "target_img_url": "",
        "target_img_description": ""
    }

    try:
        block["max_attempts"] = int(form.get("max_attempts", 0))
    except (ValueError, TypeError):
        block["max_attempts"] = None

    try:
        block["weight"] = float(form.get("weight", 1.0))
    except (ValueError, TypeError):
        block["weight"] = 1.0

    zone_count = int(form.get("zone_count", 0))
    for i in range(zone_count):
        zone = {
            "uid": form.get("zone_uid_{}".format(i), "zone-{}".format(i)),
            "title": form.get("zone_title_{}".format(i), ""),
            "description": form.get("zone_desc_{}".format(i), ""),
            "x": 10, "y": 10 + i * 180, "width": 200, "height": 150,
            "align": "center"
        }
        block["zones"].append(zone)

    item_count = int(form.get("item_count", 0))
    for i in range(item_count):
        item = {
            "id": i,
            "displayName": form.get("item_name_{}".format(i), ""),
            "imageURL": form.get("item_image_{}".format(i), ""),
            "imageDescription": "",
            "zones": [],
            "feedback": {"correct": "", "incorrect": ""}
        }
        block["items"].append(item)

    return block


@app.errorhandler(404)
def not_found(e):
    return MAIN_LAYOUT.format(page_title="Not Found", content='<div class="alert alert-error">The requested page was not found.</div>'), 404


@app.errorhandler(500)
def server_error(e):
    return MAIN_LAYOUT.format(page_title="Error", content='<div class="alert alert-error">An internal error occurred.</div>'), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
