import os
import re
import time
import json
import subprocess
import logging
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify

app = Flask(__name__)
app.secret_key = os.urandom(24)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("crmsh.web")

# Configuration
CRM_LOG_DIR = "/var/log/cluster"
CRM_HISTORY_DIR = "/var/lib/crmsh/history"
CRM_PE_DIR = "/var/lib/pacemaker/pengine"
HACLUSTER_USER = "hacluster"

# Simulated cluster state
CLUSTER_NODES = ["node1", "node2", "node3"]
CLUSTER_RESOURCES = [
    {"id": "rsc_sap_HA1_HDB00", "type": "SAPHana", "status": "Started", "node": "node1"},
    {"id": "rsc_ip_HA1_HDB00", "type": "IPaddr2", "status": "Started", "node": "node1"},
    {"id": "rsc_SAPHanaTopology_HA1_HDB00", "type": "SAPHanaTopology", "status": "Started", "node": "node2"},
    {"id": "stonith-sbd", "type": "stonith:external/sbd", "status": "Started", "node": "node1"},
]


def get_cluster_status():
    """Return simulated cluster status info."""
    return {
        "stack": "corosync",
        "current_dc": "node1",
        "version": "1.1.24+20201209.0d2b5fb4c-3.12.1",
        "nodes_online": CLUSTER_NODES,
        "nodes_offline": [],
        "resources": CLUSTER_RESOURCES,
        "last_updated": datetime.now().strftime("%a %b %d %H:%M:%S %Y"),
    }


