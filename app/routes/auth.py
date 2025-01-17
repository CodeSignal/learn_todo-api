from flask import Blueprint, request, jsonify, session
import jwt
import datetime
from auth.auth_config import AuthMethod, AuthConfig

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
    if not data or "username" not in data or "password" not in data:
        return jsonify({"error": "Username and password are required"}), 400
    
    # In a real application, you would:
    # 1. Check if username already exists
    # 2. Hash the password
    # 3. Store in database
    
    if auth_config.auth_method == AuthMethod.JWT:
        token = generate_jwt_token(data["username"])
        # Ensure token is a string
        return jsonify({
            "message": "Signup successful",
            "token": token if isinstance(token, str) else token.decode('utf-8')
        }), 201
    
    elif auth_config.auth_method == AuthMethod.SESSION:
        session["authenticated"] = True
        session["username"] = data["username"]
        return jsonify({"message": "Signup successful"}), 201
    
    return jsonify({"error": "Invalid authentication method"}), 500

@auth_bp.route("/login", methods=["POST"])
def login():
    if auth_config.auth_method == AuthMethod.API_KEY:
        return jsonify({"error": "Login not available with API key authentication"}), 400
    
    data = request.get_json()
    if not data or "username" not in data or "password" not in data:
        return jsonify({"error": "Username and password are required"}), 400
    
    # In a real application, you would:
    # 1. Verify username exists
    # 2. Verify password hash matches
    
    if auth_config.auth_method == AuthMethod.JWT:
        token = generate_jwt_token(data["username"])
        # Ensure token is a string
        return jsonify({
            "message": "Login successful",
            "token": token if isinstance(token, str) else token.decode('utf-8')
        })
    
    elif auth_config.auth_method == AuthMethod.SESSION:
        session["authenticated"] = True
        session["username"] = data["username"]
        return jsonify({"message": "Login successful"})
    
    return jsonify({"error": "Invalid authentication method"}), 500

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