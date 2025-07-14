import jwt
import datetime
import secrets
from config.auth_config import AuthConfig, AuthMethod
from models.user import User
from flask import session, jsonify, request

# --- Configuration ---
auth_config = None  # Global configuration object set during initialization

def init_auth_service(config: AuthConfig):
    global auth_config
    auth_config = config

# --- Storage ---
users = []  # In-memory storage for user objects
refresh_tokens = {}  # Maps refresh tokens to usernames
blacklisted_tokens = set()  # Set of invalidated access tokens
invalidated_sessions = set()  # Set of invalidated session IDs

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
    """Clear user session if authenticated and invalidate the session cookie"""
    if not session.get("authenticated"):
        return jsonify({"error": "Not authenticated"}), 401

    response = jsonify({"message": "Logout successful"})

    # Add current session ID to invalidated sessions set
    if request.cookies.get('session'):
        invalidated_sessions.add(request.cookies.get('session'))

    session.clear()
    # Set the session cookie to expire immediately
    response.set_cookie('session', '', expires=0)
    return response

def reset_auth_service(new_config: AuthConfig):
    """Reset the auth service with new configuration.

    This function:
    1. Updates the global auth_config
    2. Clears all existing tokens and sessions for security
    3. Re-initializes the auth service

    Args:
        new_config: New AuthConfig instance
    """
    global auth_config
    auth_config = new_config

    # Clear all existing authentication tokens and sessions for security
    # This ensures that after a config change, users need to re-authenticate
    refresh_tokens.clear()
    blacklisted_tokens.clear()
    invalidated_sessions.clear()

    print(f"Auth service reset with new configuration: {auth_config.auth_method.value}")

def reset_users(file_content):
    """Reset users with new data from uploaded JSON file.

    This method:
    1. Parses the JSON file content
    2. Validates the file format and user data
    3. Clears all existing users and their tokens/sessions
    4. Loads new users from the file data

    Args:
        file_content (str): JSON file content as string

    Returns:
        tuple: JSON response and status code
    """
    import json

    global users

    # Parse JSON content
    try:
        data = json.loads(file_content)
    except json.JSONDecodeError as e:
        return jsonify({"error": f"Invalid JSON format: {str(e)}"}), 400

    # Validate file structure - expect {"data": [...]} format (same as initial_users.json)
    if not isinstance(data, dict) or 'data' not in data:
        return jsonify({"error": "Invalid file format. Expected JSON with 'data' array field."}), 400

    new_users_data = data['data']

    # Validate the users data
    if not isinstance(new_users_data, list):
        return jsonify({"error": "Invalid users format. Expected an array of user objects."}), 400

    # Validate each user item
    for i, user_data in enumerate(new_users_data):
        if not isinstance(user_data, dict):
            return jsonify({"error": f"Invalid user at index {i}. Expected an object."}), 400

        required_fields = ['username', 'password']
        for field in required_fields:
            if field not in user_data:
                return jsonify({"error": f"Missing required field '{field}' in user at index {i}."}), 400

        # Validate field types
        if not isinstance(user_data['username'], str):
            return jsonify({"error": f"Invalid 'username' type in user at index {i}. Expected string."}), 400
        if not isinstance(user_data['password'], str):
            return jsonify({"error": f"Invalid 'password' type in user at index {i}. Expected string."}), 400

        # Validate username is not empty
        if not user_data['username'].strip():
            return jsonify({"error": f"Empty username in user at index {i}."}), 400
        if not user_data['password'].strip():
            return jsonify({"error": f"Empty password in user at index {i}."}), 400

    # Check for duplicate usernames
    usernames = [user['username'] for user in new_users_data]
    if len(usernames) != len(set(usernames)):
        return jsonify({"error": "Duplicate usernames found in the data."}), 400

    # Clear existing users and all authentication data for security
    users.clear()
    refresh_tokens.clear()
    blacklisted_tokens.clear()
    invalidated_sessions.clear()

    # Load new users
    for user_data in new_users_data:
        users.append(User(user_data['username'], user_data['password']))

    return jsonify({
        "message": f"Users reset successfully. Loaded {len(new_users_data)} users.",
        "users_count": len(new_users_data),
        "usernames": [user.username for user in users]
    }), 200
