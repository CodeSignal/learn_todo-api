from flask import Flask
from routes.todos import todos_bp
from routes.errors import errors_bp
from routes.docs import docs_bp
from routes.notes import notes_bp
from routes.auth import auth_bp, init_auth_routes
from middleware.auth_middleware import AuthMiddleware
from utils.config import load_config, load_initial_todos, load_initial_users
from utils.auth import setup_auth_config
from services.auth_service import init_auth_service, add_user
from flasgger import Swagger
import secrets

def create_app(auth_config):
    """Create and configure the Flask application.
    
    This function:
    1. Creates a new Flask instance
    2. Configures app settings and secrets
    3. Sets up authentication middleware
    4. Registers blueprints with their URL prefixes
    
    Args:
        auth_config: Authentication configuration object
        
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Configure application settings
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    app.config['SECRET_KEY'] = secrets.token_hex(32)  # Generate secure random secret key
    app.config['auth_config'] = auth_config
    app.config['initial_todos'] = load_initial_todos()  # Load initial todos from config file
    
    # Configure Swagger
    template = {
        "swagger": "2.0",
        "info": {
            "title": "Todo API",
            "description": "A RESTful API for managing todos and notes",
            "version": "1.0.0"
        }
    }
    
    app.config['SWAGGER'] = {
        'title': 'Todo API',
        'uiversion': 3,
        'specs_route': '/',
        'url_prefix': '/swagger'
    }
    
    Swagger(app, template=template)
    
    # Set up authentication
    init_auth_routes(auth_config)
    auth_middleware = AuthMiddleware(auth_config)
    
    # Define routes that require authentication
    protected_blueprints = {
        todos_bp: "/todos",  # Todo management endpoints
        notes_bp: "/notes"   # Note management endpoints
    }
    
    # Register protected routes with authentication middleware
    for blueprint, url_prefix in protected_blueprints.items():
        auth_middleware.protect_blueprint(blueprint)
        app.register_blueprint(blueprint, url_prefix=url_prefix)

    # Register public routes (no authentication required)
    app.register_blueprint(auth_bp, url_prefix="/auth")  # Authentication endpoints
    app.register_blueprint(docs_bp, url_prefix="/docs")  # API documentation
    app.register_blueprint(errors_bp)  # Error handlers (no prefix needed)

    return app

def seed_users():
    for user_data in load_initial_users():
        if not add_user(user_data["username"], user_data["password"]):
            print(f"Error: Failed to add user on init")

if __name__ == "__main__":
    try:
        # Load authentication configuration from config file
        auth_method, secret = load_config()
        
        # Set up authentication based on configuration
        auth_config = setup_auth_config(auth_method, secret)
        seed_users()
        
        # Initialize auth service
        init_auth_service(auth_config)
        
        # Create and configure the application
        app = create_app(auth_config)
        
        # Start the server
        app.run(host="0.0.0.0", port=8000)  # Listen on all interfaces, port 8000
    except ValueError as e:
        print(f"Error: {e}")
        exit(1)
