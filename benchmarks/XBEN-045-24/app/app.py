import os
import re
import json
import subprocess
import sqlite3
import uuid
import time
from flask import Flask, render_template, request, jsonify, redirect, url_for, g, send_from_directory

app = Flask(__name__)
app.secret_key = os.urandom(24)

DATABASE = '/app/data/medialib.db'
MEDIA_DIR = '/app/data/media'
LOGS_DIR = '/app/data/logs'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def init_db():
    os.makedirs(os.path.dirname(DATABASE), exist_ok=True)
    os.makedirs(MEDIA_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)
    db = sqlite3.connect(DATABASE)
    db.executescript('''
        CREATE TABLE IF NOT EXISTS media_items (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            artist TEXT DEFAULT '',
            album TEXT DEFAULT '',
            duration INTEGER DEFAULT 0,
            format TEXT DEFAULT 'mp3',
            filepath TEXT DEFAULT '',
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS processing_jobs (
            id TEXT PRIMARY KEY,
            media_id TEXT NOT NULL,
            action_template TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            output TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (media_id) REFERENCES media_items(id)
        );
        CREATE TABLE IF NOT EXISTS action_presets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            template TEXT NOT NULL,
            description TEXT DEFAULT ''
        );
    ''')
    # Insert default presets if none exist
    cursor = db.execute('SELECT COUNT(*) FROM action_presets')
    if cursor.fetchone()[0] == 0:
        db.executescript('''
            INSERT INTO action_presets (name, template, description)
            VALUES ('Log Metadata', 'echo "Processing: %(title)q by %(artist)q"', 'Log media metadata to output');
            INSERT INTO action_presets (name, template, description)
            VALUES ('Tag File', 'echo "Tagging %(filepath)q with artist=%(artist)q album=%(album)q"', 'Update file tags');
            INSERT INTO action_presets (name, template, description)
            VALUES ('Notify Complete', 'echo "Completed processing of %(title)q [%(format)s]"', 'Send completion notification');
            INSERT INTO action_presets (name, template, description)
            VALUES ('Archive Entry', 'echo "Archiving %(title)q (%(duration)s seconds) to library"', 'Archive to media library');
        ''')
    # Insert some sample media items
    cursor = db.execute('SELECT COUNT(*) FROM media_items')
    if cursor.fetchone()[0] == 0:
        db.executescript('''
            INSERT INTO media_items (id, title, artist, album, duration, format, filepath)
            VALUES ('a1b2c3d4', 'Midnight Serenade', 'The Echoes', 'Night Sessions', 245, 'mp3', '/app/data/media/a1b2c3d4.mp3');
            INSERT INTO media_items (id, title, artist, album, duration, format, filepath)
            VALUES ('e5f6a7b8', 'Ocean Waves', 'Calm Collective', 'Nature Sounds', 360, 'flac', '/app/data/media/e5f6a7b8.flac');
            INSERT INTO media_items (id, title, artist, album, duration, format, filepath)
            VALUES ('c9d0e1f2', 'Electric Dreams', 'Synthwave FM', 'Retro Future', 198, 'mp3', '/app/data/media/c9d0e1f2.mp3');
        ''')
    db.commit()
    db.close()


# --- Shell quoting utility ---
# Quote a string for safe use in shell commands.
# On this system we wrap in double quotes and escape internal double quotes.
def safe_shell_quote(s):
    s = str(s)
    if re.match(r'^[-_\w./]+$', s):
        return s
    return '"%s"' % s.replace('"', '\\"')


# --- Template expansion ---
# Template format: %(field_name)q for shell-quoted, %(field_name)s for raw string
TEMPLATE_RE = re.compile(r'%\((\w+)\)([qs])')


def expand_template(template, metadata):
    def replacer(match):
        field = match.group(1)
        fmt = match.group(2)
        value = metadata.get(field, '')
        if fmt == 'q':
            return safe_shell_quote(value)
        return str(value)
    return TEMPLATE_RE.sub(replacer, template)


# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/library')
def library():
    db = get_db()
    items = db.execute('SELECT * FROM media_items ORDER BY added_at DESC').fetchall()
    return render_template('library.html', items=items)


@app.route('/api/media', methods=['GET'])
def api_list_media():
    db = get_db()
    items = db.execute('SELECT * FROM media_items ORDER BY added_at DESC').fetchall()
    result = [dict(row) for row in items]
    return jsonify(result)


