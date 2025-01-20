from flask import Flask
from routes.todos import todos_bp
from routes.errors import errors_bp
from routes.docs import docs_bp
from routes.notes import notes_bp
from routes.auth import auth_bp, init_auth_routes
from auth.auth_config import AuthConfig, AuthMethod
from auth.middleware import AuthMiddleware
import secrets
import yaml
import os

def create_app(auth_config):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    app.config['SECRET_KEY'] = secrets.token_hex(32)
    app.config['auth_config'] = auth_config

    # Initialize authentication
    init_auth_routes(auth_config)
    auth_middleware = AuthMiddleware(auth_config)
    
    # Register protected blueprints
    protected_blueprints = {
        todos_bp: "/todos",
        notes_bp: "/notes"
    }
    
    for blueprint, url_prefix in protected_blueprints.items():
        auth_middleware.protect_blueprint(blueprint)
        app.register_blueprint(blueprint, url_prefix=url_prefix)

    # Register unprotected routes
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(docs_bp, url_prefix="/docs")
    app.register_blueprint(errors_bp)

    return app

def load_config():
    """Load configuration from config.yml file."""
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yml')
    
    if not os.path.exists(config_path):
        print(f"Warning: config.yml not found at {config_path}, using default configuration (no auth)")
        return "none", None
        
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            
        auth_config = config.get('auth', {})
        method = auth_config.get('method', 'none')
        secret = auth_config.get('secret')
        
        return method, secret
    except Exception as e:
        print(f"Error loading config.yml: {e}")
        print("Using default configuration (no auth)")
        return "none", None

def setup_auth_config(auth_method, secret=None):
    """Configure authentication based on the specified method."""
    auth_config = AuthConfig()
    
    if auth_method == "none":
        auth_config.disable_auth()
        print("Running with no authentication - all endpoints are public")
    elif auth_method == "api_key":
        secret = secret or "your-secure-api-key"
        auth_config.configure_api_key(secret)
        print(f"Running with API Key authentication")
    elif auth_method == "jwt":
        secret = secret or "your-jwt-secret-key"
        auth_config.configure_jwt(secret)
        print(f"Running with JWT authentication")
    elif auth_method == "session":
        secret = secret or "your-session-secret-key"
        auth_config.configure_session(secret)
        print(f"Running with Session authentication")
    else:
        raise ValueError(f"Invalid authentication method: {auth_method}")
    
    return auth_config

if __name__ == "__main__":
    try:
        auth_method, secret = load_config()
        auth_config = setup_auth_config(auth_method, secret)
        app = create_app(auth_config)
        app.run(host="0.0.0.0", port=8000)
    except ValueError as e:
        print(f"Error: {e}")
        exit(1)
