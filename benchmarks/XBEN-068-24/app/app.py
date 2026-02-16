import io
import os
import time
import json
from flask import Flask, request, jsonify, render_template

from safeexpr import ExpressionEngine

app = Flask(__name__)

MAX_CODE_LENGTH = 10000
MAX_EXECUTION_TIME = 10

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/v1/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "version": "2.4.1"})


@app.route('/api/v1/evaluate', methods=['POST'])
def evaluate_expression():
    """Evaluate a mathematical expression or script in the sandboxed engine."""
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    expression = data.get('expression', '')
    if not expression or not isinstance(expression, str):
        return jsonify({"error": "Missing or invalid 'expression' field"}), 400

    if len(expression) > MAX_CODE_LENGTH:
        return jsonify({"error": f"Expression exceeds maximum length of {MAX_CODE_LENGTH} characters"}), 400

    output_buffer = io.StringIO()
    err_buffer = io.StringIO()

    engine = ExpressionEngine(
        writer=output_buffer,
        err_writer=err_buffer,
        max_time=MAX_EXECUTION_TIME
    )

    try:
        result = engine.eval(expression, show_errors=False, raise_errors=False)
    except Exception:
        result = None

    stdout_output = output_buffer.getvalue()
    errors = err_buffer.getvalue()

    response = {"result": None, "output": stdout_output}

    if len(engine.error) > 0:
        err_msgs = []
        for e in engine.error:
            err_info = e.get_error()
            err_msgs.append(err_info[1])
        response["errors"] = err_msgs
    elif result is not None:
        try:
            json.dumps(result)
            response["result"] = result
        except (TypeError, ValueError):
            response["result"] = str(result)

    return jsonify(response)


@app.route('/api/v1/functions', methods=['GET'])
def list_functions():
    """List available built-in functions and constants."""
    engine = ExpressionEngine()
    functions = []
    constants = []
    for name, val in sorted(engine.symtable.items()):
        if callable(val):
            functions.append(name)
        elif isinstance(val, (int, float)):
            constants.append({"name": name, "value": val})
    return jsonify({"functions": functions, "constants": constants})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
