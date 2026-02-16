import io
import json
from flask import Flask, render_template, request, jsonify
from safemath import ExprEngine

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/docs')
def api_docs():
    return render_template('api_docs.html')


@app.route('/api/health')
def health():
    return jsonify({"status": "ok", "engine": "safemath", "version": "1.0.2"})


@app.route('/api/compute', methods=['POST'])
def compute():
    content_type = request.content_type or ''

    if 'application/json' in content_type:
        data = request.get_json(silent=True) or {}
        expression = data.get('expression', '')
        multi_line = data.get('multi_line', False)
    else:
        expression = request.form.get('expression', '')
        multi_line = request.form.get('multi_line', '') == 'true'

    if not expression or not expression.strip():
        return jsonify({"error": "No expression provided"}), 400

    max_len = 50000 if multi_line else 2000
    if len(expression) > max_len:
        return jsonify({"error": "Expression exceeds maximum length"}), 400

    engine = ExprEngine()
    output_capture = io.StringIO()
    engine.writer = output_capture

    try:
        result = engine(expression)
    except Exception:
        result = None

    printed_output = output_capture.getvalue()
    errors = []
    for err in engine.error:
        errors.append(str(err.get_error()[1]))

    response = {}
    if printed_output:
        response['output'] = printed_output.rstrip('\n')
    if result is not None:
        response['result'] = repr(result)
    if errors:
        response['errors'] = errors
    if not response:
        response['result'] = 'None'

    return jsonify(response)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
