from auth.auth_config import AuthConfig

def setup_auth_config(auth_method, secret=None):
    """Configure authentication based on the specified method."""
    auth_config = AuthConfig()
    
    if auth_method == "none":
        auth_config.disable_auth()
        print("Running with no authentication - all endpoints are public")
    elif auth_method == "api_key":
        secret = secret or "your-secure-api-key"
        auth_config.configure_api_key(secret)
        print(f"Running with API Key authentication")
    elif auth_method == "jwt":
        secret = secret or "your-jwt-secret-key"
        auth_config.configure_jwt(secret)
        print(f"Running with JWT authentication")
    elif auth_method == "session":
        secret = secret or "your-session-secret-key"
        auth_config.configure_session(secret)
        print(f"Running with Session authentication")
    else:
        raise ValueError(f"Invalid authentication method: {auth_method}")
    
    return auth_config 