INDEX_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>XWiki - Document Management System</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
        .header { background: #3498db; color: white; padding: 15px 30px; }
        .header h1 { margin: 0; font-size: 24px; }
        .nav { background: #2980b9; padding: 10px 30px; }
        .nav a { color: white; text-decoration: none; margin-right: 20px; }
        .nav a:hover { text-decoration: underline; }
        .content { max-width: 1000px; margin: 30px auto; padding: 20px; background: white; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .wiki-list { list-style: none; padding: 0; }
        .wiki-list li { padding: 15px; border-bottom: 1px solid #eee; }
        .wiki-list li:last-child { border-bottom: none; }
        .wiki-list a { color: #2980b9; text-decoration: none; font-weight: bold; }
        .wiki-list a:hover { text-decoration: underline; }
        .wiki-list .desc { color: #666; font-size: 14px; margin-top: 5px; }
        .breadcrumb { color: #666; margin-bottom: 20px; }
        .breadcrumb a { color: #2980b9; }
        .footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>XWiki Document Management</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/xwiki/bin/view/Main/WebHome">Documents</a>
        <a href="/xwiki/bin/attach/Main/WebHome">Attachments</a>
    </div>
    <div class="content">
        <div class="breadcrumb">
            <a href="/">Home</a> &raquo; Wiki Spaces
        </div>
        <h2>Available Wiki Spaces</h2>
        <ul class="wiki-list">
            <li>
                <a href="/xwiki/bin/view/Main/WebHome">Main</a>
                <div class="desc">Main wiki space - contains primary documentation</div>
            </li>
            <li>
                <a href="/xwiki/bin/view/Sandbox/WebHome">Sandbox</a>
                <div class="desc">Test space for experimenting with wiki features</div>
            </li>
            <li>
                <a href="/xwiki/bin/attach/Main/WebHome">Manage Attachments</a>
                <div class="desc">Upload, view, and delete file attachments</div>
            </li>
        </ul>
    </div>
    <div class="footer">
        XWiki Platform - Document Management System v14.10.5
    </div>
</body>
</html>
"""

ERROR_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>XWiki - {error_title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }}
        .header {{ background: #3498db; color: white; padding: 15px 30px; }}
        .header h1 {{ margin: 0; font-size: 24px; }}
        .nav {{ background: #2980b9; padding: 10px 30px; }}
        .nav a {{ color: white; text-decoration: none; margin-right: 20px; }}
        .nav a:hover {{ text-decoration: underline; }}
        .content {{ max-width: 1000px; margin: 30px auto; padding: 20px; background: white; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .error-box {{ background: #fee; border: 1px solid #f00; border-radius: 5px; padding: 20px; margin: 20px 0; }}
        .error-box h2 {{ color: #c00; margin-top: 0; }}
        .error-box p {{ color: #666; margin-bottom: 0; }}
        .breadcrumb {{ color: #666; margin-bottom: 20px; }}
        .breadcrumb a {{ color: #2980b9; }}
        .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
        .debug-info {{ background: #efe; border: 1px solid #0a0; padding: 10px; margin-top: 15px; border-radius: 3px; font-family: monospace; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>XWiki Document Management</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/xwiki/bin/view/Main/WebHome">Documents</a>
        <a href="/xwiki/bin/attach/Main/WebHome">Attachments</a>
    </div>
    <div class="content">
        <div class="breadcrumb">
            <a href="/">Home</a> &raquo; Error
        </div>
        <div class="error-box">
            <h2>{error_title}</h2>
            <p>{error_message}</p>
        </div>
    </div>
    <div class="footer">
        XWiki Platform - Document Management System v14.10.5
    </div>
</body>
</html>
"""

DOCUMENT_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>XWiki - {space}/{page}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }}
        .header {{ background: #3498db; color: white; padding: 15px 30px; }}
        .header h1 {{ margin: 0; font-size: 24px; }}
        .nav {{ background: #2980b9; padding: 10px 30px; }}
        .nav a {{ color: white; text-decoration: none; margin-right: 20px; }}
        .nav a:hover {{ text-decoration: underline; }}
        .content {{ max-width: 1000px; margin: 30px auto; padding: 20px; background: white; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .breadcrumb {{ color: #666; margin-bottom: 20px; }}
        .breadcrumb a {{ color: #2980b9; }}
        .doc-content {{ line-height: 1.6; }}
        .doc-actions {{ margin-top: 20px; padding-top: 20px; border-top: 1px solid #eee; }}
        .doc-actions a {{ color: #2980b9; margin-right: 15px; }}
        .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>XWiki Document Management</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/xwiki/bin/view/Main/WebHome">Documents</a>
        <a href="/xwiki/bin/attach/{space}/{page}">Attachments</a>
    </div>
    <div class="content">
        <div class="breadcrumb">
            <a href="/">Home</a> &raquo; <a href="/xwiki/bin/view/{space}/WebHome">{space}</a> &raquo; {page}
        </div>
        <h2>{page}</h2>
        <div class="doc-content">
            <p>Welcome to the {page} document in the {space} space.</p>
            <p>This is a collaborative wiki page where users can share and edit content.</p>
        </div>
        <div class="doc-actions">
            <a href="/xwiki/bin/edit/{space}/{page}">Edit</a>
            <a href="/xwiki/bin/attach/{space}/{page}">Attachments</a>
            <a href="/xwiki/bin/history/{space}/{page}">History</a>
        </div>
    </div>
    <div class="footer">
        XWiki Platform - Document Management System v14.10.5
    </div>
</body>
</html>
"""

ATTACHMENTS_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>XWiki - Attachments - {space}/{page}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }}
        .header {{ background: #3498db; color: white; padding: 15px 30px; }}
        .header h1 {{ margin: 0; font-size: 24px; }}
        .nav {{ background: #2980b9; padding: 10px 30px; }}
        .nav a {{ color: white; text-decoration: none; margin-right: 20px; }}
        .nav a:hover {{ text-decoration: underline; }}
        .content {{ max-width: 1000px; margin: 30px auto; padding: 20px; background: white; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .breadcrumb {{ color: #666; margin-bottom: 20px; }}
        .breadcrumb a {{ color: #2980b9; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ text-align: left; padding: 12px; border-bottom: 1px solid #ddd; }}
        th {{ background: #f8f8f8; }}
        .btn {{ display: inline-block; padding: 5px 10px; background: #e74c3c; color: white; text-decoration: none; border-radius: 3px; font-size: 12px; }}
        .btn:hover {{ background: #c0392b; }}
        .btn-primary {{ background: #3498db; }}
        .btn-primary:hover {{ background: #2980b9; }}
        .info-box {{ background: #e8f4fd; border: 1px solid #3498db; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>XWiki Document Management</h1>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/xwiki/bin/view/Main/WebHome">Documents</a>
        <a href="/xwiki/bin/attach/Main/WebHome">Attachments</a>
    </div>
    <div class="content">
        <div class="breadcrumb">
            <a href="/">Home</a> &raquo; <a href="/xwiki/bin/view/{space}/WebHome">{space}</a> &raquo; <a href="/xwiki/bin/view/{space}/{page}">{page}</a> &raquo; Attachments
        </div>
        <h2>Attachments for {space}/{page}</h2>
        <div class="info-box">
            <strong>Tip:</strong> To delete an attachment, use the delete action: 
            <code>/xwiki/bin/delattachment/{space}/{page}/&lt;filename&gt;</code>
        </div>
        <table>
            <tr>
                <th>Filename</th>
                <th>Size</th>
                <th>Date</th>
                <th>Actions</th>
            </tr>
            <tr>
                <td>document.pdf</td>
                <td>1.2 MB</td>
                <td>2024-01-15</td>
                <td>
                    <a href="/xwiki/bin/download/{space}/{page}/document.pdf" class="btn btn-primary">Download</a>
                    <a href="/xwiki/bin/delattachment/{space}/{page}/document.pdf" class="btn">Delete</a>
                </td>
            </tr>
            <tr>
                <td>image.png</td>
                <td>245 KB</td>
                <td>2024-01-10</td>
                <td>
                    <a href="/xwiki/bin/download/{space}/{page}/image.png" class="btn btn-primary">Download</a>
                    <a href="/xwiki/bin/delattachment/{space}/{page}/image.png" class="btn">Delete</a>
                </td>
            </tr>
            <tr>
                <td>notes.txt</td>
                <td>4 KB</td>
                <td>2024-01-05</td>
                <td>
                    <a href="/xwiki/bin/download/{space}/{page}/notes.txt" class="btn btn-primary">Download</a>
                    <a href="/xwiki/bin/delattachment/{space}/{page}/notes.txt" class="btn">Delete</a>
                </td>
            </tr>
        </table>
    </div>
    <div class="footer">
        XWiki Platform - Document Management System v14.10.5
    </div>
</body>
</html>
"""
