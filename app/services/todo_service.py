from flask import jsonify, request, current_app
from models.todo import Todo

class TodoService:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TodoService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not TodoService._initialized:
            self.todos = {}
            self.next_id = 1
            self._initialize_todos()
            TodoService._initialized = True

    def _initialize_todos(self):
        """Initialize todos from the app config."""
        initial_todos = current_app.config.get('initial_todos', [])
        for todo_data in initial_todos:
            todo_id = todo_data['id']
            self.todos[todo_id] = Todo(
                todo_id,
                todo_data['title'],
                todo_data['done'],
                todo_data['description']
            )
            # Update next_id to be greater than the highest existing id
            self.next_id = max(self.next_id, todo_id + 1)

    @classmethod
    def get_instance(cls):
        """Get the singleton instance of TodoService."""
        if cls._instance is None:
            cls._instance = TodoService()
        return cls._instance

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
        service = TodoService.get_instance()
        done = request.args.get("done", type=str)
        title_prefix = request.args.get("title", type=str)
        page = request.args.get("page", type=int)
        limit = request.args.get("limit", type=int)

        if done is not None:
            done = done.lower() == 'true'

        results = list(service.todos.values())

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
        service = TodoService.get_instance()
        todo = service.todos.get(todo_id)
        if todo is None:
            return jsonify({"error": "Todo not found"}), 404
        return jsonify(todo.to_dict()), 200

    @staticmethod
    def add_todo(request):
        service = TodoService.get_instance()
        data = request.get_json()
        if not data or "title" not in data:
            return jsonify({"error": "Invalid request. 'title' is required."}), 400

        todo = Todo(service.next_id, data["title"], data.get("done", False), data.get("description"))
        service.todos[service.next_id] = todo
        service.next_id += 1
        return jsonify(todo.to_dict()), 201

    @staticmethod
    def edit_todo(todo_id, request):
        service = TodoService.get_instance()
        data = request.get_json()
        todo = service.todos.get(todo_id)
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
        service = TodoService.get_instance()
        data = request.get_json()
        todo = service.todos.get(todo_id)
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
        service = TodoService.get_instance()
        if todo_id not in service.todos:
            return jsonify({"error": "Todo not found"}), 404
        del service.todos[todo_id]
        return '', 204

    @staticmethod
    def reset_todos(file_content):
        """Reset todos with new data from uploaded JSON file.

        This method:
        1. Parses the JSON file content
        2. Validates the file format and todo data
        3. Clears all existing todos
        4. Loads new todos from the file data
        5. Updates the next_id counter appropriately

        Args:
            file_content (str): JSON file content as string

        Returns:
            tuple: JSON response and status code
        """
        import json

        service = TodoService.get_instance()

        # Parse JSON content
        try:
            data = json.loads(file_content)
        except json.JSONDecodeError as e:
            return jsonify({"error": f"Invalid JSON format: {str(e)}"}), 400

        # Validate file structure - expect {"todos": [...]} format
        if not isinstance(data, dict) or 'todos' not in data:
            return jsonify({"error": "Invalid file format. Expected JSON with 'todos' array field."}), 400

        new_todos_data = data['todos']

        # Validate the todos data
        if not isinstance(new_todos_data, list):
            return jsonify({"error": "Invalid todos format. Expected an array of todo objects."}), 400

        # Validate each todo item
        for i, todo_data in enumerate(new_todos_data):
            if not isinstance(todo_data, dict):
                return jsonify({"error": f"Invalid todo at index {i}. Expected an object."}), 400

            required_fields = ['id', 'title', 'done']
            for field in required_fields:
                if field not in todo_data:
                    return jsonify({"error": f"Missing required field '{field}' in todo at index {i}."}), 400

            # Validate field types
            if not isinstance(todo_data['id'], int):
                return jsonify({"error": f"Invalid 'id' type in todo at index {i}. Expected integer."}), 400
            if not isinstance(todo_data['title'], str):
                return jsonify({"error": f"Invalid 'title' type in todo at index {i}. Expected string."}), 400
            if not isinstance(todo_data['done'], bool):
                return jsonify({"error": f"Invalid 'done' type in todo at index {i}. Expected boolean."}), 400
            if 'description' in todo_data and not isinstance(todo_data['description'], str):
                return jsonify({"error": f"Invalid 'description' type in todo at index {i}. Expected string."}), 400

        # Check for duplicate IDs
        ids = [todo['id'] for todo in new_todos_data]
        if len(ids) != len(set(ids)):
            return jsonify({"error": "Duplicate todo IDs found in the data."}), 400

        # Clear existing todos
        service.todos.clear()
        service.next_id = 1

        # Load new todos
        for todo_data in new_todos_data:
            todo_id = todo_data['id']
            service.todos[todo_id] = Todo(
                todo_id,
                todo_data['title'],
                todo_data['done'],
                todo_data.get('description', '')
            )
            # Update next_id to be greater than the highest existing id
            service.next_id = max(service.next_id, todo_id + 1)

        return jsonify({
            "message": f"Todos reset successfully. Loaded {len(new_todos_data)} todos.",
            "todos_count": len(new_todos_data),
            "next_id": service.next_id
        }), 200
