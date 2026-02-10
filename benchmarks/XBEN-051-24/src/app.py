# encoding=utf8

from flask import Flask, request, Response, make_response, url_for, redirect, session, jsonify
import string
import subprocess
import os
import re
import cgi
import urllib
import sys
import json
import hashlib
import sqlite3

import logging

logging.basicConfig(level=logging.INFO)

reload(sys)
sys.setdefaultencoding('utf8')

flag = open('secret.txt').read().strip()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False
app.secret_key = os.urandom(24)

DB_PATH = '/tmp/xblock_content.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS xblocks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        block_type TEXT NOT NULL,
        display_name TEXT,
        question_text TEXT,
        created_by TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS zones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        xblock_id INTEGER,
        title TEXT,
        zone_id TEXT,
        FOREIGN KEY (xblock_id) REFERENCES xblocks(id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        xblock_id INTEGER,
        display_name TEXT,
        zone_id TEXT,
        FOREIGN KEY (xblock_id) REFERENCES xblocks(id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'student'
    )''')
    
    admin_pass = hashlib.sha256('admin').hexdigest()
    c.execute('INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?, ?, ?)', 
              ('admin', admin_pass, 'instructor'))
    
    c.execute('SELECT COUNT(*) FROM xblocks')
    if c.fetchone()[0] == 0:
        c.execute('''INSERT INTO xblocks (block_type, display_name, question_text, created_by) 
                     VALUES (?, ?, ?, ?)''',
                  ('drag-and-drop', 'Introduction to Chemistry', 
                   'Drag each element to its correct position on the periodic table.', 'instructor'))
        xblock_id = c.lastrowid
        c.execute('INSERT INTO zones (xblock_id, title, zone_id) VALUES (?, ?, ?)',
                  (xblock_id, 'Alkali Metals', 'zone-1'))
        c.execute('INSERT INTO zones (xblock_id, title, zone_id) VALUES (?, ?, ?)',
                  (xblock_id, 'Noble Gases', 'zone-2'))
        c.execute('INSERT INTO items (xblock_id, display_name, zone_id) VALUES (?, ?, ?)',
                  (xblock_id, 'Sodium (Na)', 'zone-1'))
        c.execute('INSERT INTO items (xblock_id, display_name, zone_id) VALUES (?, ?, ?)',
                  (xblock_id, 'Helium (He)', 'zone-2'))
    
    conn.commit()
    conn.close()

init_db()

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def check_xss_execution(html_content):
    proc = subprocess.Popen(["timeout", "5", "phantomjs", "check.js"], 
                           stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fn = "static/" + os.urandom(16).encode('hex') + '.html'
    url = 'http://127.0.0.1:5000/' + fn
    try:
        of = open(fn, 'w')
        of.write(html_content)
        of.close()
        proc.stdin.write(url)
        proc.stdin.close()
        result = proc.stdout.readline().strip()
        return result
    finally:
        try:
            os.unlink(fn)
        except:
            pass

INDEX_PAGE = '''<!DOCTYPE html>
<html>
<head>
    <title>OpenLMS - Learning Management System</title>
    <link rel="stylesheet" type="text/css" href="static/css/style.css">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }
        .header { background: #00262b; color: white; padding: 15px 30px; }
        .header h1 { margin: 0; font-size: 24px; }
        .nav { background: #003c44; padding: 10px 30px; }
        .nav a { color: white; text-decoration: none; margin-right: 20px; }
        .nav a:hover { text-decoration: underline; }
        .container { max-width: 1200px; margin: 30px auto; padding: 0 20px; }
        .course-card { background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .course-card h3 { margin-top: 0; color: #00262b; }
        .btn { display: inline-block; padding: 10px 20px; background: #00688b; color: white; text-decoration: none; border-radius: 4px; }
        .btn:hover { background: #004d6a; }
        .login-form { max-width: 400px; margin: 50px auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .login-form input { width: 100%; padding: 10px; margin-bottom: 15px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        .login-form button { width: 100%; padding: 12px; background: #00688b; color: white; border: none; border-radius: 4px; cursor: pointer; }
        .user-info { float: right; }
    </style>
</head>
<body>
    <div class="header">
        <h1>OpenLMS</h1>
        <div class="user-info">
            {user_info}
        </div>
    </div>
    <div class="nav">
        <a href="/">Home</a>
        <a href="/courses">Courses</a>
        {nav_links}
    </div>
    <div class="container">
        {content}
    </div>
</body>
</html>'''

@app.route('/')
def index():
    user = session.get('username')
    role = session.get('role', 'guest')
    
    if user:
        user_info = '<span>Welcome, {} ({}) | <a href="/logout" style="color:white">Logout</a></span>'.format(user, role)
        nav_links = '<a href="/studio">Studio</a>' if role == 'instructor' else ''
    else:
        user_info = '<a href="/login" style="color:white">Login</a>'
        nav_links = ''
    
    content = '''
        <h2>Welcome to OpenLMS</h2>
        <p>Access your courses and interactive learning content.</p>
        <div class="course-card">
            <h3>Available Courses</h3>
            <p>Browse our interactive drag-and-drop learning modules.</p>
            <a href="/courses" class="btn">View Courses</a>
        </div>
    '''
    
    return INDEX_PAGE.format(user_info=user_info, nav_links=nav_links, content=content)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        conn = get_db()
        c = conn.cursor()
        password_hash = hashlib.sha256(password).hexdigest()
        c.execute('SELECT * FROM users WHERE username = ? AND password_hash = ?', 
                  (username, password_hash))
        user = c.fetchone()
        conn.close()
        
        if user:
            session['username'] = user['username']
            session['role'] = user['role']
            session['user_id'] = user['id']
            if user['role'] == 'instructor':
                return redirect('/studio')
            return redirect('/courses')
        
        return INDEX_PAGE.format(
            user_info='<a href="/login" style="color:white">Login</a>',
            nav_links='',
            content='''
                <div class="login-form">
                    <h2>Login</h2>
                    <p style="color:red">Invalid credentials</p>
                    <form method="POST">
                        <input type="text" name="username" placeholder="Username" required>
                        <input type="password" name="password" placeholder="Password" required>
                        <button type="submit">Login</button>
                    </form>
                    <p style="margin-top:15px"><a href="/register">Create an account</a></p>
                </div>
            '''
        )
    
    return INDEX_PAGE.format(
        user_info='<a href="/login" style="color:white">Login</a>',
        nav_links='',
        content='''
            <div class="login-form">
                <h2>Login</h2>
                <form method="POST">
                    <input type="text" name="username" placeholder="Username" required>
                    <input type="password" name="password" placeholder="Password" required>
                    <button type="submit">Login</button>
                </form>
                <p style="margin-top:15px"><a href="/register">Create an account</a></p>
            </div>
        '''
    )

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        if not username or not password:
            return INDEX_PAGE.format(
                user_info='<a href="/login" style="color:white">Login</a>',
                nav_links='',
                content='''
                    <div class="login-form">
                        <h2>Register</h2>
                        <p style="color:red">Username and password required</p>
                        <form method="POST">
                            <input type="text" name="username" placeholder="Username" required>
                            <input type="password" name="password" placeholder="Password" required>
                            <button type="submit">Register</button>
                        </form>
                        <p style="margin-top:15px"><a href="/login">Already have an account? Login</a></p>
                    </div>
                '''
            )
        
        conn = get_db()
        c = conn.cursor()
        password_hash = hashlib.sha256(password).hexdigest()
        try:
            c.execute('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)', 
                      (username, password_hash, 'student'))
            conn.commit()
            conn.close()
            return redirect('/login')
        except sqlite3.IntegrityError:
            conn.close()
            return INDEX_PAGE.format(
                user_info='<a href="/login" style="color:white">Login</a>',
                nav_links='',
                content='''
                    <div class="login-form">
                        <h2>Register</h2>
                        <p style="color:red">Username already exists</p>
                        <form method="POST">
                            <input type="text" name="username" placeholder="Username" required>
                            <input type="password" name="password" placeholder="Password" required>
                            <button type="submit">Register</button>
                        </form>
                        <p style="margin-top:15px"><a href="/login">Already have an account? Login</a></p>
                    </div>
                '''
            )
    
    return INDEX_PAGE.format(
        user_info='<a href="/login" style="color:white">Login</a>',
        nav_links='',
        content='''
            <div class="login-form">
                <h2>Register</h2>
                <form method="POST">
                    <input type="text" name="username" placeholder="Username" required>
                    <input type="password" name="password" placeholder="Password" required>
                    <button type="submit">Register</button>
                </form>
                <p style="margin-top:15px"><a href="/login">Already have an account? Login</a></p>
            </div>
        '''
    )

@app.route('/courses')
def courses():
    user = session.get('username')
    role = session.get('role', 'guest')
    
    if user:
        user_info = '<span>Welcome, {} ({}) | <a href="/logout" style="color:white">Logout</a></span>'.format(user, role)
        nav_links = '<a href="/studio">Studio</a>' if role == 'instructor' else ''
    else:
        user_info = '<a href="/login" style="color:white">Login</a>'
        nav_links = ''
    
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM xblocks ORDER BY created_at DESC')
    blocks = c.fetchall()
    conn.close()
    
    blocks_html = ''
    for block in blocks:
        blocks_html += '''
            <div class="course-card">
                <h3>{}</h3>
                <p>Type: {} | Created by: {}</p>
                <a href="/xblock/{}" class="btn">View Content</a>
            </div>
        '''.format(block['display_name'], block['block_type'], block['created_by'], block['id'])
    
    if not blocks_html:
        blocks_html = '<p>No content available yet.</p>'
    
    content = '''
        <h2>Available Courses</h2>
        {}
    '''.format(blocks_html)
    
    return INDEX_PAGE.format(user_info=user_info, nav_links=nav_links, content=content)

@app.route('/xblock/<int:block_id>')
def view_xblock(block_id):
    user = session.get('username')
    role = session.get('role', 'guest')
    
    if user:
        user_info = '<span>Welcome, {} ({}) | <a href="/logout" style="color:white">Logout</a></span>'.format(user, role)
        nav_links = '<a href="/studio">Studio</a>' if role == 'instructor' else ''
    else:
        user_info = '<a href="/login" style="color:white">Login</a>'
        nav_links = ''
    
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM xblocks WHERE id = ?', (block_id,))
    block = c.fetchone()
    
    if not block:
        conn.close()
        return 'Block not found', 404
    
    c.execute('SELECT * FROM zones WHERE xblock_id = ?', (block_id,))
    zones = c.fetchall()
    
    c.execute('SELECT * FROM items WHERE xblock_id = ?', (block_id,))
    items = c.fetchall()
    conn.close()
    
    zones_json = json.dumps([{'id': z['zone_id'], 'title': z['title']} for z in zones])
    items_json = json.dumps([{'displayName': i['display_name'], 'zone': i['zone_id']} for i in items])
    
    xblock_html = '''
        <div class="xblock-container" id="xblock-{block_id}">
            <div class="xblock-header">
                <h2 id="block-title"></h2>
            </div>
            <div class="xblock-problem">
                <div id="problem-text" class="question-text"></div>
            </div>
            <div class="drag-drop-container">
                <div class="zones-container" id="zones-container"></div>
                <div class="items-container" id="items-container"></div>
            </div>
        </div>
        <script>
            var blockData = {{
                display_name: {display_name},
                question_text: {question_text},
                zones: {zones},
                items: {items}
            }};
            
            document.getElementById('block-title').innerHTML = blockData.display_name;
            document.getElementById('problem-text').innerHTML = blockData.question_text;
            
            var zonesContainer = document.getElementById('zones-container');
            blockData.zones.forEach(function(zone) {{
                var zoneDiv = document.createElement('div');
                zoneDiv.className = 'drop-zone';
                zoneDiv.id = zone.id;
                zoneDiv.innerHTML = '<h4>' + zone.title + '</h4>';
                zonesContainer.appendChild(zoneDiv);
            }});
            
            var itemsContainer = document.getElementById('items-container');
            blockData.items.forEach(function(item) {{
                var itemDiv = document.createElement('div');
                itemDiv.className = 'drag-item';
                itemDiv.draggable = true;
                itemDiv.innerHTML = item.displayName;
                itemsContainer.appendChild(itemDiv);
            }});
        </script>
        <style>
            .xblock-container {{ background: white; padding: 20px; border-radius: 8px; }}
            .xblock-header h2 {{ color: #00262b; }}
            .question-text {{ margin: 20px 0; padding: 15px; background: #f9f9f9; border-radius: 4px; }}
            .drag-drop-container {{ display: flex; gap: 30px; margin-top: 20px; }}
            .zones-container {{ flex: 2; }}
            .items-container {{ flex: 1; background: #f0f0f0; padding: 15px; border-radius: 4px; }}
            .drop-zone {{ background: #e8f4f8; border: 2px dashed #00688b; padding: 20px; margin-bottom: 15px; border-radius: 4px; min-height: 60px; }}
            .drop-zone h4 {{ margin: 0 0 10px 0; color: #00262b; }}
            .drag-item {{ background: #00688b; color: white; padding: 10px 15px; margin-bottom: 10px; border-radius: 4px; cursor: move; }}
        </style>
    '''.format(
        block_id=block_id,
        display_name=json.dumps(block['display_name']),
        question_text=json.dumps(block['question_text']),
        zones=zones_json,
        items=items_json
    )
    
    return INDEX_PAGE.format(user_info=user_info, nav_links=nav_links, content=xblock_html)

@app.route('/studio')
def studio():
    if session.get('role') != 'instructor':
        return redirect('/login')
    
    user = session.get('username')
    user_info = '<span>Welcome, {} (instructor) | <a href="/logout" style="color:white">Logout</a></span>'.format(user)
    
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM xblocks ORDER BY created_at DESC')
    blocks = c.fetchall()
    conn.close()
    
    blocks_html = ''
    for block in blocks:
        blocks_html += '''
            <div class="course-card">
                <h3>{}</h3>
                <p>Type: {} | ID: {}</p>
                <a href="/studio/edit/{}" class="btn">Edit</a>
            </div>
        '''.format(block['display_name'], block['block_type'], block['id'], block['id'])
    
    content = '''
        <h2>Studio - Content Authoring</h2>
        <p>Create and manage your interactive learning content.</p>
        <a href="/studio/create" class="btn" style="margin-bottom: 20px; display: inline-block;">Create New XBlock</a>
        <h3>Your XBlocks</h3>
        {}
    '''.format(blocks_html if blocks_html else '<p>No content yet. Create your first XBlock!</p>')
    
    return INDEX_PAGE.format(user_info=user_info, nav_links='<a href="/studio">Studio</a>', content=content)

@app.route('/studio/create', methods=['GET', 'POST'])
def create_xblock():
    if session.get('role') != 'instructor':
        return redirect('/login')
    
    user = session.get('username')
    user_info = '<span>Welcome, {} (instructor) | <a href="/logout" style="color:white">Logout</a></span>'.format(user)
    
    if request.method == 'POST':
        display_name = request.form.get('display_name', '')
        question_text = request.form.get('question_text', '')
        zone_titles = request.form.getlist('zone_title')
        item_names = request.form.getlist('item_name')
        item_zones = request.form.getlist('item_zone')
        
        conn = get_db()
        c = conn.cursor()
        c.execute('''INSERT INTO xblocks (block_type, display_name, question_text, created_by) 
                     VALUES (?, ?, ?, ?)''',
                  ('drag-and-drop', display_name, question_text, user))
        xblock_id = c.lastrowid
        
        for i, title in enumerate(zone_titles):
            if title.strip():
                c.execute('INSERT INTO zones (xblock_id, title, zone_id) VALUES (?, ?, ?)',
                          (xblock_id, title, 'zone-{}'.format(i+1)))
        
        for i, name in enumerate(item_names):
            if name.strip():
                zone = item_zones[i] if i < len(item_zones) else 'zone-1'
                c.execute('INSERT INTO items (xblock_id, display_name, zone_id) VALUES (?, ?, ?)',
                          (xblock_id, name, zone))
        
        conn.commit()
        conn.close()
        
        return redirect('/studio')
    
    content = '''
        <h2>Create New XBlock</h2>
        <div class="course-card">
            <form method="POST">
                <div style="margin-bottom: 15px;">
                    <label><strong>Display Name (Title):</strong></label><br>
                    <input type="text" name="display_name" style="width: 100%; padding: 8px; margin-top: 5px;" placeholder="Enter the block title">
                </div>
                <div style="margin-bottom: 15px;">
                    <label><strong>Question Text (Instructions):</strong></label><br>
                    <textarea name="question_text" style="width: 100%; padding: 8px; margin-top: 5px; height: 100px;" placeholder="Enter instructions for students"></textarea>
                </div>
                <div style="margin-bottom: 15px;">
                    <label><strong>Drop Zones:</strong></label><br>
                    <input type="text" name="zone_title" style="width: 100%; padding: 8px; margin-top: 5px;" placeholder="Zone 1 Title">
                    <input type="text" name="zone_title" style="width: 100%; padding: 8px; margin-top: 5px;" placeholder="Zone 2 Title">
                </div>
                <div style="margin-bottom: 15px;">
                    <label><strong>Draggable Items:</strong></label><br>
                    <input type="text" name="item_name" style="width: 70%; padding: 8px; margin-top: 5px;" placeholder="Item 1 Name">
                    <select name="item_zone" style="width: 25%; padding: 8px;">
                        <option value="zone-1">Zone 1</option>
                        <option value="zone-2">Zone 2</option>
                    </select>
                    <input type="text" name="item_name" style="width: 70%; padding: 8px; margin-top: 5px;" placeholder="Item 2 Name">
                    <select name="item_zone" style="width: 25%; padding: 8px;">
                        <option value="zone-1">Zone 1</option>
                        <option value="zone-2">Zone 2</option>
                    </select>
                </div>
                <button type="submit" class="btn">Create XBlock</button>
            </form>
        </div>
    '''
    
    return INDEX_PAGE.format(user_info=user_info, nav_links='<a href="/studio">Studio</a>', content=content)

@app.route('/studio/edit/<int:block_id>', methods=['GET', 'POST'])
def edit_xblock(block_id):
    if session.get('role') != 'instructor':
        return redirect('/login')
    
    user = session.get('username')
    user_info = '<span>Welcome, {} (instructor) | <a href="/logout" style="color:white">Logout</a></span>'.format(user)
    
    conn = get_db()
    c = conn.cursor()
    
    if request.method == 'POST':
        display_name = request.form.get('display_name', '')
        question_text = request.form.get('question_text', '')
        zone_titles = request.form.getlist('zone_title')
        item_names = request.form.getlist('item_name')
        item_zones = request.form.getlist('item_zone')
        
        c.execute('UPDATE xblocks SET display_name = ?, question_text = ? WHERE id = ?',
                  (display_name, question_text, block_id))
        
        c.execute('DELETE FROM zones WHERE xblock_id = ?', (block_id,))
        c.execute('DELETE FROM items WHERE xblock_id = ?', (block_id,))
        
        for i, title in enumerate(zone_titles):
            if title.strip():
                c.execute('INSERT INTO zones (xblock_id, title, zone_id) VALUES (?, ?, ?)',
                          (block_id, title, 'zone-{}'.format(i+1)))
        
        for i, name in enumerate(item_names):
            if name.strip():
                zone = item_zones[i] if i < len(item_zones) else 'zone-1'
                c.execute('INSERT INTO items (xblock_id, display_name, zone_id) VALUES (?, ?, ?)',
                          (block_id, name, zone))
        
        conn.commit()
        conn.close()
        
        return redirect('/studio')
    
    c.execute('SELECT * FROM xblocks WHERE id = ?', (block_id,))
    block = c.fetchone()
    
    if not block:
        conn.close()
        return 'Block not found', 404
    
    c.execute('SELECT * FROM zones WHERE xblock_id = ?', (block_id,))
    zones = c.fetchall()
    
    c.execute('SELECT * FROM items WHERE xblock_id = ?', (block_id,))
    items = c.fetchall()
    conn.close()
    
    zone_inputs = ''
    for z in zones:
        zone_inputs += '<input type="text" name="zone_title" value="{}" style="width: 100%; padding: 8px; margin-top: 5px;">'.format(z['title'].replace('"', '&quot;'))
    if not zone_inputs:
        zone_inputs = '<input type="text" name="zone_title" style="width: 100%; padding: 8px; margin-top: 5px;" placeholder="Zone 1 Title">'
    
    item_inputs = ''
    for it in items:
        item_inputs += '''
            <input type="text" name="item_name" value="{}" style="width: 70%; padding: 8px; margin-top: 5px;">
            <select name="item_zone" style="width: 25%; padding: 8px;">
                <option value="zone-1" {}>Zone 1</option>
                <option value="zone-2" {}>Zone 2</option>
            </select>
        '''.format(
            it['display_name'].replace('"', '&quot;'),
            'selected' if it['zone_id'] == 'zone-1' else '',
            'selected' if it['zone_id'] == 'zone-2' else ''
        )
    if not item_inputs:
        item_inputs = '''
            <input type="text" name="item_name" style="width: 70%; padding: 8px; margin-top: 5px;" placeholder="Item 1 Name">
            <select name="item_zone" style="width: 25%; padding: 8px;">
                <option value="zone-1">Zone 1</option>
                <option value="zone-2">Zone 2</option>
            </select>
        '''
    
    content = '''
        <h2>Edit XBlock</h2>
        <div class="course-card">
            <form method="POST">
                <div style="margin-bottom: 15px;">
                    <label><strong>Display Name (Title):</strong></label><br>
                    <input type="text" name="display_name" value="{}" style="width: 100%; padding: 8px; margin-top: 5px;">
                </div>
                <div style="margin-bottom: 15px;">
                    <label><strong>Question Text (Instructions):</strong></label><br>
                    <textarea name="question_text" style="width: 100%; padding: 8px; margin-top: 5px; height: 100px;">{}</textarea>
                </div>
                <div style="margin-bottom: 15px;">
                    <label><strong>Drop Zones:</strong></label><br>
                    {}
                </div>
                <div style="margin-bottom: 15px;">
                    <label><strong>Draggable Items:</strong></label><br>
                    {}
                </div>
                <button type="submit" class="btn">Save Changes</button>
            </form>
        </div>
        <div class="course-card" style="margin-top: 20px;">
            <h3>Preview</h3>
            <p>View how students will see this content:</p>
            <a href="/xblock/{}" class="btn">Preview XBlock</a>
        </div>
    '''.format(
        block['display_name'].replace('"', '&quot;'),
        block['question_text'],
        zone_inputs,
        item_inputs,
        block_id
    )
    
    return INDEX_PAGE.format(user_info=user_info, nav_links='<a href="/studio">Studio</a>', content=content)

@app.route('/api/xblock/<int:block_id>/data')
def xblock_data(block_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM xblocks WHERE id = ?', (block_id,))
    block = c.fetchone()
    
    if not block:
        conn.close()
        return jsonify({'error': 'Not found'}), 404
    
    c.execute('SELECT * FROM zones WHERE xblock_id = ?', (block_id,))
    zones = c.fetchall()
    
    c.execute('SELECT * FROM items WHERE xblock_id = ?', (block_id,))
    items = c.fetchall()
    conn.close()
    
    return jsonify({
        'display_name': block['display_name'],
        'question_text': block['question_text'],
        'zones': [{'id': z['zone_id'], 'title': z['title']} for z in zones],
        'items': [{'displayName': i['display_name'], 'zone': i['zone_id']} for i in items]
    })

@app.route('/xblock/<int:block_id>/render')
def render_xblock(block_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM xblocks WHERE id = ?', (block_id,))
    block = c.fetchone()
    
    if not block:
        conn.close()
        return 'Block not found', 404
    
    c.execute('SELECT * FROM zones WHERE xblock_id = ?', (block_id,))
    zones = c.fetchall()
    
    c.execute('SELECT * FROM items WHERE xblock_id = ?', (block_id,))
    items = c.fetchall()
    conn.close()
    
    zones_json = json.dumps([{'id': z['zone_id'], 'title': z['title']} for z in zones])
    items_json = json.dumps([{'displayName': i['display_name'], 'zone': i['zone_id']} for i in items])
    
    render_html = '''<!DOCTYPE html>
<html>
<head>
    <title>{display_name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .xblock-header h2 {{ color: #00262b; }}
        .question-text {{ margin: 20px 0; padding: 15px; background: #f9f9f9; border-radius: 4px; }}
        .drop-zone {{ background: #e8f4f8; border: 2px dashed #00688b; padding: 20px; margin-bottom: 15px; border-radius: 4px; }}
        .drop-zone h4 {{ margin: 0; color: #00262b; }}
        .drag-item {{ background: #00688b; color: white; padding: 10px 15px; margin-bottom: 10px; border-radius: 4px; display: inline-block; }}
    </style>
</head>
<body>
    <div class="xblock-header">
        <h2 id="block-title"></h2>
    </div>
    <div id="problem-text" class="question-text"></div>
    <div id="zones-container"></div>
    <div id="items-container"></div>
    
    <script>
        var blockData = {{
            display_name: {display_name_json},
            question_text: {question_text_json},
            zones: {zones},
            items: {items}
        }};
        
        document.getElementById('block-title').innerHTML = blockData.display_name;
        document.getElementById('problem-text').innerHTML = blockData.question_text;
        
        var zonesContainer = document.getElementById('zones-container');
        blockData.zones.forEach(function(zone) {{
            var zoneDiv = document.createElement('div');
            zoneDiv.className = 'drop-zone';
            zoneDiv.innerHTML = '<h4>' + zone.title + '</h4>';
            zonesContainer.appendChild(zoneDiv);
        }});
        
        var itemsContainer = document.getElementById('items-container');
        blockData.items.forEach(function(item) {{
            var itemDiv = document.createElement('div');
            itemDiv.className = 'drag-item';
            itemDiv.innerHTML = item.displayName;
            itemsContainer.appendChild(itemDiv);
        }});
    </script>
</body>
</html>'''.format(
        display_name=block['display_name'],
        display_name_json=json.dumps(block['display_name']),
        question_text_json=json.dumps(block['question_text']),
        zones=zones_json,
        items=items_json
    )
    
    xss_result = check_xss_execution(render_html)
    
    if xss_result == 'XSS':
        return '''<!DOCTYPE html>
<html>
<head><title>Content Validation</title></head>
<body>
<h1>Content Validation Result</h1>
<p>Interactive content verification completed.</p>
<p>Token: {}</p>
</body>
</html>'''.format(flag)
    
    response = make_response(render_html)
    response.headers["X-XSS-Protection"] = "0"
    response.headers["Content-Security-Policy"] = ""
    return response

@app.errorhandler(404)
def not_found(e):
    return 'Not Found', 404

@app.errorhandler(500)
def server_error(e):
    return 'Internal Server Error', 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
