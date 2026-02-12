"""REST API routes for prompt generation."""

import logging
from flask import Blueprint, request, jsonify

from tasks import TASK_REGISTRY

logger = logging.getLogger("prompt_service.api")

api_bp = Blueprint("api", __name__)


@api_bp.route("/tasks", methods=["GET"])
def list_tasks():
    """List all available task types."""
    return jsonify({
        "tasks": list(TASK_REGISTRY.keys()),
        "version": "0.7.2",
    })


@api_bp.route("/tasks/<task_type>/generate", methods=["POST"])
def generate_prompt(task_type):
    """Generate a prompt for the specified task type.

    Expects JSON body with:
      - text (str): The input text to process
      - template (str, optional): Custom Jinja2 template override
      - labels (list, optional): Labels for NER/textcat tasks
      - examples (list, optional): Few-shot examples
      - Additional task-specific parameters
    """
    if task_type not in TASK_REGISTRY:
        return jsonify({
            "error": f"Unknown task type: {task_type}",
            "available_tasks": list(TASK_REGISTRY.keys()),
        }), 400

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    text = data.get("text")
    if not text:
        return jsonify({"error": "Field 'text' is required"}), 400

    task_cls = TASK_REGISTRY[task_type]

    # Build task constructor kwargs from request
    task_kwargs = {}
    if "template" in data:
        task_kwargs["template"] = data["template"]
    if "examples" in data:
        task_kwargs["prompt_examples"] = data["examples"]

    # Task-specific parameters
    if task_type == "ner":
        if "labels" in data:
            task_kwargs["labels"] = data["labels"]
        if "label_definitions" in data:
            task_kwargs["label_definitions"] = data["label_definitions"]
    elif task_type == "textcat":
        if "labels" in data:
            task_kwargs["labels"] = data["labels"]
        if "exclusive_classes" in data:
            task_kwargs["exclusive_classes"] = data["exclusive_classes"]
    elif task_type == "summarization":
        if "max_length" in data:
            task_kwargs["max_length"] = data["max_length"]
    elif task_type == "raw":
        if "field" in data:
            task_kwargs["field"] = data["field"]

    try:
        task = task_cls(**task_kwargs)
        rendered = task.generate_prompt(text, **{
            k: v for k, v in data.items()
            if k not in ("text", "template", "examples", "field")
        })
    except Exception as e:
        logger.warning("Prompt generation failed: %s", str(e))
        return jsonify({"error": "Template rendering failed"}), 400

    return jsonify({
        "task": task_type,
        "prompt": rendered,
    })


@api_bp.route("/render", methods=["POST"])
def render_template_endpoint():
    """Render a raw Jinja2 template with provided context variables.

    Expects JSON body with:
      - template (str): Jinja2 template string
      - context (dict, optional): Variables to pass to the template
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    template_str = data.get("template")
    if not template_str:
        return jsonify({"error": "Field 'template' is required"}), 400

    context = data.get("context", {})

    try:
        from tasks.builtin_task import BuiltinTask
        import jinja2
        environment = jinja2.Environment()
        tpl = environment.from_string(template_str)
        rendered = tpl.render(**context)
    except Exception as e:
        logger.warning("Template rendering failed: %s", str(e))
        return jsonify({"error": "Template rendering failed"}), 400

    return jsonify({
        "rendered": rendered,
    })
