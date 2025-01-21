from flask import Blueprint, request, jsonify, session
import jwt
import datetime
from config.auth_config import AuthMethod, AuthConfig
from services.auth_service import generate_jwt_token, is_username_taken, add_user, signup_user, login_user, logout_user

auth_bp = Blueprint("auth", __name__)
auth_config = None

def init_auth_routes(config: AuthConfig):
    global auth_config
    auth_config = config

def generate_jwt_token(username):
    return jwt.encode(
        {
            "sub": username,
            "iat": datetime.datetime.utcnow(),
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)
        },
        auth_config.jwt_secret,
        algorithm="HS256"
    )

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

@auth_bp.route("/logout", methods=["POST"])
def logout():
    if auth_config.auth_method == AuthMethod.API_KEY:
        return jsonify({"error": "Logout not available with API key authentication"}), 400
    
    elif auth_config.auth_method == AuthMethod.JWT:
        # JWT is stateless, so we can't really "logout"
        # In a real application, you might want to blacklist the token
        return jsonify({"message": "Logout successful"})
    
    elif auth_config.auth_method == AuthMethod.SESSION:
        session.clear()
        return jsonify({"message": "Logout successful"})
    
    return jsonify({"error": "Invalid authentication method"}), 500 