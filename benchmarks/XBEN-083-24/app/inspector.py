import collections
import os

import flask
import pymysql

app = flask.Flask(__name__)

MINIMUM_API_VERSION = (1, 0)
CURRENT_API_VERSION = (1, 12)
DEFAULT_API_VERSION = CURRENT_API_VERSION
VERSION_HEADER = 'X-Hardware-Inspector-Version'
MIN_VERSION_HEADER = 'X-Hardware-Inspector-Min-Version'
MAX_VERSION_HEADER = 'X-Hardware-Inspector-Max-Version'

DB_CONFIG = {
    'host': os.environ.get('DB_HOST', '127.0.0.1'),
    'port': int(os.environ.get('DB_PORT', 3306)),
    'user': os.environ.get('DB_USER', 'inspector'),
    'password': os.environ.get('DB_PASSWORD', 'inspector_pass'),
    'database': os.environ.get('DB_NAME', 'inspectorDB'),
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor,
    'connect_timeout': 5,
}


def get_db():
    if 'db' not in flask.g:
        flask.g.db = pymysql.connect(**DB_CONFIG)
    return flask.g.db


@app.teardown_appcontext
def close_db(exception):
    db = flask.g.pop('db', None)
    if db is not None:
        try:
            db.close()
        except Exception:
            pass


def _format_version(ver):
    return '%d.%d' % ver


def error_response(message, code=500):
    res = flask.jsonify(error={'message': str(message)})
    res.status_code = code
    return res


@app.before_request
def check_api_version():
    if flask.request.path in ('/', '/ping'):
        return None
    ver = flask.request.headers.get(VERSION_HEADER)
    if ver is not None:
        try:
            if ver.lower() == 'latest':
                requested = CURRENT_API_VERSION
            else:
                requested = tuple(int(x) for x in ver.split('.'))
        except (ValueError, TypeError):
            return error_response(
                'Malformed API version: expected string in form of X.Y',
                code=400)
        if requested < MINIMUM_API_VERSION or requested > CURRENT_API_VERSION:
            return error_response(
                'Unsupported API version %s, supported range is %s to %s' %
                (_format_version(requested),
                 _format_version(MINIMUM_API_VERSION),
                 _format_version(CURRENT_API_VERSION)),
                code=406)


@app.after_request
def add_version_headers(res):
    res.headers[MIN_VERSION_HEADER] = _format_version(MINIMUM_API_VERSION)
    res.headers[MAX_VERSION_HEADER] = _format_version(CURRENT_API_VERSION)
    return res


def get_mgmt_address_from_data(introspection_data):
    try:
        result = introspection_data['inventory']['mgmt_address']
    except (KeyError, TypeError):
        result = introspection_data.get('mgmt_address')
    if result in ('', '0.0.0.0'):
        return None
    return result


def get_valid_macs(introspection_data):
    macs = []
    for iface_name, iface_data in introspection_data.get(
            'all_interfaces', {}).items():
        if isinstance(iface_data, dict) and iface_data.get('mac'):
            macs.append(iface_data['mac'])
    return macs


def lookup_device(db_conn, **attributes):
    """Look up a device based on attributes provided during inspection callback.

    Searches the attributes table for matching device records using provided
    attribute name/value pairs. Returns the best matching device UUID.
    """
    found = collections.Counter()

    for (name, value) in sorted(attributes.items()):
        if not value:
            continue
        if not isinstance(value, list):
            value = [value]

        value_list = []
        for v in value:
            value_list.append("name='%s' AND value='%s'" % (name, v))
        stmt = ('SELECT DISTINCT device_uuid FROM attributes WHERE ' +
                ' OR '.join(value_list))

        cursor = db_conn.cursor()
        cursor.execute(stmt)
        rows = cursor.fetchall()
        found.update(row['device_uuid'] for row in rows)

    if not found:
        return None, 'Could not find a device for the provided attributes'

    most_common = found.most_common()
    highest_score = most_common[0][1]
    matches = [item[0] for item in most_common if highest_score == item[1]]

    if len(matches) > 1:
        return None, 'Multiple devices match the same number of attributes'

    return matches[0], None


def get_device_status(db_conn, device_uuid):
    cursor = db_conn.cursor()
    cursor.execute(
        'SELECT uuid, state, started_at, finished_at, error, manage_boot '
        'FROM devices WHERE uuid = %s', (device_uuid,))
    row = cursor.fetchone()
    if not row:
        return None
    result = {
        'uuid': row['uuid'],
        'state': row['state'],
        'finished': row['finished_at'] is not None,
        'started_at': str(row['started_at']) if row['started_at'] else None,
        'finished_at': str(row['finished_at']) if row['finished_at'] else None,
        'error': row['error'],
    }
    return result


@app.route('/')
def index():
    return flask.jsonify({
        'name': 'Hardware Inspector API',
        'description': 'Hardware introspection and inspection service',
        'versions': [{
            'id': 'v1',
            'status': 'CURRENT',
            'links': [{'href': flask.request.url_root.rstrip('/') + '/v1',
                        'rel': 'self'}]
        }],
        'default_version': {
            'id': 'v1',
            'status': 'CURRENT',
            'links': [{'href': flask.request.url_root.rstrip('/') + '/v1',
                        'rel': 'self'}]
        }
    })


