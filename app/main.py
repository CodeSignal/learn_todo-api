from flask import Flask
from routes.todos import todos_bp
from routes.errors import errors_bp
from routes.docs import docs_bp
from routes.notes import notes_bp
from routes.auth import auth_bp, init_auth_routes
from auth.auth_config import AuthConfig
from auth.middleware import AuthMiddleware
import secrets

def create_app(auth_config=None):
    app = Flask(__name__)
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    app.config['SECRET_KEY'] = secrets.token_hex(32)  # For session management

    # Configure authentication
    if auth_config is None:
        auth_config = AuthConfig()
        
    # Initialize auth routes with config
    init_auth_routes(auth_config)
        
    # Create auth middleware
    auth_middleware = AuthMiddleware(auth_config)
    
    # Register blueprints with authentication
    blueprints_with_auth = {
        todos_bp: "/todos",
        docs_bp: "/docs",
        notes_bp: "/notes"
    }
    
    for blueprint, url_prefix in blueprints_with_auth.items():
        # Protect the blueprint with authentication
        auth_middleware.protect_blueprint(blueprint)
        app.register_blueprint(blueprint, url_prefix=url_prefix)

    # Register auth routes (without auth protection)
    app.register_blueprint(auth_bp, url_prefix="/auth")

    # Register error handlers (without auth)
    app.register_blueprint(errors_bp)

    return app

# Example usage with different auth methods
if __name__ == "__main__":
    auth_config = AuthConfig()
    
    # Choose one of these authentication methods:
    
    # For API Key authentication:
    # auth_config.configure_api_key("your-secure-api-key")
    
    # For JWT authentication:
    # auth_config.configure_jwt("your-jwt-secret-key")
    
    # For Session authentication:
    # auth_config.configure_session("your-session-secret-key")
    
    # Or disable authentication:
    auth_config.disable_auth()
    
    app = create_app(auth_config)
    app.run(host="0.0.0.0", port=8000)
