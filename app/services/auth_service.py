import jwt
import datetime
import secrets
from config.auth_config import AuthConfig, AuthMethod
from models.user import User
from flask import session, jsonify

# --- Configuration ---
auth_config = None  # Global configuration object set during initialization

def init_auth_service(config: AuthConfig):
    global auth_config
    auth_config = config

# --- Storage ---
users = []  # In-memory storage for user objects
refresh_tokens = {}  # Maps refresh tokens to usernames
blacklisted_tokens = set()  # Set of invalidated access tokens

# --- User Management ---
def is_username_taken(username):
    """Check if a username is already registered"""
    return any(user.username == username for user in users)

def add_user(username, password):
    """Add a new user if username is not taken"""
    if not is_username_taken(username):
        users.append(User(username, password))
        return True
    return False

def validate_credentials(username, password):
    """Verify username/password combination and return user if valid"""
    user = next((user for user in users if user.username == username), None)
    if not user or not user.check_password(password):
        return None
    return user

# --- Token Management ---
def generate_refresh_token(username):
    """Create and store a new refresh token for a user"""
    refresh_token = secrets.token_hex(32)
    refresh_tokens[refresh_token] = username
    return refresh_token

def validate_refresh_token(refresh_token):
    """Check if refresh token is valid and return associated username"""
    return refresh_tokens.get(refresh_token)

def blacklist_token(token):
    """Invalidate an access token"""
    blacklisted_tokens.add(token)

def generate_jwt_token(username):
    """Generate a new JWT access token and refresh token pair"""
    access_token = jwt.encode(
        {
            "sub": username,
            "iat": datetime.datetime.utcnow(),
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
        },
        auth_config.jwt_secret,
        algorithm="HS256"
    )
    refresh_token = generate_refresh_token(username)
    return access_token, refresh_token

# --- Authentication Operations ---
def signup_user(data):
    """Register a new user with username and password"""
    if not data or "username" not in data or "password" not in data:
        return jsonify({"error": "Username and password are required"}), 400
    
    if is_username_taken(data["username"]):
        return jsonify({"error": "Username already exists"}), 400
    
    add_user(data["username"], data["password"])
    return jsonify({"message": "Signup successful. Please log in to continue."}), 201

def login_jwt(username, password):
    """Authenticate user and return JWT tokens if valid"""
    user = validate_credentials(username, password)
    if not user:
        return jsonify({"error": "Invalid username or password"}), 401
    
    access_token, refresh_token = generate_jwt_token(username)
    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "refresh_token": refresh_token
    })

def login_session(username, password):
    """Authenticate user and create session if valid"""
    user = validate_credentials(username, password)
    if not user:
        return jsonify({"error": "Invalid username or password"}), 401
    
    session["authenticated"] = True
    session["username"] = username
    return jsonify({"message": "Login successful"})

def logout_jwt(access_token, refresh_token):
    """Invalidate JWT access and refresh tokens"""
    if not access_token or not refresh_token:
        return jsonify({"error": "Both access token and refresh token are required"}), 400
    
    blacklist_token(access_token)
    if refresh_token in refresh_tokens:
        del refresh_tokens[refresh_token]
    
    return jsonify({"message": "Logout successful"})

def logout_session():
    """Clear user session if authenticated"""
    if not session.get("authenticated"):
        return jsonify({"error": "Not authenticated"}), 401
    
    session.clear()
    return jsonify({"message": "Logout successful"}) 