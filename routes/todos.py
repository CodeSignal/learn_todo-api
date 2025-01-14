from flask import Blueprint, request
from services.todo_service import TodoService

todos_bp = Blueprint("todos", __name__)

@todos_bp.route("", methods=["GET"])
def get_all_todos():
    return TodoService.get_all_todos(request)

@todos_bp.route("<int:todo_id>", methods=["GET"])
def get_todo(todo_id):
    return TodoService.get_todo(todo_id)

@todos_bp.route("", methods=["POST"])
def add_todo():
    return TodoService.add_todo(request)

@todos_bp.route("<int:todo_id>", methods=["PUT"])
def edit_todo(todo_id):
    return TodoService.edit_todo(todo_id, request)

@todos_bp.route("<int:todo_id>", methods=["PATCH"])
def patch_todo(todo_id):
    return TodoService.patch_todo(todo_id, request)

@todos_bp.route("<int:todo_id>", methods=["DELETE"])
def delete_todo(todo_id):
    return TodoService.delete_todo(todo_id)