from flask import Flask, request, jsonify, render_template
import os
import json
import uuid
from datetime import datetime

app = Flask(__name__)

agent_templates = {}

def eval_agent_config(key, value):
    """Evaluate agent configuration values for dynamic content.
    Similar to SuperAGI's AgentTemplate.eval_agent_config method."""
    if key == "goal" or key == "constraints" or key == "instruction":
        return eval(value)
    return value

def process_template_config(template_data):
    """Process template configuration and evaluate dynamic fields."""
    processed = {}
    agent_configs = template_data.get('agent_configs', {})
    
    for key, value in agent_configs.items():
        if isinstance(value, str):
            try:
                processed[key] = eval_agent_config(key, value)
            except Exception:
                processed[key] = value
        else:
            processed[key] = value
    
    return processed

@app.route('/api/agent_templates', methods=['GET'])
def list_agent_templates():
    """List all agent templates."""
    templates_list = []
    for tid, template in agent_templates.items():
        templates_list.append({
            'id': tid,
            'name': template.get('name', 'Unnamed'),
            'description': template.get('description', ''),
            'created_at': template.get('created_at', '')
        })
    return jsonify({'templates': templates_list})

@app.route('/api/agent_templates/create', methods=['POST'])
def create_agent_template():
    """Create a new agent template."""
    data = request.get_json()
    
    if not data or 'name' not in data:
        return jsonify({'error': 'Template name is required'}), 400
    
    template_id = str(uuid.uuid4())[:8]
    agent_templates[template_id] = {
        'name': data.get('name'),
        'description': data.get('description', ''),
        'agent_configs': data.get('agent_configs', {}),
        'created_at': datetime.now().isoformat()
    }
    
    return jsonify({'id': template_id, 'message': 'Template created successfully'})

@app.route('/api/agent_templates/<template_id>', methods=['GET'])
def get_agent_template(template_id):
    """Get a specific agent template by ID."""
    if template_id not in agent_templates:
        return jsonify({'error': 'Template not found'}), 404
    
    template = agent_templates[template_id]
    processed_config = process_template_config(template)
    
    return jsonify({
        'id': template_id,
        'name': template.get('name'),
        'description': template.get('description'),
        'agent_configs': template.get('agent_configs'),
        'processed_configs': processed_config,
        'created_at': template.get('created_at')
    })

@app.route('/api/agent_templates/update/<template_id>', methods=['PUT'])
def update_agent_template(template_id):
    """Update an existing agent template."""
    if template_id not in agent_templates:
        return jsonify({'error': 'Template not found'}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    template = agent_templates[template_id]
    
    if 'name' in data:
        template['name'] = data['name']
    if 'description' in data:
        template['description'] = data['description']
    if 'agent_configs' in data:
        template['agent_configs'] = data['agent_configs']
    
    template['updated_at'] = datetime.now().isoformat()
    
    processed_config = process_template_config(template)
    
    return jsonify({
        'id': template_id,
        'message': 'Template updated successfully',
        'processed_configs': processed_config
    })

@app.route('/api/agent_templates/clone_from_marketplace', methods=['POST'])
def clone_agent_template_from_marketplace():
    """Clone an agent template from the marketplace."""
    data = request.get_json()
    
    if not data or 'template' not in data:
        return jsonify({'error': 'Template data is required'}), 400
    
    marketplace_template = data['template']
    template_id = str(uuid.uuid4())[:8]
    
    agent_templates[template_id] = {
        'name': marketplace_template.get('name', 'Imported Template'),
        'description': marketplace_template.get('description', ''),
        'agent_configs': marketplace_template.get('agent_configs', {}),
        'created_at': datetime.now().isoformat(),
        'source': 'marketplace'
    }
    
    processed_config = process_template_config(agent_templates[template_id])
    
    return jsonify({
        'id': template_id,
        'message': 'Template cloned successfully',
        'processed_configs': processed_config
    })

@app.route('/api/agent_templates/delete/<template_id>', methods=['DELETE'])
def delete_agent_template(template_id):
    """Delete an agent template."""
    if template_id not in agent_templates:
        return jsonify({'error': 'Template not found'}), 404
    
    del agent_templates[template_id]
    return jsonify({'message': 'Template deleted successfully'})

@app.route('/')
def index():
    return render_template('index.html')

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)

