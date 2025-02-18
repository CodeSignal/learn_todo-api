from functools import wraps
from flask import request, jsonify, session, Blueprint
import jwt
from config.auth_config import AuthMethod, AuthConfig
from services.auth_service import blacklisted_tokens, invalidated_sessions

class AuthMiddleware:
    def __init__(self, config: AuthConfig):
        self.config = config

    def protect_blueprint(self, blueprint):
        """Add authentication middleware to all routes in a blueprint"""
        @blueprint.before_request
        @wraps(blueprint)
        def authenticate():
            if self.config.auth_method == AuthMethod.NONE:
                return None

            if self.config.auth_method == AuthMethod.API_KEY:
                return self._validate_api_key()
            elif self.config.auth_method == AuthMethod.JWT:
                return self._validate_jwt()
            elif self.config.auth_method == AuthMethod.SESSION:
                return self._validate_session()

    def _validate_api_key(self):
        """Validate API key from request header"""
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({"error": "API key is required"}), 401
        if api_key != self.config.api_key:
            return jsonify({"error": "Invalid API key"}), 401
        return None

    def _validate_jwt(self):
        """Validate JWT from Authorization header"""
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "JWT token is required"}), 401

        token = auth_header.split(' ')[1]
        if token in blacklisted_tokens:
            return jsonify({"error": "You have been logged out. Please log in again."}), 401

        try:
            jwt.decode(token, self.config.jwt_secret, algorithms=["HS256"])
            return None
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError as e:
            return jsonify({"error": f"Invalid JWT token: {str(e)}"}), 401

    def _validate_session(self):
        """Validate session authentication"""
        if not session.get("authenticated"):
            return jsonify({"error": "Valid session required"}), 401
            
        # Check if session has been invalidated
        current_session = request.cookies.get('session')
        if current_session and current_session in invalidated_sessions:
            session.clear()
            return jsonify({"error": "Session has been invalidated"}), 401
            
        return None 