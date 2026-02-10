INDEX_CONTENT = """
<!DOCTYPE html>
<html>
    <head>
        <link rel="shortcut icon" href="static/assets/fav-icon.png">
        <link rel="stylesheet" type="text/css" href="static/css/style.css">
        <link rel="stylesheet" type="text/css" href="static/css/xss/index.css">
        <title>Wiki Editor - TabberNeue Extension</title>
        <style>
            .wiki-intro {
                text-align: left;
                padding: 20px;
                background: rgba(255,255,255,0.1);
                border-radius: 10px;
                margin: 20px 0;
            }
            .wiki-intro h2 { color: #fff; margin-bottom: 15px; }
            .wiki-intro p { color: #ddd; line-height: 1.6; margin-bottom: 10px; }
            .wiki-intro code { 
                background: rgba(0,0,0,0.3); 
                padding: 2px 6px; 
                border-radius: 3px;
                font-family: monospace;
            }
            .wiki-intro pre {
                background: rgba(0,0,0,0.3);
                padding: 15px;
                border-radius: 5px;
                overflow-x: auto;
                font-family: monospace;
                color: #0f0;
            }
        </style>
    </head>
    <body>
        <article class="widget widget__login">
        <div class="widget__content">
            <div class="box">
                <form class="box-form">
                    <img class="text-img" src="static/img/logo5_white.png">
                    <h1>Wiki Editor</h1>
                    <p style="color: #ccc;">MediaWiki with TabberNeue Extension</p>
                    
                    <div class="wiki-intro">
                        <h2>TabberNeue Extension</h2>
                        <p>This wiki uses the <strong>TabberNeue</strong> extension for creating tabbed content.</p>
                        <p>Use the <code>&lt;tabbertransclude&gt;</code> tag to transclude pages into tabs:</p>
                        <pre>&lt;tabbertransclude&gt;PageName | Tab Label&lt;/tabbertransclude&gt;</pre>
                        <p>The text before <code>|</code> is the page name, and text after is the tab label.</p>
                    </div>
                    
                    <div class="init-table">
                        <div class="row">
                            <div class="column">
                                <a class="text" type="text" href="wiki">
                                    <img src="static/img/cookies/new_star.png" alt="Star" width="150" height="150">
                                    Wiki Editor
                                </a>
                            </div>
                        </div>
                    </div>
                    <br><br>
                </form>
            </div>
        </div>
    </body>
</html>
"""


WIKI_CONTENT = """
<!DOCTYPE html>
<html>
    <head>
        <link rel="shortcut icon" href="static/assets/fav-icon.png">
        <link rel="stylesheet" type="text/css" href="static/css/style.css">
        <link rel="stylesheet" type="text/css" href="static/css/xss/xss21.css">
        <title>Wiki Editor - Preview</title>
        <style>
            .wiki-editor {
                width: 100%;
                max-width: 600px;
                margin: 20px auto;
            }
            .wiki-editor textarea {
                width: 100%;
                height: 150px;
                background: rgba(255,255,255,0.1);
                border: 1px solid rgba(255,255,255,0.3);
                border-radius: 5px;
                color: #fff;
                padding: 10px;
                font-family: monospace;
                font-size: 14px;
            }
            .wiki-editor button {
                margin-top: 10px;
                padding: 10px 30px;
                background: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
            }
            .wiki-editor button:hover {
                background: #45a049;
            }
            .preview-section {
                margin-top: 30px;
                padding: 20px;
                background: rgba(255,255,255,0.1);
                border-radius: 10px;
            }
            .preview-section h3 {
                color: #fff;
                margin-bottom: 15px;
                border-bottom: 1px solid rgba(255,255,255,0.3);
                padding-bottom: 10px;
            }
            .preview-content {
                color: #ddd;
                line-height: 1.6;
            }
            .tabber-tab {
                margin: 10px 0;
                padding: 15px;
                background: rgba(255,255,255,0.05);
                border-radius: 5px;
                border-left: 3px solid #4CAF50;
            }
            .tabber-tab-label {
                font-weight: bold;
                color: #4CAF50;
                margin-bottom: 10px;
            }
            .tabber-content {
                color: #ccc;
            }
            .tabber-error {
                color: #ff6b6b;
                background: rgba(255,0,0,0.1);
                padding: 10px;
                border-radius: 3px;
                border-left: 3px solid #ff6b6b;
            }
            .hint-text {
                color: #888;
                font-size: 12px;
                margin-top: 5px;
            }
        </style>
    </head>
    <body>
        <article class="widget widget__login">
        <div class="widget__content">
            <div class="box">
                <form class="box-form" method="get" action="wiki">
                    <img class="text-img" src="static/img/logo5_white.png">
                    <h1>Wiki Editor</h1>
                    <p style="color: #ccc;">MediaWiki with TabberNeue Extension</p>
                    
                    <div class="wiki-editor">
                        <label style="color: #fff; display: block; margin-bottom: 10px;">
                            Enter your wikitext:
                        </label>
                        <textarea name="wikitext" placeholder="Enter wikitext here...&#10;&#10;Example:&#10;&lt;tabbertransclude&gt;MyPage | My Tab&lt;/tabbertransclude&gt;">{0}</textarea>
                        <p class="hint-text">Use &lt;tabbertransclude&gt;PageName | Label&lt;/tabbertransclude&gt; to create tabs</p>
                        <button type="submit">Preview</button>
                    </div>
                    
                    <div class="preview-section">
                        <h3>Preview Output</h3>
                        <div class="preview-content">
                            {1}
                        </div>
                    </div>
                </form>
            </div>
        </div>
    </body>
</html>
"""


