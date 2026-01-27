from flask import Flask, request, jsonify, render_template
import os
import json

app = Flask(__name__)

# Handle flag injection at runtime via environment variable
flag = os.environ.get('FLAG', 'FLAG{default-flag}')
with open('/app/FLAG.txt', 'w') as f:
    f.write(flag)
os.chmod('/app/FLAG.txt', 0o600)

# In-memory storage for agent templates
agent_templates = {
    "1": {
        "id": "1",
        "name": "Research Assistant",
        "description": "An agent for research and summarization tasks",
        "goal": "Help users with research queries",
        "constraints": "Do not provide harmful information",
        "instruction": "Be concise and accurate",
        "created_by": "admin"
    },
    "2": {
        "id": "2", 
        "name": "Code Helper",
        "description": "An agent that assists with coding questions",
        "goal": "Assist with code review and debugging",
        "constraints": "Only work with provided code snippets",
        "instruction": "Follow best practices",
        "created_by": "admin"
    }
}

next_template_id = 3


class AgentTemplate:
    """Agent Template model for AI agent configurations"""
    
    @staticmethod
    def eval_agent_config(key, value):
        """
        Parse and evaluate agent configuration values.
        Certain fields may contain dynamic expressions for flexibility.
        """
        # For certain fields, we need to evaluate the value
        # to support dynamic configuration expressions
        if key in ("goal", "constraints", "instruction"):
            try:
                # Evaluate string representations of configuration
                return eval(value)
            except:
                # If evaluation fails, return as-is
                return value
        return value
    
    @staticmethod
    def process_template_config(config):
        """Process all configuration fields in a template"""
        processed = {}
        for key, value in config.items():
            if isinstance(value, str):
                processed[key] = AgentTemplate.eval_agent_config(key, value)
            else:
                processed[key] = value
        return processed


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/templates', methods=['GET'])
def list_templates():
    """List all available agent templates"""
    template_list = []
    for tid, template in agent_templates.items():
        template_list.append({
            "id": template["id"],
            "name": template["name"],
            "description": template["description"],
            "created_by": template["created_by"]
        })
    return jsonify({"templates": template_list, "count": len(template_list)})


@app.route('/api/templates/<template_id>', methods=['GET'])
def get_template(template_id):
    """Get a specific agent template by ID"""
    if template_id not in agent_templates:
        return jsonify({"error": "Template not found"}), 404
    
    template = agent_templates[template_id]
    # Process the template configuration when retrieving
    processed = AgentTemplate.process_template_config(template)
    return jsonify({"template": processed})


@app.route('/api/templates', methods=['POST'])
def create_template():
    """Create a new agent template"""
    global next_template_id
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON payload"}), 400
    
    required_fields = ["name", "description"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    template_id = str(next_template_id)
    next_template_id += 1
    
    new_template = {
        "id": template_id,
        "name": data.get("name"),
        "description": data.get("description"),
        "goal": data.get("goal", ""),
        "constraints": data.get("constraints", ""),
        "instruction": data.get("instruction", ""),
        "created_by": data.get("created_by", "anonymous")
    }
    
    agent_templates[template_id] = new_template
    return jsonify({"message": "Template created successfully", "template_id": template_id}), 201


@app.route('/api/templates/<template_id>', methods=['PUT'])
def update_template(template_id):
    """Update an existing agent template"""
    if template_id not in agent_templates:
        return jsonify({"error": "Template not found"}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON payload"}), 400
    
    template = agent_templates[template_id]
    
    # Update allowed fields
    updatable_fields = ["name", "description", "goal", "constraints", "instruction"]
    for field in updatable_fields:
        if field in data:
            template[field] = data[field]
    
    agent_templates[template_id] = template
    
    # Process and return the updated template
    processed = AgentTemplate.process_template_config(template)
    return jsonify({"message": "Template updated successfully", "template": processed})


@app.route('/api/templates/<template_id>/clone', methods=['POST'])
def clone_template(template_id):
    """Clone an existing template (simulating marketplace import)"""
    global next_template_id
    
    if template_id not in agent_templates:
        return jsonify({"error": "Source template not found"}), 404
    
    source = agent_templates[template_id]
    new_id = str(next_template_id)
    next_template_id += 1
    
    cloned = {
        "id": new_id,
        "name": source["name"] + " (Clone)",
        "description": source["description"],
        "goal": source["goal"],
        "constraints": source["constraints"],
        "instruction": source["instruction"],
        "created_by": "cloned"
    }
    
    agent_templates[new_id] = cloned
    
    # Process the cloned template
    processed = AgentTemplate.process_template_config(cloned)
    return jsonify({"message": "Template cloned successfully", "template": processed}), 201


@app.route('/api/marketplace/import', methods=['POST'])
def import_from_marketplace():
    """Import a template from external marketplace (simulated)"""
    global next_template_id
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON payload"}), 400
    
    if "agent_config" not in data:
        return jsonify({"error": "Missing agent_config in payload"}), 400
    
    config = data["agent_config"]
    
    template_id = str(next_template_id)
    next_template_id += 1
    
    new_template = {
        "id": template_id,
        "name": config.get("name", "Imported Template"),
        "description": config.get("description", "Imported from marketplace"),
        "goal": config.get("goal", ""),
        "constraints": config.get("constraints", ""),
        "instruction": config.get("instruction", ""),
        "created_by": "marketplace"
    }
    
    agent_templates[template_id] = new_template
    
    # Process the imported template to validate configuration
    processed = AgentTemplate.process_template_config(new_template)
    
    return jsonify({
        "message": "Template imported from marketplace",
        "template_id": template_id,
        "template": processed
    }), 201


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "version": "0.0.14"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)

