"""OpenStack Ironic Inspector - Bare Metal Introspection Service."""

import logging
import sys

import flask

from inspector import db
from inspector import node_cache
from inspector import process
from inspector import rules

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(name)s %(levelname)s %(message)s',
    stream=sys.stderr,
)
LOG = logging.getLogger('ironic_inspector')

app = flask.Flask(__name__)
app.config['JSON_SORT_KEYS'] = False


def _error_response(msg, code=400):
    return flask.jsonify({"error": {"message": str(msg)}}), code


@app.teardown_appcontext
def shutdown_session(exception=None):
    db.cleanup_session()


@app.route('/')
def index():
    return flask.jsonify({
        "name": "OpenStack Ironic Inspector",
        "description": "Bare Metal Introspection Service",
        "versions": [
            {
                "id": "v1",
                "status": "CURRENT",
                "links": [{"href": "/v1", "rel": "self"}]
            }
        ]
    })


@app.route('/v1')
@app.route('/v1/')
def api_version():
    return flask.jsonify({
        "id": "v1",
        "status": "CURRENT",
        "links": [
            {"href": "/v1", "rel": "self"},
            {"href": "/v1/continue", "rel": "continue"},
            {"href": "/v1/introspection", "rel": "introspection"},
            {"href": "/v1/rules", "rel": "rules"},
        ]
    })


@app.route('/v1/continue', methods=['POST'])
def api_continue():
    """Endpoint for the ramdisk to post back introspection data.

    This is called by the inspection ramdisk when introspection
    is complete. The data is processed and the node state is updated.
    """
    data = flask.request.get_json(force=True)
    if not data:
        return _error_response("No data provided", 400)

    LOG.info("Processing introspection data for continue request")
    result = process.process(data)

    if "error" in result:
        return flask.jsonify(result), 404

    return flask.jsonify(result)


@app.route('/v1/introspection')
@app.route('/v1/introspection/')
def api_list_introspection():
    """List all introspection statuses."""
    try:
        nodes = node_cache.list_nodes()
        result = []
        for n in nodes:
            entry = {
                "uuid": n["uuid"],
                "state": n["state"],
                "started_at": str(n.get("started_at", "")),
                "finished_at": str(n.get("finished_at", "")),
                "error": n.get("error"),
            }
            result.append(entry)
        return flask.jsonify({"introspection": result})
    except Exception as exc:
        LOG.error("Error listing introspection: %s", exc)
        return _error_response("Internal error", 500)


@app.route('/v1/introspection/<node_uuid>')
def api_get_introspection(node_uuid):
    """Get introspection status for a specific node."""
    try:
        node = node_cache.get_node(node_uuid)
        return flask.jsonify({
            "uuid": node["uuid"],
            "state": node["state"],
            "started_at": str(node.get("started_at", "")),
            "finished_at": str(node.get("finished_at", "")),
            "error": node.get("error"),
            "manage_boot": bool(node.get("manage_boot", True)),
        })
    except node_cache.NodeNotFoundError:
        return _error_response("Node %s not found" % node_uuid, 404)
    except Exception as exc:
        LOG.error("Error getting introspection status: %s", exc)
        return _error_response("Internal error", 500)


@app.route('/v1/rules')
@app.route('/v1/rules/')
def api_list_rules():
    """List all introspection rules."""
    try:
        all_rules = rules.get_all_rules()
        result = []
        for r in all_rules:
            result.append({
                "uuid": r["uuid"],
                "description": r.get("description", ""),
            })
        return flask.jsonify({"rules": result})
    except Exception as exc:
        LOG.error("Error listing rules: %s", exc)
        return _error_response("Internal error", 500)


@app.route('/v1/rules/<rule_uuid>')
def api_get_rule(rule_uuid):
    """Get a specific introspection rule."""
    try:
        rule = rules.get_rule(rule_uuid)
        return flask.jsonify(rule)
    except rules.RuleNotFoundError:
        return _error_response("Rule %s not found" % rule_uuid, 404)
    except Exception as exc:
        LOG.error("Error getting rule: %s", exc)
        return _error_response("Internal error", 500)


@app.route('/v1/rules/<rule_uuid>', methods=['DELETE'])
def api_delete_rule(rule_uuid):
    """Delete an introspection rule."""
    try:
        rules.delete_rule(rule_uuid)
        return '', 204
    except rules.RuleNotFoundError:
        return _error_response("Rule %s not found" % rule_uuid, 404)
    except Exception as exc:
        LOG.error("Error deleting rule: %s", exc)
        return _error_response("Internal error", 500)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
