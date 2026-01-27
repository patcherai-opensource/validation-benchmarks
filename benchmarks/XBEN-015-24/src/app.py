# encoding=utf8
# Pimcore Asset Manager - Internal CMS Administration Panel

from flask import Flask, request, jsonify
import sqlite3
import os
import sys
import json

import logging

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

DATABASE = 'assets.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with asset data"""
    # Read flag from secret.txt or environment
    try:
        with open('secret.txt') as f:
            flag = f.read().strip()
            if flag == '@FLAG@':
                flag = os.getenv('FLAG', 'FLAG{default-flag}')
    except FileNotFoundError:
        flag = os.getenv('FLAG', 'FLAG{default-flag}')
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Create assets table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS assets (
            id INTEGER PRIMARY KEY,
            filename TEXT NOT NULL,
            filepath TEXT NOT NULL,
            mimetype TEXT,
            filesize INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create system_config table (stores the flag)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_config (
            id INTEGER PRIMARY KEY,
            config_key TEXT NOT NULL,
            config_value TEXT NOT NULL
        )
    ''')
    
    # Clear tables for fresh start
    cursor.execute('DELETE FROM assets')
    cursor.execute('DELETE FROM system_config')
    
    # Insert sample assets
    assets = [
        (1, 'logo.png', '/var/www/assets/images/logo.png', 'image/png', 45678),
        (2, 'banner.jpg', '/var/www/assets/images/banner.jpg', 'image/jpeg', 128456),
        (3, 'document.pdf', '/var/www/assets/documents/document.pdf', 'application/pdf', 256789),
        (4, 'styles.css', '/var/www/assets/css/styles.css', 'text/css', 12345),
        (5, 'script.js', '/var/www/assets/js/script.js', 'application/javascript', 8765),
        (6, 'backup.zip', '/var/www/assets/archive/backup.zip', 'application/zip', 987654),
        (7, 'config.xml', '/var/www/assets/config/config.xml', 'application/xml', 4567),
        (8, 'readme.txt', '/var/www/assets/docs/readme.txt', 'text/plain', 2345),
    ]
    
    cursor.executemany(
        'INSERT INTO assets (id, filename, filepath, mimetype, filesize) VALUES (?, ?, ?, ?, ?)',
        assets
    )
    
    # Insert system configuration including the flag
    configs = [
        (1, 'site_name', 'Pimcore CMS'),
        (2, 'version', '10.5.20'),
        (3, 'admin_secret', flag),
        (4, 'debug_mode', 'false'),
        (5, 'max_upload_size', '10485760'),
    ]
    
    cursor.executemany(
        'INSERT INTO system_config (id, config_key, config_value) VALUES (?, ?, ?)',
        configs
    )
    
    conn.commit()
    conn.close()


@app.route('/')
def index():
    return '''<!DOCTYPE html>
<html>
<head>
    <title>Pimcore - Asset Management</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: #3b5998; color: white; padding: 20px; margin-bottom: 20px; }
        .header h1 { margin: 0; }
        .nav { background: #2d4373; padding: 10px 20px; }
        .nav a { color: white; text-decoration: none; margin-right: 20px; }
        .panel { background: white; padding: 20px; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .btn { display: inline-block; padding: 10px 20px; background: #3b5998; color: white; text-decoration: none; border-radius: 4px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #f8f9fa; }
        .info { color: #666; font-size: 0.9em; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Pimcore Asset Manager</h1>
            <p>Digital Asset Management System v10.5.20</p>
        </div>
        <div class="nav">
            <a href="/">Dashboard</a>
            <a href="/admin/assets">Assets</a>
            <a href="/admin/assets/download-as-zip">Download Manager</a>
        </div>
        <div class="panel">
            <h2>Welcome to Pimcore Asset Manager</h2>
            <p>Manage your digital assets efficiently with our enterprise-grade CMS.</p>
            <p><a class="btn" href="/admin/assets">Browse Assets</a></p>
            <p class="info">Logged in as: admin@example.com</p>
        </div>
    </div>
</body>
</html>'''


@app.route('/admin/assets')
def list_assets():
    """List all assets in the system"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, filename, filepath, mimetype, filesize FROM assets ORDER BY id')
    assets = cursor.fetchall()
    conn.close()
    
    rows = ''
    for asset in assets:
        rows += '<tr><td><input type="checkbox" name="asset" value="{0}"></td><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td><td>{4}</td></tr>'.format(
            asset['id'], asset['filename'], asset['filepath'], asset['mimetype'], asset['filesize']
        )
    
    return '''<!DOCTYPE html>
<html>
<head>
    <title>Pimcore - Asset List</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: #3b5998; color: white; padding: 20px; margin-bottom: 20px; }}
        .header h1 {{ margin: 0; }}
        .nav {{ background: #2d4373; padding: 10px 20px; }}
        .nav a {{ color: white; text-decoration: none; margin-right: 20px; }}
        .panel {{ background: white; padding: 20px; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        .btn {{ display: inline-block; padding: 10px 20px; background: #3b5998; color: white; text-decoration: none; border-radius: 4px; border: none; cursor: pointer; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #f8f9fa; }}
        .actions {{ margin-top: 20px; }}
        .info {{ color: #666; font-size: 0.9em; margin-top: 10px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Pimcore Asset Manager</h1>
            <p>Digital Asset Management System v10.5.20</p>
        </div>
        <div class="nav">
            <a href="/">Dashboard</a>
            <a href="/admin/assets">Assets</a>
            <a href="/admin/assets/download-as-zip">Download Manager</a>
        </div>
        <div class="panel">
            <h2>Asset Library</h2>
            <p>Select assets to download as ZIP archive</p>
            <form action="/admin/assets/download-as-zip-add-files" method="GET">
                <table>
                    <thead>
                        <tr>
                            <th>Select</th>
                            <th>ID</th>
                            <th>Filename</th>
                            <th>Path</th>
                            <th>Type</th>
                            <th>Size</th>
                        </tr>
                    </thead>
                    <tbody>
                        {0}
                    </tbody>
                </table>
                <div class="actions">
                    <p class="info">Enter asset IDs (comma-separated) for bulk download:</p>
                    <input type="text" name="selectedIds" placeholder="e.g., 1,2,3" style="padding: 10px; width: 300px; margin-right: 10px;">
                    <button type="submit" class="btn">Download Selected as ZIP</button>
                </div>
            </form>
        </div>
    </div>
</body>
</html>'''.format(rows)


@app.route('/admin/assets/download-as-zip')
def download_zip_page():
    """Download manager page"""
    return '''<!DOCTYPE html>
<html>
<head>
    <title>Pimcore - Download Manager</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: #3b5998; color: white; padding: 20px; margin-bottom: 20px; }
        .header h1 { margin: 0; }
        .nav { background: #2d4373; padding: 10px 20px; }
        .nav a { color: white; text-decoration: none; margin-right: 20px; }
        .panel { background: white; padding: 20px; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .btn { display: inline-block; padding: 10px 20px; background: #3b5998; color: white; text-decoration: none; border-radius: 4px; border: none; cursor: pointer; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input[type="text"] { padding: 10px; width: 400px; border: 1px solid #ddd; border-radius: 4px; }
        .info { color: #666; font-size: 0.9em; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Pimcore Asset Manager</h1>
            <p>Digital Asset Management System v10.5.20</p>
        </div>
        <div class="nav">
            <a href="/">Dashboard</a>
            <a href="/admin/assets">Assets</a>
            <a href="/admin/assets/download-as-zip">Download Manager</a>
        </div>
        <div class="panel">
            <h2>Download Assets as ZIP</h2>
            <p>Enter the asset IDs you want to download as a ZIP archive.</p>
            <form action="/admin/assets/download-as-zip-add-files" method="GET">
                <div class="form-group">
                    <label for="selectedIds">Selected Asset IDs:</label>
                    <input type="text" id="selectedIds" name="selectedIds" placeholder="Enter comma-separated IDs (e.g., 1,2,3)">
                </div>
                <button type="submit" class="btn">Prepare Download</button>
            </form>
            <p class="info">Note: You can find asset IDs in the <a href="/admin/assets">Asset Library</a></p>
        </div>
    </div>
</body>
</html>'''


@app.route('/admin/assets/download-as-zip-add-files')
def download_as_zip_add_files():
    """
    VULNERABLE ENDPOINT - SQL Injection via selectedIds parameter
    Mirrors CVE-2023-2338 in Pimcore AssetController
    """
    selected_ids = request.args.get('selectedIds', '')
    
    if not selected_ids:
        return jsonify({
            'success': False,
            'message': 'No assets selected. Please provide selectedIds parameter.'
        }), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # VULNERABLE: Direct string concatenation without proper escaping
        # This mirrors the CVE where selectedIds are not properly quoted
        ids_list = selected_ids.split(',')
        condition = 'id IN (' + ','.join(ids_list) + ')'
        
        query = 'SELECT id, filename, filepath, mimetype, filesize FROM assets WHERE ' + condition
        
        logging.info("Executing query: %s", query)
        
        cursor.execute(query)
        assets = cursor.fetchall()
        
        result = {
            'success': True,
            'message': 'Assets prepared for download',
            'query_info': 'Selected {} asset(s)'.format(len(assets)),
            'assets': [
                {
                    'id': a['id'],
                    'filename': a['filename'],
                    'filepath': a['filepath'],
                    'mimetype': a['mimetype'],
                    'filesize': a['filesize']
                }
                for a in assets
            ]
        }
        
        conn.close()
        return jsonify(result)
        
    except sqlite3.Error as e:
        conn.close()
        # Return detailed error message (helps with blind SQL injection)
        return jsonify({
            'success': False,
            'message': 'Database error occurred',
            'error': str(e)
        }), 500


@app.route('/api/system/info')
def system_info():
    """Public system information endpoint"""
    return jsonify({
        'application': 'Pimcore Asset Manager',
        'version': '10.5.20',
        'database': 'SQLite',
        'endpoints': [
            '/admin/assets',
            '/admin/assets/download-as-zip',
            '/admin/assets/download-as-zip-add-files'
        ]
    })


# Initialize database on startup
init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
