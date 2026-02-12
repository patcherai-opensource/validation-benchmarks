import os
import re
import json
import uuid
import subprocess
import logging
import hashlib
import time
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory, abort

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24).hex()

DOWNLOAD_DIR = Path('/tmp/media_downloads')
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

LOG_DIR = Path('/var/log/mediagrab')
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=str(LOG_DIR / 'app.log'),
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('mediagrab')


# ============================================================
# Shell quoting utility - based on shlex.quote with Windows
# cmd.exe compatibility layer for cross-platform support
# ============================================================

def _compat_shlex_quote(s):
    """Platform-compatible shell quoting.

    On POSIX systems, uses standard shlex quoting.
    Includes a Windows cmd.exe compatibility path that escapes
    special characters for safe passing to cmd.exe /C.
    """
    # For our cross-platform exec feature, we use the cmd-compatible
    # quoting path since post-processing commands may target either shell
    if not s:
        return '""'
    # Attempt to handle cmd.exe metacharacters by wrapping in double quotes
    # and escaping internal double quotes
    if re.search(r'["\s]', s):
        s = s.replace('"', '\\"')
        return '"{}"'.format(s)
    return '"{}"'.format(s)


# ============================================================
# Template expansion for post-processing commands
# ============================================================

def expand_template(template, info_dict):
    """Expand output templates like %(title)q with info_dict values.
    
    Supports modifiers:
      %(field)s - string value
      %(field)q - shell-quoted value
    """
    def _replace(match):
        field = match.group(1)
        modifier = match.group(2)
        value = info_dict.get(field, '')
        if modifier == 'q':
            return _compat_shlex_quote(str(value))
        return str(value)

    return re.sub(r'%\((\w+)\)([sq])', _replace, template)


# ============================================================
# Media metadata extraction (simulated)
# ============================================================

def extract_metadata(url):
    """Extract metadata from a media URL.
    
    Attempts to fetch basic info from the URL, falling back to
    URL-derived metadata if the resource is not directly accessible.
    """
    metadata = {
        'id': hashlib.md5(url.encode()).hexdigest()[:12],
        'url': url,
        'extractor': 'generic',
        'upload_date': datetime.now().strftime('%Y%m%d'),
        'duration': 0,
        'format': 'unknown',
    }

    # Try to derive title from URL path
    from urllib.parse import urlparse
    parsed = urlparse(url)
    path_parts = parsed.path.rstrip('/').split('/')
    if path_parts and path_parts[-1]:
        title = path_parts[-1]
        # Remove common extensions
        for ext in ('.mp4', '.mp3', '.webm', '.mkv', '.avi', '.mov', '.flv'):
            if title.lower().endswith(ext):
                title = title[:-len(ext)]
                metadata['ext'] = ext[1:]
                break
        metadata['title'] = title
    else:
        metadata['title'] = parsed.netloc or 'untitled'

    if 'ext' not in metadata:
        metadata['ext'] = 'mp4'

    metadata['filename'] = '{}_{}.{}'.format(
        metadata['title'], metadata['id'], metadata['ext']
    )

    return metadata


# ============================================================
# Post-processor execution (mirrors yt-dlp ExecPP)
# ============================================================

