# SPDX-FileCopyrightText: 2024-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0

import logging
import os

from flask import Flask, jsonify, render_template, request

from haystack_studio.components.builders.prompt_builder import PromptBuilder
from haystack_studio.components.builders.chat_prompt_builder import (
    ChatPromptBuilder,
    ChatMessage,
)
from haystack_studio.pipeline import PipelineManager, COMPONENT_REGISTRY

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config["PROPAGATE_EXCEPTIONS"] = False

pipeline_manager = PipelineManager()


@app.errorhandler(404)
def not_found(e):
    if request.path.startswith("/api/"):
        return jsonify({"error": "Not found"}), 404
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(e):
    if request.path.startswith("/api/"):
        return jsonify({"error": "Internal server error"}), 500
    return render_template("500.html"), 500


@app.after_request
def remove_server_header(response):
    response.headers.pop("Server", None)
    return response


# ─── Web UI Routes ──────────────────────────────────────────────────────────

@app.route("/")
def index():
    pipelines = pipeline_manager.list_pipelines()
    return render_template("index.html", pipelines=pipelines)


@app.route("/pipelines")
def pipelines_page():
    pipelines = pipeline_manager.list_pipelines()
    return render_template("pipelines.html", pipelines=pipelines)


@app.route("/pipelines/<pipeline_id>")
def pipeline_detail(pipeline_id):
    pipeline = pipeline_manager.get_pipeline(pipeline_id)
    if not pipeline:
        return render_template("404.html"), 404
    return render_template(
        "pipeline_detail.html",
        pipeline=pipeline.to_dict(),
        components=COMPONENT_REGISTRY,
    )


@app.route("/prompt-builder")
def prompt_builder_page():
    return render_template("prompt_builder.html")


@app.route("/components")
def components_page():
    return render_template("components.html", components=COMPONENT_REGISTRY)


# ─── API Routes ─────────────────────────────────────────────────────────────

@app.route("/api/v1/pipelines", methods=["GET"])
def api_list_pipelines():
    return jsonify({"pipelines": pipeline_manager.list_pipelines()})


@app.route("/api/v1/pipelines", methods=["POST"])
def api_create_pipeline():
    data = request.get_json()
    if not data or "name" not in data:
        return jsonify({"error": "Pipeline name is required"}), 400
    pipeline = pipeline_manager.create_pipeline(data["name"])
    return jsonify(pipeline.to_dict()), 201


@app.route("/api/v1/pipelines/<pipeline_id>", methods=["GET"])
def api_get_pipeline(pipeline_id):
    pipeline = pipeline_manager.get_pipeline(pipeline_id)
    if not pipeline:
        return jsonify({"error": "Pipeline not found"}), 404
    return jsonify(pipeline.to_dict())


@app.route("/api/v1/pipelines/<pipeline_id>", methods=["DELETE"])
def api_delete_pipeline(pipeline_id):
    if pipeline_manager.delete_pipeline(pipeline_id):
        return jsonify({"status": "deleted"})
    return jsonify({"error": "Pipeline not found"}), 404


@app.route("/api/v1/pipelines/<pipeline_id>/components", methods=["POST"])
def api_add_component(pipeline_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    component_name = data.get("name")
    component_type = data.get("type")
    init_params = data.get("init_parameters", {})

    if not component_name or not component_type:
        return jsonify({"error": "Component name and type are required"}), 400

    if component_type not in COMPONENT_REGISTRY:
        return jsonify({"error": f"Unknown component type: {component_type}"}), 400

    result = pipeline_manager.add_component_to_pipeline(
        pipeline_id, component_name, component_type, init_params
    )
    if result is None:
        return jsonify({"error": "Pipeline not found"}), 404
    return jsonify(result)


@app.route("/api/v1/components", methods=["GET"])
def api_list_components():
    return jsonify({"components": COMPONENT_REGISTRY})


@app.route("/api/v1/prompt/render", methods=["POST"])
def api_render_prompt():
    """
    Render a prompt template with the provided variables.

    Accepts a template string and variables, compiles the template,
    and returns the rendered output. Used for testing prompt templates
    before adding them to a pipeline.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    template_text = data.get("template")
    if not template_text:
        return jsonify({"error": "Template string is required"}), 400

    template_variables = data.get("template_variables", {})

    try:
        builder = PromptBuilder(template=template_text)
        result = builder.run(template_variables=template_variables)
        return jsonify({
            "rendered": result["prompt"],
            "variables_used": list(template_variables.keys()),
        })
    except Exception as e:
        return jsonify({"error": f"Template rendering failed: {str(e)}"}), 400


@app.route("/api/v1/prompt/validate", methods=["POST"])
def api_validate_prompt():
    """Validate a prompt template and extract its variables."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    template_text = data.get("template")
    if not template_text:
        return jsonify({"error": "Template string is required"}), 400

    try:
        builder = PromptBuilder(template=template_text)
        variables = builder.get_template_variables()
        return jsonify({
            "valid": True,
            "variables": variables,
        })
    except Exception as e:
        return jsonify({"error": f"Template validation failed: {str(e)}"}), 400


@app.route("/api/v1/chat/render", methods=["POST"])
def api_render_chat():
    """
    Render a chat prompt template with the provided variables.

    Accepts a list of message objects (role + content template) and variables,
    renders each message content as a Jinja2 template, and returns the result.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    messages_data = data.get("messages")
    if not messages_data or not isinstance(messages_data, list):
        return jsonify({"error": "Messages list is required"}), 400

    template_variables = data.get("template_variables", {})

    try:
        messages = []
        for msg in messages_data:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            messages.append(ChatMessage(role=role, content=content))

        builder = ChatPromptBuilder(template=messages)
        result = builder.run(template_variables=template_variables)
        return jsonify({"rendered": result["prompt"]})
    except Exception as e:
        return jsonify({"error": f"Chat rendering failed: {str(e)}"}), 400


@app.route("/api/v1/pipelines/<pipeline_id>/run", methods=["POST"])
def api_run_pipeline(pipeline_id):
    """Execute a pipeline's prompt builder component with given inputs."""
    pipeline = pipeline_manager.get_pipeline(pipeline_id)
    if not pipeline:
        return jsonify({"error": "Pipeline not found"}), 404

    data = request.get_json() or {}
    component_name = data.get("component", "prompt_builder")
    template_override = data.get("template")
    template_variables = data.get("template_variables", {})

    component = pipeline.components.get(component_name)
    if not component:
        return jsonify({"error": f"Component '{component_name}' not found in pipeline"}), 404

    try:
        result = component.run(
            template=template_override,
            template_variables=template_variables,
        )
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": f"Pipeline execution failed: {str(e)}"}), 400


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
