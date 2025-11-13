"""
Custom exceptions for the application
"""


class CleoException(Exception):
    """Base exception for Cleo application"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class AuthenticationException(CleoException):
    """Authentication failed"""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)


class AuthorizationException(CleoException):
    """User not authorized to perform action"""
    def __init__(self, message: str = "Not authorized"):
        super().__init__(message, status_code=403)


class NotFoundException(CleoException):
    """Resource not found"""
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class ValidationException(CleoException):
    """Validation error"""
    def __init__(self, message: str = "Validation error"):
        super().__init__(message, status_code=422)


class ExternalServiceException(CleoException):
    """External service error"""
    def __init__(self, message: str = "External service error", status_code: int = 502):
        super().__init__(message, status_code=status_code)


class PlaidException(ExternalServiceException):
    """Plaid API error"""
    def __init__(self, message: str = "Plaid API error"):
        super().__init__(message)


class DatabaseException(CleoException):
    """Database operation error"""
    def __init__(self, message: str = "Database error"):
        super().__init__(message, status_code=500)
