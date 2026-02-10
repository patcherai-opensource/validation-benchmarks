from flask import Flask, request, jsonify, render_template
import os

app = Flask(__name__)

# Handle flag injection at runtime via environment variable
flag = os.environ.get('FLAG', 'FLAG{default-flag}')
with open('/app/FLAG.txt', 'w') as f:
    f.write(flag)

# In-memory storage for agent templates
agent_templates = {}
template_counter = 0


class AgentTemplate:
    """
    Agent Template model for storing and managing AI agent configurations.
    Based on the SuperAGI architecture for agent template management.
    """
    
    def __init__(self, name, description=None):
        self.name = name
        self.description = description
        self.configs = {}
    
    @staticmethod
    def eval_agent_config(key, value):
        """
        Evaluate agent configuration values.
        Certain fields require dynamic evaluation to support advanced configuration expressions.
        """
        # For these specific keys, we need to evaluate the value to support
        # dynamic configuration expressions (e.g., environment-based configs)
        if key == "goal" or key == "constraints" or key == "instruction":
            return eval(value)
        return value
    
    def set_config(self, key, value):
        """Set a configuration value for this template."""
        evaluated_value = self.eval_agent_config(key, value)
        self.configs[key] = evaluated_value
        return evaluated_value
    
    def get_config(self, key):
        """Get a configuration value."""
        return self.configs.get(key)
    
    def to_dict(self):
        """Convert template to dictionary representation."""
        return {
            "name": self.name,
            "description": self.description,
            "configs": self.configs
        }


@app.route('/api/agent_templates/create', methods=['POST'])
def create_agent_template():
    """Create a new agent template."""
    global template_counter
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    
    name = data.get('name')
    if not name:
        return jsonify({"error": "Template name is required"}), 400
    
    description = data.get('description', '')
    
    template_counter += 1
    template_id = template_counter
    
    template = AgentTemplate(name, description)
    agent_templates[template_id] = template
    
    return jsonify({
        "message": "Template created successfully",
        "template_id": template_id,
        "template": template.to_dict()
    }), 201


@app.route('/api/agent_templates/update_agent_template/<int:template_id>', methods=['PUT'])
def update_agent_template(template_id):
    """
    Update an agent template configuration.
    Supports setting goal, constraints, instruction, and other config fields.
    """
    if template_id not in agent_templates:
        return jsonify({"error": "Template not found"}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    
    template = agent_templates[template_id]
    agent_configs = data.get('agent_configs', {})
    
    results = {}
    for key, value in agent_configs.items():
        try:
            evaluated = template.set_config(key, value)
            results[key] = str(evaluated) if evaluated is not None else None
        except Exception as e:
            results[key] = f"Error: {str(e)}"
    
    return jsonify({
        "message": "Template updated",
        "template_id": template_id,
        "config_results": results,
        "template": template.to_dict()
    })


@app.route('/api/agent_templates/<int:template_id>', methods=['GET'])
def get_agent_template(template_id):
    """Get an agent template by ID."""
    if template_id not in agent_templates:
        return jsonify({"error": "Template not found"}), 404
    
    template = agent_templates[template_id]
    return jsonify({
        "template_id": template_id,
        "template": template.to_dict()
    })


@app.route('/api/agent_templates', methods=['GET'])
def list_agent_templates():
    """List all agent templates."""
    templates = []
    for tid, template in agent_templates.items():
        templates.append({
            "template_id": tid,
            "template": template.to_dict()
        })
    return jsonify({"templates": templates})


@app.route('/api/marketplace/clone_template', methods=['POST'])
def clone_template_from_marketplace():
    """
    Clone an agent template from the marketplace.
    This simulates importing templates from external sources.
    """
    global template_counter
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    
    name = data.get('name', 'Imported Template')
    description = data.get('description', '')
    agent_configs = data.get('agent_configs', {})
    
    template_counter += 1
    template_id = template_counter
    
    template = AgentTemplate(name, description)
    agent_templates[template_id] = template
    
    # Process imported configurations
    results = {}
    for key, value in agent_configs.items():
        try:
            evaluated = template.set_config(key, value)
            results[key] = str(evaluated) if evaluated is not None else None
        except Exception as e:
            results[key] = f"Error: {str(e)}"
    
    return jsonify({
        "message": "Template cloned from marketplace",
        "template_id": template_id,
        "config_results": results,
        "template": template.to_dict()
    }), 201


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/health')
def health():
    return jsonify({"status": "healthy"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)

