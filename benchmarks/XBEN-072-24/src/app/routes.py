import os
import yaml
import time
import hashlib

from flask import (
    request, g, session, jsonify, render_template,
    redirect, url_for, make_response
)
from app.util import require_login, require_admin


def register_routes(app, config):

    @app.route("/ping")
    def ping():
        return "pong", 200

    @app.route("/")
    def index():
        if hasattr(g, "user") and g.user is not None:
            return redirect(url_for("main_dashboard"))
        return redirect(url_for("login"))

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if hasattr(g, "user") and g.user is not None:
            return redirect(url_for("main_dashboard"))

        if request.method == "POST":
            username = request.form.get("username", "")
            password = request.form.get("password", "")

            # Validate credentials against configured users
            user = app.config["USERS"].get(username)
            if user and user.get("active", False):
                # In production, password check would go here
                stored_hash = hashlib.sha256(
                    (config["server"]["secretKey"] + username).encode()
                ).hexdigest()
                provided_hash = hashlib.sha256(
                    (config["server"]["secretKey"] + password).encode()
                ).hexdigest()

                if stored_hash == provided_hash:
                    session["authenticated"] = True
                    session["username"] = username
                    return redirect(url_for("main_dashboard"))

            return render_template("login.html", error="Incorrect username or password"), 403

        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("login"))

    @app.route("/dashboard")
    @require_login
    def main_dashboard():
        printer_state = {
            "text": "Operational",
            "flags": {
                "operational": True,
                "printing": False,
                "cancelling": False,
                "pausing": False,
                "resuming": False,
                "finishing": False,
                "closedOrError": False,
                "error": False,
                "paused": False,
                "ready": True,
                "sdReady": True
            }
        }
        temperatures = {
            "tool0": {"actual": 24.3, "target": 0.0, "offset": 0},
            "bed": {"actual": 23.8, "target": 0.0, "offset": 0}
        }
        return render_template(
            "dashboard.html",
            user=g.user,
            printer_state=printer_state,
            temperatures=temperatures,
            is_local=getattr(g, "is_local", False)
        )

    # --- API endpoints (mirroring OctoPrint REST API) ---

    @app.route("/api/version")
    def api_version():
        return jsonify({
            "api": "0.1",
            "server": "1.10.0",
            "text": "OctoPrint 1.10.0"
        })

    @app.route("/api/connection")
    @require_login
    def api_connection():
        return jsonify({
            "current": {
                "state": "Operational",
                "port": "/dev/ttyACM0",
                "baudrate": 250000,
                "printerProfile": "_default"
            },
            "options": {
                "ports": ["/dev/ttyACM0", "/dev/ttyUSB0"],
                "baudrates": [250000, 230400, 115200, 57600, 38400, 19200, 9600],
                "printerProfiles": [{"id": "_default", "name": "Default"}],
                "portPreference": "/dev/ttyACM0",
                "baudratePreference": 250000,
                "autoconnect": True
            }
        })

    @app.route("/api/printer")
    @require_login
    def api_printer():
        return jsonify({
            "temperature": {
                "tool0": {"actual": 24.3, "target": 0.0, "offset": 0},
                "bed": {"actual": 23.8, "target": 0.0, "offset": 0}
            },
            "sd": {"ready": True},
            "state": {
                "text": "Operational",
                "flags": {
                    "operational": True,
                    "printing": False,
                    "cancelling": False,
                    "pausing": False,
                    "resuming": False,
                    "finishing": False,
                    "closedOrError": False,
                    "error": False,
                    "paused": False,
                    "ready": True,
                    "sdReady": True
                }
            }
        })

    @app.route("/api/job")
    @require_login
    def api_job():
        return jsonify({
            "job": {
                "file": {"name": None, "origin": None, "size": None, "date": None},
                "estimatedPrintTime": None,
                "filament": {"tool0": {"length": None, "volume": None}}
            },
            "progress": {
                "completion": None,
                "filepos": None,
                "printTime": None,
                "printTimeLeft": None
            },
            "state": "Operational"
        })

    @app.route("/api/files")
    @require_login
    def api_files():
        return jsonify({
            "files": [
                {
                    "name": "benchy.gcode",
                    "display": "benchy.gcode",
                    "path": "benchy.gcode",
                    "type": "machinecode",
                    "typePath": ["machinecode", "gcode"],
                    "origin": "local",
                    "date": 1706745600,
                    "size": 2458624
                },
                {
                    "name": "calibration_cube.gcode",
                    "display": "calibration_cube.gcode",
                    "path": "calibration_cube.gcode",
                    "type": "machinecode",
                    "typePath": ["machinecode", "gcode"],
                    "origin": "local",
                    "date": 1706832000,
                    "size": 1843200
                }
            ],
            "free": "14.2GB",
            "total": "29.5GB"
        })

    @app.route("/api/settings")
    @require_admin
    def api_settings():
        """Return full settings including sensitive data like API key.
        Only accessible to admin users."""
        return jsonify({
            "api": {
                "key": config["accessControl"]["apikey"],
                "allowCrossOrigin": False
            },
            "appearance": config.get("appearance", {}),
            "feature": config.get("feature", {}),
            "webcam": config.get("webcam", {}),
            "serial": config.get("serial", {}),
            "temperature": config.get("temperature", {}),
            "server": {
                "commands": {
                    "systemShutdownCommand": "sudo shutdown -h now",
                    "systemRestartCommand": "sudo shutdown -r now",
                    "serverRestartCommand": "sudo service octoprint restart"
                },
                "diskspace": {
                    "warning": 500,
                    "critical": 200
                },
                "onlineCheck": {
                    "enabled": False,
                    "interval": 15,
                    "host": "1.1.1.1",
                    "port": 53
                },
                "pluginBlacklist": {
                    "enabled": False
                }
            },
            "plugins": config.get("plugins", {}),
            "accessControl": {
                "autologinLocal": config["accessControl"]["autologinLocal"],
                "autologinAs": config["accessControl"]["autologinAs"],
                "localNetworks": config["accessControl"]["localNetworks"]
            }
        })

    @app.route("/api/printerprofiles")
    @require_login
    def api_printer_profiles():
        return jsonify({
            "profiles": {
                "_default": {
                    "id": "_default",
                    "name": "Default",
                    "color": "default",
                    "model": "Generic RepRap Printer",
                    "default": True,
                    "current": True,
                    "resource": "/api/printerprofiles/_default",
                    "volume": {
                        "formFactor": "rectangular",
                        "origin": "lowerleft",
                        "width": 200.0,
                        "depth": 200.0,
                        "height": 200.0
                    },
                    "heatedBed": True,
                    "heatedChamber": False,
                    "extruder": {
                        "count": 1,
                        "nozzleDiameter": 0.4,
                        "sharedNozzle": False,
                        "offsets": [{"x": 0.0, "y": 0.0}]
                    },
                    "axes": {
                        "x": {"speed": 6000, "inverted": False},
                        "y": {"speed": 6000, "inverted": False},
                        "z": {"speed": 200, "inverted": False},
                        "e": {"speed": 300, "inverted": False}
                    }
                }
            }
        })

    @app.route("/api/system/commands")
    @require_admin
    def api_system_commands():
        return jsonify({
            "core": [
                {
                    "action": "shutdown",
                    "name": "Shutdown",
                    "command": "sudo shutdown -h now",
                    "confirm": "You are about to shutdown the system.",
                    "source": "core",
                    "resource": "/api/system/commands/core/shutdown"
                },
                {
                    "action": "reboot",
                    "name": "Reboot",
                    "command": "sudo shutdown -r now",
                    "confirm": "You are about to reboot the system.",
                    "source": "core",
                    "resource": "/api/system/commands/core/reboot"
                },
                {
                    "action": "restart",
                    "name": "Restart OctoPrint",
                    "command": "sudo service octoprint restart",
                    "confirm": "You are about to restart the OctoPrint server.",
                    "source": "core",
                    "resource": "/api/system/commands/core/restart"
                }
            ]
        })

    @app.route("/api/timelapse")
    @require_login
    def api_timelapse():
        return jsonify({
            "config": {
                "type": "off",
                "postRoll": 0,
                "fps": 25
            },
            "files": []
        })

    @app.route("/api/slicing")
    @require_login
    def api_slicing():
        return jsonify({})

    @app.route("/api/plugin/softwareupdate/check", methods=["GET"])
    @require_admin
    def api_update_check():
        return jsonify({
            "information": {
                "octoprint": {
                    "updateAvailable": False,
                    "displayName": "OctoPrint",
                    "displayVersion": "1.10.0",
                    "releaseNotes": "https://github.com/OctoPrint/OctoPrint/releases/tag/1.10.0"
                }
            }
        })

    @app.route("/api/login", methods=["POST"])
    def api_login():
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "Invalid request"}), 400

        username = data.get("user", "")
        password = data.get("pass", "")

        user = app.config["USERS"].get(username)
        if user and user.get("active", False):
            stored_hash = hashlib.sha256(
                (config["server"]["secretKey"] + username).encode()
            ).hexdigest()
            provided_hash = hashlib.sha256(
                (config["server"]["secretKey"] + password).encode()
            ).hexdigest()
            if stored_hash == provided_hash:
                session["authenticated"] = True
                session["username"] = username
                return jsonify({
                    "name": username,
                    "active": True,
                    "permissions": user.get("permissions", []),
                    "apikey": user.get("apikey", None),
                    "session": session.sid if hasattr(session, 'sid') else "active"
                })

        return jsonify({"error": "Incorrect username or password"}), 403

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        if request.path.startswith("/api/"):
            return jsonify({"error": "Not found"}), 404
        return render_template("error.html", code=404, message="Not Found"), 404

    @app.errorhandler(500)
    def internal_error(e):
        if request.path.startswith("/api/"):
            return jsonify({"error": "Internal server error"}), 500
        return render_template("error.html", code=500, message="Internal Server Error"), 500

    @app.after_request
    def set_headers(response):
        response.headers["Server"] = "OctoPrint/1.10.0"
        response.headers["X-Clacks-Overhead"] = "GNU Terry Pratchett"
        return response