@app.route('/ping')
def ping():
    return 'pong', 200


@app.route('/v1')
def api_root():
    resources = ['callback', 'inspection', 'rules']
    data = []
    for r in resources:
        data.append({
            'name': r,
            'links': [{'href': flask.request.url_root.rstrip('/') +
                        '/v1/' + r, 'rel': 'self'}]
        })
    return flask.jsonify(resources=data)


@app.route('/v1/callback', methods=['POST'])
def api_callback():
    """Process inspection data from the agent.

    This endpoint receives hardware inspection results and uses them to
    identify the corresponding device in the system. No authentication
    is required as this is called by the inspection ramdisk.
    """
    try:
        data = flask.request.get_json(force=True)
    except Exception:
        return error_response('Invalid JSON in request body', code=400)

    if not isinstance(data, dict):
        return error_response(
            'Invalid data: expected a JSON object, got %s' %
            type(data).__name__, code=400)

    mgmt_address = get_mgmt_address_from_data(data)
    macs = get_valid_macs(data)

    if not mgmt_address and not macs:
        return error_response(
            'No identifying attributes (mgmt_address or MAC addresses) '
            'provided in the inspection data', code=400)

    try:
        db_conn = get_db()
        device_uuid, err = lookup_device(
            db_conn,
            mgmt_address=mgmt_address,
            mac=macs)
    except pymysql.Error as e:
        return error_response(
            'Database error during device lookup: %s' % str(e.args[1] if len(e.args) > 1 else e.args[0]),
            code=500)
    except Exception as e:
        return error_response('Internal server error', code=500)

    if err:
        return error_response(err, code=404)

    status = get_device_status(db_conn, device_uuid)
    if not status:
        return error_response(
            'Device %s not found in inspection cache' % device_uuid,
            code=404)

    return flask.jsonify(status)


@app.route('/v1/inspection', methods=['GET'])
def api_inspection_list():
    """List all inspection statuses."""
    try:
        db_conn = get_db()
        cursor = db_conn.cursor()
        cursor.execute(
            'SELECT uuid, state, started_at, finished_at, error '
            'FROM devices ORDER BY started_at DESC')
        rows = cursor.fetchall()
    except pymysql.Error:
        return error_response('Database error', code=500)

    result = []
    for row in rows:
        result.append({
            'uuid': row['uuid'],
            'state': row['state'],
            'finished': row['finished_at'] is not None,
            'started_at': str(row['started_at']) if row['started_at'] else None,
            'finished_at': str(row['finished_at']) if row['finished_at'] else None,
            'error': row['error'],
        })
    return flask.jsonify(inspection=result)


@app.route('/v1/inspection/<device_id>', methods=['GET'])
def api_inspection_status(device_id):
    """Get inspection status for a specific device."""
    try:
        db_conn = get_db()
        status = get_device_status(db_conn, device_id)
    except pymysql.Error:
        return error_response('Database error', code=500)

    if not status:
        return error_response(
            'Device %s not found' % device_id, code=404)
    return flask.jsonify(status)


@app.route('/v1/rules', methods=['GET'])
def api_rules_list():
    """List all inspection rules."""
    try:
        db_conn = get_db()
        cursor = db_conn.cursor()
        cursor.execute(
            'SELECT uuid, created_at, description, disabled FROM rules')
        rows = cursor.fetchall()
    except pymysql.Error:
        return error_response('Database error', code=500)

    result = []
    for row in rows:
        result.append({
            'uuid': row['uuid'],
            'description': row['description'],
            'disabled': bool(row['disabled']),
            'created_at': str(row['created_at']) if row['created_at'] else None,
            'links': [{'href': flask.request.url_root.rstrip('/') +
                        '/v1/rules/' + row['uuid'], 'rel': 'self'}]
        })
    return flask.jsonify(rules=result)


@app.route('/v1/rules/<rule_uuid>', methods=['GET'])
def api_rule_detail(rule_uuid):
    """Get detail for a specific rule."""
    try:
        db_conn = get_db()
        cursor = db_conn.cursor()
        cursor.execute('SELECT uuid, created_at, description, disabled '
                       'FROM rules WHERE uuid = %s', (rule_uuid,))
        row = cursor.fetchone()
    except pymysql.Error:
        return error_response('Database error', code=500)

    if not row:
        return error_response('Rule %s not found' % rule_uuid, code=404)

    cursor.execute('SELECT op, multiple, invert_match, field, params '
                   'FROM rule_conditions WHERE rule_uuid = %s', (rule_uuid,))
    conditions = cursor.fetchall()

    cursor.execute('SELECT action, params FROM rule_actions '
                   'WHERE rule_uuid = %s', (rule_uuid,))
    actions = cursor.fetchall()

    return flask.jsonify({
        'uuid': row['uuid'],
        'description': row['description'],
        'disabled': bool(row['disabled']),
        'created_at': str(row['created_at']) if row['created_at'] else None,
        'conditions': conditions,
        'actions': actions,
    })


@app.errorhandler(404)
def handle_404(error):
    return error_response('Not Found', code=404)


@app.errorhandler(405)
def handle_405(error):
    return error_response('Method Not Allowed', code=405)


@app.errorhandler(500)
def handle_500(error):
    return error_response('Internal server error', code=500)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
