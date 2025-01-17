from flask import Blueprint, jsonify

docs_bp = Blueprint("docs", __name__)

@docs_bp.route("", methods=["GET"])
def api_docs():
    """Provide comprehensive API documentation."""
    docs = {
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
    }
    return jsonify(docs), 200
