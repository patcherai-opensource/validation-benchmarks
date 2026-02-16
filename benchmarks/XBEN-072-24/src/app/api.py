import logging

import netaddr
from flask import Blueprint, abort, current_app, jsonify, request
from flask_login import current_user, login_required

from app.util import resolve_client_address, _parse_trusted_networks

logger = logging.getLogger(__name__)


def register_api(app):

    @app.route("/api/v1/status")
    def api_status():
        if not current_user.is_authenticated:
            return jsonify({"error": "Unauthorized"}), 401
        return jsonify({
            "state": {
                "text": "Operational",
                "flags": {
                    "operational": True,
                    "printing": False,
                    "cancelling": False,
                    "pausing": False,
                    "resuming": False,
                    "ready": True,
                    "error": False,
                },
            }
        })

    @app.route("/api/v1/version")
    def api_version():
        return jsonify({
            "api": "0.1",
            "server": "1.8.7",
            "text": "FabricCtl 1.8.7",
        })

    @app.route("/api/v1/currentuser")
    def api_current_user():
        if not current_user.is_authenticated:
            return jsonify({
                "name": "",
                "active": False,
                "admin": False,
                "needs": {"role": []},
                "_is_external_client": True,
            })

        remote_addr = resolve_client_address(request)
        cfg = current_app.config["SETTINGS"]
        ac = cfg.get("accessControl", {})
        trusted_raw = ac.get("trustedNetworks", [])
        trusted = _parse_trusted_networks(trusted_raw)
        is_local = False
        try:
            client_ip = netaddr.IPAddress(remote_addr)
            for net in trusted:
                if client_ip in net:
                    is_local = True
                    break
        except Exception:
            pass

        result = current_user.as_dict()
        result["_is_external_client"] = not is_local
        return jsonify(result)

    @app.route("/api/v1/connection")
    def api_connection():
        if not current_user.is_authenticated:
            return jsonify({"error": "Unauthorized"}), 401
        cfg = current_app.config["SETTINGS"]
        fabricator = cfg.get("fabricator", {})
        return jsonify({
            "current": {
                "state": "Operational",
                "port": fabricator.get("serialPort", "/dev/ttyUSB0"),
                "baudrate": fabricator.get("baudrate", 115200),
                "deviceProfile": fabricator.get("defaultProfile", "standard_fdm"),
            },
            "options": {
                "ports": ["/dev/ttyUSB0", "/dev/ttyACM0"],
                "baudrates": [115200, 250000, 57600, 38400, 19200, 9600],
                "deviceProfiles": [
                    {"id": "standard_fdm", "name": "Standard FDM"},
                    {"id": "resin_sla", "name": "Resin SLA"},
                ],
            },
        })

    @app.route("/api/v1/job")
    def api_job():
        if not current_user.is_authenticated:
            return jsonify({"error": "Unauthorized"}), 401
        return jsonify({
            "job": {
                "file": None,
                "estimatedPrintTime": None,
                "filament": None,
            },
            "progress": {
                "completion": None,
                "filepos": None,
                "printTime": None,
                "printTimeLeft": None,
            },
            "state": "Operational",
        })

    @app.route("/api/v1/files")
    def api_files():
        if not current_user.is_authenticated:
            return jsonify({"error": "Unauthorized"}), 401
        return jsonify({
            "files": [
                {
                    "name": "calibration_cube.gcode",
                    "display": "calibration_cube.gcode",
                    "size": 284510,
                    "date": 1709251200,
                    "origin": "local",
                },
                {
                    "name": "benchy.gcode",
                    "display": "benchy.gcode",
                    "size": 1547823,
                    "date": 1709164800,
                    "origin": "local",
                },
            ],
            "free": "14.2GB",
            "total": "29.1GB",
        })

    @app.route("/api/v1/settings")
    def api_settings():
        if not current_user.is_authenticated:
            return jsonify({"error": "Unauthorized"}), 401
        if not current_user.is_admin:
            return jsonify({"error": "Forbidden"}), 403

        cfg = current_app.config["SETTINGS"]

        return jsonify({
            "server": {
                "ipCheck": cfg.get("server", {}).get("ipCheck", {}),
            },
            "accessControl": {
                "localAutologin": cfg.get("accessControl", {}).get("localAutologin", False),
                "localAutologinAs": cfg.get("accessControl", {}).get("localAutologinAs"),
                "trustedNetworks": cfg.get("accessControl", {}).get("trustedNetworks", []),
            },
            "fabricator": cfg.get("fabricator", {}),
            "system": cfg.get("system", {}),
            "secrets": cfg.get("secrets", {}),
        })

    @app.route("/api/v1/auth/passive", methods=["POST"])
    def api_passive_auth():
        """Passive authentication check - returns current user info.

        Used by the web UI to determine login status on page load.
        When auto-login is enabled for local clients, this endpoint
        will return the auto-logged-in user details.
        """
        if current_user.is_authenticated:
            remote_addr = resolve_client_address(request)
            cfg = current_app.config["SETTINGS"]
            ac = cfg.get("accessControl", {})
            trusted_raw = ac.get("trustedNetworks", [])
            trusted = _parse_trusted_networks(trusted_raw)
            is_local = False
            try:
                client_ip = netaddr.IPAddress(remote_addr)
                for net in trusted:
                    if client_ip in net:
                        is_local = True
                        break
            except Exception:
                pass

            result = current_user.as_dict()
            result["_is_external_client"] = not is_local
            result["session"] = "active"
            return jsonify(result)

        return jsonify({
            "name": "",
            "active": False,
            "admin": False,
            "needs": {"role": []},
            "_is_external_client": True,
            "session": "inactive",
        })

    @app.route("/api/v1/system", methods=["POST"])
    def api_system_command():
        if not current_user.is_authenticated:
            return jsonify({"error": "Unauthorized"}), 401
        if not current_user.is_admin:
            return jsonify({"error": "Forbidden"}), 403

        data = request.get_json(silent=True) or {}
        action = data.get("action")
        if not action:
            return jsonify({"error": "Missing action parameter"}), 400

        cfg = current_app.config["SETTINGS"]
        system_actions = cfg.get("system", {}).get("actions", [])
        valid_actions = [a["action"] for a in system_actions]

        if action not in valid_actions:
            return jsonify({"error": "Unknown action"}), 400

        return jsonify({"result": "Command queued", "action": action})
