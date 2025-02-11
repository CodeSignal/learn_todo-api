import yaml
import os
import json
from pathlib import Path
from typing import List

INITIAL_USERS_FILE = "initial_users.json"
INITIAL_TODOS_FILE = "initial_todos.json"


def load_config():
    """Load configuration from auth_config.yml file."""
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'auth_config.yml')
    
    if not os.path.exists(config_path):
        print(f"Warning: auth_config.yml not found at {config_path}, using default configuration (no auth)")
        return "none", None
        
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            
        auth_config = config.get('auth', {})
        method = auth_config.get('method', 'none')
        
        if method == 'none':
            return method, None
            
        # Handle different authentication methods
        if method == 'api_key':
            secret = auth_config.get('api_key')
            if not secret:
                raise ValueError("API key must be provided when using api_key authentication")
        elif method in ['jwt', 'session']:
            secret = auth_config.get('secret')
            if not secret:
                raise ValueError(f"Secret key must be provided when using {method} authentication")
        else:
            raise ValueError(f"Invalid authentication method: {method}")
        
        return method, secret
    except Exception as e:
        print(f"Error loading auth_config.yml: {e}")
        print("Using default configuration (no auth)")
        return "none", None


def load_initial_todos():
    """Load initial todos from the configuration file."""
    path = Path(__file__).resolve().parents[2] / INITIAL_TODOS_FILE
    return load_initial_data(path, "todos")

def load_initial_users() -> List:
    path = Path(__file__).resolve().parents[2] / INITIAL_USERS_FILE
    return load_initial_data(path)

def load_initial_data(path: Path, data_key: str = "data") -> List:
    filename = path.name

    if not path.exists():
        print(f"Warning: {filename} not found at {path}, using empty list")
        return []

    try:
        with open(path, 'r') as f:
            data = json.load(f)
            return data.get(data_key, [])
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return []
