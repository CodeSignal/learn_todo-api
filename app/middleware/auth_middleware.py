from functools import wraps
from flask import request, jsonify, session, Blueprint
import jwt
from config.auth_config import AuthMethod, AuthConfig
from services.auth_service import blacklisted_tokens

class AuthMiddleware:
    def __init__(self, auth_config: AuthConfig):
        self.auth_config = auth_config

    def protect_blueprint(self, blueprint: Blueprint):
        @blueprint.before_request
        def verify_request():
            if self.auth_config.auth_method == AuthMethod.NONE:
                return None

            auth_handlers = {
                AuthMethod.API_KEY: self._handle_api_key,
                AuthMethod.JWT: self._handle_jwt,
                AuthMethod.SESSION: self._handle_session
            }

            handler = auth_handlers.get(self.auth_config.auth_method)
            if not handler:
                return jsonify({"error": "Invalid authentication method"}), 500

            result = handler()
            if result is not True:
                return result

            return None

    def _handle_api_key(self):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({"error": "API key is required"}), 401
        if api_key != self.auth_config.api_key:
            return jsonify({"error": "Invalid API key"}), 401
        return True

    def _handle_jwt(self):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "JWT token is required"}), 401
        
        token = auth_header.split(' ')[1]
        if token in blacklisted_tokens:
            return jsonify({"error": "You have been logged out. Please log in again."}), 401
        
        try:
            jwt.decode(
                token, 
                self.auth_config.jwt_secret, 
                algorithms=["HS256"],
                options={"verify_exp": True}
            )
            return True
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError as e:
            return jsonify({"error": f"Invalid JWT token: {str(e)}"}), 401

    def _handle_session(self):
        if not session.get('authenticated'):
            return jsonify({"error": "Valid session required"}), 401
        return True 