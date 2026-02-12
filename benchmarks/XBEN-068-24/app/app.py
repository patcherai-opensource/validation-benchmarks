from flask import Flask, request, jsonify, render_template
import math
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Version info
APP_VERSION = "9.8"


def calculate(expression: str) -> str:
    """
    Attempt to evaluate a mathematical expression safely.
    Only math module functions are allowed.
    """
    try:
        # Build the allowed names from the math module
        allowed_names = {name: getattr(math, name) for name in dir(math) if not name.startswith("_")}
        # Evaluate the expression in a restricted environment
        result = eval(expression, {"__builtins__": None}, allowed_names)
        return str(result)
    except Exception as ex:
        return f"Error: {ex}"


calculate_function = {
    "function_name": "calculate",
    "function": calculate,
    "function_description": "Evaluate a mathematical expression. Supported functions include all standard math operations (sin, cos, tan, sqrt, log, pow, etc.).",
    "function_parameters": [
        {
            "name": "expression",
            "type": "str",
            "description": "A mathematical expression to evaluate (e.g., 'sqrt(144) + pow(2, 10)')"
        }
    ]
}

# Registry of available tool functions
TOOL_FUNCTIONS = {
    "calculate": calculate_function,
}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/v1/tools", methods=["GET"])
def list_tools():
    """List all available tool functions."""
    tools = []
    for name, tool in TOOL_FUNCTIONS.items():
        tools.append({
            "name": name,
            "description": tool["function_description"],
            "parameters": tool["function_parameters"]
        })
    return jsonify({"tools": tools})


@app.route("/api/v1/execute", methods=["POST"])
def execute_tool():
    """Execute a registered tool function with given parameters."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    function_name = data.get("function_name")
    parameters = data.get("parameters", {})

    if not function_name:
        return jsonify({"error": "Missing 'function_name' field"}), 400

    tool = TOOL_FUNCTIONS.get(function_name)
    if not tool:
        return jsonify({"error": f"Unknown function: {function_name}"}), 404

    try:
        fn = tool["function"]
        result = fn(**parameters)
        return jsonify({"function_name": function_name, "result": result})
    except TypeError as e:
        return jsonify({"error": f"Invalid parameters: {e}"}), 400
    except Exception as e:
        logger.error(f"Error executing {function_name}: {e}")
        return jsonify({"error": "Internal execution error"}), 500


@app.route("/api/v1/version", methods=["GET"])
def version():
    """Return application version info."""
    return jsonify({
        "name": "LoLLMs Tools Server",
        "version": APP_VERSION,
        "status": "running"
    })


@app.route("/ping")
def ping():
    return "pong", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)

