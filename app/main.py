from flask import Flask
from routes.todos import todos_bp
from routes.errors import errors_bp
from routes.docs import docs_bp
from routes.notes import notes_bp
from routes.auth import auth_bp, init_auth_routes
from auth.auth_config import AuthConfig, AuthMethod
from auth.middleware import AuthMiddleware
import secrets
import argparse

def create_app(auth_config):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    app.config['SECRET_KEY'] = secrets.token_hex(32)

    # Initialize authentication
    init_auth_routes(auth_config)
    auth_middleware = AuthMiddleware(auth_config)
    
    # Register blueprints
    protected_blueprints = {
        todos_bp: "/todos",
        docs_bp: "/docs",
        notes_bp: "/notes"
    }
    
    for blueprint, url_prefix in protected_blueprints.items():
        auth_middleware.protect_blueprint(blueprint)
        app.register_blueprint(blueprint, url_prefix=url_prefix)

    # Register unprotected routes
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(errors_bp)

    return app

def parse_arguments():
    """Parse command line arguments for authentication configuration."""
    parser = argparse.ArgumentParser(description='Run the Todo API')
    parser.add_argument('--auth', 
                       choices=['none', 'api_key', 'jwt', 'session'],
                       default='none',
                       help='Authentication method to use (default: none)')
    parser.add_argument('--secret',
                       help='Secret key for the chosen authentication method')
    return parser.parse_args()

def setup_auth_config(auth_method, secret=None):
    """Configure authentication based on the specified method."""
    auth_config = AuthConfig()
    
    if auth_method == "none":
        auth_config.disable_auth()
        print("Running with no authentication - all endpoints are public")
    elif auth_method == "api_key":
        secret = secret or "your-secure-api-key"
        auth_config.configure_api_key(secret)
        print(f"Running with API Key authentication (key: {secret})")
    elif auth_method == "jwt":
        secret = secret or "your-jwt-secret-key"
        auth_config.configure_jwt(secret)
        print(f"Running with JWT authentication (secret: {secret})")
    elif auth_method == "session":
        secret = secret or "your-session-secret-key"
        auth_config.configure_session(secret)
        print(f"Running with Session authentication (secret: {secret})")
    else:
        raise ValueError(f"Invalid authentication method: {auth_method}")
    
    return auth_config

if __name__ == "__main__":
    args = parse_arguments()
    
    try:
        auth_config = setup_auth_config(args.auth, args.secret)
        app = create_app(auth_config)
        app.run(host="0.0.0.0", port=8000)
    except ValueError as e:
        print(f"Error: {e}")
        exit(1)
