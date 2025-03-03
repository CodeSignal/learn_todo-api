from flask import Blueprint, jsonify, request

errors_bp = Blueprint("errors", __name__)

@errors_bp.app_errorhandler(404)
def handle_not_found_error(error):
    return jsonify({
        "error": str(error),
        "endpoint": request.path
    }), 404

@errors_bp.app_errorhandler(400)
def handle_bad_request_error(error):
    return jsonify({
        "error": str(error),
        "endpoint": request.path
    }), 400

@errors_bp.app_errorhandler(500)
def handle_internal_server_error(error):
    return jsonify({
        "error": str(error),
        "endpoint": request.path
    }), 500
