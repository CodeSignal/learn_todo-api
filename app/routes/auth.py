from flask import Blueprint, request, jsonify
from config.auth_config import AuthMethod, AuthConfig
from services.auth_service import (
    signup_user,
    validate_refresh_token,
    generate_jwt_token,
    refresh_tokens,
    login_jwt,
    login_session,
    logout_jwt,
    logout_session
)

# --- Configuration ---
auth_bp = Blueprint("auth", __name__)  # Flask blueprint for auth routes
auth_config = None  # Global configuration object set during initialization

def init_auth_routes(config: AuthConfig):
    global auth_config
    auth_config = config

# --- Authentication Routes ---
@auth_bp.route("/signup", methods=["POST"])
def signup():
    """
    Register a new user
    Expects JSON: {"username": "user", "password": "pass"}
    """
    if auth_config.auth_method == AuthMethod.API_KEY:
        return jsonify({"error": "Signup not available with API key authentication"}), 400
    
    data = request.get_json()
    return signup_user(data)

@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Authenticate user and return tokens (JWT) or create session
    Expects JSON: {"username": "user", "password": "pass"}
    """
    if auth_config.auth_method == AuthMethod.API_KEY:
        return jsonify({"error": "Login not available with API key authentication"}), 400
    
    data = request.get_json()
    if not data or "username" not in data or "password" not in data:
        return jsonify({"error": "Username and password are required"}), 400
    
    username = data["username"]
    password = data["password"]
    
    if auth_config.auth_method == AuthMethod.JWT:
        return login_jwt(username, password)
    
    return login_session(username, password)

@auth_bp.route("/logout", methods=["POST"])
def logout():
    """
    End user session or invalidate JWT tokens
    For JWT: Requires Authorization header with Bearer token and refresh_token in JSON body
    For Session: No additional requirements
    """
    if auth_config.auth_method == AuthMethod.API_KEY:
        return jsonify({"error": "Logout not available with API key authentication"}), 400

    if auth_config.auth_method == AuthMethod.JWT:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Access token is required in Authorization header"}), 401
        access_token = auth_header.split(' ')[1]
        
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 415
        
        data = request.get_json()
        refresh_token = data.get("refresh_token")
        if not refresh_token:
            return jsonify({"error": "Refresh token is required in request body"}), 400
        
        return logout_jwt(access_token, refresh_token)
    
    return logout_session()

@auth_bp.route("/refresh", methods=["POST"])
def refresh_token():
    """
    Get new access token using refresh token
    Expects JSON: {"refresh_token": "token"}
    Returns: New access token and refresh token pair
    """
    data = request.get_json()
    refresh_token = data.get("refresh_token")
    username = validate_refresh_token(refresh_token)
    if not username:
        return jsonify({"error": "Invalid refresh token"}), 401
    
    access_token, new_refresh_token = generate_jwt_token(username)
    
    if refresh_token in refresh_tokens:
        del refresh_tokens[refresh_token]
    
    return jsonify({
        "access_token": access_token,
        "refresh_token": new_refresh_token
    }), 200 