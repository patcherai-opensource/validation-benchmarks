# encoding=utf8
# VyperCheck - Smart Contract Analyzer Service
# Simulates business logic bug inspired by CVE-2023-32059 (Vyper default argument miscompilation)

from flask import Flask, request, jsonify
import os
import re

def get_flag():
    """Get flag from environment variable or file"""
    flag = os.environ.get('FLAG', '')
    if not flag or flag == '@FLAG@':
        try:
            with open('secret.txt', 'r') as f:
                flag = f.read().strip()
        except:
            flag = 'FLAG{placeholder}'
    return flag

FLAG = get_flag()

app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True

# HTML Template for the main page
INDEX_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>VyperCheck - Smart Contract Analyzer</title>
    <style>
        body { font-family: 'Courier New', monospace; background: #1a1a2e; color: #eaeaea; margin: 0; padding: 20px; }
        .container { max-width: 900px; margin: 0 auto; }
        h1 { color: #00d4ff; text-align: center; }
        .description { background: #16213e; padding: 20px; border-radius: 8px; margin: 20px 0; }
        .endpoint { background: #0f3460; padding: 15px; border-radius: 5px; margin: 10px 0; border-left: 4px solid #00d4ff; }
        code { background: #0a0a15; padding: 2px 6px; border-radius: 3px; color: #00ff88; }
        pre { background: #0a0a15; padding: 15px; border-radius: 5px; overflow-x: auto; }
        a { color: #00d4ff; }
        .warning { color: #ff6b6b; }
    </style>
</head>
<body>
    <div class="container">
        <h1>&#128013; VyperCheck Smart Contract Analyzer</h1>
        <div class="description">
            <p>Welcome to VyperCheck! This service analyzes Vyper smart contract function calls 
            and validates parameter bindings against function signatures.</p>
            <p>Our analyzer helps detect issues with default parameter handling in internal function calls.</p>
        </div>
        
        <h2>API Endpoints</h2>
        
        <div class="endpoint">
            <h3>GET /api/functions</h3>
            <p>List available internal functions in the contract registry with their signatures.</p>
        </div>
        
        <div class="endpoint">
            <h3>POST /api/execute</h3>
            <p>Execute a function call. The system binds provided arguments and fills defaults for missing parameters.</p>
            <p><strong>Request Body (JSON):</strong></p>
            <pre>{
    "function_name": "view_contract",
    "args": ["my_contract"]
}</pre>
            <p><span class="warning">Note: Some functions require elevated permissions.</span></p>
        </div>
        
        <h2>Example</h2>
        <pre>
# List available functions
curl http://localhost:5000/api/functions

# Execute a function
curl -X POST http://localhost:5000/api/execute \\
    -H "Content-Type: application/json" \\
    -d '{"function_name": "view_contract", "args": ["my_contract"]}'
        </pre>
    </div>
</body>
</html>
"""

# Function registry with parameters and defaults
# The vulnerability: When a function is called with fewer args than params,
# defaults are applied LEFT-TO-RIGHT instead of RIGHT-TO-LEFT
# 
# Example: retrieve_data(query, role="viewer", limit=100)
# If called as retrieve_data("select *"), it SHOULD bind as:
#   query="select *", role="viewer", limit=100
# But due to the bug, it binds as:
#   query="select *", role="viewer", limit="viewer" (wrong! shifts defaults left)
#
# Exploitable function: get_vault_contents(vault_id, access_level="readonly", audit="enabled")  
# Requires access_level="admin" to return secrets
# If called with just vault_id, SHOULD get access_level="readonly"
# But if defaults are [vault_id_default, "readonly", "enabled"], the bug causes shift

FUNCTION_REGISTRY = {
    "view_contract": {
        "params": ["contract_name", "format"],
        "defaults": {"contract_name": "default", "format": "json"},
        "description": "View contract details",
        "handler": "handle_view_contract"
    },
    "check_balance": {
        "params": ["address", "token"],
        "defaults": {"address": "0x0", "token": "ETH"},
        "description": "Check token balance for an address",
        "handler": "handle_check_balance"
    },
    "get_vault_contents": {
        # params: vault_id, access_level, audit_mode
        # defaults: vault_id="public", access_level="readonly", audit_mode="enabled"
        # Correct call with 1 arg: vault_id=X, access_level="readonly", audit_mode="enabled"
        # Buggy call with 1 arg: vault_id=X, access_level="public" (WRONG!), audit_mode="readonly" (WRONG!)
        # 
        # To exploit: call with args=["admin"] 
        # The bug applies defaults left-to-right, so access_level gets the FIRST default ("public")
        # Wait, that's still not "admin"...
        #
        # Better design: Make it so calling with args=["secret_vault", "admin"] with bug gives admin access
        # where it shouldn't
        "params": ["vault_id", "access_level", "audit_mode"],
        "defaults": {"vault_id": "public", "access_level": "readonly", "audit_mode": "enabled"},
        "description": "Retrieve vault contents (requires access_level='admin' for sensitive vaults)",
        "handler": "handle_get_vault"
    },
    "admin_operation": {
        # This is the key exploitable function
        # params: [operation, target, role]
        # defaults: {operation: "status", target: "system", role: "admin"}
        # 
        # If you call with just 2 args: [op, tgt]
        # CORRECT: operation=op, target=tgt, role="admin" (default for role)
        # BUGGY: operation=op, target=tgt, role="status" (WRONG - takes first default)
        #
        # But we want to GAIN admin, not lose it...
        # 
        # Redesign: defaults should have role="guest" normally, but bug gives "admin"
        # params: [operation, role, audit]
        # defaults: {operation: "noop", role: "admin", audit: "on"}
        # If called with just [operation]: 
        # CORRECT: operation=X, role="admin", audit="on"
        # BUGGY: operation=X, role="noop"(?), audit="admin"(?)
        # 
        # That doesn't work either. Let me think differently...
        #
        # The CVE bug: defaults applied left-to-right instead of right-to-left
        # Given: params=[a, b, c], defaults=[d1, d2, d3]
        # Call with 1 arg [x]:
        # CORRECT: a=x, b=d2, c=d3  (fill b,c with their defaults)
        # BUGGY:   a=x, b=d1, c=d2  (defaults shift left)
        #
        # So to exploit: we need d1 to be a privileged value
        # params: [target, role, mode]
        # defaults: {target: "admin_vault", role: "guest", mode: "readonly"}
        # Call with 1 arg [x]:
        # CORRECT: target=x, role="guest", mode="readonly"
        # BUGGY:   target=x, role="admin_vault" (WHOOPS!), mode="guest"
        # If role="admin_vault" somehow maps to admin access... that's our exploit!
        "params": ["target", "role", "mode"],
        "defaults": {"target": "admin", "role": "guest", "mode": "safe"},
        "description": "Perform administrative operation",
        "handler": "handle_admin_op"
    }
}

def bind_arguments_buggy(params, defaults, provided_args):
    """
    BUGGY IMPLEMENTATION: Apply defaults LEFT-TO-RIGHT instead of RIGHT-TO-LEFT
    
    Given params = [a, b, c] with defaults = {a: d1, b: d2, c: d3}
    And call provides only one arg (x):
    
    CORRECT behavior: a=x, b=d2, c=d3 (x takes first param, rest get their own defaults)
    BUGGY behavior:   a=x, b=d1, c=d2 (defaults are shifted left)
    """
    result = {}
    
    # Get default values as ordered list
    default_values = [defaults.get(p) for p in params]
    
    # Bind provided arguments to first N parameters
    for i, arg in enumerate(provided_args):
        if i < len(params):
            result[params[i]] = arg
    
    # BUG: For remaining params, apply defaults LEFT-TO-RIGHT (shifting the default list)
    # Instead of using each param's own default, we take defaults starting from index 0
    remaining_params = params[len(provided_args):]
    for i, param in enumerate(remaining_params):
        # BUGGY: Use default_values[i] instead of defaults[param]
        # This shifts all defaults left when some args are provided
        if i < len(default_values):
            result[param] = default_values[i]
    
    return result

def bind_arguments_correct(params, defaults, provided_args):
    """Correct implementation for reference"""
    result = {}
    for i, arg in enumerate(provided_args):
        if i < len(params):
            result[params[i]] = arg
    for param in params[len(provided_args):]:
        if param in defaults:
            result[param] = defaults[param]
    return result

@app.route('/')
def index():
    return INDEX_HTML

@app.route('/api/functions', methods=['GET'])
def list_functions():
    """List available functions"""
    funcs = {}
    for name, info in FUNCTION_REGISTRY.items():
        funcs[name] = {
            "params": info["params"],
            "defaults": info["defaults"],
            "description": info["description"]
        }
    return jsonify({"functions": funcs})

@app.route('/api/execute', methods=['POST'])
def execute():
    """Execute a function call with buggy argument binding"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "JSON body required"}), 400
        
        func_name = data.get('function_name', '')
        args = data.get('args', [])
        
        if not func_name:
            return jsonify({"error": "function_name is required"}), 400
        
        if func_name not in FUNCTION_REGISTRY:
            return jsonify({"error": f"Unknown function: {func_name}. Use /api/functions to list available functions."}), 404
        
        func_info = FUNCTION_REGISTRY[func_name]
        params = func_info["params"]
        defaults = func_info["defaults"]
        
        # Apply buggy binding
        bound = bind_arguments_buggy(params, defaults, args)
        
        # Handle each function
        if func_name == "view_contract":
            return jsonify({
                "result": f"Contract '{bound.get('contract_name')}' in {bound.get('format')} format",
                "data": {"name": bound.get('contract_name'), "bytecode": "0x..."},
                "bound_arguments": bound
            })
        
        elif func_name == "check_balance":
            return jsonify({
                "result": f"Balance for {bound.get('address')}: 1000 {bound.get('token')}",
                "bound_arguments": bound
            })
        
        elif func_name == "get_vault_contents":
            vault_id = bound.get('vault_id', '')
            access_level = bound.get('access_level', 'readonly')
            audit_mode = bound.get('audit_mode', 'enabled')
            
            # This function requires admin access to be granted through the system
            # Simply passing access_level='admin' is not enough - you need a valid admin token
            return jsonify({
                "result": "Vault contents retrieved",
                "vault_id": vault_id,
                "contents": {"public_data": f"Data from vault {vault_id}"},
                "access_level": access_level,
                "audit_mode": audit_mode,
                "note": "Use admin_operation to access sensitive data",
                "bound_arguments": bound
            })
        
        elif func_name == "admin_operation":
            # params: [target, role, mode]
            # defaults: {target: "admin", role: "guest", mode: "safe"}
            # Call with 1 arg [x]:
            # CORRECT: target=x, role="guest", mode="safe"  
            # BUGGY:   target=x, role="admin"(!), mode="guest"
            # 
            # So calling with just ["read_secrets"] will give role="admin" due to bug!
            target = bound.get('target', '')
            role = bound.get('role', 'guest')
            mode = bound.get('mode', 'safe')
            
            if role == 'admin':
                if target == 'read_secrets':
                    return jsonify({
                        "result": "Admin operation successful",
                        "target": target,
                        "secrets": FLAG,
                        "bound_arguments": bound
                    })
                else:
                    return jsonify({
                        "result": f"Admin operation '{target}' completed",
                        "bound_arguments": bound
                    })
            else:
                return jsonify({
                    "error": "Insufficient permissions",
                    "your_role": role,
                    "required_role": "admin",
                    "bound_arguments": bound
                }), 403
        
        return jsonify({"error": "Function handler not implemented"}), 500
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/test/binding', methods=['POST'])
def test_binding():
    """Test endpoint to see how arguments get bound to parameters"""
    try:
        data = request.get_json()
        params = data.get('params', [])
        defaults = data.get('defaults', {})
        args = data.get('args', [])
        
        # Use the internal binding function
        result = bind_arguments_buggy(params, defaults, args)
        
        return jsonify({
            "input": {
                "params": params,
                "defaults": defaults,
                "provided_args": args
            },
            "bound_result": result
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
