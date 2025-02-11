import os
from flask import Blueprint, current_app, json, Response
from config.auth_config import AuthMethod

docs_bp = Blueprint("docs", __name__)

def load_json_file(filename):
    """Load and parse a JSON file."""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

@docs_bp.route("", methods=["GET"])
def api_docs():
    """Provide comprehensive API documentation."""
    docs = {}
    
    # Load route documentation in specific order
    route_files = ['todos.json', 'notes.json']  # Define order explicitly
    docs_dir = os.path.join(current_app.root_path, '..', 'docs', 'routes')
    
    for filename in route_files:
        route_docs = load_json_file(os.path.join(docs_dir, filename))
        docs.update(route_docs)
    
    # Load authentication documentation
    auth_docs = _get_auth_docs()
    if auth_docs:
        docs["authentication"] = auth_docs
    
    return Response(
        json.dumps(docs, sort_keys=False, indent=2) + "\n",
        mimetype='application/json'
    ), 200

def _get_auth_docs():
    """Return authentication documentation based on current auth method."""
    auth_config = current_app.config.get('auth_config')
    if not auth_config or auth_config.auth_method == AuthMethod.NONE:
        return None
    
    auth_method_map = {
        AuthMethod.API_KEY: 'api_key',
        AuthMethod.JWT: 'jwt',
        AuthMethod.SESSION: 'session'
    }
    
    method_name = auth_method_map.get(auth_config.auth_method)
    if not method_name:
        return {"error": "Unknown authentication method"}
    
    auth_file = os.path.join(
        current_app.root_path, 
        '..', 
        'docs',
        'auth',
        f'{method_name}.json'
    )
    return load_json_file(auth_file)
