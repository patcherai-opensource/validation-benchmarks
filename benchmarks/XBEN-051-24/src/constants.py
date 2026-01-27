# OpenLearn Course Builder - HTML Templates
# Drag & Drop XBlock Editor

INDEX_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenLearn - Course Builder</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        .container {
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
            max-width: 600px;
            width: 90%;
        }
        .logo { text-align: center; margin-bottom: 30px; }
        .logo h1 { color: #1e3c72; font-size: 2.5em; }
        .logo p { color: #666; margin-top: 10px; }
        .nav-links { display: flex; flex-direction: column; gap: 15px; }
        .nav-link {
            display: block;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 8px;
            text-align: center;
            font-weight: bold;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .nav-link:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        }
        .nav-link .icon { font-size: 1.5em; margin-right: 10px; }
        .footer { margin-top: 30px; text-align: center; color: #999; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            <h1>&#128218; OpenLearn</h1>
            <p>Interactive Course Builder Platform</p>
        </div>
        <div class="nav-links">
            <a href="/studio" class="nav-link">
                <span class="icon">&#128640;</span>
                Studio Dashboard
            </a>
            <a href="/xblock/edit" class="nav-link">
                <span class="icon">&#127922;</span>
                Create Drag & Drop Block
            </a>
            <a href="/api/blocks" class="nav-link">
                <span class="icon">&#128196;</span>
                View Block API
            </a>
        </div>
        <div class="footer">
            <p>OpenLearn Course Builder v2.1.0</p>
            <p>Build interactive learning experiences</p>
        </div>
    </div>
</body>
</html>
"""

STUDIO_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenLearn Studio - Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f5f5;
        }
        .header {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 20px 40px;
        }
        .header h1 { font-size: 1.8em; }
        .main { padding: 40px; max-width: 1200px; margin: 0 auto; }
        .card-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .card {
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 25px;
        }
        .card h3 { color: #1e3c72; margin-bottom: 15px; }
        .card p { color: #666; line-height: 1.6; }
        .card a {
            display: inline-block;
            margin-top: 15px;
            color: #667eea;
            text-decoration: none;
            font-weight: bold;
        }
        .card a:hover { text-decoration: underline; }
        .info-box {
            background: #e8f4fd;
            border-left: 4px solid #1e3c72;
            padding: 15px;
            margin-top: 30px;
            border-radius: 0 8px 8px 0;
        }
        .info-box h4 { color: #1e3c72; margin-bottom: 10px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>&#128218; OpenLearn Studio</h1>
    </div>
    <div class="main">
        <div class="card-grid">
            <div class="card">
                <h3>&#127922; Drag & Drop XBlock</h3>
                <p>Create interactive drag-and-drop exercises for your courses. Students can drag items to designated zones.</p>
                <a href="/xblock/edit">Create New Block &rarr;</a>
            </div>
            <div class="card">
                <h3>&#128196; Content Library</h3>
                <p>Browse and manage your created XBlocks. View block IDs and content via the API.</p>
                <a href="/api/blocks">View API &rarr;</a>
            </div>
            <div class="card">
                <h3>&#9881; Block Settings</h3>
                <p>Configure display names, question text, and zone titles for your interactive blocks.</p>
                <a href="/xblock/edit">Configure &rarr;</a>
            </div>
        </div>
        <div class="info-box">
            <h4>&#128161; Quick Tips</h4>
            <p>The XBlock editor allows you to set custom display names, question text, and zone titles. Your content will be rendered directly to provide a live preview of how students will see it.</p>
        </div>
    </div>
</body>
</html>
"""

XBLOCK_EDIT_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenLearn - XBlock Editor</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f5f5;
            min-height: 100vh;
        }}
        .header {{
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 20px 40px;
        }}
        .header h1 {{ font-size: 1.8em; }}
        .header a {{ color: white; margin-left: 20px; }}
        .main {{ padding: 40px; max-width: 900px; margin: 0 auto; }}
        .editor-panel {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 30px;
            margin-bottom: 20px;
        }}
        .editor-panel h2 {{ color: #1e3c72; margin-bottom: 20px; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
        .form-group {{ margin-bottom: 20px; }}
        .form-group label {{ display: block; margin-bottom: 8px; color: #333; font-weight: bold; }}
        .form-group input, .form-group textarea {{
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 6px;
            font-size: 1em;
            transition: border-color 0.2s;
        }}
        .form-group input:focus, .form-group textarea:focus {{
            border-color: #667eea;
            outline: none;
        }}
        .form-group textarea {{ min-height: 100px; resize: vertical; }}
        .form-group small {{ color: #888; display: block; margin-top: 5px; }}
        .btn {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 6px;
            font-size: 1em;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s;
        }}
        .btn:hover {{ transform: translateY(-2px); }}
        .preview-panel {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 30px;
        }}
        .preview-panel h2 {{ color: #1e3c72; margin-bottom: 20px; }}
        .block-status {{ padding: 20px; text-align: center; border-radius: 8px; background: #f0f0f0; }}
        .block-status.success {{ background: #d4edda; color: #155724; }}
        .block-status.warning {{ background: #fff3cd; color: #856404; }}
        .block-status.error {{ background: #f8f8f8; color: #666; }}
        .status-icon {{ font-size: 2em; display: block; margin-bottom: 10px; }}
        .validation-error {{ background: #f8d7da; color: #721c24; padding: 15px; border-radius: 6px; margin-bottom: 20px; }}
        .help-text {{ background: #e7f1ff; padding: 15px; border-radius: 6px; margin-top: 20px; color: #0c5460; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>&#127922; Drag & Drop XBlock Editor</h1>
        <a href="/">Home</a>
        <a href="/studio">Studio</a>
    </div>
    <div class="main">
        {error_msg}
        <div class="editor-panel">
            <h2>Block Configuration</h2>
            <form method="POST" action="/xblock/edit">
                <div class="form-group">
                    <label for="display_name">Display Name (Block Title)</label>
                    <input type="text" id="display_name" name="display_name" value="{display_name}" placeholder="e.g., Chemistry Molecules Quiz">
                    <small>The title shown to students at the top of the block</small>
                </div>
                <div class="form-group">
                    <label for="question_text">Question Text (Instructions)</label>
                    <textarea id="question_text" name="question_text" placeholder="e.g., Drag each molecule to its correct category">{question_text}</textarea>
                    <small>Instructions displayed to students explaining what to do</small>
                </div>
                <div class="form-group">
                    <label for="zone_title">Zone Title (Drop Area Label)</label>
                    <input type="text" id="zone_title" name="zone_title" value="{zone_title}" placeholder="e.g., Organic Compounds">
                    <small>Label for the drag-and-drop target zone</small>
                </div>
                <button type="submit" class="btn">&#128065; Preview Block</button>
            </form>
            <div class="help-text">
                <strong>&#128161; Tip:</strong> Your content will be rendered in a live preview to show exactly how students will see it. HTML formatting is supported for rich content display.
            </div>
        </div>
        <div class="preview-panel">
            <h2>Block Preview</h2>
            {result}
        </div>
    </div>
</body>
</html>
"""

XBLOCK_PREVIEW = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>XBlock Preview</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            padding: 30px;
            background: #f5f5f5;
        }}
        .xblock-container {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 25px;
            max-width: 800px;
            margin: 0 auto;
        }}
        .xblock-title {{
            color: #1e3c72;
            font-size: 1.5em;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #eee;
        }}
        .xblock-question {{
            color: #333;
            line-height: 1.6;
            margin-bottom: 20px;
            padding: 15px;
            background: #f9f9f9;
            border-radius: 6px;
        }}
        .drop-zone {{
            border: 3px dashed #667eea;
            border-radius: 8px;
            padding: 30px;
            text-align: center;
            min-height: 150px;
        }}
        .zone-title {{
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }}
        .zone-hint {{ color: #888; }}
    </style>
</head>
<body>
    <div class="xblock-container">
        <div class="xblock-title">{display_name}</div>
        <div class="xblock-question">{question_text}</div>
        <div class="drop-zone">
            <div class="zone-title">{zone_title}</div>
            <div class="zone-hint">Drag items here</div>
        </div>
    </div>
</body>
</html>
"""

# Kept for backwards compatibility - not used in new implementation
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
