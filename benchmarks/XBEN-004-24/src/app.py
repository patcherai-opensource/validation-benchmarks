# encoding=utf8

from flask import Flask, request, Response, make_response, jsonify, abort
import subprocess
import os
import json
import uuid
import sys
import logging

from phantomjs import Phantom

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

# Read flag from build-time planted file
flag_value = ''
try:
    flag_value = open('secret.txt').read().strip()
except:
    pass

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False

phantom = Phantom()

# In-memory store for XBlock configurations (simulates database)
# Pre-populated with a sample drag-and-drop block
xblock_store = {}

SAMPLE_BLOCK_ID = 'block-v1:edX+DemoX+2023+type@drag-and-drop-v2+block@demo'

xblock_store[SAMPLE_BLOCK_ID] = {
    'id': SAMPLE_BLOCK_ID,
    'display_name': 'Drag and Drop Activity',
    'question_text': 'Drag each item to the correct zone on the image below.',
    'show_title': True,
    'max_items_per_zone': 0,
    'mode': 'standard',
    'target_img_expanded_url': '/static/img/target_image.png',
    'target_img_description': 'A diagram showing different regions',
    'zones': [
        {'uid': 'zone-1', 'title': 'Zone A', 'description': 'Top-left area',
         'x': 10, 'y': 10, 'width': 200, 'height': 100},
        {'uid': 'zone-2', 'title': 'Zone B', 'description': 'Top-right area',
         'x': 220, 'y': 10, 'width': 200, 'height': 100},
    ],
    'items': [
        {'id': 0, 'displayName': 'Item 1', 'imageURL': '', 'zones': ['zone-1']},
        {'id': 1, 'displayName': 'Item 2', 'imageURL': '', 'zones': ['zone-2']},
    ],
    'feedback': {
        'start': 'Drag the items onto the matching zones.',
        'finish': 'Great work! You completed the activity.'
    }
}


