from flask import Blueprint, jsonify

docs_bp = Blueprint("docs", __name__)

@docs_bp.route("", methods=["GET"])
def api_docs():
    """Provide comprehensive API documentation."""
    docs = {
        "/todos": {
            "GET": {
                "description": "Fetch all TODO items.",
                "query_params": {
                    "done": "Filter by completion status (true/false).",
                    "title": "Filter by TODO item title prefix."
                }
            },
            "POST": {
                "description": "Add a new TODO item.",
                "body_params": {
                    "title": "The TODO item title (required).",
                    "done": "Completion status (optional, default: false).",
                    "description": "Detailed TODO item description (optional)."
                }
            }
        },
        "/todos/<int:todo_id>": {
            "GET": {
                "description": "Fetch a single TODO item by its ID."
            },
            "PUT": {
                "description": "Replace an existing TODO item by its ID (all fields required).",
                "body_params": {
                    "title": "The TODO item title (required).",
                    "done": "Completion status (required).",
                    "description": "Detailed TODO item description (required)."
                }
            },
            "PATCH": {
                "description": "Update part of a TODO item by its ID (any field can be provided).",
                "body_params": {
                    "title": "The TODO item title (optional).",
                    "done": "Completion status (optional).",
                    "description": "Detailed TODO item description (optional)."
                }
            },
            "DELETE": {
                "description": "Delete a TODO item by its ID."
            }
        }
    }
    return jsonify(docs), 200
