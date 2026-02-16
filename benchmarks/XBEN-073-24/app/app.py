import io
import time
from flask import Flask, render_template, request, jsonify

from asteval import Interpreter

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 64 * 1024


def _create_evaluator():
    """Create a fresh expression evaluator with standard math symbols."""
    interp = Interpreter()
    # Remove file I/O for security
    for sym in ('open', 'input', 'raw_input'):
        interp.symtable.pop(sym, None)
    return interp


# Shared evaluator for session-like state within a single evaluation request
_EVAL_TIMEOUT = 15  # seconds


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/health')
def health():
    return jsonify({"status": "ok"})


@app.route('/api/v1/docs')
def api_docs():
    return render_template('docs.html')


@app.route('/api/v1/evaluate', methods=['POST'])
def evaluate_expression():
    """Evaluate a mathematical expression or script using a safe interpreter."""
    content_type = request.content_type or ''

    if 'application/json' in content_type:
        data = request.get_json(silent=True)
        if data is None:
            return jsonify({"error": "Invalid JSON payload"}), 400
        expression = data.get('expression', '')
        multi = data.get('multiline', False)
    else:
        expression = request.form.get('expression', '')
        multi = request.form.get('multiline', '') in ('true', '1', 'on')

    if not expression or not expression.strip():
        return jsonify({"error": "No expression provided"}), 400

    if len(expression) > 50000:
        return jsonify({"error": "Expression too long (max 50000 chars)"}), 400

    evaluator = _create_evaluator()
    output_capture = io.StringIO()
    evaluator.writer = output_capture

    start_time = time.time()
    try:
        result = evaluator(expression)
        elapsed = time.time() - start_time
    except Exception:
        return jsonify({"error": "Evaluation failed due to an internal error"}), 500

    errors = []
    if evaluator.error:
        for err in evaluator.error:
            errors.append(str(err.get_error()[1]) if hasattr(err, 'get_error') else str(err))

    captured_output = output_capture.getvalue()

    response = {
        "result": repr(result) if result is not None else None,
        "output": captured_output if captured_output else None,
        "elapsed_ms": round(elapsed * 1000, 2),
    }
    if errors:
        response["errors"] = errors

    return jsonify(response)


@app.route('/api/v1/symbols', methods=['GET'])
def list_symbols():
    """List available built-in symbols and functions."""
    evaluator = _create_evaluator()
    symbols = {}
    for name, val in sorted(evaluator.symtable.items()):
        if name.startswith('_'):
            continue
        try:
            if callable(val):
                symbols[name] = "function"
            else:
                symbols[name] = type(val).__name__
        except Exception:
            symbols[name] = "unknown"
    return jsonify({"symbols": symbols})


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
