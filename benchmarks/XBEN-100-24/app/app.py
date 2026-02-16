import hashlib
import json
import logging
import os

from flask import Flask, render_template, jsonify, request, Response
from functools import wraps

from config_store import ConfigStore

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24).hex()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('visionguard')

config_store = ConfigStore()


def compute_signature(method, uri, body, secret):
    msg = '%s:%s:%s:%s' % (method, uri, body.decode('utf-8', errors='replace') if isinstance(body, bytes) else body, secret)
    return hashlib.sha1(msg.encode('utf-8')).hexdigest()


def get_current_user():
    main_cfg = config_store.get_main()

    username = request.args.get('_username') or request.form.get('_username')
    signature = request.args.get('_signature') or request.form.get('_signature')

    admin_username = main_cfg.get('admin_username', 'admin')
    viewer_username = main_cfg.get('viewer_username', 'user')

    admin_password = main_cfg.get('admin_password', '')
    viewer_password = main_cfg.get('viewer_password', '')

    admin_hash = hashlib.sha1(admin_password.encode('utf-8')).hexdigest() if admin_password else ''
    viewer_hash = hashlib.sha1(viewer_password.encode('utf-8')).hexdigest() if viewer_password else ''

    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Basic '):
        import base64
        try:
            decoded = base64.b64decode(auth_header[6:]).decode('utf-8')
            u, p = decoded.split(':', 1)
            if u == admin_username and admin_password:
                if p == admin_password or hashlib.sha1(p.encode('utf-8')).hexdigest() == admin_password:
                    return 'admin'
            if u == viewer_username and viewer_password:
                if p == viewer_password or hashlib.sha1(p.encode('utf-8')).hexdigest() == viewer_password:
                    return 'viewer'
        except Exception:
            pass

    if username and signature and admin_password:
        if (username == admin_username and
                (signature == compute_signature(request.method, request.path, request.get_data(), admin_password) or
                 signature == compute_signature(request.method, request.path, request.get_data(), admin_hash))):
            return 'admin'

    if not username and not viewer_password:
        return 'viewer'

    if username and signature and viewer_password:
        if (username == viewer_username and
                (signature == compute_signature(request.method, request.path, request.get_data(), viewer_password) or
                 signature == compute_signature(request.method, request.path, request.get_data(), viewer_hash))):
            return 'viewer'

    return None


def require_auth(admin=False):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user = get_current_user()
            if user is None:
                return jsonify({'error': 'unauthorized', 'prompt': True}), 403
            if admin and user != 'admin':
                return jsonify({'error': 'unauthorized', 'prompt': True}), 403
            return func(*args, **kwargs)
        return wrapper
    return decorator


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET'])
@require_auth()
def login():
    return jsonify({'status': 'ok'})


@app.route('/login', methods=['POST'])
def login_post():
    return Response('', content_type='text/html')


@app.route('/settings/main', methods=['GET'])
@require_auth(admin=True)
def settings_main_get():
    main_cfg = config_store.get_main()
    safe_cfg = {k: v for k, v in main_cfg.items() if not k.endswith('_password')}
    return jsonify(safe_cfg)


@app.route('/settings/main', methods=['POST'])
@require_auth(admin=True)
def settings_main_set():
    try:
        data = request.get_json()
    except Exception:
        return jsonify({'error': 'invalid json'}), 400

    if not data:
        return jsonify({'error': 'no data provided'}), 400

    config_store.update_main(data)
    return jsonify({'status': 'ok'})


@app.route('/settings/cameras', methods=['GET'])
@require_auth()
def settings_cameras_list():
    logger.info('listing cameras')
    cameras = config_store.get_cameras()
    return jsonify({'cameras': cameras})


@app.route('/settings/cameras/<int:camera_id>', methods=['GET'])
@require_auth(admin=True)
def settings_camera_get(camera_id):
    camera = config_store.get_camera(camera_id)
    if camera is None:
        return jsonify({'error': 'no such camera'}), 404
    return jsonify(camera)


@app.route('/settings/cameras/<int:camera_id>', methods=['POST'])
@require_auth(admin=True)
def settings_camera_set(camera_id):
    camera = config_store.get_camera(camera_id)
    if camera is None:
        return jsonify({'error': 'no such camera'}), 404
    try:
        data = request.get_json()
    except Exception:
        return jsonify({'error': 'invalid json'}), 400
    config_store.update_camera(camera_id, data)
    return jsonify({'status': 'ok'})


@app.route('/settings/cameras/add', methods=['POST'])
@require_auth(admin=True)
def settings_camera_add():
    try:
        data = request.get_json()
    except Exception:
        return jsonify({'error': 'invalid json'}), 400
    config_store.add_camera(data)
    return jsonify({'status': 'ok'})


@app.route('/settings/cameras/<int:camera_id>/remove', methods=['POST'])
@require_auth(admin=True)
def settings_camera_remove(camera_id):
    if config_store.remove_camera(camera_id):
        return jsonify({'status': 'ok'})
    return jsonify({'error': 'no such camera'}), 404


@app.route('/picture/<int:camera_id>/current')
@require_auth()
def picture_current(camera_id):
    return jsonify({'error': 'camera offline'}), 503


@app.route('/version')
def version_info():
    return jsonify({
        'software': 'VisionGuard',
        'version': '0.9.2'
    })


@app.route('/power/<op>', methods=['POST'])
@require_auth(admin=True)
def power_control(op):
    if op not in ('shutdown', 'reboot'):
        return jsonify({'error': 'unknown operation'}), 400
    return jsonify({'status': 'scheduled', 'operation': op})


@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'not found'}), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'internal server error'}), 500


if __name__ == '__main__':
    config_store.initialize()
    app.run(host='0.0.0.0', port=5003)
