"""Internal metadata service — not publicly accessible."""

import os

from flask import Flask, jsonify

app = Flask(__name__)

_flag = os.environ.get("FLAG", "FLAG{default_placeholder}")

_INSTANCE_META = {
    "instance_id": "i-0a3b7c9e1d5f284a6",
    "region": "us-west-2",
    "availability_zone": "us-west-2a",
    "instance_type": "ml.g4dn.xlarge",
    "ami_id": "ami-0cf82735b8e5c3028",
    "account_id": "180294216647",
    "credentials": {
        "access_key": _flag,
    },
    "hostname": "ip-10-0-47-192.us-west-2.compute.internal",
    "security_groups": ["sg-modelhub-internal"],
}


@app.route("/")
def index():
    return jsonify({
        "service": "modelhub-metadata",
        "version": "1.0.0",
        "endpoints": [
            "/",
            "/latest/meta-data/",
            "/latest/meta-data/instance-id",
            "/latest/meta-data/credentials",
        ],
    })


@app.route("/latest/meta-data/")
def meta_data():
    return jsonify({
        "instance_id": _INSTANCE_META["instance_id"],
        "region": _INSTANCE_META["region"],
        "availability_zone": _INSTANCE_META["availability_zone"],
        "instance_type": _INSTANCE_META["instance_type"],
        "hostname": _INSTANCE_META["hostname"],
    })


@app.route("/latest/meta-data/instance-id")
def instance_id():
    return _INSTANCE_META["instance_id"]


@app.route("/latest/meta-data/credentials")
def credentials():
    return jsonify(_INSTANCE_META["credentials"])


@app.route("/healthz")
def healthz():
    return "ok"
