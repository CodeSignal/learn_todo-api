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
                    "task": "Filter by task name prefix."
                }
            },
            "POST": {
                "description": "Add a new TODO item.",
                "body_params": {
                    "task": "The task name (required).",
                    "done": "Completion status (optional, default: false).",
                    "description": "Detailed task description (optional)."
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
                    "task": "The task name (required).",
                    "done": "Completion status (required).",
                    "description": "Detailed task description (required)."
                }
            },
            "PATCH": {
                "description": "Update part of a TODO item by its ID (any field can be provided).",
                "body_params": {
                    "task": "The task name (optional).",
                    "done": "Completion status (optional).",
                    "description": "Detailed task description (optional)."
                }
            },
            "DELETE": {
                "description": "Delete a TODO item by its ID."
            }
        }
    }
    return jsonify(docs), 200