def filter_log_output(log_content, pattern):
    """Filter log content by pattern using grep."""
    cmd = "grep -i '%s'" % pattern
    try:
        proc = subprocess.Popen(
            cmd, shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = proc.communicate(input=log_content.encode())
        return stdout.decode("utf-8", errors="replace")
    except Exception as e:
        logger.error("filter_log_output error: %s", e)
        return ""


def get_log_for_node(node, from_time=None):
    """Retrieve cluster log entries for a specific node."""
    log_path = os.path.join(CRM_LOG_DIR, "ha-log.txt")
    if not os.path.exists(log_path):
        return "No log file found at %s" % log_path

    cmd = "cat %s | grep -i '%s'" % (log_path, node)
    if from_time:
        cmd = cmd + " | grep '%s'" % from_time

    try:
        proc = subprocess.Popen(
            cmd, shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = proc.communicate(timeout=10)
        output = stdout.decode("utf-8", errors="replace")
        if not output.strip():
            return "No matching log entries for node '%s'" % node
        return output
    except subprocess.TimeoutExpired:
        proc.kill()
        return "Log retrieval timed out"
    except Exception as e:
        logger.error("get_log_for_node error: %s", e)
        return "Error retrieving logs: %s" % str(e)


def get_pe_inputs(node=None):
    """List PE (policy engine) input files."""
    if not os.path.isdir(CRM_PE_DIR):
        return []
    try:
        cmd = "ls -lt %s/*.xml 2>/dev/null | head -20" % CRM_PE_DIR
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, _ = proc.communicate(timeout=5)
        lines = stdout.decode("utf-8", errors="replace").strip().split("\n")
        return [l.strip() for l in lines if l.strip()]
    except Exception:
        return []


def get_transition_log(session_name):
    """Retrieve transition details for a given history session."""
    session_dir = os.path.join(CRM_HISTORY_DIR, session_name)
    if not os.path.isdir(CRM_HISTORY_DIR):
        return "History directory not found"

    cmd = "find %s -name '*.log' -exec cat {} \\; 2>/dev/null" % session_dir
    try:
        proc = subprocess.Popen(
            cmd, shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = proc.communicate(timeout=10)
        output = stdout.decode("utf-8", errors="replace")
        if not output.strip():
            return "No transition data found for session '%s'" % session_name
        return output
    except subprocess.TimeoutExpired:
        proc.kill()
        return "Transition log retrieval timed out"
    except Exception as e:
        return "Error: %s" % str(e)


def list_history_sessions():
    """List available history sessions."""
    if not os.path.isdir(CRM_HISTORY_DIR):
        return []
    try:
        entries = os.listdir(CRM_HISTORY_DIR)
        return sorted(entries)
    except Exception:
        return []


@app.route("/")
def index():
    status = get_cluster_status()
    return render_template("index.html", status=status)


@app.route("/status")
def cluster_status():
    status = get_cluster_status()
    return render_template("status.html", status=status)


@app.route("/history")
def history():
    sessions = list_history_sessions()
    return render_template("history.html", sessions=sessions)


@app.route("/history/log", methods=["GET", "POST"])
def history_log():
    """View cluster logs filtered by node."""
    output = None
    node = ""
    from_time = ""

    if request.method == "POST":
        node = request.form.get("node", "").strip()
        from_time = request.form.get("from_time", "").strip()

        if not node:
            flash("Please specify a node name.", "error")
            return render_template("history_log.html", output=None, node=node,
                                   from_time=from_time, nodes=CLUSTER_NODES)

        output = get_log_for_node(node, from_time if from_time else None)

    return render_template("history_log.html", output=output, node=node,
                           from_time=from_time, nodes=CLUSTER_NODES)


@app.route("/history/transition", methods=["GET", "POST"])
def history_transition():
    """View transition details for a history session."""
    output = None
    session_name = ""
    sessions = list_history_sessions()

    if request.method == "POST":
        session_name = request.form.get("session", "").strip()
        if not session_name:
            flash("Please specify a session name.", "error")
            return render_template("history_transition.html", output=None,
                                   session_name=session_name, sessions=sessions)
        output = get_transition_log(session_name)

    return render_template("history_transition.html", output=output,
                           session_name=session_name, sessions=sessions)


@app.route("/history/diff", methods=["GET", "POST"])
def history_diff():
    """Compare two PE input configurations."""
    output = None
    pe_inputs = get_pe_inputs()

    if request.method == "POST":
        file1 = request.form.get("file1", "").strip()
        file2 = request.form.get("file2", "").strip()

        if not file1 or not file2:
            flash("Please specify both PE input files.", "error")
            return render_template("history_diff.html", output=None, pe_inputs=pe_inputs)

        # Validate inputs are actual PE file paths
        if not all(f.startswith(CRM_PE_DIR) for f in [file1, file2]):
            flash("Invalid PE input path.", "error")
            return render_template("history_diff.html", output=None, pe_inputs=pe_inputs)

        cmd = "diff -u %s %s 2>/dev/null" % (file1, file2)
        try:
            proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, _ = proc.communicate(timeout=10)
            output = stdout.decode("utf-8", errors="replace")
            if not output.strip():
                output = "No differences found."
        except Exception as e:
            output = "Error: %s" % str(e)

    return render_template("history_diff.html", output=output, pe_inputs=pe_inputs)


@app.route("/configure")
def configure():
    """Show cluster configuration - read-only view."""
    cib_path = "/var/lib/pacemaker/cib/cib.xml"
    config_content = ""
    if os.path.exists(cib_path):
        with open(cib_path, "r") as f:
            config_content = f.read()
    else:
        config_content = "CIB configuration not available."
    return render_template("configure.html", config=config_content)


@app.route("/node")
def node_list():
    """List cluster nodes with their status."""
    return render_template("nodes.html", nodes=CLUSTER_NODES,
                           status=get_cluster_status())


@app.route("/ping", methods=["POST"])
def ping():
    """Network connectivity check with proper input validation."""
    ip_address = request.form.get("ip_address", "").strip()
    if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9.\-]{0,253}[a-zA-Z0-9]$', ip_address):
        return render_template("result.html", ip_address=ip_address,
                               ping_output="Invalid host address format.")
    try:
        result = subprocess.run(
            ["ping", "-c", "2", "-W", "3", ip_address],
            capture_output=True, text=True, timeout=10
        )
        ping_output = result.stdout if result.stdout else result.stderr
    except subprocess.TimeoutExpired:
        ping_output = "Ping timed out."
    except Exception as e:
        ping_output = "Error: %s" % str(e)
    return render_template("result.html", ip_address=ip_address, ping_output=ping_output)


@app.route("/api/v1/cluster/status")
def api_cluster_status():
    """API endpoint for cluster status."""
    return jsonify(get_cluster_status())


@app.route("/api/v1/cluster/health")
def api_cluster_health():
    """Health check endpoint."""
    return jsonify({"status": "ok", "cluster": "healthy", "quorum": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
