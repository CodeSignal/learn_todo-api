import jwt
import datetime
from auth.auth_config import AuthConfig, AuthMethod
from models.user import User
from flask import session, jsonify

# Initialize auth_config as None
auth_config = None

# List to store User objects
users = []

def init_auth_service(config: AuthConfig):
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

# Function to check if a username already exists
def is_username_taken(username):
    return any(user.username == username for user in users)

# Function to add a new user
def add_user(username, password):
    if not is_username_taken(username):
        users.append(User(username, password))
        return True
    return False

def signup_user(data):
    if not data or "username" not in data or "password" not in data:
        return jsonify({"error": "Username and password are required"}), 400
    
    if is_username_taken(data["username"]):
        return jsonify({"error": "Username already exists"}), 400
    
    add_user(data["username"], data["password"])
    
    if auth_config.auth_method == AuthMethod.JWT:
        token = generate_jwt_token(data["username"])
        return jsonify({
            "message": "Signup successful",
            "token": token if isinstance(token, str) else token.decode('utf-8')
        }), 201
    
    elif auth_config.auth_method == AuthMethod.SESSION:
        session["authenticated"] = True
        session["username"] = data["username"]
        return jsonify({"message": "Signup successful"}), 201
    
    return jsonify({"error": "Invalid authentication method"}), 500


def login_user(data):
    if not data or "username" not in data or "password" not in data:
        return jsonify({"error": "Username and password are required"}), 400
    
    if auth_config.auth_method == AuthMethod.JWT:
        token = generate_jwt_token(data["username"])
        return jsonify({
            "message": "Login successful",
            "token": token if isinstance(token, str) else token.decode('utf-8')
        })
    
    elif auth_config.auth_method == AuthMethod.SESSION:
        session["authenticated"] = True
        session["username"] = data["username"]
        return jsonify({"message": "Login successful"})
    
    return jsonify({"error": "Invalid authentication method"}), 500


def logout_user():
    if auth_config.auth_method == AuthMethod.JWT:
        return jsonify({"message": "Logout successful"})
    
    elif auth_config.auth_method == AuthMethod.SESSION:
        session.clear()
        return jsonify({"message": "Logout successful"})
    
    return jsonify({"error": "Invalid authentication method"}), 500 