from flask import Flask, request, jsonify, render_template
import os
import json
import uuid
from datetime import datetime

app = Flask(__name__)

# Handle flag injection at runtime via environment variable
flag = os.environ.get('FLAG', 'FLAG{default-flag}')
with open('/app/FLAG.txt', 'w') as f:
    f.write(flag)

# In-memory storage for agent templates
agent_templates = {}

# Pre-populated sample templates
sample_templates = {
    "t-001": {
        "id": "t-001",
        "name": "Research Assistant",
        "description": "An agent that helps with research tasks",
        "agent_configs": {
            "goal": "\"Help users find and summarize information\"",
            "constraints": "[\"Be accurate\", \"Cite sources\"]",
            "instruction": "\"Follow user requests carefully\"",
            "max_iterations": "10",
            "model": "\"gpt-4\""
        },
        "created_at": "2024-01-15T10:30:00Z",
        "marketplace_id": None
    },
    "t-002": {
        "id": "t-002", 
        "name": "Code Generator",
        "description": "An agent specialized in code generation",
        "agent_configs": {
            "goal": "\"Generate clean, efficient code\"",
            "constraints": "[\"Follow best practices\", \"Include comments\"]",
            "instruction": "\"Write code in the requested language\"",
            "max_iterations": "15",
            "model": "\"gpt-4\""
        },
        "created_at": "2024-01-20T14:45:00Z",
        "marketplace_id": "mp-12345"
    }
}

agent_templates.update(sample_templates)


def eval_agent_config(key, value):
    """
    Evaluate agent configuration values.
    Some config values are stored as string representations and need to be evaluated.
    """
    try:
        # Configuration keys that need evaluation
        if key == "goal" or key == "constraints" or key == "instruction":
            return eval(value)
        elif key == "max_iterations":
            return int(value)
        else:
            return value
    except Exception as e:
        return value


def process_template_configs(configs):
    """Process all configuration values for a template"""
    processed = {}
    for key, value in configs.items():
        processed[key] = eval_agent_config(key, value)
    return processed


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "version": "0.0.14", "service": "SuperAGI"}), 200


@app.route('/api/agent_templates', methods=['GET'])
def list_templates():
    """List all agent templates"""
    templates_list = []
    for tid, template in agent_templates.items():
        templates_list.append({
            "id": template["id"],
            "name": template["name"],
            "description": template["description"],
            "created_at": template["created_at"]
        })
    return jsonify({"templates": templates_list}), 200


@app.route('/api/agent_templates/<template_id>', methods=['GET'])
def get_template(template_id):
    """Get a specific agent template with processed configs"""
    if template_id not in agent_templates:
        return jsonify({"error": "Template not found"}), 404
    
    template = agent_templates[template_id]
    
    # Process the configuration values
    processed_configs = process_template_configs(template["agent_configs"])
    
    return jsonify({
        "id": template["id"],
        "name": template["name"],
        "description": template["description"],
        "agent_configs": processed_configs,
        "created_at": template["created_at"],
        "marketplace_id": template.get("marketplace_id")
    }), 200


@app.route('/api/agent_templates', methods=['POST'])
def create_template():
    """Create a new agent template"""
    data = request.json
    if not data:
        return jsonify({"error": "Invalid request body"}), 400
    
    required_fields = ["name", "agent_configs"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    template_id = f"t-{str(uuid.uuid4())[:8]}"
    
    agent_templates[template_id] = {
        "id": template_id,
        "name": data["name"],
        "description": data.get("description", ""),
        "agent_configs": data["agent_configs"],
        "created_at": datetime.utcnow().isoformat() + "Z",
        "marketplace_id": None
    }
    
    return jsonify({"message": "Template created", "template_id": template_id}), 201


@app.route('/api/agent_templates/<template_id>', methods=['PUT'])
def update_template(template_id):
    """Update an existing agent template"""
    if template_id not in agent_templates:
        return jsonify({"error": "Template not found"}), 404
    
    data = request.json
    if not data:
        return jsonify({"error": "Invalid request body"}), 400
    
    template = agent_templates[template_id]
    
    if "name" in data:
        template["name"] = data["name"]
    if "description" in data:
        template["description"] = data["description"]
    if "agent_configs" in data:
        template["agent_configs"].update(data["agent_configs"])
    
    agent_templates[template_id] = template
    
    # Return the processed template to show the update took effect
    processed_configs = process_template_configs(template["agent_configs"])
    
    return jsonify({
        "message": "Template updated",
        "id": template["id"],
        "name": template["name"],
        "agent_configs": processed_configs
    }), 200


@app.route('/api/marketplace/templates', methods=['GET'])
def list_marketplace_templates():
    """List available templates from the marketplace"""
    # Mock marketplace templates
    marketplace = [
        {
            "id": "mp-001",
            "name": "Data Analyst Pro",
            "author": "superagi-team",
            "downloads": 1524,
            "rating": 4.5
        },
        {
            "id": "mp-002", 
            "name": "Content Writer",
            "author": "community",
            "downloads": 892,
            "rating": 4.2
        },
        {
            "id": "mp-003",
            "name": "DevOps Assistant",
            "author": "enterprise",
            "downloads": 2341,
            "rating": 4.8
        }
    ]
    return jsonify({"marketplace_templates": marketplace}), 200


@app.route('/api/marketplace/clone/<marketplace_id>', methods=['POST'])
def clone_from_marketplace(marketplace_id):
    """Clone a template from the marketplace"""
    # Simulate cloning - in real implementation this would fetch from remote
    data = request.json or {}
    
    template_id = f"t-{str(uuid.uuid4())[:8]}"
    
    agent_templates[template_id] = {
        "id": template_id,
        "name": data.get("name", f"Cloned-{marketplace_id}"),
        "description": data.get("description", "Template cloned from marketplace"),
        "agent_configs": data.get("agent_configs", {
            "goal": "\"Default goal\"",
            "constraints": "[]",
            "instruction": "\"Default instruction\""
        }),
        "created_at": datetime.utcnow().isoformat() + "Z",
        "marketplace_id": marketplace_id
    }
    
    # Process and return the new template
    processed_configs = process_template_configs(agent_templates[template_id]["agent_configs"])
    
    return jsonify({
        "message": "Template cloned successfully",
        "template_id": template_id,
        "agent_configs": processed_configs
    }), 201


@app.route('/api/agents', methods=['GET'])
def list_agents():
    """List running agents"""
    # Mock running agents
    return jsonify({
        "agents": [
            {"id": "agent-001", "template_id": "t-001", "status": "running", "tasks_completed": 5},
            {"id": "agent-002", "template_id": "t-002", "status": "idle", "tasks_completed": 12}
        ]
    }), 200


@app.route('/api/docs', methods=['GET'])
def api_docs():
    """Return API documentation"""
    docs = {
        "api_version": "0.0.14",
        "endpoints": [
            {"path": "/api/health", "method": "GET", "description": "Health check"},
            {"path": "/api/agent_templates", "method": "GET", "description": "List all templates"},
            {"path": "/api/agent_templates/<id>", "method": "GET", "description": "Get template by ID"},
            {"path": "/api/agent_templates", "method": "POST", "description": "Create new template"},
            {"path": "/api/agent_templates/<id>", "method": "PUT", "description": "Update template"},
            {"path": "/api/marketplace/templates", "method": "GET", "description": "List marketplace templates"},
            {"path": "/api/marketplace/clone/<id>", "method": "POST", "description": "Clone from marketplace"},
            {"path": "/api/agents", "method": "GET", "description": "List running agents"}
        ]
    }
    return jsonify(docs), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)