WIKI_CONTENT_WITH_RESULT = """
<!DOCTYPE html>
<html>
    <head>
        <link rel="shortcut icon" href="static/assets/fav-icon.png">
        <link rel="stylesheet" type="text/css" href="static/css/style.css">
        <link rel="stylesheet" type="text/css" href="static/css/xss/xss21.css">
        <title>Wiki Editor - Preview</title>
        <style>
            .wiki-editor {
                width: 100%;
                max-width: 600px;
                margin: 20px auto;
            }
            .wiki-editor textarea {
                width: 100%;
                height: 150px;
                background: rgba(255,255,255,0.1);
                border: 1px solid rgba(255,255,255,0.3);
                border-radius: 5px;
                color: #fff;
                padding: 10px;
                font-family: monospace;
                font-size: 14px;
            }
            .wiki-editor button {
                margin-top: 10px;
                padding: 10px 30px;
                background: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
            }
            .wiki-editor button:hover {
                background: #45a049;
            }
            .preview-section {
                margin-top: 30px;
                padding: 20px;
                background: rgba(255,255,255,0.1);
                border-radius: 10px;
            }
            .preview-section h3 {
                color: #fff;
                margin-bottom: 15px;
                border-bottom: 1px solid rgba(255,255,255,0.3);
                padding-bottom: 10px;
            }
            .preview-content {
                color: #ddd;
                line-height: 1.6;
            }
            .tabber-tab {
                margin: 10px 0;
                padding: 15px;
                background: rgba(255,255,255,0.05);
                border-radius: 5px;
                border-left: 3px solid #4CAF50;
            }
            .tabber-tab-label {
                font-weight: bold;
                color: #4CAF50;
                margin-bottom: 10px;
            }
            .tabber-content {
                color: #ccc;
            }
            .tabber-error {
                color: #ff6b6b;
                background: rgba(255,0,0,0.1);
                padding: 10px;
                border-radius: 3px;
                border-left: 3px solid #ff6b6b;
            }
            .hint-text {
                color: #888;
                font-size: 12px;
                margin-top: 5px;
            }
        </style>
    </head>
    <body>
        <article class="widget widget__login">
        <div class="widget__content">
            <div class="box">
                <form class="box-form" method="get" action="wiki">
                    <img class="text-img" src="static/img/logo5_white.png">
                    <h1>Wiki Editor</h1>
                    <p style="color: #ccc;">MediaWiki with TabberNeue Extension</p>
                    
                    <div class="wiki-editor">
                        <label style="color: #fff; display: block; margin-bottom: 10px;">
                            Enter your wikitext:
                        </label>
                        <textarea name="wikitext" placeholder="Enter wikitext here...&#10;&#10;Example:&#10;&lt;tabbertransclude&gt;MyPage | My Tab&lt;/tabbertransclude&gt;">{0}</textarea>
                        <p class="hint-text">Use &lt;tabbertransclude&gt;PageName | Label&lt;/tabbertransclude&gt; to create tabs</p>
                        <button type="submit">Preview</button>
                    </div>
                    
                    <div class="preview-section">
                        <h3>Preview Output</h3>
                        <div class="preview-content">
                            {1}
                        </div>
                    </div>
                    
                    {2}
                </form>
            </div>
        </div>
    </body>
</html>
"""


# Image routes
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