@app.route('/api/media/<item_id>', methods=['GET'])
def api_get_media(item_id):
    db = get_db()
    item = db.execute('SELECT * FROM media_items WHERE id = ?', (item_id,)).fetchone()
    if not item:
        return jsonify({'error': 'Media item not found'}), 404
    return jsonify(dict(item))


@app.route('/api/media', methods=['POST'])
def api_add_media():
    data = request.get_json(silent=True)
    if not data:
        data = request.form.to_dict()
    title = data.get('title', '').strip()
    if not title:
        return jsonify({'error': 'Title is required'}), 400
    item_id = uuid.uuid4().hex[:8]
    artist = data.get('artist', '')
    album = data.get('album', '')
    try:
        duration = int(data.get('duration', 0) or 0)
    except (ValueError, TypeError):
        duration = 0
    fmt = data.get('format', 'mp3')
    filepath = os.path.join(MEDIA_DIR, f'{item_id}.{fmt}')
    db = get_db()
    db.execute(
        'INSERT INTO media_items (id, title, artist, album, duration, format, filepath) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (item_id, title, artist, album, duration, fmt, filepath)
    )
    db.commit()
    return jsonify({'id': item_id, 'title': title, 'status': 'added'}), 201


@app.route('/presets')
def presets():
    db = get_db()
    items = db.execute('SELECT * FROM action_presets ORDER BY id').fetchall()
    return render_template('presets.html', presets=items)


@app.route('/api/presets', methods=['GET'])
def api_list_presets():
    db = get_db()
    items = db.execute('SELECT * FROM action_presets ORDER BY id').fetchall()
    return jsonify([dict(row) for row in items])


@app.route('/process', methods=['GET'])
def process_form():
    db = get_db()
    items = db.execute('SELECT * FROM media_items ORDER BY added_at DESC').fetchall()
    presets_list = db.execute('SELECT * FROM action_presets ORDER BY id').fetchall()
    return render_template('process.html', items=items, presets=presets_list)


@app.route('/api/process', methods=['POST'])
def api_process():
    data = request.get_json(silent=True)
    if not data:
        data = request.form.to_dict()

    media_id = str(data.get('media_id', '') or '').strip()
    preset_id = str(data.get('preset_id', '') or '').strip()
    action_template = str(data.get('action_template', '') or '').strip()

    if not media_id:
        return jsonify({'error': 'media_id is required'}), 400

    db = get_db()
    item = db.execute('SELECT * FROM media_items WHERE id = ?', (media_id,)).fetchone()
    if not item:
        return jsonify({'error': 'Media item not found'}), 404

    # Resolve the action template from preset or custom input
    if preset_id:
        preset = db.execute('SELECT * FROM action_presets WHERE id = ?', (preset_id,)).fetchone()
        if not preset:
            return jsonify({'error': 'Preset not found'}), 404
        action_template = preset['template']
    elif action_template:
        # Validate custom templates: must use template syntax, no raw command execution
        if not TEMPLATE_RE.search(action_template):
            return jsonify({'error': 'Template must contain at least one field expansion like %(field)q or %(field)s'}), 400
    else:
        return jsonify({'error': 'Either preset_id or action_template is required'}), 400

    metadata = dict(item)

    # Expand the template with metadata fields
    try:
        cmd = expand_template(action_template, metadata)
    except Exception as e:
        return jsonify({'error': 'Template expansion failed', 'details': str(e)}), 400

    # Execute the post-processing action
    job_id = uuid.uuid4().hex[:12]
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        output = result.stdout if result.stdout else result.stderr
        status = 'completed' if result.returncode == 0 else 'failed'
    except subprocess.TimeoutExpired:
        output = 'Command timed out'
        status = 'timeout'
    except Exception as e:
        output = str(e)
        status = 'error'

    db.execute(
        'INSERT INTO processing_jobs (id, media_id, action_template, status, output) VALUES (?, ?, ?, ?, ?)',
        (job_id, media_id, action_template, status, output)
    )
    db.commit()

    return jsonify({
        'job_id': job_id,
        'media_id': media_id,
        'command': cmd,
        'status': status,
        'output': output
    })


@app.route('/api/jobs', methods=['GET'])
def api_list_jobs():
    db = get_db()
    jobs = db.execute(
        '''SELECT j.*, m.title as media_title 
           FROM processing_jobs j 
           LEFT JOIN media_items m ON j.media_id = m.id 
           ORDER BY j.created_at DESC LIMIT 50'''
    ).fetchall()
    return jsonify([dict(row) for row in jobs])


@app.route('/health')
def health():
    return jsonify({'status': 'ok'}), 200


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=80)
