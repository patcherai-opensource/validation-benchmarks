import logging
import uuid
from datetime import datetime

from flask import Flask, jsonify, render_template, request

from promptforge.components import StaticRenderer, TemplateRenderer, VariableExtractor
from promptforge.components.template_renderer import TemplateValidationError

app = Flask(__name__)
app.config["SECRET_KEY"] = "pf-9x3k7m2v1q8w5r6t4y0u"

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("promptforge")

# Pre-configured pipeline templates (safe, using StaticRenderer)
PIPELINE_TEMPLATES = {
    "summarization": {
        "id": "summarization",
        "name": "Text Summarizer",
        "description": "Summarize the provided document text into key points.",
        "template": "Summarize the following text into {{ num_points }} key points:\n\n{{ document_text }}\n\nKey Points:",
        "variables": ["document_text", "num_points"],
        "category": "generation",
    },
    "translation": {
        "id": "translation",
        "name": "Language Translator",
        "description": "Translate text between languages.",
        "template": "Translate the following {{ source_language }} text to {{ target_language }}:\n\n{{ input_text }}\n\nTranslation:",
        "variables": ["input_text", "source_language", "target_language"],
        "category": "generation",
    },
    "extraction": {
        "id": "extraction",
        "name": "Entity Extractor",
        "description": "Extract named entities from the provided text.",
        "template": "Extract all {{ entity_type }} entities from the following text:\n\n{{ content }}\n\nEntities:",
        "variables": ["content", "entity_type"],
        "category": "analysis",
    },
    "classification": {
        "id": "classification",
        "name": "Text Classifier",
        "description": "Classify text into predefined categories.",
        "template": "Classify the following text into one of these categories: {{ categories }}.\n\nText: {{ input_text }}\n\nCategory:",
        "variables": ["input_text", "categories"],
        "category": "analysis",
    },
    "qa": {
        "id": "qa",
        "name": "Question Answering",
        "description": "Answer questions based on provided context documents.",
        "template": "Given the following context, answer the question.\n\nContext:\n{{ context }}\n\nQuestion: {{ question }}\n\nAnswer:",
        "variables": ["context", "question"],
        "category": "retrieval",
    },
}

# In-memory storage for custom pipeline runs
pipeline_runs = {}

# Initialize components
dynamic_renderer = TemplateRenderer()
variable_extractor = VariableExtractor()

# Initialize static renderers for each pre-configured template
static_renderers = {}
for tid, tpl in PIPELINE_TEMPLATES.items():
    static_renderers[tid] = StaticRenderer(
        template=tpl["template"],
        required_variables=tpl["variables"],
    )


@app.route("/")
def index():
    return render_template("index.html", pipelines=PIPELINE_TEMPLATES)


@app.route("/health")
def health():
    return jsonify({"status": "healthy", "version": "1.4.2"}), 200


@app.route("/api/v1/pipelines", methods=["GET"])
def list_pipelines():
    """List all available pipeline templates."""
    result = []
    for pid, p in PIPELINE_TEMPLATES.items():
        result.append({
            "id": p["id"],
            "name": p["name"],
            "description": p["description"],
            "variables": p["variables"],
            "category": p["category"],
        })
    return jsonify({"pipelines": result})


@app.route("/api/v1/pipelines/<pipeline_id>", methods=["GET"])
def get_pipeline(pipeline_id):
    """Get details of a specific pipeline template."""
    if pipeline_id not in PIPELINE_TEMPLATES:
        return jsonify({"error": "Pipeline not found"}), 404
    p = PIPELINE_TEMPLATES[pipeline_id]
    return jsonify({
        "id": p["id"],
        "name": p["name"],
        "description": p["description"],
        "template": p["template"],
        "variables": p["variables"],
        "category": p["category"],
    })


@app.route("/api/v1/pipelines/<pipeline_id>/run", methods=["POST"])
def run_pipeline(pipeline_id):
    """
    Execute a pre-configured pipeline with provided variables.
    Uses StaticRenderer (sandboxed) for safety.
    """
    if pipeline_id not in PIPELINE_TEMPLATES:
        return jsonify({"error": "Pipeline not found"}), 404

    data = request.get_json(silent=True) or {}
    variables = data.get("variables", {})

    renderer = static_renderers[pipeline_id]
    try:
        result = renderer.execute(template_variables=variables)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    run_id = str(uuid.uuid4())[:8]
    pipeline_runs[run_id] = {
        "run_id": run_id,
        "pipeline_id": pipeline_id,
        "output": result,
        "timestamp": datetime.utcnow().isoformat(),
    }

    return jsonify({
        "run_id": run_id,
        "pipeline_id": pipeline_id,
        "output": result,
    })


@app.route("/api/v1/render", methods=["POST"])
def render_custom_template():
    """
    Render a custom user-supplied template with provided variables.

    This endpoint allows advanced users to supply their own Jinja2 template
    strings for dynamic prompt engineering. The template is compiled and
    rendered with the provided variables.
    """
    data = request.get_json(silent=True) or {}
    template_text = data.get("template")
    variables = data.get("variables", {})

    if not template_text:
        return jsonify({"error": "Missing required field: template"}), 400

    if not isinstance(template_text, str):
        return jsonify({"error": "Field 'template' must be a string"}), 400

    if not isinstance(variables, dict):
        return jsonify({"error": "Field 'variables' must be an object"}), 400

    try:
        result = dynamic_renderer.execute(template_text, runtime_variables=variables)
    except TemplateValidationError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Template rendering failed"}), 500

    run_id = str(uuid.uuid4())[:8]
    pipeline_runs[run_id] = {
        "run_id": run_id,
        "pipeline_id": "custom",
        "output": result,
        "timestamp": datetime.utcnow().isoformat(),
    }

    return jsonify({
        "run_id": run_id,
        "output": result,
    })


@app.route("/api/v1/validate", methods=["POST"])
def validate_template():
    """
    Validate a Jinja2 template string and extract its variables.

    Returns the list of required variables found in the template.
    """
    data = request.get_json(silent=True) or {}
    template_text = data.get("template")

    if not template_text:
        return jsonify({"error": "Missing required field: template"}), 400

    try:
        variables = variable_extractor.extract(template_text)
        valid = True
    except ValueError as e:
        return jsonify({"valid": False, "error": str(e)}), 400

    return jsonify({
        "valid": valid,
        "variables": variables,
    })


@app.route("/api/v1/runs", methods=["GET"])
def list_runs():
    """List recent pipeline run results."""
    runs = sorted(pipeline_runs.values(), key=lambda r: r["timestamp"], reverse=True)[:20]
    return jsonify({"runs": runs})


@app.route("/api/v1/runs/<run_id>", methods=["GET"])
def get_run(run_id):
    """Get a specific pipeline run result."""
    if run_id not in pipeline_runs:
        return jsonify({"error": "Run not found"}), 404
    return jsonify(pipeline_runs[run_id])


@app.route("/playground")
def playground():
    """Interactive prompt engineering playground."""
    return render_template("playground.html", pipelines=PIPELINE_TEMPLATES)


@app.route("/docs")
def api_docs():
    """API documentation page."""
    return render_template("docs.html")


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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
