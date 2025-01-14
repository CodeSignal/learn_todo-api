from flask import jsonify, request
from models.todo import Todo

todos = {
    1: Todo(1, "Buy groceries", done=False, description="Milk, eggs, bread, and coffee"),
    2: Todo(2, "Call mom", done=True, description="Check in and catch up"),
    3: Todo(3, "Finish project report", done=False, description="Summarize Q4 performance metrics"),
    4: Todo(4, "Workout", done=True, description="30 minutes of cardio"),
}

next_id = 5

class TodoService:
    @staticmethod
    def get_all_todos(request):
        done = request.args.get("done", type=str)
        task_prefix = request.args.get("task", type=str)

        if done is not None:
            done = done.lower() == 'true'

        results = list(todos.values())

        if done is not None:
            results = [todo for todo in results if todo.done == done]

        if task_prefix:
            results = [todo for todo in results if todo.task.lower().startswith(task_prefix.lower())]

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
        if not data or "task" not in data:
            return jsonify({"error": "Invalid request. 'task' is required."}), 400

        todo = Todo(next_id, data["task"], data.get("done", False), data.get("description"))
        todos[next_id] = todo
        next_id += 1
        return jsonify(todo.to_dict()), 201

    @staticmethod
    def edit_todo(todo_id, request):
        data = request.get_json()
        todo = todos.get(todo_id)
        if todo is None:
            return jsonify({"error": "Todo not found"}), 404
        if not data or "task" not in data or "done" not in data or "description" not in data:
            return jsonify({"error": "Invalid request. 'task', 'done', and 'description' fields are required."}), 400

        todo.task = data["task"]
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

        todo.task = data.get("task", todo.task)
        todo.done = data.get("done", todo.done)
        todo.description = data.get("description", todo.description)
        return jsonify(todo.to_dict()), 200

    @staticmethod
    def delete_todo(todo_id):
        if todo_id not in todos:
            return jsonify({"error": "Todo not found"}), 404
        del todos[todo_id]
        return jsonify({"message": "Todo deleted successfully"}), 200
