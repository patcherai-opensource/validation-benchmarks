# encoding=utf8
# GROWI-like Comment Management System
# Vulnerable to authorization bypass (CVE-2021-3852 inspired)

from flask import Flask, request, jsonify, session, redirect, url_for, render_template_string
import os
import json
import uuid

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['PROPAGATE_EXCEPTIONS'] = True

# Read the flag from secret.txt
FLAG = open('secret.txt').read().strip()

# In-memory storage for users and comments
users = {
    "admin": {"password": "Adm1n$3cur3P@ss!", "role": "admin"},
    "guest": {"password": "guest", "role": "user"},
    "demo": {"password": "demo123", "role": "user"}
}

# Initial comments - admin's comment contains the flag (only visible to admin)
comments = {
    "comment_001": {
        "id": "comment_001",
        "page_id": "page_1",
        "author": "admin",
        "content": "Welcome to WikiNote! This is a public announcement.",
        "is_private": False
    },
    "comment_002": {
        "id": "comment_002",
        "page_id": "page_1",
        "author": "demo",
        "content": "Thanks for the welcome message!",
        "is_private": False
    },
    "comment_003": {
        "id": "comment_003",
        "page_id": "admin_notes",
        "author": "admin",
        "content": FLAG,
        "is_private": True
    }
}

