from enum import Enum

class AuthMethod(Enum):
    API_KEY = "api_key"
    SESSION = "session"
    JWT = "jwt"
    NONE = "none"

class AuthConfig:
    def __init__(self):
        self.auth_method = AuthMethod.NONE
        self.api_key = None
        self.jwt_secret = None
        self.session_secret = None
        
    def configure_api_key(self, api_key):
        self.auth_method = AuthMethod.API_KEY
        self.api_key = api_key
        
    def configure_jwt(self, secret_key):
        self.auth_method = AuthMethod.JWT
        self.jwt_secret = secret_key
        
    def configure_session(self, secret_key):
        self.auth_method = AuthMethod.SESSION
        self.session_secret = secret_key
        
    def disable_auth(self):
        self.auth_method = AuthMethod.NONE 