def generate_student_view_html(block):
    """Generate the student-facing HTML for a drag-and-drop XBlock.
    
    This renders the block configuration into HTML that the LMS would display.
    Fields are rendered directly as they were entered by the course author.
    """
    zones_html = ''
    for zone in block.get('zones', []):
        zones_html += ''.join([
            '\n            <div class="xblock-zone" data-uid="',
            str(zone.get('uid', '')),
            '" style="position:absolute;left:',
            str(zone.get('x', 0)),
            'px;top:',
            str(zone.get('y', 0)),
            'px;width:',
            str(zone.get('width', 200)),
            'px;height:',
            str(zone.get('height', 100)),
            'px;border:2px dashed #ccc;">',
            '\n                <span class="zone-title">',
            zone.get('title', ''),
            '</span>',
            '\n            </div>\n'
        ])

    items_html = ''
    for item in block.get('items', []):
        items_html += ''.join([
            '\n            <div class="xblock-draggable" draggable="true" data-item-id="',
            str(item.get('id', 0)),
            '">',
            '\n                <span class="item-content">',
            item.get('displayName', ''),
            '</span>',
            '\n            </div>\n'
        ])

    feedback = block.get('feedback', {})

    block_json = json.dumps(block)
    block_id = block.get('id', '')

    html = ''.join([
        '<!DOCTYPE html>\n<html>\n<head>\n',
        '    <meta charset="utf-8">\n',
        '    <title>XBlock Student View</title>\n',
        '    <style>\n',
        "        body { font-family: 'Open Sans', sans-serif; margin: 0; padding: 20px; background: #fff; }\n",
        '        .xblock-drag-and-drop {\n',
        '            max-width: 800px; margin: 0 auto;\n',
        '            border: 1px solid #e0e0e0; border-radius: 4px; padding: 20px;\n',
        '        }\n',
        '        .xblock-header { margin-bottom: 16px; }\n',
        '        .xblock-header h2 { color: #333; font-size: 1.2em; margin: 0 0 8px 0; }\n',
        '        .problem-text { color: #555; font-size: 0.95em; margin-bottom: 16px; line-height: 1.5; }\n',
        '        .target-img-container {\n',
        '            position: relative; margin: 20px 0;\n',
        '            background: #f5f5f5; min-height: 250px; border: 1px solid #ddd;\n',
        '        }\n',
        '        .xblock-zone { background: rgba(200, 220, 255, 0.3); }\n',
        '        .zone-title { font-size: 0.85em; color: #666; padding: 4px; }\n',
        '        .items-container { display: flex; flex-wrap: wrap; gap: 8px; margin: 16px 0; }\n',
        '        .xblock-draggable {\n',
        '            background: #e8f0fe; border: 1px solid #4a86c8; border-radius: 4px;\n',
        '            padding: 8px 16px; cursor: grab; user-select: none;\n',
        '        }\n',
        '        .xblock-draggable:hover { background: #d0e0fd; }\n',
        '        .feedback-message { color: #666; font-style: italic; margin-top: 12px; }\n',
        '    </style>\n',
        '</head>\n<body>\n',
        '    <div class="xblock-drag-and-drop" data-block-id="', block_id, '">\n',
        '        <div class="xblock-header">\n',
        '            <h2 id="block-title"></h2>\n',
        '        </div>\n',
        '        <div class="problem-text" id="problem-text"></div>\n',
        '        <div class="target-img-container">\n',
        zones_html,
        '        </div>\n',
        '        <div class="items-container">\n',
        items_html,
        '        </div>\n',
        '        <div class="feedback-message" id="feedback-start"></div>\n',
        '    </div>\n',
        '    <script>\n',
        '        var blockData = ', block_json, ';\n',
        '        document.getElementById("block-title").innerHTML = blockData.display_name;\n',
        '        document.getElementById("problem-text").innerHTML = blockData.question_text;\n',
        '        document.getElementById("feedback-start").innerHTML = blockData.feedback.start;\n',
        '        var zoneTitles = document.querySelectorAll(".zone-title");\n',
        '        for (var i = 0; i < zoneTitles.length; i++) {\n',
        '            if (blockData.zones[i]) {\n',
        '                zoneTitles[i].innerHTML = blockData.zones[i].title;\n',
        '            }\n',
        '        }\n',
        '        var itemContents = document.querySelectorAll(".item-content");\n',
        '        for (var j = 0; j < itemContents.length; j++) {\n',
        '            if (blockData.items[j]) {\n',
        '                itemContents[j].innerHTML = blockData.items[j].displayName;\n',
        '            }\n',
        '        }\n',
        '    </script>\n',
        '</body>\n</html>'
    ])
    return html


