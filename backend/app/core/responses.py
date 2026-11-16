"""JSON response envelope — the single API contract for every endpoint.

Success:
    {
      "success": true,
      "data": <resource | list | null>,
      "message": "..." | null,
      "meta": {"page": 1, ...} | null
    }

Error (produced by the global exception handlers):
    {
      "success": false,
      "error": {"code": "NOT_FOUND", "message": "...", "details": [...]}
    }

Rules:
- Every endpoint returns this envelope, without exception.
- `data` holds the resource or list; pagination info goes in `meta`.
- `message` is optional human-readable text (e.g. "Profile created.").
- Error `details` entries: {"field": str|null, "message": str, "code": str|null}.
"""

from typing import Any, Literal

from fastapi import Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field


class ErrorDetailItem(BaseModel):
    field: str | None = None
    message: str
    code: str | None = None


class ErrorBody(BaseModel):
    code: str
    message: str
    details: list[ErrorDetailItem] = Field(default_factory=list)


class PaginationMeta(BaseModel):
    page: int = Field(ge=1, description="Current page number (1-based)")
    page_size: int = Field(ge=1, description="Items per page")
    total_items: int = Field(ge=0, description="Total items matching the query")
    total_pages: int = Field(ge=0, description="Total number of pages")
    has_next: bool
    has_previous: bool


class ApiResponse[T](BaseModel):
    """Generic envelope model — use as the `response_model` of endpoints so
    the OpenAPI schema describes the envelope.

    Example: `response_model=ApiResponse[ProfileRead]`
    """

    success: Literal[True] = True
    data: T | None = None
    message: str | None = None
    meta: PaginationMeta | dict[str, Any] | None = None


class ErrorResponse(BaseModel):
    success: Literal[False] = False
    error: ErrorBody


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def success_response(
    data: Any = None,
    *,
    message: str | None = None,
    meta: PaginationMeta | dict[str, Any] | None = None,
    status_code: int = 200,
    headers: dict[str, str] | None = None,
) -> Response:
    """Build a success envelope JSONResponse."""
    payload: dict[str, Any] = {"success": True, "data": data, "message": message, "meta": meta}
    if meta is not None and isinstance(meta, PaginationMeta):
        payload["meta"] = meta.model_dump()
    return JSONResponse(content=payload, status_code=status_code, headers=headers)


def error_response(
    code: str,
    message: str,
    *,
    details: list[ErrorDetailItem | dict[str, Any]] | None = None,
    status_code: int = 400,
    headers: dict[str, str] | None = None,
) -> Response:
    """Build an error envelope JSONResponse (used by exception handlers)."""
    serialized_details = [
        d.model_dump() if isinstance(d, ErrorDetailItem) else d for d in (details or [])
    ]
    payload = {
        "success": False,
        "error": {"code": code, "message": message, "details": serialized_details},
    }
    return JSONResponse(content=payload, status_code=status_code, headers=headers)


def build_pagination_meta(page: int, page_size: int, total_items: int) -> PaginationMeta:
    """Compute pagination meta from query state and total count."""
    total_pages = (total_items + page_size - 1) // page_size if page_size else 0
    return PaginationMeta(
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_previous=page > 1,
    )
