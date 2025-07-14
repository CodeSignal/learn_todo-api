from flask import Blueprint, request, jsonify
from services.todo_service import TodoService

todos_bp = Blueprint("todos", __name__)

@todos_bp.route("", methods=["GET"])
def get_all_todos():
    """Get all todos with optional filtering and pagination
    ---
    tags:
      - todos
    parameters:
      - name: done
        in: query
        type: boolean
        required: false
        description: Filter by completion status
      - name: title
        in: query
        type: string
        required: false
        description: Filter by TODO item title prefix
      - name: page
        in: query
        type: integer
        required: false
        description: Page number for pagination (starts at 1)
      - name: limit
        in: query
        type: integer
        required: false
        description: Number of items per page
    responses:
      200:
        description: List of todo items
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
                description: The todo ID
              title:
                type: string
                description: The todo title
              done:
                type: boolean
                description: Whether the todo is completed
              description:
                type: string
                description: Detailed todo description
    """
    return TodoService.get_all_todos(request)

@todos_bp.route("<int:todo_id>", methods=["GET"])
def get_todo(todo_id):
    """Get a specific todo by ID
    ---
    tags:
      - todos
    parameters:
      - name: todo_id
        in: path
        type: integer
        required: true
        description: ID of the todo to retrieve
    responses:
      200:
        description: Todo details
        schema:
          type: object
          properties:
            id:
              type: integer
              description: The todo ID
            title:
              type: string
              description: The todo title
            done:
              type: boolean
              description: Whether the todo is completed
            description:
              type: string
              description: Detailed todo description
      404:
        description: Todo not found
    """
    return TodoService.get_todo(todo_id)

@todos_bp.route("", methods=["POST"])
def add_todo():
    """Add a new TODO item
    ---
    tags:
      - todos
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - title
          properties:
            title:
              type: string
              description: The TODO item title
            done:
              type: boolean
              description: Completion status. Defaults to false if not provided
            description:
              type: string
              description: Detailed TODO item description
    responses:
      201:
        description: Created todo item
        schema:
          type: object
          properties:
            id:
              type: integer
              description: The todo ID
            title:
              type: string
              description: The todo title
            done:
              type: boolean
              description: Whether the todo is completed
            description:
              type: string
              description: Detailed todo description
      400:
        description: Invalid request - missing title
    """
    return TodoService.add_todo(request)

@todos_bp.route("<int:todo_id>", methods=["PUT"])
def edit_todo(todo_id):
    """Replace an existing TODO item (all fields required)
    ---
    tags:
      - todos
    parameters:
      - name: todo_id
        in: path
        type: integer
        required: true
        description: ID of the todo to update
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - title
            - done
            - description
          properties:
            title:
              type: string
              description: The TODO item title
            done:
              type: boolean
              description: Completion status
            description:
              type: string
              description: Detailed TODO item description
    responses:
      200:
        description: Updated todo item
        schema:
          type: object
          properties:
            id:
              type: integer
            title:
              type: string
            done:
              type: boolean
            description:
              type: string
      400:
        description: Invalid request (missing required fields)
      404:
        description: Todo not found
    """
    return TodoService.edit_todo(todo_id, request)

@todos_bp.route("<int:todo_id>", methods=["PATCH"])
def patch_todo(todo_id):
    """Update part of a TODO item (any field optional)
    ---
    tags:
      - todos
    parameters:
      - name: todo_id
        in: path
        type: integer
        required: true
        description: ID of the todo to update
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            title:
              type: string
              description: The TODO item title
            done:
              type: boolean
              description: Completion status
            description:
              type: string
              description: Detailed TODO item description
    responses:
      200:
        description: Updated todo item
        schema:
          type: object
          properties:
            id:
              type: integer
            title:
              type: string
            done:
              type: boolean
            description:
              type: string
      400:
        description: Invalid request (empty body)
      404:
        description: Todo not found
    """
    return TodoService.patch_todo(todo_id, request)

@todos_bp.route("<int:todo_id>", methods=["DELETE"])
def delete_todo(todo_id):
    """Delete a TODO item
    ---
    tags:
      - todos
    parameters:
      - name: todo_id
        in: path
        type: integer
        required: true
        description: ID of the todo to delete
    responses:
      204:
        description: Todo deleted successfully
      404:
        description: Todo not found
    """
    return TodoService.delete_todo(todo_id)

@todos_bp.route("/reset", methods=["POST"])
def reset_todos():
    """Reset todos with data from uploaded JSON file
    ---
    tags:
      - todos
    summary: Reset all todos with data from JSON file
    description: |
      Replaces all existing todos with data from an uploaded JSON file.
      The original initial_todos.json file remains unchanged.
      This is useful for testing different todo datasets or resetting to a clean state.

      The uploaded file should be in the same format as initial_todos.json:
      {
        "todos": [
          {
            "id": 1,
            "title": "Todo title",
            "done": false,
            "description": "Optional description"
          }
        ]
      }
    consumes:
      - multipart/form-data
    parameters:
      - in: formData
        name: file
        type: file
        required: true
        description: JSON file containing todos data
    responses:
      200:
        description: Todos reset successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Todos reset successfully. Loaded 4 todos."
            todos_count:
              type: integer
              example: 4
            next_id:
              type: integer
              example: 5
            filename:
              type: string
              example: "my_todos.json"
      400:
        description: Invalid file format or data
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Invalid JSON format: Expecting ',' delimiter"
      415:
        description: No file provided
        schema:
          type: object
          properties:
            error:
              type: string
              example: "No file provided"
    """

    # Check if file was uploaded
    if 'file' not in request.files:
        return jsonify({"error": "No file provided. Please upload a JSON file."}), 400

    file = request.files['file']

    # Check if file was actually selected
    if file.filename == '':
        return jsonify({"error": "No file selected. Please select a JSON file."}), 400

    # Check file extension
    if not file.filename.lower().endswith('.json'):
        return jsonify({"error": "Invalid file type. Please upload a JSON file."}), 400

    try:
        # Read file content
        file_content = file.read().decode('utf-8')

        # Reset todos with file content
        response, status_code = TodoService.reset_todos(file_content)

        # Add filename to successful response
        if status_code == 200:
            response_data = response.get_json()
            response_data['filename'] = file.filename
            return jsonify(response_data), status_code

        return response, status_code

    except UnicodeDecodeError:
        return jsonify({"error": "Invalid file encoding. Please ensure the file is UTF-8 encoded."}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to process file: {str(e)}"}), 500
