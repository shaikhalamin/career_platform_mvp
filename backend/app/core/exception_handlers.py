"""Global exception handlers converting every error into the JSON envelope.

Registered once in `app.main.create_app()`. No endpoint needs its own
try/except just to shape an error response: services raise `AppError`
subclasses, FastAPI/Pydantic validation failures and Starlette HTTP
exceptions are rewritten here, and anything unhandled becomes a logged 500
envelope (never a raw traceback).
"""

import logging

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import AppError, ErrorCode
from app.core.responses import error_response

logger = logging.getLogger("app.errors")

# Map bare HTTP status codes to stable error codes when only a
# StarletteHTTPException is available (e.g. 404 route not found).
_STATUS_CODE_MAP: dict[int, tuple[ErrorCode, str]] = {
    400: (ErrorCode.VALIDATION_ERROR, "Bad request."),
    401: (ErrorCode.UNAUTHORIZED, "Authentication required."),
    403: (ErrorCode.FORBIDDEN, "You do not have permission to perform this action."),
    404: (ErrorCode.NOT_FOUND, "Resource not found."),
    405: (ErrorCode.METHOD_NOT_ALLOWED, "HTTP method not allowed for this endpoint."),
    409: (ErrorCode.CONFLICT, "The request conflicts with existing data."),
    422: (ErrorCode.VALIDATION_ERROR, "Request validation failed."),
    429: (ErrorCode.RATE_LIMITED, "Too many requests. Please try again later."),
    500: (ErrorCode.INTERNAL_ERROR, "An unexpected internal error occurred."),
    503: (ErrorCode.SERVICE_UNAVAILABLE, "A dependent service is unavailable."),
}


def _status_phrase(status_code: int) -> str:
    """Standard HTTP reason phrase for a status code (e.g. 404 -> 'Not Found')."""
    from http import HTTPStatus

    try:
        return HTTPStatus(status_code).phrase
    except ValueError:
        return ""


def register_exception_handlers(app: FastAPI) -> None:
    """Attach all envelope-producing exception handlers to the app."""

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        response = error_response(
            code=str(exc.code),
            message=exc.message,
            details=exc.details,
            status_code=exc.status_code,
            headers=exc.headers or None,
        )
        if exc.status_code >= 500:
            logger.error("AppError %s: %s", exc.code, exc.message, exc_info=exc)
        return response

    @app.exception_handler(RequestValidationError)
    async def request_validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Rewrite FastAPI/Pydantic 422s into the standard envelope with
        field-level details."""
        details = []
        for error in exc.errors():
            loc = error.get("loc", ())
            field = ".".join(str(part) for part in loc[1:]) if len(loc) > 1 else None
            details.append(
                {
                    "field": field,
                    "message": error.get("msg", "Invalid value."),
                    "code": error.get("type"),
                }
            )
        return error_response(
            code=str(ErrorCode.VALIDATION_ERROR),
            message="Request validation failed.",
            details=details,
            status_code=422,
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        code, default_message = _STATUS_CODE_MAP.get(
            exc.status_code, (ErrorCode.INTERNAL_ERROR, "HTTP error.")
        )
        # Prefer our curated message when the handler raised with a bare
        # detail (None, the status int, or a stock reason phrase like
        # "Not Found"); use custom details only when they're meaningful.
        stock_details = {None, int(exc.status_code), _status_phrase(exc.status_code)}
        message = default_message if exc.detail in stock_details else str(exc.detail)
        headers = getattr(exc, "headers", None)
        return error_response(
            code=str(code),
            message=message,
            status_code=exc.status_code,
            headers=headers,
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> Response:
        """Last resort for anything that escaped the layers above — the
        client sees the generic 500 envelope, the traceback stays in logs."""
        logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
        return error_response(
            code=str(ErrorCode.INTERNAL_ERROR),
            message="An unexpected internal error occurred.",
            status_code=500,
        )
