"""Application exception hierarchy and error codes.

Every error response follows the envelope in `app.core.responses`:

    {"success": false, "error": {"code": ..., "message": ..., "details": [...]}}

Raise `AppError` subclasses (or AppError with an ErrorCode) — never leak raw
exceptions to clients.
"""

from enum import StrEnum


class ErrorCode(StrEnum):
    """Stable, machine-readable error codes used across the API."""

    # Generic / transport
    VALIDATION_ERROR = "VALIDATION_ERROR"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    RATE_LIMITED = "RATE_LIMITED"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    METHOD_NOT_ALLOWED = "METHOD_NOT_ALLOWED"

    # Profiles
    EMAIL_ALREADY_REGISTERED = "EMAIL_ALREADY_REGISTERED"
    PROFILE_NOT_FOUND = "PROFILE_NOT_FOUND"

    # Opportunities & shortlist
    OPPORTUNITY_NOT_FOUND = "OPPORTUNITY_NOT_FOUND"
    SHORTLIST_NOT_FOUND = "SHORTLIST_NOT_FOUND"
    SHORTLIST_ALREADY_EXISTS = "SHORTLIST_ALREADY_EXISTS"


class AppError(Exception):
    """Base application error carrying HTTP status + error code.

    Attributes:
        status_code: HTTP status to return.
        code: Machine-readable ErrorCode string.
        message: Human-readable summary (safe to show to users).
        details: Optional list of {field, message, code} dicts for
            field-level errors.
        headers: Optional extra HTTP headers (e.g. Retry-After).
    """

    status_code: int = 400
    code: ErrorCode = ErrorCode.INTERNAL_ERROR
    default_message: str = "An application error occurred."

    def __init__(
        self,
        message: str | None = None,
        *,
        code: ErrorCode | None = None,
        status_code: int | None = None,
        details: list[dict] | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.message = message or self.default_message
        if code is not None:
            self.code = code
        if status_code is not None:
            self.status_code = status_code
        self.details = details or []
        self.headers = headers or {}
        super().__init__(self.message)


# ---------------------------------------------------------------------------
# Concrete errors (keep the set small and reuse; add new codes to ErrorCode
# above, not ad-hoc strings)
# ---------------------------------------------------------------------------


class ValidationError(AppError):
    status_code = 422
    code = ErrorCode.VALIDATION_ERROR
    default_message = "Request validation failed."


class UnauthorizedError(AppError):
    status_code = 401
    code = ErrorCode.UNAUTHORIZED
    default_message = "Authentication required."


class ForbiddenError(AppError):
    status_code = 403
    code = ErrorCode.FORBIDDEN
    default_message = "You do not have permission to perform this action."


class NotFoundError(AppError):
    status_code = 404
    code = ErrorCode.NOT_FOUND
    default_message = "Resource not found."


class ConflictError(AppError):
    status_code = 409
    code = ErrorCode.CONFLICT
    default_message = "The request conflicts with existing data."


class RateLimitedError(AppError):
    status_code = 429
    code = ErrorCode.RATE_LIMITED
    default_message = "Too many requests. Please try again later."


class ServiceUnavailableError(AppError):
    status_code = 503
    code = ErrorCode.SERVICE_UNAVAILABLE
    default_message = "A dependent service is unavailable."
