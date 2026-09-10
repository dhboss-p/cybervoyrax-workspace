import logging
import uuid
from flask import g, request


def register_request_logging(app):
    if not app.logger.handlers:
        logging.basicConfig(level=logging.INFO)

    @app.before_request
    def assign_request_id():
        g.request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())

    @app.after_request
    def add_request_headers(response):
        response.headers["X-Request-ID"] = g.get("request_id", "unknown")
        app.logger.info(
            "%s %s -> %s request_id=%s",
            request.method,
            request.path,
            response.status_code,
            g.get("request_id", "unknown"),
        )
        return response
