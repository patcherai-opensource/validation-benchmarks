import io
import logging

from flask import Flask, render_template, request, jsonify
from asteval import Interpreter

app = Flask(__name__)
app.secret_key = "b9c1a7e3-4f2d-4821-9e6a-d8f5c3b7a190"

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("calcengine")

# Version and config
APP_VERSION = "2.4.1"
MAX_EXPR_LENGTH = 8192
EVAL_TIMEOUT = 30

# Preloaded standard library functions available in evaluator
STDLIB_DESCRIPTION = {
    "sin": "Sine function",
    "cos": "Cosine function",
    "tan": "Tangent function",
    "sqrt": "Square root",
    "log": "Natural logarithm",
    "log10": "Base-10 logarithm",
    "exp": "Exponential function",
    "abs": "Absolute value",
    "pi": "Pi constant (3.14159...)",
    "e": "Euler's number (2.71828...)",
    "asin": "Arc sine",
    "acos": "Arc cosine",
    "atan": "Arc tangent",
    "ceil": "Ceiling function",
    "floor": "Floor function",
    "round": "Rounding function",
}


def create_interpreter(writer=None):
    """Create a sandboxed asteval interpreter instance with filesystem access disabled."""
    kwargs = {}
    if writer is not None:
        kwargs["writer"] = writer
    aeval = Interpreter(**kwargs)
    # Remove filesystem and I/O functions that shouldn't be available in a calculator context
    for name in ("open", "fromfile", "loadtxt", "genfromtxt", "fromregex", "memmap", "fromstring"):
        aeval.symtable.pop(name, None)
    return aeval


def evaluate_expression(code):
    """Evaluate an expression in the asteval sandbox and capture output."""
    output_buffer = io.StringIO()
    aeval = create_interpreter(writer=output_buffer)

    result = aeval(code)

    printed = output_buffer.getvalue()
    errors = []
    for err in aeval.error:
        errors.append(str(err.get_error()[1]))

    return result, printed, errors


@app.route("/")
def index():
    return render_template("index.html", version=APP_VERSION)


@app.route("/api/evaluate", methods=["POST"])
def api_evaluate():
    """Evaluate a mathematical expression or program."""
    data = request.get_json(silent=True)
    if not data:
        data = {}

    code = data.get("expression", "") or data.get("code", "")
    if not code:
        return jsonify({"error": "No expression provided"}), 400

    if len(code) > MAX_EXPR_LENGTH:
        return jsonify({"error": f"Expression exceeds maximum length of {MAX_EXPR_LENGTH} characters"}), 400

    try:
        result, printed_output, errors = evaluate_expression(code)
    except Exception:
        return jsonify({"error": "Evaluation failed unexpectedly"}), 500

    response = {
        "result": repr(result) if result is not None else None,
        "output": printed_output if printed_output else None,
    }

    if errors:
        response["errors"] = errors

    return jsonify(response)


@app.route("/evaluate", methods=["POST"])
def evaluate():
    """Web form evaluation endpoint."""
    code = request.form.get("expression", "")
    if not code:
        return render_template("result.html", expression=code, error="No expression provided")

    if len(code) > MAX_EXPR_LENGTH:
        return render_template("result.html", expression=code,
                               error=f"Expression exceeds maximum length of {MAX_EXPR_LENGTH} characters")

    try:
        result, printed_output, errors = evaluate_expression(code)
    except Exception:
        return render_template("result.html", expression=code, error="Evaluation failed unexpectedly")

    return render_template("result.html",
                           expression=code,
                           result=result,
                           output=printed_output,
                           errors=errors)


@app.route("/api/stdlib")
def api_stdlib():
    """List available standard library functions."""
    return jsonify({"functions": STDLIB_DESCRIPTION})


@app.route("/docs")
def docs():
    return render_template("docs.html", version=APP_VERSION, functions=STDLIB_DESCRIPTION)


@app.route("/health")
def health():
    return jsonify({"status": "ok", "version": APP_VERSION})


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
