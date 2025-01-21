from flask import Blueprint, request, jsonify, session
import jwt
import datetime
from config.auth_config import AuthMethod, AuthConfig
from services.auth_service import generate_jwt_token, is_username_taken, add_user, signup_user, login_user, logout_user, blacklist_token, validate_refresh_token, refresh_tokens

auth_bp = Blueprint("auth", __name__)
auth_config = None

def init_auth_routes(config: AuthConfig):
    global auth_config
    auth_config = config

@auth_bp.route("/signup", methods=["POST"])
def signup():
    if auth_config.auth_method == AuthMethod.API_KEY:
        return jsonify({"error": "Signup not available with API key authentication"}), 400
    
    data = request.get_json()
    return signup_user(data)

@auth_bp.route("/login", methods=["POST"])
def login():
    if auth_config.auth_method == AuthMethod.API_KEY:
        return jsonify({"error": "Login not available with API key authentication"}), 400
    
    data = request.get_json()
    return login_user(data)

@auth_bp.route("/refresh", methods=["POST"])
def refresh_token():
    data = request.get_json()
    refresh_token = data.get("refresh_token")
    username = validate_refresh_token(refresh_token)
    if not username:
        return jsonify({"error": "Invalid refresh token"}), 401
    
    access_token, new_refresh_token = generate_jwt_token(username)
    
    # Remove old refresh token and store new one
    if refresh_token in refresh_tokens:
        del refresh_tokens[refresh_token]
    
    return jsonify({
        "access_token": access_token,
        "refresh_token": new_refresh_token
    }), 200

@auth_bp.route("/logout", methods=["POST"])
def logout():
    if auth_config.auth_method == AuthMethod.API_KEY:
        return jsonify({"error": "Logout not available with API key authentication"}), 400
    
    elif auth_config.auth_method == AuthMethod.JWT:
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            blacklist_token(token)
        
        # Invalidate refresh token
        data = request.get_json()
        refresh_token = data.get("refresh_token")
        if refresh_token in refresh_tokens:
            del refresh_tokens[refresh_token]
        
        return jsonify({"message": "Logout successful"})
    
    elif auth_config.auth_method == AuthMethod.SESSION:
        session.clear()
        return jsonify({"message": "Logout successful"})
    
    return jsonify({"error": "Invalid authentication method"}), 500 