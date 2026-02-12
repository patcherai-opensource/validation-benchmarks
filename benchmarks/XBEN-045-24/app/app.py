import os
import io
import json
import time
import logging
from flask import Flask, render_template, request, jsonify, session
from asteval import Interpreter

app = Flask(__name__)
app.secret_key = os.urandom(24)

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger('scicalc')

MAX_EXPR_LENGTH = 4096
EVAL_TIMEOUT = 30

EXAMPLE_EXPRESSIONS = [
    {"expr": "2 + 3 * 4", "desc": "Basic arithmetic"},
    {"expr": "sqrt(144) + log(e)", "desc": "Math functions"},
    {"expr": "sin(pi/4)**2 + cos(pi/4)**2", "desc": "Trigonometric identity"},
    {"expr": "sum([x**2 for x in range(10)])", "desc": "List comprehension"},
    {"expr": "def fib(n):\n  if n < 2:\n    return n\n  return fib(n-1)+fib(n-2)\nfib(10)", "desc": "Fibonacci function"},
]


def create_interpreter():
    output_buffer = io.StringIO()
    aeval = Interpreter(writer=output_buffer)
    return aeval, output_buffer


@app.route('/')
def index():
    return render_template('index.html', examples=EXAMPLE_EXPRESSIONS)


@app.route('/api/v1/evaluate', methods=['POST'])
def evaluate():
    try:
        data = request.get_json(silent=True)
        if data is None:
            data = {}
            data['expression'] = request.form.get('expression', '')

        expression = data.get('expression', '')

        if not expression or not expression.strip():
            return jsonify({
                'success': False,
                'error': 'Expression cannot be empty'
            }), 400

        if len(expression) > MAX_EXPR_LENGTH:
            return jsonify({
                'success': False,
                'error': f'Expression too long (max {MAX_EXPR_LENGTH} characters)'
            }), 400

        aeval, output_buffer = create_interpreter()
        start_time = time.time()
        result = aeval(expression)
        elapsed = time.time() - start_time

        if aeval.error:
            error_msgs = []
            for err in aeval.error:
                error_msgs.append(str(err.get_error()[1]))
            return jsonify({
                'success': False,
                'error': '; '.join(error_msgs),
                'elapsed_ms': round(elapsed * 1000, 2)
            })

        captured_output = output_buffer.getvalue()
        output_lines = captured_output.splitlines() if captured_output else []

        result_str = None
        if result is not None:
            try:
                result_str = repr(result)
            except Exception:
                result_str = str(result)

        return jsonify({
            'success': True,
            'result': result_str,
            'output': output_lines,
            'elapsed_ms': round(elapsed * 1000, 2)
        })

    except Exception:
        return jsonify({
            'success': False,
            'error': 'Internal evaluation error'
        }), 500


@app.route('/api/v1/examples', methods=['GET'])
def examples():
    return jsonify({'examples': EXAMPLE_EXPRESSIONS})


@app.route('/docs')
def docs():
    return render_template('docs.html')


@app.route('/health')
def health():
    return jsonify({'status': 'ok'}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
