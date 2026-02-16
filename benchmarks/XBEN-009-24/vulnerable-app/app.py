"""
Prompt Workbench - NLP Prompt Engineering Platform

A web service for composing, previewing, and managing NLP prompt templates.
Supports custom Jinja2 templates for generating structured prompts used
with large language models.
"""

import logging
import os
import traceback

from flask import Flask, request, jsonify, render_template, abort

from prompt_engine.tasks.core_task import CoreTask
from prompt_engine.tasks.registry import TaskRegistry


app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(32).hex()

# Suppress default Flask banner
logging.getLogger("werkzeug").setLevel(logging.WARNING)
logger = logging.getLogger("prompt_workbench")
logger.setLevel(logging.INFO)


@app.errorhandler(404)
def not_found(e):
    if request.accept_mimetypes.best == "application/json":
        return jsonify({"error": "Not found"}), 404
    return render_template("error.html", code=404, message="Page not found"), 404


@app.errorhandler(500)
def server_error(e):
    if request.accept_mimetypes.best == "application/json":
        return jsonify({"error": "Internal server error"}), 500
    return render_template("error.html", code=500, message="Internal server error"), 500


@app.errorhandler(400)
def bad_request(e):
    return jsonify({"error": str(e.description)}), 400


@app.route("/")
def index():
    """Landing page showing available task types and API documentation."""
    tasks = TaskRegistry.list_tasks()
    return render_template("index.html", tasks=tasks)


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/api/v1/tasks", methods=["GET"])
def list_tasks():
    """List all available predefined task types."""
    tasks = TaskRegistry.list_tasks()
    return jsonify({"tasks": tasks})


@app.route("/api/v1/tasks/<task_name>/preview", methods=["POST"])
def preview_builtin_task(task_name):
    """Preview a prompt generated from a built-in task type.

    Expects JSON body with:
        - text (str): Input text for the prompt
        - examples (list, optional): Few-shot examples
        - extra (dict, optional): Additional template variables
    """
    task = TaskRegistry.get_task(task_name)
    if task is None:
        return jsonify({"error": f"Unknown task type: {task_name}"}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    text = data.get("text", "")
    if not text:
        return jsonify({"error": "Field 'text' is required"}), 400

    extra = data.get("extra", {})

    try:
        prompt = task.compose_prompt(text=text, **extra)
        return jsonify({
            "task": task_name,
            "prompt": prompt,
        })
    except Exception:
        return jsonify({"error": "Failed to render prompt template"}), 400


@app.route("/api/v1/compose", methods=["POST"])
def compose_prompt():
    """Compose a prompt from a user-provided template.

    Expects JSON body with:
        - template (str): Jinja2 template string
        - text (str): Input text to render into the template
        - examples (list, optional): Few-shot examples for the template
        - extra (dict, optional): Additional template variables
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    template_str = data.get("template")
    if not template_str:
        return jsonify({"error": "Field 'template' is required"}), 400

    text = data.get("text", "")
    if not text:
        return jsonify({"error": "Field 'text' is required"}), 400

    examples = data.get("examples", [])
    extra = data.get("extra", {})

    try:
        task = CoreTask(
            template=template_str,
            examples=examples,
        )
        prompt = task.compose_prompt(text=text, **extra)
        return jsonify({
            "prompt": prompt,
            "template_length": len(template_str),
        })
    except Exception:
        return jsonify({"error": "Template rendering failed. Check your template syntax."}), 400


@app.route("/api/v1/validate", methods=["POST"])
def validate_template():
    """Validate a Jinja2 template string without rendering it.

    Expects JSON body with:
        - template (str): Jinja2 template string to validate
    """
    import jinja2

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    template_str = data.get("template")
    if not template_str:
        return jsonify({"error": "Field 'template' is required"}), 400

    try:
        env = jinja2.Environment()
        env.parse(template_str)
        return jsonify({"valid": True, "message": "Template syntax is valid"})
    except jinja2.TemplateSyntaxError as e:
        return jsonify({
            "valid": False,
            "message": f"Syntax error at line {e.lineno}: {e.message}",
        })


@app.route("/docs")
def docs():
    """API documentation page."""
    return render_template("docs.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
