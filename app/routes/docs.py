from flask import Blueprint, current_app, json, Response
from config.auth_config import AuthMethod

docs_bp = Blueprint("docs", __name__)

@docs_bp.route("", methods=["GET"])
def api_docs():
    """Provide comprehensive API documentation."""
    docs = {}
    
    auth_docs = _get_auth_docs()
    if auth_docs:
        docs["authentication"] = auth_docs
        
    docs.update({
        "/todos": {
            "GET": {
                "description": "Fetch all TODO items with optional filtering and pagination.",
                "query_params": {
                    "done": "Filter by completion status (true/false).",
                    "title": "Filter by TODO item title prefix.",
                    "page": "Page number for pagination (optional, starts at 1).",
                    "limit": "Number of items per page (optional)."
                },
                "responses": {
                    "200": "List of todo items"
                }
            },
            "POST": {
                "description": "Add a new TODO item.",
                "body_params": {
                    "title": "The TODO item title (required).",
                    "done": "Completion status (optional, default: false).",
                    "description": "Detailed TODO item description (optional)."
                },
                "responses": {
                    "201": "Created todo item",
                    "400": "Invalid request (missing title)"
                }
            }
        },
        "/todos/<int:todo_id>": {
            "GET": {
                "description": "Fetch a single TODO item by its ID.",
                "responses": {
                    "200": "Todo item",
                    "404": "Todo not found"
                }
            },
            "PUT": {
                "description": "Replace an existing TODO item by its ID (all fields required).",
                "body_params": {
                    "title": "The TODO item title (required).",
                    "done": "Completion status (required).",
                    "description": "Detailed TODO item description (required)."
                },
                "responses": {
                    "200": "Updated todo item",
                    "400": "Invalid request (missing required fields)",
                    "404": "Todo not found"
                }
            },
            "PATCH": {
                "description": "Update part of a TODO item by its ID (any field can be provided).",
                "body_params": {
                    "title": "The TODO item title (optional).",
                    "done": "Completion status (optional).",
                    "description": "Detailed TODO item description (optional)."
                },
                "responses": {
                    "200": "Updated todo item",
                    "400": "Invalid request (empty body)",
                    "404": "Todo not found"
                }
            },
            "DELETE": {
                "description": "Delete a TODO item by its ID.",
                "responses": {
                    "204": "Todo deleted successfully",
                    "404": "Todo not found"
                }
            }
        },
        "/notes": {
            "POST": {
                "description": "Upload a new note file.",
                "content_type": "multipart/form-data",
                "form_params": {
                    "file": "The .txt file to upload (required, max size: 1MB)"
                },
                "responses": {
                    "201": "Note created successfully",
                    "400": "Invalid request (empty file, wrong format, etc.)"
                }
            }
        },
        "/notes/<note_name>": {
            "GET": {
                "description": "Download a note by its name.",
                "responses": {
                    "200": "Note file content",
                    "404": "Note not found"
                }
            },
            "DELETE": {
                "description": "Delete a note by its name.",
                "responses": {
                    "204": "Note deleted successfully",
                    "404": "Note not found"
                }
            }
        }
    })
    return Response(
        json.dumps(docs, sort_keys=False, indent=2) + "\n",
        mimetype='application/json'
    ), 200

def _get_auth_docs():
    """Return authentication documentation based on current auth method."""
    auth_config = current_app.config.get('auth_config')
    if not auth_config or auth_config.auth_method == AuthMethod.NONE:
        return None
    
    auth_docs = {
        AuthMethod.API_KEY: {
            "method": "api_key",
            "description": "API Key authentication required for protected endpoints.",
            "how_to_authenticate": "Include your API key in the X-API-Key header for all requests.",
            "example": {
                "headers": {
                    "X-API-Key": "your-api-key-here"
                }
            },
            "protected_endpoints": ["/todos/*", "/notes/*"]
        },
        AuthMethod.JWT: {
            "method": "jwt",
            "description": "JWT (JSON Web Token) authentication required for protected endpoints.",
            "how_to_authenticate": "1. Get a token via /auth/login or /auth/signup\n2. Include the token in the Authorization header.",
            "endpoints": {
                "/auth/signup": {
                    "method": "POST",
                    "body": {"username": "string", "password": "string"},
                    "response": {"token": "string"}
                },
                "/auth/login": {
                    "method": "POST",
                    "body": {"username": "string", "password": "string"},
                    "response": {"token": "string"}
                }
            },
            "example": {
                "headers": {
                    "Authorization": "Bearer your-jwt-token-here"
                }
            },
            "protected_endpoints": ["/todos/*", "/notes/*"]
        },
        AuthMethod.SESSION: {
            "method": "session",
            "description": "Session-based authentication required for protected endpoints.",
            "how_to_authenticate": "1. Login via /auth/login or signup via /auth/signup\n2. Session cookie will be automatically managed by your browser.",
            "endpoints": {
                "/auth/signup": {
                    "method": "POST",
                    "body": {"username": "string", "password": "string"}
                },
                "/auth/login": {
                    "method": "POST",
                    "body": {"username": "string", "password": "string"}
                },
                "/auth/logout": {
                    "method": "POST"
                }
            },
            "protected_endpoints": ["/todos/*", "/notes/*"]
        }
    }
    
    return auth_docs.get(auth_config.auth_method, {"error": "Unknown authentication method"})
