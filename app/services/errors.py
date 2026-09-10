class AppError(Exception):
    code = "application_error"
    status_code = 400

    def __init__(self, message=None):
        super().__init__(message or self.code)
        self.message = message or self.code


class NotFoundError(AppError):
    code = "not_found"
    status_code = 404


class AuthenticationError(AppError):
    code = "authentication_required"
    status_code = 401


class AuthorizationError(AppError):
    code = "forbidden"
    status_code = 403


class ValidationError(AppError):
    code = "validation_error"
    status_code = 400
