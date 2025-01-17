from flask import jsonify, request
from models.todo import Todo
import json
import os

# Load initial todos from JSON file
def load_initial_todos():
    json_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'initial_todos.json')
    with open(json_path, 'r') as f:
        data = json.load(f)
        loaded_todos = {}
        for todo_data in data['todos']:
            todo_id = todo_data['id']
            loaded_todos[todo_id] = Todo(
                todo_id,
                todo_data['title'],
                todo_data['done'],
                todo_data['description']
            )
        # Calculate next_id based on the highest id in the todos
        next_id = max(todo.id for todo in loaded_todos.values()) + 1
        return loaded_todos, next_id

todos, next_id = load_initial_todos()

class TodoService:
    @staticmethod
    def get_all_todos(request):
        """Get all todos with optional filtering and pagination.

        Query Parameters:
            done (str, optional): Filter by completion status ('true' or 'false')
            title (str, optional): Filter todos by title prefix (case-insensitive)
            page (int, optional): Page number for pagination (starts at 1)
            limit (int, optional): Number of items per page

        Returns:
            tuple: JSON response containing list of todos and HTTP status code
            
        Examples:
            GET /todos - Returns all todos
            GET /todos?done=true - Returns all completed todos
            GET /todos?title=buy - Returns todos with titles starting with 'buy'
            GET /todos?page=1&limit=10 - Returns first 10 todos
        """
        done = request.args.get("done", type=str)
        title_prefix = request.args.get("title", type=str)
        page = request.args.get("page", type=int)
        limit = request.args.get("limit", type=int)

        if done is not None:
            done = done.lower() == 'true'

        results = list(todos.values())

        if done is not None:
            results = [todo for todo in results if todo.done == done]

        if title_prefix:
            results = [todo for todo in results if todo.title.lower().startswith(title_prefix.lower())]

        # Apply pagination only if both page and limit parameters are provided
        if page is not None and limit is not None:
            start_idx = (page - 1) * limit
            end_idx = start_idx + limit
            results = results[start_idx:end_idx]

        return jsonify([todo.to_dict() for todo in results]), 200

    @staticmethod
    def get_todo(todo_id):
        todo = todos.get(todo_id)
        if todo is None:
            return jsonify({"error": "Todo not found"}), 404
        return jsonify(todo.to_dict()), 200

    @staticmethod
    def add_todo(request):
        global next_id
        data = request.get_json()
        if not data or "title" not in data:
            return jsonify({"error": "Invalid request. 'title' is required."}), 400

        todo = Todo(next_id, data["title"], data.get("done", False), data.get("description"))
        todos[next_id] = todo
        next_id += 1
        return jsonify(todo.to_dict()), 201

    @staticmethod
    def edit_todo(todo_id, request):
        data = request.get_json()
        todo = todos.get(todo_id)
        if todo is None:
            return jsonify({"error": "Todo not found"}), 404
        if not data or "title" not in data or "done" not in data or "description" not in data:
            return jsonify({"error": "Invalid request. 'title', 'done', and 'description' fields are required."}), 400

        todo.title = data["title"]
        todo.done = data["done"]
        todo.description = data["description"]
        return jsonify(todo.to_dict()), 200

    @staticmethod
    def patch_todo(todo_id, request):
        data = request.get_json()
        todo = todos.get(todo_id)
        if todo is None:
            return jsonify({"error": "Todo not found"}), 404
        if not data:
            return jsonify({"error": "Invalid request."}), 400

        todo.title = data.get("title", todo.title)
        todo.done = data.get("done", todo.done)
        todo.description = data.get("description", todo.description)
        return jsonify(todo.to_dict()), 200

    @staticmethod
    def delete_todo(todo_id):
        if todo_id not in todos:
            return jsonify({"error": "Todo not found"}), 404
        del todos[todo_id]
        return '', 204
