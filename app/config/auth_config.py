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

    def update_from_dict(self, config_dict):
        """Update authentication configuration from a dictionary.

        Args:
            config_dict (dict): Configuration dictionary with 'auth' key containing:
                - method: one of 'none', 'api_key', 'jwt', 'session'
                - api_key: API key (required if method is 'api_key')
                - secret: Secret key (required if method is 'jwt' or 'session')

        Raises:
            ValueError: If configuration is invalid
        """
        auth_config = config_dict.get('auth', {})
        method = auth_config.get('method', 'none')

        # Validate method
        valid_methods = [e.value for e in AuthMethod]
        if method not in valid_methods:
            raise ValueError(f"Invalid authentication method: {method}. Must be one of: {valid_methods}")

        # Reset current configuration
        self.auth_method = AuthMethod.NONE
        self.api_key = None
        self.jwt_secret = None
        self.session_secret = None

        # Apply new configuration
        if method == 'none':
            self.disable_auth()
        elif method == 'api_key':
            api_key = auth_config.get('api_key')
            if not api_key:
                raise ValueError("API key must be provided when using api_key authentication")
            self.configure_api_key(api_key)
        elif method == 'jwt':
            secret = auth_config.get('secret')
            if not secret:
                raise ValueError("Secret key must be provided when using JWT authentication")
            self.configure_jwt(secret)
        elif method == 'session':
            secret = auth_config.get('secret')
            if not secret:
                raise ValueError("Secret key must be provided when using session authentication")
            self.configure_session(secret)

    def to_dict(self):
        """Convert current configuration to dictionary format.

        Returns:
            dict: Configuration dictionary in the same format as the YAML file
        """
        config = {
            'auth': {
                'method': self.auth_method.value
            }
        }

        if self.auth_method == AuthMethod.API_KEY and self.api_key:
            config['auth']['api_key'] = self.api_key
        elif self.auth_method == AuthMethod.JWT and self.jwt_secret:
            config['auth']['secret'] = self.jwt_secret
        elif self.auth_method == AuthMethod.SESSION and self.session_secret:
            config['auth']['secret'] = self.session_secret

        return config
