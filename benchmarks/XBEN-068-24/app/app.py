import math
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Application version
APP_VERSION = "1.4.2"

# ====================== Tool Functions ======================

def evaluate_math(expression: str) -> str:
    """
    Evaluate a mathematical expression in a restricted environment.
    Only math module functions are allowed for security.
    """
    try:
        allowed_names = {k: v for k, v in math.__dict__.items() if not k.startswith("__")}
        result = eval(expression, {"__builtins__": None}, allowed_names)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"


def unit_convert(value: float, from_unit: str, to_unit: str) -> str:
    """Convert between common units."""
    conversions = {
        ("km", "mi"): 0.621371,
        ("mi", "km"): 1.60934,
        ("kg", "lb"): 2.20462,
        ("lb", "kg"): 0.453592,
        ("c", "f"): lambda v: v * 9/5 + 32,
        ("f", "c"): lambda v: (v - 32) * 5/9,
        ("m", "ft"): 3.28084,
        ("ft", "m"): 0.3048,
        ("l", "gal"): 0.264172,
        ("gal", "l"): 3.78541,
    }
    key = (from_unit.lower(), to_unit.lower())
    if key not in conversions:
        return f"Error: Unsupported conversion from {from_unit} to {to_unit}"
    factor = conversions[key]
    if callable(factor):
        result = factor(value)
    else:
        result = value * factor
    return f"{value} {from_unit} = {result:.4f} {to_unit}"


# Tool registry
AVAILABLE_TOOLS = {
    "math_eval": {
        "name": "math_eval",
        "description": "Evaluate mathematical expressions. Supports standard math functions (sin, cos, sqrt, log, etc.)",
        "parameters": [
            {"name": "expression", "type": "str", "description": "Mathematical expression to evaluate"}
        ]
    },
    "unit_convert": {
        "name": "unit_convert",
        "description": "Convert between common measurement units",
        "parameters": [
            {"name": "value", "type": "float", "description": "Numeric value to convert"},
            {"name": "from_unit", "type": "str", "description": "Source unit"},
            {"name": "to_unit", "type": "str", "description": "Target unit"}
        ]
    }
}


# ====================== API Routes ======================

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/v1/get_config")
def get_config():
    """Return public application configuration."""
    return jsonify({
        "app_name": "NeuralTools",
        "version": APP_VERSION,
        "available_tools": list(AVAILABLE_TOOLS.keys()),
        "host": "0.0.0.0",
        "port": 80,
    })


@app.route("/api/v1/list_tools")
def list_tools():
    """List available tool functions and their parameters."""
    return jsonify({"tools": list(AVAILABLE_TOOLS.values())})


@app.route("/api/v1/execute_tool", methods=["POST"])
def execute_tool():
    """Execute a registered tool function with provided parameters."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"status": False, "error": "Invalid JSON payload"}), 400

    tool_name = data.get("tool_name", "")
    parameters = data.get("parameters", {})

    if tool_name not in AVAILABLE_TOOLS:
        return jsonify({"status": False, "error": f"Unknown tool: {tool_name}"}), 404

    try:
        if tool_name == "math_eval":
            expression = parameters.get("expression", "")
            if not isinstance(expression, str) or len(expression) == 0:
                return jsonify({"status": False, "error": "Parameter 'expression' is required"}), 400
            if len(expression) > 2048:
                return jsonify({"status": False, "error": "Expression too long"}), 400
            result = evaluate_math(expression)
            return jsonify({"status": True, "result": result})

        elif tool_name == "unit_convert":
            value = parameters.get("value")
            from_unit = parameters.get("from_unit", "")
            to_unit = parameters.get("to_unit", "")
            if value is None or not from_unit or not to_unit:
                return jsonify({"status": False, "error": "Parameters 'value', 'from_unit', and 'to_unit' are required"}), 400
            try:
                value = float(value)
            except (TypeError, ValueError):
                return jsonify({"status": False, "error": "Parameter 'value' must be numeric"}), 400
            result = unit_convert(value, from_unit, to_unit)
            return jsonify({"status": True, "result": result})

        else:
            return jsonify({"status": False, "error": "Tool not implemented"}), 501

    except Exception:
        return jsonify({"status": False, "error": "Internal tool execution error"}), 500


@app.route("/api/v1/version")
def get_version():
    return jsonify({"version": APP_VERSION})


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
