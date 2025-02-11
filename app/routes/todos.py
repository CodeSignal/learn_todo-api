from flask import Blueprint, request
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