# Constants for OpenEdX XBlock Drag-and-Drop v2 Demo
# Simulating CVE-2022-46147 - Stored XSS vulnerability

INDEX_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <link rel="stylesheet" type="text/css" href="static/css/style.css">
    <title>OpenEdX XBlock Drag-and-Drop Demo</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f5f5f5; margin: 0; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #0075b4; }
        .nav-links { margin: 20px 0; }
        .nav-links a { display: inline-block; padding: 10px 20px; margin: 5px; background: #0075b4; color: white; text-decoration: none; border-radius: 4px; }
        .nav-links a:hover { background: #005a8c; }
        .info-box { background: #e8f4f8; padding: 15px; border-radius: 4px; margin: 20px 0; border-left: 4px solid #0075b4; }
        code { background: #f0f0f0; padding: 2px 6px; border-radius: 3px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>OpenEdX XBlock Drag-and-Drop v2 Demo</h1>
        <p>This application demonstrates the XBlock Drag-and-Drop v2 module functionality.</p>
        
        <div class="info-box">
            <strong>Course Authors:</strong> Create interactive drag-and-drop problems for your courses.<br>
            <strong>Students:</strong> View and interact with published XBlocks.
        </div>
        
        <div class="nav-links">
            <a href="/api/v1/xblock/studio">Studio (Author Interface)</a>
            <a href="/xblock/quick">Quick Test</a>
            <a href="/api/v1/xblock/list">View All XBlocks</a>
        </div>
        
        <h3>API Endpoints:</h3>
        <ul>
            <li><code>POST /api/v1/xblock/create</code> - Create a new XBlock (JSON body)</li>
            <li><code>GET /api/v1/xblock/list</code> - List all XBlocks</li>
            <li><code>GET /xblock/view/&lt;block_id&gt;</code> - View an XBlock (student view)</li>
            <li><code>GET /xblock/quick?display_name=...</code> - Quick test endpoint</li>
        </ul>
    </div>
</body>
</html>
"""

STUDIO_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <title>Studio - Create XBlock</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f5f5f5; margin: 0; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #0075b4; }
        .form-group { margin: 15px 0; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input[type="text"], textarea { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        textarea { height: 100px; resize: vertical; }
        button { padding: 12px 24px; background: #0075b4; color: white; border: none; border-radius: 4px; cursor: pointer; margin-top: 10px; }
        button:hover { background: #005a8c; }
        .info-box { background: #fff3cd; padding: 15px; border-radius: 4px; margin: 20px 0; border-left: 4px solid #ffc107; }
        .response { margin-top: 20px; padding: 15px; border-radius: 4px; display: none; }
        .response.success { background: #d4edda; border: 1px solid #c3e6cb; }
        .response.error { background: #f8d7da; border: 1px solid #f5c6cb; }
        pre { background: #f0f0f0; padding: 10px; border-radius: 4px; overflow-x: auto; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Studio - Create XBlock</h1>
        <p>As a course author, you can create drag-and-drop XBlock problems here.</p>
        
        <div class="info-box">
            <strong>Note:</strong> All fields support rich HTML content for formatting.
        </div>
        
        <form id="xblock-form">
            <div class="form-group">
                <label for="display_name">Display Name (Problem Title):</label>
                <input type="text" id="display_name" name="display_name" placeholder="Enter the problem title...">
            </div>
            
            <div class="form-group">
                <label for="question_text">Question Text (Instructions):</label>
                <textarea id="question_text" name="question_text" placeholder="Enter instructions for students..."></textarea>
            </div>
            
            <button type="submit">Create XBlock</button>
        </form>
        
        <div id="response" class="response"></div>
        
        <h3>Example API Usage:</h3>
        <pre>
curl -X POST http://localhost:5000/api/v1/xblock/create \\
  -H "Content-Type: application/json" \\
  -d '{"display_name": "My Problem", "question_text": "Drag items to zones"}'
        </pre>
    </div>
    
    <script>
        document.getElementById('xblock-form').addEventListener('submit', function(e) {
            e.preventDefault();
            var data = {
                display_name: document.getElementById('display_name').value,
                question_text: document.getElementById('question_text').value
            };
            
            fetch('/api/v1/xblock/create', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                var responseDiv = document.getElementById('response');
                responseDiv.style.display = 'block';
                if (result.success) {
                    responseDiv.className = 'response success';
                    responseDiv.innerHTML = '<strong>Success!</strong><br>' + result.message + 
                        '<br><br><a href="' + '/xblock/view/' + result.block_id + '">View XBlock (Student View)</a>';
                } else {
                    responseDiv.className = 'response error';
                    responseDiv.innerHTML = '<strong>Error:</strong> ' + (result.error || 'Unknown error');
                }
            })
            .catch(error => {
                var responseDiv = document.getElementById('response');
                responseDiv.style.display = 'block';
                responseDiv.className = 'response error';
                responseDiv.innerHTML = '<strong>Error:</strong> ' + error.message;
            });
        });
    </script>
</body>
</html>
"""

QUICK_TEST_FORM = """
<!DOCTYPE html>
<html>
<head>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <title>Quick Test - XBlock</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f5f5f5; margin: 0; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #0075b4; }
        .form-group { margin: 15px 0; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input[type="text"], textarea { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        textarea { height: 100px; }
        button { padding: 12px 24px; background: #0075b4; color: white; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #005a8c; }
        .info-box { background: #e8f4f8; padding: 15px; border-radius: 4px; margin: 20px 0; border-left: 4px solid #0075b4; }
        code { background: #f0f0f0; padding: 2px 6px; border-radius: 3px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Quick Test - XBlock Preview</h1>
        <p>Quickly create and preview an XBlock. Enter content below to see how it renders.</p>
        
        <form method="POST" action="/xblock/quick">
            <div class="form-group">
                <label for="display_name">Display Name:</label>
                <input type="text" id="display_name" name="display_name" placeholder="Problem title...">
            </div>
            
            <div class="form-group">
                <label for="question_text">Question Text:</label>
                <textarea id="question_text" name="question_text" placeholder="Instructions for students..."></textarea>
            </div>
            
            <button type="submit">Preview XBlock</button>
        </form>
        
        <div class="info-box">
            <strong>Quick URL Test:</strong><br>
            <code>/xblock/quick?display_name=Your+Title&question_text=Your+Instructions</code>
        </div>
    </div>
</body>
</html>
"""

# Student view template - This is where the XSS vulnerability manifests
# The display_name and question_text are rendered via innerHTML without sanitization
# This directly mirrors CVE-2022-46147's vulnerable code pattern
XBLOCK_STUDENT_VIEW = """
<!DOCTYPE html>
<html>
<head>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <title>XBlock - Student View</title>
    <style>
        body {{ font-family: Arial, sans-serif; background: #f5f5f5; margin: 0; padding: 20px; }}
        .xblock-container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .xblock-header {{ border-bottom: 2px solid #0075b4; padding-bottom: 15px; margin-bottom: 20px; }}
        .xblock-title {{ color: #0075b4; margin: 0; }}
        .xblock-question {{ background: #f8f9fa; padding: 20px; border-radius: 4px; margin: 20px 0; }}
        .drag-drop-area {{ display: flex; gap: 20px; margin-top: 20px; }}
        .zones-container, .items-container {{ flex: 1; }}
        .zone {{ border: 2px dashed #ccc; padding: 20px; margin: 10px 0; border-radius: 4px; min-height: 100px; }}
        .item {{ background: #0075b4; color: white; padding: 10px; margin: 5px 0; border-radius: 4px; cursor: move; }}
    </style>
</head>
<body>
    <div class="xblock-container">
        <div class="xblock-header">
            <!-- VULNERABILITY: display_name rendered via innerHTML without sanitization -->
            <h1 class="xblock-title" id="problem-title"></h1>
        </div>
        
        <div class="xblock-question">
            <!-- VULNERABILITY: question_text rendered via innerHTML without sanitization -->
            <div id="question-text"></div>
        </div>
        
        <div class="drag-drop-area">
            <div class="zones-container">
                <h3>Drop Zones</h3>
                <div id="zones"></div>
            </div>
            <div class="items-container">
                <h3>Draggable Items</h3>
                <div id="items"></div>
            </div>
        </div>
    </div>
    
    <script>
        // Simulating the vulnerable rendering from drag_and_drop.js
        // CVE-2022-46147: innerHTML assignment without sanitization
        
        var ctx = {{
            title_html: {display_name!r},
            problem_html: {question_text!r},
            zones: {zones_json},
            items: {items_json}
        }};
        
        // VULNERABILITY SINK: Direct innerHTML assignment (mirrors CVE)
        document.getElementById('problem-title').innerHTML = ctx.title_html;
        document.getElementById('question-text').innerHTML = ctx.problem_html;
        
        // Render zones (also vulnerable)
        var zonesContainer = document.getElementById('zones');
        ctx.zones.forEach(function(zone) {{
            var zoneDiv = document.createElement('div');
            zoneDiv.className = 'zone';
            // VULNERABILITY: Zone title rendered via innerHTML
            zoneDiv.innerHTML = '<strong>' + (zone.title || 'Zone') + '</strong>';
            zonesContainer.appendChild(zoneDiv);
        }});
        
        // Render items (also vulnerable)
        var itemsContainer = document.getElementById('items');
        ctx.items.forEach(function(item) {{
            var itemDiv = document.createElement('div');
            itemDiv.className = 'item';
            itemDiv.draggable = true;
            // VULNERABILITY: Item displayName rendered via innerHTML
            itemDiv.innerHTML = item.displayName || 'Item';
            itemsContainer.appendChild(itemDiv);
        }});
        
        // Add default content if empty
        if (ctx.zones.length === 0) {{
            document.getElementById('zones').innerHTML = '<div class="zone"><strong>Default Zone</strong></div>';
        }}
        if (ctx.items.length === 0) {{
            document.getElementById('items').innerHTML = '<div class="item">Sample Item</div>';
        }}
    </script>
</body>
</html>
"""

XBLOCK_STUDENT_VIEW_WITH_FEEDBACK = """
<!DOCTYPE html>
<html>
<head>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <title>XBlock - Student View</title>
    <style>
        body {{ font-family: Arial, sans-serif; background: #f5f5f5; margin: 0; padding: 20px; }}
        .xblock-container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .xblock-header {{ border-bottom: 2px solid #0075b4; padding-bottom: 15px; margin-bottom: 20px; }}
        .xblock-title {{ color: #0075b4; margin: 0; }}
        .xblock-question {{ background: #f8f9fa; padding: 20px; border-radius: 4px; margin: 20px 0; }}
        .drag-drop-area {{ display: flex; gap: 20px; margin-top: 20px; }}
        .zones-container, .items-container {{ flex: 1; }}
        .zone {{ border: 2px dashed #ccc; padding: 20px; margin: 10px 0; border-radius: 4px; min-height: 100px; }}
        .item {{ background: #0075b4; color: white; padding: 10px; margin: 5px 0; border-radius: 4px; cursor: move; }}
        .feedback {{ padding: 15px; border-radius: 4px; margin: 20px 0; }}
        .feedback.error {{ background: #fff3cd; border: 1px solid #ffc107; }}
    </style>
</head>
<body>
    <div class="xblock-container">
        {feedback}
        <div class="xblock-header">
            <h1 class="xblock-title" id="problem-title"></h1>
        </div>
        
        <div class="xblock-question">
            <div id="question-text"></div>
        </div>
        
        <div class="drag-drop-area">
            <div class="zones-container">
                <h3>Drop Zones</h3>
                <div id="zones"></div>
            </div>
            <div class="items-container">
                <h3>Draggable Items</h3>
                <div id="items"></div>
            </div>
        </div>
    </div>
    
    <script>
        var ctx = {{
            title_html: {display_name!r},
            problem_html: {question_text!r},
            zones: {zones_json},
            items: {items_json}
        }};
        
        document.getElementById('problem-title').innerHTML = ctx.title_html;
        document.getElementById('question-text').innerHTML = ctx.problem_html;
        
        var zonesContainer = document.getElementById('zones');
        ctx.zones.forEach(function(zone) {{
            var zoneDiv = document.createElement('div');
            zoneDiv.className = 'zone';
            zoneDiv.innerHTML = '<strong>' + (zone.title || 'Zone') + '</strong>';
            zonesContainer.appendChild(zoneDiv);
        }});
        
        var itemsContainer = document.getElementById('items');
        ctx.items.forEach(function(item) {{
            var itemDiv = document.createElement('div');
            itemDiv.className = 'item';
            itemDiv.draggable = true;
            itemDiv.innerHTML = item.displayName || 'Item';
            itemsContainer.appendChild(itemDiv);
        }});
        
        if (ctx.zones.length === 0) {{
            document.getElementById('zones').innerHTML = '<div class="zone"><strong>Default Zone</strong></div>';
        }}
        if (ctx.items.length === 0) {{
            document.getElementById('items').innerHTML = '<div class="item">Sample Item</div>';
        }}
    </script>
</body>
</html>
"""

XBLOCK_SUCCESS_VIEW = """
<!DOCTYPE html>
<html>
<head>
    <link rel="shortcut icon" href="static/assets/fav-icon.png">
    <title>XBlock - Success!</title>
    <style>
        body {{ font-family: Arial, sans-serif; background: #f5f5f5; margin: 0; padding: 20px; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #28a745; }}
        .flag-box {{ background: #d4edda; padding: 20px; border-radius: 4px; margin: 20px 0; border: 2px solid #28a745; font-family: monospace; font-size: 18px; }}
        .info {{ background: #e8f4f8; padding: 15px; border-radius: 4px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Congratulations! XSS Vulnerability Exploited!</h1>
        
        <div class="info">
            <p>You have successfully demonstrated the stored XSS vulnerability (CVE-2022-46147).</p>
            <p>The malicious content in the XBlock's display_name or question_text field was rendered via innerHTML without sanitization, allowing JavaScript execution.</p>
        </div>
        
        <div class="flag-box">
            <strong>FLAG:</strong> {flag}
        </div>
        
        <p><a href="/">Return to Home</a></p>
    </div>
</body>
</html>
"""

# Keep legacy constants for compatibility
IMAGE_ROUTES = {
    "xss_easy": {
        "start": "static/img/cookies/new_circle.png",
        "process": "static/img/cookies/error_circle.png",
        "error": "static/img/cookies/error_circle.png",
        "success": "static/img/cookies/success_circle.png"
    },
    "xss_easy_med": {
        "start": "static/img/cookies/new_triangle.png",
        "process": "static/img/cookies/error_triangle.png",
        "error": "static/img/cookies/error_triangle.png",
        "success": "static/img/cookies/success_triangle.png"
    },
    "xss_medium": {
        "start": "static/img/cookies/new_star.png",
        "process": "static/img/cookies/error_star.png",
        "error": "static/img/cookies/error_star.png",
        "success": "static/img/cookies/success_star.png"
    },
    "xss_hard": {
        "start": "static/img/cookies/new_umbrella.png",
        "process": "static/img/cookies/error_umbrella.png",
        "error": "static/img/cookies/error_umbrella.png",
        "success": "static/img/cookies/success_umbrella.png"
    }
}
