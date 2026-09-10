from flask import jsonify, render_template, request
from .services.errors import AppError


def register_error_handlers(app):
    def respond(status_code, code, message):
        if request.path.startswith("/api/"):
            return jsonify({"error": code, "message": message}), status_code
        return render_template("error.html", status_code=status_code, message=message), status_code

    @app.errorhandler(AppError)
    def handle_app_error(exc):
        return respond(exc.status_code, exc.code, exc.message)

    @app.errorhandler(400)
    def bad_request(_exc):
        return respond(400, "bad_request", "The request could not be processed.")

    @app.errorhandler(401)
    def unauthorized(_exc):
        return respond(401, "unauthorized", "Sign in is required to continue.")

    @app.errorhandler(403)
    def forbidden(_exc):
        return respond(403, "forbidden", "You do not have permission to perform this action.")

    @app.errorhandler(404)
    def not_found(_exc):
        return respond(404, "not_found", "The requested page was not found.")

    @app.errorhandler(405)
    def method_not_allowed(_exc):
        return respond(405, "method_not_allowed", "This action is not available for the requested page.")

    @app.errorhandler(500)
    def internal_error(_exc):
        return respond(500, "internal_error", "An internal application error occurred.")
