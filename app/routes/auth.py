from flask import Blueprint, request, jsonify, current_app
from config.auth_config import AuthMethod, AuthConfig
from middleware.auth_middleware import reset_auth_middleware
from services.auth_service import (
    signup_user,
    validate_refresh_token,
    generate_jwt_token,
    refresh_tokens,
    login_jwt,
    login_session,
    logout_jwt,
    logout_session,
    reset_users,
    reset_auth_service,
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

@auth_bp.route("/reset", methods=["POST"])
def reset_config():
    """
    Reset authentication configuration at runtime
    ---
    tags:
      - Authentication
    summary: Update authentication configuration at runtime
    description: |
      Updates the authentication configuration without restarting the server or
      modifying the original auth_config.yml file. All existing tokens and sessions
      are invalidated for security reasons.
    parameters:
      - in: body
        name: config
        description: Authentication configuration
        required: true
        schema:
          type: object
          required:
            - auth
          properties:
            auth:
              type: object
              required:
                - method
              properties:
                method:
                  type: string
                  enum: [none, api_key, jwt, session]
                  description: Authentication method to use
                api_key:
                  type: string
                  description: API key (required if method is api_key)
                secret:
                  type: string
                  description: Secret key (required if method is jwt or session)
              example:
                method: "api_key"
                api_key: "my-secure-api-key"
    responses:
      200:
        description: Configuration updated successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Authentication configuration updated successfully"
            new_config:
              type: object
              properties:
                auth:
                  type: object
                  properties:
                    method:
                      type: string
                    api_key:
                      type: string
                    secret:
                      type: string
      400:
        description: Invalid configuration or request format
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Invalid authentication method: invalid_method"
      415:
        description: Request must be JSON
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Request must be JSON"
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Failed to update configuration: Internal error"
    """

    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 415

    try:
        new_config = request.get_json()

        # Validate configuration format
        if not isinstance(new_config, dict) or 'auth' not in new_config:
            return jsonify({
                "error": "Invalid configuration format. Expected: {'auth': {'method': '...', ...}}"
            }), 400

        # Update the global auth configuration
        auth_config.update_from_dict(new_config)

        # Update the Flask app configuration
        current_app.config['auth_config'] = auth_config

        # Reset auth service with new configuration
        reset_auth_service(auth_config)

        # Reset auth middleware with new configuration
        reset_auth_middleware(auth_config)

        return jsonify({
            "message": "Authentication configuration updated successfully",
            "new_config": auth_config.to_dict()
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to update configuration: {str(e)}"}), 500

@auth_bp.route("/reset-users", methods=["POST"])
def reset_users_endpoint():
    """Reset users with data from uploaded JSON file
    ---
    tags:
      - Authentication
    summary: Reset all users with data from JSON file
    description: |
      Replaces all existing users with data from an uploaded JSON file.
      The original initial_users.json file remains unchanged.
      All existing authentication tokens and sessions are cleared for security.

      The uploaded file should be in the same format as initial_users.json:
      {
        "data": [
          {
            "username": "user1",
            "password": "password123"
          }
        ]
      }
    consumes:
      - multipart/form-data
    parameters:
      - in: formData
        name: file
        type: file
        required: true
        description: JSON file containing users data
    responses:
      200:
        description: Users reset successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Users reset successfully. Loaded 2 users."
            users_count:
              type: integer
              example: 2
            usernames:
              type: array
              items:
                type: string
              example: ["user1", "user2"]
            filename:
              type: string
              example: "my_users.json"
      400:
        description: Invalid file format or data
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Invalid JSON format: Expecting ',' delimiter"
      415:
        description: No file provided
        schema:
          type: object
          properties:
            error:
              type: string
              example: "No file provided"
    """

    # Check if file was uploaded
    if 'file' not in request.files:
        return jsonify({"error": "No file provided. Please upload a JSON file."}), 400

    file = request.files['file']

    # Check if file was actually selected
    if file.filename == '':
        return jsonify({"error": "No file selected. Please select a JSON file."}), 400

    # Check file extension
    if not file.filename.lower().endswith('.json'):
        return jsonify({"error": "Invalid file type. Please upload a JSON file."}), 400

    try:
        # Read file content
        file_content = file.read().decode('utf-8')

        # Reset users with file content
        response, status_code = reset_users(file_content)

        # Add filename to successful response
        if status_code == 200:
            response_data = response.get_json()
            response_data['filename'] = file.filename
            return jsonify(response_data), status_code

        return response, status_code

    except UnicodeDecodeError:
        return jsonify({"error": "Invalid file encoding. Please ensure the file is UTF-8 encoded."}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to process file: {str(e)}"}), 500