# HTML Templates
INDEX_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>WikiNote - Collaborative Documentation</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #333; }
        .nav { margin-bottom: 20px; }
        .nav a { margin-right: 15px; color: #007bff; text-decoration: none; }
        .comment { background: #f9f9f9; padding: 10px; margin: 10px 0; border-radius: 4px; border-left: 3px solid #007bff; }
        .comment-author { font-weight: bold; color: #333; }
        .comment-content { margin-top: 5px; }
        .btn { padding: 8px 16px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; margin-right: 5px; }
        .btn:hover { background: #0056b3; }
        .btn-danger { background: #dc3545; }
        .btn-danger:hover { background: #c82333; }
        input, textarea { width: 100%; padding: 8px; margin: 5px 0; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        .error { color: red; margin: 10px 0; }
        .success { color: green; margin: 10px 0; }
        .info { background: #e7f3ff; padding: 10px; border-radius: 4px; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>WikiNote</h1>
        <p>Collaborative Documentation Platform</p>
        <div class="nav">
            {% if session.get('username') %}
                <span>Logged in as: <strong>{{ session.get('username') }}</strong></span> |
                <a href="/pages">Pages</a>
                <a href="/api/docs">API Documentation</a>
                <a href="/logout">Logout</a>
            {% else %}
                <a href="/login">Login</a>
                <a href="/api/docs">API Documentation</a>
            {% endif %}
        </div>
        <div class="info">
            <p><strong>Available test accounts:</strong></p>
            <ul>
                <li>Username: <code>guest</code> / Password: <code>guest</code></li>
                <li>Username: <code>demo</code> / Password: <code>demo123</code></li>
            </ul>
        </div>
    </div>
</body>
</html>
'''

LOGIN_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>WikiNote - Login</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 400px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #333; }
        input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        .btn { width: 100%; padding: 10px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
        .btn:hover { background: #0056b3; }
        .error { color: red; margin: 10px 0; }
        a { color: #007bff; }
    </style>
</head>
<body>
    <div class="container">
        <h1>WikiNote Login</h1>
        {% if error %}
        <p class="error">{{ error }}</p>
        {% endif %}
        <form method="POST">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit" class="btn">Login</button>
        </form>
        <p><a href="/">Back to Home</a></p>
    </div>
</body>
</html>
'''

PAGES_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>WikiNote - Pages</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1, h2 { color: #333; }
        .nav { margin-bottom: 20px; }
        .nav a { margin-right: 15px; color: #007bff; text-decoration: none; }
        .comment { background: #f9f9f9; padding: 15px; margin: 10px 0; border-radius: 4px; border-left: 3px solid #007bff; }
        .comment-author { font-weight: bold; color: #333; }
        .comment-id { font-size: 12px; color: #888; }
        .comment-content { margin-top: 5px; }
        .btn { padding: 8px 16px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; margin-right: 5px; text-decoration: none; display: inline-block; }
        .btn:hover { background: #0056b3; }
        .btn-danger { background: #dc3545; }
        .btn-danger:hover { background: #c82333; }
        .btn-sm { padding: 4px 8px; font-size: 12px; }
        input, textarea { width: 100%; padding: 8px; margin: 5px 0; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        .private-badge { background: #ffc107; color: #000; padding: 2px 6px; border-radius: 3px; font-size: 11px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>WikiNote Pages</h1>
        <div class="nav">
            <a href="/">Home</a>
            <a href="/api/docs">API Documentation</a>
            <a href="/logout">Logout</a>
        </div>
        
        <h2>Page: Main Discussion</h2>
        <p>View and manage comments on this page.</p>
        
        <h3>Comments</h3>
        {% for comment in comments %}
        <div class="comment">
            <div class="comment-author">{{ comment.author }} 
                <span class="comment-id">(ID: {{ comment.id }})</span>
                {% if comment.is_private %}<span class="private-badge">Private</span>{% endif %}
            </div>
            <div class="comment-content">{{ comment.content }}</div>
        </div>
        {% endfor %}
        
        <h3>Add New Comment</h3>
        <form method="POST" action="/api/comments.add">
            <input type="hidden" name="page_id" value="page_1">
            <textarea name="comment" placeholder="Write your comment..." rows="3"></textarea>
            <button type="submit" class="btn">Add Comment</button>
        </form>
    </div>
</body>
</html>
'''

API_DOCS_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>WikiNote - API Documentation</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 900px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1, h2, h3 { color: #333; }
        .nav { margin-bottom: 20px; }
        .nav a { margin-right: 15px; color: #007bff; text-decoration: none; }
        .endpoint { background: #f9f9f9; padding: 15px; margin: 15px 0; border-radius: 4px; border-left: 3px solid #28a745; }
        .method { display: inline-block; padding: 3px 8px; border-radius: 3px; font-size: 12px; font-weight: bold; margin-right: 10px; }
        .method-post { background: #28a745; color: white; }
        .method-get { background: #007bff; color: white; }
        code { background: #e9ecef; padding: 2px 6px; border-radius: 3px; font-family: monospace; }
        pre { background: #2d2d2d; color: #f8f8f2; padding: 15px; border-radius: 4px; overflow-x: auto; }
        .param { margin: 5px 0; }
        .param-name { font-weight: bold; color: #007bff; }
    </style>
</head>
<body>
    <div class="container">
        <h1>WikiNote API Documentation</h1>
        <div class="nav">
            <a href="/">Home</a>
            <a href="/pages">Pages</a>
        </div>
        
        <h2>Comment Management API</h2>
        <p>The following endpoints allow you to manage comments on wiki pages.</p>
        
        <div class="endpoint">
            <h3><span class="method method-get">GET</span> /api/comments.list</h3>
            <p>List all public comments for a page.</p>
            <p><strong>Parameters:</strong></p>
            <div class="param"><span class="param-name">page_id</span> - The page identifier</div>
        </div>
        
        <div class="endpoint">
            <h3><span class="method method-post">POST</span> /api/comments.add</h3>
            <p>Add a new comment to a page.</p>
            <p><strong>Parameters:</strong></p>
            <div class="param"><span class="param-name">page_id</span> - The page identifier</div>
            <div class="param"><span class="param-name">comment</span> - The comment content</div>
        </div>
        
        <div class="endpoint">
            <h3><span class="method method-post">POST</span> /api/comments.update</h3>
            <p>Update an existing comment.</p>
            <p><strong>Parameters (JSON body):</strong></p>
            <div class="param"><span class="param-name">commentForm.comment_id</span> - The comment ID to update</div>
            <div class="param"><span class="param-name">commentForm.comment</span> - The new comment content</div>
            <div class="param"><span class="param-name">commentForm.author</span> - The author username for verification</div>
            <pre>{
  "commentForm": {
    "comment_id": "comment_001",
    "comment": "Updated content",
    "author": "username"
  }
}</pre>
        </div>
        
        <div class="endpoint">
            <h3><span class="method method-post">POST</span> /api/comments.remove</h3>
            <p>Remove a comment.</p>
            <p><strong>Parameters (JSON body):</strong></p>
            <div class="param"><span class="param-name">commentForm.comment_id</span> - The comment ID to remove</div>
            <div class="param"><span class="param-name">commentForm.author</span> - The author username for verification</div>
        </div>
        
        <div class="endpoint">
            <h3><span class="method method-get">GET</span> /api/comments.get</h3>
            <p>Get a specific comment by ID.</p>
            <p><strong>Parameters:</strong></p>
            <div class="param"><span class="param-name">comment_id</span> - The comment ID</div>
            <div class="param"><span class="param-name">author</span> - The author username for authorization</div>
        </div>
        
        <h2>Known Comment IDs</h2>
        <p>For testing purposes, here are some existing comment IDs:</p>
        <ul>
            <li><code>comment_001</code> - Public announcement by admin</li>
            <li><code>comment_002</code> - Reply from demo user</li>
            <li><code>comment_003</code> - Private admin notes</li>
        </ul>
    </div>
</body>
</html>
'''


@app.route('/')
def index():
    return render_template_string(INDEX_HTML)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        if username in users and users[username]['password'] == password:
            session['username'] = username
            session['role'] = users[username]['role']
            return redirect(url_for('pages'))
        else:
            error = "Invalid username or password"
    
    return render_template_string(LOGIN_HTML, error=error)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/pages')
def pages():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Show only public comments to regular users
    visible_comments = []
    for cid, comment in comments.items():
        if comment['page_id'] == 'page_1':
            if not comment['is_private'] or session.get('username') == comment['author']:
                visible_comments.append(comment)
    
    return render_template_string(PAGES_HTML, comments=visible_comments)


@app.route('/api/docs')
def api_docs():
    return render_template_string(API_DOCS_HTML)


@app.route('/api/comments.list', methods=['GET'])
def api_comments_list():
    page_id = request.args.get('page_id', 'page_1')
    
    result = []
    for cid, comment in comments.items():
        if comment['page_id'] == page_id and not comment['is_private']:
            result.append({
                'id': comment['id'],
                'author': comment['author'],
                'content': comment['content']
            })
    
    return jsonify({'ok': True, 'comments': result})


@app.route('/api/comments.add', methods=['POST'])
def api_comments_add():
    if 'username' not in session:
        return jsonify({'ok': False, 'error': 'Authentication required'}), 401
    
    if request.is_json:
        data = request.get_json()
        page_id = data.get('page_id', 'page_1')
        content = data.get('comment', '')
    else:
        page_id = request.form.get('page_id', 'page_1')
        content = request.form.get('comment', '')
    
    if not content:
        return jsonify({'ok': False, 'error': 'Comment content required'}), 400
    
    comment_id = 'comment_' + str(uuid.uuid4())[:8]
    comments[comment_id] = {
        'id': comment_id,
        'page_id': page_id,
        'author': session['username'],
        'content': content,
        'is_private': False
    }
    
    if request.is_json:
        return jsonify({'ok': True, 'comment_id': comment_id})
    else:
        return redirect(url_for('pages'))


@app.route('/api/comments.update', methods=['POST'])
def api_comments_update():
    """
    VULNERABLE: This endpoint trusts the 'author' field from user input
    instead of checking actual ownership from the database.
    
    An attacker can update any comment by providing their own username
    as the 'author' field along with the target comment_id.
    """
    if 'username' not in session:
        return jsonify({'ok': False, 'error': 'Authentication required'}), 401
    
    try:
        data = request.get_json()
        comment_form = data.get('commentForm', {})
        comment_id = comment_form.get('comment_id')
        new_content = comment_form.get('comment')
        author = comment_form.get('author')  # VULNERABLE: trusting user-provided author
        
        if not comment_id or not new_content:
            return jsonify({'ok': False, 'error': 'Missing required fields'}), 400
        
        if comment_id not in comments:
            return jsonify({'ok': False, 'error': 'Comment not found'}), 404
        
        # VULNERABLE: Authorization check uses user-provided 'author' field
        # instead of checking the actual comment's author from database
        if author == session['username']:
            # Bug: Should be checking comments[comment_id]['author'] == session['username']
            old_content = comments[comment_id]['content']
            comments[comment_id]['content'] = new_content
            return jsonify({
                'ok': True, 
                'message': 'Comment updated successfully',
                'previous_content': old_content,
                'new_content': new_content
            })
        else:
            return jsonify({'ok': False, 'error': 'You can only update your own comments'}), 403
            
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 400


@app.route('/api/comments.remove', methods=['POST'])
def api_comments_remove():
    """
    VULNERABLE: Same authorization bypass as comments.update
    """
    if 'username' not in session:
        return jsonify({'ok': False, 'error': 'Authentication required'}), 401
    
    try:
        data = request.get_json()
        comment_form = data.get('commentForm', {})
        comment_id = comment_form.get('comment_id')
        author = comment_form.get('author')  # VULNERABLE: trusting user-provided author
        
        if not comment_id:
            return jsonify({'ok': False, 'error': 'Comment ID required'}), 400
        
        if comment_id not in comments:
            return jsonify({'ok': False, 'error': 'Comment not found'}), 404
        
        # VULNERABLE: Authorization check uses user-provided 'author' field
        if author == session['username']:
            deleted_comment = comments.pop(comment_id)
            return jsonify({
                'ok': True, 
                'message': 'Comment removed successfully',
                'deleted_content': deleted_comment['content']
            })
        else:
            return jsonify({'ok': False, 'error': 'You can only remove your own comments'}), 403
            
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 400


@app.route('/api/comments.get', methods=['GET'])
def api_comments_get():
    """
    VULNERABLE: Authorization bypass - trusts user-provided author parameter
    Allows reading private comments by providing any username as author
    """
    comment_id = request.args.get('comment_id')
    author = request.args.get('author')  # VULNERABLE: trusting user-provided author
    
    if not comment_id:
        return jsonify({'ok': False, 'error': 'Comment ID required'}), 400
    
    if comment_id not in comments:
        return jsonify({'ok': False, 'error': 'Comment not found'}), 404
    
    comment = comments[comment_id]
    
    # VULNERABLE: For private comments, checks if user-provided 'author' matches
    # the comment's author, instead of checking session username
    if comment['is_private']:
        if author == comment['author']:
            # Bug: Should check session['username'] == comment['author']
            return jsonify({
                'ok': True,
                'comment': {
                    'id': comment['id'],
                    'author': comment['author'],
                    'content': comment['content'],
                    'is_private': comment['is_private']
                }
            })
        else:
            return jsonify({'ok': False, 'error': 'Access denied: Private comment'}), 403
    else:
        return jsonify({
            'ok': True,
            'comment': {
                'id': comment['id'],
                'author': comment['author'],
                'content': comment['content'],
                'is_private': comment['is_private']
            }
        })


if __name__ == '__main__':
    app.run(debug=True)
