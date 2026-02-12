import os

from flask import jsonify, request, abort

from app import app

NACOS_CONFIG_DIR = os.path.join(os.path.dirname(__file__), 'nacos_config')


@app.route('/nacos/v1/cs/configs', methods=['GET'])
def nacos_get_config():
    data_id = request.args.get('dataId', '')
    group = request.args.get('group', 'DEFAULT_GROUP')
    tenant = request.args.get('tenant', '')

    if not data_id:
        return jsonify({'code': 400, 'message': 'dataId is required'}), 400

    safe_name = os.path.basename(data_id)
    config_path = os.path.join(NACOS_CONFIG_DIR, safe_name)

    if not os.path.isfile(config_path):
        return '', 404

    with open(config_path, 'r') as f:
        content = f.read()

    return content, 200, {'Content-Type': 'text/plain; charset=utf-8'}


@app.route('/nacos/v1/cs/configs/listener', methods=['POST'])
def nacos_listener():
    return '', 200


@app.route('/nacos/v1/ns/instance/list', methods=['GET'])
def nacos_service_list():
    service_name = request.args.get('serviceName', '')
    return jsonify({
        'name': service_name,
        'groupName': 'DEFAULT_GROUP',
        'clusters': '',
        'cacheMillis': 10000,
        'hosts': [],
        'lastRefTime': 0,
        'checksum': '',
        'allIPs': False,
        'reachProtectionThreshold': False,
        'valid': True,
    })