@app.route('/')
def index():
    """Course outline - list available XBlocks"""
    blocks = []
    for bid, block in xblock_store.items():
        blocks.append({
            'id': bid,
            'display_name': block.get('display_name', 'Untitled'),
            'type': 'drag-and-drop-v2'
        })
    
    blocks_html = ''
    for b in blocks:
        blocks_html += '''
            <tr>
                <td><a href="/xblock/{id}/student_view">{name}</a></td>
                <td>{type}</td>
                <td>
                    <a href="/xblock/{id}/student_view" class="btn btn-view">Student View</a>
                    <a href="/xblock/{id}/studio_view" class="btn btn-edit">Edit</a>
                </td>
            </tr>
        '''.format(id=b['id'], name=b['display_name'], type=b['type'])

    return '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Open edX Studio - Course Blocks</title>
    <style>
        body {{ font-family: 'Open Sans', sans-serif; margin: 0; background: #f5f5f5; }}
        .studio-header {{
            background: #00262b; color: white; padding: 12px 24px;
            display: flex; align-items: center; justify-content: space-between;
        }}
        .studio-header h1 {{ font-size: 1.1em; font-weight: 400; }}
        .studio-header .nav-links a {{ color: #00bbff; text-decoration: none; margin-left: 20px; font-size: 0.9em; }}
        .content {{ max-width: 960px; margin: 30px auto; padding: 0 20px; }}
        .panel {{ background: white; border: 1px solid #ddd; border-radius: 4px; padding: 20px; margin-bottom: 20px; }}
        .panel h2 {{ color: #333; font-size: 1.1em; margin: 0 0 16px 0; border-bottom: 1px solid #eee; padding-bottom: 10px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th {{ text-align: left; padding: 10px; color: #666; font-size: 0.85em; text-transform: uppercase; border-bottom: 2px solid #eee; }}
        td {{ padding: 12px 10px; border-bottom: 1px solid #f0f0f0; color: #333; font-size: 0.95em; }}
        td a {{ color: #0075b4; text-decoration: none; }}
        .btn {{ display: inline-block; padding: 4px 12px; border-radius: 3px; font-size: 0.85em; text-decoration: none; margin-right: 4px; }}
        .btn-view {{ background: #0075b4; color: white; }}
        .btn-edit {{ background: #00838f; color: white; }}
        .btn-view:hover {{ background: #005d8f; }}
        .btn-edit:hover {{ background: #006b75; }}
        .btn-create {{ background: #00838f; color: white; padding: 8px 16px; border: none; cursor: pointer; border-radius: 3px; font-size: 0.9em; }}
        .create-section {{ margin-bottom: 20px; text-align: right; }}
    </style>
</head>
<body>
    <div class="studio-header">
        <h1>Studio - DemoX Course</h1>
        <div class="nav-links">
            <a href="/">Course Outline</a>
            <a href="/api/xblocks">API</a>
        </div>
    </div>
    <div class="content">
        <div class="create-section">
            <a href="/xblock/new" class="btn btn-create">+ New Component</a>
        </div>
        <div class="panel">
            <h2>Course Components</h2>
            <table>
                <thead>
                    <tr>
                        <th>Display Name</th>
                        <th>Type</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {blocks}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>'''.format(blocks=blocks_html)


@app.route('/xblock/new', methods=['GET'])
def new_xblock():
    """Create a new drag-and-drop XBlock - Studio interface"""
    return render_studio_form(None)


@app.route('/xblock/<path:block_id>/studio_view', methods=['GET'])
def studio_view(block_id):
    """Edit an existing XBlock - Studio interface"""
    block = xblock_store.get(block_id)
    if not block:
        abort(404)
    return render_studio_form(block)


def render_studio_form(block):
    """Render the Studio editing form for a drag-and-drop XBlock"""
    is_new = block is None
    if is_new:
        block = {
            'display_name': '',
            'question_text': '',
            'show_title': True,
            'max_items_per_zone': 0,
            'mode': 'standard',
            'target_img_expanded_url': '',
            'target_img_description': '',
            'zones': [{'uid': 'zone-1', 'title': '', 'description': '', 'x': 10, 'y': 10, 'width': 200, 'height': 100}],
            'items': [{'id': 0, 'displayName': '', 'imageURL': '', 'zones': ['zone-1']}],
            'feedback': {'start': '', 'finish': ''}
        }
    
    block_id = block.get('id', '')
    action_url = '/api/xblock/{}/studio_submit'.format(block_id) if not is_new else '/api/xblock/studio_submit'

    zones_fields = ''
    for i, zone in enumerate(block.get('zones', [])):
        zones_fields += '''
            <div class="field-group zone-group">
                <h4>Zone {idx}</h4>
                <label>Title <span class="field-hint">(supports rich text)</span></label>
                <input type="text" name="zone_title_{i}" value="{title}" class="input-field">
                <label>Description</label>
                <input type="text" name="zone_desc_{i}" value="{desc}" class="input-field">
            </div>
        '''.format(i=i, idx=i+1, title=zone.get('title', ''), desc=zone.get('description', ''))

    items_fields = ''
    for i, item in enumerate(block.get('items', [])):
        items_fields += '''
            <div class="field-group item-group">
                <h4>Item {idx}</h4>
                <label>Display Name <span class="field-hint">(supports rich text)</span></label>
                <input type="text" name="item_name_{i}" value="{name}" class="input-field">
                <label>Zone</label>
                <input type="text" name="item_zone_{i}" value="{zone}" class="input-field">
            </div>
        '''.format(i=i, idx=i+1, name=item.get('displayName', ''),
                   zone=','.join(item.get('zones', [])))

    return '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Studio - Edit XBlock</title>
    <style>
        body {{ font-family: 'Open Sans', sans-serif; margin: 0; background: #f5f5f5; }}
        .studio-header {{
            background: #00262b; color: white; padding: 12px 24px;
            display: flex; align-items: center; justify-content: space-between;
        }}
        .studio-header h1 {{ font-size: 1.1em; font-weight: 400; }}
        .studio-header .nav-links a {{ color: #00bbff; text-decoration: none; margin-left: 20px; font-size: 0.9em; }}
        .content {{ max-width: 720px; margin: 30px auto; padding: 0 20px; }}
        .panel {{ background: white; border: 1px solid #ddd; border-radius: 4px; padding: 24px; margin-bottom: 20px; }}
        .panel h2 {{ color: #333; font-size: 1.1em; margin: 0 0 20px 0; border-bottom: 1px solid #eee; padding-bottom: 10px; }}
        .field-group {{ margin-bottom: 16px; }}
        .field-group label {{ display: block; color: #555; font-size: 0.85em; margin-bottom: 4px; }}
        .field-hint {{ color: #999; font-size: 0.85em; }}
        .input-field {{ width: 100%; padding: 8px 10px; border: 1px solid #ccc; border-radius: 3px; font-size: 0.95em; box-sizing: border-box; }}
        .input-field:focus {{ border-color: #0075b4; outline: none; }}
        textarea.input-field {{ min-height: 80px; resize: vertical; }}
        h3 {{ color: #444; font-size: 1em; margin: 20px 0 12px 0; }}
        h4 {{ color: #555; font-size: 0.9em; margin: 8px 0; }}
        .zone-group, .item-group {{ background: #fafafa; padding: 12px; border: 1px solid #eee; border-radius: 3px; margin-bottom: 8px; }}
        .btn-row {{ display: flex; gap: 10px; margin-top: 20px; }}
        .btn {{ padding: 8px 20px; border: none; border-radius: 3px; cursor: pointer; font-size: 0.9em; }}
        .btn-save {{ background: #0075b4; color: white; }}
        .btn-save:hover {{ background: #005d8f; }}
        .btn-cancel {{ background: #eee; color: #333; }}
        .btn-preview {{ background: #00838f; color: white; }}
        .btn-preview:hover {{ background: #006b75; }}
        .result-box {{ margin-top: 16px; padding: 12px; border-radius: 4px; display: none; }}
        .result-success {{ background: #e8f5e9; border: 1px solid #a5d6a7; color: #2e7d32; }}
        .result-error {{ background: #fbe9e7; border: 1px solid #ef9a9a; color: #c62828; }}
        .result-info {{ background: #e3f2fd; border: 1px solid #90caf9; color: #1565c0; }}
    </style>
</head>
<body>
    <div class="studio-header">
        <h1>Studio - Edit Component</h1>
        <div class="nav-links">
            <a href="/">Course Outline</a>
        </div>
    </div>
    <div class="content">
        <div class="panel">
            <h2>{form_title}</h2>
            <form id="studio-form" method="post" action="{action_url}">
                <div class="field-group">
                    <label>Problem Title / Display Name <span class="field-hint">(supports rich text)</span></label>
                    <input type="text" name="display_name" value="{display_name}" class="input-field" placeholder="e.g. Drag and Drop Activity">
                </div>
                <div class="field-group">
                    <label>Question Text / Instructions <span class="field-hint">(supports rich text / HTML)</span></label>
                    <textarea name="question_text" class="input-field" placeholder="Enter the instructions students will see...">{question_text}</textarea>
                </div>
                <div class="field-group">
                    <label>Mode</label>
                    <select name="mode" class="input-field">
                        <option value="standard" {mode_standard}>Standard</option>
                        <option value="assessment" {mode_assessment}>Assessment</option>
                    </select>
                </div>

                <h3>Drop Zones</h3>
                {zones_fields}
                
                <h3>Draggable Items</h3>
                {items_fields}

                <h3>Feedback Messages</h3>
                <div class="field-group">
                    <label>Introductory Feedback <span class="field-hint">(supports rich text)</span></label>
                    <input type="text" name="feedback_start" value="{feedback_start}" class="input-field">
                </div>
                <div class="field-group">
                    <label>Final Feedback <span class="field-hint">(supports rich text)</span></label>
                    <input type="text" name="feedback_finish" value="{feedback_finish}" class="input-field">
                </div>

                <div class="btn-row">
                    <button type="submit" class="btn btn-save">Save</button>
                    <button type="button" class="btn btn-preview" onclick="previewBlock()">Preview Student View</button>
                    <a href="/" class="btn btn-cancel">Cancel</a>
                </div>
            </form>
            <div id="result-box" class="result-box"></div>
        </div>
    </div>
    <script>
        document.getElementById('studio-form').addEventListener('submit', function(e) {{
            e.preventDefault();
            var formData = new FormData(this);
            var data = {{}};
            formData.forEach(function(value, key) {{ data[key] = value; }});
            
            fetch(this.action, {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify(data)
            }})
            .then(function(r) {{ return r.json(); }})
            .then(function(result) {{
                var box = document.getElementById('result-box');
                if (result.success) {{
                    box.className = 'result-box result-success';
                    box.style.display = 'block';
                    box.innerHTML = 'Block saved successfully. <a href="/xblock/' + result.block_id + '/student_view">View student preview</a>';
                    // Update form action for future saves
                    document.getElementById('studio-form').action = '/api/xblock/' + result.block_id + '/studio_submit';
                }} else {{
                    box.className = 'result-box result-error';
                    box.style.display = 'block';
                    box.textContent = result.error || 'Failed to save block.';
                }}
            }})
            .catch(function(err) {{
                var box = document.getElementById('result-box');
                box.className = 'result-box result-error';
                box.style.display = 'block';
                box.textContent = 'Error: ' + err.message;
            }});
        }});

        function previewBlock() {{
            var form = document.getElementById('studio-form');
            var formData = new FormData(form);
            var data = {{}};
            formData.forEach(function(value, key) {{ data[key] = value; }});
            
            fetch(form.action, {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify(data)
            }})
            .then(function(r) {{ return r.json(); }})
            .then(function(result) {{
                if (result.success && result.block_id) {{
                    window.open('/xblock/' + result.block_id + '/student_view', '_blank');
                }}
            }});
        }}
    </script>
</body>
</html>'''.format(
        form_title='New Drag and Drop Component' if is_new else 'Edit: ' + block.get('display_name', ''),
        action_url=action_url,
        display_name=block.get('display_name', ''),
        question_text=block.get('question_text', ''),
        mode_standard='selected' if block.get('mode') == 'standard' else '',
        mode_assessment='selected' if block.get('mode') == 'assessment' else '',
        zones_fields=zones_fields,
        items_fields=items_fields,
        feedback_start=block.get('feedback', {}).get('start', ''),
        feedback_finish=block.get('feedback', {}).get('finish', ''),
    )


@app.route('/api/xblock/studio_submit', methods=['POST'])
def create_xblock():
    """Create a new XBlock from Studio form submission"""
    block_id = 'block-v1:edX+DemoX+2023+type@drag-and-drop-v2+block@' + uuid.uuid4().hex[:12]
    return save_xblock_data(block_id, request)


@app.route('/api/xblock/<path:block_id>/studio_submit', methods=['POST'])
def update_xblock(block_id):
    """Update an existing XBlock from Studio form submission"""
    return save_xblock_data(block_id, request)


def save_xblock_data(block_id, req):
    """Process and store XBlock configuration data.
    
    Accepts both JSON and form data from the Studio editor.
    Fields support rich text (HTML) for display purposes.
    """
    if req.is_json:
        data = req.get_json()
    else:
        data = req.form.to_dict()

    # Build the block configuration from submitted data
    zones = []
    items = []
    
    # Parse zones from form fields
    i = 0
    while True:
        title_key = 'zone_title_{}'.format(i)
        if title_key not in data:
            break
        zones.append({
            'uid': 'zone-{}'.format(i + 1),
            'title': data.get(title_key, ''),
            'description': data.get('zone_desc_{}'.format(i), ''),
            'x': 10 + (i * 210),
            'y': 10,
            'width': 200,
            'height': 100
        })
        i += 1

    # Parse items from form fields  
    i = 0
    while True:
        name_key = 'item_name_{}'.format(i)
        if name_key not in data:
            break
        items.append({
            'id': i,
            'displayName': data.get(name_key, ''),
            'imageURL': '',
            'zones': [z.strip() for z in data.get('item_zone_{}'.format(i), '').split(',') if z.strip()]
        })
        i += 1

    # If no zones/items were parsed from indexed fields, keep defaults
    if not zones:
        zones = [{'uid': 'zone-1', 'title': 'Zone A', 'description': '', 'x': 10, 'y': 10, 'width': 200, 'height': 100}]
    if not items:
        items = [{'id': 0, 'displayName': 'Item 1', 'imageURL': '', 'zones': ['zone-1']}]

    block = {
        'id': block_id,
        'display_name': data.get('display_name', 'Untitled Block'),
        'question_text': data.get('question_text', ''),
        'show_title': True,
        'max_items_per_zone': 0,
        'mode': data.get('mode', 'standard'),
        'target_img_expanded_url': '/static/img/target_image.png',
        'target_img_description': 'Target image for drag and drop activity',
        'zones': zones,
        'items': items,
        'feedback': {
            'start': data.get('feedback_start', ''),
            'finish': data.get('feedback_finish', '')
        }
    }

    xblock_store[block_id] = block
    
    return jsonify({'success': True, 'block_id': block_id})


@app.route('/api/xblocks', methods=['GET'])
def list_xblocks():
    """API endpoint to list all XBlocks"""
    blocks = []
    for bid, block in xblock_store.items():
        blocks.append({
            'id': bid,
            'display_name': block.get('display_name', ''),
            'type': 'drag-and-drop-v2',
            'student_view_url': '/xblock/{}/student_view'.format(bid)
        })
    return jsonify({'blocks': blocks})


@app.route('/api/xblock/<path:block_id>/student_view_data', methods=['GET'])
def student_view_data(block_id):
    """API endpoint returning the student view data for an XBlock.
    
    This is the data that gets rendered in the LMS student view.
    Returns the block configuration as JSON for client-side rendering.
    """
    block = xblock_store.get(block_id)
    if not block:
        return jsonify({'error': 'Block not found'}), 404
    return jsonify(block)


@app.route('/xblock/<path:block_id>/student_view', methods=['GET'])
def student_view(block_id):
    """Render the student view for an XBlock.
    
    This generates the HTML that students see in the LMS.
    Content is rendered client-side using the block's configuration data.
    """
    block = xblock_store.get(block_id)
    if not block:
        abort(404)
    return generate_student_view_html(block)


@app.route('/xblock/<path:block_id>/check_preview', methods=['POST'])
def check_preview(block_id):
    """Server-side preview check for XBlock content.
    
    Renders the student view in a headless browser to verify content
    displays correctly. Used by the Studio preview feature.
    """
    block = xblock_store.get(block_id)
    if not block:
        return jsonify({'error': 'Block not found'}), 404

    # Generate the student view HTML
    page_html = generate_student_view_html(block)
    
    # Render in headless browser for preview verification
    fn = 'static/' + os.urandom(16).encode('hex') + '.html'
    host = os.getenv('APP_HOST', 'localhost')
    port = os.getenv('APP_PORT', '5000')
    url = 'http://{}:{}/{}'.format(host, port, fn)
    
    result = ''
    try:
        of = open(fn, 'w')
        of.write(page_html)
        of.close()
        
        proc = subprocess.Popen(
            ['timeout', '5', 'phantomjs', 'check.js'],
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE
        )
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
    except Exception as e:
        logging.error('Preview check failed: %s', str(e))
    finally:
        try:
            os.unlink(fn)
        except:
            pass

    if result == 'XSS':
        # XSS detected in preview - this indicates a content security issue
        # Log the security event and return the diagnostic information
        return jsonify({
            'preview_status': 'security_warning',
            'message': 'Content security check detected potential issues.',
            'diagnostic_token': flag_value
        })
    elif result:
        return jsonify({
            'preview_status': 'warning',
            'message': 'Preview rendered with unexpected behavior: {}'.format(result)
        })
    else:
        return jsonify({
            'preview_status': 'ok',
            'message': 'Preview rendered successfully.'
        })


@app.route('/ping')
def health_check():
    return 'OK', 200


@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
