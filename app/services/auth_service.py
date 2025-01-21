import jwt
import datetime
import secrets
from config.auth_config import AuthConfig, AuthMethod
from models.user import User
from flask import session, jsonify

# Initialize auth_config as None
auth_config = None

# List to store User objects
users = []

# In-memory store for refresh tokens and blacklisted tokens
refresh_tokens = {}
blacklisted_tokens = set()

def init_auth_service(config: AuthConfig):
    global auth_config
    auth_config = config

def generate_refresh_token(username):
    refresh_token = secrets.token_hex(32)
    refresh_tokens[refresh_token] = username
    return refresh_token

def validate_refresh_token(refresh_token):
    return refresh_tokens.get(refresh_token)

def blacklist_token(token):
    blacklisted_tokens.add(token)

def generate_jwt_token(username):
    access_token = jwt.encode(
        {
            "sub": username,
            "iat": datetime.datetime.utcnow(),
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=15)  # Shorter expiry for access token
        },
        auth_config.jwt_secret,
        algorithm="HS256"
    )
    refresh_token = generate_refresh_token(username)
    return access_token, refresh_token

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
    
    return jsonify({"message": "Signup successful. Please log in to continue."}), 201


def login_user(data):
    if not data or "username" not in data or "password" not in data:
        return jsonify({"error": "Username and password are required"}), 400
    
    if auth_config.auth_method == AuthMethod.JWT:
        access_token, refresh_token = generate_jwt_token(data["username"])
        return jsonify({
            "message": "Login successful",
            "access_token": access_token,
            "refresh_token": refresh_token
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