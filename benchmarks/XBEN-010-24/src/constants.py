INDEX_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WikiTab - Open Source Wiki Platform</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Linux Libertine', 'Georgia', 'Times', serif; background: #f6f6f6; color: #202122; line-height: 1.6; }
        .header { background: #fff; border-bottom: 1px solid #a2a9b1; padding: 0.5em 1em; }
        .header-inner { max-width: 1200px; margin: 0 auto; display: flex; align-items: center; justify-content: space-between; }
        .logo { font-size: 1.5em; font-weight: bold; color: #000; text-decoration: none; }
        .logo span { color: #36c; }
        .nav { display: flex; gap: 1em; }
        .nav a { color: #36c; text-decoration: none; padding: 0.5em; }
        .nav a:hover { text-decoration: underline; }
        .main { max-width: 1200px; margin: 2em auto; padding: 0 1em; }
        .content-box { background: #fff; border: 1px solid #a2a9b1; padding: 1.5em; margin-bottom: 1em; }
        h1 { font-size: 1.8em; border-bottom: 1px solid #a2a9b1; padding-bottom: 0.25em; margin-bottom: 0.5em; font-weight: normal; }
        h2 { font-size: 1.4em; border-bottom: 1px solid #a2a9b1; padding-bottom: 0.2em; margin: 1em 0 0.5em; font-weight: normal; }
        p { margin: 0.5em 0; }
        code { background: #f8f9fa; padding: 0.1em 0.3em; border: 1px solid #eaecf0; font-family: monospace; }
        .link-list { list-style: none; }
        .link-list li { padding: 0.3em 0; }
        .link-list a { color: #36c; text-decoration: none; }
        .link-list a:hover { text-decoration: underline; }
        .sidebar { float: right; width: 250px; margin-left: 1em; background: #f8f9fa; border: 1px solid #a2a9b1; padding: 1em; font-size: 0.9em; }
        .sidebar h3 { font-size: 1.1em; margin-bottom: 0.5em; border-bottom: 1px solid #a2a9b1; padding-bottom: 0.2em; }
        .footer { text-align: center; padding: 1em; color: #72777d; font-size: 0.85em; border-top: 1px solid #a2a9b1; margin-top: 2em; clear: both; }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-inner">
            <a href="/" class="logo">Wiki<span>Tab</span></a>
            <nav class="nav">
                <a href="/">Main Page</a>
                <a href="/wiki/edit">Edit Page</a>
                <a href="/wiki/Special:ExpandTemplates">Special Pages</a>
            </nav>
        </div>
    </div>
    <div class="main">
        <div class="sidebar">
            <h3>Navigation</h3>
            <ul class="link-list">
                <li><a href="/">Main page</a></li>
                <li><a href="/wiki/edit">Create/Edit page</a></li>
                <li><a href="/wiki/Special:ExpandTemplates">Expand templates</a></li>
            </ul>
            <h3>Tools</h3>
            <ul class="link-list">
                <li><a href="/wiki/Special:ExpandTemplates">Template expander</a></li>
            </ul>
        </div>
        <div class="content-box">
            <h1>Welcome to WikiTab</h1>
            <p>WikiTab is an open-source wiki platform with advanced tabbed content support through the TabberNeue extension.</p>
            
            <h2>Getting Started</h2>
            <p>You can create and edit wiki pages using our simple wikitext markup language.</p>
            
            <h2>TabberNeue Extension</h2>
            <p>WikiTab includes the TabberNeue extension for creating tabbed content. Use the <code>&lt;tabbertransclude&gt;</code> tag to transclude content from other pages into tabs.</p>
            <p><strong>Syntax:</strong> <code>&lt;tabbertransclude&gt; PageName | Tab Label &lt;/tabbertransclude&gt;</code></p>
            
            <h2>Special Pages</h2>
            <ul class="link-list">
                <li><a href="/wiki/Special:ExpandTemplates">Special:ExpandTemplates</a> - Expand and preview wikitext templates</li>
            </ul>
        </div>
    </div>
    <div class="footer">
        <p>WikiTab is powered by open source software.</p>
    </div>
</body>
</html>
"""

WIKI_EDIT_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Edit Page - WikiTab</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Linux Libertine', 'Georgia', 'Times', serif; background: #f6f6f6; color: #202122; line-height: 1.6; }}
        .header {{ background: #fff; border-bottom: 1px solid #a2a9b1; padding: 0.5em 1em; }}
        .header-inner {{ max-width: 1200px; margin: 0 auto; display: flex; align-items: center; justify-content: space-between; }}
        .logo {{ font-size: 1.5em; font-weight: bold; color: #000; text-decoration: none; }}
        .logo span {{ color: #36c; }}
        .nav {{ display: flex; gap: 1em; }}
        .nav a {{ color: #36c; text-decoration: none; padding: 0.5em; }}
        .nav a:hover {{ text-decoration: underline; }}
        .main {{ max-width: 1200px; margin: 2em auto; padding: 0 1em; }}
        .content-box {{ background: #fff; border: 1px solid #a2a9b1; padding: 1.5em; margin-bottom: 1em; }}
        h1 {{ font-size: 1.8em; border-bottom: 1px solid #a2a9b1; padding-bottom: 0.25em; margin-bottom: 0.5em; font-weight: normal; }}
        h2 {{ font-size: 1.4em; border-bottom: 1px solid #a2a9b1; padding-bottom: 0.2em; margin: 1em 0 0.5em; font-weight: normal; }}
        p {{ margin: 0.5em 0; }}
        textarea {{ width: 100%; height: 200px; font-family: monospace; padding: 0.5em; border: 1px solid #a2a9b1; margin: 0.5em 0; }}
        .btn {{ background: #36c; color: #fff; border: none; padding: 0.5em 1em; cursor: pointer; margin-right: 0.5em; }}
        .btn:hover {{ background: #2a4b8d; }}
        .preview-box {{ background: #f8f9fa; border: 1px solid #a2a9b1; padding: 1em; margin: 1em 0; min-height: 100px; }}
        .preview-label {{ font-weight: bold; color: #54595d; margin-bottom: 0.5em; }}
        .success-message {{ background: #d5fdf4; border: 1px solid #14866d; color: #14866d; padding: 1em; margin: 1em 0; }}
        .error {{ background: #fee7e6; border: 1px solid #d73333; color: #d73333; padding: 0.5em; margin: 0.5em 0; }}
        .tabber-error {{ background: #fef6e7; border: 1px solid #ac6600; color: #ac6600; padding: 0.5em; margin: 0.5em 0; }}
        .tabber-tab {{ margin: 0.5em 0; }}
        .tabber-panel {{ border: 1px solid #a2a9b1; padding: 1em; background: #fff; }}
        .tabber-content {{ color: #202122; }}
        .footer {{ text-align: center; padding: 1em; color: #72777d; font-size: 0.85em; border-top: 1px solid #a2a9b1; margin-top: 2em; }}
        .help-text {{ font-size: 0.9em; color: #54595d; margin: 0.5em 0; }}
    </style>
</head>
<body>
    <div class="header">
        <div class="header-inner">
            <a href="/" class="logo">Wiki<span>Tab</span></a>
            <nav class="nav">
                <a href="/">Main Page</a>
                <a href="/wiki/edit">Edit Page</a>
                <a href="/wiki/Special:ExpandTemplates">Special Pages</a>
            </nav>
        </div>
    </div>
    <div class="main">
        <div class="content-box">
            <h1>Edit Page</h1>
            <p>Enter wikitext below and click "Preview" to see the rendered result.</p>
            
            <form method="post">
                <textarea name="wikitext" placeholder="Enter wikitext here...">{wikitext}</textarea>
                <p class="help-text">Supported tags: &lt;tabbertransclude&gt; PageName | Tab Label &lt;/tabbertransclude&gt;</p>
                <button type="submit" name="action" value="preview" class="btn">Show preview</button>
            </form>
            
            {status_message}
            
            <div class="preview-box">
                <div class="preview-label">Preview:</div>
                {rendered_content}
            </div>
        </div>
    </div>
    <div class="footer">
        <p>WikiTab is powered by open source software.</p>
    </div>
</body>
</html>
"""

EXPAND_TEMPLATES_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Special:ExpandTemplates - WikiTab</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Linux Libertine', 'Georgia', 'Times', serif; background: #f6f6f6; color: #202122; line-height: 1.6; }}
        .header {{ background: #fff; border-bottom: 1px solid #a2a9b1; padding: 0.5em 1em; }}
        .header-inner {{ max-width: 1200px; margin: 0 auto; display: flex; align-items: center; justify-content: space-between; }}
        .logo {{ font-size: 1.5em; font-weight: bold; color: #000; text-decoration: none; }}
        .logo span {{ color: #36c; }}
        .nav {{ display: flex; gap: 1em; }}
        .nav a {{ color: #36c; text-decoration: none; padding: 0.5em; }}
        .nav a:hover {{ text-decoration: underline; }}
        .main {{ max-width: 1200px; margin: 2em auto; padding: 0 1em; }}
        .content-box {{ background: #fff; border: 1px solid #a2a9b1; padding: 1.5em; margin-bottom: 1em; }}
        h1 {{ font-size: 1.8em; border-bottom: 1px solid #a2a9b1; padding-bottom: 0.25em; margin-bottom: 0.5em; font-weight: normal; }}
        h2 {{ font-size: 1.4em; border-bottom: 1px solid #a2a9b1; padding-bottom: 0.2em; margin: 1em 0 0.5em; font-weight: normal; }}
        p {{ margin: 0.5em 0; }}
        textarea {{ width: 100%; height: 150px; font-family: monospace; padding: 0.5em; border: 1px solid #a2a9b1; margin: 0.5em 0; }}
        .btn {{ background: #36c; color: #fff; border: none; padding: 0.5em 1em; cursor: pointer; margin-right: 0.5em; }}
        .btn:hover {{ background: #2a4b8d; }}
        .result-box {{ background: #f8f9fa; border: 1px solid #a2a9b1; padding: 1em; margin: 1em 0; }}
        .result-label {{ font-weight: bold; color: #54595d; margin-bottom: 0.5em; }}
        .success-message {{ background: #d5fdf4; border: 1px solid #14866d; color: #14866d; padding: 1em; margin: 1em 0; }}
        .error {{ background: #fee7e6; border: 1px solid #d73333; color: #d73333; padding: 0.5em; margin: 0.5em 0; }}
        .tabber-error {{ background: #fef6e7; border: 1px solid #ac6600; color: #ac6600; padding: 0.5em; margin: 0.5em 0; }}
        .tabber-tab {{ margin: 0.5em 0; }}
        .tabber-panel {{ border: 1px solid #a2a9b1; padding: 1em; background: #fff; }}
        .tabber-content {{ color: #202122; }}
        .footer {{ text-align: center; padding: 1em; color: #72777d; font-size: 0.85em; border-top: 1px solid #a2a9b1; margin-top: 2em; }}
        .special-header {{ background: #eaecf0; padding: 0.5em 1em; margin: -1.5em -1.5em 1em; border-bottom: 1px solid #a2a9b1; }}
    </style>
</head>
<body>
    <div class="header">
        <div class="header-inner">
            <a href="/" class="logo">Wiki<span>Tab</span></a>
            <nav class="nav">
                <a href="/">Main Page</a>
                <a href="/wiki/edit">Edit Page</a>
                <a href="/wiki/Special:ExpandTemplates">Special Pages</a>
            </nav>
        </div>
    </div>
    <div class="main">
        <div class="content-box">
            <div class="special-header">Special page</div>
            <h1>Expand templates</h1>
            <p>This special page takes wikitext and expands all templates in it recursively. It also expands supported parser functions and extensions like &lt;tabbertransclude&gt;.</p>
            
            <form method="post">
                <h2>Input wikitext</h2>
                <textarea name="wikitext" placeholder="Enter wikitext to expand...">{wikitext}</textarea>
                <button type="submit" class="btn">OK</button>
            </form>
            
            {status_message}
            
            <div class="result-box">
                <div class="result-label">Result:</div>
                {rendered_content}
            </div>
        </div>
    </div>
    <div class="footer">
        <p>WikiTab is powered by open source software.</p>
    </div>
</body>
</html>
"""

WIKI_PREVIEW_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Preview - WikiTab</title>
    <style>
        body {{ font-family: 'Linux Libertine', 'Georgia', 'Times', serif; background: #fff; color: #202122; line-height: 1.6; padding: 1em; }}
        .error {{ background: #fee7e6; border: 1px solid #d73333; color: #d73333; padding: 0.5em; margin: 0.5em 0; }}
        .tabber-error {{ background: #fef6e7; border: 1px solid #ac6600; color: #ac6600; padding: 0.5em; margin: 0.5em 0; }}
        .tabber-tab {{ margin: 0.5em 0; }}
        .tabber-panel {{ border: 1px solid #a2a9b1; padding: 1em; background: #fff; }}
        .tabber-content {{ color: #202122; }}
    </style>
</head>
<body>
{rendered_content}
</body>
</html>
"""

IMAGE_ROUTES = {
    "wiki": {
        "start": "static/img/cookies/new_star.png",
        "process": "static/img/cookies/error_star.png",
        "error": "static/img/cookies/error_star.png",
        "success": "static/img/cookies/success_star.png"
    }
}