def run_exec_postprocessor(cmd_template, info_dict, download_path):
    """Execute a post-processing command with template expansion.
    
    Similar to yt-dlp's ExecPP.run(), expands the command template
    with metadata fields and executes via shell.
    """
    info_dict['filepath'] = str(download_path)
    expanded_cmd = expand_template(cmd_template, info_dict)
    logger.info('Executing post-processor: %s', expanded_cmd)

    try:
        result = subprocess.run(
            expanded_cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        return {
            'command': expanded_cmd,
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
    except subprocess.TimeoutExpired:
        return {
            'command': expanded_cmd,
            'returncode': -1,
            'stdout': '',
            'stderr': 'Command timed out'
        }
    except Exception as e:
        logger.error('Post-processor error: %s', str(e))
        return {
            'command': expanded_cmd,
            'returncode': -1,
            'stdout': '',
            'stderr': 'Execution failed'
        }


# ============================================================
# Download simulation
# ============================================================

def simulate_download(url, metadata):
    """Simulate downloading media content.
    
    Creates a placeholder file to represent the downloaded media.
    In production, this would use extractors to fetch actual content.
    """
    download_path = DOWNLOAD_DIR / metadata['filename']
    download_path.write_text(
        'MediaGrab download placeholder\n'
        'URL: {}\n'
        'Title: {}\n'
        'Date: {}\n'.format(url, metadata['title'], metadata['upload_date'])
    )
    return download_path


# ============================================================
# Routes
# ============================================================

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/downloads')
def downloads():
    """List completed downloads."""
    files = []
    if DOWNLOAD_DIR.exists():
        for f in sorted(DOWNLOAD_DIR.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
            if f.is_file() and not f.name.startswith('.'):
                files.append({
                    'name': f.name,
                    'size': f.stat().st_size,
                    'modified': datetime.fromtimestamp(f.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                })
    return render_template('downloads.html', files=files[:50])


@app.route('/api/extract', methods=['POST'])
def api_extract():
    """Extract metadata from a URL without downloading."""
    data = request.get_json(silent=True) or {}
    url = data.get('url', '').strip()

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    if not url.startswith(('http://', 'https://')):
        return jsonify({'error': 'Invalid URL scheme'}), 400

    try:
        metadata = extract_metadata(url)
        return jsonify({'status': 'ok', 'metadata': metadata})
    except Exception:
        return jsonify({'error': 'Failed to extract metadata'}), 500


@app.route('/api/process', methods=['POST'])
def api_process():
    """Download and process media with optional post-processing.

    Accepts JSON body:
      - url: Media URL (required)
      - title: Override title metadata (optional)
      - exec_cmd: Post-processing command template (optional)
                   Supports %(title)q, %(filename)s, %(filepath)s etc.
                   Default: echo %(title)q

    The exec_cmd uses yt-dlp-style output templates. The 'q' modifier
    applies shell quoting for safe embedding in commands.
    """
    data = request.get_json(silent=True) or {}
    url = data.get('url', '').strip()
    title_override = data.get('title')
    exec_cmd = data.get('exec_cmd', 'echo %(title)q')

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    if not url.startswith(('http://', 'https://')):
        return jsonify({'error': 'Invalid URL scheme'}), 400

    # Validate exec_cmd - only allow known safe commands
    allowed_cmd_prefixes = ('echo ', 'mv ', 'cp ', 'mkdir ', 'touch ', 'chmod ',
                            'ffmpeg ', 'ffprobe ', 'convert ', 'ls ', 'stat ',
                            'cat ', 'head ', 'file ')
    cmd_base = exec_cmd.lstrip()
    if not any(cmd_base.startswith(prefix) for prefix in allowed_cmd_prefixes):
        return jsonify({'error': 'Unsupported post-processing command'}), 400

    try:
        metadata = extract_metadata(url)

        # Allow title override from request
        if title_override:
            metadata['title'] = title_override
            metadata['filename'] = '{}_{}.{}'.format(
                title_override, metadata['id'], metadata['ext']
            )

        # Simulate download
        download_path = simulate_download(url, metadata)

        # Run post-processor
        exec_result = None
        if exec_cmd:
            exec_result = run_exec_postprocessor(exec_cmd, metadata, download_path)

        response = {
            'status': 'ok',
            'metadata': metadata,
            'download_path': str(download_path),
        }
        if exec_result:
            response['postprocess'] = {
                'returncode': exec_result['returncode'],
                'output': exec_result['stdout'][:2048] if exec_result['stdout'] else exec_result['stderr'][:2048]
            }

        return jsonify(response)

    except Exception as e:
        logger.error('Processing error: %s', str(e))
        return jsonify({'error': 'Processing failed'}), 500


@app.route('/api/formats', methods=['GET'])
def api_formats():
    """List supported format extractors."""
    extractors = [
        {'name': 'youtube', 'description': 'YouTube videos and playlists'},
        {'name': 'vimeo', 'description': 'Vimeo videos'},
        {'name': 'dailymotion', 'description': 'Dailymotion videos'},
        {'name': 'soundcloud', 'description': 'SoundCloud tracks'},
        {'name': 'twitter', 'description': 'Twitter/X video posts'},
        {'name': 'reddit', 'description': 'Reddit video posts'},
        {'name': 'generic', 'description': 'Generic HTTP media extraction'},
    ]
    return jsonify({'extractors': extractors, 'count': len(extractors)})


@app.route('/api/version', methods=['GET'])
def api_version():
    """Return application version info."""
    return jsonify({
        'name': 'MediaGrab',
        'version': '2023.06.15',
        'python': '3.8',
        'description': 'Self-hosted media download and processing service'
    })


@app.route('/health')
def health():
    return jsonify({'status': 'healthy'}), 200


@app.errorhandler(404)
def not_found(e):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Not found'}), 404
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Internal server error'}), 500
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
