from flask import Flask
from routes.todos import todos_bp
from routes.errors import errors_bp
from routes.docs import docs_bp

def create_app():
    app = Flask(__name__)
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True  # Enable pretty-printing for JSON responses

    app.register_blueprint(todos_bp, url_prefix="/todos")
    app.register_blueprint(errors_bp)
    app.register_blueprint(docs_bp, url_prefix="/docs")

    return app


# Automatically run the app if this script is executed directly
if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8000)
